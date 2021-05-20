def is_equal(x, y, tolerance=0.1):
    return abs(x - y) < tolerance


def is_smaller(x, y):
    return x < y


def is_larger(x, y):
    return x > y