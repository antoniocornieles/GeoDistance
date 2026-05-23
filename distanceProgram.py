import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# Constants
EARTH_RADIUS_KM = 6371.0
KM_PER_DEG_LAT = 111.32
NORTH_POLE_LAT = 90.0
NORTH_POLE_LON = 0.0

def get_coordinates(city_name):
    geolocator = Nominatim(user_agent="north_pole_mapper")
    try:
        location = geolocator.geocode(city_name, timeout=10)
        if location:
            return location.latitude, location.longitude
        else:
            print(f"Could not find '{city_name}'")
            return None, None
    except (GeocoderTimedOut, GeocoderServiceError):
        print("Geocoding service error. Try again later.")
        return None, None


def pythagorean_distance(lat, lon):
    """1. Pythagorean flat approximation"""
    delta_lat = abs(NORTH_POLE_LAT - lat)
    dist_lat_km = delta_lat * KM_PER_DEG_LAT

    avg_lat = (NORTH_POLE_LAT + lat) / 2
    delta_lon = abs(NORTH_POLE_LON - lon)
    dist_lon_km = delta_lon * KM_PER_DEG_LAT * math.cos(math.radians(avg_lat))

    distance_km = math.sqrt(dist_lat_km**2 + dist_lon_km**2)
    return distance_km


def haversine_distance(lat, lon):
    """2. Haversine formula - most accurate for spherical Earth"""
    lat1, lon1 = math.radians(NORTH_POLE_LAT), math.radians(NORTH_POLE_LON)
    lat2, lon2 = math.radians(lat), math.radians(lon)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance_km = EARTH_RADIUS_KM * c
    return distance_km


def cascading_triangles_distance(lat, lon, num_steps=100):
    """3. Cascading Triangles (piecewise linear approximation)"""
    lat1 = math.radians(NORTH_POLE_LAT)
    lon1 = math.radians(NORTH_POLE_LON)
    lat2 = math.radians(lat)
    lon2 = math.radians(lon)

    dlat = (lat2 - lat1) / num_steps
    dlon = (lon2 - lon1) / num_steps

    total_distance = 0.0
    current_lat = lat1
    current_lon = lon1

    for _ in range(num_steps):
        next_lat = current_lat + dlat
        next_lon = current_lon + dlon

        # Small segment distance using haversine (or Pythagorean for tiny steps)
        a = math.sin((next_lat - current_lat)/2)**2 + \
            math.cos(current_lat) * math.cos(next_lat) * math.sin((next_lon - current_lon)/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        segment = EARTH_RADIUS_KM * c

        total_distance += segment
        current_lat = next_lat
        current_lon = next_lon

    return total_distance


def main():
    print("=== North Pole Distance Calculator (3 Methods) ===\n")
    
    while True:
        city = input("Enter city name (or 'quit'): ").strip()
        if city.lower() in ['quit', 'exit', 'q']:
            break

        lat, lon = get_coordinates(city)
        if lat is None:
            continue

        print(f"\n📍 {city}: {lat:.4f}°N, {lon:.4f}°E")

        dist_pyth = pythagorean_distance(lat, lon)
        dist_hav = haversine_distance(lat, lon)
        dist_casc = cascading_triangles_distance(lat, lon, num_steps=200)

        print(f"1. Pythagorean (flat)     : {dist_pyth:8.1f} km")
        print(f"2. Haversine (spherical)  : {dist_hav:8.1f} km")
        print(f"3. Cascading Triangles    : {dist_casc:8.1f} km")
        print("-" * 50)

if __name__ == "__main__":
    main()
