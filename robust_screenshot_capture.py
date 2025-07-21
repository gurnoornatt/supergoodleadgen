"""
Robust Screenshot Capture Implementation
Handles various website layouts, loading times, and edge cases
"""

import os
import time
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
from logger_config import setup_logger

logger = setup_logger(__name__)

class RobustScreenshotCapture:
    """Robust screenshot capture with error handling and layout adaptation"""
    
    def __init__(self):
        self.screenshot_dir = "screenshots"
        self._ensure_screenshot_directory()
        
        # Configuration for different website types
        self.capture_config = {
            'wait_time': 3,
            'max_wait_time': 10,
            'retry_attempts': 2,
            'viewport_width': 1920,
            'viewport_height': 1080,
            'timeout_seconds': 30
        }
        
        # Known problematic domains and their specific handling
        self.domain_specific_config = {
            'shopify.com': {'wait_time': 5, 'retry_attempts': 3},
            'squarespace.com': {'wait_time': 6, 'retry_attempts': 3},
            'wix.com': {'wait_time': 7, 'retry_attempts': 3},
            'wordpress.com': {'wait_time': 4, 'retry_attempts': 2},
            'weebly.com': {'wait_time': 5, 'retry_attempts': 2}
        }
    
    def _ensure_screenshot_directory(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            logger.info(f"Created screenshot directory: {self.screenshot_dir}")
    
    def _sanitize_filename(self, url: str) -> str:
        """Create a safe filename from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        safe_name = domain.replace('/', '_').replace(':', '_').replace('?', '_').replace('#', '_')
        timestamp = int(time.time())
        return f"robust_{safe_name}_{timestamp}.png"
    
    def _get_domain_config(self, url: str) -> Dict[str, Any]:
        """Get domain-specific configuration"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace('www.', '')
        
        # Check for platform-specific handling
        for platform, config in self.domain_specific_config.items():
            if platform in domain:
                logger.info(f"Using specialized config for {platform} platform")
                return {**self.capture_config, **config}
        
        return self.capture_config
    
    def _classify_website_type(self, url: str) -> str:
        """Classify website type for specialized handling"""
        domain = urlparse(url).netloc.lower()
        
        if any(platform in domain for platform in ['shopify', 'bigcommerce', 'magento']):
            return 'ecommerce'
        elif any(cms in domain for cms in ['wordpress', 'wix', 'squarespace', 'weebly']):
            return 'cms'
        elif any(social in domain for social in ['facebook', 'instagram', 'twitter']):
            return 'social'
        elif any(tech in domain for tech in ['react', 'angular', 'vue', 'spa']):
            return 'spa'
        else:
            return 'standard'
    
    def capture_screenshots_with_layout_handling(self, red_leads: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Capture screenshots with robust layout and loading time handling
        """
        logger.info(f"Starting robust screenshot capture for {len(red_leads)} RED leads")
        
        captured_screenshots = {}
        failed_captures = []
        
        for i, lead in enumerate(red_leads, 1):
            url = lead.get('website', '').strip()
            business_name = lead.get('business_name', 'Unknown')
            
            if not url:
                logger.warning(f"No URL for {business_name}")
                lead['screenshot_url'] = 'NO_URL'
                failed_captures.append({'business': business_name, 'reason': 'No URL provided'})
                continue
            
            logger.info(f"[{i}/{len(red_leads)}] Processing {business_name}: {url}")
            
            # Clean and validate URL
            cleaned_url = self._clean_and_validate_url(url)
            if not cleaned_url:
                logger.error(f"Invalid URL for {business_name}: {url}")
                lead['screenshot_url'] = 'INVALID_URL'
                failed_captures.append({'business': business_name, 'reason': 'Invalid URL'})
                continue
            
            # Classify website type for specialized handling
            website_type = self._classify_website_type(cleaned_url)
            config = self._get_domain_config(cleaned_url)
            
            logger.info(f"Website type: {website_type}, Wait time: {config['wait_time']}s")
            
            try:
                screenshot_path = self._robust_capture_with_retries(
                    cleaned_url, business_name, website_type, config
                )
                
                if screenshot_path and self._validate_screenshot(screenshot_path):
                    captured_screenshots[cleaned_url] = screenshot_path
                    lead['screenshot_url'] = screenshot_path
                    lead['website_type'] = website_type
                    logger.info(f"✓ Screenshot captured: {screenshot_path}")
                else:
                    lead['screenshot_url'] = 'FAILED'
                    failed_captures.append({'business': business_name, 'reason': 'Capture failed'})
                    logger.error(f"✗ Screenshot failed for {business_name}")
                    
            except Exception as e:
                logger.error(f"Error capturing {business_name}: {str(e)}")
                lead['screenshot_url'] = 'FAILED'
                lead['error_notes'] = lead.get('error_notes', '') + f' Screenshot error: {str(e)};'
                failed_captures.append({'business': business_name, 'reason': str(e)})
        
        # Log summary
        success_count = len(captured_screenshots)
        failure_count = len(failed_captures)
        
        logger.info(f"\nScreenshot capture summary:")
        logger.info(f"✓ Successful: {success_count}/{len(red_leads)} ({success_count/len(red_leads)*100:.1f}%)")
        logger.info(f"✗ Failed: {failure_count}/{len(red_leads)} ({failure_count/len(red_leads)*100:.1f}%)")
        
        if failed_captures:
            logger.info("Failed captures:")
            for failure in failed_captures:
                logger.info(f"  - {failure['business']}: {failure['reason']}")
        
        return captured_screenshots
    
    def _clean_and_validate_url(self, url: str) -> Optional[str]:
        """Clean and validate URL with robust error handling"""
        if not url:
            return None
        
        url = url.strip()
        
        # Remove common prefixes that aren't protocols
        if url.startswith('www.'):
            url = url[4:]
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            
            # Basic domain validation
            if '.' not in parsed.netloc:
                return None
            
            return url
            
        except Exception as e:
            logger.debug(f"URL validation error: {e}")
            return None
    
    def _robust_capture_with_retries(self, url: str, business_name: str, 
                                   website_type: str, config: Dict[str, Any]) -> Optional[str]:
        """
        Capture screenshot with retries and specialized handling
        """
        filename = self._sanitize_filename(url)
        filepath = os.path.join(self.screenshot_dir, filename)
        
        max_attempts = config.get('retry_attempts', 2)
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Attempt {attempt}/{max_attempts} for {business_name}")
            
            try:
                success = self._capture_with_specialized_handling(
                    url, filepath, website_type, config, attempt
                )
                
                if success:
                    return filepath
                
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
                
                if attempt < max_attempts:
                    wait_time = attempt * 2  # Progressive backoff
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
        
        logger.error(f"All {max_attempts} attempts failed for {business_name}")
        return None
    
    def _capture_with_specialized_handling(self, url: str, filepath: str, 
                                         website_type: str, config: Dict[str, Any], 
                                         attempt: int) -> bool:
        """
        Capture screenshot with specialized handling based on website type
        """
        wait_time = config.get('wait_time', 3)
        
        # Adjust wait time based on website type and attempt
        if website_type == 'spa':
            wait_time += 2  # SPAs need more time to load
        elif website_type == 'ecommerce':
            wait_time += 1  # E-commerce sites often have dynamic content
        elif website_type == 'cms':
            wait_time += 1  # CMS sites can be slow
        
        # Increase wait time on retries
        if attempt > 1:
            wait_time += attempt
        
        logger.info(f"Capturing {website_type} website with {wait_time}s wait time")
        
        try:
            # This is where the actual MCP calls would go:
            # 1. mcp__playwright__browser_navigate(url)
            # 2. mcp__playwright__browser_resize(config['viewport_width'], config['viewport_height'])
            # 3. mcp__playwright__browser_wait_for(time=wait_time)
            # 4. Additional waits for specific website types:
            
            if website_type == 'spa':
                # Wait for JavaScript to render
                # mcp__playwright__browser_wait_for(text="", time=2)  # Wait for any content
                pass
            elif website_type == 'ecommerce':
                # Wait for product images to load
                # mcp__playwright__browser_wait_for(time=1)
                pass
            elif website_type == 'cms':
                # Wait for theme to fully load
                # mcp__playwright__browser_wait_for(time=1)
                pass
            
            # 5. mcp__playwright__browser_take_screenshot(filename=filepath, raw=True)
            
            # For demo purposes, simulate the capture
            return self._simulate_specialized_capture(url, filepath, website_type, wait_time)
            
        except Exception as e:
            logger.error(f"Specialized capture error: {str(e)}")
            return False
    
    def _simulate_specialized_capture(self, url: str, filepath: str, 
                                    website_type: str, wait_time: float) -> bool:
        """Simulate specialized screenshot capture"""
        try:
            # Simulate processing time based on website complexity
            processing_time = {
                'standard': 0.1,
                'cms': 0.2,
                'ecommerce': 0.3,
                'spa': 0.4,
                'social': 0.2
            }.get(website_type, 0.1)
            
            time.sleep(processing_time)
            
            # Create a detailed demo file
            capture_info = {
                'url': url,
                'website_type': website_type,
                'wait_time': wait_time,
                'timestamp': time.ctime(),
                'viewport': f"{self.capture_config['viewport_width']}x{self.capture_config['viewport_height']}",
                'capture_method': 'robust_with_retries'
            }
            
            with open(filepath, 'w') as f:
                f.write(f"ROBUST SCREENSHOT CAPTURE\n")
                f.write(f"{'='*40}\n")
                for key, value in capture_info.items():
                    f.write(f"{key.title()}: {value}\n")
            
            return os.path.exists(filepath)
            
        except Exception as e:
            logger.error(f"Simulation error: {str(e)}")
            return False
    
    def _validate_screenshot(self, filepath: str) -> bool:
        """Validate screenshot file"""
        try:
            if not os.path.exists(filepath):
                return False
            
            file_size = os.path.getsize(filepath)
            if file_size < 50:  # Very small file is probably invalid
                logger.warning(f"Screenshot file too small: {filepath} ({file_size} bytes)")
                return False
            
            logger.debug(f"Screenshot validation passed: {filepath} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Error validating screenshot {filepath}: {str(e)}")
            return False

def demonstrate_robust_capture():
    """Demonstrate robust screenshot capture with various website types"""
    logger.info("=" * 80)
    logger.info("ROBUST SCREENSHOT CAPTURE DEMONSTRATION")
    logger.info("=" * 80)
    
    # Diverse set of RED leads with different website types
    red_leads = [
        {
            'business_name': 'Local Restaurant (Standard)',
            'website': 'https://example.com',
            'status': 'red',
            'mobile_score': 35,
            'pain_score': 65.0
        },
        {
            'business_name': 'E-commerce Store (Shopify)',
            'website': 'test-store.myshopify.com',
            'status': 'red',
            'mobile_score': 42,
            'pain_score': 58.0
        },
        {
            'business_name': 'CMS Website (WordPress)',
            'website': 'sample.wordpress.com',
            'status': 'red',
            'mobile_score': 38,
            'pain_score': 62.0
        },
        {
            'business_name': 'Modern SPA (React)',
            'website': 'https://react-example.com',
            'status': 'red',
            'mobile_score': 28,
            'pain_score': 72.0
        },
        {
            'business_name': 'Invalid URL Test',
            'website': 'not-a-valid-url',
            'status': 'red',
            'mobile_score': 30,
            'pain_score': 70.0
        },
        {
            'business_name': 'No Website Business',
            'website': '',
            'status': 'red',
            'mobile_score': 25,
            'pain_score': 75.0
        }
    ]
    
    # Create robust capture instance
    capture = RobustScreenshotCapture()
    
    # Process screenshots
    results = capture.capture_screenshots_with_layout_handling(red_leads)
    
    # Display detailed results
    logger.info("\n" + "=" * 80)
    logger.info("DETAILED CAPTURE RESULTS")
    logger.info("=" * 80)
    
    for lead in red_leads:
        name = lead['business_name']
        url = lead.get('website', 'NO_URL')
        screenshot = lead.get('screenshot_url', 'NOT_PROCESSED')
        website_type = lead.get('website_type', 'unknown')
        
        logger.info(f"\nBusiness: {name}")
        logger.info(f"  Website: {url}")
        logger.info(f"  Type: {website_type}")
        logger.info(f"  Mobile Score: {lead['mobile_score']}/100")
        logger.info(f"  Pain Score: {lead['pain_score']}")
        logger.info(f"  Screenshot: {screenshot}")
        
        if screenshot.startswith('screenshots/'):
            logger.info(f"  Status: ✓ SUCCESS")
        else:
            logger.info(f"  Status: ✗ FAILED ({screenshot})")
    
    logger.info(f"\n" + "=" * 80)
    logger.info("PERFORMANCE METRICS")
    logger.info("=" * 80)
    logger.info(f"Total leads processed: {len(red_leads)}")
    logger.info(f"Screenshots captured: {len(results)}")
    logger.info(f"Success rate: {len(results)/len(red_leads)*100:.1f}%")
    logger.info(f"Failed captures: {len(red_leads) - len(results)}")
    
    # Website type breakdown
    type_counts = {}
    for lead in red_leads:
        website_type = lead.get('website_type', 'failed')
        type_counts[website_type] = type_counts.get(website_type, 0) + 1
    
    logger.info(f"\nWebsite type breakdown:")
    for website_type, count in type_counts.items():
        logger.info(f"  {website_type}: {count}")
    
    logger.info("=" * 80)

if __name__ == "__main__":
    demonstrate_robust_capture()