"""
Test suite for gym-specific RED/GREEN classification
"""
import pytest
from unittest.mock import Mock, patch
from lead_processor import LeadProcessor


class TestGymRedGreenClassification:
    """Test gym-specific RED/GREEN classification system"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = LeadProcessor()
    
    def test_red_classification_high_pain_score(self):
        """Test RED classification for high adjusted pain score"""
        lead = {
            'business_name': 'Pain Gym',
            'gym_adjusted_pain_score': 75,
            'gym_adjusted_urgency': 'high',
            'gym_digital_infrastructure_score': 45,
            'gym_digital_infrastructure_tier': 'Poor',
            'gym_software_quality_score': 35,
            'gym_website_feature_score': 40,
            'gym_mobile_app_quality_score': 0,
            'mobile_score': 55,
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': ['Mobile score below 70', 'No member portal'],
            'gym_mobile_app': {'has_app': False},
            'status': 'green'
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'red'
        assert result['gym_classification_confidence'] in ['high', 'very_high']
        assert result['gym_action_priority'] == 'urgent'
        assert result['gym_sales_readiness'] == 'hot_lead'
        assert len(result['gym_classification_reasons']) > 0
        assert 'Adjusted pain score of 75.0' in result['gym_classification_reasons'][0]
        assert result['status'] == 'red'
        assert result['status_source'] == 'gym_specific_classification'
    
    def test_red_classification_critical_urgency(self):
        """Test RED classification for critical urgency level"""
        lead = {
            'business_name': 'Critical Gym',
            'gym_adjusted_pain_score': 65,
            'gym_adjusted_urgency': 'critical',
            'gym_digital_infrastructure_score': 35,
            'gym_digital_infrastructure_tier': 'Very Poor',
            'gym_software_quality_score': 30,
            'gym_website_feature_score': 25,
            'mobile_score': 45,
            'gym_size_estimate': 'large',
            'gym_type': 'boutique_fitness',
            'gym_threshold_violations': ['Mobile score below 70', 'Digital infrastructure below 65'],
            'gym_mobile_app': {'has_app': False}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'red'
        assert result['gym_action_priority'] == 'urgent'
        assert 'Multiple critical pain points' in str(result['gym_classification_reasons'])
        assert result['gym_classification_confidence'] in ['high', 'very_high']
    
    def test_red_classification_poor_infrastructure(self):
        """Test RED classification for poor digital infrastructure"""
        lead = {
            'business_name': 'Old School Gym',
            'gym_adjusted_pain_score': 60,
            'gym_adjusted_urgency': 'high',
            'gym_digital_infrastructure_score': 25,
            'gym_digital_infrastructure_tier': 'Very Poor',
            'gym_software_quality_score': 45,
            'gym_website_feature_score': 35,
            'mobile_score': 48,
            'gym_size_estimate': 'medium',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': False}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'red'
        assert any('Very Poor tier' in reason for reason in result['gym_classification_reasons'])
        assert any('Mobile score 48/100' in reason for reason in result['gym_classification_reasons'])
    
    def test_red_classification_multiple_violations(self):
        """Test RED classification for multiple threshold violations"""
        lead = {
            'business_name': 'Violation Gym',
            'gym_adjusted_pain_score': 55,
            'gym_adjusted_urgency': 'medium',
            'gym_digital_infrastructure_score': 50,
            'gym_digital_infrastructure_tier': 'Fair',
            'gym_software_quality_score': 50,
            'gym_website_feature_score': 45,
            'mobile_score': 60,
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': [
                'Mobile score below 70',
                'Digital infrastructure below 65',
                'Missing member portal',
                'No mobile app'
            ],
            'gym_mobile_app': {'has_app': False}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'red'
        assert any('4 critical thresholds violated' in reason for reason in result['gym_classification_reasons'])
    
    def test_yellow_classification_moderate_pain(self):
        """Test YELLOW classification for moderate pain score"""
        lead = {
            'business_name': 'Average Gym',
            'gym_adjusted_pain_score': 55,
            'gym_adjusted_urgency': 'medium',
            'gym_digital_infrastructure_score': 50,
            'gym_digital_infrastructure_tier': 'Fair',
            'gym_software_quality_score': 55,
            'gym_website_feature_score': 50,
            'mobile_score': 65,
            'gym_size_estimate': 'medium',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': False},
            'status': 'green'
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'yellow'
        assert result['gym_action_priority'] == 'medium'
        assert result['gym_sales_readiness'] == 'warm_lead'
        assert result['status'] == 'yellow'
        assert result['status_source'] == 'gym_specific_classification'
    
    def test_yellow_classification_high_urgency(self):
        """Test YELLOW classification for high urgency but not critical"""
        lead = {
            'business_name': 'Urgent Gym',
            'gym_adjusted_pain_score': 45,
            'gym_adjusted_urgency': 'high',
            'gym_digital_infrastructure_score': 55,
            'gym_digital_infrastructure_tier': 'Fair',
            'gym_software_quality_score': 58,
            'gym_website_feature_score': 55,
            'mobile_score': 68,
            'gym_size_estimate': 'small',
            'gym_type': 'yoga_studio',
            'gym_threshold_violations': ['Missing class scheduling'],
            'gym_mobile_app': {'has_app': False}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'yellow'
        assert 'Several important pain points' in str(result['gym_classification_reasons'])
    
    def test_green_classification_good_infrastructure(self):
        """Test GREEN classification for good digital infrastructure"""
        lead = {
            'business_name': 'Modern Gym',
            'gym_adjusted_pain_score': 30,
            'gym_adjusted_urgency': 'low',
            'gym_digital_infrastructure_score': 75,
            'gym_digital_infrastructure_tier': 'Good',
            'gym_software_quality_score': 80,
            'gym_website_feature_score': 85,
            'gym_mobile_app_quality_score': 75,
            'mobile_score': 82,
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': True}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(lead)
        
        assert result['gym_classification'] == 'green'
        assert result['gym_action_priority'] == 'low'
        assert result['gym_sales_readiness'] == 'not_ready'
        assert 'Digital infrastructure meets current needs' in result['gym_classification_reasons'][0]
    
    def test_classification_summary_generation(self):
        """Test classification summary generation for different classifications"""
        # Test RED summary
        red_lead = {
            'gym_adjusted_pain_score': 75,
            'gym_adjusted_urgency': 'critical',
            'gym_digital_infrastructure_score': 30,
            'gym_digital_infrastructure_tier': 'Very Poor',
            'gym_software_quality_score': 25,
            'gym_website_feature_score': 20,
            'mobile_score': 40,
            'gym_size_estimate': 'large',
            'gym_type': 'boutique_fitness',
            'gym_threshold_violations': ['Multiple'],
            'gym_mobile_app': {'has_app': False}
        }
        
        red_result = self.processor._apply_gym_specific_red_green_classification(red_lead)
        assert 'urgent need for modern gym management solutions' in red_result['gym_classification_summary']
        assert 'Boutique Fitness' in red_result['gym_classification_summary']
        
        # Test YELLOW summary
        yellow_lead = {
            'gym_adjusted_pain_score': 55,
            'gym_adjusted_urgency': 'medium',
            'gym_digital_infrastructure_score': 50,
            'gym_digital_infrastructure_tier': 'Fair',
            'gym_software_quality_score': 55,
            'gym_website_feature_score': 50,
            'mobile_score': 65,
            'gym_size_estimate': 'medium',
            'gym_type': 'crossfit',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': False}
        }
        
        yellow_result = self.processor._apply_gym_specific_red_green_classification(yellow_lead)
        assert 'moderate potential for improvement' in yellow_result['gym_classification_summary']
        assert 'Crossfit' in yellow_result['gym_classification_summary']
    
    def test_confidence_levels(self):
        """Test classification confidence levels based on criteria"""
        # Very high confidence (3+ critical factors)
        very_high_lead = {
            'business_name': 'High Confidence Gym',
            'gym_adjusted_pain_score': 80,
            'gym_adjusted_urgency': 'critical',
            'gym_digital_infrastructure_score': 25,
            'gym_digital_infrastructure_tier': 'Very Poor',
            'gym_software_quality_score': 30,
            'gym_website_feature_score': 20,
            'mobile_score': 35,
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': ['Many'],
            'gym_mobile_app': {'has_app': False}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(very_high_lead)
        assert result['gym_classification'] == 'red'
        assert result['gym_classification_confidence'] == 'very_high'
    
    def test_mobile_app_criteria(self):
        """Test mobile app availability criteria for different gym types"""
        # Large gym without app and other issues should be RED
        large_no_app = {
            'business_name': 'Large No App Gym',
            'gym_adjusted_pain_score': 55,  # Increased to trigger yellow criteria
            'gym_adjusted_urgency': 'high',  # Changed to high urgency
            'gym_digital_infrastructure_score': 45,  # Lowered to Poor tier
            'gym_digital_infrastructure_tier': 'Poor',
            'gym_software_quality_score': 55,  # Lowered to trigger yellow
            'gym_website_feature_score': 50,  # Lowered
            'mobile_score': 65,  # Lowered to yellow range
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': False}
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(large_no_app)
        assert result['gym_classification'] == 'red'
        # Check that the mobile app issue is mentioned in the classification
        all_reasons = ' '.join(result['gym_classification_reasons'])
        assert 'Poor digital infrastructure' in all_reasons or 'mobile app' in all_reasons.lower()
        
        # Boutique fitness without app and other yellow flags should be YELLOW
        boutique_no_app = {
            'business_name': 'Boutique No App Gym',
            'gym_adjusted_pain_score': 52,  # Moderate pain score
            'gym_adjusted_urgency': 'medium',  # Medium urgency
            'gym_digital_infrastructure_score': 55,  # Fair infrastructure
            'gym_digital_infrastructure_tier': 'Fair',
            'gym_software_quality_score': 58,  # Almost outdated
            'gym_website_feature_score': 55,  # Incomplete features
            'mobile_score': 68,  # Subpar mobile
            'gym_size_estimate': 'medium',
            'gym_type': 'boutique_fitness',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': False}
        }
        
        result2 = self.processor._apply_gym_specific_red_green_classification(boutique_no_app)
        assert result2['gym_classification'] == 'yellow'
        assert len(result2['gym_classification_reasons']) > 0
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Missing data
        incomplete_lead = {
            'business_name': 'Incomplete Gym'
        }
        
        result = self.processor._apply_gym_specific_red_green_classification(incomplete_lead)
        assert result['gym_classification'] in ['green', 'yellow', 'red', 'unknown']
        assert 'gym_classification_confidence' in result
        assert 'gym_classification_reasons' in result
        
        # All zeros
        zero_lead = {
            'business_name': 'Zero Score Gym',
            'gym_adjusted_pain_score': 0,
            'gym_adjusted_urgency': 'low',
            'gym_digital_infrastructure_score': 0,
            'gym_digital_infrastructure_tier': 'Very Poor',
            'gym_software_quality_score': 0,
            'gym_website_feature_score': 0,
            'mobile_score': 0,
            'gym_size_estimate': 'small',
            'gym_type': 'personal_training',
            'gym_threshold_violations': [],
            'gym_mobile_app': {'has_app': False}
        }
        
        result2 = self.processor._apply_gym_specific_red_green_classification(zero_lead)
        assert result2['gym_classification'] == 'red'  # Should be RED due to all poor scores
    
    def test_integration_with_pipeline(self):
        """Test integration with the complete lead processing pipeline"""
        with patch.object(self.processor.serp_client, 'search_google_maps') as mock_search:
            with patch.object(self.processor.pagespeed_client, 'analyze_url') as mock_pagespeed:
                with patch.object(self.processor.builtwith_client, 'analyze_domain') as mock_builtwith:
                    # Mock a gym with mixed signals
                    mock_search.return_value = {
                        'local_results': [{
                            'title': 'FitZone Gym',
                            'website': 'https://fitzone.com',
                            'reviews': 450,
                            'rating': 4.2,
                            'type': 'Gym',
                            'snippet': 'Modern fitness facility with group classes'
                        }]
                    }
                    
                    mock_pagespeed.return_value = {
                        'performance_score': 58,
                        'strategy': 'mobile',
                        'raw_data': {}
                    }
                    
                    mock_builtwith.return_value = {
                        'technologies': [
                            {'name': 'WordPress', 'category': 'CMS'},
                            {'name': 'MindBody', 'category': 'Scheduling'}
                        ],
                        'meta': {}
                    }
                    
                    leads = self.processor.extract_leads_from_maps('gym', 'Test City', 1)
                    processed = self.processor.process_lead_batch(leads)
                    
                    assert len(processed) == 1
                    lead = processed[0]
                    
                    # Verify gym classification fields exist
                    assert 'gym_classification' in lead
                    assert 'gym_classification_confidence' in lead
                    assert 'gym_classification_reasons' in lead
                    assert 'gym_action_priority' in lead
                    assert 'gym_sales_readiness' in lead
                    assert 'gym_classification_summary' in lead
                    
                    # Should have some classification
                    assert lead['gym_classification'] in ['red', 'yellow', 'green']
                    assert len(lead['gym_classification_reasons']) > 0
                    assert lead['gym_classification_summary'] != ''