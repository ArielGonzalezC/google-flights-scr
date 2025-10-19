"""Example usage for round-trip flight searches."""

from fast_flights import FlightData, Passengers, get_flights

# Example round-trip flight search
result = get_flights(
    flight_data=[
        FlightData(
            date="2025-12-20",  # Outbound date
            from_airport="JFK",  # New York
            to_airport="LAX"     # Los Angeles
        ),
        FlightData(
            date="2025-12-27",  # Return date
            from_airport="LAX",  # Los Angeles
            to_airport="JFK"     # New York
        ),
    ],
    trip="round-trip",
    seat="economy",
    passengers=Passengers(adults=2, children=0, infants_in_seat=0, infants_on_lap=0),
    fetch_mode="common",
)

print("Current price indicator:", result.current_price)
print(f"\nFound {len(result.flights)} outbound flights")

# Display first few outbound flights
for i, flight in enumerate(result.flights[:3], 1):
    print(f"\n--- Flight {i} ---")
    print(f"Airline: {flight.name}")
    print(f"Departure: {flight.departure}")
    print(f"Arrival: {flight.arrival}")
    print(f"Duration: {flight.duration}")
    print(f"Stops: {flight.stops}")
    print(f"Price: {flight.price}")
    if flight.flight_codes:
        print(f"Flight codes: {', '.join(flight.flight_codes)}")
    if flight.is_best:
        print("⭐ Best flight option")

# Check for return flights
if result.return_flights:
    print(f"\nFound {len(result.return_flights)} return flights")
    for i, flight in enumerate(result.return_flights[:3], 1):
        print(f"\n--- Return Flight {i} ---")
        print(f"Airline: {flight.name}")
        print(f"Departure: {flight.departure}")
        print(f"Arrival: {flight.arrival}")
        print(f"Duration: {flight.duration}")
        print(f"Stops: {flight.stops}")
        print(f"Price: {flight.price}")
else:
    print("\nNote: This search returned outbound flights only.")
    print("Google Flights typically shows outbound flights first.")
    print("Return flights may require separate filtering or different approach.")
