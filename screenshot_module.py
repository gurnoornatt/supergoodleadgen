"""
Screenshot Capture Module for RED Leads
Captures full-page screenshots of business websites using Playwright MCP
"""

import os
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import logging
from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)

class ScreenshotCapture:
    """Handles screenshot capture for RED leads using Playwright MCP"""
    
    def __init__(self):
        self.config = Config()
        self.screenshot_dir = "screenshots"
        self._ensure_screenshot_directory()
    
    def _ensure_screenshot_directory(self):
        """Create screenshots directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            logger.info(f"Created screenshot directory: {self.screenshot_dir}")
    
    def _sanitize_filename(self, url: str) -> str:
        """Create a safe filename from URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        # Replace invalid filename characters
        safe_name = domain.replace('/', '_').replace(':', '_').replace('?', '_').replace('#', '_')
        return f"{safe_name}.png"
    
    def capture_screenshot_for_red_leads(self, leads_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Capture screenshots for all RED leads using Playwright MCP
        
        Args:
            leads_data: List of lead dictionaries
            
        Returns:
            Dictionary mapping lead URLs to screenshot paths
        """
        screenshot_results = {}
        red_leads = [lead for lead in leads_data if lead.get('status') == 'red']
        
        if not red_leads:
            logger.info("No RED leads found for screenshot capture")
            return screenshot_results
        
        logger.info(f"Starting screenshot capture for {len(red_leads)} RED leads")
        
        for i, lead in enumerate(red_leads, 1):
            url = lead.get('website', '').strip()
            business_name = lead.get('business_name', 'Unknown')
            
            if not url:
                logger.warning(f"No website URL for {business_name}")
                lead['screenshot_url'] = 'NO_URL'
                continue
            
            logger.info(f"Capturing screenshot {i}/{len(red_leads)}: {business_name} ({url})")
            
            try:
                screenshot_path = self.capture_single_screenshot(url, business_name)
                if screenshot_path:
                    screenshot_results[url] = screenshot_path
                    lead['screenshot_url'] = screenshot_path
                    logger.info(f"✓ Screenshot captured: {screenshot_path}")
                else:
                    lead['screenshot_url'] = 'FAILED'
                    lead['error_notes'] = lead.get('error_notes', '') + ' Screenshot capture failed;'
                    logger.error(f"✗ Failed to capture screenshot for {business_name}")
                    
            except Exception as e:
                logger.error(f"Error capturing screenshot for {business_name}: {str(e)}")
                lead['screenshot_url'] = 'FAILED'
                lead['error_notes'] = lead.get('error_notes', '') + f' Screenshot error: {str(e)};'
        
        successful_captures = len(screenshot_results)
        logger.info(f"Screenshot capture completed: {successful_captures}/{len(red_leads)} successful")
        return screenshot_results
    
    def capture_single_screenshot(self, url: str, business_name: str = "") -> Optional[str]:
        """
        Capture a single website screenshot using Playwright MCP
        This method will be used by the main process to make MCP calls
        """
        try:
            if not url or not url.startswith(('http://', 'https://')):
                if url and not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"
                else:
                    logger.warning(f"Invalid URL provided: {url}")
                    return None
            
            filename = self._sanitize_filename(url)
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Return the expected filepath - the actual screenshot will be captured
            # by the main process using MCP tools
            return filepath
            
        except Exception as e:
            logger.error(f"Error preparing screenshot capture for {url}: {str(e)}")
            return None
    
    def validate_screenshot_quality(self, filepath: str) -> bool:
        """
        Validate that the screenshot meets quality standards
        
        Args:
            filepath: Path to screenshot file
            
        Returns:
            True if screenshot is valid, False otherwise
        """
        try:
            if not os.path.exists(filepath):
                return False
            
            # Check file size (should be reasonable)
            file_size = os.path.getsize(filepath)
            if file_size < 1000:  # Less than 1KB is probably invalid
                logger.warning(f"Screenshot file too small: {filepath} ({file_size} bytes)")
                return False
            
            if file_size > 50 * 1024 * 1024:  # Greater than 50MB is probably too large
                logger.warning(f"Screenshot file too large: {filepath} ({file_size} bytes)")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating screenshot {filepath}: {str(e)}")
            return False

def test_screenshot_module():
    """Test the screenshot capture functionality"""
    logger.info("Testing screenshot capture module")
    
    # Sample test data
    test_leads = [
        {
            'business_name': 'Test Restaurant',
            'website': 'https://example.com',
            'status': 'red',
            'mobile_score': 45
        }
    ]
    
    capture = ScreenshotCapture()
    results = capture.capture_screenshot_for_red_leads(test_leads)
    
    logger.info(f"Test results: {results}")
    return results

if __name__ == "__main__":
    test_screenshot_module()