# Simple Calculator with user input

def calculator():
    print("=" * 40)
    print("       PYTHON CALCULATOR")
    print("=" * 40)
    
    try:
        # Get user input
        num1 = float(input("\nEnter first number: "))
        operator = input("Enter operator (+, -, *, /): ")
        num2 = float(input("Enter second number: "))
        
        # Perform calculation
        print("\nResult: ", end="")
        
        if operator == '+':
            print(f"{num1} + {num2} = {num1 + num2}")
        elif operator == '-':
            print(f"{num1} - {num2} = {num1 - num2}")
        elif operator == '*':
            print(f"{num1} * {num2} = {num1 * num2}")
        elif operator == '/':
            if num2 != 0:
                print(f"{num1} / {num2} = {num1 / num2}")
            else:
                print("Error: Cannot divide by zero!")
        else:
            print("Error: Invalid operator!")
    
    except ValueError:
        print("Error: Please enter valid numbers!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    calculator()
