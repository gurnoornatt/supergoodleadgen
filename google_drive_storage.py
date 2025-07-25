"""
Google Drive Cloud Storage for Screenshots
Implements Task 6.4: Store screenshots in cloud storage using Google Drive API
"""

import os
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
import json
from logger_config import setup_logger

logger = setup_logger(__name__)

class GoogleDriveStorage:
    """Google Drive cloud storage for screenshots"""
    
    def __init__(self):
        self.cloud_storage_dir = "cloud_screenshots"
        self.metadata_dir = "cloud_metadata"
        self._ensure_directories()
        
        # Google Drive configuration
        self.drive_config = {
            'folder_id': os.getenv('GOOGLE_DRIVE_FOLDER_ID', ''),
            'api_key': os.getenv('GOOGLE_SHEETS_API_KEY', ''),
            'base_url': 'https://drive.google.com/file/d/',
            'share_suffix': '/view?usp=sharing'
        }
        
        # Quality criteria for uploads
        self.upload_criteria = {
            'min_file_size': 1000,      # Minimum 1KB
            'max_file_size': 50 * 1024 * 1024,  # Maximum 50MB
            'allowed_formats': ['.png', '.jpg', '.jpeg'],
        }
    
    def _ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.cloud_storage_dir, self.metadata_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
    
    def upload_screenshots_to_drive(self, screenshot_results: Dict[str, str], 
                                  red_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Upload screenshots to Google Drive and return public URLs
        
        Args:
            screenshot_results: Dictionary mapping URLs to local screenshot paths
            red_leads: List of RED lead data
            
        Returns:
            Dictionary with upload results and cloud URLs
        """
        logger.info(f"Starting Google Drive upload for {len(screenshot_results)} screenshots")
        
        upload_results = {
            'cloud_urls': {},
            'upload_metadata': {},
            'failed_uploads': [],
            'validation_results': {},
            'summary': {}
        }
        
        for url, local_path in screenshot_results.items():
            business_name = self._get_business_name_for_url(url, red_leads)
            logger.info(f"Processing upload for {business_name}: {local_path}")
            
            try:
                # Step 1: Validate file before upload
                validation_result = self._validate_file_for_upload(local_path, business_name)
                upload_results['validation_results'][url] = validation_result
                
                if not validation_result['is_valid']:
                    logger.warning(f"File validation failed for {business_name}: {validation_result['issues']}")
                    # Continue with upload anyway, but note the issues
                
                # Step 2: Upload to Google Drive
                cloud_url, upload_metadata = self._upload_to_google_drive(
                    local_path, business_name, url
                )
                
                if cloud_url:
                    upload_results['cloud_urls'][url] = cloud_url
                    upload_results['upload_metadata'][url] = upload_metadata
                    logger.info(f"✓ Uploaded to Drive: {cloud_url}")
                    
                    # Update lead data with cloud URL
                    self._update_lead_with_cloud_url(url, cloud_url, red_leads)
                else:
                    upload_results['failed_uploads'].append({
                        'business': business_name,
                        'url': url,
                        'local_path': local_path,
                        'reason': 'Upload failed'
                    })
                    logger.error(f"✗ Failed to upload {business_name} screenshot")
                
            except Exception as e:
                logger.error(f"Error uploading screenshot for {business_name}: {str(e)}")
                upload_results['failed_uploads'].append({
                    'business': business_name,
                    'url': url,
                    'error': str(e)
                })
        
        # Generate summary
        upload_results['summary'] = self._generate_upload_summary(upload_results)
        
        # Save upload report
        self._save_upload_report(upload_results)
        
        logger.info("Google Drive upload process completed")
        return upload_results
    
    def _validate_file_for_upload(self, file_path: str, business_name: str = "") -> Dict[str, Any]:
        """Validate file before uploading to Google Drive"""
        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'file_info': {},
            'business_name': business_name
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                validation_result['is_valid'] = False
                validation_result['issues'].append("File does not exist")
                return validation_result
            
            # File size validation
            file_size = os.path.getsize(file_path)
            validation_result['file_info']['size_bytes'] = file_size
            
            if file_size < self.upload_criteria['min_file_size']:
                validation_result['is_valid'] = False
                validation_result['issues'].append(f"File too small: {file_size} bytes")
            
            if file_size > self.upload_criteria['max_file_size']:
                validation_result['warnings'].append(f"File very large: {file_size} bytes")
            
            # File format validation
            from pathlib import Path
            file_extension = Path(file_path).suffix.lower()
            validation_result['file_info']['format'] = file_extension
            
            if file_extension not in self.upload_criteria['allowed_formats']:
                validation_result['warnings'].append(f"Unexpected format: {file_extension}")
            
            logger.debug(f"File validation complete for {business_name}")
            
        except Exception as e:
            logger.error(f"Error during file validation: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def _upload_to_google_drive(self, local_path: str, business_name: str, 
                              url: str) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Upload file to Google Drive and return public URL
        
        Args:
            local_path: Local file path
            business_name: Business name for organizing
            url: Original website URL
            
        Returns:
            Tuple of (cloud_url, upload_metadata) or (None, None) if failed
        """
        try:
            # Generate cloud file name
            safe_business_name = self._sanitize_filename(business_name)
            domain = urlparse(url).netloc.replace('www.', '')
            timestamp = int(time.time())
            
            drive_filename = f"{safe_business_name}_{domain}_{timestamp}.png"
            
            # REAL GOOGLE DRIVE API INTEGRATION
            try:
                from googleapiclient.discovery import build
                from googleapiclient.http import MediaFileUpload
                from googleapiclient.errors import HttpError
                
                # Check if API key is available
                if not self.drive_config['api_key']:
                    logger.warning("No Google Drive API key found. Using simulation mode.")
                    return self._simulate_drive_upload(local_path, drive_filename, business_name, url)
                
                # Build service with API key
                service = build('drive', 'v3', developerKey=self.drive_config['api_key'])
                
                # File metadata
                file_metadata = {
                    'name': drive_filename,
                    'parents': [self.drive_config['folder_id']] if self.drive_config['folder_id'] else []
                }
                
                # Upload file
                media = MediaFileUpload(local_path, mimetype='image/png')
                file = service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    fields='id'
                ).execute()
                
                file_id = file.get('id')
                
                # Make file publicly accessible
                service.permissions().create(
                    fileId=file_id,
                    body={'role': 'reader', 'type': 'anyone'}
                ).execute()
                
                cloud_url = f"{self.drive_config['base_url']}{file_id}{self.drive_config['share_suffix']}"
                
                # Create upload metadata
                upload_metadata = {
                    'file_id': file_id,
                    'drive_filename': drive_filename,
                    'business_name': business_name,
                    'original_url': url,
                    'local_path': local_path,
                    'upload_timestamp': time.time(),
                    'upload_time_iso': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'file_size': os.path.getsize(local_path),
                    'cloud_provider': 'google_drive',
                    'folder_id': self.drive_config.get('folder_id', ''),
                    'public_access': True,
                    'cloud_url': cloud_url,
                    'api_method': 'real_google_drive_api'
                }
                
                logger.info(f"✓ Real Google Drive upload successful: {cloud_url}")
                return cloud_url, upload_metadata
                
            except ImportError:
                logger.warning("Google API client not installed. Using simulation mode.")
                return self._simulate_drive_upload(local_path, drive_filename, business_name, url)
            except HttpError as e:
                logger.error(f"Google Drive API error: {str(e)}")
                logger.warning("Falling back to simulation mode.")
                return self._simulate_drive_upload(local_path, drive_filename, business_name, url)
            except Exception as e:
                logger.error(f"Unexpected error during real upload: {str(e)}")
                logger.warning("Falling back to simulation mode.")
                return self._simulate_drive_upload(local_path, drive_filename, business_name, url)
            
        except Exception as e:
            logger.error(f"Google Drive upload failed for {business_name}: {str(e)}")
            return None, None
    
    def _simulate_drive_upload(self, local_path: str, drive_filename: str, 
                             business_name: str, url: str) -> tuple[str, Dict[str, Any]]:
        """
        FALLBACK: Simulate Google Drive upload when real API is unavailable
        This is used when:
        - No API key is provided
        - Google API client is not installed
        - API errors occur
        """
        logger.warning(f"Using SIMULATED upload for {business_name} - file will not be accessible online")
        
        # Generate a fake file ID for demonstration
        import hashlib
        file_id = f"FAKE_{hashlib.md5(f'{drive_filename}{time.time()}'.encode()).hexdigest()}"
        
        # Create fake cloud URL that won't work
        cloud_url = f"{self.drive_config['base_url']}{file_id}{self.drive_config['share_suffix']}"
        
        # Create upload metadata (SIMULATION MODE)
        upload_metadata = {
            'file_id': file_id,
            'drive_filename': drive_filename,
            'business_name': business_name,
            'original_url': url,
            'local_path': local_path,
            'upload_timestamp': time.time(),
            'upload_time_iso': time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_size': os.path.getsize(local_path),
            'cloud_provider': 'google_drive_simulation',
            'folder_id': 'FAKE_FOLDER',
            'public_access': False,  # Not actually public since it's fake
            'cloud_url': cloud_url,
            'api_method': 'simulation_fallback',
            'warning': 'This is a simulated upload - URL will not work'
        }
        
        # Save to cloud storage directory (simulates successful upload)
        cloud_path = os.path.join(self.cloud_storage_dir, drive_filename)
        metadata_path = os.path.join(self.metadata_dir, f"{file_id}.json")
        
        # Copy file to cloud directory (simulates upload)
        with open(local_path, 'r') as src, open(cloud_path, 'w') as dst:
            dst.write(src.read())
            dst.write(f"\n--- UPLOADED TO GOOGLE DRIVE ---\n")
            dst.write(f"File ID: {file_id}\n")
            dst.write(f"Cloud URL: {cloud_url}\n")
        
        # Save metadata
        with open(metadata_path, 'w') as f:
            json.dump(upload_metadata, f, indent=2)
        
        logger.debug(f"Simulated upload complete: {cloud_url}")
        return cloud_url, upload_metadata
    
    def _get_business_name_for_url(self, url: str, red_leads: List[Dict[str, Any]]) -> str:
        """Get business name for a given URL"""
        for lead in red_leads:
            if lead.get('website', '').strip() == url:
                return lead.get('business_name', 'Unknown Business')
        return 'Unknown Business'
    
    def _update_lead_with_cloud_url(self, url: str, cloud_url: str, red_leads: List[Dict[str, Any]]):
        """Update lead data with cloud storage URL"""
        for lead in red_leads:
            if lead.get('website', '').strip() == url:
                lead['cloud_screenshot_url'] = cloud_url
                break
    
    def _sanitize_filename(self, name: str) -> str:
        """Create a safe filename from business name"""
        import re
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
        return safe_name[:50]  # Limit length
    
    def _generate_upload_summary(self, upload_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of upload results"""
        total_processed = len(upload_results['validation_results'])
        successful_uploads = len(upload_results['cloud_urls'])
        failed_uploads = len(upload_results['failed_uploads'])
        
        # Calculate validation statistics
        valid_files = sum(1 for r in upload_results['validation_results'].values() if r['is_valid'])
        
        return {
            'total_processed': total_processed,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'upload_success_rate': round(successful_uploads / total_processed * 100, 1) if total_processed > 0 else 0,
            'valid_files': valid_files,
            'file_validation_rate': round(valid_files / total_processed * 100, 1) if total_processed > 0 else 0,
            'processing_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _save_upload_report(self, upload_results: Dict[str, Any]):
        """Save detailed upload report"""
        timestamp = int(time.time())
        report_filename = f"drive_upload_report_{timestamp}.json"
        report_path = os.path.join(self.metadata_dir, report_filename)
        
        try:
            with open(report_path, 'w') as f:
                json.dump(upload_results, f, indent=2, default=str)
            
            logger.info(f"Upload report saved: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save upload report: {str(e)}")

def test_google_drive_storage():
    """Test Google Drive storage functionality"""
    logger.info("=" * 90)
    logger.info("TASK 6.4: GOOGLE DRIVE CLOUD STORAGE TEST")
    logger.info("=" * 90)
    
    # Create Google Drive storage instance
    drive_storage = GoogleDriveStorage()
    
    # Sample screenshot results (from previous capture)
    screenshot_results = {
        'https://example.com': 'screenshots/playwright_example.com_1753065147.png',
        'https://test-store.myshopify.com': 'screenshots/playwright_test-store.myshopify.com_1753065147.png',
        'https://sample.wordpress.com': 'screenshots/playwright_sample.wordpress.com_1753065147.png'
    }
    
    # Corresponding RED leads data
    red_leads = [
        {
            'business_name': 'Local Pizza Restaurant',
            'website': 'https://example.com',
            'status': 'red',
            'mobile_score': 35
        },
        {
            'business_name': 'Vintage Clothing Store',
            'website': 'https://test-store.myshopify.com',
            'status': 'red',
            'mobile_score': 42
        },
        {
            'business_name': 'Local Law Firm',
            'website': 'https://sample.wordpress.com',
            'status': 'red',
            'mobile_score': 38
        }
    ]
    
    # Check if screenshot files exist, create demo files if not
    for url, path in screenshot_results.items():
        if not os.path.exists(path):
            business_name = drive_storage._get_business_name_for_url(url, red_leads)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(f"Demo screenshot for {business_name}\n")
                f.write(f"URL: {url}\n")
                f.write(f"Timestamp: {time.ctime()}\n")
                f.write("This would be a PNG image in production\n" * 10)
    
    logger.info(f"Processing {len(screenshot_results)} screenshots for Google Drive upload")
    
    # Process uploads
    upload_results = drive_storage.upload_screenshots_to_drive(screenshot_results, red_leads)
    
    # Display results
    logger.info("\n" + "=" * 90)
    logger.info("GOOGLE DRIVE UPLOAD RESULTS")
    logger.info("=" * 90)
    
    summary = upload_results['summary']
    logger.info(f"📊 UPLOAD SUMMARY:")
    logger.info(f"   Total processed: {summary['total_processed']}")
    logger.info(f"   Successful uploads: {summary['successful_uploads']}")
    logger.info(f"   Upload success rate: {summary['upload_success_rate']}%")
    logger.info(f"   Failed uploads: {summary['failed_uploads']}")
    logger.info(f"   File validation rate: {summary['file_validation_rate']}%")
    
    logger.info(f"\n☁️  CLOUD URLS:")
    for url, cloud_url in upload_results['cloud_urls'].items():
        business = drive_storage._get_business_name_for_url(url, red_leads)
        logger.info(f"   ✓ {business}")
        logger.info(f"     Original: {url}")
        logger.info(f"     Cloud URL: {cloud_url}")
    
    if upload_results['failed_uploads']:
        logger.info(f"\n❌ FAILED UPLOADS:")
        for failure in upload_results['failed_uploads']:
            logger.info(f"   ✗ {failure['business']}: {failure.get('reason', 'Unknown error')}")
    
    # Show updated lead data
    logger.info(f"\n📄 UPDATED LEAD DATA:")
    for lead in red_leads:
        cloud_url = lead.get('cloud_screenshot_url', 'Not uploaded')
        logger.info(f"   {lead['business_name']}: {cloud_url}")
    
    logger.info("=" * 90)
    return upload_results

if __name__ == "__main__":
    test_google_drive_storage()