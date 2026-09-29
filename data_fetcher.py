"""
data_fetcher.py
================
Builds a connected road-network graph for a selected USA region.
Uses:
  - Nominatim OpenStreetMap API for geocoding (coordinates)
  - OSRM Routing API for road driving distances

Saves the resulting graph to `map_data.json`.
"""

import json
import time
import math
import requests

# ---------------------------------------------------------
# Configuration: Select USA Region & Locations (>= 20 cities)
# Example Region: Illinois, USA
# ---------------------------------------------------------
REGION_NAME = "California, USA"

# List of at least 20 cities/locations in the selected region
CITIES = [
    "San Francisco, CA",
    "Oakland, CA",
    "Berkeley, CA",
    "San Rafael, CA",
    "Santa Rosa, CA",
    "Napa, CA",
    "Vallejo, CA",
    "Fairfield, CA",
    "Davis, CA",
    "Sacramento, CA",
    "Stockton, CA",
    "Modesto, CA",
    "San Jose, CA",
    "Santa Cruz, CA",
    "Monterey, CA",
    "Salinas, CA",
    "Fresno, CA",
    "Chico, CA",
    "Redding, CA",
    "Reno, NV"
]

# Road connections between cities (Undirected graph edges)
# Ensure the graph is fully connected (a path exists between any two cities)
ROAD_CONNECTIONS = [
    ("San Francisco, CA", "Oakland, CA"),
    ("San Francisco, CA", "Berkeley, CA"),
    ("San Francisco, CA", "San Rafael, CA"),
    ("San Francisco, CA", "San Jose, CA"),
    ("Oakland, CA", "Berkeley, CA"),
    ("Oakland, CA", "Vallejo, CA"),
    ("Oakland, CA", "San Jose, CA"),
    ("Berkeley, CA", "Vallejo, CA"),
    ("San Rafael, CA", "Santa Rosa, CA"),
    ("San Rafael, CA", "Vallejo, CA"),
    ("Santa Rosa, CA", "Napa, CA"),
    ("Napa, CA", "Vallejo, CA"),
    ("Napa, CA", "Fairfield, CA"),
    ("Vallejo, CA", "Fairfield, CA"),
    ("Fairfield, CA", "Davis, CA"),
    ("Fairfield, CA", "Sacramento, CA"),
    ("Davis, CA", "Sacramento, CA"),
    ("Davis, CA", "Napa, CA"),
    ("Sacramento, CA", "Stockton, CA"),
    ("Sacramento, CA", "Chico, CA"),
    ("Stockton, CA", "Modesto, CA"),
    ("Stockton, CA", "San Jose, CA"),
    ("Modesto, CA", "San Jose, CA"),
    ("Modesto, CA", "Fresno, CA"),
    ("San Jose, CA", "Santa Cruz, CA"),
    ("San Jose, CA", "Salinas, CA"),
    ("Santa Cruz, CA", "Monterey, CA"),
    ("Santa Cruz, CA", "Salinas, CA"),
    ("Monterey, CA", "Salinas, CA"),
    ("Salinas, CA", "Fresno, CA"),
    ("Chico, CA", "Redding, CA"),
    ("Sacramento, CA", "Redding, CA"),
    ("Sacramento, CA", "Reno, NV"),
    ("Redding, CA", "Reno, NV")
]

USER_AGENT = "CS411-Search-Visualizer/1.0 (uic-cs411-student-project)"


def haversine_distance(coord1, coord2):
    """
    Fallback straight-line (great-circle) distance in miles.
    coord = (lat, lon)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 3958.8  # Earth radius in miles

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


def fetch_coordinates(city_name):
    """
    Fetch latitude and longitude from Nominatim OpenStreetMap API.
    """
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city_name,
        "format": "json",
        "limit": 1
    }
    headers = {
        "User-Agent": USER_AGENT
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return {"lat": lat, "lon": lon}
    except Exception as e:
        print(f"  [Warning] Failed to fetch coordinates for {city_name}: {e}")

    return None


def fetch_road_distance(coord1, coord2):
    """
    Fetch road driving distance in miles from OSRM Routing API.
    coord = (lat, lon)
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
    params = {"overview": "false"}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == "Ok" and len(data.get("routes", [])) > 0:
                distance_meters = data["routes"][0]["distance"]
                distance_miles = distance_meters * 0.000621371
                return round(distance_miles, 2)
    except Exception as e:
        print(f"  [Warning] OSRM routing failed ({coord1} -> {coord2}): {e}")

    # Fallback to straight-line distance if routing API fails
    return haversine_distance(coord1, coord2)


def build_graph():
    """
    Build the map graph and save to map_data.json.
    """
    print(f"Building map graph for region: {REGION_NAME}")
    print(f"Total locations to geocode: {len(CITIES)}")

    locations = {}
    for idx, city in enumerate(CITIES, 1):
        print(f"[{idx}/{len(CITIES)}] Geocoding: {city} ...")
        coords = fetch_coordinates(city)
        if coords:
            locations[city] = coords
        else:
            print(f"  [Error] Could not find coordinates for {city}")
        # Nominatim usage policy requires 1-second delay between requests
        time.sleep(1.0)

    # Initialize adjacency list
    graph = {city: {} for city in locations}

    print(f"\nFetching road distances for {len(ROAD_CONNECTIONS)} connections ...")
    total_edges = 0
    for u, v in ROAD_CONNECTIONS:
        if u in locations and v in locations:
            c1 = (locations[u]["lat"], locations[u]["lon"])
            c2 = (locations[v]["lat"], locations[v]["lon"])
            dist = fetch_road_distance(c1, c2)

            graph[u][v] = dist
            graph[v][u] = dist
            total_edges += 1
            print(f"  Connection: {u} <---> {v} : {dist} miles")
            time.sleep(0.2)
        else:
            print(f"  [Warning] Skipping edge ({u}, {v}) - missing location coordinates.")

    map_data = {
        "region": REGION_NAME,
        "total_cities": len(locations),
        "total_edges": total_edges,
        "locations": locations,
        "graph": graph
    }

    with open("map_data.json", "w") as f:
        json.dump(map_data, f, indent=2)

    print("\nGraph construction complete!")
    print(f"Saved to map_data.json with {len(locations)} cities and {total_edges} connections.")


if __name__ == "__main__":
    build_graph()
