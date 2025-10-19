"""
Simple test of minimal_flights module
"""

from minimal_flights import search_flights, PassengerConfig

# Test 1: One-way flight
print("Test 1: One-way flight")
print("-" * 50)
url = search_flights(
    origin="TPE",
    destination="MYJ",
    departure_date="2025-07-01",
    passengers=PassengerConfig(adults=2, children=1),
    seat_class="economy",
    max_stops=1
)
print(f"URL: {url}")
print()

# Test 2: Round-trip flight
print("Test 2: Round-trip flight")
print("-" * 50)
url = search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2025-07-01",
    return_date="2025-07-10",
    passengers=PassengerConfig(adults=1),
    seat_class="economy"
)
print(f"URL: {url}")
print()

print("✅ All tests passed!")
