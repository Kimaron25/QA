# Лабораторная работа 7: CI/CD с Jenkins для OpenBMC

CI/CD pipeline для тестирования OpenBMC (Redfish API, WebUI, нагрузка).

## Структура

- `Jenkinsfile` — Pipeline (Groovy)
- `Dockerfile.jenkins` — Jenkins-образ с Docker CLI
- `test_redfish.py` — PyTest тесты ЛР5 (5 тестов)
- `locustfile.py` — Locust сценарии ЛР6
- `tests/test_webui.py` — Selenium WebUI-тесты ЛР4

## Pipeline Stages

1. Checkout
2. Setup (pytest, locust, sshpass)
3. Prepare
4. Check QEMU (Redfish API)
5. PyTest (LR5) — 5 passed
6. Selenium (LR4)
7. Locust (LR6) — 13 requests, 0 failures

## Артефакты

- `reports/pytest.xml`
- `reports/locust_stats.csv`
- `reports/selenium.log`
