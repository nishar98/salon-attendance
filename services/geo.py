"""Haversine distance calculation for geofence validation."""

import math


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth.

    Args:
        lat1, lon1: Coordinates of point 1 (degrees)
        lat2, lon2: Coordinates of point 2 (degrees)

    Returns:
        Distance in metres.
    """
    R = 6_371_000  # Earth radius in metres

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def is_within_geofence(
    punch_lat: float,
    punch_lon: float,
    site_lat: float,
    site_lon: float,
    radius_m: int,
) -> tuple[bool, float]:
    """
    Check if punch coordinates are within the geofence.

    Returns:
        Tuple of (is_within, distance_in_metres)
    """
    distance = haversine(punch_lat, punch_lon, site_lat, site_lon)
    return distance <= radius_m, round(distance, 1)
