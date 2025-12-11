"""Example Python file for demonstrations.

This file shows some sample Python code that can be opened
by the FileLink widget examples.
"""


def greet(name: str) -> str:
    """Greet someone by name.

    Args:
        name: The person's name

    Returns:
        A greeting message
    """
    return f"Hello, {name}!"


def add(a: int, b: int) -> int:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        The sum of a and b
    """
    return a + b


if __name__ == "__main__":
    print(greet("World"))
    print(f"2 + 3 = {add(2, 3)}")
