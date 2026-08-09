"""Tests for the Haversine distance calculation."""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.geo import haversine, is_within_geofence


def test_same_point_is_zero():
    """Distance from a point to itself should be 0."""
    d = haversine(6.9271, 79.8612, 6.9271, 79.8612)
    assert d == 0.0


def test_known_short_distance():
    """Two points ~5m apart (manually verified coordinates)."""
    # Approximately 5 metres apart at Colombo latitude
    lat1, lon1 = 6.9271000, 79.8612000
    lat2, lon2 = 6.9271450, 79.8612000  # ~5m north
    d = haversine(lat1, lon1, lat2, lon2)
    assert 4.5 < d < 5.5, f"Expected ~5m, got {d}"


def test_known_100m_distance():
    """Two points approximately 100m apart."""
    lat1, lon1 = 6.9271000, 79.8612000
    lat2, lon2 = 6.9280000, 79.8612000  # ~100m north
    d = haversine(lat1, lon1, lat2, lon2)
    assert 90 < d < 110, f"Expected ~100m, got {d}"


def test_within_geofence_inside():
    """Point inside the geofence should return True."""
    within, dist = is_within_geofence(6.9271, 79.8612, 6.9271, 79.8612, 10)
    assert within is True
    assert dist == 0.0


def test_within_geofence_outside():
    """Point 100m away from a 10m geofence should return False."""
    within, dist = is_within_geofence(6.9280, 79.8612, 6.9271, 79.8612, 10)
    assert within is False
    assert dist > 10


def test_within_geofence_boundary():
    """Point at boundary (within 5m of a 5m geofence) should be accepted."""
    # ~3m from center
    within, dist = is_within_geofence(6.92710270, 79.8612, 6.9271, 79.8612, 5)
    assert within is True
    assert dist < 5
