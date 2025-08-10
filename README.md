# mini-matchers

A lightweight Python library that enables the use of matcher objects with standard `assert` statements. Write concise and expressive tests for dynamic values and complex data structures.

## Basic Usage

Use matcher objects directly with standard `assert` statements:

```python
from mini_matchers import regex, around_now, greater_than, any_of, contains
from datetime import datetime

def test_mytest():
    actual = myfunc()
    assert actual == {
        "prop1": 42,
        "random_id": regex(r"[0-9]{10}"),
        "prop_date": around_now(),
        "prop_date2": around_now(300),  # Within 5 minutes
        "status": any_of("success", "completed", "done"),
        "message": contains("Hello")
    }
```

## API Reference

| Function | Description | Example |
|----------|-------------|---------|
| `regex(pattern, flags=0)` | Regular expression matching | `assert "test123" == regex(r"test\\d+")` |
| `around_now(seconds=60)` | Time within N seconds of now | `assert datetime.now() == around_now()` |
| `greater_than(value)` | Greater than comparison | `assert 10 == greater_than(5)` |
| `less_than(value)` | Less than comparison | `assert 3 == less_than(10)` |
| `any_of(*values)` | Match any of the given values | `assert "success" == any_of("success", "ok")` |
| `contains(substring)` | String contains substring | `assert "hello world" == contains("world")` |

## Development

### Development Setup

```bash
# Clone the repository
git clone https://github.com/r-tamura/mini-matchers.git
cd mini-matchers

# Install dependencies
uv sync

# Run tests
uv run pytest

# Type checking
uv run mypy mini_matchers/
```