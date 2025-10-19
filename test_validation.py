"""
Comprehensive validation tests for minimal_flights.py
"""

from minimal_flights import (
    search_flights, 
    PassengerConfig, 
    FlightQuery,
    create_search_filter,
    parse_flights_from_html
)

def test_one_way():
    """Test one-way flight generation."""
    print("Test 1: One-way flight")
    url = search_flights("JFK", "LAX", "2025-07-01")
    assert "tfs=" in url
    assert url.startswith("https://www.google.com/travel/flights?tfs=")
    print("  ✓ One-way URL generated")

def test_round_trip():
    """Test round-trip flight generation."""
    print("Test 2: Round-trip flight")
    url = search_flights("JFK", "LAX", "2025-07-01", "2025-07-10")
    assert "tfs=" in url
    assert url.startswith("https://www.google.com/travel/flights?tfs=")
    print("  ✓ Round-trip URL generated")

def test_passengers():
    """Test various passenger configurations."""
    print("Test 3: Passenger configurations")
    
    # Single adult
    p1 = PassengerConfig(adults=1)
    p1.validate()
    print("  ✓ Single adult")
    
    # Family
    p2 = PassengerConfig(adults=2, children=2)
    p2.validate()
    print("  ✓ Family (2 adults, 2 children)")
    
    # With infant
    p3 = PassengerConfig(adults=1, infants_on_lap=1)
    p3.validate()
    print("  ✓ Adult with infant on lap")
    
    # Test validation errors
    try:
        p4 = PassengerConfig(adults=10)
        p4.validate()
        assert False, "Should have raised error for too many passengers"
    except ValueError:
        print("  ✓ Validation catches too many passengers")
    
    try:
        p5 = PassengerConfig(adults=1, infants_on_lap=2)
        p5.validate()
        assert False, "Should have raised error for infants > adults"
    except ValueError:
        print("  ✓ Validation catches infant/adult ratio")

def test_seat_classes():
    """Test all seat classes."""
    print("Test 4: Seat classes")
    
    for seat in ["economy", "premium-economy", "business", "first"]:
        url = search_flights("JFK", "LAX", "2025-07-01", seat_class=seat)
        assert "tfs=" in url
        print(f"  ✓ {seat}")

def test_max_stops():
    """Test max stops parameter."""
    print("Test 5: Max stops")
    
    for stops in [0, 1, 2]:
        url = search_flights("JFK", "LAX", "2025-07-01", max_stops=stops)
        assert "tfs=" in url
        print(f"  ✓ max_stops={stops}")

def test_manual_queries():
    """Test manual query creation."""
    print("Test 6: Manual query creation")
    
    queries = [
        FlightQuery("2025-07-01", "JFK", "LAX", max_stops=1),
        FlightQuery("2025-07-10", "LAX", "JFK", max_stops=1)
    ]
    
    tfs = create_search_filter(
        queries=queries,
        trip_type="round-trip",
        passengers=PassengerConfig(adults=2),
        seat_class="economy"
    )
    
    assert len(tfs) > 0
    print("  ✓ Manual queries work")

def test_url_format():
    """Test URL format is correct."""
    print("Test 7: URL format validation")
    
    url = search_flights("JFK", "LAX", "2025-07-01")
    
    assert url.startswith("https://www.google.com/travel/flights?tfs=")
    assert "&hl=en" in url
    print("  ✓ URL format correct")

def test_protobuf_compatibility():
    """Test compatibility with original implementation."""
    print("Test 8: Protobuf compatibility")
    
    try:
        from fast_flights import create_filter, FlightData, Passengers
        
        # Test one-way
        url_minimal = search_flights("JFK", "LAX", "2025-07-01")
        filter_orig = create_filter(
            flight_data=[FlightData(date="2025-07-01", from_airport="JFK", to_airport="LAX")],
            trip="one-way",
            passengers=Passengers(adults=1),
            seat="economy"
        )
        url_orig = f"https://www.google.com/travel/flights?tfs={filter_orig.as_b64().decode('utf-8')}&hl=en"
        
        assert url_minimal == url_orig
        print("  ✓ One-way URLs match original")
        
        # Test round-trip
        url_minimal_rt = search_flights("JFK", "LAX", "2025-07-01", "2025-07-10")
        filter_orig_rt = create_filter(
            flight_data=[
                FlightData(date="2025-07-01", from_airport="JFK", to_airport="LAX"),
                FlightData(date="2025-07-10", from_airport="LAX", to_airport="JFK")
            ],
            trip="round-trip",
            passengers=Passengers(adults=1),
            seat="economy"
        )
        url_orig_rt = f"https://www.google.com/travel/flights?tfs={filter_orig_rt.as_b64().decode('utf-8')}&hl=en"
        
        assert url_minimal_rt == url_orig_rt
        print("  ✓ Round-trip URLs match original")
        
    except ImportError:
        print("  ⚠ Original implementation not available (skipped)")

def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("COMPREHENSIVE VALIDATION TESTS")
    print("=" * 70 + "\n")
    
    tests = [
        test_one_way,
        test_round_trip,
        test_passengers,
        test_seat_classes,
        test_max_stops,
        test_manual_queries,
        test_url_format,
        test_protobuf_compatibility,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70 + "\n")
    
    if failed > 0:
        return 1
    
    print("✅ All tests passed!")
    return 0

if __name__ == "__main__":
    exit(main())
