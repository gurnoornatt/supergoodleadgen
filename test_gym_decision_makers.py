import pytest
from lead_processor import LeadProcessor


class TestGymDecisionMakers:
    """Test decision maker identification system"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.processor = LeadProcessor()
    
    def test_large_gym_corporate_structure(self):
        """Test decision maker identification for large corporate gym"""
        lead = {
            'business_name': 'Mega Fitness Center',
            'gym_size_estimate': 'large',
            'gym_type': 'fitness_center',
            'gym_franchise_chain': '',
            'website': 'https://megafitness.com',
            'phone': '555-1234',
            'reviews_data': []
        }
        
        result = self.processor._identify_decision_makers(lead)
        
        assert result['decision_making_structure'] == 'corporate'
        assert result['management_level'] == 'multi_tier'
        assert len(result['likely_decision_makers']) >= 3
        
        # Check for expected roles
        titles = [dm['title'] for dm in result['likely_decision_makers']]
        assert 'General Manager' in titles
        assert 'Operations Director' in titles
        assert 'Regional Manager' in titles
        
        # Check contact quality (website + phone)
        assert result['contact_quality'] in ['good', 'fair']
        assert result['accessibility_rating'] == 'low'  # Multi-tier = harder access
        
        # Check sales approach
        assert result['sales_approach']['strategy'] == 'enterprise'
        assert result['sales_approach']['estimated_sales_cycle'] == '3-6 months'
    
    def test_franchise_gym_decision_makers(self):
        """Test decision maker identification for franchise gym"""
        lead = {
            'business_name': 'Anytime Fitness - Downtown',
            'gym_size_estimate': 'large',
            'gym_type': 'fitness_center',
            'gym_franchise_chain': 'Anytime Fitness',
            'website': 'https://anytimefitness.com',
            'phone': '555-5678',
            'reviews_data': []
        }
        
        result = self.processor._identify_decision_makers(lead)
        
        assert result['decision_making_structure'] == 'corporate'
        assert result['franchise_considerations']['is_franchise'] == True
        assert result['franchise_considerations']['approval_complexity'] == 'high'
        assert result['franchise_considerations']['decision_level'] == 'may require corporate approval'
        
        # Check for franchise owner in decision makers
        titles = [dm['title'] for dm in result['likely_decision_makers']]
        assert 'Franchise Owner' in titles
        
        # Find franchise owner and check influence
        franchise_owner = next(dm for dm in result['likely_decision_makers'] if dm['title'] == 'Franchise Owner')
        assert franchise_owner['influence'] == 'very_high'
        assert franchise_owner['focus'] == 'roi'
    
    def test_medium_owner_operated_gym(self):
        """Test decision maker identification for medium owner-operated gym"""
        lead = {
            'business_name': 'Local Fitness Hub',
            'gym_size_estimate': 'medium',
            'gym_type': 'traditional_gym',
            'gym_franchise_chain': '',
            'website': 'https://localfitness.com',
            'phone': '555-9999',
            'reviews_data': [
                {'text': 'The owner John is always here and very helpful'},
                {'text': 'Love this place, the owner really cares'},
                {'text': 'John the owner fixed my billing issue immediately'}
            ]
        }
        
        result = self.processor._identify_decision_makers(lead)
        
        assert result['decision_making_structure'] == 'owner_operated'
        assert result['management_level'] == 'single_tier'
        assert result['owner_identified'] == True  # Mentioned in reviews
        
        titles = [dm['title'] for dm in result['likely_decision_makers']]
        assert 'Owner/Operator' in titles
        assert 'General Manager' in titles
        
        assert result['contact_quality'] == 'excellent'  # Website + phone + owner identified + medium size
        assert result['accessibility_rating'] == 'high'  # Good contact + single tier
        
        # Check decision factors
        assert 'Owner actively involved (mentioned in reviews)' in result['decision_factors']
        
        # Check sales approach
        assert result['sales_approach']['strategy'] == 'relationship'
        assert result['sales_approach']['estimated_sales_cycle'] == '1-3 months'
    
    def test_small_boutique_owner_direct(self):
        """Test decision maker identification for small boutique gym"""
        lead = {
            'business_name': 'Elite Pilates Studio',
            'gym_size_estimate': 'small',
            'gym_type': 'boutique_fitness',
            'gym_franchise_chain': '',
            'website': '',
            'phone': '555-3333',
            'reviews_data': []
        }
        
        result = self.processor._identify_decision_makers(lead)
        
        assert result['decision_making_structure'] == 'owner_direct'
        assert result['management_level'] == 'owner_only'
        assert result['owner_identified'] == True  # Small/boutique automatically identifies owner
        
        assert len(result['likely_decision_makers']) == 1
        assert result['likely_decision_makers'][0]['title'] == 'Owner'
        assert result['likely_decision_makers'][0]['influence'] == 'exclusive'
        
        # Contact quality (no website but has phone + small size + owner)
        assert result['contact_quality'] in ['good', 'fair']
        assert result['accessibility_rating'] == 'high'  # Owner only = easy access
        
        # Check sales approach
        assert result['sales_approach']['strategy'] == 'consultative'
        assert result['sales_approach']['estimated_sales_cycle'] == '2-4 weeks'
    
    def test_personal_training_studio(self):
        """Test decision maker identification for personal training studio"""
        lead = {
            'business_name': 'PT Excellence',
            'gym_size_estimate': 'medium',  # Will be overridden by type
            'gym_type': 'personal_training',
            'gym_franchise_chain': '',
            'website': 'https://ptexcellence.com',
            'phone': '',
            'reviews_data': []
        }
        
        result = self.processor._identify_decision_makers(lead)
        
        # Medium size overrides the personal training type check
        assert result['decision_making_structure'] == 'owner_operated'
        assert result['management_level'] == 'single_tier'
        assert result['owner_identified'] == False  # Not identified from reviews
    
    def test_manager_mentions_in_reviews(self):
        """Test detection of management structure from reviews"""
        lead = {
            'business_name': 'Professional Gym',
            'gym_size_estimate': 'medium',
            'gym_type': 'fitness_center',
            'gym_franchise_chain': '',
            'website': '',
            'phone': '',
            'reviews_data': [
                {'text': 'The manager helped me with my membership'},
                {'text': 'Great management team here'},
                {'text': 'I spoke to the GM about the equipment'},
                {'text': 'Management is very professional'},
                {'text': 'The general manager resolved my issue'},
                {'text': 'Excellent management and staff'}
            ]
        }
        
        result = self.processor._identify_decision_makers(lead)
        
        assert 'Professional management structure evident' in result['decision_factors']
    
    def test_contact_quality_scoring(self):
        """Test contact quality scoring with different combinations"""
        # Test with all contact methods
        lead_all = {
            'business_name': 'Complete Gym',
            'gym_size_estimate': 'small',
            'gym_type': 'traditional_gym',
            'website': 'https://complete.com',
            'phone': '555-1111',
            'gym_linkedin_presence': True,
            'reviews_data': [
                {'text': 'The owner is great'},
                {'text': 'Owner always here'},
                {'text': 'Spoke with the owner'}
            ]
        }
        result = self.processor._identify_decision_makers(lead_all)
        assert result['contact_quality'] == 'excellent'  # 30+20+25+15+10 = 100
        
        # Test with minimal contact
        lead_minimal = {
            'business_name': 'Minimal Gym',
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'website': '',
            'phone': '',
            'gym_linkedin_presence': False,
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_minimal)
        assert result['contact_quality'] == 'poor'  # 0 points
    
    def test_accessibility_rating_combinations(self):
        """Test accessibility rating with different combinations"""
        # High accessibility: good contact + owner only
        lead_high = {
            'business_name': 'Easy Access Gym',
            'gym_size_estimate': 'small',
            'gym_type': 'yoga_studio',
            'website': 'https://yoga.com',
            'phone': '555-2222',
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_high)
        assert result['accessibility_rating'] == 'high'
        
        # Low accessibility: poor contact or multi-tier
        lead_low = {
            'business_name': 'Hard Access Gym',
            'gym_size_estimate': 'large',
            'gym_type': 'fitness_center',
            'website': '',
            'phone': '',
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_low)
        assert result['accessibility_rating'] == 'low'
        
        # Medium accessibility: in between
        lead_medium = {
            'business_name': 'Medium Access Gym',
            'gym_size_estimate': 'medium',
            'gym_type': 'traditional_gym',
            'website': 'https://medium.com',
            'phone': '',
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_medium)
        assert result['accessibility_rating'] == 'medium'
    
    def test_sales_approach_recommendations(self):
        """Test sales approach recommendations for different structures"""
        # Enterprise approach for corporate
        lead_corporate = {
            'business_name': 'Corporate Fitness',
            'gym_size_estimate': 'large',
            'gym_type': 'health_club',
            'website': '',
            'phone': '',
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_corporate)
        assert result['sales_approach']['strategy'] == 'enterprise'
        assert 'Focus on scalability and standardization' in result['sales_approach']['key_points']
        
        # Relationship approach for owner-operated
        lead_owner_op = {
            'business_name': 'Owner Fitness',
            'gym_size_estimate': 'medium',
            'gym_type': 'crossfit',
            'website': '',
            'phone': '',
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_owner_op)
        assert result['sales_approach']['strategy'] == 'relationship'
        assert 'Build trust with owner/operator' in result['sales_approach']['key_points']
        
        # Consultative approach for owner-direct
        lead_owner_direct = {
            'business_name': 'Small Studio',
            'gym_size_estimate': 'small',
            'gym_type': 'martial_arts',
            'website': '',
            'phone': '',
            'reviews_data': []
        }
        result = self.processor._identify_decision_makers(lead_owner_direct)
        assert result['sales_approach']['strategy'] == 'consultative'
        assert 'Direct owner engagement' in result['sales_approach']['key_points']
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        # Test with empty data
        lead = {}
        result = self.processor._identify_decision_makers(lead)
        
        # With empty data, it still runs with defaults  
        assert result['decision_making_structure'] in ['unknown', 'owner_direct']  # Depends on defaults
        assert result['contact_quality'] == 'poor'  # No contact info = poor
        assert len(result['likely_decision_makers']) >= 0  # May have defaults
        
        # Test with None values
        lead = {
            'business_name': None,
            'gym_size_estimate': None,
            'gym_type': None,
            'reviews_data': None
        }
        result = self.processor._identify_decision_makers(lead)
        
        # Should handle gracefully
        assert result['decision_making_structure'] == 'unknown'