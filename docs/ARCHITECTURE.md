# RedFlag System Architecture

## Overview

RedFlag is designed as a modular, scalable lead generation and assessment platform optimized for high-volume processing of small business data across Central Valley markets.

## System Components

### 1. Data Ingestion Layer

#### SerpAPI Integration (`api_client.py`)
- **Purpose**: Primary data source for business discovery
- **Rate Limiting**: 100 searches/hour on paid tier
- **Error Handling**: Exponential backoff with circuit breaker
- **Caching**: 24-hour cache for duplicate queries

```python
class SerpApiClient:
    def __init__(self):
        self.api_key = Config.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
        self.rate_limiter = RateLimiter(max_calls=100, time_window=3600)
    
    def search_google_maps(self, query, location, max_results=20):
        # Implements rate limiting, error handling, caching
```

#### Search Strategy
- **Multi-Category Approach**: 8 search patterns per city
- **Geographical Precision**: City-specific location parameters  
- **Pagination Handling**: Up to 100 results per category
- **Chain Filtering**: 25+ franchise patterns excluded

### 2. Business Intelligence Layer

#### Chain Detection Algorithm
```python
def is_chain_gym(business_name: str) -> bool:
    """
    Sophisticated chain detection using:
    - Exact name matching
    - Partial substring matching  
    - Franchise indicator words
    - Review count thresholds
    """
```

#### Independence Scoring
5-point scale based on:
1. Name contains owner/family indicators
2. Local/regional branding patterns
3. Review count < 500 (chains typically higher)
4. Absence of franchise legal terms
5. Geographic clustering patterns

#### Lead Qualification Matrix
```
HIGH PRIORITY (RED):    Mobile score < 60, No SSL, Outdated tech
MEDIUM PRIORITY (YELLOW): Mobile score 60-80, Basic tech stack  
LOW PRIORITY (GREEN):   Mobile score > 80, Modern infrastructure
```

### 3. Digital Assessment Engine

#### Performance Analysis
- **PageSpeed Insights API**: Mobile performance scoring
- **SSL Certificate Check**: Security infrastructure assessment
- **Technology Stack Analysis**: BuiltWith API integration
- **Local SEO Evaluation**: Google Business Profile optimization

#### Scoring Algorithm
```python
def calculate_pain_score(business_data: dict) -> int:
    """
    Proprietary pain scoring algorithm considering:
    - Mobile performance (40% weight)
    - Technology modernization (30% weight)  
    - Local SEO optimization (20% weight)
    - Security infrastructure (10% weight)
    
    Returns: Integer score 0-100 (higher = more pain/opportunity)
    """
```

### 4. Asset Generation Pipeline

#### Screenshot Capture
- **Selenium WebDriver**: Full-page website screenshots
- **Error Handling**: Fallback to homepage if specific pages fail
- **Optimization**: WebP compression for storage efficiency
- **Metadata**: Capture timestamp, device viewport, performance metrics

#### Logo Extraction & Generation
```python
def extract_or_generate_logo(website_url: str, business_name: str) -> str:
    """
    Priority order:
    1. Extract from website favicon
    2. Extract from social media profiles
    3. Generate fallback using business name
    4. Use generic gym icon as last resort
    """
```

### 5. Revenue & Budget Estimation

#### Size Classification Algorithm
```python
def estimate_gym_size(business_data: dict) -> str:
    """
    Classification based on:
    - Google review count patterns
    - Address analysis (square footage indicators)
    - Staff listings and social media presence
    - Competition analysis
    
    Returns: "boutique", "mid_size", "large_independent"
    """
```

#### Budget Calculation Matrix
| Gym Size | Monthly Revenue | Software Budget Range |
|----------|----------------|---------------------|
| Boutique (50-150 members) | $8K-$25K | $270-$750/month |
| Mid-size (150-400 members) | $25K-$80K | $750-$2,400/month |
| Large (400+ members) | $80K-$200K | $2,400-$4,625/month |

### 6. Automation & Integration Layer

