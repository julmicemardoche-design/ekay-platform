# Python Quick Reference Guide

## 🐍 Running Python Code

### Method 1: Terminal
```bash
python filename.py
```

### Method 2: VS Code
- Press **F5** - Run with debugger
- Press **Ctrl + F5** - Run without debugger
- Press **Ctrl + Alt + N** - Quick run (Code Runner extension)

---

## 📝 Basic Syntax

### Print Output
```python
print("Hello!")
print(f"My name is {name}")  # F-string (formatted)
```

### Variables
```python
name = "Alice"      # String
age = 25            # Integer
height = 5.6        # Float
is_active = True    # Boolean
```

### Comments
```python
# Single line comment

"""
Multi-line comment
or docstring
"""
```

---

## 🔢 Data Types

### Strings
```python
text = "Hello"
text.upper()        # "HELLO"
text.lower()        # "hello"
len(text)           # 5
text[0]             # "H"
text + " World"     # "Hello World"
```

### Numbers
```python
x = 10
y = 3
x + y    # 13 (addition)
x - y    # 7 (subtraction)
x * y    # 30 (multiplication)
x / y    # 3.33 (division)
x // y   # 3 (integer division)
x % y    # 1 (remainder/modulo)
x ** y   # 1000 (power)
```

### Lists (Arrays)
```python
fruits = ["apple", "banana", "cherry"]
fruits[0]           # "apple"
fruits[-1]          # "cherry" (last item)
fruits.append("date")   # Add item
fruits.remove("banana") # Remove item
len(fruits)         # Number of items
```

### Dictionaries (Key-Value Pairs)
```python
person = {"name": "Alice", "age": 25}
person["name"]      # "Alice"
person["age"]       # 25
person["city"] = "NYC"  # Add new key
```

---

## 🔁 Control Flow

### If Statements
```python
if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")
```

### For Loops
```python
# Loop through list
for fruit in fruits:
    print(fruit)

# Loop with range
for i in range(5):      # 0 to 4
    print(i)

# Loop with index
for i, fruit in enumerate(fruits):
    print(f"{i}: {fruit}")
```

### While Loops
```python
count = 0
while count < 5:
    print(count)
    count += 1
```

---

## 🎯 Functions

### Basic Function
```python
def greet(name):
    return f"Hello, {name}!"

result = greet("Alice")  # "Hello, Alice!"
```

### Default Parameters
```python
def introduce(name, age=25):
    return f"{name} is {age}"

introduce("Bob")         # "Bob is 25"
introduce("Carol", 30)   # "Carol is 30"
```

### Multiple Return Values
```python
def get_stats(numbers):
    return min(numbers), max(numbers)

minimum, maximum = get_stats([1, 2, 3, 4, 5])
```

---

## 📥 User Input

```python
name = input("Enter your name: ")
age = int(input("Enter your age: "))
height = float(input("Enter your height: "))
```

---

## 📦 List Comprehension

```python
# Square numbers
squares = [x**2 for x in range(5)]  # [0, 1, 4, 9, 16]

# Filter even numbers
evens = [x for x in numbers if x % 2 == 0]
```

---

## 🛠️ Useful Built-in Functions

```python
len(list)           # Length
sum(numbers)        # Sum of all items
min(numbers)        # Minimum value
max(numbers)        # Maximum value
sorted(list)        # Sort list
range(5)            # 0, 1, 2, 3, 4
type(variable)      # Get type
str(123)            # Convert to string
int("123")          # Convert to integer
float("3.14")       # Convert to float
```

---

## ⚠️ Error Handling

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")
except Exception as e:
    print(f"Error: {e}")
```

---

## 📚 Common Operators

### Comparison
```python
==    # Equal to
!=    # Not equal to
>     # Greater than
<     # Less than
>=    # Greater than or equal
<=    # Less than or equal
```

### Logical
```python
and   # Both conditions true
or    # At least one condition true
not   # Opposite
```

---

## 💡 Quick Tips

1. **Indentation matters!** Use 4 spaces
2. **Variables are case-sensitive** (`name` ≠ `Name`)
3. **Lists start at index 0**
4. **Use f-strings for formatting**: `f"Hello {name}"`
5. **Practice with `print()`** to see what's happening

---

**Happy Coding! 🐍**
