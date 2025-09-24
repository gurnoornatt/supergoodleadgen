# AI Sales Intelligence Agent

A Python CLI tool that processes gym leads using LangChain, Groq API, and Playwright for web analysis and personalized email generation.

## Project Structure

```
ai_agent/
├── __init__.py                 # Main package initialization
├── main.py                     # CLI entry point
├── README.md                   # This file
├── config/
│   ├── __init__.py
│   └── settings.py            # Configuration management
├── agents/
│   ├── __init__.py
│   ├── analysis_agent.py      # TODO: Website analysis agent
│   └── email_agent.py         # TODO: Email generation agent
├── utils/
│   ├── __init__.py
│   ├── data_processor.py      # TODO: CSV processing utilities
│   ├── playwright_renderer.py # TODO: Web content rendering
│   └── progress_tracker.py    # TODO: Progress monitoring
└── tests/
    ├── __init__.py
    └── test_*.py              # TODO: Test files
```

## Installation

1. **Install dependencies** (from project root):
   ```bash
   pip install -r ai_requirements.txt
   ```

2. **Install Playwright browsers**:
   ```bash
   playwright install
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and set GROQ_API_KEY
   ```

## Usage

### Basic Usage

```bash
# Process gym leads
python ai_agent/main.py --input gym_leads.csv --output processed_leads.csv
```

### Validation Only

```bash
# Validate input file and configuration without processing
python ai_agent/main.py --input gym_leads.csv --validate-only
```

### Help

```bash
python ai_agent/main.py --help
```

## Input Format

Input CSV must contain these columns:
- `gym_name`: Name of the gym/fitness business
- `website_url`: Website URL to analyze

Example:
```csv
gym_name,website_url
"Joe's Gym","https://joesgym.com"
"Fitness First","https://fitnessfirst.example.com"
```

## Output Format

Output CSV includes original columns plus:
- `status`: Processing status (success/failed)
- `error_message`: Error details if processing failed
- `analysis_json`: JSON string with website analysis results
- `generated_email`: Personalized sales email content

## Configuration

Environment variables:
- `GROQ_API_KEY`: **Required** - Groq API key for AI processing
- `GROQ_MODEL_NAME`: Model name (default: meta-llama/llama-4-scout-17b-16e-instruct)
- `CHUNK_SIZE`: Processing chunk size (default: 200)
- `TIMEOUT_SECONDS`: Timeout for operations (default: 15)

## Development Status

✅ **Completed (Task 16)**:
- Environment setup and dependencies
- Configuration management
- Project structure organization
- API connection verification

🚧 **In Development**:
- Data processing pipeline (Task 17-18)
- Playwright web renderer (Task 19)
- LangChain AI agents (Task 20-21)
- Error handling and logging (Task 22-23)
- Main pipeline integration (Task 24)
- Documentation and optimization (Task 25)

## Integration with Existing Project

This AI agent is cleanly separated from existing pain-gap audit tools while leveraging shared utilities:

- **Shared**: Environment configuration (.env), logging patterns, utility functions
- **Separate**: AI-specific code, dependencies, and functionality
- **Compatible**: Existing scripts continue to work unchanged

## Testing

Run structure tests:
```bash
python test_ai_agent_structure.py
```

Run individual component tests:
```bash
python test_imports.py          # Dependencies
python test_env_loading.py      # Environment
python test_playwright.py       # Browser automation
python test_groq_api.py         # AI model connection
```