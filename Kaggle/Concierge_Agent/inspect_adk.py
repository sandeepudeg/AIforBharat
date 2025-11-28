import google.adk
import os
import pkgutil

package = google.adk
print(f"Package: {package.__name__}")
print(f"Path: {package.__path__}")

print("\nSubmodules:")
for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
    print(f"  {name} {'(pkg)' if is_pkg else ''}")
