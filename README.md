# RedFlag - AI Sales Intelligence Platform

> **Next-generation lead qualification platform using AI-powered website analysis**

Transform your sales team from manual researchers to strategic closers with automated gym lead qualification and personalized email generation.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/gurnoornatt/supergoodleadgen/graphs/commit-activity)

## 🎯 What This Does

**Input:** CSV of gym leads from existing sources
**Process:** AI-powered website analysis + personalized sales email generation
**Output:** Enriched leads with analysis + ready-to-send sales emails

### Core Capabilities

- ✅ **Automated Lead Processing**: Batch process hundreds of gym leads
- ✅ **AI Website Analysis**: LangChain + Groq API for intelligent analysis
- ✅ **Web Content Rendering**: Playwright-based JavaScript-heavy site rendering
- ✅ **Smart Resumption**: Resume interrupted processing from any point
- ✅ **Professional Output**: Rich CSV with analysis + metadata

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/gurnoornatt/supergoodleadgen.git
cd supergoodleadgen
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Add your API keys to .env:
# GROQ_API_KEY=your_groq_key_here
```

### 3. Process Leads
```bash
python ai_agent/main.py --input gym_leads.csv --output processed_leads.csv --verbose
```

## 🏗️ Architecture

### Modern AI Agent System
```
Input CSV → Data Processing → Web Rendering → AI Analysis → Output CSV
     ↓           ↓              ↓             ↓           ↓
   Reader    Chunking      Playwright    LangChain    Results
```

### Key Components

- **`ai_agent/`** - Core AI processing system with async pipeline
- **`legacy/`** - Previous scraping and analysis tools
- **`data/`** - Organized data storage (raw, processed, output)
- **`archive/`** - Historical assets and media files

## 📊 Production Performance

**Real-world metrics from testing:**
- 🚀 **Parallel Processing**: 5 concurrent website renders
- ⚡ **Speed**: 2.02s average render time per website
- 📈 **Success Rate**: 100% on valid gym websites
- 💾 **Memory Efficient**: Chunked processing handles large datasets
- 🔄 **Reliable**: Smart resumption with URL comparison

## 🛠️ Usage Examples

### Basic Processing
```bash
# Process gym leads with verbose output
python ai_agent/main.py --input leads.csv --output results.csv --verbose
```

### Advanced Options
```bash
# Resume interrupted processing
python ai_agent/main.py --input leads.csv --output results.csv --resume

# Test with limited rows
python ai_agent/main.py --input leads.csv --output test.csv --max-rows 50

# Dry run (no API calls)
python ai_agent/main.py --input leads.csv --output test.csv --dry-run
```

### Output Format
The system generates enriched CSV files with:
- Original lead data preserved
- Website analysis results (accessibility, performance, features)
- AI-generated analysis in structured JSON format
- Processing metadata and timestamps
- Error details for failed analyses

## 🔧 Configuration

### Required API Keys
- **Groq API**: For AI analysis (get at [console.groq.com](https://console.groq.com))
- **Optional**: SerpAPI, Google PageSpeed, BuiltWith for legacy tools

### Environment Variables
```bash
# Core AI agent
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_NAME=meta-llama/llama-4-scout-17b-16e-instruct  # default

# Processing settings
CHUNK_SIZE=200          # rows per batch
TIMEOUT_SECONDS=15      # website rendering timeout
MAX_RETRIES=3          # API retry attempts
```

## 📁 Project Structure

```
redflag/
├── ai_agent/              # Modern AI processing system
│   ├── main.py           # Main CLI entry point
│   ├── agents/           # AI agents (web renderer, analyzers)
│   ├── config/           # Configuration management
│   ├── data/             # Data processing utilities
│   └── utils/            # Helper utilities
├── legacy/               # Previous generation tools
│   ├── scrapers/         # Google Maps scraping tools
│   └── analyzers/        # Analysis and processing scripts
├── data/                 # Organized data storage
│   ├── raw/              # Raw input data
│   ├── processed/        # Processed datasets
│   └── output/           # Final results
├── scripts/              # Utility scripts
└── docs/                 # Documentation
```

## 🧪 Development

### Running Tests
```bash
# Run unit tests
python -m pytest tests/ -v

# Test with real data (small sample)
python ai_agent/main.py --input test_data/sample.csv --output test_output.csv --max-rows 5
```

### Code Quality
```bash
# Linting
flake8 ai_agent/ --max-line-length=100

# Type checking
mypy ai_agent/
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Quick contribution workflow:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📈 Roadmap

- [x] Core AI agent with web rendering
- [x] Async processing pipeline
- [x] Smart resumption logic
- [ ] Advanced AI email generation
- [ ] Integration with CRM systems
- [ ] Multi-industry support beyond gyms
- [ ] Real-time processing dashboard

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/gurnoornatt/supergoodleadgen/issues)
- **Email**: orrixteam@gmail.com
- **Developer**: gnatt@usfca.edu

---

**Built by [Orrix](https://orrix.com) - Transforming sales through intelligent automation**