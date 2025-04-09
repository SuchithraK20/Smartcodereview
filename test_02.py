def add_numbers(a, b):
    result = a + b
    return result

def subtract_numbers(a, b):
    result = a - b
    return result

def multiply_numbers(a, b):
    result = a * b
    return result

def divide_numbers(a, b):
    if b == 0:
        return "Error: Division by zero"
    result = a / b
    return result

def main():
    x = 10
    y = 5

    print(f"Addition: {add_numbers(x, y)}")
    print(f"Subtraction: {subtract_numbers(x, y)}")
    print(f"Multiplication: {multiply_numbers(x, y)}")
    print(f"Division: {divide_numbers(x, y)}")

if __name__ == "__main__":
    main()
