try:
    import google.adk.cli.fast_api_agents
    print("✅ google.adk.cli.fast_api_agents exists")
    if hasattr(google.adk.cli.fast_api_agents, 'create_web_app'):
        print("✅ create_web_app FOUND in google.adk.cli.fast_api_agents")
    else:
        print("❌ create_web_app NOT found in google.adk.cli.fast_api_agents")
        print("Contents:", dir(google.adk.cli.fast_api_agents))
except ImportError:
    print("❌ google.adk.cli.fast_api_agents does NOT exist")
