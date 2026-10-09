import urllib3
from locust import HttpUser, task, between

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BMC_URL = "https://127.0.0.1:2443"
BMC_USER = "root"
BMC_PASS = "0penBmc"


class OpenBMCAPIUser(HttpUser):
    """Нагрузочный сценарий для Redfish API OpenBMC."""

    host = BMC_URL
    wait_time = between(1, 3)

    def on_start(self):
        """Аутентификация при старте пользователя — получаем X-Auth-Token."""
        response = self.client.post(
            "/redfish/v1/SessionService/Sessions",
            json={"UserName": BMC_USER, "Password": BMC_PASS},
            verify=False,
        )
        if response.status_code == 201:
            self.token = response.headers.get("X-Auth-Token")
        else:
            self.token = None
            print(f"[OpenBMC] Ошибка аутентификации: {response.status_code}")

    @property
    def headers(self):
        return {"X-Auth-Token": self.token} if self.token else {}

    @task(3)
    def get_system_info(self):
        """Получение информации о системе."""
        self.client.get(
            "/redfish/v1/Systems/system",
            headers=self.headers,
            verify=False,
            name="/redfish/v1/Systems/system",
        )

    @task(2)
    def get_power_state(self):
        """Получение состояния питания."""
        self.client.get(
            "/redfish/v1/Systems/system",
            headers=self.headers,
            verify=False,
            name="/redfish/v1/Systems/system (PowerState)",
        )

    @task(1)
    def get_thermal_subsystem(self):
        """Получение данных термоподсистемы."""
        self.client.get(
            "/redfish/v1/Chassis/chassis/ThermalSubsystem",
            headers=self.headers,
            verify=False,
            name="/redfish/v1/Chassis/chassis/ThermalSubsystem",
        )


class PublicAPIUser(HttpUser):
    """Нагрузочный сценарий для публичных API."""

    host = "https://jsonplaceholder.typicode.com"
    wait_time = between(1, 3)

    @task(1)
    def get_jsonplaceholder_posts(self):
        """JSONPlaceholder — список постов."""
        self.client.get(
            "https://jsonplaceholder.typicode.com/posts",
            name="JSONPlaceholder /posts",
        )

    @task(1)
    def get_wttr_novosibirsk(self):
        """wttr.in — погода в Новосибирске."""
        self.client.get(
            "https://wttr.in/Novosibirsk?format=j1",
            name="wttr.in /Novosibirsk",
        )
