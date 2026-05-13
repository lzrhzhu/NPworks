# -*- coding: utf-8 -*-
# 1.4 函数
# 学习函数定义、参数和返回值

def kinetic_energy(mass, velocity):
    return 0.5 * mass * velocity ** 2

def potential_energy(mass, height, g=9.8):
    return mass * g * height

def free_fall_time(height, g=9.8):
    return (2 * height / g) ** 0.5

print("=== 动能计算 ===")
m = 1.0
for v in [1, 5, 10, 20, 50]:
    ke = kinetic_energy(m, v)
    print(f"  质量={m}kg, 速度={v}m/s, 动能={ke:.2f}J")
print()

print("=== 自由落体 ===")
h = 100
t = free_fall_time(h)
pe = potential_energy(m, h)
print(f"  高度={h}m, 落地时间={t:.4f}s")
print(f"  初始势能={pe:.2f}J, 落地动能={kinetic_energy(m, 2*g*h/2):.2f}J")
print()

print("=== 装饰器: 计时函数执行 ===")
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"  {func.__name__} 耗时: {elapsed:.6f}s")
        return result
    return wrapper

@timer
def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

result = fibonacci(1000)
print(f"  fibonacci(1000) = {result}")
