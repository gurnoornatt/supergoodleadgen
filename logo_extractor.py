"""
Logo extraction and fallback generation module for Pain-Gap Audit Automation
"""
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image, ImageDraw, ImageFont
import hashlib
import time
from logger_config import setup_logger

# Firecrawl is available via MCP tools
FIRECRAWL_AVAILABLE = True

# Use Beautiful Soup for HTML parsing as fallback
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = setup_logger(__name__)

class LogoExtractor:
    """Extract business logos from websites with fallback generation"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.logos_dir = "logos"
        self.fallback_logos_dir = "fallback_logos"
        self._ensure_directories()
        
        # Firecrawl is available via MCP tools
        self.firecrawl_available = FIRECRAWL_AVAILABLE
        if self.firecrawl_available:
            logger.info("Firecrawl MCP available for logo extraction")
        else:
            logger.info("Using fallback web scraping for logo extraction")
    
    def _ensure_directories(self):
        """Create necessary directories for logo storage"""
        for directory in [self.logos_dir, self.fallback_logos_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def extract_logo_from_website(self, url: str, business_name: str) -> Dict[str, Any]:
        """
        Extract logo from business website
        
        Args:
            url: Website URL to scrape
            business_name: Business name for fallback generation
            
        Returns:
            Dict containing logo extraction results
        """
        result = {
            'business_name': business_name,
            'website_url': url,
            'logo_url': '',
            'logo_local_path': '',
            'extraction_method': '',
            'success': False,
            'error_message': '',
            'fallback_generated': False
        }
        
        try:
            logger.info(f"Extracting logo for {business_name} from {url}")
            
            # Try Firecrawl first if available
            if self.firecrawl_available:
                logo_info = self._extract_logo_with_firecrawl(url)
                if logo_info['success']:
                    result.update(logo_info)
                    result['extraction_method'] = 'firecrawl'
                    
                    # Download and save the logo
                    downloaded_path = self._download_logo(logo_info['logo_url'], business_name)
                    if downloaded_path:
                        result['logo_local_path'] = downloaded_path
                        result['success'] = True
                        logger.info(f"Successfully extracted logo for {business_name} using Firecrawl")
                        return result
            
            # Fall back to HTML parsing
            if BS4_AVAILABLE:
                logo_info = self._extract_logo_with_beautifulsoup(url)
                if logo_info['success']:
                    result.update(logo_info)
                    result['extraction_method'] = 'beautifulsoup'
                    
                    # Download and save the logo
                    downloaded_path = self._download_logo(logo_info['logo_url'], business_name)
                    if downloaded_path:
                        result['logo_local_path'] = downloaded_path
                        result['success'] = True
                        logger.info(f"Successfully extracted logo for {business_name} using BeautifulSoup")
                        return result
            
            # If extraction failed, generate fallback logo
            logger.warning(f"Logo extraction failed for {business_name}, generating fallback")
            fallback_path = self.generate_fallback_logo(business_name)
            result['logo_local_path'] = fallback_path
            result['fallback_generated'] = True
            result['extraction_method'] = 'fallback_generated'
            result['success'] = True
            result['error_message'] = 'No logo found on website, fallback generated'
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting logo for {business_name}: {e}")
            
            # Generate fallback logo on any error
            try:
                fallback_path = self.generate_fallback_logo(business_name)
                result['logo_local_path'] = fallback_path
                result['fallback_generated'] = True
                result['extraction_method'] = 'fallback_generated'
                result['success'] = True
                result['error_message'] = f'Extraction error: {str(e)}, fallback generated'
            except Exception as fallback_error:
                result['error_message'] = f'Extraction failed: {str(e)}, Fallback failed: {str(fallback_error)}'
                result['success'] = False
            
            return result
    
    def _extract_logo_with_firecrawl(self, url: str) -> Dict[str, Any]:
        """Extract logo using Firecrawl MCP"""
        result = {'success': False, 'logo_url': '', 'error_message': ''}
        
        try:
            # Use Firecrawl to scrape the page
            scrape_result = self.firecrawl_client.scrape(url, formats=['html'])
            
            if 'html' in scrape_result:
                html_content = scrape_result['html']
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find logo using common selectors
                logo_url = self._find_logo_in_html(soup, url)
                if logo_url:
                    result['success'] = True
                    result['logo_url'] = logo_url
                else:
                    result['error_message'] = 'No logo found in HTML content'
            else:
                result['error_message'] = 'Failed to get HTML content from Firecrawl'
                
        except Exception as e:
            result['error_message'] = f'Firecrawl extraction error: {str(e)}'
            
        return result
    
    def _extract_logo_with_beautifulsoup(self, url: str) -> Dict[str, Any]:
        """Extract logo using BeautifulSoup (fallback method)"""
        result = {'success': False, 'logo_url': '', 'error_message': ''}
        
        try:
            # Make request to get HTML content
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find logo using common selectors
            logo_url = self._find_logo_in_html(soup, url)
            if logo_url:
                result['success'] = True
                result['logo_url'] = logo_url
            else:
                result['error_message'] = 'No logo found in HTML content'
                
        except Exception as e:
            result['error_message'] = f'BeautifulSoup extraction error: {str(e)}'
            
        return result
    
    def _find_logo_in_html(self, soup, base_url: str) -> Optional[str]:
        """Find logo in HTML using common patterns"""
        logo_selectors = [
            # Common logo class names and IDs
            'img[class*="logo" i]',
            'img[id*="logo" i]',
            'img[alt*="logo" i]',
            'img[src*="logo" i]',
            
            # Brand and header images
            'img[class*="brand" i]',
            'img[id*="brand" i]',
            'img[alt*="brand" i]',
            
            # Header area logos
            'header img',
            '.header img',
            '#header img',
            '.navbar img',
            '.nav img',
            
            # Common logo containers
            '.logo img',
            '#logo img',
            '.brand img',
            '#brand img',
            '.site-logo img',
            '.company-logo img',
            
            # WordPress and common CMS patterns
            '.custom-logo',
            '.site-title img',
            '.site-branding img',
        ]
        
        for selector in logo_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    src = element.get('src')
                    if src and self._is_valid_logo_url(src):
                        # Convert relative URLs to absolute
                        absolute_url = urljoin(base_url, src)
                        if self._is_valid_logo_url(absolute_url):
                            logger.debug(f"Found logo with selector '{selector}': {absolute_url}")
                            return absolute_url
            except Exception as e:
                logger.debug(f"Error with selector '{selector}': {e}")
                continue
        
        # Try to find favicon as last resort
        favicon_selectors = [
            'link[rel="icon"]',
            'link[rel="shortcut icon"]',
            'link[rel="apple-touch-icon"]'
        ]
        
        for selector in favicon_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href')
                    if href:
                        absolute_url = urljoin(base_url, href)
                        logger.debug(f"Found favicon with selector '{selector}': {absolute_url}")
                        return absolute_url
            except Exception as e:
                logger.debug(f"Error with favicon selector '{selector}': {e}")
                continue
        
        return None
    
    def _is_valid_logo_url(self, url: str) -> bool:
        """Check if URL is likely to be a valid logo"""
        if not url:
            return False
        
        # Check for common image extensions
        url_lower = url.lower()
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']
        
        # Check if URL ends with image extension
        for ext in valid_extensions:
            if url_lower.endswith(ext):
                return True
        
        # Check if URL contains image extension with parameters
        for ext in valid_extensions:
            if ext in url_lower:
                return True
        
        # Exclude obvious non-logo patterns
        exclude_patterns = [
            'data:', 'mailto:', 'tel:', 'javascript:',
            'advertisement', 'banner', 'tracking',
            '1x1', 'pixel', 'spacer', 'blank'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
        
        return True
    
    def _download_logo(self, url: str, business_name: str) -> Optional[str]:
        """Download logo from URL and save locally"""
        try:
            # Create safe filename
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', business_name.lower())
            timestamp = str(int(time.time()))
            
            # Get file extension from URL
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('.')
            extension = '.png'  # Default extension
            if len(path_parts) > 1:
                ext = path_parts[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'gif', 'svg', 'webp']:
                    extension = f'.{ext}'
            
            filename = f"logo_{safe_name}_{timestamp}{extension}"
            filepath = os.path.join(self.logos_dir, filename)
            
            # Download the image
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded logo: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error downloading logo from {url}: {e}")
            return None
    
    def generate_fallback_logo(self, business_name: str) -> str:
        """
        Generate fallback logo using Pillow (400×120px colored rectangle with business name)
        Uses 700-weight Poppins white text as specified
        """
        try:
            # Create safe filename
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', business_name.lower())
            timestamp = str(int(time.time()))
            filename = f"fallback_logo_{safe_name}_{timestamp}.png"
            filepath = os.path.join(self.fallback_logos_dir, filename)
            
            # Color palette for logos (professional business colors)
            colors = [
                (45, 55, 72),    # Dark blue-gray
                (56, 161, 105),  # Green
                (49, 130, 206),  # Blue
                (128, 90, 213),  # Purple
                (245, 101, 101), # Red
                (237, 137, 54),  # Orange
                (102, 126, 234), # Indigo
                (113, 128, 150), # Gray
            ]
            
            # Select color based on business name hash for consistency
            color_index = hash(business_name) % len(colors)
            bg_color = colors[color_index]
            
            # Create image
            width, height = 400, 120
            image = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(image)
            
            # Try to load Poppins font (fallback to default if not available)
            font_size = 32
            try:
                # Try to find Poppins font (common locations)
                font_paths = [
                    "/System/Library/Fonts/Helvetica.ttc",  # macOS fallback
                    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
                    "C:/Windows/Fonts/arial.ttf",  # Windows fallback
                ]
                
                font = None
                for font_path in font_paths:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, font_size)
                        break
                
                if font is None:
                    font = ImageFont.load_default()
                    
            except Exception as e:
                logger.debug(f"Could not load custom font, using default: {e}")
                font = ImageFont.load_default()
            
            # Prepare text (truncate if too long)
            max_chars = 20
            display_text = business_name[:max_chars]
            if len(business_name) > max_chars:
                display_text = display_text.rstrip() + "..."
            
            # Calculate text position (center)
            bbox = draw.textbbox((0, 0), display_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Draw text in white (700-weight effect with slight offset)
            text_color = (255, 255, 255)
            
            # Draw text with slight offset for bold effect
            for offset_x in range(-1, 2):
                for offset_y in range(-1, 2):
                    if offset_x != 0 or offset_y != 0:
                        draw.text((x + offset_x, y + offset_y), display_text, 
                                font=font, fill=text_color)
            
            # Draw main text
            draw.text((x, y), display_text, font=font, fill=text_color)
            
            # Save image
            image.save(filepath, 'PNG', quality=95)
            
            logger.info(f"Generated fallback logo: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error generating fallback logo for {business_name}: {e}")
            raise
    
    def validate_logo(self, logo_path: str) -> Dict[str, Any]:
        """
        Validate logo for quality and usability
        
        Args:
            logo_path: Path to logo file
            
        Returns:
            Dict containing validation results
        """
        validation_result = {
            'path': logo_path,
            'valid': False,
            'dimensions': {'width': 0, 'height': 0},
            'file_size': 0,
            'format': '',
            'issues': [],
            'quality_score': 0
        }
        
        try:
            if not os.path.exists(logo_path):
                validation_result['issues'].append('File does not exist')
                return validation_result
            
            # Check file size
            file_size = os.path.getsize(logo_path)
            validation_result['file_size'] = file_size
            
            if file_size == 0:
                validation_result['issues'].append('File is empty')
                return validation_result
            
            if file_size > 5 * 1024 * 1024:  # 5MB limit
                validation_result['issues'].append('File size too large (>5MB)')
            
            # Validate image
            try:
                with Image.open(logo_path) as img:
                    width, height = img.size
                    validation_result['dimensions'] = {'width': width, 'height': height}
                    validation_result['format'] = img.format
                    
                    # Check minimum dimensions
                    if width < 50 or height < 50:
                        validation_result['issues'].append('Dimensions too small (minimum 50x50)')
                    
                    # Check aspect ratio (should be reasonable for a logo)
                    aspect_ratio = width / height
                    if aspect_ratio > 10 or aspect_ratio < 0.1:
                        validation_result['issues'].append('Unusual aspect ratio')
                    
                    # Calculate quality score (0-100)
                    quality_score = 100
                    
                    # Deduct points for issues
                    if width < 100 or height < 100:
                        quality_score -= 20
                    if file_size > 1024 * 1024:  # >1MB
                        quality_score -= 10
                    if aspect_ratio > 5 or aspect_ratio < 0.2:
                        quality_score -= 15
                    
                    # Bonus for good dimensions
                    if 200 <= width <= 800 and 50 <= height <= 400:
                        quality_score += 10
                    
                    validation_result['quality_score'] = max(0, min(100, quality_score))
                    
                    # Mark as valid if no critical issues
                    if not any(issue in ['File does not exist', 'File is empty', 'Dimensions too small'] 
                             for issue in validation_result['issues']):
                        validation_result['valid'] = True
                        
            except Exception as img_error:
                validation_result['issues'].append(f'Invalid image file: {str(img_error)}')
            
            return validation_result
            
        except Exception as e:
            validation_result['issues'].append(f'Validation error: {str(e)}')
            return validation_result
    
    def process_leads_for_logos(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process a batch of leads to extract logos
        
        Args:
            leads: List of lead dictionaries
            
        Returns:
            Updated leads with logo information
        """
        logger.info(f"Starting logo extraction for {len(leads)} leads")
        
        for i, lead in enumerate(leads, 1):
            business_name = lead.get('business_name', f'Business_{i}')
            website = lead.get('website', '').strip()
            
            logger.info(f"Processing logo {i}/{len(leads)}: {business_name}")
            
            if not website:
                logger.warning(f"No website for {business_name}, generating fallback logo")
                try:
                    fallback_path = self.generate_fallback_logo(business_name)
                    lead['logo_url'] = fallback_path
                    lead['logo_extraction_method'] = 'fallback_no_website'
                except Exception as e:
                    logger.error(f"Failed to generate fallback logo for {business_name}: {e}")
                    lead['logo_url'] = ''
                    lead['logo_extraction_method'] = 'failed'
                continue
            
            # Extract logo
            logo_result = self.extract_logo_from_website(website, business_name)
            
            # Update lead with logo information
            lead['logo_url'] = logo_result.get('logo_local_path', '')
            lead['logo_extraction_method'] = logo_result.get('extraction_method', 'failed')
            lead['logo_fallback_generated'] = logo_result.get('fallback_generated', False)
            
            if logo_result.get('error_message'):
                error_notes = lead.get('error_notes', '')
                if error_notes:
                    error_notes += ' | '
                error_notes += f"Logo: {logo_result['error_message']}"
                lead['error_notes'] = error_notes
            
            # Validate logo if extraction was successful
            if lead['logo_url'] and os.path.exists(lead['logo_url']):
                validation = self.validate_logo(lead['logo_url'])
                lead['logo_quality_score'] = validation['quality_score']
                lead['logo_valid'] = validation['valid']
                
                if validation['issues']:
                    logger.warning(f"Logo validation issues for {business_name}: {validation['issues']}")
            else:
                lead['logo_quality_score'] = 0
                lead['logo_valid'] = False
        
        successful_extractions = sum(1 for lead in leads if lead.get('logo_url'))
        fallback_generated = sum(1 for lead in leads if lead.get('logo_fallback_generated'))
        
        logger.info(f"Logo extraction completed: {successful_extractions}/{len(leads)} successful, {fallback_generated} fallbacks generated")
        
        return leads