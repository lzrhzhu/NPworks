def is_prime(n):
    """Return True when n is a prime number."""
    if n < 2:
        return False

    divisor = 2
    while divisor * divisor <= n:
        if n % divisor == 0:
            return False
        divisor += 1
    return True


primes = [n for n in range(2, 101) if is_prime(n)]

# 两个独立的基准检查：局部序列与总个数。
assert primes[:5] == [2, 3, 5, 7, 11]
assert len(primes) == 25

print("Primes from 2 to 100:")
print(primes)
print("Validation passed: 25 primes found.")
