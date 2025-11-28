import google.adk.apps
import pkgutil

print("Inspecting google.adk.apps...")
package = google.adk.apps
for loader, name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
    print(f"  {name}")
