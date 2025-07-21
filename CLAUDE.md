# Pain-Gap Audit Automation Script

## Project Overview
Automated script to identify and qualify small business sales leads in California's Central Valley, generating personalized Pain-Gap Audit PDFs at scale.

## Goal
Process 200+ leads per day and generate 50+ 'RED' audits with cost per lead under $0.50.

## Tech Stack
- **Python** - Core automation script
- **APIs**: SerpApi (Google Maps), Google PageSpeed Insights, BuiltWith
- **Data**: Google Sheets API, CSV output
- **Images**: Pillow (Python) for logo generation
- **Screenshots**: Selenium/Playwright for website capture
- **Automation**: Make.com for PDF generation workflow
- **Template**: Google Slides for PDF template

## Key Components

### 1. Lead Ingestion & Scraping
- Google Maps scraping via SerpApi
- Target: Central Valley cities business listings
- Extract: Business Name, Website URL, Phone, Google Business Profile, Address
- Handle pagination and rate limits

### 2. Website Analysis
- **Performance**: PageSpeed Insights API for mobile scores
- **Technology**: BuiltWith API for tech stack analysis
- **Scoring**: RED flag if mobile score < 60/100

### 3. Asset Collection
- **Screenshots**: Full-page captures for RED leads
- **Logos**: Extract from websites with Pillow fallback (400×120px colored rectangles)
- **Storage**: Cloud storage for assets

### 4. PDF Generation Pipeline
- **Template**: Google Slides template with placeholders
- **Automation**: Make.com 3-step scenario:
  1. Watch Google Sheet for new RED leads
  2. Populate template with data/assets
  3. Export PDF and write public link back to sheet

### 5. VA Handoff
- Clean Google Sheet output format
- All data needed for follow-up calls
- Simple, non-technical interface

## Environment Setup

### Required API Keys
```bash
# Add to .env file
SERPAPI_KEY=your_serpapi_key
GOOGLE_PAGESPEED_API_KEY=your_pagespeed_key
BUILTWITH_API_KEY=your_builtwith_key
GOOGLE_SHEETS_CREDENTIALS=path_to_service_account.json
```

### Python Dependencies
```bash
pip install requests pandas pillow google-api-python-client selenium
```

## Data Schema

### Lead Data Structure
- Business Name
- Website URL
- Phone Number
- Google Business Profile Link
- Physical Address
- Mobile Performance Score (0-100)
- Technology Stack
- Status (RED/GREEN)
- Screenshot URL
- Logo URL
- PDF Audit Link
- Error Notes

## Performance Requirements
- Process 200+ leads daily
- Generate 50+ RED audits
- Cost per RED lead < $0.50
- Reliable error handling and recovery

## Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run lead scraping
python scrape_leads.py --category "restaurants" --city "Fresno"

# Run performance analysis
python analyze_performance.py --input leads.csv

# Run full pipeline
python main.py --config config.json
```

## Testing
- Test API connections individually
- Verify data extraction accuracy
- Test error handling with bad data
- End-to-end pipeline testing
- VA usability testing

## Deployment
- Host on low-cost cloud solution (DigitalOcean/Heroku/AWS Lambda)
- Scheduled execution via cron
- Environment variables and secrets management
- Monitoring and alerting setup

## Quality Assurance
- Comprehensive error handling
- Rate limit management with exponential backoff
- Data validation at each step
- Logging and monitoring throughout
- Backup and recovery procedures