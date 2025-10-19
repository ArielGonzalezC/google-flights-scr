# Project Structure

## Minimal Implementation (Recommended)

For a simple, easy-to-understand implementation, use:

- **`minimal_flights.py`** - All core functionality in a single, well-commented file (~500 lines)
- **`example.py`** - Command-line interface for searching flights
- **`test.py`** - Simple tests
- **`requirements.txt`** - Only 3 dependencies needed

This is the **recommended** approach if you want:
- ✅ Simple code that's easy to understand
- ✅ Minimal dependencies
- ✅ Full control over the implementation
- ✅ Easy to modify and extend

## Full Implementation (Original)

The `fast_flights/` directory contains the original, full-featured implementation with:

- Multiple specialized modules
- Additional features (cookies, fallback modes, etc.)
- Protobuf definitions and generated code
- More robust error handling

Use this if you need:
- Advanced features like Playwright fallback
- Integration with the original fast-flights package
- Complete compatibility with existing code

## Quick Comparison

| Feature | Minimal | Full |
|---------|---------|------|
| Files | 1 main file | 20+ files |
| Lines of code | ~500 | ~4,700 |
| Dependencies | 3 | 3+ (optional: playwright) |
| Learning curve | Easy | Moderate |
| Flexibility | High | High |
| Features | Core only | Advanced |

## Which Should You Use?

**Use `minimal_flights.py` if:**
- You're learning how Google Flights scraping works
- You want to customize the code for your needs
- You prefer simple, readable code
- You only need basic functionality

**Use `fast_flights/` if:**
- You need advanced features (Playwright fallback, Bright Data)
- You're integrating with existing fast-flights code
- You want the most robust implementation

## Files Overview

### Core Files (Minimal Approach)
- `minimal_flights.py` - Main implementation
- `example.py` - CLI tool
- `test.py` - Simple tests
- `requirements.txt` - Dependencies
- `README.md` - Documentation

### Original Implementation
- `fast_flights/` - Full package
  - `flights.proto` - Protobuf schema
  - `flights_pb2.py` - Generated protobuf code (required by minimal_flights.py)
  - `core.py` - Main logic
  - `parser.py` - HTML parsing
  - `schema.py` - Data structures
  - Other modules for advanced features

### Documentation & Examples
- `docs/` - Documentation files
- `examples/` - Example scripts
- `mkdocs.yml` - Documentation configuration

### Configuration
- `.gitignore` - Git ignore rules
- `pyproject.toml` - Package metadata
- `setup.py` - Installation script
- `Pipfile` - Dependency management

## Getting Started

1. **For minimal approach:**
   ```bash
   pip install -r requirements.txt
   python example.py --help
   ```

2. **For full package:**
   ```bash
   pip install -e .
   python -m fast_flights
   ```

## Migration

If you're currently using the full implementation and want to switch to minimal:

```python
# Old (full implementation)
from fast_flights import create_filter, FlightData, Passengers

# New (minimal implementation)
from minimal_flights import search_flights, FlightQuery, PassengerConfig
```

The minimal implementation provides the same core functionality with a cleaner API.