#### Make.com Workflow
```
Google Sheets Trigger → Data Validation → Template Population → PDF Generation → Distribution
```

#### PDF Template Variables
- Business name and contact information
- Performance scores and technology gaps
- Competitive analysis data  
- Personalized recommendations
- Budget estimates and ROI projections

### 7. Data Storage & Management

#### File Organization
```
data/
├── raw/                 # Scraped JSON data
├── processed/           # Qualified leads CSV  
├── assets/             
│   ├── screenshots/     # Website captures
│   └── logos/          # Extracted/generated logos
├── reports/            # Generated PDF audits
└── archive/            # Historical data
```

#### Data Lifecycle
1. **Ingestion**: Raw scraping data (JSON)
2. **Processing**: Qualification and scoring (CSV)
3. **Enrichment**: Asset generation and analysis
4. **Report Generation**: PDF audit creation
5. **Archive**: 90-day retention for performance analysis

## Scalability Considerations

### Horizontal Scaling
- **API Distribution**: Multiple SerpAPI keys for higher throughput
- **Parallel Processing**: City-based processing parallelization
- **Queue Management**: Redis/Celery for background job processing

### Performance Optimization
- **Caching Strategy**: Redis for API response caching
- **Database Optimization**: PostgreSQL with proper indexing
- **Asset Storage**: CloudFlare CDN for global distribution
- **Monitoring**: Comprehensive logging and alerting

### Cost Management
- **API Efficiency**: Intelligent query deduplication
- **Resource Utilization**: Auto-scaling based on demand
- **Storage Optimization**: Automated archive and cleanup

## Security Architecture

### API Key Management
- Environment variable storage only
- Rotation schedule every 90 days
- Access logging and monitoring
- Principle of least privilege

### Data Protection
- Encryption at rest and in transit
- PII handling compliance
- Secure credential storage
- Regular security audits

### Access Control
- Team-based authentication
- Role-based permissions
- Audit logging for all actions
- Secure development practices

## Monitoring & Observability

### Key Metrics
- **Lead Discovery Rate**: Businesses found per hour
- **Qualification Accuracy**: RED/GREEN classification precision  
- **API Efficiency**: Cost per qualified lead
- **System Performance**: Response times and error rates

### Alerting Strategy
- **Critical**: System downtime or API failures
- **Warning**: Performance degradation or high error rates
- **Info**: Daily summary reports and trend analysis

### Dashboard Components
- Real-time processing status
- Cost tracking and budget alerts
- Quality metrics and conversion rates
- Performance benchmarks and SLA monitoring

## Deployment Architecture

### Development Environment
- Local development with Docker Compose
- Mock API responses for testing
- Comprehensive test coverage
- CI/CD pipeline integration

### Staging Environment
- Production-like infrastructure
- Real API integration testing
- Performance and load testing  
- Security vulnerability scanning

### Production Environment
- Auto-scaling containerized deployment
- Multi-region failover capability
- Comprehensive monitoring and logging
- Automated backup and recovery

## Future Enhancements

### Phase 2: Market Expansion
- Additional Central Valley cities
- New business categories (restaurants, salons)
- Enhanced competitive analysis
- Advanced ML-based scoring

### Phase 3: Intelligence Layer
- Predictive lead scoring
- Market trend analysis
- Automated follow-up optimization
- Customer lifetime value modeling

### Phase 4: Platform Evolution
- Self-service dashboard
- Real-time market insights
- Advanced reporting and analytics
- Integration marketplace

## Technical Debt & Maintenance

### Current Technical Debt
- Hardcoded configuration values
- Limited error recovery mechanisms
- Basic logging and monitoring
- Manual scaling procedures

### Maintenance Schedule
- **Weekly**: Dependency updates and security patches
- **Monthly**: Performance optimization and cleanup
- **Quarterly**: Architecture review and refactoring
- **Annually**: Technology stack evaluation and upgrades

---

*This architecture supports our goal of processing 200+ leads daily while maintaining <$0.50 cost per qualified lead across all Central Valley markets.*