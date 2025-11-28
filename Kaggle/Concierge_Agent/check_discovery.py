try:
    import google.adk.cli.discovery
    print("✅ google.adk.cli.discovery exists")
    if hasattr(google.adk.cli.discovery, 'register_agent'):
        print("✅ register_agent FOUND")
    else:
        print("❌ register_agent NOT found")
        print("Contents:", dir(google.adk.cli.discovery))
except ImportError:
    print("❌ google.adk.cli.discovery does NOT exist")
