filename = r"c:\Users\sande\AppData\Local\Programs\Python\Python311\Lib\site-packages\google\adk\cli\cli_tools_click.py"
with open(filename, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "get_fast_api_app" in line and "import" in line:
            print(f"{i+1}: {line.strip()}")
        if i > 100: # Imports should be at the top
            break
