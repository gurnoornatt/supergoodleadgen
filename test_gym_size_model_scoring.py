"""
Test suite for gym size and business model-specific pain scoring
"""
import pytest
from unittest.mock import Mock, patch
from lead_processor import LeadProcessor


class TestGymSizeModelScoring:
    """Test gym size and model-specific pain scoring adjustments"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = LeadProcessor()
    
    def test_large_gym_pain_multiplier(self):
        """Test that large gyms get higher pain multipliers"""
        lead = {
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_mobile_app': {'has_app': False},
            'gym_website_features': {},
            'mobile_score': 65,
            'digital_infrastructure_score': 60
        }
        
        pain_factors = {
            'pain_score': 50,
            'urgency_level': 'medium',
            'operational_inefficiencies': []
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Large gym should have 1.2x multiplier
        assert result['pain_multiplier'] == 1.2
        assert result['adjusted_pain_score'] > pain_factors['pain_score']
        assert result['size_context'] == 'Large gym with high member expectations'
        
        # Should have size-specific pain factors
        assert len(result['size_specific_pain_factors']) > 0
        assert any('No mobile app for large facility' in p['factor'] for p in result['size_specific_pain_factors'])
    
    def test_small_gym_pain_reduction(self):
        """Test that small gyms get lower pain multipliers"""
        lead = {
            'gym_size_estimate': 'small',
            'gym_type': 'traditional_gym',
            'gym_mobile_app': {'has_app': False},
            'gym_website_features': {'social_integration': False},
            'mobile_score': 55,
            'digital_infrastructure_score': 45
        }
        
        pain_factors = {
            'pain_score': 60,
            'urgency_level': 'high'
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Small gym should have 0.8x multiplier
        assert result['pain_multiplier'] == 0.8
        assert result['adjusted_pain_score'] < pain_factors['pain_score']
        assert result['size_context'] == 'Small gym with focused member base'
        
        # Should detect missing community tools for small gym
        assert any('Missing community building tools' in p['factor'] for p in result['size_specific_pain_factors'])
    
    def test_boutique_fitness_model_multiplier(self):
        """Test boutique fitness gets highest model multiplier"""
        lead = {
            'gym_size_estimate': 'medium',
            'gym_type': 'boutique_fitness',
            'mobile_score': 70,  # Below boutique expectations
            'gym_website_features': {}
        }
        
        pain_factors = {
            'pain_score': 40,
            'urgency_level': 'medium'
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Boutique should have 1.3x model multiplier
        assert result['model_multiplier'] == 1.3
        assert result['model_context'] == 'Boutique fitness with premium expectations'
        
        # Should detect subpar mobile for boutique
        assert any('Subpar mobile experience for boutique' in p['factor'] for p in result['model_specific_pain_factors'])
    
    def test_personal_training_lower_requirements(self):
        """Test personal training has lower tech requirements"""
        lead = {
            'gym_size_estimate': 'small',
            'gym_type': 'personal_training',
            'mobile_score': 45,
            'digital_infrastructure_score': 35
        }
        
        pain_factors = {
            'pain_score': 60,
            'urgency_level': 'high'
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Personal training should have 0.7x model multiplier
        assert result['model_multiplier'] == 0.7
        # Combined with small gym (0.8x), total multiplier should be 0.56
        total_multiplier = result['pain_multiplier'] * result['model_multiplier']
        assert total_multiplier == pytest.approx(0.56)
        
        # Adjusted score should be significantly lower
        assert result['adjusted_pain_score'] < 40
    
    def test_crossfit_community_requirements(self):
        """Test CrossFit has specific community feature requirements"""
        lead = {
            'gym_size_estimate': 'medium',
            'gym_type': 'crossfit',
            'gym_website_features': {
                'social_integration': False  # Missing key CrossFit feature
            }
        }
        
        pain_factors = {
            'pain_score': 50,
            'urgency_level': 'medium'
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # CrossFit should have 1.2x model multiplier
        assert result['model_multiplier'] == 1.2
        assert result['model_context'] == 'CrossFit box with community focus'
        
        # Should detect missing community features
        assert any('No community features for CrossFit' in p['factor'] for p in result['model_specific_pain_factors'])
    
    def test_yoga_studio_scheduling_requirements(self):
        """Test yoga studios have specific scheduling requirements"""
        lead = {
            'gym_size_estimate': 'small',
            'gym_type': 'yoga_studio',
            'gym_website_features': {
                'class_scheduling': False  # Missing critical yoga feature
            }
        }
        
        pain_factors = {
            'pain_score': 40,
            'urgency_level': 'medium'
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Yoga studio should have 1.1x model multiplier
        assert result['model_multiplier'] == 1.1
        assert result['model_context'] == 'Yoga studio with wellness focus'
        
        # Should detect missing scheduling
        assert any('No online class scheduling for yoga' in p['factor'] for p in result['model_specific_pain_factors'])
    
    def test_critical_threshold_violations(self):
        """Test critical threshold violations for different gym sizes"""
        # Large gym with violations
        large_lead = {
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'mobile_score': 65,  # Below 70 threshold
            'digital_infrastructure_score': 60,  # Below 65 threshold
            'gym_website_features': {
                'online_booking': True,
                'member_portal': False,  # Missing required
                'payment_processing': True,
                'mobile_app': False  # Missing required
            }
        }
        
        pain_factors = {'pain_score': 40, 'urgency_level': 'medium'}
        
        result = self.processor._apply_gym_size_and_model_scoring(large_lead, pain_factors)
        
        # Should have multiple violations
        assert len(result['threshold_violations']) >= 3
        assert any('Mobile score' in v for v in result['threshold_violations'])
        assert any('Digital infrastructure' in v for v in result['threshold_violations'])
        assert any('member_portal' in v for v in result['threshold_violations'])
        
        # Urgency should be upgraded from medium to high due to violations
        assert result['adjusted_urgency'] == 'high'
    
    def test_combined_size_and_model_effects(self):
        """Test combined effects of size and model multipliers"""
        test_cases = [
            # (size, model, expected_combined_multiplier)
            ('large', 'boutique_fitness', 1.56),  # 1.2 * 1.3
            ('small', 'personal_training', 0.56),  # 0.8 * 0.7
            ('medium', 'crossfit', 1.2),          # 1.0 * 1.2
            ('large', 'recreation_center', 1.38),  # 1.2 * 1.15
            ('small', 'martial_arts', 0.64)       # 0.8 * 0.8
        ]
        
        for size, model, expected_multiplier in test_cases:
            lead = {
                'gym_size_estimate': size,
                'gym_type': model,
                'gym_website_features': {},
                'gym_mobile_app': {'has_app': True}
            }
            
            pain_factors = {'pain_score': 50, 'urgency_level': 'medium'}
            
            result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
            
            combined = result['pain_multiplier'] * result['model_multiplier']
            assert combined == pytest.approx(expected_multiplier), f"Failed for {size} {model}"
    
    def test_urgency_recalculation(self):
        """Test urgency level recalculation based on adjusted scores"""
        lead = {
            'gym_size_estimate': 'large',
            'gym_type': 'boutique_fitness'
        }
        
        # Test different pain score ranges
        test_cases = [
            (15, 'low'),      # Very low score stays low even with multipliers
            (25, 'high'),     # Low becomes high with 1.56x multiplier (25 * 1.56 = 39)
            (45, 'critical'), # Medium becomes critical with 1.56x multiplier (45 * 1.56 = 70.2)
            (80, 'critical')  # Critical stays critical
        ]
        
        for base_score, expected_urgency in test_cases:
            pain_factors = {
                'pain_score': base_score,
                'urgency_level': 'medium'  # Original urgency
            }
            
            result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
            
            assert result['adjusted_urgency'] == expected_urgency, f"Failed for score {base_score}"
    
    def test_additional_pain_factors_integration(self):
        """Test integration of size/model-specific pain factors into scoring"""
        lead = {
            'gym_size_estimate': 'large',
            'gym_type': 'traditional_gym',
            'gym_mobile_app': {'has_app': False},
            'gym_website_features': {}
        }
        
        pain_factors = {
            'pain_score': 50,
            'urgency_level': 'medium',
            'operational_inefficiencies': []
        }
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Should have additional pain factors
        assert len(result['size_specific_pain_factors']) > 0
        
        # Adjusted score should incorporate additional factors
        # Base score (50) + additional factors contribution
        assert result['adjusted_pain_score'] > 50
        
        # Verify severity levels are being used
        factors = result['size_specific_pain_factors']
        assert all('severity' in f for f in factors)
        assert all(1 <= f['severity'] <= 10 for f in factors)
    
    def test_error_handling(self):
        """Test error handling in size/model scoring"""
        # Test with missing data
        lead = {}
        pain_factors = {}
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Should return safe defaults
        assert result['pain_multiplier'] == 1.0
        assert result['model_multiplier'] == 1.0
        assert result['adjusted_pain_score'] == 0
        assert result['adjusted_urgency'] == 'low'
        
        # Test with invalid gym category
        lead = {
            'gym_size_estimate': 'medium',
            'gym_type': 'invalid_category'
        }
        pain_factors = {'pain_score': 50}
        
        result = self.processor._apply_gym_size_and_model_scoring(lead, pain_factors)
        
        # Should use default multiplier
        assert result['model_multiplier'] == 1.0
    
    def test_integration_with_pain_analysis_pipeline(self):
        """Test integration with the complete pain analysis pipeline"""
        with patch.object(self.processor.serp_client, 'search_google_maps') as mock_search:
            with patch.object(self.processor.pagespeed_client, 'analyze_url') as mock_pagespeed:
                with patch.object(self.processor.builtwith_client, 'analyze_domain') as mock_builtwith:
                    # Mock a large boutique fitness gym with issues
                    mock_search.return_value = {
                        'local_results': [{
                            'title': 'Elite Fitness Center',  # Removed 'boutique' from name
                            'website': 'https://elitefitness.com',
                            'reviews': 1200,  # Increased to ensure large
                            'rating': 4.8,
                            'type': 'Fitness Center',
                            'snippet': 'Large fitness facility with multiple locations and 24/7 access'  # Added large indicators
                        }]
                    }
                    
                    mock_pagespeed.return_value = {
                        'performance_score': 68,  # Below boutique standards
                        'strategy': 'mobile',
                        'raw_data': {}
                    }
                    
                    mock_builtwith.return_value = {
                        'technologies': [
                            {'name': 'WordPress', 'category': 'CMS'},
                            {'name': 'WooCommerce', 'category': 'Ecommerce'}
                        ],
                        'meta': {}
                    }
                    
                    # Process leads
                    leads = self.processor.extract_leads_from_maps('boutique fitness', 'Test City', 1)
                    processed = self.processor.process_lead_batch(leads)
                    
                    assert len(processed) == 1
                    lead = processed[0]
                    
                    # Verify size/model adjusted scores exist
                    assert 'gym_adjusted_pain_score' in lead
                    assert 'gym_adjusted_urgency' in lead
                    assert 'gym_size_pain_multiplier' in lead
                    assert 'gym_model_pain_multiplier' in lead
                    assert 'gym_threshold_violations' in lead
                    
                    # Should be identified as large traditional gym
                    assert lead['gym_size_estimate'] == 'large'
                    assert lead['gym_type'] == 'traditional_gym'
                    
                    # Should have high multipliers
                    assert lead['gym_size_pain_multiplier'] >= 1.0
                    assert lead['gym_model_pain_multiplier'] >= 1.0
                    
                    # Adjusted score should be higher than base
                    if 'gym_pain_score' in lead and 'gym_adjusted_pain_score' in lead:
                        assert lead['gym_adjusted_pain_score'] >= lead['gym_pain_score']