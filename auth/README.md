# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest test_handler.py

# Run specific test
pytest test_handler.py::TestHealthCheckEndpoint::test_health_check_returns_200