# Testing

This directory contains tests for the OpenHexa Docker images.

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # or
   .\venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

## Running Tests

To run all tests:
```bash
pytest
```

To run specific test files:
```bash
pytest tests/test_*.py
```

## Test Structure

- `test_*.py`: Test files for various components