# Contributing to RedFlag

> **Internal Team Development Guidelines**

Thank you for contributing to RedFlag! This document outlines our development standards, workflow, and best practices for authorized team members.

## 🚨 Important Notice

This is a **proprietary project** with restricted access. All contributions must be made by authorized team members only. Unauthorized access, copying, or distribution is strictly prohibited.

## 🔄 Development Workflow

### 1. Branch Strategy

```bash
main           # Production-ready code, always deployable
├── develop    # Integration branch for features
├── feature/*  # New features and enhancements
├── hotfix/*   # Critical bug fixes for production
└── release/*  # Release preparation branches
```

### 2. Feature Development Process

1. **Create Feature Branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature-name
   ```

2. **Implement Changes**
   - Write code following our standards (see below)
   - Add comprehensive tests
   - Update documentation as needed
   - Test thoroughly in development environment

3. **Submit Pull Request**
   - Use descriptive PR titles and descriptions
   - Reference any related issues
   - Include testing instructions
   - Request review from at least one team member

4. **Code Review Process**
   - All PRs require approval from a senior team member
   - Address feedback promptly and professionally
   - Ensure all CI/CD checks pass
   - Squash commits before merging when appropriate

## 📋 Code Standards

### Python Style Guide

We follow **PEP 8** with these specific guidelines:

```python
# Imports: stdlib, third-party, local
import os
import sys
from datetime import datetime

import requests
import pandas as pd

from api_client import SerpApiClient
from config import Config

# Constants in UPPER_CASE
API_TIMEOUT = 30
MAX_RETRIES = 3

# Classes in PascalCase
class LeadProcessor:
    """Process and qualify business leads.
    
    This class handles the core business logic for lead qualification,
    scoring, and categorization based on digital infrastructure analysis.
    """
    
    def __init__(self, config: Config):
        self.config = config
        self._api_client = None
    
    def process_leads(self, raw_data: list) -> list:
        """Process raw lead data into qualified prospects.
        
        Args:
            raw_data: List of raw business data from scraping
            
        Returns:
            List of processed and scored leads
            
        Raises:
            ValueError: If raw_data is empty or invalid
        """
        if not raw_data:
            raise ValueError("Raw data cannot be empty")
            
        # Implementation here
        pass

# Functions in snake_case with descriptive names
def calculate_pain_score(business_data: dict) -> int:
    """Calculate pain score based on digital infrastructure gaps."""
    pass
```

### Documentation Standards

#### Function Documentation
```python
def scrape_city_gyms(city: str, max_results: int = 100) -> list:
    """Scrape independent gyms for a specific city.
    
    Performs comprehensive gym discovery across multiple search categories,
    filters out major chains, and applies independence scoring.
    
    Args:
        city: Target city name (e.g., "Fresno", "Bakersfield")
        max_results: Maximum number of results per search category
        
    Returns:
        List of gym data dictionaries with the following keys:
        - business_name: Name of the gym/fitness business
        - address: Physical address
        - phone: Contact phone number
        - website: Website URL (if available)
        - rating: Google rating (1-5 stars)
        - reviews: Number of Google reviews
        - independent_score: Independence likelihood (1-5)
        
    Raises:
        APIError: If SerpAPI request fails
        ValueError: If city parameter is invalid
        
    Example:
        >>> gyms = scrape_city_gyms("Fresno", max_results=50)
        >>> len(gyms)
        45
        >>> gyms[0]['business_name']
        'Strong Family Fitness'
    """
```

### Error Handling Standards

```python
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Raised when external API calls fail."""
    pass

def safe_api_call(endpoint: str, params: dict) -> Optional[dict]:
    """Make API call with comprehensive error handling.
    
    Args:
        endpoint: API endpoint URL
        params: Request parameters
        
    Returns:
        API response data or None if failed
    """
    try:
        response = requests.get(endpoint, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.Timeout:
        logger.error(f"API timeout for {endpoint}")
        return None
        
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error {e.response.status_code}: {e}")
        if e.response.status_code == 429:
            # Handle rate limiting
            time.sleep(60)
            return safe_api_call(endpoint, params)
        return None
        
    except Exception as e:
        logger.exception(f"Unexpected error calling {endpoint}: {e}")
        return None
```

### Testing Standards

#### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch

class TestLeadProcessor(unittest.TestCase):
    """Test suite for LeadProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Mock()
        self.processor = LeadProcessor(self.config)
    
    def test_process_leads_empty_input(self):
        """Test that empty input raises ValueError."""
        with self.assertRaises(ValueError):
            self.processor.process_leads([])
    
    @patch('api_client.SerpApiClient')
    def test_process_leads_success(self, mock_client):
        """Test successful lead processing."""
        # Mock API response
        mock_client.return_value.search.return_value = {
            'local_results': [{'title': 'Test Gym', 'rating': 4.5}]
        }
        
        # Test implementation
        result = self.processor.process_leads([{'name': 'Test Gym'}])
        
        # Assertions
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
```

#### Integration Tests
```python
class TestEndToEndPipeline(unittest.TestCase):
    """End-to-end testing of the complete pipeline."""
    
    @unittest.skipIf(not os.getenv('RUN_INTEGRATION_TESTS'), 
                     "Integration tests disabled")
    def test_full_pipeline_bakersfield(self):
        """Test complete pipeline with real API calls."""
        # This test uses actual API keys and should be run sparingly
        pass
