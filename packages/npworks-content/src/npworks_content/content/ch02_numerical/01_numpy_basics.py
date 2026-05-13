# -*- coding: utf-8 -*-
# 2.1 NumPy 基础
# 学习 NumPy 数组创建、切片和运算

import numpy as np

print("=== 数组创建 ===")
a = np.array([1, 2, 3, 4, 5])
print(f"一维数组: {a}")
print(f"类型: {type(a)}, dtype: {a.dtype}, shape: {a.shape}")

b = np.zeros(5)
print(f"零数组: {b}")

c = np.ones((3, 3))
print(f"3x3 全1矩阵:\n{c}")

d = np.linspace(0, 2 * np.pi, 5)
print(f"等间距数组 [0, 2π]: {d}")

e = np.arange(0, 10, 2)
print(f"步长数组 [0,10,2): {e}")
print()

print("=== 数组运算 ===")
x = np.array([1.0, 2.0, 3.0, 4.0])
y = np.array([5.0, 6.0, 7.0, 8.0])
print(f"x = {x}")
print(f"y = {y}")
print(f"x + y = {x + y}")
print(f"x * y = {x * y}")
print(f"x ** 2 = {x ** 2}")
print(f"np.sqrt(x) = {np.sqrt(x)}")
print(f"np.sin(x) = {np.sin(x)}")
print()

print("=== 统计函数 ===")
data = np.random.randn(1000)
print(f"样本数: {len(data)}")
print(f"均值: {np.mean(data):.4f}")
print(f"标准差: {np.std(data):.4f}")
print(f"最小值: {np.min(data):.4f}")
print(f"最大值: {np.max(data):.4f}")
print()

print("=== 矩阵运算 ===")
A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])
print(f"A =\n{A}")
print(f"B =\n{B}")
print(f"A @ B =\n{A @ B}")
print(f"A的逆 =\n{np.linalg.inv(A)}")
print(f"A的行列式 = {np.linalg.det(A):.2f}")
eigvals, eigvecs = np.linalg.eig(A)
print(f"A的特征值 = {eigvals}")
