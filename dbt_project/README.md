# dbt Project — Hardware Tuning Guide

This pipeline diverges from the default [CogStack profiles.yml](https://github.com/CogStack/dbt_mimic_omop/blob/main/profiles.yml) which is designed for server-grade hardware. The configuration here is tuned for a **16GB RAM laptop running WSL2**.

---

## WSL2 Memory Allocation

Before running, configure WSL2 to give Docker enough headroom. Create or edit `~/.wslconfig` on Windows.

> **Finding the file on Windows:** Open File Explorer, paste `%USERPROFILE%` into the address bar, and create `.wslconfig` there if it doesn't exist.

```ini
# C:\Users\<your_windows_user>\.wslconfig
[wsl2]
memory=10GB
swap=4GB
```

Restart WSL after saving:
```bash
wsl --shutdown
```

---

## Benchmarks — 16GB RAM, WSL2

Counter-intuitively, more threads and more memory did **not** improve performance on this workload. DuckDB's parallel execution adds overhead on memory-constrained machines.

| Threads | Memory Limit | Runtime |
|---|---|---|
| 1 | 5.5 GB | 39 mins |
| **1** | **6 GB** | **36 mins ✅ fastest** |
| 2 | 6 GB | 44 mins |
| 2 | 7 GB | 51 mins |
| 2 | 8 GB | 54 mins |
| 3 | 6.5 GB | 61 mins |

**Winner: 1 thread, 6GB memory limit.**

---

## Current profiles.yml

```yaml
threads: 1
settings:
  memory_limit: '6GB'
  max_temp_directory_size: '150GB'
  preserve_insertion_order: false
```

> `preserve_insertion_order: false` is a significant performance gain for large OMOP tables — DuckDB skips row ordering overhead during inserts.

> `temp_directory` is intentionally omitted — setting it after DuckDB has already used the default temp path causes a `Cannot switch temporary directory` error on re-runs.

