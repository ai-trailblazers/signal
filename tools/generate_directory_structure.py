import os

def generate_directory_structure(startpath, output_file, exclude_paths=None):
    with open(output_file, 'w') as f:
        for root, dirs, files in os.walk(startpath):
            # Skip paths in the exclude list
            if exclude_paths and any(excluded in root for excluded in exclude_paths):
                continue
            
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            f.write(f"{indent}{os.path.basename(root)}/\n")
            subindent = ' ' * 4 * (level + 1)
            for file in files:
                f.write(f"{subindent}{file}\n")

# Define the list of paths to exclude
exclude_paths = ['venv', '.git']

startpath = '.'
output_file = 'assets/diagrams/directory_structure.txt'
generate_directory_structure(startpath, output_file, exclude_paths)
