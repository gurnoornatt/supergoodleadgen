"""
Lead processing module for Pain-Gap Audit Automation
"""
import pandas as pd
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import re
import time
from datetime import datetime, timedelta
from api_client import SerpApiClient, GooglePageSpeedClient, BuiltWithClient
from screenshot_module import ScreenshotCapture
from config import Config
from logger_config import setup_logger

logger = setup_logger(__name__)

class LeadProcessor:
    """Process leads through the complete analysis pipeline"""
    
    def __init__(self):
        self.serp_client = SerpApiClient()
        self.pagespeed_client = GooglePageSpeedClient()
        self.builtwith_client = BuiltWithClient()
        self.screenshot_capture = ScreenshotCapture()
        
    def extract_leads_from_maps(self, query: str, location: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """Extract business leads from Google Maps search with pagination"""
        try:
            maps_data = self.serp_client.search_google_maps(query, location, max_results)
            local_results = maps_data.get('local_results', [])
            search_metadata = maps_data.get('search_metadata', {})
            
            leads = []
            for result in local_results:
                lead = self._process_maps_result(result)
                if lead:
                    leads.append(lead)
            
            total_results = search_metadata.get('total_results', len(leads))
            pages_fetched = search_metadata.get('pages_fetched', 1)
            
            logger.info(f"Extracted {len(leads)} leads from Maps search: {query} in {location}")
            logger.info(f"Search metadata: {total_results} total results across {pages_fetched} pages")
            return leads
            
        except Exception as e:
            logger.error(f"Failed to extract leads from Maps: {e}")
            return []
    
    def _process_maps_result(self, result: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual Google Maps search result"""
        try:
            # Extract basic information
            business_name = result.get('title', '')
            website = result.get('website', '')
            phone = result.get('phone', '')
            address = result.get('address', '')
            
            # Get Google Business Profile link
            place_id = result.get('place_id', '')
            gps_coordinates = result.get('gps_coordinates', {})
            rating = result.get('rating', 0)
            reviews = result.get('reviews', 0)
            
            # Skip if missing essential information
            if not business_name:
                logger.debug("Skipping result with no business name")
                return None
            
            lead = {
                'business_name': business_name,
                'website': website,
                'phone': phone,
                'address': address,
                'place_id': place_id,
                'google_business_url': f"https://maps.google.com/maps?cid={place_id}" if place_id else '',
                'rating': rating,
                'reviews': reviews,
                'latitude': gps_coordinates.get('latitude', ''),
                'longitude': gps_coordinates.get('longitude', ''),
                'status': 'pending',
                'mobile_score': None,
                'technologies': [],
                'outdated_technologies': [],
                'technology_age_score': None,
                'technology_flags': [],
                'pain_score': None,
                'pain_level': None,
                'pain_breakdown': {},
                'pain_factors': [],
                'screenshot_url': '',
                'logo_url': '',
                'pdf_url': '',
                'error_notes': ''
            }
            
            return lead
            
        except Exception as e:
            logger.error(f"Error processing Maps result: {e}")
            return None
    
    def analyze_website_performance(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze website performance using PageSpeed Insights"""
        website = lead.get('website', '').strip()
        
        if not website:
            lead['error_notes'] = 'No website URL provided'
            lead['status'] = 'skipped'
            return lead
        
        try:
            # Clean and validate URL
            cleaned_url = self._clean_url(website)
            if not cleaned_url:
                lead['error_notes'] = f'Invalid website URL: {website}'
                lead['status'] = 'error'
                return lead
            
            # Analyze mobile performance
            performance_data = self.pagespeed_client.analyze_url(cleaned_url, 'mobile')
            mobile_score = performance_data.get('performance_score', 0)
            
            lead['mobile_score'] = mobile_score
            lead['website'] = cleaned_url
            
            # Determine if this is a RED flag lead
            if mobile_score < Config.RED_FLAG_MOBILE_SCORE_THRESHOLD:
                lead['status'] = 'red'
                logger.info(f"RED FLAG: {lead['business_name']} - Mobile score: {mobile_score}")
            else:
                lead['status'] = 'green'
                logger.info(f"GREEN: {lead['business_name']} - Mobile score: {mobile_score}")
            
            return lead
            
        except Exception as e:
            logger.error(f"Error analyzing performance for {lead['business_name']}: {e}")
            lead['error_notes'] = f'Performance analysis failed: {str(e)}'
            lead['status'] = 'error'
            return lead
    
    def analyze_website_technology(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze website technology stack using BuiltWith"""
        website = lead.get('website', '').strip()
        
        if not website or lead['status'] == 'error':
            return lead
        
        try:
            # Extract domain from URL
            domain = self._extract_domain(website)
            if not domain:
                lead['error_notes'] += ' | Invalid domain for tech analysis'
                return lead
            
            # Analyze technology stack
            tech_data = self.builtwith_client.analyze_domain(domain)
            
            if 'error' in tech_data:
                lead['error_notes'] += f' | Tech analysis: {tech_data["error"]}'
            else:
                technologies = tech_data.get('technologies', [])
                lead['technologies'] = technologies
                
                # Analyze technology age and identify outdated technologies
                tech_analysis = self._analyze_technology_age(technologies)
                lead['outdated_technologies'] = tech_analysis['outdated']
                lead['technology_age_score'] = tech_analysis['age_score']
                lead['technology_flags'] = tech_analysis['flags']
                
                logger.info(f"Technology analysis completed for {lead['business_name']}: {len(technologies)} techs, age score: {tech_analysis['age_score']}")
            
            return lead
            
        except Exception as e:
            logger.error(f"Error analyzing technology for {lead['business_name']}: {e}")
            lead['error_notes'] += f' | Tech analysis failed: {str(e)}'
            return lead
    
    def process_lead_batch(self, leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of leads through the complete pipeline"""
        processed_leads = []
        
        for i, lead in enumerate(leads, 1):
            logger.info(f"Processing lead {i}/{len(leads)}: {lead['business_name']}")
            
            try:
                # Step 1: Analyze website performance
                lead = self.analyze_website_performance(lead)
                
                # Step 2: Analyze technology stack (only for leads with websites)
                if lead.get('website') and lead['status'] != 'error':
                    lead = self.analyze_website_technology(lead)
                
                # Step 3: Apply comprehensive pain scoring algorithm
                lead = self.apply_comprehensive_pain_scoring(lead)
                
                processed_leads.append(lead)
                
            except Exception as e:
                logger.error(f"Critical error processing {lead['business_name']}: {e}")
                lead['status'] = 'error'
                lead['error_notes'] = f'Critical processing error: {str(e)}'
                processed_leads.append(lead)
        
        # Step 4: Capture screenshots for RED leads
        self._capture_screenshots_for_red_leads(processed_leads)
        
        # Generate comprehensive scoring dashboard
        self._generate_scoring_dashboard(processed_leads)
        
        return processed_leads
    
    def _capture_screenshots_for_red_leads(self, leads: List[Dict[str, Any]]) -> None:
        """Capture screenshots for all RED leads"""
        red_leads = [lead for lead in leads if lead.get('status') == 'red']
        
        if not red_leads:
            logger.info("No RED leads found - skipping screenshot capture")
            return
        
        logger.info(f"Starting screenshot capture for {len(red_leads)} RED leads")
        
        try:
            # Use the screenshot capture module
            screenshot_results = self.screenshot_capture.capture_screenshot_for_red_leads(red_leads)
            
            # Update leads with screenshot information
            for lead in red_leads:
                url = lead.get('website', '').strip()
                if url in screenshot_results:
                    lead['screenshot_url'] = screenshot_results[url]
                    logger.info(f"Screenshot captured for {lead['business_name']}: {screenshot_results[url]}")
                elif lead.get('screenshot_url') != 'FAILED':
                    lead['screenshot_url'] = 'NO_SCREENSHOT'
                    logger.warning(f"No screenshot captured for {lead['business_name']}")
            
            successful_captures = len(screenshot_results)
            logger.info(f"Screenshot capture completed: {successful_captures}/{len(red_leads)} successful")
            
        except Exception as e:
            logger.error(f"Error during screenshot capture process: {e}")
            # Mark all RED leads as having failed screenshot capture
            for lead in red_leads:
                if not lead.get('screenshot_url'):
                    lead['screenshot_url'] = 'FAILED'
                    lead['error_notes'] = lead.get('error_notes', '') + ' Screenshot capture failed;'
    
    def _generate_scoring_dashboard(self, leads: List[Dict[str, Any]]) -> None:
        """Generate scoring dashboard and analytics"""
        red_count = sum(1 for lead in leads if lead['status'] == 'red')
        green_count = sum(1 for lead in leads if lead['status'] == 'green')
        yellow_count = sum(1 for lead in leads if lead['status'] == 'yellow')
        error_count = sum(1 for lead in leads if lead['status'] == 'error')
        
        logger.info(f"Batch processing complete: {red_count} RED, {green_count} GREEN, {yellow_count} YELLOW, {error_count} errors")
        
        # Pain scoring analytics
        pain_scores = [lead.get('pain_score', 0) for lead in leads if lead.get('pain_score') is not None]
        mobile_scores = [lead.get('mobile_score', 0) for lead in leads if lead.get('mobile_score') is not None]
        tech_age_scores = [lead.get('technology_age_score', 0) for lead in leads if lead.get('technology_age_score') is not None]
        
        if pain_scores:
            avg_pain = sum(pain_scores) / len(pain_scores)
            avg_mobile = sum(mobile_scores) / len(mobile_scores) if mobile_scores else 0
            avg_tech_age = sum(tech_age_scores) / len(tech_age_scores) if tech_age_scores else 0
            
            logger.info("=" * 60)
            logger.info("COMPREHENSIVE SCORING DASHBOARD")
            logger.info("=" * 60)
            logger.info(f"📊 LEAD DISTRIBUTION:")
            logger.info(f"   🔴 RED (High Pain):    {red_count:3d} leads ({red_count/len(leads)*100:.1f}%)")
            logger.info(f"   🟡 YELLOW (Med Pain):  {yellow_count:3d} leads ({yellow_count/len(leads)*100:.1f}%)")
            logger.info(f"   🟢 GREEN (Low Pain):   {green_count:3d} leads ({green_count/len(leads)*100:.1f}%)")
            logger.info(f"   ⚪ ERROR:              {error_count:3d} leads ({error_count/len(leads)*100:.1f}%)")
            
            logger.info(f"📈 AVERAGE SCORES:")
            logger.info(f"   Pain Score:        {avg_pain:.1f}/100 (lower is better)")
            logger.info(f"   Mobile Performance: {avg_mobile:.1f}/100 (higher is better)")
            logger.info(f"   Technology Age:     {avg_tech_age:.1f}/100 (higher is better)")
            
            # Pain factors analysis
            all_pain_factors = []
            for lead in leads:
                factors = lead.get('pain_factors', [])
                if factors:
                    all_pain_factors.extend(factors)
            
            if all_pain_factors:
                mobile_issues = sum(1 for factor in all_pain_factors if 'mobile performance' in factor.lower())
                tech_issues = sum(1 for factor in all_pain_factors if 'technology' in factor.lower())
                
                logger.info(f"🔍 PAIN FACTORS:")
                logger.info(f"   Mobile Performance Issues: {mobile_issues}")
                logger.info(f"   Technology Stack Issues:   {tech_issues}")
            
            # Top pain businesses
            red_leads = [lead for lead in leads if lead['status'] == 'red']
            if red_leads:
                sorted_red = sorted(red_leads, key=lambda x: x.get('pain_score', 0), reverse=True)
                logger.info(f"🎯 TOP PAIN LEADS (Highest Scores):")
                for i, lead in enumerate(sorted_red[:3], 1):
                    pain = lead.get('pain_score', 0)
                    mobile = lead.get('mobile_score', 0)
                    logger.info(f"   {i}. {lead['business_name']}: Pain {pain:.1f}, Mobile {mobile}/100")
            
            logger.info("=" * 60)
    
    def _clean_url(self, url: str) -> Optional[str]:
        """Clean and validate URL"""
        if not url:
            return None
        
        url = url.strip()
        
        # Add protocol if missing
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return None
            return url
        except Exception:
            return None
    
    def _extract_domain(self, url: str) -> Optional[str]:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain if domain else None
        except Exception:
            return None
    
    def _analyze_technology_age(self, technologies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze technology age and identify outdated technologies"""
        outdated_technologies = []
        current_time = time.time() * 1000  # Convert to milliseconds
        age_scores = []
        flags = []
        
        # Define technology age thresholds (in years)
        OUTDATED_THRESHOLD_YEARS = 3
        VERY_OUTDATED_THRESHOLD_YEARS = 5
        
        # Convert years to milliseconds
        outdated_threshold_ms = OUTDATED_THRESHOLD_YEARS * 365 * 24 * 60 * 60 * 1000
        very_outdated_threshold_ms = VERY_OUTDATED_THRESHOLD_YEARS * 365 * 24 * 60 * 60 * 1000
        
        # Known problematic or outdated technologies to flag
        PROBLEMATIC_TECHNOLOGIES = {
            'flash', 'silverlight', 'activex', 'java applet', 'internet explorer',
            'ie6', 'ie7', 'ie8', 'ie9', 'jquery 1.', 'php 5.', 'python 2.',
            'angular.js', 'angularjs', 'backbone.js', 'prototype.js'
        }
        
        for tech in technologies:
            try:
                name = tech.get('name', '').lower()
                last_detected = tech.get('last_detected', '')
                first_detected = tech.get('first_detected', '')
                category = tech.get('category', '')
                
                # Skip if no detection timestamps
                if not last_detected:
                    continue
                
                # Convert timestamp to milliseconds if needed
                if isinstance(last_detected, str):
                    try:
                        last_detected = int(last_detected)
                    except (ValueError, TypeError):
                        continue
                
                # Calculate age since last detection
                age_ms = current_time - last_detected
                age_years = age_ms / (365 * 24 * 60 * 60 * 1000)
                
                # Score technology age (0-100, where 100 is current, 0 is very outdated)
                if age_years <= 1:
                    age_score = 100
                elif age_years <= 2:
                    age_score = 80
                elif age_years <= 3:
                    age_score = 60
                elif age_years <= 5:
                    age_score = 30
                else:
                    age_score = 10
                
                age_scores.append(age_score)
                
                # Check if technology is outdated
                is_outdated = False
                severity = 'medium'
                
                # Check against problematic technologies list
                for prob_tech in PROBLEMATIC_TECHNOLOGIES:
                    if prob_tech in name:
                        is_outdated = True
                        severity = 'high'
                        flags.append(f"Problematic technology: {tech.get('name')}")
                        break
                
                # Check age-based outdated status
                if not is_outdated:
                    if age_ms > very_outdated_threshold_ms:
                        is_outdated = True
                        severity = 'high'
                        flags.append(f"Very outdated: {tech.get('name')} (last seen {age_years:.1f} years ago)")
                    elif age_ms > outdated_threshold_ms:
                        is_outdated = True
                        severity = 'medium'
                        flags.append(f"Outdated: {tech.get('name')} (last seen {age_years:.1f} years ago)")
                
                if is_outdated:
                    outdated_tech = {
                        'name': tech.get('name'),
                        'category': category,
                        'age_years': round(age_years, 1),
                        'last_detected': last_detected,
                        'severity': severity,
                        'reason': f"Last detected {age_years:.1f} years ago"
                    }
                    outdated_technologies.append(outdated_tech)
                    
            except Exception as e:
                logger.debug(f"Error analyzing technology age for {tech.get('name', 'unknown')}: {e}")
                continue
        
        # Calculate overall technology age score
        if age_scores:
            overall_age_score = sum(age_scores) / len(age_scores)
        else:
            overall_age_score = 50  # Neutral score if no technologies analyzed
        
        # Add summary flags
        if outdated_technologies:
            high_severity_count = sum(1 for tech in outdated_technologies if tech['severity'] == 'high')
            medium_severity_count = sum(1 for tech in outdated_technologies if tech['severity'] == 'medium')
            
            if high_severity_count > 0:
                flags.append(f"🚨 {high_severity_count} critical outdated technologies")
            if medium_severity_count > 0:
                flags.append(f"⚠️ {medium_severity_count} moderately outdated technologies")
        
        return {
            'outdated': outdated_technologies,
            'age_score': round(overall_age_score, 1),
            'flags': flags,
            'total_technologies': len(technologies),
            'outdated_count': len(outdated_technologies)
        }
    
    def apply_comprehensive_pain_scoring(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Apply comprehensive pain scoring algorithm combining performance and technology factors"""
        try:
            # Initialize scoring components
            mobile_score = lead.get('mobile_score', 0) or 0
            technology_age_score = lead.get('technology_age_score', 50) or 50
            outdated_technologies = lead.get('outdated_technologies', [])
            technology_flags = lead.get('technology_flags', [])
            
            # Pain scoring weights (higher = more pain/worse)
            MOBILE_WEIGHT = 0.6  # 60% weight on mobile performance
            TECH_AGE_WEIGHT = 0.3  # 30% weight on technology age
            TECH_FLAGS_WEIGHT = 0.1  # 10% weight on critical tech flags
            
            # Calculate pain scores (0-100, where 100 = maximum pain)
            mobile_pain_score = 100 - mobile_score  # Invert mobile score
            tech_age_pain_score = 100 - technology_age_score  # Invert tech age score
            
            # Technology flags pain score based on critical issues
            tech_flags_pain_score = 0
            if technology_flags:
                critical_flags = sum(1 for flag in technology_flags if '🚨' in str(flag))
                warning_flags = sum(1 for flag in technology_flags if '⚠️' in str(flag))
                problem_flags = sum(1 for flag in technology_flags if 'Problematic technology' in str(flag))
                
                # Score based on severity and count
                tech_flags_pain_score = min(100, (critical_flags * 30) + (warning_flags * 15) + (problem_flags * 20))
            
            # Calculate overall pain score
            overall_pain_score = (
                (mobile_pain_score * MOBILE_WEIGHT) +
                (tech_age_pain_score * TECH_AGE_WEIGHT) +
                (tech_flags_pain_score * TECH_FLAGS_WEIGHT)
            )
            
            # Determine pain level and final status
            # Pain threshold: 40+ = RED (corresponds to mobile score < 60)
            pain_threshold = 100 - Config.RED_FLAG_MOBILE_SCORE_THRESHOLD  # 100 - 60 = 40
            
            if overall_pain_score >= pain_threshold:
                pain_level = 'high'
                final_status = 'red'
            elif overall_pain_score >= 30:
                pain_level = 'medium'
                final_status = 'yellow'  # Medium pain level
            else:
                pain_level = 'low'
                final_status = 'green'
            
            # Override with existing status if it's already red from mobile score
            if lead.get('status') == 'red':
                final_status = 'red'
                pain_level = 'high'
            elif lead.get('status') == 'error':
                final_status = 'error'
                pain_level = 'unknown'
            
            # Pain score breakdown for analysis
            pain_breakdown = {
                'mobile_pain': round(mobile_pain_score, 1),
                'tech_age_pain': round(tech_age_pain_score, 1),
                'tech_flags_pain': round(tech_flags_pain_score, 1),
                'overall_pain': round(overall_pain_score, 1),
                'pain_level': pain_level,
                'scoring_weights': {
                    'mobile': MOBILE_WEIGHT,
                    'tech_age': TECH_AGE_WEIGHT,
                    'tech_flags': TECH_FLAGS_WEIGHT
                }
            }
            
            # Update lead with comprehensive scoring
            lead['status'] = final_status
            lead['pain_score'] = round(overall_pain_score, 1)
            lead['pain_level'] = pain_level
            lead['pain_breakdown'] = pain_breakdown
            
            # Add pain factors summary
            pain_factors = []
            if mobile_pain_score > 40:
                pain_factors.append(f"Poor mobile performance ({mobile_score}/100)")
            if tech_age_pain_score > 50:
                pain_factors.append(f"Outdated technology stack (age score: {technology_age_score})")
            if tech_flags_pain_score > 20:
                pain_factors.append(f"Critical technology issues ({len(outdated_technologies)} outdated)")
            
            lead['pain_factors'] = pain_factors
            
            logger.info(f"Pain scoring for {lead['business_name']}: {overall_pain_score:.1f} ({pain_level}) -> {final_status.upper()}")
            
            return lead
            
        except Exception as e:
            logger.error(f"Error in comprehensive pain scoring for {lead.get('business_name', 'unknown')}: {e}")
            # Keep existing status if scoring fails
            lead['pain_score'] = 50.0  # Neutral score
            lead['pain_level'] = 'unknown'
            lead['pain_breakdown'] = {}
            lead['pain_factors'] = ['Scoring analysis failed']
            return lead
    
    def save_leads_to_csv(self, leads: List[Dict[str, Any]], filename: str = "leads_output.csv") -> str:
        """Save processed leads to CSV file"""
        try:
            df = pd.DataFrame(leads)
            
            # Reorder columns for better readability
            column_order = [
                'business_name', 'website', 'phone', 'address', 'status',
                'mobile_score', 'pain_score', 'pain_level', 'pain_factors',
                'rating', 'reviews', 'google_business_url', 'place_id', 
                'latitude', 'longitude', 'technologies', 'outdated_technologies', 
                'technology_age_score', 'technology_flags', 'pain_breakdown',
                'screenshot_url', 'logo_url', 'pdf_url', 'error_notes'
            ]
            
            # Only include columns that exist in the DataFrame
            available_columns = [col for col in column_order if col in df.columns]
            df = df[available_columns]
            
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(leads)} leads to {filename}")
            
            return filename
            
        except Exception as e:
            logger.error(f"Error saving leads to CSV: {e}")
            raise