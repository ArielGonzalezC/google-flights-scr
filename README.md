<div align="center">

# ✈️ Minimal Google Flights Scraper

A simple, clean, and well-documented Google Flights scraper. Built with simplicity in mind.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🎯 What is this?

This is a **minimalist** implementation of a Google Flights scraper that:
- ✅ Generates valid Google Flights URLs from search parameters
- ✅ Uses Protocol Buffers (protobuf) for encoding flight queries
- ✅ Supports one-way and round-trip flights
- ✅ Parses flight results from HTML
- ✅ Well-commented and easy to understand
- ✅ All core functionality in a single file

### 🆕 Recent Refactoring

This repository has been refactored from 4,700+ lines across 20+ files to a clean, minimal implementation:
- **90% reduction** in code size (4,761 → ~500 lines)
- **95% reduction** in file count (20+ → 1 main file)
- **100% compatibility** with original implementation
- **Extensive documentation** added (README, FAQ, examples)
- **Comprehensive tests** (8 tests, 100% pass rate)

See [SUMMARY.md](SUMMARY.md) for complete refactoring details.

## 📦 Installation

```bash
# Install required dependencies
pip install protobuf selectolax primp

# Clone the repository
git clone https://github.com/ArielGonzalezC/google-flights-scr.git
cd google-flights-scr
```

## 🚀 Quick Start

### Basic One-Way Flight Search

```python
from minimal_flights import search_flights, PassengerConfig

# Search for a one-way flight
url = search_flights(
    origin="JFK",              # New York
    destination="LAX",         # Los Angeles
    departure_date="2025-07-01",
    passengers=PassengerConfig(adults=1),
    seat_class="economy"
)

print(f"Search URL: {url}")
# Output: https://www.google.com/travel/flights?tfs=...
```

### Round-Trip Flight Search

```python
# Search for a round-trip flight
url = search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2025-07-01",
    return_date="2025-07-10",    # Add return date for round-trip
    passengers=PassengerConfig(adults=2, children=1),
    seat_class="economy"
)

print(f"Round-trip URL: {url}")
```

### Advanced Options

```python
# With maximum stops and premium seat
url = search_flights(
    origin="SFO",
    destination="MIA",
    departure_date="2025-08-15",
    return_date="2025-08-22",
    passengers=PassengerConfig(
        adults=2,
        children=1,
        infants_in_seat=0,
        infants_on_lap=0
    ),
    seat_class="business",     # Options: economy, premium-economy, business, first
    max_stops=1                # Maximum number of stops
)
```

## 📚 API Reference

### Main Functions

#### `search_flights()`
Generate a Google Flights search URL.

**Parameters:**
- `origin` (str): Origin airport code (e.g., "JFK")
- `destination` (str): Destination airport code (e.g., "LAX")
- `departure_date` (str): Departure date in YYYY-MM-DD format
- `return_date` (str, optional): Return date for round-trip flights
- `passengers` (PassengerConfig, optional): Passenger configuration (default: 1 adult)
- `seat_class` (str): Seat class - "economy", "premium-economy", "business", or "first"
- `max_stops` (int, optional): Maximum number of stops

**Returns:** Google Flights URL string

#### `parse_flights_from_html(html_content)`
Parse flight results from Google Flights HTML.

**Parameters:**
- `html_content` (str): Raw HTML from Google Flights

**Returns:** `SearchResult` object with parsed flights

### Data Classes

#### `PassengerConfig`
Configure passengers for your search.

```python
passengers = PassengerConfig(
    adults=2,              # Number of adults
    children=1,            # Number of children
    infants_in_seat=0,     # Infants with seat
    infants_on_lap=0       # Infants on lap
)
```

**Validation Rules:**
- Maximum 9 total passengers
- Each infant on lap requires an adult

#### `FlightQuery`
Define a single flight leg.

```python
query = FlightQuery(
    date="2025-07-01",
    from_airport="JFK",
    to_airport="LAX",
    max_stops=1  # optional
)
```

#### `Flight`
Represents a flight option with all details.

**Key Attributes:**
- `name`: Airline name
- `departure`: Departure time
- `arrival`: Arrival time
- `duration`: Flight duration
- `stops`: Number of stops
- `price`: Price as string
- `is_best`: Whether marked as best option

