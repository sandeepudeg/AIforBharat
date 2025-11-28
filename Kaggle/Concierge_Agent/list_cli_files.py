import os

root_path = r"c:\Users\sande\AppData\Local\Programs\Python\Python311\Lib\site-packages\google\adk\cli"

print(f"Listing files in {root_path}...")
for root, dirs, files in os.walk(root_path):
    for file in files:
        if file.endswith(".py"):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, root_path)
            print(rel_path)
