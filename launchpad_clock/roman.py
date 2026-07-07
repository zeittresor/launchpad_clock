"""Roman numeral conversion for the Launchpad clock."""

def to_roman(number: int) -> str:
    """Convert 0..59 to compact Roman numerals."""
    if number == 0:
        return "N"
    if not 0 <= number <= 59:
        raise ValueError("Roman clock supports values from 0 to 59.")

    values = [
        (50, "L"),
        (40, "XL"),
        (10, "X"),
        (9, "IX"),
        (5, "V"),
        (4, "IV"),
        (1, "I"),
    ]

    result = []
    remaining = number
    for value, symbol in values:
        while remaining >= value:
            result.append(symbol)
            remaining -= value
    return "".join(result)
