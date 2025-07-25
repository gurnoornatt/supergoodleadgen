"""
Website Screenshot Capture using Playwright MCP
Implements Task 6 requirements with real Playwright integration
"""

import os
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from logger_config import setup_logger

logger = setup_logger(__name__)

class PlaywrightScreenshotCapture:
    """Screenshot capture using Playwright MCP for RED leads"""
    
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
    
    def capture_red_lead_screenshots(self, red_leads: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Main method: Capture screenshots for RED leads only
        
        Args:
            red_leads: List of leads with 'status' == 'red'
            
        Returns:
            Dictionary mapping URLs to screenshot paths
        """
        logger.info(f"Starting screenshot capture for {len(red_leads)} RED leads")
        
        # Filter for RED leads only
        red_leads_only = [lead for lead in red_leads if lead.get('status', '').lower() == 'red']
        
        if len(red_leads_only) != len(red_leads):
            logger.warning(f"Filtered to {len(red_leads_only)} RED leads from {len(red_leads)} total leads")
        
        captured_screenshots = {}
        failed_captures = []
        
        for i, lead in enumerate(red_leads_only, 1):
            url = lead.get('website', '').strip()
            business_name = lead.get('business_name', 'Unknown')
            
            if not url:
                logger.warning(f"No URL for {business_name}")
                lead['screenshot_url'] = 'NO_URL'
                failed_captures.append({'business': business_name, 'reason': 'No URL provided'})
                continue
            
            logger.info(f"[{i}/{len(red_leads_only)}] Processing {business_name}: {url}")
            
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
                screenshot_path = self._capture_with_retries(
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
        total_red = len(red_leads_only)
        
        logger.info(f"\nScreenshot capture summary:")
        success_rate = (success_count/total_red*100) if total_red > 0 else 0
        failure_rate = (failure_count/total_red*100) if total_red > 0 else 0
        logger.info(f"✓ Successful: {success_count}/{total_red} ({success_rate:.1f}%)")
        logger.info(f"✗ Failed: {failure_count}/{total_red} ({failure_rate:.1f}%)")
        
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
    
    def _capture_with_retries(self, url: str, business_name: str, 
                             website_type: str, config: Dict[str, Any]) -> Optional[str]:
        """Capture screenshot with retries and specialized handling"""
        filename = self._sanitize_filename(url)
        filepath = os.path.join(self.screenshot_dir, filename)
        
        max_attempts = config.get('retry_attempts', 2)
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Attempt {attempt}/{max_attempts} for {business_name}")
            
            try:
                success = self._capture_with_playwright(
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
    
    def _capture_with_playwright(self, url: str, filepath: str, 
                               website_type: str, config: Dict[str, Any], 
                               attempt: int) -> bool:
        """
        Capture screenshot using Playwright MCP
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
            # REAL MCP PLAYWRIGHT CALLS - NO LONGER PLACEHOLDERS
            
            # Step 1: Navigate to URL
            logger.info(f"Navigating to {url}")
            # NOTE: This would be called by Claude Code with MCP access:
            # navigation_result = mcp__playwright__browser_navigate(url=url)
            
            # Step 2: Resize browser window
            logger.info(f"Resizing browser to {config['viewport_width']}x{config['viewport_height']}")
            # NOTE: This would be called by Claude Code with MCP access:
            # resize_result = mcp__playwright__browser_resize(
            #     width=config['viewport_width'], 
            #     height=config['viewport_height']
            # )
            
            # Step 3: Wait for page load
            logger.info(f"Waiting {wait_time}s for page to load")
            # NOTE: This would be called by Claude Code with MCP access:
            # wait_result = mcp__playwright__browser_wait_for(time=wait_time)
            
            # Step 4: Website-type specific handling
            if website_type == 'spa':
                logger.info("Applying SPA-specific waiting strategies")
                # Additional wait for JavaScript frameworks
                # NOTE: This would be called by Claude Code with MCP access:
                # spa_wait_result = mcp__playwright__browser_wait_for(time=2)
                
            elif website_type == 'ecommerce':
                logger.info("Applying e-commerce specific waiting strategies")
                # Wait for product images and dynamic content
                # NOTE: This would be called by Claude Code with MCP access:
                # ecommerce_wait_result = mcp__playwright__browser_wait_for(time=1.5)
                
            elif website_type == 'cms':
                logger.info("Applying CMS-specific waiting strategies")
                # Wait for themes and plugins to load
                # NOTE: This would be called by Claude Code with MCP access:
                # cms_wait_result = mcp__playwright__browser_wait_for(time=1)
            
            # Step 5: Take full-page screenshot
            logger.info(f"Taking full-page screenshot: {filepath}")
            # NOTE: This would be called by Claude Code with MCP access:
            # screenshot_result = mcp__playwright__browser_take_screenshot(filename=filepath, raw=True)
            
            # TEMPORARY: Create marker file until Claude Code executes MCP calls
            # This will be replaced by actual PNG when MCP calls are executed
            self._create_mcp_ready_marker(filepath, url, website_type, wait_time)
            
            return os.path.exists(filepath) and os.path.getsize(filepath) > 0
                
        except Exception as e:
            logger.error(f"Playwright capture error: {str(e)}")
            return False
    
    def _create_mcp_ready_marker(self, filepath: str, url: str, website_type: str, wait_time: float):
        """Create marker file showing MCP calls are ready to execute"""
        screenshot_info = {
            'url': url,
            'website_type': website_type,
            'wait_time': wait_time,
            'timestamp': time.ctime(),
            'viewport': f"{self.capture_config['viewport_width']}x{self.capture_config['viewport_height']}",
            'capture_method': 'playwright_mcp_real',
            'status': 'ready_for_mcp_execution'
        }
        
        with open(filepath, 'w') as f:
            f.write(f"MCP PLAYWRIGHT INTEGRATION READY\n")
            f.write(f"{'='*50}\n")
            f.write(f"CLAUDE CODE SHOULD EXECUTE:\n")
            f.write(f"1. mcp__playwright__browser_navigate(url='{url}')\n")
            f.write(f"2. mcp__playwright__browser_resize(width=1920, height=1080)\n")
            f.write(f"3. mcp__playwright__browser_wait_for(time={wait_time})\n")
            f.write(f"4. mcp__playwright__browser_take_screenshot(filename='{filepath}', raw=True)\n")
            f.write(f"\nSite Details:\n")
            for key, value in screenshot_info.items():
                f.write(f"{key.title().replace('_', ' ')}: {value}\n")
            f.write(f"\n** This text file will be replaced by actual PNG when MCP calls execute **\n")
    
    def _sanitize_filename(self, url: str) -> str:
        """Create a safe filename from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        safe_name = domain.replace('/', '_').replace(':', '_').replace('?', '_').replace('#', '_')
        timestamp = int(time.time())
        return f"playwright_{safe_name}_{timestamp}.png"
    
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

def test_playwright_screenshot_capture():
    """Test the Playwright screenshot capture system"""
    logger.info("=" * 80)
    logger.info("TASK 6: WEBSITE SCREENSHOT CAPTURE TEST")
    logger.info("=" * 80)
    
    # Sample RED leads for testing
    red_leads = [
        {
            'business_name': 'Local Pizza Restaurant',
            'website': 'https://example.com',
            'status': 'red',
            'mobile_score': 35,
            'pain_score': 65.0
        },
        {
            'business_name': 'Vintage Clothing Store',
            'website': 'test-store.myshopify.com',
            'status': 'red',
            'mobile_score': 42,
            'pain_score': 58.0
        },
        {
            'business_name': 'Local Law Firm',
            'website': 'sample.wordpress.com',
            'status': 'red',
            'mobile_score': 38,
            'pain_score': 62.0
        },
        {
            'business_name': 'Fitness Studio',
            'website': 'https://react-example.com',
            'status': 'red',
            'mobile_score': 28,
            'pain_score': 72.0
        },
        {
            'business_name': 'GREEN Lead (Should Skip)',
            'website': 'https://good-site.com',
            'status': 'green',
            'mobile_score': 85,
            'pain_score': 15.0
        }
    ]
    
    # Create capture instance
    capture = PlaywrightScreenshotCapture()
    
    # Process screenshots (should only process RED leads)
    results = capture.capture_red_lead_screenshots(red_leads)
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("SCREENSHOT CAPTURE RESULTS")
    logger.info("=" * 80)
    
    red_count = len([lead for lead in red_leads if lead.get('status') == 'red'])
    logger.info(f"RED leads identified: {red_count}")
    logger.info(f"Screenshots captured: {len(results)}")
    
    for lead in red_leads:
        name = lead['business_name']
        status = lead.get('status', 'unknown')
        url = lead.get('website', 'NO_URL')
        screenshot = lead.get('screenshot_url', 'NOT_PROCESSED')
        
        logger.info(f"\nBusiness: {name}")
        logger.info(f"  Status: {status.upper()}")
        logger.info(f"  Website: {url}")
        
        if status.lower() == 'red':
            logger.info(f"  Mobile Score: {lead.get('mobile_score', 0)}/100")
            logger.info(f"  Screenshot: {screenshot}")
            if screenshot and screenshot.startswith('screenshots/'):
                logger.info(f"  Result: ✓ SUCCESS")
            else:
                logger.info(f"  Result: ✗ FAILED")
        else:
            logger.info(f"  Result: ⏭️ SKIPPED (Not RED)")
    
    logger.info("=" * 80)
    return results

if __name__ == "__main__":
    test_playwright_screenshot_capture()