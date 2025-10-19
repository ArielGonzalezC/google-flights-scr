"""Example of using round-trip flight search with fast-flights."""

from fast_flights import FlightData, Passengers, get_flights

# Example round-trip search from New York (JFK) to Los Angeles (LAX)
result = get_flights(
    flight_data=[
        FlightData(
            date="2025-12-15",  # Outbound date
            from_airport="JFK",  # New York JFK
            to_airport="LAX",  # Los Angeles
        ),
        FlightData(
            date="2025-12-22",  # Return date
            from_airport="LAX",  # Los Angeles
            to_airport="JFK",  # New York JFK
        ),
    ],
    trip="round-trip",
    passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
    seat="economy",
    fetch_mode="common",  # or "fallback", "force-fallback", "local", "bright-data"
)

print("Current price level:", result.current_price)
print(f"\nFound {len(result.flights)} flight options:\n")

for i, flight in enumerate(result.flights, 1):
    print(f"Option {i}:")
    print(f"  Combined: {flight.name}")
    print(f"  Price: {flight.price}")
    print(f"  Duration: {flight.duration}")
    print(f"  Stops: {flight.stops}")
    
    # If round-trip fields are populated, show details
    if flight.outbound_name:
        print(f"\n  Outbound:")
        print(f"    Airline: {flight.outbound_name}")
        print(f"    Departure: {flight.outbound_departure}")
        print(f"    Arrival: {flight.outbound_arrival}")
        print(f"    Duration: {flight.outbound_duration}")
        print(f"    Stops: {flight.outbound_stops}")
        print(f"    Price: {flight.outbound_price}")
    
    if flight.return_name:
        print(f"\n  Return:")
        print(f"    Airline: {flight.return_name}")
        print(f"    Departure: {flight.return_departure}")
        print(f"    Arrival: {flight.return_arrival}")
        print(f"    Duration: {flight.return_duration}")
        print(f"    Stops: {flight.return_stops}")
        print(f"    Price: {flight.return_price}")
    
    print("-" * 50)
