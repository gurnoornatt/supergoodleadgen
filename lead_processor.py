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
from logo_extractor_mcp import LogoExtractorMCP
from config import Config
from logger_config import setup_logger
from gym_software_database import gym_software_db

logger = setup_logger(__name__)

class LeadProcessor:
    """Process leads through the complete analysis pipeline"""
    
    def __init__(self):
        self.serp_client = SerpApiClient()
        self.pagespeed_client = GooglePageSpeedClient()
        self.builtwith_client = BuiltWithClient()
        self.screenshot_capture = ScreenshotCapture()
        self.logo_extractor = LogoExtractorMCP()
        
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
            
            # Extract gym-specific data from result
            gym_data = self._extract_gym_specific_data(result)
            
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
                'error_notes': '',
                # Gym-specific fields
                'gym_type': gym_data.get('gym_type', ''),
                'gym_size_estimate': gym_data.get('gym_size_estimate', ''),
                'gym_size_confidence': gym_data.get('gym_size_confidence', 0),
                'gym_size_factors': gym_data.get('gym_size_factors', []),
                'gym_services': gym_data.get('gym_services', []),
                'gym_location_type': gym_data.get('gym_location_type', ''),
                'gym_membership_model': gym_data.get('gym_membership_model', ''),
                'gym_equipment_types': gym_data.get('gym_equipment_types', []),
                'gym_operating_hours': gym_data.get('gym_operating_hours', ''),
                'gym_pricing_indicators': gym_data.get('gym_pricing_indicators', []),
                'gym_target_demographic': gym_data.get('gym_target_demographic', ''),
                'gym_franchise_chain': gym_data.get('gym_franchise_chain', ''),
                'gym_years_in_business': gym_data.get('gym_years_in_business', ''),
                'gym_staff_size_estimate': gym_data.get('gym_staff_size_estimate', ''),
                'gym_digital_presence_score': gym_data.get('gym_digital_presence_score', 0),
                'gym_software_needs_score': gym_data.get('gym_software_needs_score', 0),
                # Gym software detection fields
                'gym_software_detected': [],
                'gym_software_scores': {},
                'gym_software_quality_score': 0,
                'gym_software_recommendations': [],
                'gym_software_red_flags': [],
                
                # Website feature analysis fields
                'gym_website_features': {},
                'gym_website_feature_score': 0,
                'gym_website_feature_indicators': [],
                'gym_website_missing_features': [],
                'gym_website_feature_recommendations': [],
                'gym_website_implemented_features': 0
            }
            
            return lead
            
        except Exception as e:
            logger.error(f"Error processing Maps result: {e}")
            return None
    
    def _extract_gym_specific_data(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract gym-specific data from Google Maps result"""
        try:
            business_name = result.get('title', '').lower()
            description = result.get('snippet', '').lower()
            categories = result.get('type', '').lower()
            address = result.get('address', '').lower()
            reviews_data = result.get('reviews_data', []) if isinstance(result.get('reviews_data'), list) else []
            
            # Combine all text data for analysis
            combined_text = f"{business_name} {description} {categories} {address}"
            
            # Extract gym type based on business name and categories
            gym_type = self._determine_gym_type(combined_text)
            
            # Estimate gym size based on available indicators
            gym_size_estimate, size_estimation_details = self._estimate_gym_size_with_details(result, combined_text)
            
            # Extract services offered
            gym_services = self._extract_gym_services(combined_text)
            
            # Determine location type
            gym_location_type = self._determine_location_type(address, combined_text)
            
            # Estimate membership model
            gym_membership_model = self._estimate_membership_model(combined_text)
            
            # Extract equipment types
            gym_equipment_types = self._extract_equipment_types(combined_text)
            
            # Extract operating hours if available
            gym_operating_hours = result.get('hours', '')
            
            # Extract pricing indicators
            gym_pricing_indicators = self._extract_pricing_indicators(combined_text, reviews_data)
            
            # Determine target demographic
            gym_target_demographic = self._determine_target_demographic(combined_text)
            
            # Check if it's a franchise/chain
            gym_franchise_chain = self._identify_franchise_chain(business_name)
            
            # Estimate years in business (basic heuristic)
            gym_years_in_business = self._estimate_years_in_business(result)
            
            # Estimate staff size
            gym_staff_size_estimate = self._estimate_staff_size(gym_size_estimate, gym_type)
            
            # Calculate digital presence score
            gym_digital_presence_score = self._calculate_digital_presence_score(result)
            
            # Calculate software needs score
            gym_software_needs_score = self._calculate_software_needs_score(gym_type, gym_size_estimate, gym_services)
            
            return {
                'gym_type': gym_type,
                'gym_size_estimate': gym_size_estimate,
                'gym_size_confidence': size_estimation_details.get('confidence_level', 0),
                'gym_size_factors': size_estimation_details.get('confidence_factors', []),
                'gym_services': gym_services,
                'gym_location_type': gym_location_type,
                'gym_membership_model': gym_membership_model,
                'gym_equipment_types': gym_equipment_types,
                'gym_operating_hours': gym_operating_hours,
                'gym_pricing_indicators': gym_pricing_indicators,
                'gym_target_demographic': gym_target_demographic,
                'gym_franchise_chain': gym_franchise_chain,
                'gym_years_in_business': gym_years_in_business,
                'gym_staff_size_estimate': gym_staff_size_estimate,
                'gym_digital_presence_score': gym_digital_presence_score,
                'gym_software_needs_score': gym_software_needs_score
            }
            
        except Exception as e:
            logger.debug(f"Error extracting gym-specific data: {e}")
            return {
                'gym_type': '',
                'gym_size_estimate': '',
                'gym_size_confidence': 0,
                'gym_size_factors': [],
                'gym_services': [],
                'gym_location_type': '',
                'gym_membership_model': '',
                'gym_equipment_types': [],
                'gym_operating_hours': '',
                'gym_pricing_indicators': [],
                'gym_target_demographic': '',
                'gym_franchise_chain': '',
                'gym_years_in_business': '',
                'gym_staff_size_estimate': '',
                'gym_digital_presence_score': 0,
                'gym_software_needs_score': 0,
                # Gym software detection fields
                'gym_software_detected': [],
                'gym_software_scores': {},
                'gym_software_quality_score': 0,
                'gym_software_recommendations': [],
                'gym_software_red_flags': []
            }
    
    def _determine_gym_type(self, text: str) -> str:
        """Determine gym type based on text analysis (ordered by specificity)"""
        # Order matters - more specific types should be checked first
        gym_types = [
            ('crossfit', ['crossfit', 'cross fit']),
            ('martial_arts', ['martial arts', 'karate', 'jiu jitsu', 'mma', 'boxing', 'kickboxing', 'dojo']),
            ('dance_studio', ['dance', 'ballet', 'salsa', 'ballroom']),
            ('personal_training', ['personal training', 'personal trainer', '1-on-1']),
            ('recreation_center', ['recreation', 'community center', 'ymca', 'ywca']),
            ('boutique_fitness', ['yoga', 'pilates', 'barre', 'cycling', 'spin', 'hiit', 'boutique']),
            ('specialty_fitness', ['rock climbing', 'swimming', 'aquatic', 'tennis', 'racquet']),
            ('traditional_gym', ['gym', 'fitness center', 'health club', 'fitness club'])
        ]
        
        for gym_type, keywords in gym_types:
            if any(keyword in text for keyword in keywords):
                return gym_type
        
        return 'general_fitness'
    
    def _estimate_gym_size(self, result: Dict[str, Any], text: str) -> str:
        """Enhanced gym size estimation using multiple data sources"""
        # Collect all available data points
        reviews = result.get('reviews', 0)
        rating = result.get('rating', 0)
        business_name = result.get('title', '').lower()
        
        # Initialize scoring system (higher score = larger gym)
        size_score = 0
        confidence_factors = []
        
        # 1. Review count analysis (most reliable indicator)
        if reviews > 1000:
            size_score += 80
            confidence_factors.append(f"High review count ({reviews})")
        elif reviews > 500:
            size_score += 60
            confidence_factors.append(f"Moderate-high review count ({reviews})")
        elif reviews > 200:
            size_score += 40
            confidence_factors.append(f"Moderate review count ({reviews})")
        elif reviews > 50:
            size_score += 20
            confidence_factors.append(f"Low-moderate review count ({reviews})")
        else:
            size_score += 0
            confidence_factors.append(f"Low review count ({reviews})")
        
        # 2. Franchise/Chain identification (strong size indicator)
        major_chains = ['planet fitness', '24 hour fitness', 'la fitness', 'gold\'s gym', 'lifetime', 'equinox']
        mid_chains = ['anytime fitness', 'snap fitness', 'curves', 'orange theory', 'crunch']
        
        for chain in major_chains:
            if chain in business_name:
                size_score += 50
                confidence_factors.append(f"Major chain: {chain}")
                break
        
        for chain in mid_chains:
            if chain in business_name:
                size_score += 30
                confidence_factors.append(f"Mid-size chain: {chain}")
                break
        
        # 3. Text-based size indicators (weighted by specificity)
        text_indicators = [
            # Large indicators
            (['multiple locations', 'locations', 'branches'], 40, 'large'),
            (['24/7', '24 hour', 'always open'], 35, 'large'),
            (['huge', 'massive', 'enormous'], 30, 'large'),
            (['full service', 'complete facility', 'everything'], 25, 'large'),
            (['chain', 'franchise'], 20, 'large'),
            
            # Medium indicators  
            (['established', 'complete', 'full gym'], 15, 'medium'),
            (['mid-size', 'medium'], 20, 'medium'),
            (['multiple rooms', 'various equipment'], 10, 'medium'),
            
            # Small indicators (negative scoring for large)
            (['boutique', 'intimate', 'cozy'], -30, 'small'),
            (['studio', 'small'], -20, 'small'),
            (['personal', 'private', 'exclusive'], -15, 'small'),
            (['home', 'residential'], -40, 'small')
        ]
        
        for keywords, score_change, size_hint in text_indicators:
            if any(keyword in text for keyword in keywords):
                size_score += score_change
                confidence_factors.append(f"Text indicator: {keywords[0]} ({size_hint})")
                break  # Only apply first match to avoid double-counting
        
        # 4. Business type size tendencies
        business_type_scores = {
            'recreation_center': 40,  # Usually large facilities
            'traditional_gym': 20,   # Generally larger than boutique
            'crossfit': 0,           # Varies widely
            'martial_arts': -10,     # Usually smaller
            'dance_studio': -15,     # Usually smaller
            'boutique_fitness': -20, # Explicitly small/intimate
            'personal_training': -30 # Usually very small
        }
        
        gym_type = self._determine_gym_type(text)
        type_score = business_type_scores.get(gym_type, 0)
        if type_score != 0:
            size_score += type_score
            confidence_factors.append(f"Business type: {gym_type} ({type_score:+d})")
        
        # 5. Location type influence
        if 'mall' in text or 'shopping center' in text:
            size_score += 15
            confidence_factors.append("Shopping center location (typically larger)")
        elif 'strip' in text:
            size_score -= 5
            confidence_factors.append("Strip mall location (typically smaller)")
        
        # 6. Rating influence (high ratings with many reviews suggest established, larger gyms)
        if rating >= 4.0 and reviews > 200:
            size_score += 10
            confidence_factors.append(f"High rating with many reviews ({rating}, {reviews})")
        
        # Convert score to size category with adjusted thresholds
        if size_score >= 80:
            estimated_size = 'large'
        elif size_score >= 30:
            estimated_size = 'medium'
        else:
            estimated_size = 'small'
        
        # Calculate confidence level
        confidence_level = min(100, len(confidence_factors) * 20)
        
        # Store detailed estimation data for analysis
        estimation_details = {
            'size_score': size_score,
            'confidence_level': confidence_level,
            'confidence_factors': confidence_factors,
            'estimated_size': estimated_size
        }
        
        # Log detailed estimation for debugging
        logger.debug(f"Gym size estimation for {business_name}: {estimated_size} "
                    f"(score: {size_score}, confidence: {confidence_level}%)")
        logger.debug(f"Factors: {', '.join(confidence_factors[:3])}")  # Log top 3 factors
        
        return estimated_size
    
    def _estimate_gym_size_with_details(self, result: Dict[str, Any], text: str) -> tuple:
        """Enhanced gym size estimation that returns both size and detailed analytics"""
        # Collect all available data points
        reviews = result.get('reviews', 0)
        rating = result.get('rating', 0)
        business_name = result.get('title', '').lower()
        
        # Initialize scoring system (higher score = larger gym)
        size_score = 0
        confidence_factors = []
        
        # 1. Review count analysis (most reliable indicator)
        if reviews > 1000:
            size_score += 80
            confidence_factors.append(f"High review count ({reviews})")
        elif reviews > 500:
            size_score += 60
            confidence_factors.append(f"Moderate-high review count ({reviews})")
        elif reviews > 200:
            size_score += 40
            confidence_factors.append(f"Moderate review count ({reviews})")
        elif reviews > 50:
            size_score += 20
            confidence_factors.append(f"Low-moderate review count ({reviews})")
        else:
            size_score += 0
            confidence_factors.append(f"Low review count ({reviews})")
        
        # 2. Franchise/Chain identification (strong size indicator)
        major_chains = ['planet fitness', '24 hour fitness', 'la fitness', 'gold\'s gym', 'lifetime', 'equinox']
        mid_chains = ['anytime fitness', 'snap fitness', 'curves', 'orange theory', 'crunch']
        
        for chain in major_chains:
            if chain in business_name:
                size_score += 50
                confidence_factors.append(f"Major chain: {chain}")
                break
        
        for chain in mid_chains:
            if chain in business_name:
                size_score += 30
                confidence_factors.append(f"Mid-size chain: {chain}")
                break
        
        # 3. Text-based size indicators (weighted by specificity)
        text_indicators = [
            # Large indicators
            (['multiple locations', 'locations', 'branches'], 40, 'large'),
            (['24/7', '24 hour', 'always open'], 35, 'large'),
            (['huge', 'massive', 'enormous'], 30, 'large'),
            (['full service', 'complete facility', 'everything'], 25, 'large'),
            (['chain', 'franchise'], 20, 'large'),
            
            # Medium indicators  
            (['established', 'complete', 'full gym'], 15, 'medium'),
            (['mid-size', 'medium'], 20, 'medium'),
            (['multiple rooms', 'various equipment'], 10, 'medium'),
            
            # Small indicators (negative scoring for large)
            (['boutique', 'intimate', 'cozy'], -30, 'small'),
            (['studio', 'small'], -20, 'small'),
            (['personal', 'private', 'exclusive'], -15, 'small'),
            (['home', 'residential'], -40, 'small')
        ]
        
        for keywords, score_change, size_hint in text_indicators:
            if any(keyword in text for keyword in keywords):
                size_score += score_change
                confidence_factors.append(f"Text indicator: {keywords[0]} ({size_hint})")
                break  # Only apply first match to avoid double-counting
        
        # 4. Business type size tendencies
        business_type_scores = {
            'recreation_center': 40,  # Usually large facilities
            'traditional_gym': 20,   # Generally larger than boutique
            'crossfit': 0,           # Varies widely
            'martial_arts': -10,     # Usually smaller
            'dance_studio': -15,     # Usually smaller
            'boutique_fitness': -20, # Explicitly small/intimate
            'personal_training': -30 # Usually very small
        }
        
        gym_type = self._determine_gym_type(text)
        type_score = business_type_scores.get(gym_type, 0)
        if type_score != 0:
            size_score += type_score
            confidence_factors.append(f"Business type: {gym_type} ({type_score:+d})")
        
        # 5. Location type influence
        if 'mall' in text or 'shopping center' in text:
            size_score += 15
            confidence_factors.append("Shopping center location (typically larger)")
        elif 'strip' in text:
            size_score -= 5
            confidence_factors.append("Strip mall location (typically smaller)")
        
        # 6. Rating influence (high ratings with many reviews suggest established, larger gyms)
        if rating >= 4.0 and reviews > 200:
            size_score += 10
            confidence_factors.append(f"High rating with many reviews ({rating}, {reviews})")
        
        # Convert score to size category with adjusted thresholds
        if size_score >= 80:
            estimated_size = 'large'
        elif size_score >= 30:
            estimated_size = 'medium'
        else:
            estimated_size = 'small'
        
        # Calculate confidence level
        confidence_level = min(100, len(confidence_factors) * 20)
        
        # Store detailed estimation data for analysis
        estimation_details = {
            'size_score': size_score,
            'confidence_level': confidence_level,
            'confidence_factors': confidence_factors,
            'estimated_size': estimated_size,
            'review_count': reviews,
            'rating': rating,
            'business_name': business_name
        }
        
        # Log detailed estimation for debugging
        logger.debug(f"Gym size estimation for {business_name}: {estimated_size} "
                    f"(score: {size_score}, confidence: {confidence_level}%)")
        logger.debug(f"Factors: {', '.join(confidence_factors[:3])}")  # Log top 3 factors
        
        return estimated_size, estimation_details
    
    def _extract_gym_services(self, text: str) -> List[str]:
        """Extract services offered by the gym"""
        services = []
        service_keywords = {
            'personal_training': ['personal training', 'personal trainer', 'pt'],
            'group_classes': ['group classes', 'fitness classes', 'group fitness'],
            'yoga': ['yoga', 'vinyasa', 'hatha', 'bikram'],
            'pilates': ['pilates', 'reformer'],
            'cardio': ['cardio', 'treadmill', 'elliptical', 'bike'],
            'strength_training': ['strength', 'weights', 'weight training', 'free weights'],
            'swimming': ['pool', 'swimming', 'aquatic', 'water'],
            'childcare': ['childcare', 'kids club', 'child care'],
            'nutrition': ['nutrition', 'meal planning', 'diet'],
            'physical_therapy': ['physical therapy', 'rehabilitation', 'recovery'],
            'spa_services': ['spa', 'massage', 'sauna', 'steam'],
            'sports': ['basketball', 'tennis', 'racquetball', 'volleyball']
        }
        
        for service, keywords in service_keywords.items():
            if any(keyword in text for keyword in keywords):
                services.append(service)
        
        return services
    
    def _determine_location_type(self, address: str, text: str) -> str:
        """Determine gym location type"""
        if any(keyword in text for keyword in ['mall', 'shopping center', 'plaza']):
            return 'shopping_center'
        elif any(keyword in text for keyword in ['downtown', 'city center', 'urban']):
            return 'urban'
        elif any(keyword in text for keyword in ['suburb', 'residential']):
            return 'suburban'
        elif any(keyword in text for keyword in ['strip mall', 'strip center']):
            return 'strip_mall'
        else:
            return 'standalone'
    
    def _estimate_membership_model(self, text: str) -> str:
        """Estimate membership model based on text analysis"""
        if any(keyword in text for keyword in ['drop-in', 'day pass', 'per class', 'pay per']):
            return 'pay_per_use'
        elif any(keyword in text for keyword in ['membership', 'monthly', 'annual']):
            return 'membership'
        elif any(keyword in text for keyword in ['package', 'session', 'bundle']):
            return 'package_based'
        else:
            return 'membership'
    
    def _extract_equipment_types(self, text: str) -> List[str]:
        """Extract equipment types available"""
        equipment = []
        equipment_keywords = {
            'cardio_equipment': ['treadmill', 'elliptical', 'bike', 'stair', 'rowing'],
            'free_weights': ['free weights', 'dumbbells', 'barbells', 'plates'],
            'machines': ['machines', 'cable', 'smith machine', 'leg press'],
            'functional': ['functional', 'kettlebell', 'battle rope', 'suspension'],
            'specialized': ['reformer', 'climbing wall', 'pool', 'court']
        }
        
        for equipment_type, keywords in equipment_keywords.items():
            if any(keyword in text for keyword in keywords):
                equipment.append(equipment_type)
        
        return equipment
    
    def _extract_pricing_indicators(self, text: str, reviews_data: List[Dict]) -> List[str]:
        """Extract pricing indicators from text and reviews"""
        pricing_indicators = []
        
        # Direct price mentions
        if any(keyword in text for keyword in ['$', 'dollar', 'cheap', 'affordable', 'budget']):
            pricing_indicators.append('budget_friendly')
        if any(keyword in text for keyword in ['premium', 'luxury', 'high-end', 'exclusive']):
            pricing_indicators.append('premium')
        
        # From reviews (if available)
        for review in reviews_data[:5]:  # Check first 5 reviews
            review_text = review.get('text', '').lower()
            if 'expensive' in review_text or 'costly' in review_text:
                pricing_indicators.append('high_price')
            elif 'affordable' in review_text or 'reasonable' in review_text:
                pricing_indicators.append('reasonable_price')
        
        return list(set(pricing_indicators))  # Remove duplicates
    
    def _determine_target_demographic(self, text: str) -> str:
        """Determine target demographic"""
        if any(keyword in text for keyword in ['women', 'ladies', 'female']):
            return 'women'
        elif any(keyword in text for keyword in ['senior', 'older', 'mature']):
            return 'seniors'
        elif any(keyword in text for keyword in ['youth', 'teen', 'junior']):
            return 'youth'
        elif any(keyword in text for keyword in ['athlete', 'performance', 'competitive']):
            return 'athletes'
        else:
            return 'general'
    
    def _identify_franchise_chain(self, business_name: str) -> str:
        """Identify if business is part of a franchise or chain"""
        chains = [
            'planet fitness', '24 hour fitness', 'la fitness', 'gold\'s gym',
            'anytime fitness', 'snap fitness', 'curves', 'orange theory',
            'crossfit', 'pure barre', 'soulcycle', 'equinox', 'lifetime',
            'crunch', 'ymca', 'ywca'
        ]
        
        for chain in chains:
            if chain in business_name:
                return chain.title()
        
        return ''
    
    def _estimate_years_in_business(self, result: Dict[str, Any]) -> str:
        """Estimate years in business (basic heuristic)"""
        reviews = result.get('reviews', 0)
        
        if reviews > 1000:
            return '10+'
        elif reviews > 500:
            return '5-10'
        elif reviews > 100:
            return '2-5'
        else:
            return '0-2'
    
    def _estimate_staff_size(self, gym_size: str, gym_type: str) -> str:
        """Estimate staff size based on gym size and type"""
        if gym_size == 'large':
            return '20+'
        elif gym_size == 'medium':
            return '10-20'
        elif gym_type in ['personal_training', 'boutique_fitness']:
            return '2-5'
        else:
            return '5-10'
    
    def _calculate_digital_presence_score(self, result: Dict[str, Any]) -> int:
        """Calculate digital presence score (0-100)"""
        score = 0
        
        # Has website
        if result.get('website'):
            score += 30
        
        # Has Google Business Profile
        if result.get('place_id'):
            score += 20
        
        # Has reviews
        reviews = result.get('reviews', 0)
        if reviews > 0:
            score += min(30, reviews // 10)  # Up to 30 points for reviews
        
        # Has rating
        if result.get('rating', 0) > 0:
            score += 10
        
        # Has photos (if available in result)
        if result.get('photos'):
            score += 10
        
        return min(100, score)
    
    def _calculate_software_needs_score(self, gym_type: str, gym_size: str, services: List[str]) -> int:
        """Calculate software needs score (0-100) - higher means more need"""
        score = 0
        
        # Base score by gym type
        type_scores = {
            'traditional_gym': 80,
            'boutique_fitness': 70,
            'crossfit': 75,
            'martial_arts': 65,
            'dance_studio': 60,
            'specialty_fitness': 70,
            'personal_training': 85,
            'recreation_center': 90
        }
        score += type_scores.get(gym_type, 70)
        
        # Size multiplier
        size_multipliers = {
            'large': 1.2,
            'medium': 1.0,
            'small': 0.8
        }
        score *= size_multipliers.get(gym_size, 1.0)
        
        # Service complexity adds to needs
        complex_services = ['personal_training', 'group_classes', 'childcare', 'nutrition']
        service_bonus = sum(5 for service in services if service in complex_services)
        score += service_bonus
        
        return min(100, int(score))
    
    def _analyze_gym_software(self, technologies: List[Dict[str, Any]], website: str) -> Dict[str, Any]:
        """Analyze gym management software using the gym software database"""
        try:
            # Detect software from technologies
            detected_from_tech = gym_software_db.detect_software_from_technologies(technologies)
            
            # Detect software from website URL
            detected_from_url = gym_software_db.detect_software_from_url(website)
            
            # Combine and deduplicate detections
            all_detected = list(set(detected_from_tech + detected_from_url))
            
            software_scores = {}
            recommendations = []
            red_flags = []
            overall_scores = []
            
            # Analyze each detected software
            for software_key in all_detected:
                software = gym_software_db.get_software_by_name(software_key.replace('_', ' '))
                if software:
                    # Get quality score
                    score_data = gym_software_db.score_software_quality(software.name)
                    software_scores[software.name] = score_data
                    overall_scores.append(score_data['quality_score'])
                    
                    # Add recommendations and red flags
                    recommendations.append(score_data['recommendation'])
                    
                    # Check for red flags
                    if score_data['quality_score'] < 40:
                        red_flags.append(f"Using outdated software: {software.name}")
                    
                    if not software.mobile_app:
                        red_flags.append(f"No mobile app available for {software.name}")
                    
                    if not software.api_available:
                        red_flags.append(f"Limited integration capabilities for {software.name}")
                    
                    if software.quality.value == 'outdated':
                        red_flags.append(f"CRITICAL: {software.name} uses outdated technology")
            
            # Calculate overall software quality score
            if overall_scores:
                overall_quality_score = sum(overall_scores) / len(overall_scores)
            else:
                overall_quality_score = 0
            
            # Check if no specialized gym software was detected
            generic_software = ['wordpress', 'square', 'stripe', 'calendly']
            has_only_generic = all_detected and all(any(generic in software_key for generic in generic_software) for software_key in all_detected)
            
            if not all_detected or has_only_generic:
                recommendations.append("No specialized gym management software detected")
            
            # Add contextual recommendations based on gym type and size
            contextual_recommendations = self._get_contextual_software_recommendations(all_detected)
            recommendations.extend(contextual_recommendations)
            
            return {
                'detected_software': [software_key.replace('_', ' ').title() for software_key in all_detected],
                'software_scores': software_scores,
                'overall_quality_score': round(overall_quality_score, 1),
                'recommendations': recommendations,
                'red_flags': red_flags,
                'detection_methods': {
                    'from_technologies': detected_from_tech,
                    'from_url': detected_from_url
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing gym software: {e}")
            return {
                'detected_software': [],
                'software_scores': {},
                'overall_quality_score': 0,
                'recommendations': ['Software analysis failed'],
                'red_flags': [],
                'detection_methods': {'from_technologies': [], 'from_url': []}
            }
    
    def _analyze_gym_website_features(self, website: str, technologies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze gym website for key digital features and functionality"""
        try:
            features = {
                'online_booking': False,
                'class_scheduling': False,
                'membership_management': False,
                'payment_processing': False,
                'member_portal': False,
                'mobile_responsive': False,
                'ecommerce': False,
                'virtual_classes': False,
                'live_chat': False,
                'social_integration': False
            }
            
            feature_indicators = []
            missing_features = []
            
            if not website or not technologies:
                return {
                    'detected_features': features,
                    'feature_score': 0,
                    'feature_indicators': ['No website or technology data available'],
                    'missing_features': list(features.keys()),
                    'recommendations': ['Implement basic website with core gym features'],
                    'implemented_count': 0,
                    'total_features': len(features)
                }
            
            # Analyze technologies for feature detection
            tech_names = [tech.get('name', '').lower() for tech in technologies]
            tech_categories = [tech.get('category', '').lower() for tech in technologies]
            all_tech_text = ' '.join(tech_names + tech_categories)
            
            # Online booking detection
            booking_indicators = [
                'mindbody', 'zenplanner', 'wodify', 'glofox', 'teamup', 'acuity', 
                'calendly', 'schedulicity', 'booking', 'appointment', 'reserve'
            ]
            if any(indicator in all_tech_text for indicator in booking_indicators):
                features['online_booking'] = True
                feature_indicators.append('Online booking system detected')
            else:
                missing_features.append('online_booking')
            
            # Class scheduling detection
            scheduling_indicators = [
                'schedule', 'class', 'timetable', 'calendar', 'booking', 'mindbody',
                'zenplanner', 'wodify', 'glofox', 'teamup'
            ]
            if any(indicator in all_tech_text for indicator in scheduling_indicators):
                features['class_scheduling'] = True
                feature_indicators.append('Class scheduling system detected')
            else:
                missing_features.append('class_scheduling')
            
            # Payment processing detection
            payment_indicators = [
                'stripe', 'paypal', 'square', 'payment', 'billing', 'checkout',
                'ecommerce', 'shop', 'cart', 'braintree', 'authorize.net'
            ]
            if any(indicator in all_tech_text for indicator in payment_indicators):
                features['payment_processing'] = True
                feature_indicators.append('Payment processing system detected')
            else:
                missing_features.append('payment_processing')
            
            # Member portal/management detection
            member_indicators = [
                'member', 'login', 'account', 'portal', 'dashboard', 'profile',
                'mindbody', 'zenplanner', 'wodify', 'glofox'
            ]
            if any(indicator in all_tech_text for indicator in member_indicators):
                features['membership_management'] = True
                feature_indicators.append('Member management system detected')
            else:
                missing_features.append('membership_management')
            
            # Member portal detection (separate from management)
            portal_indicators = [
                'member portal', 'client portal', 'login', 'account access',
                'dashboard', 'member area', 'my account'
            ]
            if any(indicator in all_tech_text for indicator in portal_indicators):
                features['member_portal'] = True
                feature_indicators.append('Member portal detected')
            else:
                missing_features.append('member_portal')
            
            # Mobile responsiveness detection
            mobile_indicators = [
                'responsive', 'mobile', 'viewport', 'bootstrap', 'foundation',
                'flexbox', 'grid', 'media queries'
            ]
            if any(indicator in all_tech_text for indicator in mobile_indicators):
                features['mobile_responsive'] = True
                feature_indicators.append('Mobile responsive design detected')
            else:
                missing_features.append('mobile_responsive')
            
            # E-commerce detection
            ecommerce_indicators = [
                'woocommerce', 'shopify', 'magento', 'ecommerce', 'shop', 'cart',
                'product', 'merchandise', 'store', 'retail'
            ]
            if any(indicator in all_tech_text for indicator in ecommerce_indicators):
                features['ecommerce'] = True
                feature_indicators.append('E-commerce functionality detected')
            else:
                missing_features.append('ecommerce')
            
            # Virtual classes detection
            virtual_indicators = [
                'zoom', 'livestream', 'virtual', 'online classes', 'video',
                'streaming', 'webex', 'meet', 'live', 'remote'
            ]
            if any(indicator in all_tech_text for indicator in virtual_indicators):
                features['virtual_classes'] = True
                feature_indicators.append('Virtual classes capability detected')
            else:
                missing_features.append('virtual_classes')
            
            # Live chat detection
            chat_indicators = [
                'chat', 'intercom', 'zendesk', 'drift', 'crisp', 'tawk',
                'messenger', 'support', 'helpdesk'
            ]
            if any(indicator in all_tech_text for indicator in chat_indicators):
                features['live_chat'] = True
                feature_indicators.append('Live chat support detected')
            else:
                missing_features.append('live_chat')
            
            # Social media integration detection
            social_indicators = [
                'facebook', 'instagram', 'twitter', 'social', 'share',
                'youtube', 'tiktok', 'linkedin', 'social media'
            ]
            if any(indicator in all_tech_text for indicator in social_indicators):
                features['social_integration'] = True
                feature_indicators.append('Social media integration detected')
            else:
                missing_features.append('social_integration')
            
            # Calculate feature score (0-100)
            total_features = len(features)
            implemented_features = sum(1 for implemented in features.values() if implemented)
            feature_score = (implemented_features / total_features) * 100
            
            # Generate recommendations based on missing features
            recommendations = []
            if not features['online_booking']:
                recommendations.append('Implement online booking system (MindBody, Zen Planner, or similar)')
            if not features['payment_processing']:
                recommendations.append('Add online payment processing (Stripe, Square)')
            if not features['mobile_responsive']:
                recommendations.append('Upgrade to mobile-responsive website design')
            if not features['member_portal']:
                recommendations.append('Create member portal for account management')
            if not features['virtual_classes']:
                recommendations.append('Add virtual/online class capabilities')
            
            # Add priority recommendations for low-scoring websites
            if feature_score < 30:
                recommendations.insert(0, 'URGENT: Complete website overhaul needed - missing critical features')
            elif feature_score < 50:
                recommendations.insert(0, 'Major website improvements needed for competitive digital presence')
            
            return {
                'detected_features': features,
                'feature_score': round(feature_score, 1),
                'feature_indicators': feature_indicators,
                'missing_features': missing_features,
                'recommendations': recommendations,
                'implemented_count': implemented_features,
                'total_features': total_features
            }
            
        except Exception as e:
            logger.error(f"Error analyzing gym website features: {e}")
            return {
                'detected_features': {key: False for key in ['online_booking', 'class_scheduling', 'membership_management', 'payment_processing', 'member_portal', 'mobile_responsive', 'ecommerce', 'virtual_classes', 'live_chat', 'social_integration']},
                'feature_score': 0,
                'feature_indicators': ['Feature analysis failed'],
                'missing_features': ['Feature analysis error'],
                'recommendations': ['Website feature analysis could not be completed'],
                'implemented_count': 0,
                'total_features': 10
            }

    def _analyze_gym_mobile_app(self, business_name: str, website: str, detected_software: List[str]) -> Dict[str, Any]:
        """Analyze gym mobile app availability and quality"""
        try:
            app_analysis = {
                'has_mobile_app': False,
                'app_platforms': [],
                'app_quality_score': 0,
                'app_rating_ios': None,
                'app_rating_android': None,
                'app_quality_issues': [],
                'app_recommendations': [],
                'detection_method': 'software_analysis'
            }
            
            # Check if gym software indicates mobile app availability
            software_with_apps = {
                'mindbody': {'name': 'MindBody Connect', 'quality': 85},
                'zen_planner': {'name': 'Zen Planner', 'quality': 75},
                'wodify': {'name': 'Wodify', 'quality': 80},
                'glofox': {'name': 'Glofox', 'quality': 75},
                'teamup': {'name': 'TeamUp', 'quality': 70},
                'wellnessliving': {'name': 'WellnessLiving', 'quality': 75},
                'clubready': {'name': 'ClubReady', 'quality': 60},
                'pushpress': {'name': 'PushPress', 'quality': 65},
                'pike13': {'name': 'Pike13', 'quality': 70}
            }
            
            # Analyze detected software for mobile app capabilities
            detected_app_software = []
            total_quality = 0
            app_count = 0
            
            for software_name in detected_software:
                # Convert software name back to database key format
                software_key = software_name.lower().replace(' ', '_')
                if software_key in software_with_apps:
                    app_info = software_with_apps[software_key]
                    detected_app_software.append(app_info['name'])
                    total_quality += app_info['quality']
                    app_count += 1
                    app_analysis['has_mobile_app'] = True
                    
                    # Add platforms only once (avoid duplicates)
                    if 'iOS' not in app_analysis['app_platforms']:
                        app_analysis['app_platforms'].append('iOS')
                    if 'Android' not in app_analysis['app_platforms']:
                        app_analysis['app_platforms'].append('Android')
            
            # Calculate overall app quality score
            if app_count > 0:
                app_analysis['app_quality_score'] = round(total_quality / app_count, 1)
                
                # Provide quality assessment
                if app_analysis['app_quality_score'] >= 80:
                    app_analysis['app_recommendations'].append('Excellent mobile app solution detected')
                elif app_analysis['app_quality_score'] >= 70:
                    app_analysis['app_recommendations'].append('Good mobile app solution in use')
                elif app_analysis['app_quality_score'] >= 60:
                    app_analysis['app_recommendations'].append('Acceptable mobile app - consider improvements')
                else:
                    app_analysis['app_quality_issues'].append('Low-quality mobile app solution')
                    app_analysis['app_recommendations'].append('Consider upgrading to better mobile app platform')
            
            # Check for basic/generic solutions without good mobile apps
            basic_software = ['square', 'calendly', 'wordpress', 'stripe']
            has_only_basic = detected_software and all(any(basic in software_name.lower().replace(' ', '_') for basic in basic_software) for software_name in detected_software)
            
            if has_only_basic or not app_analysis['has_mobile_app']:
                app_analysis['app_quality_issues'].extend([
                    'No dedicated gym mobile app detected',
                    'Members likely cannot book classes via mobile app',
                    'Missing mobile-first member experience'
                ])
                app_analysis['app_recommendations'].extend([
                    'CRITICAL: Implement dedicated gym mobile app',
                    'Consider MindBody, Glofox, or Wodify for comprehensive mobile solutions',
                    'Mobile app essential for member retention and convenience'
                ])
            
            # Check for mobile responsiveness as fallback
            if not app_analysis['has_mobile_app']:
                # Look for mobile-responsive indicators in website technologies
                mobile_indicators = ['bootstrap', 'responsive', 'mobile', 'jquery_mobile']
                detected_software_text = ' '.join([name.lower().replace(' ', '_') for name in detected_software])
                has_mobile_web = any(indicator in detected_software_text for indicator in mobile_indicators)
                
                if has_mobile_web:
                    app_analysis['app_recommendations'].append('Mobile-responsive website detected, but dedicated app still recommended')
                else:
                    app_analysis['app_quality_issues'].append('Neither mobile app nor mobile-responsive website detected')
                    app_analysis['app_recommendations'].append('URGENT: Implement mobile-responsive website as minimum requirement')
            
            # Additional quality issues based on software age and capabilities
            outdated_software = ['abc_financial', 'perfect_gym']
            has_outdated = any(outdated in software_name.lower().replace(' ', '_') for software_name in detected_software for outdated in outdated_software)
            
            if has_outdated:
                app_analysis['app_quality_issues'].extend([
                    'Outdated software platform with poor mobile support',
                    'Mobile app likely has limited functionality'
                ])
                app_analysis['app_recommendations'].append('Upgrade to modern platform for better mobile experience')
            
            return app_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing gym mobile app: {e}")
            return {
                'has_mobile_app': False,
                'app_platforms': [],
                'app_quality_score': 0,
                'app_rating_ios': None,
                'app_rating_android': None,
                'app_quality_issues': ['Mobile app analysis failed'],
                'app_recommendations': ['Unable to analyze mobile app capabilities'],
                'detection_method': 'error'
            }

    def _calculate_digital_infrastructure_score(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive digital infrastructure score for gym"""
        try:
            # Initialize scoring components
            scoring_components = {
                'website_features': {'score': 0, 'weight': 0.35, 'max_score': 100},
                'mobile_app_quality': {'score': 0, 'weight': 0.25, 'max_score': 100},
                'online_booking': {'score': 0, 'weight': 0.20, 'max_score': 100},
                'member_experience': {'score': 0, 'weight': 0.20, 'max_score': 100}
            }
            
            # Website Features Score (35% weight)
            website_score = lead.get('gym_website_feature_score', 0)
            scoring_components['website_features']['score'] = website_score
            
            # Mobile App Quality Score (25% weight)
            mobile_app_score = lead.get('gym_mobile_app_quality_score', 0)
            scoring_components['mobile_app_quality']['score'] = mobile_app_score
            
            # Online Booking Capabilities Score (20% weight)
            booking_score = self._calculate_online_booking_score(lead)
            scoring_components['online_booking']['score'] = booking_score
            
            # Member Experience Score (20% weight)
            experience_score = self._calculate_member_experience_score(lead)
            scoring_components['member_experience']['score'] = experience_score
            
            # Calculate weighted overall score
            total_weighted_score = 0
            total_weight = 0
            
            for component, data in scoring_components.items():
                weighted_contribution = (data['score'] / data['max_score']) * data['weight'] * 100
                total_weighted_score += weighted_contribution
                total_weight += data['weight']
            
            overall_score = round(total_weighted_score / total_weight, 1)
            
            # Determine digital infrastructure tier
            if overall_score >= 80:
                tier = 'excellent'
                tier_description = 'Excellent digital infrastructure - comprehensive modern platform'
            elif overall_score >= 65:
                tier = 'good'
                tier_description = 'Good digital infrastructure - some areas for improvement'
            elif overall_score >= 45:
                tier = 'average'
                tier_description = 'Average digital infrastructure - significant gaps present'
            elif overall_score >= 25:
                tier = 'poor'
                tier_description = 'Poor digital infrastructure - major upgrades needed'
            else:
                tier = 'critical'
                tier_description = 'Critical digital infrastructure gaps - immediate action required'
            
            # Generate improvement recommendations
            recommendations = self._generate_infrastructure_recommendations(scoring_components, lead)
            
            # Calculate digital readiness for modern members
            digital_readiness = self._calculate_digital_readiness(scoring_components)
            
            return {
                'overall_score': overall_score,
                'tier': tier,
                'tier_description': tier_description,
                'component_scores': {
                    'website_features': website_score,
                    'mobile_app_quality': mobile_app_score,
                    'online_booking': booking_score,
                    'member_experience': experience_score
                },
                'weighted_contributions': {
                    comp: round((data['score'] / data['max_score']) * data['weight'] * 100, 1)
                    for comp, data in scoring_components.items()
                },
                'digital_readiness': digital_readiness,
                'improvement_recommendations': recommendations,
                'critical_gaps': self._identify_critical_gaps(scoring_components, lead),
                'competitive_analysis': self._assess_competitive_position(overall_score)
            }
            
        except Exception as e:
            logger.error(f"Error calculating digital infrastructure score: {e}")
            return {
                'overall_score': 0,
                'tier': 'error',
                'tier_description': 'Unable to calculate digital infrastructure score',
                'component_scores': {'website_features': 0, 'mobile_app_quality': 0, 'online_booking': 0, 'member_experience': 0},
                'weighted_contributions': {'website_features': 0, 'mobile_app_quality': 0, 'online_booking': 0, 'member_experience': 0},
                'digital_readiness': 0,
                'improvement_recommendations': ['Digital infrastructure analysis failed'],
                'critical_gaps': ['Analysis error'],
                'competitive_analysis': 'Unable to assess competitive position'
            }
    
    def _calculate_online_booking_score(self, lead: Dict[str, Any]) -> float:
        """Calculate online booking capabilities score"""
        score = 0
        
        # Check if online booking is available
        website_features = lead.get('gym_website_features', {})
        if website_features.get('online_booking', False):
            score += 50  # Base score for having online booking
            
            # Bonus for comprehensive booking features
            if website_features.get('class_scheduling', False):
                score += 20
            if website_features.get('membership_management', False):
                score += 15
            if website_features.get('payment_processing', False):
                score += 15
        
        # Check for specialized gym software with booking
        detected_software = lead.get('gym_software_detected', [])
        booking_software = ['MindBody', 'Zen Planner', 'Wodify', 'Glofox', 'TeamUp', 'Acuity Scheduling', 'Calendly']
        
        has_booking_software = any(software in detected_software for software in booking_software)
        if has_booking_software:
            score = max(score, 60)  # Minimum score if booking software detected
            
            # Premium booking software bonus
            premium_booking = ['MindBody', 'Glofox', 'Wodify']
            if any(software in detected_software for software in premium_booking):
                score += 20
        
        # Penalties for poor implementation
        mobile_app_available = lead.get('gym_mobile_app_available', False)
        if not mobile_app_available and score > 0:
            score -= 15  # Penalty for no mobile booking
        
        return min(100, max(0, score))
    
    def _calculate_member_experience_score(self, lead: Dict[str, Any]) -> float:
        """Calculate overall member digital experience score"""
        score = 0
        
        # Website user experience factors
        website_features = lead.get('gym_website_features', {})
        mobile_score = lead.get('mobile_score', 0)
        
        # Mobile responsiveness (critical for member experience)
        if website_features.get('mobile_responsive', False):
            score += 25
        elif mobile_score >= 60:
            score += 15  # Partial credit for decent mobile performance
        
        # Member portal and self-service
        if website_features.get('member_portal', False):
            score += 20
        
        # Communication and engagement
        if website_features.get('live_chat', False):
            score += 10
        if website_features.get('social_integration', False):
            score += 10
        
        # Modern features
        if website_features.get('virtual_classes', False):
            score += 15  # Important post-COVID feature
        if website_features.get('ecommerce', False):
            score += 10
        
        # Mobile app experience
        mobile_app_score = lead.get('gym_mobile_app_quality_score', 0)
        if mobile_app_score > 0:
            score += min(20, mobile_app_score * 0.2)  # Up to 20 points from mobile app
        
        # Technology age factor
        tech_age_score = lead.get('technology_age_score', 70)
        if tech_age_score < 50:
            score -= 15  # Penalty for outdated technology
        elif tech_age_score > 80:
            score += 5   # Bonus for modern technology
        
        return min(100, max(0, round(score, 1)))
    
    def _generate_infrastructure_recommendations(self, scoring_components: Dict[str, Any], lead: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations for digital infrastructure improvements"""
        recommendations = []
        
        # Analyze each component for improvement opportunities
        website_score = scoring_components['website_features']['score']
        mobile_score = scoring_components['mobile_app_quality']['score']
        booking_score = scoring_components['online_booking']['score']
        experience_score = scoring_components['member_experience']['score']
        
        # Critical improvements (score < 30)
        if website_score < 30:
            recommendations.append("CRITICAL: Website overhaul needed - implement modern gym website with core features")
        if mobile_score < 30:
            recommendations.append("CRITICAL: Mobile app essential - 80% of members expect mobile booking and account access")
        if booking_score < 30:
            recommendations.append("CRITICAL: Online booking system required - manual scheduling loses members")
        
        # High priority improvements (score < 50)
        if website_score < 50:
            recommendations.append("HIGH: Upgrade website features - add member portal, class schedules, and payment processing")
        if mobile_score < 50:
            recommendations.append("HIGH: Implement dedicated gym mobile app for member retention")
        if booking_score < 50:
            recommendations.append("HIGH: Improve online booking system - integrate with mobile app and payment processing")
        if experience_score < 50:
            recommendations.append("HIGH: Enhance member digital experience - mobile responsiveness and self-service features")
        
        # Medium priority improvements (score < 70)
        if website_score < 70:
            recommendations.append("MEDIUM: Add advanced website features - virtual classes, e-commerce, social integration")
        if mobile_score < 70:
            recommendations.append("MEDIUM: Upgrade mobile app platform for better member experience")
        if experience_score < 70:
            recommendations.append("MEDIUM: Implement member communication tools - live chat, notifications, community features")
        
        # Software-specific recommendations
        detected_software = lead.get('gym_software_detected', [])
        if not detected_software or all('WordPress' in software or 'Square' in software or 'Calendly' in software for software in detected_software):
            recommendations.append("Consider comprehensive gym management software (MindBody, Glofox, or Zen Planner)")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _identify_critical_gaps(self, scoring_components: Dict[str, Any], lead: Dict[str, Any]) -> List[str]:
        """Identify critical gaps in digital infrastructure"""
        gaps = []
        
        # Check for fundamental missing components
        if scoring_components['website_features']['score'] < 40:
            gaps.append("Website lacks essential gym features (scheduling, payments, member management)")
        
        if scoring_components['mobile_app_quality']['score'] < 30:
            gaps.append("No mobile app or poor mobile experience for members")
        
        if scoring_components['online_booking']['score'] < 40:
            gaps.append("Limited or no online booking capabilities")
        
        # Check for modern member expectations
        website_features = lead.get('gym_website_features', {})
        if not website_features.get('mobile_responsive', False):
            gaps.append("Website not mobile-responsive (critical for member acquisition)")
        
        if not website_features.get('payment_processing', False):
            gaps.append("No online payment processing (limits member convenience)")
        
        # Technology age issues
        tech_age_score = lead.get('technology_age_score', 70)
        if tech_age_score < 40:
            gaps.append("Outdated technology stack affecting performance and security")
        
        # Software quality issues
        gym_software_quality = lead.get('gym_software_quality_score', 50)
        if gym_software_quality < 40:
            gaps.append("Poor quality or outdated gym management software")
        
        return gaps
    
    def _calculate_digital_readiness(self, scoring_components: Dict[str, Any]) -> int:
        """Calculate readiness for modern digital-first members"""
        # Weight components for digital readiness (different from overall scoring)
        mobile_weight = 0.4   # Mobile is critical for digital readiness
        booking_weight = 0.3  # Online booking essential
        experience_weight = 0.2  # User experience important
        website_weight = 0.1  # Website less critical if mobile is excellent
        
        readiness = (
            scoring_components['mobile_app_quality']['score'] * mobile_weight +
            scoring_components['online_booking']['score'] * booking_weight +
            scoring_components['member_experience']['score'] * experience_weight +
            scoring_components['website_features']['score'] * website_weight
        )
        
        return round(readiness)
    
    def _assess_competitive_position(self, overall_score: float) -> str:
        """Assess competitive position based on digital infrastructure score"""
        if overall_score >= 85:
            return "Industry leader - digital infrastructure exceeds member expectations"
        elif overall_score >= 70:
            return "Competitive - good digital infrastructure with room for optimization"
        elif overall_score >= 55:
            return "Below average - digital infrastructure gaps may impact member acquisition"
        elif overall_score >= 35:
            return "Falling behind - significant digital infrastructure improvements needed"
        else:
            return "Critical disadvantage - digital infrastructure far below industry standards"
    
    def _analyze_gym_pain_factors(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze gym-specific pain factors for comprehensive scoring"""
        pain_factors = {
            'operational_inefficiencies': [],
            'member_retention_risks': [],
            'competitive_disadvantages': [],
            'revenue_loss_factors': [],
            'growth_limitations': [],
            'pain_score': 0,
            'primary_pain_category': '',
            'urgency_level': 'low'
        }
        
        try:
            # Get relevant data
            digital_score = lead.get('digital_infrastructure_score', 50)
            website_features = lead.get('gym_website_features', {})
            mobile_app = lead.get('gym_mobile_app', {})
            gym_software = lead.get('gym_software_detected', [])
            mobile_score = lead.get('mobile_score', 70)
            tech_age_score = lead.get('technology_age_score', 70)
            
            # Operational Inefficiencies
            if not website_features.get('online_booking', False):
                pain_factors['operational_inefficiencies'].append({
                    'factor': 'Manual booking process',
                    'impact': 'Staff spends 15-20 hours/week on phone scheduling',
                    'severity': 8
                })
            
            if not website_features.get('payment_processing', False):
                pain_factors['operational_inefficiencies'].append({
                    'factor': 'Manual payment collection',
                    'impact': 'Higher admin costs and delayed revenue',
                    'severity': 7
                })
            
            if not gym_software or all(sw in ['WordPress', 'Square', 'Calendly'] for sw in gym_software):
                pain_factors['operational_inefficiencies'].append({
                    'factor': 'No integrated gym management system',
                    'impact': 'Multiple disconnected tools increase errors and time',
                    'severity': 9
                })
            
            # Member Retention Risks
            if not mobile_app.get('has_app', False):
                pain_factors['member_retention_risks'].append({
                    'factor': 'No mobile app for members',
                    'impact': '25% higher churn rate vs gyms with apps',
                    'severity': 9
                })
            
            if not website_features.get('member_portal', False):
                pain_factors['member_retention_risks'].append({
                    'factor': 'No self-service member portal',
                    'impact': 'Members can\'t manage accounts 24/7',
                    'severity': 7
                })
            
            if mobile_score < 60:
                pain_factors['member_retention_risks'].append({
                    'factor': 'Poor mobile website experience',
                    'impact': '40% of prospects abandon slow mobile sites',
                    'severity': 8
                })
            
            # Competitive Disadvantages
            if digital_score < 50:
                pain_factors['competitive_disadvantages'].append({
                    'factor': 'Below-average digital infrastructure',
                    'impact': 'Losing tech-savvy millennials to modern gyms',
                    'severity': 8
                })
            
            if not website_features.get('virtual_classes', False):
                pain_factors['competitive_disadvantages'].append({
                    'factor': 'No virtual/hybrid fitness options',
                    'impact': 'Missing 30% of market seeking flexible options',
                    'severity': 6
                })
            
            if tech_age_score < 50:
                pain_factors['competitive_disadvantages'].append({
                    'factor': 'Outdated technology stack',
                    'impact': 'Appears unprofessional vs modern competitors',
                    'severity': 7
                })
            
            # Revenue Loss Factors
            if not website_features.get('ecommerce', False):
                pain_factors['revenue_loss_factors'].append({
                    'factor': 'No online merchandise/supplement sales',
                    'impact': 'Missing $500-2000/month ancillary revenue',
                    'severity': 5
                })
            
            if not website_features.get('class_scheduling', False):
                pain_factors['revenue_loss_factors'].append({
                    'factor': 'No online class booking',
                    'impact': 'Losing drop-in revenue from convenience seekers',
                    'severity': 7
                })
            
            if mobile_app.get('quality_score', 0) < 50:
                pain_factors['revenue_loss_factors'].append({
                    'factor': 'Poor quality mobile experience',
                    'impact': 'Reduced member engagement and upgrades',
                    'severity': 6
                })
            
            # Growth Limitations
            if not website_features.get('social_integration', False):
                pain_factors['growth_limitations'].append({
                    'factor': 'No social media integration',
                    'impact': 'Missing viral marketing and referrals',
                    'severity': 5
                })
            
            if not website_features.get('live_chat', False):
                pain_factors['growth_limitations'].append({
                    'factor': 'No instant communication channel',
                    'impact': 'Losing 20% of prospects who want immediate answers',
                    'severity': 6
                })
            
            # Calculate total pain score
            all_pain_items = (
                pain_factors['operational_inefficiencies'] +
                pain_factors['member_retention_risks'] +
                pain_factors['competitive_disadvantages'] +
                pain_factors['revenue_loss_factors'] +
                pain_factors['growth_limitations']
            )
            
            if all_pain_items:
                # Average severity weighted by category importance
                operational_weight = 0.25
                retention_weight = 0.30
                competitive_weight = 0.20
                revenue_weight = 0.15
                growth_weight = 0.10
                
                operational_avg = sum(p['severity'] for p in pain_factors['operational_inefficiencies']) / max(1, len(pain_factors['operational_inefficiencies'])) if pain_factors['operational_inefficiencies'] else 0
                retention_avg = sum(p['severity'] for p in pain_factors['member_retention_risks']) / max(1, len(pain_factors['member_retention_risks'])) if pain_factors['member_retention_risks'] else 0
                competitive_avg = sum(p['severity'] for p in pain_factors['competitive_disadvantages']) / max(1, len(pain_factors['competitive_disadvantages'])) if pain_factors['competitive_disadvantages'] else 0
                revenue_avg = sum(p['severity'] for p in pain_factors['revenue_loss_factors']) / max(1, len(pain_factors['revenue_loss_factors'])) if pain_factors['revenue_loss_factors'] else 0
                growth_avg = sum(p['severity'] for p in pain_factors['growth_limitations']) / max(1, len(pain_factors['growth_limitations'])) if pain_factors['growth_limitations'] else 0
                
                weighted_score = (
                    operational_avg * operational_weight +
                    retention_avg * retention_weight +
                    competitive_avg * competitive_weight +
                    revenue_avg * revenue_weight +
                    growth_avg * growth_weight
                )
                
                pain_factors['pain_score'] = round(weighted_score * 10)  # Convert to 0-100 scale
                
                # Determine primary pain category
                category_scores = {
                    'operational_inefficiencies': operational_avg,
                    'member_retention_risks': retention_avg,
                    'competitive_disadvantages': competitive_avg,
                    'revenue_loss_factors': revenue_avg,
                    'growth_limitations': growth_avg
                }
                
                if category_scores:
                    pain_factors['primary_pain_category'] = max(category_scores, key=category_scores.get)
                
                # Determine urgency level
                if pain_factors['pain_score'] >= 70:
                    pain_factors['urgency_level'] = 'critical'
                elif pain_factors['pain_score'] >= 50:
                    pain_factors['urgency_level'] = 'high'
                elif pain_factors['pain_score'] >= 30:
                    pain_factors['urgency_level'] = 'medium'
                else:
                    pain_factors['urgency_level'] = 'low'
            
            # Add summary metrics
            pain_factors['total_pain_points'] = len(all_pain_items)
            pain_factors['critical_issues'] = len([p for p in all_pain_items if p['severity'] >= 8])
            pain_factors['high_impact_issues'] = len([p for p in all_pain_items if p['severity'] >= 7])
            
            return pain_factors
            
        except Exception as e:
            logger.error(f"Error analyzing gym pain factors: {e}")
            return pain_factors
    
    def _apply_gym_size_and_model_scoring(self, lead: Dict[str, Any], pain_factors: Dict[str, Any]) -> Dict[str, Any]:
        """Apply gym size and business model-specific adjustments to pain scoring"""
        try:
            # Get gym size and business model data
            gym_size = lead.get('gym_size_estimate', 'medium')
            gym_type = lead.get('gym_type', 'traditional_gym')
            
            # Initialize adjustment factors
            size_adjustments = {
                'pain_multiplier': 1.0,
                'critical_thresholds': {},
                'size_specific_pain_factors': [],
                'model_specific_pain_factors': [],
                'adjusted_pain_score': pain_factors['pain_score'],
                'size_context': '',
                'model_context': ''
            }
            
            # Size-specific pain adjustments
            if gym_size == 'large':
                # Large gyms have different pain points
                size_adjustments['pain_multiplier'] = 1.2  # Higher stakes
                size_adjustments['critical_thresholds'] = {
                    'min_mobile_score': 70,  # Higher expectations
                    'min_digital_infrastructure': 65,
                    'required_features': ['online_booking', 'member_portal', 'payment_processing', 'mobile_app']
                }
                size_adjustments['size_context'] = 'Large gym with high member expectations'
                
                # Check for large gym-specific pain
                # Only add if there are actual operational issues
                operational_issues = pain_factors.get('operational_inefficiencies', [])
                if len(operational_issues) == 0 and not lead.get('gym_software_detected'):
                    size_adjustments['size_specific_pain_factors'].append({
                        'factor': 'Scale inefficiencies',
                        'impact': 'Managing 1000+ members manually costs $50K+ annually',
                        'severity': 9
                    })
                
                if lead.get('gym_mobile_app', {}).get('has_app', False) == False:
                    size_adjustments['size_specific_pain_factors'].append({
                        'factor': 'No mobile app for large facility',
                        'impact': 'Losing 30%+ of millennial/Gen-Z prospects',
                        'severity': 10
                    })
                
            elif gym_size == 'small':
                # Small gyms have different pain thresholds
                size_adjustments['pain_multiplier'] = 0.8  # Lower absolute impact
                size_adjustments['critical_thresholds'] = {
                    'min_mobile_score': 50,  # Lower threshold
                    'min_digital_infrastructure': 40,
                    'required_features': ['online_booking', 'payment_processing']  # Fewer requirements
                }
                size_adjustments['size_context'] = 'Small gym with focused member base'
                
                # Small gym-specific opportunities
                if not lead.get('gym_website_features', {}).get('social_integration', False):
                    size_adjustments['size_specific_pain_factors'].append({
                        'factor': 'Missing community building tools',
                        'impact': 'Small gyms thrive on community - missing 40% growth potential',
                        'severity': 8
                    })
                
            else:  # medium
                size_adjustments['pain_multiplier'] = 1.0
                size_adjustments['critical_thresholds'] = {
                    'min_mobile_score': 60,
                    'min_digital_infrastructure': 50,
                    'required_features': ['online_booking', 'member_portal', 'payment_processing']
                }
                size_adjustments['size_context'] = 'Medium gym balancing growth and efficiency'
            
            # Business model-specific adjustments
            model_multipliers = {
                'boutique_fitness': 1.3,  # High touch, high expectations
                'crossfit': 1.2,          # Community-focused, tech-savvy members
                'personal_training': 0.7,  # Lower tech needs
                'martial_arts': 0.8,      # Traditional, less tech-dependent
                'yoga_studio': 1.1,       # Wellness-focused, expect good UX
                'boxing_gym': 0.9,        # Traditional sport focus
                'dance_studio': 0.85,     # Schedule-focused
                'traditional_gym': 1.0,   # Baseline
                'recreation_center': 1.15  # Public expectations for accessibility
            }
            
            model_multiplier = model_multipliers.get(gym_type, 1.0)
            size_adjustments['model_multiplier'] = model_multiplier
            
            # Model-specific pain factors
            if gym_type == 'boutique_fitness':
                size_adjustments['model_context'] = 'Boutique fitness with premium expectations'
                if lead.get('mobile_score', 100) < 80:
                    size_adjustments['model_specific_pain_factors'].append({
                        'factor': 'Subpar mobile experience for boutique',
                        'impact': 'Premium clients expect premium digital experience',
                        'severity': 9
                    })
                    
            elif gym_type == 'crossfit':
                size_adjustments['model_context'] = 'CrossFit box with community focus'
                if not lead.get('gym_website_features', {}).get('social_integration', False):
                    size_adjustments['model_specific_pain_factors'].append({
                        'factor': 'No community features for CrossFit',
                        'impact': 'CrossFit thrives on community - missing key differentiator',
                        'severity': 8
                    })
                    
            elif gym_type == 'yoga_studio':
                size_adjustments['model_context'] = 'Yoga studio with wellness focus'
                if not lead.get('gym_website_features', {}).get('class_scheduling', False):
                    size_adjustments['model_specific_pain_factors'].append({
                        'factor': 'No online class scheduling for yoga',
                        'impact': 'Yoga students plan ahead - losing convenience-seekers',
                        'severity': 9
                    })
            
            # Calculate adjusted pain score
            base_pain_score = pain_factors['pain_score']
            
            # Add size and model-specific pain factors
            additional_pain_points = (
                size_adjustments['size_specific_pain_factors'] + 
                size_adjustments['model_specific_pain_factors']
            )
            
            if additional_pain_points:
                # Only add additional pain if base pain is already significant
                # This prevents low-pain gyms from being flagged just because they're large
                if base_pain_score >= 30:
                    additional_severity = sum(p['severity'] for p in additional_pain_points) / len(additional_pain_points)
                    additional_pain_contribution = additional_severity * 5  # Convert to 0-100 scale
                    base_pain_score = (base_pain_score * 0.8) + (additional_pain_contribution * 0.2)
                else:
                    # For low base pain, only slightly increase based on additional factors
                    additional_severity = sum(p['severity'] for p in additional_pain_points) / len(additional_pain_points)
                    additional_pain_contribution = additional_severity * 2  # Smaller contribution for low pain
                    base_pain_score = base_pain_score + (additional_pain_contribution * 0.1)
            
            # Apply size and model multipliers
            adjusted_score = base_pain_score * size_adjustments['pain_multiplier'] * model_multiplier
            size_adjustments['adjusted_pain_score'] = round(min(100, adjusted_score))
            
            # Recalculate urgency based on adjusted score
            if size_adjustments['adjusted_pain_score'] >= 70:
                size_adjustments['adjusted_urgency'] = 'critical'
            elif size_adjustments['adjusted_pain_score'] >= 50:
                size_adjustments['adjusted_urgency'] = 'high'
            elif size_adjustments['adjusted_pain_score'] >= 30:
                size_adjustments['adjusted_urgency'] = 'medium'
            else:
                size_adjustments['adjusted_urgency'] = 'low'
            
            # Check against critical thresholds
            threshold_violations = []
            
            mobile_score = lead.get('mobile_score', 100)
            if mobile_score < size_adjustments['critical_thresholds']['min_mobile_score']:
                threshold_violations.append(f"Mobile score ({mobile_score}) below threshold for {gym_size} gym")
            
            digital_score = lead.get('digital_infrastructure_score', 100)
            if digital_score < size_adjustments['critical_thresholds']['min_digital_infrastructure']:
                threshold_violations.append(f"Digital infrastructure ({digital_score}) below threshold for {gym_size} gym")
            
            # Check required features
            website_features = lead.get('gym_website_features', {})
            for feature in size_adjustments['critical_thresholds']['required_features']:
                if not website_features.get(feature, False):
                    threshold_violations.append(f"Missing critical feature for {gym_size} gym: {feature}")
            
            size_adjustments['threshold_violations'] = threshold_violations
            
            # If there are critical violations, ensure urgency is at least 'high'
            if threshold_violations and size_adjustments['adjusted_urgency'] == 'medium':
                size_adjustments['adjusted_urgency'] = 'high'
            
            return size_adjustments
            
        except Exception as e:
            logger.error(f"Error applying gym size and model scoring: {e}")
            return {
                'pain_multiplier': 1.0,
                'model_multiplier': 1.0,
                'adjusted_pain_score': pain_factors.get('pain_score', 0),
                'adjusted_urgency': pain_factors.get('urgency_level', 'low'),
                'error': str(e)
            }
    
    def _apply_gym_specific_red_green_classification(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Apply gym-specific RED/GREEN classification based on comprehensive analysis"""
        try:
            # Extract all relevant scores and factors
            gym_adjusted_pain_score = lead.get('gym_adjusted_pain_score', 50)
            gym_adjusted_urgency = lead.get('gym_adjusted_urgency', 'medium')
            digital_infrastructure_score = lead.get('gym_digital_infrastructure_score', 50)
            digital_tier = lead.get('gym_digital_infrastructure_tier', 'Poor')
            software_quality_score = lead.get('gym_software_quality_score', 50)
            website_feature_score = lead.get('gym_website_feature_score', 50)
            mobile_app_quality = lead.get('gym_mobile_app_quality_score', 0)
            mobile_score = lead.get('mobile_score', 50)
            gym_size = lead.get('gym_size_estimate', 'medium')
            gym_type = lead.get('gym_type', 'traditional_gym')
            threshold_violations = lead.get('gym_threshold_violations', [])
            
            # Initialize classification data
            classification_data = {
                'gym_classification': 'green',
                'gym_classification_confidence': 'high',
                'gym_classification_reasons': [],
                'gym_action_priority': 'low',
                'gym_sales_readiness': 'not_ready'
            }
            
            # Define RED criteria specific to gyms
            red_criteria = []
            yellow_criteria = []
            
            # 1. Adjusted pain score criteria (most important)
            if gym_adjusted_pain_score >= 70:
                red_criteria.append({
                    'factor': 'High gym-specific pain score',
                    'detail': f'Adjusted pain score of {gym_adjusted_pain_score:.1f} indicates severe operational challenges',
                    'weight': 'critical'
                })
            elif gym_adjusted_pain_score >= 50:
                yellow_criteria.append({
                    'factor': 'Moderate gym-specific pain score',
                    'detail': f'Adjusted pain score of {gym_adjusted_pain_score:.1f} shows significant improvement opportunities',
                    'weight': 'important'
                })
            
            # 2. Urgency level criteria
            if gym_adjusted_urgency == 'critical':
                red_criteria.append({
                    'factor': 'Critical urgency level',
                    'detail': 'Multiple critical pain points requiring immediate attention',
                    'weight': 'critical'
                })
            elif gym_adjusted_urgency == 'high':
                yellow_criteria.append({
                    'factor': 'High urgency level',
                    'detail': 'Several important pain points that need addressing',
                    'weight': 'important'
                })
            
            # 3. Digital infrastructure criteria
            if digital_tier in ['Very Poor', 'Poor'] or digital_infrastructure_score < 40:
                red_criteria.append({
                    'factor': 'Poor digital infrastructure',
                    'detail': f'{digital_tier} tier ({digital_infrastructure_score}/100) - severely behind competitors',
                    'weight': 'critical'
                })
            elif digital_tier == 'Fair' or digital_infrastructure_score < 60:
                yellow_criteria.append({
                    'factor': 'Fair digital infrastructure',
                    'detail': f'{digital_tier} tier ({digital_infrastructure_score}/100) - needs modernization',
                    'weight': 'moderate'
                })
            
            # 4. Mobile performance for gyms (critical for member experience)
            if mobile_score < 50:
                red_criteria.append({
                    'factor': 'Poor mobile performance',
                    'detail': f'Mobile score {mobile_score}/100 - critical for member engagement',
                    'weight': 'critical'
                })
            elif mobile_score < 70:
                yellow_criteria.append({
                    'factor': 'Subpar mobile performance',
                    'detail': f'Mobile score {mobile_score}/100 - below member expectations',
                    'weight': 'important'
                })
            
            # 5. Gym software quality
            if software_quality_score < 40:
                red_criteria.append({
                    'factor': 'Poor gym management software',
                    'detail': f'Software quality score {software_quality_score}/100 - major operational inefficiencies',
                    'weight': 'critical'
                })
            elif software_quality_score < 60:
                yellow_criteria.append({
                    'factor': 'Outdated gym management software',
                    'detail': f'Software quality score {software_quality_score}/100 - limiting growth potential',
                    'weight': 'important'
                })
            
            # 6. Critical threshold violations
            if len(threshold_violations) >= 3:
                red_criteria.append({
                    'factor': 'Multiple critical violations',
                    'detail': f'{len(threshold_violations)} critical thresholds violated for {gym_size} {gym_type}',
                    'weight': 'critical'
                })
            elif len(threshold_violations) >= 1:
                yellow_criteria.append({
                    'factor': 'Critical threshold violations',
                    'detail': f'{len(threshold_violations)} threshold(s) below expectations for {gym_size} {gym_type}',
                    'weight': 'important'
                })
            
            # 7. Website feature completeness for gyms
            if website_feature_score < 30:
                red_criteria.append({
                    'factor': 'Missing critical website features',
                    'detail': f'Only {website_feature_score}% of essential gym website features implemented',
                    'weight': 'critical'
                })
            elif website_feature_score < 60:
                yellow_criteria.append({
                    'factor': 'Incomplete website features',
                    'detail': f'{website_feature_score}% of gym website features - missing key member tools',
                    'weight': 'moderate'
                })
            
            # 8. Mobile app availability (important for modern gyms)
            has_mobile_app = lead.get('gym_mobile_app', {}).get('has_app', False)
            if gym_size == 'large' and not has_mobile_app:
                red_criteria.append({
                    'factor': 'No mobile app for large gym',
                    'detail': 'Large gyms require mobile apps for competitive member experience',
                    'weight': 'critical'
                })
            elif gym_type in ['boutique_fitness', 'crossfit'] and not has_mobile_app:
                yellow_criteria.append({
                    'factor': 'No mobile app for tech-forward gym type',
                    'detail': f'{gym_type.replace("_", " ").title()} typically benefits from mobile apps',
                    'weight': 'important'
                })
            
            # Determine final classification
            critical_red_factors = sum(1 for r in red_criteria if r['weight'] == 'critical')
            total_red_factors = len(red_criteria)
            total_yellow_factors = len(yellow_criteria)
            
            if critical_red_factors >= 2 or total_red_factors >= 3:
                classification_data['gym_classification'] = 'red'
                classification_data['gym_action_priority'] = 'urgent'
                classification_data['gym_sales_readiness'] = 'hot_lead'
                classification_data['gym_classification_reasons'] = [r['detail'] for r in red_criteria[:5]]  # Top 5 reasons
                
                # Adjust confidence based on number of factors
                if critical_red_factors >= 3:
                    classification_data['gym_classification_confidence'] = 'very_high'
                elif critical_red_factors >= 2:
                    classification_data['gym_classification_confidence'] = 'high'
                else:
                    classification_data['gym_classification_confidence'] = 'medium'
                    
            elif total_red_factors >= 1 or total_yellow_factors >= 3:
                classification_data['gym_classification'] = 'yellow'
                classification_data['gym_action_priority'] = 'medium'
                classification_data['gym_sales_readiness'] = 'warm_lead'
                
                # Combine top red and yellow reasons
                reasons = [r['detail'] for r in red_criteria[:2]]
                reasons.extend([y['detail'] for y in yellow_criteria[:3-len(reasons)]])
                classification_data['gym_classification_reasons'] = reasons[:5]
                
                # Confidence adjustment
                if total_red_factors >= 1:
                    classification_data['gym_classification_confidence'] = 'high'
                else:
                    classification_data['gym_classification_confidence'] = 'medium'
                    
            else:
                classification_data['gym_classification'] = 'green'
                classification_data['gym_action_priority'] = 'low'
                classification_data['gym_sales_readiness'] = 'not_ready'
                classification_data['gym_classification_reasons'] = ['Digital infrastructure meets current needs', 'No critical pain points identified']
                classification_data['gym_classification_confidence'] = 'high'
            
            # Add classification summary
            classification_data['gym_classification_summary'] = self._generate_classification_summary(
                classification_data['gym_classification'],
                gym_type,
                gym_size,
                red_criteria,
                yellow_criteria
            )
            
            # Update lead with classification data
            for key, value in classification_data.items():
                lead[key] = value
            
            # Override general status with gym-specific classification if more severe
            if classification_data['gym_classification'] == 'red' and lead.get('status') != 'error':
                lead['status'] = 'red'
                lead['status_source'] = 'gym_specific_classification'
            elif classification_data['gym_classification'] == 'yellow' and lead.get('status') == 'green':
                lead['status'] = 'yellow'
                lead['status_source'] = 'gym_specific_classification'
            
            logger.info(f"Gym classification for {lead['business_name']} ({gym_size} {gym_type}): "
                       f"{classification_data['gym_classification'].upper()} "
                       f"(confidence: {classification_data['gym_classification_confidence']}, "
                       f"priority: {classification_data['gym_action_priority']})")
            
            return lead
            
        except Exception as e:
            logger.error(f"Error in gym-specific classification: {e}")
            lead['gym_classification'] = 'unknown'
            lead['gym_classification_confidence'] = 'low'
            lead['gym_classification_reasons'] = ['Classification analysis failed']
            lead['gym_action_priority'] = 'unknown'
            lead['gym_sales_readiness'] = 'unknown'
            return lead
    
    def _generate_classification_summary(self, classification: str, gym_type: str, gym_size: str,
                                       red_criteria: List[Dict], yellow_criteria: List[Dict]) -> str:
        """Generate a human-readable classification summary"""
        gym_type_display = gym_type.replace('_', ' ').title()
        
        if classification == 'red':
            severity = "urgent" if len(red_criteria) >= 3 else "high"
            return (f"This {gym_size} {gym_type_display} has {severity} need for modern gym management solutions. "
                   f"With {len(red_criteria)} critical issues identified, they are experiencing significant "
                   f"operational inefficiencies and member experience challenges that directly impact revenue.")
        
        elif classification == 'yellow':
            return (f"This {gym_size} {gym_type_display} shows moderate potential for improvement. "
                   f"While functioning, they have {len(red_criteria) + len(yellow_criteria)} areas where modern "
                   f"gym software could enhance operations and member satisfaction.")
        
        else:
            return (f"This {gym_size} {gym_type_display} appears to have adequate digital infrastructure "
                   f"for their current needs. They may not be immediately interested in new solutions.")
    
    def _qualify_gym_size_and_revenue(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Qualify leads based on gym size and revenue potential for sales viability"""
        try:
            qualification_data = {
                'size_qualification': 'unqualified',
                'revenue_potential': 'low',
                'estimated_monthly_revenue': 0,
                'estimated_member_count': 0,
                'viability_score': 0,  # 0-100
                'qualification_reasons': [],
                'disqualification_reasons': [],
                'size_tier': 'unknown',
                'revenue_tier': 'unknown'
            }
            
            # Get gym size and type
            gym_size = lead.get('gym_size_estimate', 'unknown')
            gym_type = lead.get('gym_type', 'unknown')
            gym_services = lead.get('gym_services', [])
            pricing_indicators = lead.get('gym_pricing_indicators', [])
            reviews_count = lead.get('reviews_count', 0)
            rating = lead.get('rating', 0)
            
            # Estimate member count based on gym size
            member_count_ranges = {
                'large': {'min': 1000, 'max': 5000, 'typical': 2500},
                'medium': {'min': 300, 'max': 1000, 'typical': 600},
                'small': {'min': 50, 'max': 300, 'typical': 150},
                'unknown': {'min': 100, 'max': 500, 'typical': 250}
            }
            
            size_data = member_count_ranges.get(gym_size, member_count_ranges['unknown'])
            
            # Adjust member count based on gym type
            type_multipliers = {
                'crossfit': 0.4,  # Smaller member base but higher revenue per member
                'boutique_fitness': 0.5,
                'yoga_studio': 0.6,
                'martial_arts': 0.7,
                'personal_training': 0.2,  # Very small member base
                'traditional_gym': 1.0,
                'fitness_center': 1.0,
                'health_club': 1.2
            }
            
            type_multiplier = type_multipliers.get(gym_type, 1.0)
            estimated_members = int(size_data['typical'] * type_multiplier)
            
            # Adjust based on review count as a proxy for popularity
            if reviews_count > 500:
                estimated_members = int(estimated_members * 1.3)
            elif reviews_count > 200:
                estimated_members = int(estimated_members * 1.1)
            elif reviews_count < 50:
                estimated_members = int(estimated_members * 0.7)
            
            qualification_data['estimated_member_count'] = estimated_members
            
            # Estimate monthly revenue per member based on gym type and pricing indicators
            revenue_per_member = {
                'crossfit': {'low': 100, 'mid': 150, 'high': 200},
                'boutique_fitness': {'low': 80, 'mid': 120, 'high': 180},
                'personal_training': {'low': 200, 'mid': 400, 'high': 600},
                'yoga_studio': {'low': 60, 'mid': 90, 'high': 130},
                'martial_arts': {'low': 70, 'mid': 100, 'high': 150},
                'traditional_gym': {'low': 20, 'mid': 40, 'high': 60},
                'fitness_center': {'low': 25, 'mid': 45, 'high': 70},
                'health_club': {'low': 50, 'mid': 80, 'high': 120}
            }
            
            # Determine pricing tier
            if 'premium' in pricing_indicators or 'high_price' in pricing_indicators:
                pricing_tier = 'high'
            elif 'budget_friendly' in pricing_indicators:
                pricing_tier = 'low'
            else:
                pricing_tier = 'mid'
            
            # Get revenue per member
            type_revenue = revenue_per_member.get(gym_type, revenue_per_member['traditional_gym'])
            monthly_per_member = type_revenue[pricing_tier]
            
            # Calculate estimated monthly revenue
            estimated_monthly_revenue = estimated_members * monthly_per_member
            qualification_data['estimated_monthly_revenue'] = estimated_monthly_revenue
            
            # Determine revenue tier
            if estimated_monthly_revenue >= 100000:
                qualification_data['revenue_tier'] = 'enterprise'
                qualification_data['revenue_potential'] = 'very_high'
            elif estimated_monthly_revenue >= 50000:
                qualification_data['revenue_tier'] = 'large'
                qualification_data['revenue_potential'] = 'high'
            elif estimated_monthly_revenue >= 20000:
                qualification_data['revenue_tier'] = 'medium'
                qualification_data['revenue_potential'] = 'medium'
            elif estimated_monthly_revenue >= 10000:
                qualification_data['revenue_tier'] = 'small'
                qualification_data['revenue_potential'] = 'low'
            else:
                qualification_data['revenue_tier'] = 'micro'
                qualification_data['revenue_potential'] = 'very_low'
            
            # Determine size tier based on member count
            if estimated_members >= 1000:
                qualification_data['size_tier'] = 'large'
            elif estimated_members >= 300:
                qualification_data['size_tier'] = 'medium'
            elif estimated_members >= 100:
                qualification_data['size_tier'] = 'small'
            else:
                qualification_data['size_tier'] = 'micro'
            
            # Calculate viability score (0-100)
            viability_score = 0
            
            # Revenue component (40 points)
            if qualification_data['revenue_potential'] == 'very_high':
                viability_score += 40
                qualification_data['qualification_reasons'].append('Very high revenue potential ($100K+/month)')
            elif qualification_data['revenue_potential'] == 'high':
                viability_score += 30
                qualification_data['qualification_reasons'].append('High revenue potential ($50K-100K/month)')
            elif qualification_data['revenue_potential'] == 'medium':
                viability_score += 20
                qualification_data['qualification_reasons'].append('Medium revenue potential ($20K-50K/month)')
            elif qualification_data['revenue_potential'] == 'low':
                viability_score += 10
                qualification_data['qualification_reasons'].append('Low revenue potential ($10K-20K/month)')
            else:
                qualification_data['disqualification_reasons'].append('Very low revenue potential (<$10K/month)')
            
            # Size component (30 points)
            if estimated_members >= 500:
                viability_score += 30
                qualification_data['qualification_reasons'].append(f'Good member base size (~{estimated_members} members)')
            elif estimated_members >= 200:
                viability_score += 20
                qualification_data['qualification_reasons'].append(f'Moderate member base (~{estimated_members} members)')
            elif estimated_members >= 100:
                viability_score += 10
                qualification_data['qualification_reasons'].append(f'Small but viable member base (~{estimated_members} members)')
            else:
                qualification_data['disqualification_reasons'].append(f'Very small member base (<100 members)')
            
            # Business quality component (20 points)
            if rating >= 4.5 and reviews_count >= 100:
                viability_score += 20
                qualification_data['qualification_reasons'].append('Excellent reputation (4.5+ rating, 100+ reviews)')
            elif rating >= 4.0 and reviews_count >= 50:
                viability_score += 15
                qualification_data['qualification_reasons'].append('Good reputation')
            elif rating >= 3.5:
                viability_score += 10
            else:
                qualification_data['disqualification_reasons'].append('Poor reputation (rating < 3.5)')
            
            # Growth potential component (10 points)
            if gym_type in ['crossfit', 'boutique_fitness', 'fitness_center']:
                viability_score += 10
                qualification_data['qualification_reasons'].append(f'High-growth gym type ({gym_type})')
            elif gym_type in ['traditional_gym', 'yoga_studio']:
                viability_score += 5
            
            qualification_data['viability_score'] = viability_score
            
            # Determine qualification status
            if viability_score >= 70:
                qualification_data['size_qualification'] = 'highly_qualified'
            elif viability_score >= 50:
                qualification_data['size_qualification'] = 'qualified'
            elif viability_score >= 30:
                qualification_data['size_qualification'] = 'marginally_qualified'
            else:
                qualification_data['size_qualification'] = 'unqualified'
            
            # Add context about software spend potential
            software_spend_percentage = 0.02  # 2% of revenue for software
            if gym_type in ['crossfit', 'boutique_fitness']:
                software_spend_percentage = 0.03  # Higher tech adoption
            elif gym_type == 'personal_training':
                software_spend_percentage = 0.015  # Lower needs
            
            estimated_software_budget = int(estimated_monthly_revenue * software_spend_percentage)
            qualification_data['estimated_monthly_software_budget'] = estimated_software_budget
            
            if estimated_software_budget >= 2000:
                qualification_data['qualification_reasons'].append(f'Strong software budget potential (~${estimated_software_budget}/month)')
            elif estimated_software_budget >= 1000:
                qualification_data['qualification_reasons'].append(f'Moderate software budget (~${estimated_software_budget}/month)')
            elif estimated_software_budget >= 500:
                qualification_data['qualification_reasons'].append(f'Basic software budget (~${estimated_software_budget}/month)')
            else:
                qualification_data['disqualification_reasons'].append(f'Limited software budget (<$500/month)')
            
            return qualification_data
            
        except Exception as e:
            logger.error(f"Error in gym size and revenue qualification: {e}")
            return {
                'size_qualification': 'unknown',
                'revenue_potential': 'unknown',
                'estimated_monthly_revenue': 0,
                'estimated_member_count': 0,
                'viability_score': 0,
                'qualification_reasons': [],
                'disqualification_reasons': ['Error in qualification analysis'],
                'size_tier': 'unknown',
                'revenue_tier': 'unknown'
            }
    
    def _identify_decision_makers(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and qualify decision makers at gym businesses"""
        try:
            decision_maker_data = {
                'likely_decision_makers': [],
                'decision_making_structure': 'unknown',
                'contact_quality': 'unknown',
                'owner_identified': False,
                'management_level': 'unknown',
                'franchise_considerations': {},
                'decision_factors': []
            }
            
            # Get gym data
            gym_type = lead.get('gym_type', 'unknown')
            gym_size = lead.get('gym_size_estimate', 'unknown')
            franchise_chain = lead.get('gym_franchise_chain', '')
            business_name = lead.get('business_name', '')
            reviews_data = lead.get('reviews_data', [])
            website_url = lead.get('website', '')
            
            # Analyze business structure based on size and type
            if gym_size == 'large' or franchise_chain:
                decision_maker_data['decision_making_structure'] = 'corporate'
                decision_maker_data['management_level'] = 'multi_tier'
                decision_maker_data['likely_decision_makers'] = [
                    {'title': 'General Manager', 'influence': 'high', 'focus': 'operations'},
                    {'title': 'Operations Director', 'influence': 'high', 'focus': 'efficiency'},
                    {'title': 'Regional Manager', 'influence': 'medium', 'focus': 'standardization'}
                ]
                
                if franchise_chain:
                    decision_maker_data['franchise_considerations'] = {
                        'is_franchise': True,
                        'decision_level': 'may require corporate approval',
                        'key_contact': 'Franchise owner or area developer',
                        'approval_complexity': 'high'
                    }
                    decision_maker_data['likely_decision_makers'].append(
                        {'title': 'Franchise Owner', 'influence': 'very_high', 'focus': 'roi'}
                    )
                
            elif gym_size == 'medium':
                decision_maker_data['decision_making_structure'] = 'owner_operated'
                decision_maker_data['management_level'] = 'single_tier'
                decision_maker_data['likely_decision_makers'] = [
                    {'title': 'Owner/Operator', 'influence': 'very_high', 'focus': 'growth'},
                    {'title': 'General Manager', 'influence': 'high', 'focus': 'daily_operations'}
                ]
                
            elif gym_size == 'small' or gym_type in ['personal_training', 'boutique_fitness', 'yoga_studio']:
                decision_maker_data['decision_making_structure'] = 'owner_direct'
                decision_maker_data['management_level'] = 'owner_only'
                decision_maker_data['likely_decision_makers'] = [
                    {'title': 'Owner', 'influence': 'exclusive', 'focus': 'all_aspects'}
                ]
                decision_maker_data['owner_identified'] = True
                
            # Scan reviews for owner/manager mentions
            owner_mentions = 0
            manager_mentions = 0
            staff_quality_mentions = 0
            
            for review in reviews_data[:50]:  # Check first 50 reviews
                review_text = review.get('text', '').lower()
                if any(term in review_text for term in ['owner', 'owns', 'founded']):
                    owner_mentions += 1
                if any(term in review_text for term in ['manager', 'management', 'gm']):
                    manager_mentions += 1
                if any(term in review_text for term in ['staff', 'trainer', 'instructor', 'coach']):
                    staff_quality_mentions += 1
            
            # Adjust based on review insights
            if owner_mentions >= 3:
                decision_maker_data['owner_identified'] = True
                decision_maker_data['decision_factors'].append('Owner actively involved (mentioned in reviews)')
            
            if manager_mentions >= 5:
                decision_maker_data['decision_factors'].append('Professional management structure evident')
            
            # Determine contact quality based on available info
            contact_score = 0
            
            if website_url:
                contact_score += 30
                decision_maker_data['decision_factors'].append('Website available for research')
            
            if lead.get('phone'):
                contact_score += 20
                decision_maker_data['decision_factors'].append('Direct phone contact available')
            
            if decision_maker_data['owner_identified']:
                contact_score += 25
                decision_maker_data['decision_factors'].append('Owner involvement confirmed')
            
            if gym_size in ['small', 'medium']:
                contact_score += 15
                decision_maker_data['decision_factors'].append('Smaller size = easier access to decision makers')
            
            if lead.get('gym_linkedin_presence', False):
                contact_score += 10
                decision_maker_data['decision_factors'].append('LinkedIn presence for professional outreach')
            
            # Determine contact quality
            if contact_score >= 70:
                decision_maker_data['contact_quality'] = 'excellent'
            elif contact_score >= 50:
                decision_maker_data['contact_quality'] = 'good'
            elif contact_score >= 30:
                decision_maker_data['contact_quality'] = 'fair'
            else:
                decision_maker_data['contact_quality'] = 'poor'
            
            # Add sales approach recommendations based on decision structure
            if decision_maker_data['decision_making_structure'] == 'corporate':
                decision_maker_data['sales_approach'] = {
                    'strategy': 'enterprise',
                    'key_points': [
                        'Focus on scalability and standardization',
                        'Emphasize ROI and efficiency metrics',
                        'Prepare for longer sales cycle',
                        'Consider pilot program approach'
                    ],
                    'estimated_sales_cycle': '3-6 months'
                }
            elif decision_maker_data['decision_making_structure'] == 'owner_operated':
                decision_maker_data['sales_approach'] = {
                    'strategy': 'relationship',
                    'key_points': [
                        'Build trust with owner/operator',
                        'Focus on growth and member satisfaction',
                        'Demonstrate quick wins',
                        'Offer flexible terms'
                    ],
                    'estimated_sales_cycle': '1-3 months'
                }
            else:  # owner_direct
                decision_maker_data['sales_approach'] = {
                    'strategy': 'consultative',
                    'key_points': [
                        'Direct owner engagement',
                        'Focus on time savings and simplicity',
                        'Emphasize personal support',
                        'Start with basic package'
                    ],
                    'estimated_sales_cycle': '2-4 weeks'
                }
            
            # Assess overall decision maker accessibility
            if decision_maker_data['contact_quality'] in ['excellent', 'good'] and \
               decision_maker_data['management_level'] in ['owner_only', 'single_tier']:
                decision_maker_data['accessibility_rating'] = 'high'
            elif decision_maker_data['contact_quality'] == 'poor' or \
                 decision_maker_data['management_level'] == 'multi_tier':
                decision_maker_data['accessibility_rating'] = 'low'
            else:
                decision_maker_data['accessibility_rating'] = 'medium'
            
            return decision_maker_data
            
        except Exception as e:
            logger.error(f"Error in decision maker identification: {e}")
            return {
                'likely_decision_makers': [],
                'decision_making_structure': 'unknown',
                'contact_quality': 'unknown',
                'owner_identified': False,
                'management_level': 'unknown',
                'franchise_considerations': {},
                'decision_factors': ['Error in analysis']
            }
    
    def _estimate_gym_software_budget(self, lead: Dict[str, Any]) -> Dict[str, Any]:
        """Develop comprehensive budget estimation for gym software"""
        try:
            budget_data = {
                'estimated_total_budget': 0,
                'budget_breakdown': {},
                'budget_confidence': 'low',
                'budget_factors': [],
                'recommended_package': 'unknown',
                'pricing_tier': 'unknown',
                'contract_recommendations': {},
                'competitor_spend_estimate': 0
            }
            
            # Get key data
            monthly_revenue = lead.get('gym_estimated_monthly_revenue', 0)
            member_count = lead.get('gym_estimated_member_count', 0)
            gym_type = lead.get('gym_type', 'unknown')
            gym_size = lead.get('gym_size_estimate', 'unknown')
            current_software = lead.get('gym_software_detected', [])
            digital_score = lead.get('gym_digital_infrastructure_score', 0)
            classification = lead.get('gym_classification', 'unknown')
            
            # Base software spend percentage by gym type
            base_spend_percentages = {
                'crossfit': 0.035,  # 3.5% - High tech adoption
                'boutique_fitness': 0.03,  # 3% - Premium focus
                'fitness_center': 0.025,  # 2.5% - Balanced
                'health_club': 0.025,  # 2.5% - Established systems
                'traditional_gym': 0.02,  # 2% - Cost conscious
                'yoga_studio': 0.022,  # 2.2% - Moderate tech
                'martial_arts': 0.018,  # 1.8% - Traditional
                'personal_training': 0.015  # 1.5% - Minimal needs
            }
            
            base_percentage = base_spend_percentages.get(gym_type, 0.02)
            
            # Adjust based on digital maturity
            if digital_score >= 80:
                base_percentage *= 1.3  # High digital maturity = higher spend
                budget_data['budget_factors'].append('High digital maturity (+30% budget)')
            elif digital_score >= 60:
                base_percentage *= 1.1
                budget_data['budget_factors'].append('Good digital presence (+10% budget)')
            elif digital_score < 40:
                base_percentage *= 0.8
                budget_data['budget_factors'].append('Low digital maturity (-20% budget)')
            
            # Adjust based on current software situation
            if not current_software or all('basic' in s.lower() or 'generic' in s.lower() for s in current_software):
                base_percentage *= 1.2  # No/basic software = higher initial investment
                budget_data['budget_factors'].append('Limited current software (+20% budget for initial setup)')
            elif len(current_software) >= 3:
                base_percentage *= 0.9  # Multiple systems = consolidation opportunity
                budget_data['budget_factors'].append('Multiple systems in place (-10% for consolidation)')
            
            # Calculate base budget
            estimated_monthly_budget = int(monthly_revenue * base_percentage)
            budget_data['estimated_total_budget'] = estimated_monthly_budget
            
            # Create detailed budget breakdown
            if gym_type in ['crossfit', 'boutique_fitness', 'fitness_center']:
                budget_data['budget_breakdown'] = {
                    'core_platform': int(estimated_monthly_budget * 0.6),
                    'mobile_app': int(estimated_monthly_budget * 0.2),
                    'integrations': int(estimated_monthly_budget * 0.1),
                    'support_training': int(estimated_monthly_budget * 0.1)
                }
            else:
                budget_data['budget_breakdown'] = {
                    'core_platform': int(estimated_monthly_budget * 0.7),
                    'mobile_app': int(estimated_monthly_budget * 0.15),
                    'integrations': int(estimated_monthly_budget * 0.1),
                    'support_training': int(estimated_monthly_budget * 0.05)
                }
            
            # Determine pricing tier and package recommendations
            if member_count >= 1000:
                budget_data['pricing_tier'] = 'enterprise'
                budget_data['recommended_package'] = 'enterprise_unlimited'
                per_member_cost = estimated_monthly_budget / member_count
                budget_data['budget_factors'].append(f'Enterprise tier: ${per_member_cost:.2f}/member/month')
            elif member_count >= 500:
                budget_data['pricing_tier'] = 'professional'
                budget_data['recommended_package'] = 'professional_plus'
                per_member_cost = estimated_monthly_budget / member_count
                budget_data['budget_factors'].append(f'Professional tier: ${per_member_cost:.2f}/member/month')
            elif member_count >= 200:
                budget_data['pricing_tier'] = 'standard'
                budget_data['recommended_package'] = 'standard'
                per_member_cost = estimated_monthly_budget / member_count
                budget_data['budget_factors'].append(f'Standard tier: ${per_member_cost:.2f}/member/month')
            else:
                budget_data['pricing_tier'] = 'basic'
                budget_data['recommended_package'] = 'starter'
                if member_count > 0:
                    per_member_cost = estimated_monthly_budget / member_count
                    budget_data['budget_factors'].append(f'Starter tier: ${per_member_cost:.2f}/member/month')
            
            # Contract recommendations based on gym characteristics
            if gym_size == 'large' or lead.get('gym_franchise_chain'):
                budget_data['contract_recommendations'] = {
                    'term': 'annual',
                    'payment': 'monthly',
                    'discount_potential': '15-20%',
                    'negotiation_leverage': 'high',
                    'key_terms': ['Volume pricing', 'Multi-location discount', 'SLA guarantees']
                }
            elif classification == 'red' and gym_size == 'medium':
                budget_data['contract_recommendations'] = {
                    'term': 'annual',
                    'payment': 'monthly',
                    'discount_potential': '10-15%',
                    'negotiation_leverage': 'medium',
                    'key_terms': ['Performance guarantees', 'Migration support', 'Training included']
                }
            else:
                budget_data['contract_recommendations'] = {
                    'term': 'month-to-month',
                    'payment': 'monthly',
                    'discount_potential': '5-10%',
                    'negotiation_leverage': 'low',
                    'key_terms': ['Flexible terms', 'Easy cancellation', 'Basic support']
                }
            
            # Estimate competitor spend (for sales intelligence)
            if gym_type in ['crossfit', 'boutique_fitness']:
                competitor_multiplier = 1.1  # These gyms typically spend more
            elif gym_type in ['traditional_gym', 'martial_arts']:
                competitor_multiplier = 0.9  # These typically spend less
            else:
                competitor_multiplier = 1.0
            
            budget_data['competitor_spend_estimate'] = int(estimated_monthly_budget * competitor_multiplier)
            
            # Determine budget confidence
            confidence_score = 0
            if monthly_revenue > 0:
                confidence_score += 40
            if member_count > 0:
                confidence_score += 30
            if current_software:
                confidence_score += 20
            if digital_score > 0:
                confidence_score += 10
            
            if confidence_score >= 80:
                budget_data['budget_confidence'] = 'high'
            elif confidence_score >= 60:
                budget_data['budget_confidence'] = 'medium'
            else:
                budget_data['budget_confidence'] = 'low'
            
            # Add ROI projections
            if estimated_monthly_budget > 0:
                # Estimate potential savings/gains
                efficiency_savings = int(estimated_monthly_budget * 2.5)  # 2.5x ROI typical
                budget_data['roi_projections'] = {
                    'monthly_efficiency_savings': efficiency_savings,
                    'member_retention_value': int(member_count * 0.02 * (monthly_revenue / max(1, member_count))),  # 2% better retention
                    'new_member_acquisition': int(member_count * 0.05 * (monthly_revenue / max(1, member_count))),  # 5% growth
                    'payback_period_months': max(3, int(estimated_monthly_budget * 3 / efficiency_savings))
                }
                
                total_monthly_value = sum(budget_data['roi_projections'].values()) - budget_data['roi_projections']['payback_period_months']
                budget_data['budget_factors'].append(f'Projected ROI: ${total_monthly_value:,}/month after {budget_data["roi_projections"]["payback_period_months"]} months')
            
            return budget_data
            
        except Exception as e:
            logger.error(f"Error in gym software budget estimation: {e}")
            return {
                'estimated_total_budget': 0,
                'budget_breakdown': {},
                'budget_confidence': 'low',
                'budget_factors': ['Error in budget analysis'],
                'recommended_package': 'unknown',
                'pricing_tier': 'unknown',
                'contract_recommendations': {},
                'competitor_spend_estimate': 0
            }

    def _get_contextual_software_recommendations(self, detected_software: List[str]) -> List[str]:
        """Get contextual software recommendations based on what was detected"""
        recommendations = []
        
        # Check if no specialized gym software was detected
        generic_software = ['wordpress', 'square', 'stripe', 'calendly']
        has_only_generic = detected_software and all(any(generic in software_key for generic in generic_software) for software_key in detected_software)
        
        if not detected_software or has_only_generic:
            recommendations.append("Consider implementing specialized gym management software")
            recommendations.append("MindBody, Zen Planner, or Glofox recommended for comprehensive features")
            return recommendations
        
        # Check for basic/generic solutions
        basic_solutions = ['square', 'calendly', 'wordpress']
        has_basic_only = any(basic in detected_software for basic in basic_solutions)
        
        if has_basic_only and len(detected_software) == 1:
            recommendations.append("Current solution may be too basic for comprehensive gym management")
            recommendations.append("Consider upgrading to specialized gym software for better member management")
        
        # Check for outdated solutions
        outdated_solutions = ['abc_financial', 'perfect_gym']
        has_outdated = any(outdated in detected_software for outdated in outdated_solutions)
        
        if has_outdated:
            recommendations.append("URGENT: Outdated software detected - consider immediate upgrade")
            recommendations.append("Modern alternatives: MindBody, WellnessLiving, or Glofox")
        
        return recommendations
    
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
                
                # Perform gym software detection and analysis
                gym_software_analysis = self._analyze_gym_software(technologies, website)
                lead['gym_software_detected'] = gym_software_analysis['detected_software']
                lead['gym_software_scores'] = gym_software_analysis['software_scores']
                lead['gym_software_quality_score'] = gym_software_analysis['overall_quality_score']
                lead['gym_software_recommendations'] = gym_software_analysis['recommendations']
                lead['gym_software_red_flags'] = gym_software_analysis['red_flags']
                
                # Perform gym website feature analysis
                website_feature_analysis = self._analyze_gym_website_features(website, technologies)
                lead['gym_website_features'] = website_feature_analysis['detected_features']
                lead['gym_website_feature_score'] = website_feature_analysis['feature_score']
                lead['gym_website_feature_indicators'] = website_feature_analysis['feature_indicators']
                lead['gym_website_missing_features'] = website_feature_analysis['missing_features']
                lead['gym_website_feature_recommendations'] = website_feature_analysis['recommendations']
                lead['gym_website_implemented_features'] = website_feature_analysis['implemented_count']
                
                # Perform gym mobile app analysis
                mobile_app_analysis = self._analyze_gym_mobile_app(lead['business_name'], website, gym_software_analysis['detected_software'])
                lead['gym_mobile_app_available'] = mobile_app_analysis['has_mobile_app']
                lead['gym_mobile_app_platforms'] = mobile_app_analysis['app_platforms']
                lead['gym_mobile_app_quality_score'] = mobile_app_analysis['app_quality_score']
                lead['gym_mobile_app_quality_issues'] = mobile_app_analysis['app_quality_issues']
                lead['gym_mobile_app_recommendations'] = mobile_app_analysis['app_recommendations']
                lead['gym_mobile_app_detection_method'] = mobile_app_analysis['detection_method']
                
                # Calculate comprehensive digital infrastructure score
                digital_infrastructure_analysis = self._calculate_digital_infrastructure_score(lead)
                lead['gym_digital_infrastructure_score'] = digital_infrastructure_analysis['overall_score']
                lead['gym_digital_infrastructure_tier'] = digital_infrastructure_analysis['tier']
                lead['gym_digital_infrastructure_description'] = digital_infrastructure_analysis['tier_description']
                lead['gym_digital_component_scores'] = digital_infrastructure_analysis['component_scores']
                lead['gym_digital_weighted_contributions'] = digital_infrastructure_analysis['weighted_contributions']
                lead['gym_digital_readiness'] = digital_infrastructure_analysis['digital_readiness']
                lead['gym_digital_infrastructure_recommendations'] = digital_infrastructure_analysis['improvement_recommendations']
                lead['gym_digital_critical_gaps'] = digital_infrastructure_analysis['critical_gaps']
                lead['gym_digital_competitive_analysis'] = digital_infrastructure_analysis['competitive_analysis']
                
                # Analyze gym-specific pain factors
                gym_pain_analysis = self._analyze_gym_pain_factors(lead)
                
                # Apply size and model-specific scoring adjustments
                size_model_adjustments = self._apply_gym_size_and_model_scoring(lead, gym_pain_analysis)
                
                # Update pain analysis with adjusted scores
                lead['gym_pain_factors'] = gym_pain_analysis
                lead['gym_pain_score'] = gym_pain_analysis['pain_score']
                lead['gym_pain_urgency'] = gym_pain_analysis['urgency_level']
                lead['gym_primary_pain_category'] = gym_pain_analysis['primary_pain_category']
                lead['gym_total_pain_points'] = gym_pain_analysis['total_pain_points']
                lead['gym_critical_pain_issues'] = gym_pain_analysis['critical_issues']
                
                # Add size/model adjusted scores
                lead['gym_adjusted_pain_score'] = size_model_adjustments['adjusted_pain_score']
                lead['gym_adjusted_urgency'] = size_model_adjustments['adjusted_urgency']
                lead['gym_size_pain_multiplier'] = size_model_adjustments['pain_multiplier']
                lead['gym_model_pain_multiplier'] = size_model_adjustments['model_multiplier']
                lead['gym_threshold_violations'] = size_model_adjustments.get('threshold_violations', [])
                lead['gym_size_context'] = size_model_adjustments.get('size_context', '')
                lead['gym_model_context'] = size_model_adjustments.get('model_context', '')
                
                # Apply gym-specific RED/GREEN classification
                lead = self._apply_gym_specific_red_green_classification(lead)
                
                # Apply gym size and revenue qualification
                revenue_qualification = self._qualify_gym_size_and_revenue(lead)
                lead['gym_size_qualification'] = revenue_qualification['size_qualification']
                lead['gym_revenue_potential'] = revenue_qualification['revenue_potential']
                lead['gym_estimated_monthly_revenue'] = revenue_qualification['estimated_monthly_revenue']
                lead['gym_estimated_member_count'] = revenue_qualification['estimated_member_count']
                lead['gym_viability_score'] = revenue_qualification['viability_score']
                lead['gym_qualification_reasons'] = revenue_qualification['qualification_reasons']
                lead['gym_disqualification_reasons'] = revenue_qualification['disqualification_reasons']
                lead['gym_size_tier'] = revenue_qualification['size_tier']
                lead['gym_revenue_tier'] = revenue_qualification['revenue_tier']
                lead['gym_estimated_monthly_software_budget'] = revenue_qualification.get('estimated_monthly_software_budget', 0)
                
                # Identify decision makers
                decision_maker_analysis = self._identify_decision_makers(lead)
                lead['gym_decision_makers'] = decision_maker_analysis['likely_decision_makers']
                lead['gym_decision_structure'] = decision_maker_analysis['decision_making_structure']
                lead['gym_contact_quality'] = decision_maker_analysis['contact_quality']
                lead['gym_owner_identified'] = decision_maker_analysis['owner_identified']
                lead['gym_management_level'] = decision_maker_analysis['management_level']
                lead['gym_franchise_considerations'] = decision_maker_analysis.get('franchise_considerations', {})
                lead['gym_decision_factors'] = decision_maker_analysis['decision_factors']
                lead['gym_sales_approach'] = decision_maker_analysis.get('sales_approach', {})
                lead['gym_decision_accessibility'] = decision_maker_analysis.get('accessibility_rating', 'unknown')
                
                # Estimate software budget
                budget_estimation = self._estimate_gym_software_budget(lead)
                lead['gym_software_budget_total'] = budget_estimation['estimated_total_budget']
                lead['gym_software_budget_breakdown'] = budget_estimation['budget_breakdown']
                lead['gym_budget_confidence'] = budget_estimation['budget_confidence']
                lead['gym_budget_factors'] = budget_estimation['budget_factors']
                lead['gym_recommended_package'] = budget_estimation['recommended_package']
                lead['gym_pricing_tier'] = budget_estimation['pricing_tier']
                lead['gym_contract_recommendations'] = budget_estimation['contract_recommendations']
                lead['gym_competitor_spend'] = budget_estimation['competitor_spend_estimate']
                lead['gym_roi_projections'] = budget_estimation.get('roi_projections', {})
                
                logger.info(f"Technology analysis completed for {lead['business_name']}: {len(technologies)} techs, age score: {tech_analysis['age_score']}")
                if gym_software_analysis['detected_software']:
                    logger.info(f"Gym software detected: {', '.join(gym_software_analysis['detected_software'])}")
                logger.info(f"Website features detected for {lead['business_name']}: {website_feature_analysis['implemented_count']}/{website_feature_analysis['total_features']} features (score: {website_feature_analysis['feature_score']})")
                logger.info(f"Gym revenue qualification for {lead['business_name']}: {revenue_qualification['size_qualification']} "
                           f"(viability score: {revenue_qualification['viability_score']}, "
                           f"estimated revenue: ${revenue_qualification['estimated_monthly_revenue']:,}/month, "
                           f"members: ~{revenue_qualification['estimated_member_count']})")
                logger.info(f"Decision maker analysis for {lead['business_name']}: {decision_maker_analysis['decision_making_structure']} structure, "
                           f"contact quality: {decision_maker_analysis['contact_quality']}, "
                           f"accessibility: {decision_maker_analysis.get('accessibility_rating', 'unknown')}")
                logger.info(f"Software budget estimation for {lead['business_name']}: ${budget_estimation['estimated_total_budget']:,}/month "
                           f"({budget_estimation['pricing_tier']} tier, confidence: {budget_estimation['budget_confidence']})")
                logger.info(f"Mobile app analysis for {lead['business_name']}: {'Available' if mobile_app_analysis['has_mobile_app'] else 'Not available'} (quality: {mobile_app_analysis['app_quality_score']})")
                logger.info(f"Digital infrastructure score for {lead['business_name']}: {digital_infrastructure_analysis['overall_score']}/100 ({digital_infrastructure_analysis['tier']}) - Readiness: {digital_infrastructure_analysis['digital_readiness']}/100")
                logger.info(f"Gym pain analysis for {lead['business_name']}: pain_score={gym_pain_analysis['pain_score']}, urgency={gym_pain_analysis['urgency_level']}, primary_category={gym_pain_analysis['primary_pain_category']}")
                logger.info(f"Size/Model adjustments for {lead['business_name']}: adjusted_score={size_model_adjustments['adjusted_pain_score']}, adjusted_urgency={size_model_adjustments['adjusted_urgency']}, size_multiplier={size_model_adjustments['pain_multiplier']}, model_multiplier={size_model_adjustments['model_multiplier']}")
            
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
        
        # Step 5: Extract logos for RED leads
        self._extract_logos_for_red_leads(processed_leads)
        
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
    
    def _extract_logos_for_red_leads(self, leads: List[Dict[str, Any]]) -> None:
        """Extract logos for all RED leads"""
        red_leads = [lead for lead in leads if lead.get('status') == 'red']
        
        if not red_leads:
            logger.info("No RED leads found - skipping logo extraction")
            return
        
        logger.info(f"Starting logo extraction for {len(red_leads)} RED leads")
        
        try:
            # Process logos for RED leads
            processed_leads = self.logo_extractor.process_leads_for_logos(red_leads)
            
            # Update leads with logo information
            for i, lead in enumerate(red_leads):
                processed_lead = processed_leads[i]
                
                # Copy logo information to the original lead
                lead['logo_url'] = processed_lead.get('logo_url', '')
                lead['logo_extraction_method'] = processed_lead.get('logo_extraction_method', 'failed')
                lead['logo_fallback_generated'] = processed_lead.get('logo_fallback_generated', False)
                lead['logo_quality_score'] = processed_lead.get('logo_quality_score', 0)
                lead['logo_valid'] = processed_lead.get('logo_valid', False)
                
                # Merge any additional error notes
                if processed_lead.get('error_notes'):
                    existing_errors = lead.get('error_notes', '')
                    if existing_errors and not existing_errors.endswith(';'):
                        existing_errors += ';'
                    lead['error_notes'] = existing_errors + ' ' + processed_lead['error_notes']
                
                logger.info(f"Logo processed for {lead['business_name']}: {lead['logo_extraction_method']}")
            
            successful_extractions = sum(1 for lead in red_leads if lead.get('logo_url'))
            fallback_generated = sum(1 for lead in red_leads if lead.get('logo_fallback_generated'))
            
            logger.info(f"Logo extraction completed: {successful_extractions}/{len(red_leads)} successful, {fallback_generated} fallbacks generated")
            
        except Exception as e:
            logger.error(f"Error during logo extraction process: {e}")
            # Mark all RED leads as having failed logo extraction
            for lead in red_leads:
                if not lead.get('logo_url'):
                    lead['logo_url'] = ''
                    lead['logo_extraction_method'] = 'failed'
                    lead['logo_fallback_generated'] = False
                    error_notes = lead.get('error_notes', '')
                    if error_notes and not error_notes.endswith(';'):
                        error_notes += ';'
                    lead['error_notes'] = error_notes + ' Logo extraction failed;'
    
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
            gym_software_quality_score = lead.get('gym_software_quality_score', 50) or 50
            gym_software_red_flags = lead.get('gym_software_red_flags', [])
            
            # Pain scoring weights (higher = more pain/worse)
            MOBILE_WEIGHT = 0.4  # 40% weight on mobile performance
            TECH_AGE_WEIGHT = 0.2  # 20% weight on technology age
            TECH_FLAGS_WEIGHT = 0.1  # 10% weight on critical tech flags
            GYM_SOFTWARE_WEIGHT = 0.3  # 30% weight on gym software quality
            
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
            
            # Gym software pain score (inverted - lower quality = higher pain)
            gym_software_pain_score = 100 - gym_software_quality_score
            
            # Add bonus pain for gym software red flags
            if gym_software_red_flags:
                critical_software_flags = sum(1 for flag in gym_software_red_flags if 'CRITICAL' in str(flag))
                standard_software_flags = len(gym_software_red_flags) - critical_software_flags
                gym_software_pain_score += min(30, (critical_software_flags * 20) + (standard_software_flags * 10))
            
            # Calculate overall pain score
            overall_pain_score = (
                (mobile_pain_score * MOBILE_WEIGHT) +
                (tech_age_pain_score * TECH_AGE_WEIGHT) +
                (tech_flags_pain_score * TECH_FLAGS_WEIGHT) +
                (gym_software_pain_score * GYM_SOFTWARE_WEIGHT)
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
                'gym_software_pain': round(gym_software_pain_score, 1),
                'overall_pain': round(overall_pain_score, 1),
                'pain_level': pain_level,
                'scoring_weights': {
                    'mobile': MOBILE_WEIGHT,
                    'tech_age': TECH_AGE_WEIGHT,
                    'tech_flags': TECH_FLAGS_WEIGHT,
                    'gym_software': GYM_SOFTWARE_WEIGHT
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
            if gym_software_pain_score > 50:
                pain_factors.append(f"Poor gym software quality (score: {gym_software_quality_score})")
            if gym_software_red_flags:
                pain_factors.append(f"Gym software issues ({len(gym_software_red_flags)} red flags)")
            
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
                # Gym-specific fields
                'gym_type', 'gym_size_estimate', 'gym_size_confidence', 'gym_size_factors', 'gym_services', 'gym_location_type',
                'gym_membership_model', 'gym_equipment_types', 'gym_operating_hours',
                'gym_pricing_indicators', 'gym_target_demographic', 'gym_franchise_chain',
                'gym_years_in_business', 'gym_staff_size_estimate', 'gym_digital_presence_score',
                'gym_software_needs_score', 'gym_software_detected', 'gym_software_scores',
                'gym_software_quality_score', 'gym_software_recommendations', 'gym_software_red_flags',
                # Gym pain and classification fields
                'gym_pain_score', 'gym_adjusted_pain_score', 'gym_pain_urgency', 'gym_adjusted_urgency',
                'gym_primary_pain_category', 'gym_total_pain_points', 'gym_critical_pain_issues',
                'gym_size_pain_multiplier', 'gym_model_pain_multiplier', 'gym_threshold_violations',
                'gym_classification', 'gym_classification_confidence', 'gym_classification_reasons',
                'gym_action_priority', 'gym_sales_readiness', 'gym_classification_summary',
                # Revenue qualification fields
                'gym_size_qualification', 'gym_revenue_potential', 'gym_estimated_monthly_revenue',
                'gym_estimated_member_count', 'gym_viability_score', 'gym_qualification_reasons',
                'gym_disqualification_reasons', 'gym_size_tier', 'gym_revenue_tier',
                'gym_estimated_monthly_software_budget',
                # Decision maker fields
                'gym_decision_structure', 'gym_contact_quality', 'gym_owner_identified',
                'gym_management_level', 'gym_decision_accessibility', 'gym_decision_factors',
                # Budget estimation fields
                'gym_software_budget_total', 'gym_budget_confidence', 'gym_budget_factors',
                'gym_recommended_package', 'gym_pricing_tier', 'gym_competitor_spend',
                'screenshot_url', 'logo_url', 'logo_extraction_method', 'logo_fallback_generated', 
                'logo_quality_score', 'logo_valid', 'pdf_url', 'error_notes'
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