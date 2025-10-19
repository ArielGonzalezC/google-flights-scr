"""
Minimal Google Flights Example
================================
Simple command-line interface for searching flights.

Usage:
    python example.py --origin JFK --destination LAX --depart_date 2025-07-01
    python example.py --origin JFK --destination LAX --depart_date 2025-07-01 --return_date 2025-07-10
"""

import argparse
from minimal_flights import search_flights, PassengerConfig


def main():
    """Command-line interface for flight search."""
    parser = argparse.ArgumentParser(
        description="Minimal Google Flights Search - Generate flight search URLs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # One-way flight
  python example.py --origin JFK --destination LAX --depart_date 2025-07-01

  # Round-trip flight
  python example.py --origin JFK --destination LAX --depart_date 2025-07-01 --return_date 2025-07-10

  # With multiple passengers and business class
  python example.py --origin JFK --destination LAX --depart_date 2025-07-01 --return_date 2025-07-10 --adults 2 --children 1 --seat_class business

  # With maximum stops
  python example.py --origin SFO --destination MIA --depart_date 2025-08-01 --max_stops 1
        """
    )
    
    # Required arguments
    parser.add_argument('--origin', required=True, 
                       help="Origin airport code (e.g., JFK, LAX, SFO)")
    parser.add_argument('--destination', required=True, 
                       help="Destination airport code")
    parser.add_argument('--depart_date', required=True, 
                       help="Departure date (YYYY-MM-DD)")
    
    # Optional arguments
    parser.add_argument('--return_date', 
                       help="Return date for round-trip (YYYY-MM-DD)")
    parser.add_argument('--adults', type=int, default=1, 
                       help="Number of adults (default: 1)")
    parser.add_argument('--children', type=int, default=0, 
                       help="Number of children (default: 0)")
    parser.add_argument('--infants_in_seat', type=int, default=0, 
                       help="Number of infants with seat (default: 0)")
    parser.add_argument('--infants_on_lap', type=int, default=0, 
                       help="Number of infants on lap (default: 0)")
    parser.add_argument('--seat_class', type=str, default="economy", 
                       choices=["economy", "premium-economy", "business", "first"],
                       help="Seat class (default: economy)")
    parser.add_argument('--max_stops', type=int, 
                       help="Maximum number of stops (0, 1, or 2)")

    args = parser.parse_args()

    # Create passenger configuration
    passengers = PassengerConfig(
        adults=args.adults,
        children=args.children,
        infants_in_seat=args.infants_in_seat,
        infants_on_lap=args.infants_on_lap
    )
    
    # Validate passengers
    try:
        passengers.validate()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    # Generate search URL
    try:
        url = search_flights(
            origin=args.origin.upper(),
            destination=args.destination.upper(),
            departure_date=args.depart_date,
            return_date=args.return_date,
            passengers=passengers,
            seat_class=args.seat_class,
            max_stops=args.max_stops
        )
        
        # Display results
        print("\n" + "=" * 70)
        print("FLIGHT SEARCH URL GENERATED")
        print("=" * 70)
        print()
        print(f"Route: {args.origin.upper()} → {args.destination.upper()}")
        print(f"Departure: {args.depart_date}")
        if args.return_date:
            print(f"Return: {args.return_date}")
            print(f"Trip Type: Round-trip")
        else:
            print(f"Trip Type: One-way")
        print()
        print(f"Passengers: {args.adults} adult(s)", end="")
        if args.children > 0:
            print(f", {args.children} child(ren)", end="")
        if args.infants_in_seat > 0:
            print(f", {args.infants_in_seat} infant(s) with seat", end="")
        if args.infants_on_lap > 0:
            print(f", {args.infants_on_lap} infant(s) on lap", end="")
        print()
        
        print(f"Seat Class: {args.seat_class.title()}")
        if args.max_stops is not None:
            print(f"Max Stops: {args.max_stops}")
        print()
        print("URL:")
        print(url)
        print()
        print("=" * 70)
        print()
        print("💡 Tip: Open this URL in your browser to see flight results!")
        print()
        
    except Exception as e:
        print(f"Error generating search URL: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
