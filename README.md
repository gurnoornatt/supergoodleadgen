# RedFlag

A tool to find independent gyms and analyze their websites to identify sales opportunities.

We built this to help our sales team find gym owners who need better software. It scrapes Google Maps for independent gyms (filters out chains like Planet Fitness), checks their websites, and creates reports showing what's broken or missing.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)

## What it does

- Searches Google Maps for gyms in specific cities
- Filters out major chains to focus on independent gyms
- Checks their websites for basic stuff (mobile performance, SSL, etc.)
- Generates a score based on how much help they need
- Creates CSV files with contact info and analysis

## Example results

We tested this on Bakersfield and Fresno. Found:
- **Bakersfield**: 80 independent gyms, 65 good sales leads
- **Fresno**: 98 independent gyms, 86 good sales leads
- **Key finding**: 100% of independent gyms have terrible websites or no website at all

## Quick start

```bash
# Get the code
git clone https://github.com/gurnoornatt/supergoodleadgen.git
cd supergoodleadgen

# Install requirements
pip install -r requirements.txt

# Copy example config and add your API keys
cp .env.example .env
# Edit .env with your API keys

# Run it
python scrape_fresno_gyms.py
python analyze_bakersfield_results.py
```

## API keys you need

- **SerpAPI**: For Google Maps scraping (get at serpapi.com)
- **Google PageSpeed**: For website performance checking
- **BuiltWith**: For technology stack analysis (optional)

Add these to your `.env` file.

## How it works

1. **Search**: Uses SerpAPI to find gyms on Google Maps
2. **Filter**: Removes chains using a list of 25+ major franchises
3. **Analyze**: Checks websites and scores them
4. **Output**: Creates CSV with business info and opportunity scores

## Chain filtering

The system knows about major chains and skips them:
- Planet Fitness, LA Fitness, 24 Hour Fitness
- Anytime Fitness, Gold's Gym, etc.
- Full list in the scraper files

## Files

- `scrape_bakersfield_gyms.py` - Scrapes Bakersfield gyms
- `scrape_fresno_gyms.py` - Scrapes Fresno gyms
- `demo_bakersfield_gyms.py` - Shows analysis results
- `api_client.py` - Handles SerpAPI calls
- `config.py` - Configuration management

## Output format

Each gym gets scored and categorized:
- **RED**: Bad website, good sales opportunity (mobile score < 60)
- **YELLOW**: Okay website, medium opportunity
- **GREEN**: Good website, probably not interested

## Real results

From our Bakersfield test:
```
NasPower Gym Bakersfield
- Mobile score: 38/100
- 600+ members, $48k/month revenue
- Status: RED (hot lead)
- Problem: Website barely works on mobile
```

## Project structure

```
supergoodleadgen/
├── scrape_*.py           # City-specific scrapers
├── demo_*.py             # Analysis and results
├── api_client.py         # SerpAPI wrapper
├── config.py             # Settings
├── requirements.txt      # Dependencies
└── docs/                 # More documentation
```

## Adding new cities

Copy an existing scraper file and change the city name:

```python
# In scrape_YOUR_CITY_gyms.py
results = serpapi.search_google_maps(
    query="gym fitness center YOUR_CITY CA",
    location="YOUR_CITY, CA",
    max_results=20
)
```

## Contributing

Found a bug or want to add features?
- Open an issue on GitHub
- Submit a pull request
- Email us: orrixteam@gmail.com

## Who made this

Built by Orrix (orrixteam@gmail.com) to help sales teams find better leads.

Lead developer: gnatt@usfca.edu

## License

MIT License - use it however you want.