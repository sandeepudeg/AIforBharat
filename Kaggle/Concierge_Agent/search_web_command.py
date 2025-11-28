filename = r"c:\Users\sande\AppData\Local\Programs\Python\Python311\Lib\site-packages\google\adk\cli\cli_tools_click.py"
with open(filename, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "def web(" in line or "@main.command" in line:
            print(f"{i+1}: {line.strip()}")
            # Print next few lines if it's the web command
            if "def web(" in line:
                for j in range(1, 20):
                    if i+j < len(lines):
                        print(f"{i+1+j}: {lines[i+j].strip()}")
