# C++ Debugging with GDB - Quick Reference

## Installation Steps (Run After MSYS2 Installs)

### 1. Open MSYS2 UCRT64 Terminal
- Press Windows key and search for "MSYS2 UCRT64"
- Open the terminal

### 2. Install GCC and GDB
```bash
# Update package database
pacman -Syu
# Press Y when prompted, then close terminal when it asks

# Reopen MSYS2 UCRT64 and install compiler + debugger
pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-gdb
```

### 3. Add to Windows PATH
1. Press Windows key → type "Environment Variables"
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "System variables", select "Path" → click "Edit"
5. Click "New" → add: `C:\msys64\ucrt64\bin`
6. Click OK on all windows
7. **Restart VS Code**

### 4. Verify Installation
Open a new PowerShell terminal and run:
```powershell
g++ --version
gdb --version
```

---

## GDB Debugging Commands

### Compile with Debug Symbols
```bash
# Compile with -g flag to include debug information
g++ -g -o program program.cpp
```

### Starting GDB
```bash
# Start debugging a program
gdb program.exe

# Or run with arguments
gdb --args program.exe arg1 arg2
```

### Essential GDB Commands

#### Running the Program
```gdb
run                    # Start the program
run arg1 arg2         # Start with arguments
continue (or c)       # Continue execution after stopping
quit (or q)           # Exit GDB
```

#### Breakpoints
```gdb
break main            # Break at function 'main'
break file.cpp:25     # Break at line 25 of file.cpp
break function_name   # Break at start of function
info breakpoints      # List all breakpoints
delete 1              # Delete breakpoint #1
delete                # Delete all breakpoints
```

#### Stepping Through Code
```gdb
next (or n)           # Execute next line (step over functions)
step (or s)           # Execute next line (step into functions)
finish                # Run until current function returns
until 50              # Run until line 50
```

#### Examining Variables
```gdb
print variable        # Print value of variable
print *pointer        # Dereference and print pointer
print array[0]        # Print array element
display variable      # Auto-display variable after each step
info locals           # Show all local variables
info args             # Show function arguments
```

#### Call Stack
```gdb
backtrace (or bt)     # Show call stack
frame 2               # Switch to stack frame #2
up                    # Move up one stack frame
down                  # Move down one stack frame
```

#### Watchpoints (Break on Variable Change)
```gdb
watch variable        # Break when variable changes
info watchpoints      # List all watchpoints
```

---

## Debugging in VS Code

### Setup (One-Time)

1. **Install VS Code Extensions:**
   - C/C++ (by Microsoft)
   - C/C++ Extension Pack (by Microsoft)

2. **Create Debug Configuration:**
   - Press `F5` or go to Run → Start Debugging
   - Select "C++ (GDB/LLDB)"
   - Choose "g++.exe - Build and debug active file"

This creates `.vscode/launch.json` and `.vscode/tasks.json`

### Using VS Code Debugger

- **F5** - Start debugging
- **F9** - Toggle breakpoint on current line
- **F10** - Step over (next line)
- **F11** - Step into (enter function)
- **Shift+F11** - Step out (exit function)
- **Ctrl+Shift+F5** - Restart debugging
- **Shift+F5** - Stop debugging

### Debug Panel Features
- **Variables** - View and inspect variables
- **Watch** - Add expressions to monitor
- **Call Stack** - Navigate function calls
- **Breakpoints** - Manage all breakpoints

---

## Example: Debugging Session

### Sample buggy program (test.cpp):
```cpp
#include <iostream>
using namespace std;

int divide(int a, int b) {
    return a / b;  // Bug: no check for b == 0
}

int main() {
    int x = 10;
    int y = 0;
    int result = divide(x, y);  // This will crash
    cout << "Result: " << result << endl;
    return 0;
}
```

### Debug it with GDB:
```bash
# Compile with debug symbols
g++ -g -o test test.cpp

# Start GDB
gdb test.exe

# In GDB:
(gdb) break divide         # Set breakpoint at divide function
(gdb) run                  # Run the program
(gdb) print a              # Check value of a
(gdb) print b              # Check value of b (will be 0!)
(gdb) next                 # Step to the division (will crash)
```

---

## Common Debugging Scenarios

### Segmentation Fault / Access Violation
```gdb
run                        # Run until crash
backtrace                  # See where it crashed
frame 0                    # Go to crash location
info locals                # Check local variables
print suspicious_pointer   # Check pointer values
```

### Logic Error (Wrong Output)
```gdb
break main                 # Start at main
run                        # Run to breakpoint
next                       # Step through code
print variable             # Check values at each step
```

### Infinite Loop
```gdb
run                        # Start program
Ctrl+C                     # Interrupt the loop
backtrace                  # See where you are
print loop_variable        # Check loop condition
```

---

## Tips for Effective Debugging

1. **Always compile with `-g` flag** for debugging
2. **Use `-Wall -Wextra`** flags to catch warnings
3. **Set breakpoints early** (like at main)
4. **Print/watch suspicious variables**
5. **Use backtrace** when program crashes
6. **Step through slowly** to understand flow

### Complete Compile Command for Debugging:
```bash
g++ -g -Wall -Wextra -std=c++17 -o program program.cpp
```

---

## Quick Reference Card

| Task | GDB Command | VS Code |
|------|-------------|---------|
| Start debugging | `gdb program.exe` | F5 |
| Set breakpoint | `break line_num` | F9 |
| Run/Continue | `run` / `continue` | F5 |
| Step over | `next` | F10 |
| Step into | `step` | F11 |
| Step out | `finish` | Shift+F11 |
| Print variable | `print var` | Hover/Watch |
| Show stack | `backtrace` | Call Stack panel |
| Quit | `quit` | Shift+F5 |

---

**Happy Debugging! 🐛🔍**
