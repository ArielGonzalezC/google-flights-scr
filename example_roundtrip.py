"""
Round-Trip Flight Example
==========================
Demonstrates how to search for round-trip flights using the minimal implementation.

This example shows:
1. Basic round-trip search
2. Multiple passengers configuration
3. Different seat classes
4. Maximum stops constraint
"""

from minimal_flights import search_flights, PassengerConfig, FlightQuery, create_search_filter


def example_1_basic_round_trip():
    """Example 1: Basic round-trip flight search."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Basic Round-Trip Flight")
    print("=" * 70)
    
    url = search_flights(
        origin="JFK",           # New York
        destination="LAX",      # Los Angeles
        departure_date="2025-07-01",
        return_date="2025-07-10",
        passengers=PassengerConfig(adults=1),
        seat_class="economy"
    )
    
    print(f"\nRoute: JFK → LAX → JFK")
    print(f"Departure: 2025-07-01")
    print(f"Return: 2025-07-10")
    print(f"Passengers: 1 adult")
    print(f"Seat: Economy")
    print(f"\nURL: {url}\n")


def example_2_family_trip():
    """Example 2: Family trip with multiple passengers."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Family Round-Trip")
    print("=" * 70)
    
    url = search_flights(
        origin="SFO",           # San Francisco
        destination="MIA",      # Miami
        departure_date="2025-08-15",
        return_date="2025-08-22",
        passengers=PassengerConfig(
            adults=2,           # 2 parents
            children=2,         # 2 children
            infants_on_lap=1    # 1 infant
        ),
        seat_class="premium-economy"
    )
    
    print(f"\nRoute: SFO → MIA → SFO")
    print(f"Departure: 2025-08-15")
    print(f"Return: 2025-08-22")
    print(f"Passengers: 2 adults, 2 children, 1 infant on lap")
    print(f"Seat: Premium Economy")
    print(f"\nURL: {url}\n")


def example_3_business_trip():
    """Example 3: Business trip with non-stop flights."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Business Round-Trip (Non-stop)")
    print("=" * 70)
    
    url = search_flights(
        origin="ORD",           # Chicago
        destination="ATL",      # Atlanta
        departure_date="2025-09-01",
        return_date="2025-09-03",
        passengers=PassengerConfig(adults=1),
        seat_class="business",
        max_stops=0             # Non-stop flights only
    )
    
    print(f"\nRoute: ORD → ATL → ORD")
    print(f"Departure: 2025-09-01")
    print(f"Return: 2025-09-03")
    print(f"Passengers: 1 adult")
    print(f"Seat: Business")
    print(f"Max Stops: 0 (non-stop)")
    print(f"\nURL: {url}\n")


def example_4_international_trip():
    """Example 4: International round-trip in first class."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: International Round-Trip (First Class)")
    print("=" * 70)
    
    url = search_flights(
        origin="JFK",           # New York
        destination="LHR",      # London
        departure_date="2025-12-20",
        return_date="2026-01-05",
        passengers=PassengerConfig(adults=2),
        seat_class="first",
        max_stops=1             # Up to 1 stop
    )
    
    print(f"\nRoute: JFK → LHR → JFK")
    print(f"Departure: 2025-12-20")
    print(f"Return: 2026-01-05")
    print(f"Passengers: 2 adults")
    print(f"Seat: First Class")
    print(f"Max Stops: 1")
    print(f"\nURL: {url}\n")


def example_5_manual_filter():
    """Example 5: Using manual filter creation for more control."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Manual Filter Creation")
    print("=" * 70)
    
    # Create queries manually for more control
    queries = [
        FlightQuery(
            date="2025-10-15",
            from_airport="LAX",
            to_airport="NRT",   # Tokyo
            max_stops=1
        ),
        FlightQuery(
            date="2025-10-30",
            from_airport="NRT",
            to_airport="LAX",
            max_stops=1
        )
    ]
    
    # Create filter
    tfs = create_search_filter(
        queries=queries,
        trip_type="round-trip",
        passengers=PassengerConfig(adults=2),
        seat_class="economy"
    )
    
    url = f"https://www.google.com/travel/flights?tfs={tfs}&hl=en"
    
    print(f"\nRoute: LAX → NRT → LAX")
    print(f"Outbound: 2025-10-15")
    print(f"Return: 2025-10-30")
    print(f"Passengers: 2 adults")
    print(f"Seat: Economy")
    print(f"Max Stops: 1")
    print(f"\nURL: {url}\n")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("ROUND-TRIP FLIGHT EXAMPLES")
    print("=" * 70)
    print("\nThis script demonstrates various round-trip flight scenarios.")
    print("Each example generates a Google Flights URL you can open in your browser.")
    
    # Run all examples
    example_1_basic_round_trip()
    example_2_family_trip()
    example_3_business_trip()
    example_4_international_trip()
    example_5_manual_filter()
    
    print("\n" + "=" * 70)
    print("💡 Tips:")
    print("  - Copy any URL and open it in your browser")
    print("  - Modify the dates and airports to suit your needs")
    print("  - Use max_stops=0 for non-stop flights only")
    print("  - Seat classes: economy, premium-economy, business, first")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
