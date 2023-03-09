def get_place_values(n):
    return [int(value) * 10**place for place, value in enumerate(str(n)[::-1])]

print(get_place_values(10))