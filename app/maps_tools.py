"""
Google Maps Geocoding and Places (New) function tools for IT Support Agent.
Reads GOOGLE_MAPS_API_KEY from environment variables (.env).
"""

import json
import os
import urllib.parse
import urllib.request


def _load_env_file():
    """Load environment variables from local .env if present."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()


def geocode_address(address: str) -> str:
    """Convert a street address or location name into geographic coordinates (latitude & longitude) using Google Maps Geocoding API.

    Args:
        address: The address or place name to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA').

    Returns:
        Formatted text containing matching address, latitude, and longitude.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    encoded_address = urllib.parse.quote(address)
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        if data.get("status") != "OK" or not data.get("results"):
            return f"Geocoding failed for address '{address}'. Status: {data.get('status', 'ZERO_RESULTS')}"

        result = data["results"][0]
        formatted_address = result.get("formatted_address", address)
        loc = result.get("geometry", {}).get("location", {})
        lat = loc.get("lat")
        lng = loc.get("lng")

        return (
            f"Geocoded Address: {formatted_address}\n"
            f"Latitude: {lat}\n"
            f"Longitude: {lng}"
        )
    except Exception as e:
        return f"Error during geocoding: {str(e)}"


def find_nearby_places(latitude: float, longitude: float, place_type: str = "restaurant", radius_meters: float = 1000.0) -> str:
    """Find nearby places of a given type (e.g. 'restaurant', 'cafe', 'store', 'hardware_store') using Google Places API (New).

    Args:
        latitude: Center latitude coordinate (e.g. 37.4220).
        longitude: Center longitude coordinate (e.g. -122.0841).
        place_type: Type of place to search for (e.g. 'restaurant', 'cafe', 'store').
        radius_meters: Search radius in meters (default: 1000.0).

    Returns:
        List of nearby places with name, address, and coordinates.
    """
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        return "Error: GOOGLE_MAPS_API_KEY environment variable is not set."

    url = "https://places.googleapis.com/v1/places:searchNearby"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
    }

    payload = {
        "includedTypes": [place_type.lower().strip()],
        "maxResultCount": 5,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": float(latitude),
                    "longitude": float(longitude),
                },
                "radius": float(radius_meters),
            }
        },
    }

    try:
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=req_data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        places = data.get("places", [])
        if not places:
            return f"No nearby '{place_type}' places found within {radius_meters}m of ({latitude}, {longitude})."

        results = []
        for p in places:
            name = p.get("displayName", {}).get("text", "Unknown Place")
            addr = p.get("formattedAddress", "N/A")
            loc = p.get("location", {})
            lat = loc.get("latitude")
            lng = loc.get("longitude")
            results.append(f"• Name: {name}\n  Address: {addr}\n  Location: ({lat}, {lng})")

        return "\n\n".join(results)
    except Exception as e:
        return f"Error during nearby places search: {str(e)}"
