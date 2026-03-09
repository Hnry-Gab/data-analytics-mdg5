"""Haversine distance calculation."""

import math

EARTH_RADIUS_KM = 6371.0


def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Calculate the great-circle distance between two points on Earth.

    Args:
        lat1: Latitude of point 1 (degrees).
        lng1: Longitude of point 1 (degrees).
        lat2: Latitude of point 2 (degrees).
        lng2: Longitude of point 2 (degrees).

    Returns:
        Distance in kilometers.
    """
    lat1_r, lng1_r = math.radians(lat1), math.radians(lng1)
    lat2_r, lng2_r = math.radians(lat2), math.radians(lng2)

    dlat = lat2_r - lat1_r
    dlng = lng2_r - lng1_r

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlng / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c
