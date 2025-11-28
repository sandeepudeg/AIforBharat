filename = r"c:\Users\sande\AppData\Local\Programs\Python\Python311\Lib\site-packages\google\adk\cli\fast_api.py"
with open(filename, 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "def get_fast_api_app" in line:
            print(f"{i+1}: {line.strip()}")
            for j in range(1, 20):
                if i+j < len(lines):
                    print(f"{i+1+j}: {lines[i+j].rstrip()}")
            break
