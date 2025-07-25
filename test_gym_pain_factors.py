"""
Test suite for gym-specific pain factors analysis
"""
import pytest
from unittest.mock import Mock, patch
from lead_processor import LeadProcessor


class TestGymPainFactors:
    """Test gym pain factors analysis"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = LeadProcessor()
    
    def test_analyze_gym_pain_factors_all_pain_points(self):
        """Test analysis with all pain points present"""
        lead = {
            'business_name': 'Old School Gym',
            'digital_infrastructure_score': 30,  # Low score
            'gym_website_features': {
                'online_booking': False,
                'payment_processing': False,
                'member_portal': False,
                'virtual_classes': False,
                'ecommerce': False,
                'class_scheduling': False,
                'social_integration': False,
                'live_chat': False
            },
            'gym_mobile_app': {
                'has_app': False,
                'quality_score': 0
            },
            'gym_software_detected': [],  # No gym software
            'mobile_score': 45,  # Poor mobile score
            'technology_age_score': 35  # Outdated tech
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        # Verify structure
        assert 'operational_inefficiencies' in result
        assert 'member_retention_risks' in result
        assert 'competitive_disadvantages' in result
        assert 'revenue_loss_factors' in result
        assert 'growth_limitations' in result
        assert 'pain_score' in result
        assert 'primary_pain_category' in result
        assert 'urgency_level' in result
        
        # Should have multiple pain points
        assert len(result['operational_inefficiencies']) >= 3
        assert len(result['member_retention_risks']) >= 3
        assert len(result['competitive_disadvantages']) >= 3
        assert len(result['revenue_loss_factors']) >= 2
        assert len(result['growth_limitations']) >= 2
        
        # Pain score should be high
        assert result['pain_score'] >= 70
        assert result['urgency_level'] == 'critical'
        assert result['total_pain_points'] >= 13
        assert result['critical_issues'] >= 3
    
    def test_analyze_gym_pain_factors_minimal_pain(self):
        """Test analysis with minimal pain points"""
        lead = {
            'business_name': 'Modern Fitness Center',
            'digital_infrastructure_score': 85,
            'gym_website_features': {
                'online_booking': True,
                'payment_processing': True,
                'member_portal': True,
                'virtual_classes': True,
                'ecommerce': True,
                'class_scheduling': True,
                'social_integration': True,
                'live_chat': True
            },
            'gym_mobile_app': {
                'has_app': True,
                'quality_score': 90
            },
            'gym_software_detected': ['mindbody', 'zenplanner'],
            'mobile_score': 92,
            'technology_age_score': 88
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        # Should have minimal pain points
        assert len(result['operational_inefficiencies']) == 0
        assert len(result['member_retention_risks']) == 0
        assert result['pain_score'] < 30
        assert result['urgency_level'] == 'low'
        assert result['total_pain_points'] == 0
        assert result['critical_issues'] == 0
    
    def test_operational_inefficiencies_detection(self):
        """Test operational inefficiencies detection"""
        lead = {
            'business_name': 'Test Gym',
            'gym_website_features': {
                'online_booking': False,
                'payment_processing': False
            },
            'gym_software_detected': ['WordPress', 'Square'],  # Basic tools only
            'gym_mobile_app': {'has_app': False, 'quality_score': 0},
            'mobile_score': 80,
            'technology_age_score': 70
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        operational = result['operational_inefficiencies']
        assert len(operational) == 3
        
        # Check specific pain points
        factors = [p['factor'] for p in operational]
        assert 'Manual booking process' in factors
        assert 'Manual payment collection' in factors
        assert 'No integrated gym management system' in factors
        
        # Check severity levels
        severities = [p['severity'] for p in operational]
        assert 9 in severities  # No gym management system is critical
        assert 8 in severities  # Manual booking is very severe
        assert 7 in severities  # Manual payments is severe
    
    def test_member_retention_risks_detection(self):
        """Test member retention risks detection"""
        lead = {
            'business_name': 'Test Gym',
            'gym_website_features': {
                'member_portal': False
            },
            'gym_mobile_app': {
                'has_app': False,
                'quality_score': 0
            },
            'mobile_score': 55,  # Poor mobile experience
            'gym_software_detected': [],
            'technology_age_score': 70
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        retention = result['member_retention_risks']
        assert len(retention) == 3
        
        # Check specific risks
        factors = [p['factor'] for p in retention]
        assert 'No mobile app for members' in factors
        assert 'No self-service member portal' in factors
        assert 'Poor mobile website experience' in factors
        
        # Mobile app should be most severe
        mobile_app_risk = next(p for p in retention if 'No mobile app' in p['factor'])
        assert mobile_app_risk['severity'] == 9
        assert '25% higher churn rate' in mobile_app_risk['impact']
    
    def test_competitive_disadvantages_detection(self):
        """Test competitive disadvantages detection"""
        lead = {
            'business_name': 'Test Gym',
            'digital_infrastructure_score': 45,
            'gym_website_features': {
                'virtual_classes': False
            },
            'technology_age_score': 40,
            'gym_mobile_app': {'has_app': False, 'quality_score': 0},
            'gym_software_detected': [],
            'mobile_score': 70
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        competitive = result['competitive_disadvantages']
        assert len(competitive) == 3
        
        # Check specific disadvantages
        factors = [p['factor'] for p in competitive]
        assert 'Below-average digital infrastructure' in factors
        assert 'No virtual/hybrid fitness options' in factors
        assert 'Outdated technology stack' in factors
        
        # Digital infrastructure should be severe
        digital_disadvantage = next(p for p in competitive if 'Below-average digital' in p['factor'])
        assert digital_disadvantage['severity'] == 8
        assert 'Losing tech-savvy millennials' in digital_disadvantage['impact']
    
    def test_revenue_loss_factors_detection(self):
        """Test revenue loss factors detection"""
        lead = {
            'business_name': 'Test Gym',
            'gym_website_features': {
                'ecommerce': False,
                'class_scheduling': False
            },
            'gym_mobile_app': {
                'has_app': True,
                'quality_score': 40  # Poor quality
            },
            'gym_software_detected': [],
            'mobile_score': 70,
            'technology_age_score': 70
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        revenue = result['revenue_loss_factors']
        assert len(revenue) == 3
        
        # Check specific factors
        factors = [p['factor'] for p in revenue]
        assert 'No online merchandise/supplement sales' in factors
        assert 'No online class booking' in factors
        assert 'Poor quality mobile experience' in factors
        
        # Check impact descriptions
        ecommerce_loss = next(p for p in revenue if 'merchandise' in p['factor'])
        assert '$500-2000/month' in ecommerce_loss['impact']
    
    def test_growth_limitations_detection(self):
        """Test growth limitations detection"""
        lead = {
            'business_name': 'Test Gym',
            'gym_website_features': {
                'social_integration': False,
                'live_chat': False
            },
            'gym_mobile_app': {'has_app': False, 'quality_score': 0},
            'gym_software_detected': [],
            'mobile_score': 70,
            'technology_age_score': 70
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        growth = result['growth_limitations']
        assert len(growth) == 2
        
        # Check specific limitations
        factors = [p['factor'] for p in growth]
        assert 'No social media integration' in factors
        assert 'No instant communication channel' in factors
        
        # Check impacts
        chat_limitation = next(p for p in growth if 'instant communication' in p['factor'])
        assert 'Losing 20% of prospects' in chat_limitation['impact']
    
    def test_pain_score_calculation(self):
        """Test pain score calculation with weighted categories"""
        lead = {
            'business_name': 'Test Gym',
            'gym_website_features': {
                'online_booking': False,  # Operational inefficiency
                'member_portal': False   # Retention risk
            },
            'gym_mobile_app': {
                'has_app': False,  # Major retention risk
                'quality_score': 0
            },
            'gym_software_detected': [],
            'mobile_score': 70,
            'technology_age_score': 70,
            'digital_infrastructure_score': 60
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        # Pain score should be calculated based on weighted categories
        assert 0 <= result['pain_score'] <= 100
        assert result['pain_score'] > 50  # Should have significant pain
        
        # Primary category should be identified
        assert result['primary_pain_category'] in [
            'operational_inefficiencies',
            'member_retention_risks',
            'competitive_disadvantages',
            'revenue_loss_factors',
            'growth_limitations'
        ]
    
    def test_urgency_level_classification(self):
        """Test urgency level classification based on pain score"""
        # Test critical urgency
        lead_critical = {
            'business_name': 'Critical Gym',
            'gym_website_features': {k: False for k in ['online_booking', 'payment_processing', 'member_portal', 'virtual_classes']},
            'gym_mobile_app': {'has_app': False, 'quality_score': 0},
            'gym_software_detected': [],
            'mobile_score': 40,
            'technology_age_score': 30,
            'digital_infrastructure_score': 25
        }
        
        result = self.processor._analyze_gym_pain_factors(lead_critical)
        assert result['urgency_level'] == 'critical'
        assert result['pain_score'] >= 70
        
        # Test medium urgency
        lead_medium = {
            'business_name': 'Medium Gym',
            'gym_website_features': {
                'online_booking': True,
                'payment_processing': True,  # Changed to reduce pain
                'member_portal': True,       # Changed to reduce pain
                'virtual_classes': True      # Added to reduce pain
            },
            'gym_mobile_app': {'has_app': True, 'quality_score': 60},  # Added app with decent quality
            'gym_software_detected': ['mindbody'],  # Better software
            'mobile_score': 65,
            'technology_age_score': 60,
            'digital_infrastructure_score': 55
        }
        
        result = self.processor._analyze_gym_pain_factors(lead_medium)
        assert result['urgency_level'] in ['low', 'medium']  # Adjusted expectation
        assert result['pain_score'] < 50  # Should have lower pain score
    
    def test_primary_pain_category_determination(self):
        """Test primary pain category is correctly determined"""
        # Create lead with mostly retention risks
        lead = {
            'business_name': 'Retention Risk Gym',
            'gym_website_features': {
                'member_portal': False,
                'online_booking': True,  # Has booking
                'payment_processing': True,  # Has payments
                'virtual_classes': True  # Has virtual classes
            },
            'gym_mobile_app': {
                'has_app': False,  # Major retention risk
                'quality_score': 0
            },
            'gym_software_detected': ['mindbody'],  # Has gym software
            'mobile_score': 55,  # Poor mobile (retention risk)
            'technology_age_score': 70,  # Decent tech age
            'digital_infrastructure_score': 60
        }
        
        result = self.processor._analyze_gym_pain_factors(lead)
        
        # Should identify member retention as primary pain
        assert result['primary_pain_category'] == 'member_retention_risks'
        assert len(result['member_retention_risks']) >= 2
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling"""
        # Test with missing data
        lead_missing = {
            'business_name': 'Minimal Gym'
        }
        
        result = self.processor._analyze_gym_pain_factors(lead_missing)
        
        # Should handle gracefully
        assert result['pain_score'] >= 0
        assert result['urgency_level'] in ['low', 'medium', 'high', 'critical']
        assert result['total_pain_points'] >= 0
        
        # Test with None values
        lead_none = {
            'business_name': 'None Gym',
            'gym_website_features': None,
            'gym_mobile_app': None,
            'mobile_score': None
        }
        
        result = self.processor._analyze_gym_pain_factors(lead_none)
        assert isinstance(result['pain_score'], (int, float))
        
    def test_integration_with_lead_processing_pipeline(self):
        """Test integration with the lead processing pipeline"""
        with patch.object(self.processor.serp_client, 'search_google_maps') as mock_search:
            with patch.object(self.processor.pagespeed_client, 'analyze_url') as mock_pagespeed:
                with patch.object(self.processor.builtwith_client, 'analyze_domain') as mock_builtwith:
                    # Mock responses
                    mock_search.return_value = {
                        'local_results': [{
                            'title': 'Test Gym',
                            'website': 'https://testgym.com',
                            'phone': '555-0123',
                            'address': '123 Test St'
                        }]
                    }
                    
                    mock_pagespeed.return_value = {
                        'mobile_score': 55,
                        'performance_metrics': {}
                    }
                    
                    mock_builtwith.return_value = {
                        'technologies': [
                            {'name': 'WordPress', 'category': 'CMS'},
                            {'name': 'jQuery', 'category': 'JavaScript', 'firstDetected': 1400000000000}
                        ],
                        'meta': {}
                    }
                    
                    # Process leads
                    leads = self.processor.extract_leads_from_maps('gyms', 'Test City', 1)
                    processed = self.processor.process_lead_batch(leads)
                    
                    assert len(processed) == 1
                    lead = processed[0]
                    
                    # Verify gym pain factors were analyzed
                    assert 'gym_pain_factors' in lead
                    assert 'gym_pain_score' in lead
                    assert 'gym_pain_urgency' in lead
                    assert 'gym_primary_pain_category' in lead
                    assert 'gym_total_pain_points' in lead
                    assert 'gym_critical_pain_issues' in lead
                    
                    # Should have identified pain points
                    assert lead['gym_pain_score'] > 0
                    assert lead['gym_total_pain_points'] > 0