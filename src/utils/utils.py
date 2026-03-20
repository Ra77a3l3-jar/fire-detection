def full_inside(inner, outer):
    x1a, y1a, x2a, y2a = inner
    x1b, y1b, x2b, y2b = outer

    return (
        x1a >= x1b and
        y1a >= y1b and
        x2a <= x2b and
        y2a <= y2b
    )
