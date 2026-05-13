# -*- coding: utf-8 -*-
# 1.5 文件读写
# 学习文件的打开、读取和写入

import os
import tempfile

tmpdir = tempfile.mkdtemp(prefix="pyphysbook_")
filepath = os.path.join(tmpdir, "data.txt")

print("=== 写入文件 ===")
data_lines = [
    "# 物理实验数据",
    "# 时间(s)  位移(m)  速度(m/s)",
    "0.0  0.0  0.0",
    "1.0  4.9  9.8",
    "2.0  19.6  19.6",
    "3.0  44.1  29.4",
    "4.0  78.4  39.2",
]
with open(filepath, "w", encoding="utf-8") as f:
    for line in data_lines:
        f.write(line + "\n")
print(f"已写入 {len(data_lines)} 行到 {filepath}")
print()

print("=== 读取文件 ===")
with open(filepath, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#"):
            parts = line.split()
            t, s, v = float(parts[0]), float(parts[1]), float(parts[2])
            print(f"  t={t:.1f}s, s={s:.1f}m, v={v:.1f}m/s")
print()

print("=== 使用 csv 格式 ===")
csv_path = os.path.join(tmpdir, "experiment.csv")
with open(csv_path, "w", encoding="utf-8") as f:
    f.write("mass,acceleration,force\n")
    for m in [1.0, 2.0, 5.0, 10.0]:
        a = 9.8
        f.write(f"{m},{a},{m*a}\n")

with open(csv_path, "r", encoding="utf-8") as f:
    header = f.readline().strip()
    print(f"  表头: {header}")
    for line in f:
        m, a, force = line.strip().split(",")
        print(f"  m={m}kg, a={a}m/s², F={force}N")

os.unlink(filepath)
os.unlink(csv_path)
os.rmdir(tmpdir)
print(f"\n已清理临时文件")
