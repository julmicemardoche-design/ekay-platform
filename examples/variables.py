# Learn about Python variables and data types

# Different variable types (Python automatically detects the type!)
name = "Alice"           # String
age = 25                 # Integer
height = 5.6             # Float
is_student = True        # Boolean
hobbies = ["coding", "reading", "gaming"]  # List
person = {"name": "Bob", "age": 30}        # Dictionary

# Print variables
print("=== Python Variables ===")
print(f"Name: {name} (type: {type(name).__name__})")
print(f"Age: {age} (type: {type(age).__name__})")
print(f"Height: {height} (type: {type(height).__name__})")
print(f"Is Student: {is_student} (type: {type(is_student).__name__})")
print(f"Hobbies: {hobbies} (type: {type(hobbies).__name__})")
print(f"Person: {person} (type: {type(person).__name__})")

# String operations
print("\n=== String Operations ===")
greeting = "Hello"
full_greeting = greeting + ", " + name + "!"  # Concatenation
print(full_greeting)
print(name.upper())  # Uppercase
print(name.lower())  # Lowercase
print(f"Name length: {len(name)}")

# Math operations
print("\n=== Math Operations ===")
x = 10
y = 3
print(f"{x} + {y} = {x + y}")
print(f"{x} - {y} = {x - y}")
print(f"{x} * {y} = {x * y}")
print(f"{x} / {y} = {x / y}")
print(f"{x} // {y} = {x // y} (integer division)")
print(f"{x} % {y} = {x % y} (remainder)")
print(f"{x} ** {y} = {x ** y} (power)")
