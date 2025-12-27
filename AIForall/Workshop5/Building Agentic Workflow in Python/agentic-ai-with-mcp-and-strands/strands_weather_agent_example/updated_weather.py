# import streamlit as st
# import requests
# import os
# from strands import Agent
# from strands.models import BedrockModel
# from strands_tools import http_request
# from dotenv import load_dotenv

# load_dotenv()
# st.set_page_config(page_title="Pro Weather Agent", page_icon="🌤️")

# # --- TOOLS ---

# def geocode_location(location_name: str) -> dict:
#     """Converts a city name to lat/lon."""
#     url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
#     headers = {'User-Agent': 'WeatherAgent/1.0'}
#     try:
#         r = requests.get(url, headers=headers)
#         data = r.json()
#         return {"lat": data[0]["lat"], "lon": data[0]["lon"], "name": data[0]["display_name"]} if data else {"error": "Not found"}
#     except: return {"error": "Geocoding failed"}

# def get_nearby_cities(lat: float, lon: float) -> list:
#     """Finds major cities within a 50km radius using OpenStreetMap."""
#     # We use the Overpass API to find nearby cities/towns
#     overpass_url = "http://overpass-api.de/api/interpreter"
#     overpass_query = f"""
#     [out:json];
#     (
#       node["place"~"city|town"](around:50000,{lat},{lon});
#     );
#     out tags;
#     """
#     try:
#         response = requests.get(overpass_url, params={'data': overpass_query})
#         data = response.json()
#         cities = [element['tags'].get('name') for element in data['elements'] if 'name' in element['tags']]
#         return sorted(list(set(cities)))[:15] # Return top 15 unique city names
#     except:
#         return ["Could not retrieve nearby cities."]

# @st.cache_resource
# def get_weather_agent():
#     # Update the prompt to include the new capability
#     WEATHER_PROMPT = """You are a professional Weather & Geography Expert.
#     1. If a user asks for weather: Geocode the location, then fetch the NWS forecast.
#     2. If a user asks for 'cities in the area' or 'nearby cities': Use the get_nearby_cities tool.
#     3. Always present the city list as a clean bulleted list grouped by distance or importance if possible.
#     Format your final response using beautiful Markdown."""

#     return Agent(
#         system_prompt=WEATHER_PROMPT,
#         tools=[http_request, geocode_location, get_nearby_cities],
#         model=BedrockModel(model_id="us.amazon.nova-pro-v1:0", temperature=0)
#     )

# # --- SAFE EXTRACTION HELPER ---
# def extract_answer(result):
#     try:
#         m = result.message if hasattr(result, 'message') else result['message']
#         c = m.content if hasattr(m, 'content') else m['content']
#         return c[0].text if hasattr(c[0], 'text') else c[0]['text']
#     except:
#         return str(result)

# # --- STREAMLIT UI ---
# st.title("🌤️ Pro Weather & City Explorer")
# st.markdown("Ask for weather, or ask **'What are the cities near [Location]?'**")



# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for m in st.session_state.messages:
#     with st.chat_message(m["role"]): st.markdown(m["content"])

# if prompt := st.chat_input("Ex: Weather in Seattle and nearby cities"):
#     st.session_state.messages.append({"role": "user", "content": prompt})
#     with st.chat_message("user"): st.markdown(prompt)

#     with st.chat_message("assistant"):
#         with st.spinner("Searching geography and weather data..."):
#             try:
#                 agent = get_weather_agent()
#                 raw_result = agent(prompt)
#                 answer = extract_answer(raw_result)
                
#                 st.markdown(answer)
#                 st.session_state.messages.append({"role": "assistant", "content": answer})
#             except Exception as e:
#                 st.error(f"Error: {e}")

import streamlit as st
import requests
import os
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request
from dotenv import load_dotenv

load_dotenv()
st.set_page_config(page_title="Safe Weather Agent", page_icon="🌤️")

# --- TOOLS ---
def geocode_location(location_name: str) -> dict:
    url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
    headers = {'User-Agent': 'WeatherAgent/1.0'}
    try:
        r = requests.get(url, headers=headers)
        data = r.json()
        return {"lat": data[0]["lat"], "lon": data[0]["lon"], "name": data[0]["display_name"]} if data else {"error": "Not found"}
    except: return {"error": "Connection failed"}

@st.cache_resource
def get_weather_agent():
    return Agent(
        system_prompt="You are a weather expert. Use tools to find US weather and format in Markdown.",
        tools=[http_request, geocode_location],
        model=BedrockModel(model_id="us.amazon.nova-pro-v1:0", temperature=0)
    )

# --- SAFE EXTRACTION HELPER ---
def extract_answer(result):
    # This handles both result.message.content and result['message']['content']
    try:
        # Get message
        m = result.message if hasattr(result, 'message') else result['message']
        # Get content
        c = m.content if hasattr(m, 'content') else m['content']
        # Get text from first content block
        return c[0].text if hasattr(c[0], 'text') else c[0]['text']
    except:
        return str(result)

# --- UI ---
st.title("🌤️ Bulletproof Weather Agent")

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Ask about weather..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                agent = get_weather_agent()
                raw_result = agent(prompt)
                
                # Use our new safe extraction function
                answer = extract_answer(raw_result)
                
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {e}")