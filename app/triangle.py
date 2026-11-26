"""Draw triangles using stars and spaces.

Assumptions
1. m is the number of rows.
2. n is the maximum width any row can have in a triangle.
3. The required 3 x 4 triangle is left-aligned and has 3 rows. The widest row spans 4 columns.
4. Left-aligned rows start in the first column with no spaces before the first star. The rows gradually increase in width to the right.
5. For multiple rows, start with one star and grow to n stars in the filled triangle. If a calculated width falls between two whole numbers, round up to the nearest greater integer.
6. Repetition of rows is allowed.
7. The centered outline has an empty middle and a solid base.
8. An upside-down triangle uses the same rows in reverse order.
9. m and n must be positive whole numbers. Zero, negative numbers, decimals, and text are invalid.

Extra shapes outside the assessment requirements
- Right-aligned triangle, centered triangle outline, and upside-down triangles.
"""

from math import ceil


def triangle() -> str:
    """Return the required left-aligned 3 x 4 triangle."""
    # Give the bonus function the fixed dimensions of 3 rows and 4 columns.
    return triangle_mn(3, 4)


# Left-aligned rows start in column 1 with no spaces before the first star.
def triangle_mn(m: int, n: int) -> str:
    """Return a filled, left-aligned triangle for the given size."""
    # Check that both inputs are integers greater than zero.
    if type(m) is not int or type(n) is not int or min(m, n) <= 0:
        raise ValueError("m and n must be positive whole numbers.")

    # Count rows using i = 0 through i = m - 1.
    # Give a single row all n stars. Otherwise, start with one star and spread n - 1 extra stars across m - 1 steps, rounding up.
    # Repeat "*" to build each row and join the rows with line breaks.
    return "\n".join(
        "*" * (n if m == 1 else 1 + ceil(i * (n - 1) / (m - 1)))
        for i in range(m)
    )


# Right-aligned triangle
# Add spaces before the stars so the last star in every row lines up
# in the rightmost column. As you go down, the rows get wider to the left.
# Each row ends in the rightmost column and gets wider to the left as you go down the triangle.
def right_aligned(m: int, n: int) -> str:
    """Keep all the stars and line up the last star of every row."""
    # Build the filled triangle and split it into individual rows.
    rows = triangle_mn(m, n).splitlines()

    # Subtract the row's star count from n to get its leading spaces.
    # Add those spaces before the stars so each row ends in column n.
    return "\n".join(" " * (n - len(row)) + row for row in rows)


# Centered outline triangle
def centered_outline(m: int, n: int) -> str:
    """Return a symmetric centered outline with a solid base."""
    rows = triangle_mn(m, n).splitlines()
    outline = []

    for i, row in enumerate(rows):
        if i == len(rows) - 1:
            outline.append(row)
            continue

        # Use a width that leaves the same number of spaces on both sides.
        # Round mismatched widths down. Keep two tip stars for an even base.
        width = len(row)
        if (n - width) % 2:
            width = max(2, width - 1) if n % 2 == 0 else width - 1

        # Keep the outside stars and leave the middle empty.
        edge = "*" if width == 1 else "*" + " " * (width - 2) + "*"
        outline.append(" " * ((n - width) // 2) + edge)

    return "\n".join(outline)


# Upside-down left-aligned triangle
def upside_down_left_aligned(m: int, n: int) -> str:
    """Return the left-aligned triangle with its widest row at the top."""
    # Build the filled left-aligned triangle.
    # Reverse its rows so the last row appears first.
    return flip_down(triangle_mn(m, n))


# Upside-down right-aligned triangle
def upside_down_right_aligned(m: int, n: int) -> str:
    """Return the right-aligned triangle with its widest row at the top."""
    # Build the right-aligned triangle with its leading spaces.
    # Reverse the rows. Each row keeps its leading spaces.
    return flip_down(right_aligned(m, n))


# Upside-down centered outline
def upside_down_centered_outline(m: int, n: int) -> str:
    """Return the centered outline with its solid row at the top."""
    # Build the upright centered outline.
    # Reverse the rows so the base appears first and the tip last.
    return flip_down(centered_outline(m, n))


def flip_down(triangle_text: str) -> str:
    """Reverse the rows while keeping the stars and spaces in each row."""
    # Split the triangle text into individual rows.
    rows = triangle_text.splitlines()

    # Read the rows from last to first and join them with line breaks.
    return "\n".join(reversed(rows))


if __name__ == "__main__":
    print("Required 3 x 4 left-aligned triangle:")
    print(triangle())

    print("\nEnter a size for the bonus triangles.")
    try:
        # Read both entries before converting and validating them.
        m_text = input("Enter m (number of rows): ")
        n_text = input("Enter n (maximum width): ")
        m, n = int(m_text), int(n_text)
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
        print("Error: m and n need to be positive whole integers.")
