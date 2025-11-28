import google.adk
import pkgutil
import importlib
import inspect
import sys

def find_function(package, func_name):
    print(f"Searching for {func_name} in {package.__name__}...")
    
    # Walk through all modules
    path = package.__path__
    prefix = package.__name__ + "."
    
    for loader, name, is_pkg in pkgutil.walk_packages(path, prefix):
        try:
            module = importlib.import_module(name)
            if hasattr(module, func_name):
                print(f"✅ FOUND in module: {name}")
                return
        except Exception as e:
            # print(f"  Skipping {name}: {e}")
            pass
            
    print("❌ Not found in any submodule.")

if __name__ == "__main__":
    find_function(google.adk, "create_web_app")
