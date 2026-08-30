well_depth = 15
height = 0
day = 0
height_after_day_10 = None

while True:
    day += 1

    if day % 4 != 0:
        height += 5

    print("Day %d daytime: height = %d m" % (day, height))

    if height >= well_depth:
        break

    height -= 3
    print("Day %d night:   height = %d m" % (day, height))

    if day == 10:
        height_after_day_10 = height

assert day == 11
assert height_after_day_10 == 10
assert height >= well_depth

print("The snail reaches the rim on day %d." % day)
print("Validation passed: it was still below the rim after day 10.")
