# Read the file
with open('complete_system_solver.py', 'r') as f:
    lines = f.readlines()

# Find and modify the CompleteSystemSolver __init__ method
in_class = False
in_init = False
init_indent = 0

for i, line in enumerate(lines):
    if 'class CompleteSystemSolver' in line:
        in_class = True
    elif in_class and 'def __init__' in line:
        in_init = True
        # Find the indentation level
        init_indent = len(line) - len(line.lstrip())
    elif in_init and line.strip() and (len(line) - len(line.lstrip())) <= init_indent:
        # We've reached the end of the __init__ method
        break
    elif in_init and 'super().__init__(' in line:
        # Found the super() call - modify it
        if 'grid_size, domain_size' in line:
            # Add dim parameter to both the method definition and super call
            # First, find the method definition and add dim parameter
            for j in range(i-5, i):
                if 'def __init__' in lines[j]:
                    # Add dim parameter to method signature
                    if 'tau=1.0):' in lines[j]:
                        lines[j] = lines[j].replace('tau=1.0):', 'tau=1.0, dim=2):')
                    elif 'tau=1.0):' in lines[j+1]:
                        lines[j+1] = lines[j+1].replace('tau=1.0):', 'tau=1.0, dim=2):')
            
            # Now modify the super() call
            lines[i] = lines[i].replace('super().__init__(grid_size,', 'super().__init__(dim, grid_size,')
        break

# Write the modified content back
with open('complete_system_solver.py', 'w') as f:
    f.writelines(lines)

print("Fixed CompleteSystemSolver class")
