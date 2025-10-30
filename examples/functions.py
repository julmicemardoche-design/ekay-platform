# Learn about Functions in Python

# === BASIC FUNCTIONS ===
print("=== BASIC FUNCTIONS ===\n")

def greet(name):
    """Greet someone by name"""
    return f"Hello, {name}!"

def add_numbers(a, b):
    """Add two numbers together"""
    return a + b

def calculate_area(length, width):
    """Calculate area of a rectangle"""
    return length * width

# Using functions
print(greet("Alice"))
print(f"5 + 3 = {add_numbers(5, 3)}")
print(f"Area of 4x5 rectangle: {calculate_area(4, 5)}")

# === FUNCTIONS WITH DEFAULT PARAMETERS ===
print("\n=== DEFAULT PARAMETERS ===\n")

def introduce(name, age=25, city="Unknown"):
    """Introduce a person with optional parameters"""
    return f"{name} is {age} years old and lives in {city}."

print(introduce("Bob"))
print(introduce("Carol", 30))
print(introduce("Dave", 28, "New York"))

# === FUNCTIONS THAT RETURN MULTIPLE VALUES ===
print("\n=== MULTIPLE RETURN VALUES ===\n")

def get_stats(numbers):
    """Return min, max, and average of a list"""
    return min(numbers), max(numbers), sum(numbers) / len(numbers)

data = [10, 20, 30, 40, 50]
minimum, maximum, average = get_stats(data)
print(f"Data: {data}")
print(f"Min: {minimum}, Max: {maximum}, Average: {average}")

# === LAMBDA FUNCTIONS ===
print("\n=== LAMBDA FUNCTIONS ===\n")

# Lambda = small anonymous function
square = lambda x: x ** 2
add = lambda x, y: x + y

print(f"Square of 5: {square(5)}")
print(f"Add 3 and 7: {add(3, 7)}")

# Lambda with map
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(f"Original: {numbers}")
print(f"Squared: {squared}")

# === RECURSIVE FUNCTIONS ===
print("\n=== RECURSIVE FUNCTIONS ===\n")

def factorial(n):
    """Calculate factorial recursively"""
    if n <= 1:
        return 1
    return n * factorial(n - 1)

def fibonacci(n):
    """Calculate nth Fibonacci number"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

print(f"Factorial of 5: {factorial(5)}")
print(f"First 10 Fibonacci numbers: {[fibonacci(i) for i in range(10)]}")
