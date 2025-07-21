"""
Screenshot Storage and Quality Validation Module
Handles cloud storage upload and comprehensive quality validation for screenshots
"""

import os
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urlparse
from pathlib import Path
import json
from logger_config import setup_logger

logger = setup_logger(__name__)

class ScreenshotStorageValidator:
    """Handles screenshot cloud storage and quality validation"""
    
    def __init__(self):
        self.local_storage_dir = "screenshots"
        self.cloud_storage_dir = "cloud_screenshots"
        self.validation_reports_dir = "validation_reports"
        
        # Create directories
        for directory in [self.local_storage_dir, self.cloud_storage_dir, self.validation_reports_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                logger.info(f"Created directory: {directory}")
        
        # Quality validation criteria
        self.quality_criteria = {
            'min_file_size': 1000,      # Minimum 1KB
            'max_file_size': 50 * 1024 * 1024,  # Maximum 50MB
            'min_width': 800,           # Minimum width for quality
            'min_height': 600,          # Minimum height for quality
            'max_width': 4000,          # Maximum reasonable width
            'max_height': 6000,         # Maximum reasonable height
            'required_formats': ['.png', '.jpg', '.jpeg'],
            'max_loading_indicators': 3,  # Maximum acceptable loading indicators
        }
        
        # Cloud storage configuration (simulated)
        self.cloud_config = {
            'provider': 'aws_s3',  # Could be 'aws_s3', 'google_cloud', 'azure_blob'
            'bucket_name': 'redflag-screenshots',
            'region': 'us-west-2',
            'public_read': True,
            'base_url': 'https://redflag-screenshots.s3.amazonaws.com/'
        }
    
    def store_and_validate_screenshots(self, screenshot_results: Dict[str, str], 
                                     red_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Store screenshots in cloud storage and validate quality
        
        Args:
            screenshot_results: Dictionary mapping URLs to local screenshot paths
            red_leads: List of RED lead data
            
        Returns:
            Dictionary with storage and validation results
        """
        logger.info(f"Starting storage and validation for {len(screenshot_results)} screenshots")
        
        results = {
            'stored_screenshots': {},
            'validation_results': {},
            'failed_uploads': [],
            'quality_issues': [],
            'summary': {}
        }
        
        for url, local_path in screenshot_results.items():
            business_name = self._get_business_name_for_url(url, red_leads)
            logger.info(f"Processing screenshot for {business_name}: {local_path}")
            
            try:
                # Step 1: Validate screenshot quality
                validation_result = self.validate_screenshot_quality(local_path, business_name)
                results['validation_results'][url] = validation_result
                
                if not validation_result['is_valid']:
                    results['quality_issues'].append({
                        'business': business_name,
                        'url': url,
                        'issues': validation_result['issues']
                    })
                    logger.warning(f"Quality validation failed for {business_name}: {validation_result['issues']}")
                
                # Step 2: Upload to cloud storage (even if quality issues exist)
                cloud_url = self.upload_to_cloud_storage(local_path, business_name, url)
                
                if cloud_url:
                    results['stored_screenshots'][url] = cloud_url
                    logger.info(f"✓ Uploaded to cloud: {cloud_url}")
                    
                    # Update lead data with cloud URL
                    self._update_lead_with_cloud_url(url, cloud_url, red_leads)
                else:
                    results['failed_uploads'].append({
                        'business': business_name,
                        'url': url,
                        'local_path': local_path
                    })
                    logger.error(f"✗ Failed to upload {business_name} screenshot")
                
            except Exception as e:
                logger.error(f"Error processing screenshot for {business_name}: {str(e)}")
                results['failed_uploads'].append({
                    'business': business_name,
                    'url': url,
                    'error': str(e)
                })
        
        # Generate summary
        results['summary'] = self._generate_storage_validation_summary(results)
        
        # Save validation report
        self._save_validation_report(results)
        
        logger.info("Storage and validation completed")
        return results
    
    def validate_screenshot_quality(self, file_path: str, business_name: str = "") -> Dict[str, Any]:
        """
        Comprehensive screenshot quality validation
        
        Args:
            file_path: Path to screenshot file
            business_name: Business name for context
            
        Returns:
            Dictionary with validation results
        """
        logger.debug(f"Validating screenshot quality: {file_path}")
        
        validation_result = {
            'is_valid': True,
            'issues': [],
            'warnings': [],
            'file_info': {},
            'quality_score': 100,
            'business_name': business_name
        }
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                validation_result['is_valid'] = False
                validation_result['issues'].append("File does not exist")
                validation_result['quality_score'] = 0
                return validation_result
            
            # File size validation
            file_size = os.path.getsize(file_path)
            validation_result['file_info']['size_bytes'] = file_size
            
            if file_size < self.quality_criteria['min_file_size']:
                validation_result['is_valid'] = False
                validation_result['issues'].append(f"File too small: {file_size} bytes (min: {self.quality_criteria['min_file_size']})")
                validation_result['quality_score'] -= 30
            
            if file_size > self.quality_criteria['max_file_size']:
                validation_result['warnings'].append(f"File very large: {file_size} bytes")
                validation_result['quality_score'] -= 10
            
            # File format validation
            file_extension = Path(file_path).suffix.lower()
            validation_result['file_info']['format'] = file_extension
            
            if file_extension not in self.quality_criteria['required_formats']:
                validation_result['warnings'].append(f"Unexpected format: {file_extension}")
                validation_result['quality_score'] -= 5
            
            # Simulate image dimension validation (in real implementation, would use PIL)
            simulated_dimensions = self._simulate_image_analysis(file_path, file_size)
            validation_result['file_info'].update(simulated_dimensions)
            
            # Dimension validation
            width = simulated_dimensions.get('width', 0)
            height = simulated_dimensions.get('height', 0)
            
            if width < self.quality_criteria['min_width']:
                validation_result['issues'].append(f"Width too small: {width}px (min: {self.quality_criteria['min_width']}px)")
                validation_result['quality_score'] -= 20
            
            if height < self.quality_criteria['min_height']:
                validation_result['issues'].append(f"Height too small: {height}px (min: {self.quality_criteria['min_height']}px)")
                validation_result['quality_score'] -= 20
            
            if width > self.quality_criteria['max_width']:
                validation_result['warnings'].append(f"Width very large: {width}px")
                validation_result['quality_score'] -= 5
            
            if height > self.quality_criteria['max_height']:
                validation_result['warnings'].append(f"Height very large: {height}px")
                validation_result['quality_score'] -= 5
            
            # Content quality checks (simulated)
            content_issues = self._simulate_content_analysis(file_path, business_name)
            if content_issues:
                validation_result['warnings'].extend(content_issues)
                validation_result['quality_score'] -= len(content_issues) * 5
            
            # Final quality assessment
            if validation_result['quality_score'] < 60:
                validation_result['is_valid'] = False
                validation_result['issues'].append(f"Overall quality score too low: {validation_result['quality_score']}/100")
            
            # Ensure quality score doesn't go below 0
            validation_result['quality_score'] = max(0, validation_result['quality_score'])
            
            logger.debug(f"Validation complete for {business_name}: Score {validation_result['quality_score']}/100")
            
        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Validation error: {str(e)}")
            validation_result['quality_score'] = 0
        
        return validation_result
    
    def upload_to_cloud_storage(self, local_path: str, business_name: str, url: str) -> Optional[str]:
        """
        Upload screenshot to cloud storage
        
        Args:
            local_path: Local file path
            business_name: Business name for organizing
            url: Original website URL
            
        Returns:
            Cloud storage URL or None if failed
        """
        try:
            # Generate cloud file name
            safe_business_name = self._sanitize_filename(business_name)
            domain = urlparse(url).netloc.replace('www.', '')
            timestamp = int(time.time())
            
            cloud_filename = f"{safe_business_name}_{domain}_{timestamp}.png"
            cloud_path = os.path.join(self.cloud_storage_dir, cloud_filename)
            
            # Simulate cloud upload by copying to cloud directory
            # In real implementation, this would use AWS SDK, Google Cloud SDK, etc.
            self._simulate_cloud_upload(local_path, cloud_path, business_name)
            
            # Generate public URL
            cloud_url = f"{self.cloud_config['base_url']}{cloud_filename}"
            
            logger.info(f"Simulated cloud upload: {cloud_url}")
            return cloud_url
            
        except Exception as e:
            logger.error(f"Cloud upload failed for {business_name}: {str(e)}")
            return None
    
    def _simulate_cloud_upload(self, local_path: str, cloud_path: str, business_name: str):
        """Simulate cloud upload by creating a metadata file"""
        upload_metadata = {
            'business_name': business_name,
            'original_path': local_path,
            'upload_timestamp': time.time(),
            'upload_time_iso': time.strftime('%Y-%m-%d %H:%M:%S'),
            'file_size': os.path.getsize(local_path),
            'cloud_provider': self.cloud_config['provider'],
            'bucket': self.cloud_config['bucket_name'],
            'region': self.cloud_config['region'],
            'public_read': self.cloud_config['public_read']
        }
        
        # Create metadata file
        metadata_path = cloud_path + '.metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(upload_metadata, f, indent=2)
        
        # Create placeholder cloud file
        with open(cloud_path, 'w') as f:
            f.write(f"CLOUD STORAGE PLACEHOLDER\n")
            f.write(f"Business: {business_name}\n")
            f.write(f"Original: {local_path}\n")
            f.write(f"Uploaded: {upload_metadata['upload_time_iso']}\n")
        
        logger.debug(f"Simulated upload complete: {cloud_path}")
    
    def _simulate_image_analysis(self, file_path: str, file_size: int) -> Dict[str, Any]:
        """Simulate image dimension and property analysis"""
        # In real implementation, would use PIL/Pillow:
        # from PIL import Image
        # with Image.open(file_path) as img:
        #     return {'width': img.width, 'height': img.height, 'format': img.format}
        
        # Simulate realistic dimensions based on file size
        if file_size < 5000:
            width, height = 400, 300  # Very small
        elif file_size < 50000:
            width, height = 1024, 768  # Small
        elif file_size < 500000:
            width, height = 1920, 1080  # Standard
        else:
            width, height = 2560, 1440  # Large
        
        return {
            'width': width,
            'height': height,
            'aspect_ratio': round(width / height, 2),
            'estimated_format': 'PNG'
        }
    
    def _simulate_content_analysis(self, file_path: str, business_name: str) -> List[str]:
        """Simulate content quality analysis"""
        issues = []
        
        # Simulate various content issues based on business name or file characteristics
        file_size = os.path.getsize(file_path)
        
        if 'loading' in business_name.lower():
            issues.append("Possible loading indicator detected")
        
        if file_size < 2000:
            issues.append("Image may be blank or mostly empty")
        
        if 'error' in business_name.lower():
            issues.append("Possible error page captured")
        
        # Simulate random content quality issues
        import random
        random.seed(hash(business_name))  # Consistent results for same business
        
        if random.random() < 0.1:  # 10% chance
            issues.append("Possible popup or overlay detected")
        
        if random.random() < 0.05:  # 5% chance
            issues.append("Low contrast or visibility issues")
        
        return issues
    
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
    
    def _generate_storage_validation_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of storage and validation results"""
        total_processed = len(results['validation_results'])
        successful_uploads = len(results['stored_screenshots'])
        failed_uploads = len(results['failed_uploads'])
        quality_issues = len(results['quality_issues'])
        
        # Calculate quality statistics
        valid_screenshots = sum(1 for r in results['validation_results'].values() if r['is_valid'])
        quality_scores = [r['quality_score'] for r in results['validation_results'].values()]
        avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            'total_processed': total_processed,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'upload_success_rate': round(successful_uploads / total_processed * 100, 1) if total_processed > 0 else 0,
            'quality_issues': quality_issues,
            'valid_screenshots': valid_screenshots,
            'quality_pass_rate': round(valid_screenshots / total_processed * 100, 1) if total_processed > 0 else 0,
            'average_quality_score': round(avg_quality_score, 1),
            'processing_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _save_validation_report(self, results: Dict[str, Any]):
        """Save detailed validation report"""
        timestamp = int(time.time())
        report_filename = f"validation_report_{timestamp}.json"
        report_path = os.path.join(self.validation_reports_dir, report_filename)
        
        try:
            with open(report_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"Validation report saved: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save validation report: {str(e)}")

def demonstrate_storage_validation():
    """Demonstrate storage and validation functionality"""
    logger.info("=" * 90)
    logger.info("SCREENSHOT STORAGE AND VALIDATION DEMONSTRATION")
    logger.info("=" * 90)
    
    # Create some sample screenshot files
    storage_validator = ScreenshotStorageValidator()
    
    # Sample RED leads data
    red_leads = [
        {
            'business_name': 'High Quality Restaurant',
            'website': 'https://example.com',
            'status': 'red',
            'mobile_score': 35
        },
        {
            'business_name': 'Loading Issues Cafe',
            'website': 'https://slow-site.com',
            'status': 'red',
            'mobile_score': 42
        },
        {
            'business_name': 'Error Page Business',
            'website': 'https://error-site.com',
            'status': 'red',
            'mobile_score': 28
        }
    ]
    
    # Create sample screenshot files
    screenshot_results = {}
    for lead in red_leads:
        url = lead['website']
        business_name = lead['business_name']
        
        # Create sample screenshot file
        filename = f"sample_{business_name.replace(' ', '_').lower()}.png"
        filepath = os.path.join('screenshots', filename)
        
        # Simulate different file sizes for different quality results
        if 'high quality' in business_name.lower():
            content_size = 100000  # Large, good quality
        elif 'loading' in business_name.lower():
            content_size = 5000   # Small, poor quality
        else:
            content_size = 500    # Very small, very poor quality
        
        with open(filepath, 'w') as f:
            f.write("Sample screenshot content\n" * (content_size // 30))
        
        screenshot_results[url] = filepath
    
    logger.info(f"Created {len(screenshot_results)} sample screenshot files")
    
    # Process storage and validation
    results = storage_validator.store_and_validate_screenshots(screenshot_results, red_leads)
    
    # Display results
    logger.info("\n" + "=" * 90)
    logger.info("STORAGE AND VALIDATION RESULTS")
    logger.info("=" * 90)
    
    summary = results['summary']
    logger.info(f"📊 SUMMARY METRICS:")
    logger.info(f"   Total processed: {summary['total_processed']}")
    logger.info(f"   Successful uploads: {summary['successful_uploads']}")
    logger.info(f"   Upload success rate: {summary['upload_success_rate']}%")
    logger.info(f"   Quality issues detected: {summary['quality_issues']}")
    logger.info(f"   Quality pass rate: {summary['quality_pass_rate']}%")
    logger.info(f"   Average quality score: {summary['average_quality_score']}/100")
    
    logger.info(f"\n📁 CLOUD STORAGE RESULTS:")
    for url, cloud_url in results['stored_screenshots'].items():
        business = storage_validator._get_business_name_for_url(url, red_leads)
        logger.info(f"   ✓ {business}: {cloud_url}")
    
    if results['failed_uploads']:
        logger.info(f"\n❌ FAILED UPLOADS:")
        for failure in results['failed_uploads']:
            logger.info(f"   ✗ {failure['business']}: {failure.get('error', 'Upload failed')}")
    
    if results['quality_issues']:
        logger.info(f"\n⚠️  QUALITY ISSUES:")
        for issue in results['quality_issues']:
            logger.info(f"   ⚠️  {issue['business']}: {', '.join(issue['issues'])}")
    
    # Detailed validation results
    logger.info(f"\n🔍 DETAILED VALIDATION RESULTS:")
    for url, validation in results['validation_results'].items():
        business = storage_validator._get_business_name_for_url(url, red_leads)
        status = "✓ PASS" if validation['is_valid'] else "✗ FAIL"
        score = validation['quality_score']
        
        logger.info(f"   {business}:")
        logger.info(f"     Status: {status} (Score: {score}/100)")
        logger.info(f"     File size: {validation['file_info'].get('size_bytes', 0)} bytes")
        logger.info(f"     Dimensions: {validation['file_info'].get('width', 0)}x{validation['file_info'].get('height', 0)}")
        
        if validation['issues']:
            logger.info(f"     Issues: {', '.join(validation['issues'])}")
        if validation['warnings']:
            logger.info(f"     Warnings: {', '.join(validation['warnings'])}")
    
    logger.info("=" * 90)
    
    return results

if __name__ == "__main__":
    demonstrate_storage_validation()