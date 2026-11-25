"""Draw triangles using stars and spaces.

Assumptions
- m is the number of rows. n is the width of the widest row.
- The required 3 x 4 triangle is left-aligned and has 3 rows.
  The widest row spans 4 columns.
- For multiple rows, start with one star and grow to n stars.
  Round up when a calculated row width falls between two whole numbers.
- Repetition of rows is allowed.
- The centered outline has an empty middle and a solid base.
- An upside-down triangle uses the same rows in reverse order.
- Both dimensions must be positive whole numbers.

Extra shapes outside the assessment requirements
- Right-aligned triangle, centered triangle outline, and upside-down triangles.
"""

from math import ceil


def triangle() -> str:
    """Return the required left-aligned 3 x 4 triangle."""
    # Give the bonus function the fixed dimensions of 3 rows and 4 columns.
    return triangle_mn(3, 4)


def triangle_mn(m: int, n: int) -> str:
    """Return a filled, left-aligned triangle for the given size."""
    # 1. Check that both inputs are integers greater than zero.
    if type(m) is not int or type(n) is not int or min(m, n) <= 0:
        raise ValueError("m and n must be positive whole numbers.")

    # 2. Count rows using i = 0 through i = m - 1.
    # 3. Give a single row all n stars. Otherwise, start with one star
    #    and spread n - 1 extra stars across m - 1 steps, rounding up.
    # 4. Repeat "*" to build each row and join the rows with line breaks.
    return "\n".join(
        "*" * (n if m == 1 else 1 + ceil(i * (n - 1) / (m - 1)))
        for i in range(m)
    )


# Right-aligned triangle
# Add spaces before the stars so the last star in every row lines up
# in the rightmost column. As you go down, the rows get wider to the left.
def right_aligned(m: int, n: int) -> str:
    """Keep all the stars and line up the last star of every row."""
    # 1. Build the filled triangle and split it into individual rows.
    rows = triangle_mn(m, n).splitlines()

    # 2. Subtract the row's star count from n to get its leading spaces.
    # 3. Add those spaces before the stars so each row ends in column n.
    return "\n".join(" " * (n - len(row)) + row for row in rows)


def centered_outline(m: int, n: int) -> str:
    """Return a centered triangle outline with a solid base."""
    # 1. Build the filled rows and make a list for the finished outline.
    rows = triangle_mn(m, n).splitlines()
    outline = []

    # 2. Read each row and its position, counting from zero.
    for i, row in enumerate(rows):
        # 3. Above the base, keep one star at each end of a row with
        #    at least two stars. Fill the len(row) - 2 positions between
        #    them with spaces. For example, "*****" becomes "*   *".
        if i < len(rows) - 1 and len(row) > 1:
            row = "*" + " " * (len(row) - 2) + "*"

        # 4. Center the row across n columns. Remove spaces after the
        #    last star and save the finished row.
        outline.append(row.center(n).rstrip())

    # 5. Put the saved rows on separate lines.
    return "\n".join(outline)


def upside_down_left_aligned(m: int, n: int) -> str:
    """Return the left-aligned triangle with its widest row at the top."""
    # 1. Build the filled left-aligned triangle.
    # 2. Reverse its rows so the last row appears first.
    return flip_down(triangle_mn(m, n))


def upside_down_right_aligned(m: int, n: int) -> str:
    """Return the right-aligned triangle with its widest row at the top."""
    # 1. Build the right-aligned triangle with its leading spaces.
    # 2. Reverse the rows. Each row keeps its leading spaces.
    return flip_down(right_aligned(m, n))


def upside_down_centered_outline(m: int, n: int) -> str:
    """Return the centered outline with its solid row at the top."""
    # 1. Build the upright centered outline.
    # 2. Reverse the rows so the base appears first and the tip last.
    return flip_down(centered_outline(m, n))


def flip_down(triangle_text: str) -> str:
    """Reverse the rows while keeping the stars and spaces in each row."""
    # 1. Split the triangle text into individual rows.
    rows = triangle_text.splitlines()

    # 2. Read the rows from last to first and join them with line breaks.
    return "\n".join(reversed(rows))


if __name__ == "__main__":
    print("Required 3 x 4 left-aligned triangle:")
    print(triangle())

    print("\nEnter a size for the bonus triangles.")
    try:
        # Check m before asking for n. int() rejects decimals and text.
        m = int(input("Enter m (number of rows): "))
        if m <= 0:
            raise ValueError("m must be a positive whole number.")

        # Read n. triangle_mn() checks that both dimensions are positive.
        n = int(input("Enter n (maximum width): "))
        left = triangle_mn(m, n)

        print("\nBonus left-aligned triangle:")
        print(left)

        print("\nRight-aligned triangle:")
        print(right_aligned(m, n))

        print("\nCentered triangle outline:")
        print(centered_outline(m, n))

        print("\nUpside-down left-aligned triangle:")
        print(upside_down_left_aligned(m, n))

        print("\nUpside-down right-aligned triangle:")
        print(upside_down_right_aligned(m, n))

        print("\nUpside-down centered triangle outline:")
        print(upside_down_centered_outline(m, n))

    except ValueError:
        print("Error: m and n must be positive whole numbers.")
