"""
API clients for SerpApi, Google PageSpeed Insights, and BuiltWith
"""
import requests
import time
from typing import Dict, List, Optional, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)

class APIRateLimitError(Exception):
    """Custom exception for rate limit errors"""
    pass

class APIClient:
    """Base API client with rate limiting and error handling"""
    
    def __init__(self, requests_per_minute: int = 30):
        self.requests_per_minute = requests_per_minute
        self.request_interval = 60.0 / requests_per_minute
        self.last_request_time = 0.0
    
    def _rate_limit(self):
        """Implement rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.request_interval:
            sleep_time = self.request_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

class SerpApiClient(APIClient):
    """Client for SerpApi Google Maps searches"""
    
    def __init__(self):
        super().__init__(Config.MAX_REQUESTS_PER_MINUTE)
        self.api_key = Config.SERPAPI_KEY
        self.base_url = "https://serpapi.com/search"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, APIRateLimitError))
    )
    def search_google_maps(self, query: str, location: str = "California", max_results: int = 100) -> Dict[str, Any]:
        """Search Google Maps for businesses with pagination support"""
        all_results = []
        start = 0
        results_per_page = 20  # SerpApi typical page size
        
        logger.info(f"Searching Google Maps for: {query} in {location} (max {max_results} results)")
        
        while len(all_results) < max_results:
            self._rate_limit()
            
            params = {
                'engine': 'google_maps',
                'q': query,
                'hl': 'en',
                'gl': 'us',
                'll': '@36.7468422,-119.7725868,8z',  # Central Valley coordinates
                'type': 'search',
                'api_key': self.api_key,
                'start': start
            }
            
            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                
                if response.status_code == 429:
                    logger.warning("Rate limit hit on SerpApi")
                    raise APIRateLimitError("SerpApi rate limit exceeded")
                
                response.raise_for_status()
                data = response.json()
                
                if 'error' in data:
                    logger.error(f"SerpApi error: {data['error']}")
                    raise Exception(f"SerpApi error: {data['error']}")
                
                page_results = data.get('local_results', [])
                
                if not page_results:
                    logger.info(f"No more results found at page starting from {start}")
                    break
                
                all_results.extend(page_results)
                logger.info(f"Retrieved {len(page_results)} results from page starting at {start} (total: {len(all_results)})")
                
                # Check if we've reached the limit or if there are no more results
                if len(page_results) < results_per_page:
                    logger.info("Reached end of results (partial page)")
                    break
                
                start += results_per_page
                
            except requests.RequestException as e:
                logger.error(f"Request failed for Google Maps search at start={start}: {e}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error in Google Maps search at start={start}: {e}")
                raise
        
        # Limit to max_results
        final_results = all_results[:max_results]
        logger.info(f"Found {len(final_results)} total results for {query}")
        
        # Return in the same format as before but with all results
        return {
            'local_results': final_results,
            'search_metadata': {
                'total_results': len(final_results),
                'pages_fetched': (start // results_per_page) + 1,
                'query': query,
                'location': location
            }
        }

class GooglePageSpeedClient(APIClient):
    """Client for Google PageSpeed Insights API"""
    
    def __init__(self):
        super().__init__(Config.MAX_REQUESTS_PER_MINUTE)
        self.api_key = Config.GOOGLE_PAGESPEED_API_KEY
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, APIRateLimitError))
    )
    def analyze_url(self, url: str, strategy: str = "mobile") -> Dict[str, Any]:
        """Analyze URL performance with PageSpeed Insights"""
        self._rate_limit()
        
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        params = {
            'url': url,
            'key': self.api_key,
            'strategy': strategy,
            'category': 'performance'
        }
        
        logger.info(f"Analyzing {strategy} performance for: {url}")
        
        try:
            response = requests.get(self.base_url, params=params, timeout=60)
            
            if response.status_code == 429:
                logger.warning("Rate limit hit on PageSpeed Insights")
                raise APIRateLimitError("PageSpeed Insights rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            if 'error' in data:
                logger.error(f"PageSpeed Insights error: {data['error']}")
                raise Exception(f"PageSpeed Insights error: {data['error']}")
            
            # Extract performance score
            lighthouse_result = data.get('lighthouseResult', {})
            categories = lighthouse_result.get('categories', {})
            performance = categories.get('performance', {})
            score = performance.get('score', 0)
            
            # Convert to 0-100 scale
            performance_score = int(score * 100) if score else 0
            
            logger.info(f"Performance score for {url}: {performance_score}/100")
            
            return {
                'url': url,
                'strategy': strategy,
                'performance_score': performance_score,
                'raw_data': data
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed for PageSpeed analysis: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in PageSpeed analysis: {e}")
            raise

class BuiltWithClient(APIClient):
    """Client for BuiltWith API to analyze website technology"""
    
    def __init__(self):
        super().__init__(Config.MAX_REQUESTS_PER_MINUTE)
        self.api_key = Config.BUILTWITH_API_KEY
        self.base_url = "https://api.builtwith.com/v20/api.json"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((requests.RequestException, APIRateLimitError))
    )
    def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain technology stack with BuiltWith"""
        if not self.api_key:
            logger.warning("BuiltWith API key not configured, skipping technology analysis")
            return {'domain': domain, 'technologies': [], 'error': 'API key not configured'}
        
        self._rate_limit()
        
        # Clean domain
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        if '/' in domain:
            domain = domain.split('/')[0]
        
        params = {
            'KEY': self.api_key,
            'LOOKUP': domain
        }
        
        logger.info(f"Analyzing technology stack for: {domain}")
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 429:
                logger.warning("Rate limit hit on BuiltWith")
                raise APIRateLimitError("BuiltWith rate limit exceeded")
            
            response.raise_for_status()
            data = response.json()
            
            if 'Errors' in data and data['Errors']:
                error_msg = ', '.join(data['Errors'])
                logger.error(f"BuiltWith error for {domain}: {error_msg}")
                return {'domain': domain, 'technologies': [], 'error': error_msg}
            
            # Extract technology information
            results = data.get('Results', [])
            technologies = []
            
            if results:
                result = results[0]
                paths = result.get('Result', {}).get('Paths', [])
                
                for path in paths:
                    techs = path.get('Technologies', [])
                    for tech in techs:
                        # Fix Categories handling - handle mixed data types safely
                        categories = tech.get('Categories', [])
                        try:
                            if isinstance(categories, list):
                                # Handle list items that might be dicts or strings
                                category_parts = []
                                for cat in categories:
                                    if isinstance(cat, dict):
                                        # If it's a dict, try to get a name field or convert to string
                                        cat_str = cat.get('Name', str(cat))
                                    else:
                                        cat_str = str(cat)
                                    category_parts.append(cat_str)
                                category_str = ', '.join(category_parts)
                            else:
                                category_str = str(categories) if categories else ''
                        except Exception as e:
                            logger.debug(f"Category parsing issue for {tech.get('Name', 'unknown')}: {e}")
                            category_str = 'Unknown Category'
                        
                        tech_info = {
                            'name': tech.get('Name', ''),
                            'category': category_str,
                            'description': tech.get('Description', ''),
                            'first_detected': tech.get('FirstDetected', ''),
                            'last_detected': tech.get('LastDetected', ''),
                            'tag': tech.get('Tag', ''),
                            'is_premium': tech.get('IsPremium', 'unknown')
                        }
                        technologies.append(tech_info)
            
            logger.info(f"Found {len(technologies)} technologies for {domain}")
            
            return {
                'domain': domain,
                'technologies': technologies,
                'raw_data': data
            }
            
        except requests.RequestException as e:
            logger.error(f"Request failed for BuiltWith analysis: {e}")
            return {'domain': domain, 'technologies': [], 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in BuiltWith analysis: {e}")
            return {'domain': domain, 'technologies': [], 'error': str(e)}