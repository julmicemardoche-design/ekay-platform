# C++ Development Setup Guide for Windows Beginners

## Step 1: Install C++ Compiler

### Method A: MSYS2 with MinGW-w64 (Recommended for Beginners)

1. **Download MSYS2:**
   - Visit: https://www.msys2.org/
   - Download the installer (msys2-x86_64-YYYYMMDD.exe)
   - Run the installer and follow the defaults

2. **Install MinGW-w64 GCC:**
   - Open "MSYS2 UCRT64" from Start Menu
   - Run these commands one by one:
   ```bash
   pacman -Syu
   # Press Y when asked, close the terminal when it finishes
   # Open MSYS2 UCRT64 again, then run:
   pacman -S mingw-w64-ucrt-x86_64-gcc
   pacman -S mingw-w64-ucrt-x86_64-gdb
   ```

3. **Add to PATH:**
   - Search "Environment Variables" in Windows Start Menu
   - Click "Environment Variables" button
   - Under "System variables", find and select "Path", click "Edit"
   - Click "New" and add: `C:\msys64\ucrt64\bin`
   - Click OK on all windows
   - **Restart VS Code**

4. **Verify Installation:**
   Open a new terminal and run:
   ```powershell
   g++ --version
   gdb --version
   ```

### Method B: Visual Studio Build Tools (Alternative)

1. Download from: https://visualstudio.microsoft.com/downloads/
2. Under "All Downloads" → "Tools for Visual Studio" → "Build Tools for Visual Studio 2022"
3. Install with "Desktop development with C++" workload

## Step 2: Install VS Code C++ Extensions

Install these extensions in VS Code:
1. **C/C++** (by Microsoft) - IntelliSense, debugging, and code browsing
2. **C/C++ Extension Pack** (by Microsoft) - Complete C++ development toolkit
3. **Code Runner** (by Jun Han) - Quick code execution

### To install extensions:
- Press `Ctrl+Shift+X` to open Extensions
- Search for each extension name
- Click "Install"

## Step 3: Test Your Setup

After installing the compiler and extensions, try compiling the sample programs I've created:

```powershell
# Navigate to your C++ project
cd cpp-projects

# Compile and run the hello world program
g++ -o hello hello.cpp
./hello

# Or use the shortcut: press Ctrl+Alt+N in VS Code (Code Runner)
```

## Quick Reference

### Compile C++ file:
```bash
g++ filename.cpp -o outputname
```

### Compile with C++17 standard:
```bash
g++ -std=c++17 filename.cpp -o outputname
```

### Compile with warnings enabled:
```bash
g++ -Wall -Wextra filename.cpp -o outputname
```

### Run the compiled program:
```bash
./outputname          # On MSYS2
outputname.exe        # On PowerShell
```

## Learning Resources

- **LearnCpp.com** - Comprehensive free C++ tutorial
- **CPlusPlus.com** - Language reference and tutorials
- **GeeksforGeeks C++** - Examples and practice problems
- **YouTube: The Cherno C++** - Excellent video series

## Common Issues

### "g++ is not recognized"
- Make sure you added the correct path to your environment variables
- Restart your terminal/VS Code after adding to PATH
- Verify path exists: `C:\msys64\ucrt64\bin`

### "Cannot open source file"
- Make sure you're in the correct directory
- Check file name spelling (C++ is case-sensitive)

### Compilation errors
- Check syntax carefully
- Make sure to include necessary headers like `<iostream>`
- Every statement needs a semicolon `;`

---

**Good luck with your C++ journey! 🚀**