```

## 🔧 Development Environment

### Local Setup

1. **Python Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

2. **Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your development API keys
   ```

3. **Pre-commit Hooks**
   ```bash
   pre-commit install
   # Automatically runs linting and tests before commits
   ```

### Development Tools

#### Code Formatting
```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .
```

#### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_scrapers.py -v

# Run integration tests (requires API keys)
RUN_INTEGRATION_TESTS=1 pytest tests/test_integration.py
```

#### Type Checking
```bash
# Type check with mypy
mypy . --ignore-missing-imports
```

## 📊 Performance Guidelines

### API Usage Optimization

- **Rate Limiting**: Always implement exponential backoff
- **Caching**: Cache API responses when appropriate
- **Batch Processing**: Group API calls efficiently
- **Error Recovery**: Implement retry logic with circuit breakers

```python
import time
from functools import wraps

def rate_limited(max_per_second: float):
    """Decorator to rate limit function calls."""
    min_interval = 1.0 / max_per_second
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            ret = func(*args, **kwargs)
            last_called[0] = time.time()
            return ret
        return wrapper
    return decorator

@rate_limited(2.0)  # Max 2 calls per second
def api_call():
    pass
```

### Memory Management

- Process data in chunks for large datasets
- Use generators instead of lists where possible
- Clean up resources explicitly (file handles, connections)
- Monitor memory usage in production

### Logging Standards

```python
import logging
import json
from datetime import datetime

# Structured logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('redflag.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def log_api_call(endpoint: str, params: dict, response_time: float):
    """Log API call details in structured format."""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'event': 'api_call',
        'endpoint': endpoint,
        'params': params,
        'response_time': response_time
    }
    logger.info(json.dumps(log_data))
```

## 🚀 Deployment Guidelines

### Staging Environment

- All features must be tested in staging before production
- Use production-like data volumes for performance testing
- Verify all integrations work correctly
- Run full test suite including integration tests

### Production Deployment

```bash
# Build and test
./scripts/build.sh
./scripts/test.sh

# Deploy to staging
./scripts/deploy.sh staging

# Run smoke tests
./scripts/smoke_test.sh staging

# Deploy to production (requires approval)
./scripts/deploy.sh production
```

### Configuration Management

- Use environment variables for all configuration
- Never commit secrets or API keys
- Use separate configs for each environment
- Document all configuration options

## 🔍 Code Review Checklist

### For Authors
- [ ] Code follows style guidelines
- [ ] All functions have docstrings
- [ ] Tests cover new functionality
- [ ] No secrets or API keys committed
- [ ] Error handling is comprehensive
- [ ] Performance considerations addressed
- [ ] Documentation updated if needed

### For Reviewers
- [ ] Code is readable and maintainable
- [ ] Logic is correct and efficient
- [ ] Edge cases are handled
- [ ] Tests are comprehensive
- [ ] Security considerations reviewed
- [ ] API usage is optimized
- [ ] Follows established patterns

## 🐛 Bug Reporting

### Internal Bug Reports

Use our GitHub Issues with this template:

```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.7]
- Branch: [e.g., feature/new-scraper]

## Additional Context
Screenshots, logs, or other relevant information
```

### Priority Levels
- **P0 Critical**: Production system down
- **P1 High**: Major functionality broken
- **P2 Medium**: Important feature affected
- **P3 Low**: Minor issue or enhancement

## 📚 Resources

### Internal Documentation
- **API Documentation**: `docs/API.md`
- **Deployment Guide**: `docs/DEPLOYMENT.md`
- **Architecture Overview**: `docs/ARCHITECTURE.md`

### External Resources
- [SerpAPI Documentation](https://serpapi.com/search-api)
- [Google PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started)
- [BuiltWith API](https://api.builtwith.com/)

## 🤝 Team Communication

### Channels
- **#redflag-dev**: Development discussions
- **#redflag-alerts**: Automated monitoring alerts
- **#redflag-releases**: Release announcements

### Meetings
- **Daily Standups**: 9:00 AM PST
- **Sprint Planning**: Bi-weekly Mondays
- **Retrospectives**: End of each sprint
- **Architecture Reviews**: Monthly

### Decision Making
- Technical decisions require team consensus
- Architecture changes need senior approval
- Breaking changes require advanced notice

---

## Questions?

For any questions about contributing, reach out to:
- **Tech Lead**: [name@company.com]
- **DevOps**: [devops@company.com]
- **Product Owner**: [po@company.com]

*Together we build better lead generation systems!* 🚀