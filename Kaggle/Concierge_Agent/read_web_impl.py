filename = r"c:\Users\sande\AppData\Local\Programs\Python\Python311\Lib\site-packages\google\adk\cli\cli_tools_click.py"
with open(filename, 'r') as f:
    lines = f.readlines()
    for i in range(1075, 1150):
        if i < len(lines):
            print(f"{i+1}: {lines[i].rstrip()}")
