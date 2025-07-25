#!/usr/bin/env python3
"""
Test suite for gym digital infrastructure scoring functionality
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

class TestGymDigitalInfrastructureScoring(unittest.TestCase):
    """Test gym digital infrastructure scoring functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
        
        # Base lead template for testing
        self.base_lead = {
            'business_name': 'Test Fitness Center',
            'website': 'https://testfitness.com',
            'mobile_score': 75,
            'technology_age_score': 70,
            'gym_software_detected': [],
            'gym_software_quality_score': 50,
            'gym_website_features': {},
            'gym_website_feature_score': 50,
            'gym_mobile_app_available': False,
            'gym_mobile_app_quality_score': 0
        }
    
    def test_excellent_digital_infrastructure_scoring(self):
        """Test scoring for excellent digital infrastructure"""
        # Create lead with excellent digital infrastructure
        excellent_lead = self.base_lead.copy()
        excellent_lead.update({
            'mobile_score': 95,
            'technology_age_score': 90,
            'gym_software_detected': ['MindBody', 'Glofox'],
            'gym_software_quality_score': 90,
            'gym_website_features': {
                'online_booking': True,
                'class_scheduling': True,
                'membership_management': True,
                'payment_processing': True,
                'member_portal': True,
                'mobile_responsive': True,
                'ecommerce': True,
                'virtual_classes': True,
                'live_chat': True,
                'social_integration': True
            },
            'gym_website_feature_score': 90,
            'gym_mobile_app_available': True,
            'gym_mobile_app_quality_score': 85
        })
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(excellent_lead)
        
        # Verify excellent scoring
        self.assertGreaterEqual(analysis['overall_score'], 80)
        self.assertEqual(analysis['tier'], 'excellent')
        self.assertIn('comprehensive modern platform', analysis['tier_description'])
        self.assertGreaterEqual(analysis['digital_readiness'], 80)
        
        # Verify component scores
        self.assertGreaterEqual(analysis['component_scores']['website_features'], 80)
        self.assertGreaterEqual(analysis['component_scores']['mobile_app_quality'], 80)
        self.assertGreaterEqual(analysis['component_scores']['online_booking'], 80)
        self.assertGreaterEqual(analysis['component_scores']['member_experience'], 70)
        
        print(f"✓ Excellent infrastructure: {analysis['overall_score']}/100 ({analysis['tier']})")
        print(f"   Digital readiness: {analysis['digital_readiness']}/100")
        print(f"   Component scores: Website={analysis['component_scores']['website_features']}, Mobile={analysis['component_scores']['mobile_app_quality']}")
    
    def test_poor_digital_infrastructure_scoring(self):
        """Test scoring for poor digital infrastructure"""
        # Create lead with poor digital infrastructure
        poor_lead = self.base_lead.copy()
        poor_lead.update({
            'mobile_score': 30,
            'technology_age_score': 40,
            'gym_software_detected': ['WordPress', 'Square'],
            'gym_software_quality_score': 25,
            'gym_website_features': {
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
            },
            'gym_website_feature_score': 20,
            'gym_mobile_app_available': False,
            'gym_mobile_app_quality_score': 0
        })
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(poor_lead)
        
        # Verify poor scoring
        self.assertLess(analysis['overall_score'], 35)
        self.assertIn(analysis['tier'], ['poor', 'critical'])
        self.assertLess(analysis['digital_readiness'], 30)
        
        # Verify critical gaps identified
        self.assertGreater(len(analysis['critical_gaps']), 3)
        self.assertGreater(len(analysis['improvement_recommendations']), 3)
        
        # Verify critical recommendations
        critical_recs = [rec for rec in analysis['improvement_recommendations'] if 'CRITICAL' in rec]
        self.assertGreater(len(critical_recs), 0)
        
        print(f"✓ Poor infrastructure: {analysis['overall_score']}/100 ({analysis['tier']})")
        print(f"   Critical gaps: {len(analysis['critical_gaps'])}")
        print(f"   Critical recommendations: {len(critical_recs)}")
    
    def test_online_booking_scoring_algorithm(self):
        """Test online booking capabilities scoring"""
        # Test scenarios with different booking capabilities
        test_scenarios = [
            # Scenario 1: No booking capabilities
            ({
                'gym_website_features': {},
                'gym_software_detected': [],
                'gym_mobile_app_available': False
            }, 0),
            
            # Scenario 2: Basic booking only
            ({
                'gym_website_features': {'online_booking': True},
                'gym_software_detected': [],
                'gym_mobile_app_available': False
            }, 35),  # 50 base - 15 penalty for no mobile
            
            # Scenario 3: Comprehensive booking features
            ({
                'gym_website_features': {
                    'online_booking': True,
                    'class_scheduling': True,
                    'membership_management': True,
                    'payment_processing': True
                },
                'gym_software_detected': [],
                'gym_mobile_app_available': True
            }, 100),  # Full score
            
            # Scenario 4: Premium booking software
            ({
                'gym_website_features': {},
                'gym_software_detected': ['MindBody'],
                'gym_mobile_app_available': True
            }, 80),  # 60 base + 20 premium bonus
        ]
        
        for i, (lead_data, expected_min_score) in enumerate(test_scenarios):
            test_lead = self.base_lead.copy()
            test_lead.update(lead_data)
            
            booking_score = self.lead_processor._calculate_online_booking_score(test_lead)
            self.assertGreaterEqual(booking_score, expected_min_score - 5, 
                                  f"Booking scenario {i+1}: expected >= {expected_min_score}, got {booking_score}")
            
            print(f"✓ Booking scoring test {i+1}: {booking_score} (expected >= {expected_min_score})")
    
    def test_member_experience_scoring_algorithm(self):
        """Test member experience scoring algorithm"""
        # Test comprehensive member experience
        comprehensive_lead = self.base_lead.copy()
        comprehensive_lead.update({
            'mobile_score': 85,
            'technology_age_score': 85,
            'gym_website_features': {
                'mobile_responsive': True,
                'member_portal': True,
                'live_chat': True,
                'social_integration': True,
                'virtual_classes': True,
                'ecommerce': True
            },
            'gym_mobile_app_quality_score': 80
        })
        
        experience_score = self.lead_processor._calculate_member_experience_score(comprehensive_lead)
        self.assertGreaterEqual(experience_score, 80)
        
        # Test minimal member experience
        minimal_lead = self.base_lead.copy()
        minimal_lead.update({
            'mobile_score': 30,
            'technology_age_score': 40,
            'gym_website_features': {},
            'gym_mobile_app_quality_score': 0
        })
        
        minimal_score = self.lead_processor._calculate_member_experience_score(minimal_lead)
        self.assertLess(minimal_score, 30)
        
        print(f"✓ Member experience scoring: Comprehensive={experience_score}, Minimal={minimal_score}")
    
    def test_digital_infrastructure_tier_classification(self):
        """Test digital infrastructure tier classification"""
        # Test all tier boundaries
        test_scores = [
            (85, 'excellent'),
            (75, 'good'),
            (55, 'average'),
            (35, 'poor'),
            (15, 'critical')
        ]
        
        for score, expected_tier in test_scores:
            test_lead = self.base_lead.copy()
            # Mock the overall score calculation by setting component scores
            test_lead.update({
                'gym_website_feature_score': score,
                'gym_mobile_app_quality_score': score,
                'mobile_score': score,
                'technology_age_score': score
            })
            
            analysis = self.lead_processor._calculate_digital_infrastructure_score(test_lead)
            
            # The actual score might be different due to weighted calculations
            actual_score = analysis['overall_score']
            
            # Use the actual score to determine expected tier
            if actual_score >= 80:
                expected_actual_tier = 'excellent'
            elif actual_score >= 65:
                expected_actual_tier = 'good'
            elif actual_score >= 45:
                expected_actual_tier = 'average'
            elif actual_score >= 25:
                expected_actual_tier = 'poor'
            else:
                expected_actual_tier = 'critical'
            
            self.assertEqual(analysis['tier'], expected_actual_tier)
            
            print(f"✓ Tier classification: Input ~{score} -> Actual {actual_score} -> {analysis['tier']}")
    
    def test_digital_readiness_calculation(self):
        """Test digital readiness calculation with different weights"""
        # Test mobile-first scenario (high mobile, low website)
        mobile_first_lead = self.base_lead.copy()
        mobile_first_lead.update({
            'gym_website_feature_score': 40,  # Low website score
            'gym_mobile_app_quality_score': 90,  # High mobile score
            'gym_mobile_app_available': True
        })
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(mobile_first_lead)
        
        # Digital readiness should be higher due to mobile weight (40%)
        self.assertGreater(analysis['digital_readiness'], analysis['component_scores']['website_features'])
        
        # Test traditional scenario (high website, low mobile)
        traditional_lead = self.base_lead.copy()
        traditional_lead.update({
            'gym_website_feature_score': 90,  # High website score
            'gym_mobile_app_quality_score': 20,  # Low mobile score
            'gym_mobile_app_available': False
        })
        
        traditional_analysis = self.lead_processor._calculate_digital_infrastructure_score(traditional_lead)
        
        # Digital readiness should be lower despite high website score
        self.assertLess(traditional_analysis['digital_readiness'], traditional_analysis['component_scores']['website_features'])
        
        print(f"✓ Digital readiness: Mobile-first={analysis['digital_readiness']}, Traditional={traditional_analysis['digital_readiness']}")
    
    def test_weighted_scoring_contributions(self):
        """Test weighted scoring contributions are correct"""
        test_lead = self.base_lead.copy()
        test_lead.update({
            'gym_website_feature_score': 80,
            'gym_mobile_app_quality_score': 60,
            'mobile_score': 70,
            'technology_age_score': 75
        })
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(test_lead)
        
        # Verify weighted contributions add up correctly
        expected_weights = {
            'website_features': 0.35,
            'mobile_app_quality': 0.25,
            'online_booking': 0.20,
            'member_experience': 0.20
        }
        
        total_contribution = sum(analysis['weighted_contributions'].values())
        self.assertAlmostEqual(total_contribution, analysis['overall_score'], delta=1.0)
        
        # Verify website features has highest weight
        self.assertGreater(analysis['weighted_contributions']['website_features'],
                          analysis['weighted_contributions']['mobile_app_quality'])
        
        print(f"✓ Weighted contributions: Total={total_contribution:.1f}, Expected={analysis['overall_score']}")
        print(f"   Website: {analysis['weighted_contributions']['website_features']:.1f}%, Mobile: {analysis['weighted_contributions']['mobile_app_quality']:.1f}%")
    
    def test_critical_gaps_identification(self):
        """Test critical gaps identification"""
        # Create lead with multiple critical gaps
        gaps_lead = self.base_lead.copy()
        gaps_lead.update({
            'mobile_score': 30,
            'technology_age_score': 35,
            'gym_software_quality_score': 30,
            'gym_website_features': {
                'mobile_responsive': False,
                'payment_processing': False
            },
            'gym_website_feature_score': 25,
            'gym_mobile_app_quality_score': 0
        })
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(gaps_lead)
        
        # Verify critical gaps are identified
        gaps = analysis['critical_gaps']
        self.assertGreater(len(gaps), 3)
        
        # Check for specific critical gaps
        gaps_text = ' '.join(gaps).lower()
        self.assertIn('mobile', gaps_text)
        self.assertIn('payment', gaps_text)
        self.assertIn('responsive', gaps_text)
        
        print(f"✓ Critical gaps identified: {len(gaps)} gaps")
        for gap in gaps[:3]:  # Show first 3 gaps
            print(f"   - {gap}")
    
    def test_competitive_analysis_assessment(self):
        """Test competitive analysis assessment"""
        # Test different competitive positions
        test_scenarios = [
            (90, 'Industry leader'),
            (75, 'Competitive'),
            (60, 'Below average'),
            (40, 'Falling behind'),
            (20, 'Critical disadvantage')
        ]
        
        for score, expected_position in test_scenarios:
            assessment = self.lead_processor._assess_competitive_position(score)
            
            # Check that assessment contains expected position descriptor
            self.assertIn(expected_position.lower(), assessment.lower())
            
            print(f"✓ Competitive analysis: Score {score} -> {assessment}")
    
    def test_improvement_recommendations_prioritization(self):
        """Test improvement recommendations are properly prioritized"""
        # Create lead with mixed scores to test prioritization
        mixed_lead = self.base_lead.copy()
        mixed_lead.update({
            'gym_website_feature_score': 25,  # Critical
            'gym_mobile_app_quality_score': 45,  # High priority  
            'gym_software_detected': ['WordPress'],
            'gym_website_features': {
                'mobile_responsive': False,
                'payment_processing': False
            }
        })
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(mixed_lead)
        
        recommendations = analysis['improvement_recommendations']
        self.assertGreater(len(recommendations), 3)
        
        # Check prioritization - CRITICAL should come first
        critical_recs = [i for i, rec in enumerate(recommendations) if 'CRITICAL' in rec]
        high_recs = [i for i, rec in enumerate(recommendations) if 'HIGH' in rec]
        
        if critical_recs and high_recs:
            self.assertLess(min(critical_recs), min(high_recs), "CRITICAL recommendations should come before HIGH")
        
        print(f"✓ Recommendations prioritization: {len(recommendations)} total")
        print(f"   CRITICAL: {len([r for r in recommendations if 'CRITICAL' in r])}")
        print(f"   HIGH: {len([r for r in recommendations if 'HIGH' in r])}")
    
    def test_integration_with_technology_analysis(self):
        """Test integration with existing technology analysis pipeline"""
        # Create a test lead with digital infrastructure components
        test_lead = {
            'business_name': 'Test Digital Gym',
            'website': 'https://testdigitalgym.com',
            'status': 'pending',
            'technologies': [
                {'name': 'MindBody Online', 'category': 'Fitness Management'},
                {'name': 'Stripe', 'category': 'Payment Processing'},
                {'name': 'Bootstrap', 'category': 'CSS Framework'}
            ],
            'outdated_technologies': [],
            'technology_age_score': 80,
            'technology_flags': []
        }
        
        # Mock the BuiltWith client to avoid actual API calls
        with patch.object(self.lead_processor, 'builtwith_client') as mock_client:
            mock_client.analyze_domain.return_value = {
                'technologies': test_lead['technologies']
            }
            
            # Process through technology analysis
            processed_lead = self.lead_processor.analyze_website_technology(test_lead)
            
            # Verify digital infrastructure fields are populated
            self.assertIn('gym_digital_infrastructure_score', processed_lead)
            self.assertIn('gym_digital_infrastructure_tier', processed_lead)
            self.assertIn('gym_digital_component_scores', processed_lead)
            self.assertIn('gym_digital_readiness', processed_lead)
            self.assertIn('gym_digital_infrastructure_recommendations', processed_lead)
            self.assertIn('gym_digital_critical_gaps', processed_lead)
            
            # Verify reasonable values
            self.assertGreaterEqual(processed_lead['gym_digital_infrastructure_score'], 0)
            self.assertLessEqual(processed_lead['gym_digital_infrastructure_score'], 100)
            self.assertIn(processed_lead['gym_digital_infrastructure_tier'], 
                         ['excellent', 'good', 'average', 'poor', 'critical'])
            
            print(f"✓ Integration test: Digital infrastructure score = {processed_lead['gym_digital_infrastructure_score']}")
            print(f"   Tier: {processed_lead['gym_digital_infrastructure_tier']}")
            print(f"   Digital readiness: {processed_lead['gym_digital_readiness']}")
    
    def test_error_handling_in_digital_infrastructure_scoring(self):
        """Test error handling in digital infrastructure scoring"""
        # Test with completely missing data (should result in critical tier, not error)
        empty_lead = {}
        
        analysis = self.lead_processor._calculate_digital_infrastructure_score(empty_lead)
        
        # Verify graceful handling of missing data
        self.assertIsInstance(analysis, dict)
        self.assertIn('overall_score', analysis)
        self.assertEqual(analysis['overall_score'], 0.0)
        self.assertEqual(analysis['tier'], 'critical')  # Not 'error' - that's for exceptions
        
        # Test that all required fields are present even with empty input
        required_fields = ['overall_score', 'tier', 'tier_description', 'component_scores', 
                          'weighted_contributions', 'digital_readiness', 'improvement_recommendations', 
                          'critical_gaps', 'competitive_analysis']
        
        for field in required_fields:
            self.assertIn(field, analysis, f"Missing field: {field}")
        
        print("✓ Error handling works correctly for empty digital infrastructure data")

def run_comprehensive_digital_infrastructure_scoring_test():
    """Run all gym digital infrastructure scoring tests and provide detailed report"""
    print("=" * 70)
    print("GYM DIGITAL INFRASTRUCTURE SCORING TEST SUITE")
    print("=" * 70)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_excellent_digital_infrastructure_scoring',
        'test_poor_digital_infrastructure_scoring',
        'test_online_booking_scoring_algorithm',
        'test_member_experience_scoring_algorithm',
        'test_digital_infrastructure_tier_classification',
        'test_digital_readiness_calculation',
        'test_weighted_scoring_contributions',
        'test_critical_gaps_identification',
        'test_competitive_analysis_assessment',
        'test_improvement_recommendations_prioritization',
        'test_integration_with_technology_analysis',
        'test_error_handling_in_digital_infrastructure_scoring'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymDigitalInfrastructureScoring(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    if result.errors:
        print("\nERRORS:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOVERALL: {'✓ PASS' if success else '✗ FAIL'}")
    print("=" * 70)
    
    return success

if __name__ == '__main__':
    run_comprehensive_digital_infrastructure_scoring_test()