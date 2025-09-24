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

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## Taskmaster Development Workflow & Hygiene

**CRITICAL**: Always practice good Taskmaster hygiene by properly updating task status throughout development.

### Essential Taskmaster Commands for Daily Development

#### Project Status & Navigation
```bash
taskmaster list                           # Show all tasks with current status
taskmaster list --with-subtasks          # Include subtasks in listing
taskmaster next                           # Get next available task to work on
taskmaster show <id>                      # View detailed task information (e.g., taskmaster show 16.1)
```

#### Task Status Management (CRITICAL FOR HYGIENE)
```bash
# BEFORE starting work on any task/subtask
taskmaster set-status --id=<id> --status=in-progress

# AFTER completing any task/subtask
taskmaster set-status --id=<id> --status=done

# Other status options
taskmaster set-status --id=<id> --status=pending    # Reset to pending
taskmaster set-status --id=<id> --status=deferred   # Postpone
taskmaster set-status --id=<id> --status=cancelled  # No longer needed
```

#### Task Management & Updates
```bash
taskmaster add-task --prompt="description" --research        # Add new task with AI assistance
taskmaster update-task --id=<id> --prompt="changes"          # Update specific task with new info
taskmaster update-subtask --id=<id> --prompt="notes"         # Add implementation notes to subtask
taskmaster update --from=<id> --prompt="changes"             # Update multiple tasks from ID onwards
```

#### Task Organization
```bash
taskmaster expand --id=<id> --research --force              # Break task into subtasks
taskmaster add-dependency --id=<id> --depends-on=<id>       # Add task dependency
taskmaster remove-dependency --id=<id> --depends-on=<id>    # Remove dependency
taskmaster validate-dependencies                            # Check for dependency issues
```

### Mandatory Taskmaster Hygiene Practices

#### 1. Status Updates Are REQUIRED
- **ALWAYS** mark task as `in-progress` before starting work
- **ALWAYS** mark task as `done` immediately after completion
- **NEVER** leave tasks in wrong status - this breaks dependency chains
- Update subtasks individually as you complete them

#### 2. Implementation Logging
- Use `update-subtask` to log what you learned during implementation
- Document any blockers, changes, or discoveries
- Add notes about what worked vs what didn't work

#### 3. Dependency Management
- Check `taskmaster next` before starting new work
- Never work on tasks with unmet dependencies
- Use `validate-dependencies` if dependency chain seems broken

#### 4. Progress Tracking
- Run `taskmaster list` regularly to see overall progress
- Use `--with-subtasks` to see detailed breakdown
- Check completion percentages in dashboard

### Workflow Example for AI Sales Intelligence Agent

```bash
# 1. Check what to work on next
taskmaster next

# 2. View task details
taskmaster show 16.1

# 3. Mark as in-progress BEFORE starting
taskmaster set-status --id=16.1 --status=in-progress

# 4. Do the implementation work...
# [implement the actual code]

# 5. Log implementation notes
taskmaster update-subtask --id=16.1 --prompt="Installed langchain-core==0.3.15, langchain-groq==0.2.8, playwright==1.45.0, pandas==2.1.4, tqdm==4.66.1, python-dotenv==1.0.0. All packages installed successfully. Created requirements.txt with pinned versions. Tested imports - all working."

# 6. Mark as done IMMEDIATELY after completion
taskmaster set-status --id=16.1 --status=done

# 7. Check next available task
taskmaster next
```

### Current Project Status

**Project**: AI Sales Intelligence Agent (Tag: gym-software-leads)
**Total Tasks**: 10 main tasks, 31+ subtasks
**Current Priority**: Task 16.1 - Install Dependencies and Create Requirements File

**Remember**: The Taskmaster system tracks all your progress and maintains proper dependency ordering. Following this hygiene ensures the project moves forward systematically and nothing gets forgotten or blocked.
