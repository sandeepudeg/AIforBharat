try:
    import google.adk.cli
    print("google.adk.cli exists")
    import pkgutil
    for loader, name, is_pkg in pkgutil.walk_packages(google.adk.cli.__path__, google.adk.cli.__name__ + "."):
        print(f"  {name}")
except ImportError:
    print("google.adk.cli does NOT exist")
