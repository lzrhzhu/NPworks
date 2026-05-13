# -*- coding: utf-8 -*-
# 1.3 控制流
# 学习 if/else、for 循环、while 循环

print("=== if/else 条件判断 ===")
speed = 3.0e8
if speed > 1.0e8:
    print(f"速度 {speed:.1e} m/s 超过 1e8 m/s")
elif speed > 1.0e6:
    print(f"速度 {speed:.1e} m/s 在正常范围")
else:
    print("低速运动")
print()

print("=== for 循环 ===")
temperatures = [273.15, 300, 373.15, 500]
for t in temperatures:
    celsius = t - 273.15
    print(f"  {t:.2f} K = {celsius:.2f} °C")
print()

print("=== while 循环: 放射性衰变 ===")
n_atoms = 1000
half_life = 5.0
dt = 1.0
decay_constant = 0.693 / half_life
t = 0.0
print(f"时间=0.0年, 剩余原子数={n_atoms}")
while n_atoms > 100:
    n_atoms = int(n_atoms * (1 - decay_constant * dt))
    t += dt
    print(f"时间={t:.1f}年, 剩余原子数={n_atoms}")
print()

print("=== 列表推导式 ===")
squares = [x**2 for x in range(1, 11)]
print(f"1-10 的平方: {squares}")
evens = [x for x in range(20) if x % 2 == 0]
print(f"0-19 中的偶数: {evens}")
