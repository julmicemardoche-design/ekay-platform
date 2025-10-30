# Learn about Lists and Loops in Python

# === LISTS ===
print("=== WORKING WITH LISTS ===\n")

# Creating a list
fruits = ["apple", "banana", "cherry", "date"]
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

print(f"Fruits: {fruits}")
print(f"First fruit: {fruits[0]}")
print(f"Last fruit: {fruits[-1]}")
print(f"Number of fruits: {len(fruits)}")

# Adding to a list
fruits.append("elderberry")
print(f"After adding: {fruits}")

# Removing from a list
fruits.remove("banana")
print(f"After removing banana: {fruits}")

# === FOR LOOPS ===
print("\n=== FOR LOOPS ===\n")

# Loop through a list
print("My favorite fruits:")
for fruit in fruits:
    print(f"  - {fruit.capitalize()}")

# Loop with range
print("\nCounting to 5:")
for i in range(1, 6):
    print(i, end=" ")
print()

# Loop with index
print("\nFruits with index:")
for index, fruit in enumerate(fruits):
    print(f"{index + 1}. {fruit}")

# === WHILE LOOPS ===
print("\n=== WHILE LOOPS ===\n")

countdown = 5
print("Countdown:")
while countdown > 0:
    print(countdown, end=" ")
    countdown -= 1
print("Blast off! 🚀")

# === LIST COMPREHENSION ===
print("\n=== LIST COMPREHENSION ===\n")

# Square numbers
squares = [x**2 for x in range(1, 6)]
print(f"Squares of 1-5: {squares}")

# Filter even numbers
evens = [x for x in numbers if x % 2 == 0]
print(f"Even numbers: {evens}")

# === WORKING WITH NUMBERS ===
print("\n=== NUMBER OPERATIONS ===\n")

print(f"Sum of numbers 1-10: {sum(numbers)}")
print(f"Minimum: {min(numbers)}")
print(f"Maximum: {max(numbers)}")
print(f"Average: {sum(numbers) / len(numbers)}")
