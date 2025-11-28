try:
    import google.adk.cli.fast_api
    print("✅ google.adk.cli.fast_api exists")
    print("Contents:", dir(google.adk.cli.fast_api))
except ImportError:
    print("❌ google.adk.cli.fast_api does NOT exist")
