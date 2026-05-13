# -*- coding: utf-8 -*-
# 1.2 变量与数据类型
# 学习 Python 中的基本数据类型

a = 42
b = 3.14
c = "Hello, Physics!"
d = True
e = [1, 2, 3, 4, 5]

print("整数 (int):", a, type(a))
print("浮点数 (float):", b, type(b))
print("字符串 (str):", c, type(c))
print("布尔值 (bool):", d, type(d))
print("列表 (list):", e, type(e))
print()

x = 10
y = 3
print(f"加法: {x} + {y} = {x + y}")
print(f"减法: {x} - {y} = {x - y}")
print(f"乘法: {x} * {y} = {x * y}")
print(f"除法: {x} / {y} = {x / y:.4f}")
print(f"整除: {x} // {y} = {x // y}")
print(f"取余: {x} % {y} = {x % y}")
print(f"幂运算: {x} ** {y} = {x ** y}")
print()

physics_constants = {
    "光速 c": 3.0e8,
    "万有引力常数 G": 6.674e-11,
    "普朗克常数 h": 6.626e-34,
    "电子电荷 e": 1.602e-19,
}
print("物理常数:")
for name, value in physics_constants.items():
    print(f"  {name} = {value:.3e}")
