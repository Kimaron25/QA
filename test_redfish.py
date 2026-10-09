import pytest
import requests
import urllib3
import subprocess

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://127.0.0.1:2443"
USERNAME = "root"
PASSWORD = "0penBmc"


@pytest.fixture(scope="module")
def token():
    url = f"{BASE_URL}/redfish/v1/SessionService/Sessions"
    response = requests.post(
        url,
        json={"UserName": USERNAME, "Password": PASSWORD},
        verify=False,
    )
    assert response.status_code == 201, f"Ozhidali 201, poluchili {response.status_code}"
    tok = response.headers.get("X-Auth-Token")
    assert tok, "Token X-Auth-Token ne poluchen"
    return tok


@pytest.fixture(scope="module")
def headers(token):
    return {"X-Auth-Token": token}


def test_auth(token):
    assert token, "Token ne poluchen"
    print(f"\n[TEST 1] Autentifikaciya - token poluchen: {token[:20]}...")


def test_system_info(headers):
    url = f"{BASE_URL}/redfish/v1/Systems/system"
    response = requests.get(url, headers=headers, verify=False)
    assert response.status_code == 200, f"Ozhidali 200, poluchili {response.status_code}"
    data = response.json()
    assert "Status" in data, "Net polya Status"
    assert "PowerState" in data, "Net polya PowerState"
    print(f"\n[TEST 2] PowerState={data['PowerState']}, Status={data['Status']['State']}")


def test_power_on(headers):
    url = f"{BASE_URL}/redfish/v1/Systems/system/Actions/ComputerSystem.Reset"
    response = requests.post(
        url,
        headers=headers,
        json={"ResetType": "On"},
        verify=False,
    )
    assert response.status_code in (202, 204), f"Ozhidali 202/204, poluchili {response.status_code}"
    print(f"\n[TEST 3] Komanda On prinyata (HTTP {response.status_code})")


def test_temperature(headers):
    url = f"{BASE_URL}/redfish/v1/Chassis/chassis/ThermalSubsystem"
    response = requests.get(url, headers=headers, verify=False)
    assert response.status_code == 200, f"Ozhidali 200, poluchili {response.status_code}"
    data = response.json()
    assert "ThermalMetrics" in data, "Net ThermalMetrics"
    print(f"\n[TEST 4] ThermalSubsystem dostupen, Status={data.get('Status', {}).get('Health')}")


def test_redfish_vs_ipmi(headers):
    """Test 5: sravnenie datchikov CPU v Redfish i IPMI.

    V QEMU-emulyacii Romulus fizicheskie datchiki ne emuliruyutsya.
    Test proveryaet dostupnost oboih interfeisov i strukturu otvetov.
    """
    # --- Redfish: ThermalMetrics ---
    url = f"{BASE_URL}/redfish/v1/Chassis/chassis/ThermalSubsystem/ThermalMetrics"
    r_redfish = requests.get(url, headers=headers, verify=False)
    assert r_redfish.status_code == 200, f"Redfish ThermalMetrics: {r_redfish.status_code}"
    redfish_data = r_redfish.json()
    redfish_temps = redfish_data.get("TemperatureReadingsCelsius", [])

    # --- IPMI: ipmitool sdr ---
    # Uvelichen timeout do 90 sek (QEMU medlennyy)
    ipmi_sensors = []
    ipmi_ok = False
    try:
        ipmi_result = subprocess.run(
            ["ipmitool", "-I", "lanplus", "-H", "127.0.0.1", "-p", "2623",
             "-U", "root", "-P", "0penBmc", "sdr"],
            capture_output=True, text=True, timeout=90,
        )
        ipmi_output = ipmi_result.stdout
        ipmi_sensors = [line for line in ipmi_output.splitlines() if line.strip()]
        ipmi_ok = len(ipmi_sensors) > 0
        print(f"\n[TEST 5] IPMI returncode={ipmi_result.returncode}, sensors={len(ipmi_sensors)}")
    except subprocess.TimeoutExpired as e:
        ipmi_output = e.stdout.decode() if e.stdout else ""
        ipmi_sensors = [line for line in ipmi_output.splitlines() if line.strip()]
        ipmi_ok = len(ipmi_sensors) > 0
        print(f"\n[TEST 5] IPMI timeout, no polucheno {len(ipmi_sensors)} sensorov")

    print(f"[TEST 5] Redfish temperature readings: {len(redfish_temps)}")
    print(f"[TEST 5] IPMI sensors: {len(ipmi_sensors)}")

    assert r_redfish.status_code == 200, "Redfish nedostupen"

    assert ipmi_ok, "IPMI ne vozvratil ni odnogo sensora"

    redfish_cpu = [t for t in redfish_temps if "CPU" in str(t) or "cpu" in str(t)]
    ipmi_cpu = [s for s in ipmi_sensors if "temp" in s.lower() or "cpu" in s.lower()]

    if redfish_cpu and ipmi_cpu:
        print(f"[TEST 5] Datchiki CPU est v oboih interfeisah - sravnenie vozmozhno")
    else:
        print(f"[TEST 5] Dannyh net (ogranichenie QEMU), no oba interfeisa rabotayut")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
