# Лабораторная работа 8: Профилирование ПО

Профилирование QEMU с OpenBMC Romulus. Сбор метрик CPU, RAM, сети.

## Ограничение WSL

`perf` в WSL2 недоступен: ядро `microsoft-standard-WSL2` не имеет пакета `linux-tools-*`. Использованы `vmstat`, `pidstat`, `nmon` — эквивалентные метрики.

## Методика

1. До теста: QEMU Romulus в простое.
2. Во время теста: нагрузка Locust (`-u 20 -r 5 -t 600s`).
3. Замеры: `top`, `vmstat`, `pidstat`, `nmon`, `ps`.

## Результаты

### CPU хоста (%) до/во время

| Инструмент | До | Во время |
|---|---|---|
| top (us+sy) | 6.1% | 5.3% |
| vmstat (us+sy) | 3–5% | 4–7% |
| pidstat QEMU %CPU | — | 39.4% |

### RAM QEMU (MB) до/во время

| Метрика | До | Во время |
|---|---|---|
| RSS | 1363 MB | 1365 MB |
| Δ | — | +2 MB |

### Сеть (nmon)

eth0: 0.0–0.1 KB/s. Минимальная — nmon запущен после Locust.

### Swap

Total 2048 MB, used ~1.5 GB.

## Оптимизация QEMU

| Параметр | Эффект |
|---|---|
| -accel kvm | KVM (bare-metal Linux) |
| -smp 2 | 2 ядра |
| -m 512 | Больше RAM |
| -cpu max | Максимум CPU |
| cache=writeback | Кэш диска |

## Вывод

perf в WSL недоступен → использованы vmstat, pidstat, nmon. QEMU под нагрузкой: CPU 39.4%, RAM стабильна (+2 MB). Swap 1.5 GB — проблема хоста.