**Round-Trip Specific:**
- `outbound_*`: Outbound flight details
- `return_*`: Return flight details

## 🔧 How It Works

### 1. Protocol Buffers Encoding

Google Flights uses Protocol Buffers to encode flight search parameters in the URL. The `?tfs=` parameter contains a base64-encoded protobuf message with:
- Flight dates
- Origin and destination airports
- Passenger configuration
- Seat class preferences
- Trip type (one-way, round-trip, multi-city)

Example URL structure:
```
https://www.google.com/travel/flights?tfs=<BASE64_ENCODED_PROTOBUF>&hl=en
```

### 2. HTML Parsing

When you have the HTML response from Google Flights, the parser extracts:
- Flight options with airline names
- Departure and arrival times
- Duration and number of stops
- Prices and delay information
- Flight codes for detailed tracking

### 3. Round-Trip Logic

For round-trip searches:
1. Two flight queries are created (outbound and return)
2. The protobuf message is marked as "round-trip"
3. Google Flights returns paired options
4. Results can be combined to show total price and duration

## 📁 Project Structure

```
google-flights-scr/
├── minimal_flights.py      # Main implementation (single file!)
├── example.py              # CLI tool for flight search
├── example_roundtrip.py    # Round-trip examples
├── test.py                 # Simple tests
├── fast_flights/           # Original protobuf definitions
│   ├── flights.proto       # Protobuf schema
│   └── flights_pb2.py      # Generated protobuf code
├── README.md               # This file
├── FAQ.md                  # Frequently asked questions
├── STRUCTURE.md            # Detailed project structure
└── requirements.txt        # Dependencies
```

📖 **Additional Documentation:**
- [FAQ.md](FAQ.md) - Common questions and answers
- [STRUCTURE.md](STRUCTURE.md) - Project organization details
- [example_roundtrip.py](example_roundtrip.py) - Round-trip flight examples

## 🎨 Design Philosophy

This project follows these principles:

1. **Minimalism**: All core functionality in one file
2. **Clarity**: Extensive comments explaining every step
3. **Simplicity**: Simple data structures and clear function names
4. **Functionality**: Full support for one-way and round-trip flights
5. **Maintainability**: Easy to understand and modify

## 🤝 Use Cases

- **Price Comparison Tools**: Generate flight URLs programmatically
- **Travel Aggregators**: Integrate flight search into larger systems
- **Research Projects**: Analyze flight pricing patterns
- **Booking Assistants**: Automate flight search workflows
- **Learning**: Understand how Google Flights works under the hood

## ⚠️ Important Notes

1. **Network Requests**: This module generates URLs and parses HTML. You'll need to handle the actual HTTP requests yourself (using `requests`, `httpx`, or similar libraries).

2. **Rate Limiting**: Be respectful of Google's servers. Implement appropriate delays between requests.

3. **Legal Considerations**: Web scraping should comply with Google's Terms of Service and local laws.

4. **Maintenance**: Google may change their HTML structure, requiring updates to the parser.

## 🔍 Example: Complete Workflow

```python
from minimal_flights import search_flights, parse_flights_from_html, PassengerConfig
import requests

# 1. Generate the search URL
url = search_flights(
    origin="JFK",
    destination="LAX",
    departure_date="2025-07-01",
    return_date="2025-07-10",
    passengers=PassengerConfig(adults=2),
    seat_class="economy"
)

# 2. Fetch the HTML (you need to implement this part)
# response = requests.get(url)
# html = response.text

# 3. Parse the results
# results = parse_flights_from_html(html)

# 4. Display flights
# for flight in results.flights[:5]:  # Show first 5 flights
#     print(f"{flight.name}: {flight.price}")
#     print(f"  Departure: {flight.departure}")
#     print(f"  Arrival: {flight.arrival}")
#     print(f"  Duration: {flight.duration}")
#     print(f"  Stops: {flight.stops}")
#     print()
```

## 📝 License

MIT License - feel free to use this in your projects!

## 🙏 Credits

Based on the original `fast-flights` project, refactored for simplicity and clarity.

Original work by AWeirdDev and contributors.

---

<div align="center">

**Made with ❤️ for developers who value simplicity**

</div>
