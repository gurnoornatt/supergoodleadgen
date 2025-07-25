#!/usr/bin/env python3
"""
Test suite for gym website feature analysis functionality
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

class TestGymWebsiteFeatures(unittest.TestCase):
    """Test gym website feature analysis functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
    
    def test_comprehensive_gym_website_feature_detection(self):
        """Test detection of comprehensive gym website features"""
        # Mock technologies with comprehensive gym features
        comprehensive_technologies = [
            {'name': 'MindBody Online', 'category': 'Fitness Management'},
            {'name': 'Stripe Payment Processing', 'category': 'Payment'},
            {'name': 'Bootstrap', 'category': 'CSS Framework'},
            {'name': 'Zoom Integration', 'category': 'Video Conferencing'},
            {'name': 'Facebook Pixel', 'category': 'Social Media'},
            {'name': 'Intercom Chat', 'category': 'Customer Support'},
            {'name': 'WooCommerce', 'category': 'E-commerce'}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://premiumgym.com', 
            comprehensive_technologies
        )
        
        # Verify high feature score
        self.assertGreater(analysis['feature_score'], 70)
        self.assertGreater(analysis['implemented_count'], 7)
        
        # Verify specific features detected
        features = analysis['detected_features']
        self.assertTrue(features['online_booking'])  # MindBody
        self.assertTrue(features['payment_processing'])  # Stripe
        self.assertTrue(features['mobile_responsive'])  # Bootstrap
        self.assertTrue(features['virtual_classes'])  # Zoom
        self.assertTrue(features['social_integration'])  # Facebook
        self.assertTrue(features['live_chat'])  # Intercom
        self.assertTrue(features['ecommerce'])  # WooCommerce
        
        print(f"✓ Comprehensive gym features: {analysis['implemented_count']}/{analysis['total_features']} detected")
        print(f"   Feature score: {analysis['feature_score']}")
    
    def test_basic_gym_website_feature_detection(self):
        """Test detection of basic gym website features"""
        # Mock technologies with basic features
        basic_technologies = [
            {'name': 'WordPress', 'category': 'CMS'},
            {'name': 'jQuery', 'category': 'JavaScript Library'},
            {'name': 'Calendly', 'category': 'Scheduling'}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://basicgym.com', 
            basic_technologies
        )
        
        # Verify lower feature score
        self.assertLess(analysis['feature_score'], 50)
        self.assertLess(analysis['implemented_count'], 5)
        
        # Verify specific features detected/missing
        features = analysis['detected_features']
        self.assertTrue(features['online_booking'])  # Calendly detected
        self.assertFalse(features['payment_processing'])  # Not detected
        self.assertFalse(features['mobile_responsive'])  # Not detected
        self.assertFalse(features['virtual_classes'])  # Not detected
        
        # Verify recommendations for missing features
        recommendations = analysis['recommendations']
        self.assertGreater(len(recommendations), 3)
        self.assertTrue(any('payment' in rec.lower() for rec in recommendations))
        self.assertTrue(any('mobile' in rec.lower() for rec in recommendations))
        
        print(f"✓ Basic gym features: {analysis['implemented_count']}/{analysis['total_features']} detected")
        print(f"   Recommendations: {len(recommendations)}")
    
    def test_outdated_gym_website_feature_detection(self):
        """Test detection of outdated/minimal gym website features"""
        # Mock technologies with very basic/outdated features
        outdated_technologies = [
            {'name': 'jQuery 1.x', 'category': 'JavaScript Library'},
            {'name': 'PHP', 'category': 'Server Language'}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://outdatedgym.com', 
            outdated_technologies
        )
        
        # Verify very low feature score
        self.assertLess(analysis['feature_score'], 30)
        self.assertLess(analysis['implemented_count'], 3)
        
        # Verify urgent recommendations
        recommendations = analysis['recommendations']
        urgent_recommendation = any('URGENT' in rec for rec in recommendations)
        self.assertTrue(urgent_recommendation, "Should have urgent recommendation for low-scoring website")
        
        print(f"✓ Outdated gym features: {analysis['implemented_count']}/{analysis['total_features']} detected")
        print(f"   Urgent recommendation present: {urgent_recommendation}")
    
    def test_no_website_data_handling(self):
        """Test handling of missing website or technology data"""
        # Test with no website URL
        analysis_no_website = self.lead_processor._analyze_gym_website_features(
            '', 
            [{'name': 'Test', 'category': 'Test'}]
        )
        
        self.assertEqual(analysis_no_website['feature_score'], 0)
        self.assertEqual(analysis_no_website['implemented_count'], 0)
        self.assertIn('No website', analysis_no_website['feature_indicators'][0])
        
        # Test with no technologies
        analysis_no_tech = self.lead_processor._analyze_gym_website_features(
            'https://testgym.com', 
            []
        )
        
        self.assertEqual(analysis_no_tech['feature_score'], 0)
        self.assertEqual(analysis_no_tech['implemented_count'], 0)
        
        print("✓ No website/technology data handled correctly")
    
    def test_crossfit_specific_features(self):
        """Test detection of CrossFit-specific features"""
        crossfit_technologies = [
            {'name': 'Wodify Core', 'category': 'Fitness Management'},
            {'name': 'Stripe', 'category': 'Payment Processing'},
            {'name': 'Responsive Design', 'category': 'CSS'}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://crossfitbox.com', 
            crossfit_technologies
        )
        
        # Verify CrossFit-specific software detection
        features = analysis['detected_features']
        self.assertTrue(features['online_booking'])  # Wodify
        self.assertTrue(features['class_scheduling'])  # Wodify
        self.assertTrue(features['membership_management'])  # Wodify
        self.assertTrue(features['payment_processing'])  # Stripe
        self.assertTrue(features['mobile_responsive'])  # Responsive
        
        print(f"✓ CrossFit features: {analysis['implemented_count']}/{analysis['total_features']} detected")
    
    def test_boutique_studio_features(self):
        """Test detection of boutique studio features"""
        boutique_technologies = [
            {'name': 'Glofox API', 'category': 'Fitness Management'},
            {'name': 'Zoom Webinar', 'category': 'Video Conferencing'},
            {'name': 'Instagram Widget', 'category': 'Social Media'},
            {'name': 'Mailchimp', 'category': 'Email Marketing'}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://boutiquestudio.com', 
            boutique_technologies
        )
        
        # Verify boutique-specific features
        features = analysis['detected_features']
        self.assertTrue(features['online_booking'])  # Glofox
        self.assertTrue(features['virtual_classes'])  # Zoom
        self.assertTrue(features['social_integration'])  # Instagram
        
        print(f"✓ Boutique studio features: {analysis['implemented_count']}/{analysis['total_features']} detected")
    
    def test_feature_scoring_algorithm(self):
        """Test the feature scoring algorithm accuracy"""
        # Test scenarios with known feature counts
        test_scenarios = [
            ([], 0),  # No technologies = 0% score
            ([{'name': 'MindBody', 'category': 'Fitness'}, 
              {'name': 'Stripe', 'category': 'Payment'}], 20),  # 2/10 features = 20%
            ([{'name': 'MindBody', 'category': 'Fitness'}, 
              {'name': 'Stripe', 'category': 'Payment'},
              {'name': 'Bootstrap', 'category': 'CSS'},
              {'name': 'Zoom', 'category': 'Video'},
              {'name': 'Facebook', 'category': 'Social'}], 50)  # 5/10 features = 50%
        ]
        
        for i, (technologies, expected_min_score) in enumerate(test_scenarios):
            analysis = self.lead_processor._analyze_gym_website_features(
                f'https://testgym{i}.com', 
                technologies
            )
            
            actual_score = analysis['feature_score']
            self.assertGreaterEqual(actual_score, expected_min_score)
            
            print(f"✓ Scoring test {i+1}: {actual_score}% (expected >= {expected_min_score}%)")
    
    def test_feature_recommendation_logic(self):
        """Test feature recommendation logic"""
        # Test with missing critical features
        minimal_technologies = [
            {'name': 'WordPress', 'category': 'CMS'}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://minimalgym.com', 
            minimal_technologies
        )
        
        recommendations = analysis['recommendations']
        
        # Verify critical recommendations are present
        booking_rec = any('booking' in rec.lower() for rec in recommendations)
        payment_rec = any('payment' in rec.lower() for rec in recommendations)
        mobile_rec = any('mobile' in rec.lower() for rec in recommendations)
        
        self.assertTrue(booking_rec, "Should recommend booking system")
        self.assertTrue(payment_rec, "Should recommend payment processing")
        self.assertTrue(mobile_rec, "Should recommend mobile responsiveness")
        
        print(f"✓ Recommendation logic: {len(recommendations)} recommendations generated")
        print(f"   Critical features recommended: booking={booking_rec}, payment={payment_rec}, mobile={mobile_rec}")
    
    def test_integration_with_technology_analysis(self):
        """Test integration with existing technology analysis pipeline"""
        # Create a test lead
        test_lead = {
            'business_name': 'Test Fitness Center',
            'website': 'https://testfitness.com',
            'status': 'pending',
            'technologies': [
                {'name': 'MindBody Online', 'category': 'Fitness Management'},
                {'name': 'Stripe', 'category': 'Payment Processing'},
                {'name': 'Bootstrap', 'category': 'CSS Framework'}
            ],
            'outdated_technologies': [],
            'technology_age_score': 85,
            'technology_flags': []
        }
        
        # Mock the BuiltWith client to avoid actual API calls
        with patch.object(self.lead_processor, 'builtwith_client') as mock_client:
            mock_client.analyze_domain.return_value = {
                'technologies': test_lead['technologies']
            }
            
            # Process through technology analysis
            processed_lead = self.lead_processor.analyze_website_technology(test_lead)
            
            # Verify website feature fields are populated
            self.assertIn('gym_website_features', processed_lead)
            self.assertIn('gym_website_feature_score', processed_lead)
            self.assertIn('gym_website_feature_indicators', processed_lead)
            self.assertIn('gym_website_missing_features', processed_lead)
            self.assertIn('gym_website_feature_recommendations', processed_lead)
            self.assertIn('gym_website_implemented_features', processed_lead)
            
            # Verify reasonable values
            self.assertGreater(processed_lead['gym_website_feature_score'], 0)
            self.assertGreater(processed_lead['gym_website_implemented_features'], 0)
            self.assertIsInstance(processed_lead['gym_website_features'], dict)
            
            print(f"✓ Integration test: Website feature score = {processed_lead['gym_website_feature_score']}")
            print(f"   Features implemented: {processed_lead['gym_website_implemented_features']}/10")
    
    def test_error_handling_in_feature_analysis(self):
        """Test error handling in website feature analysis"""
        # Test with malformed technology data
        malformed_technologies = [
            {'invalid': 'data'},
            None,
            {'name': None, 'category': None}
        ]
        
        analysis = self.lead_processor._analyze_gym_website_features(
            'https://testgym.com', 
            malformed_technologies
        )
        
        # Verify graceful error handling
        self.assertIsInstance(analysis, dict)
        self.assertIn('detected_features', analysis)
        self.assertIn('feature_score', analysis)
        self.assertIsInstance(analysis['feature_score'], (int, float))
        self.assertIsInstance(analysis['detected_features'], dict)
        
        print("✓ Error handling works correctly for malformed technology data")

def run_comprehensive_website_features_test():
    """Run all gym website feature tests and provide detailed report"""
    print("=" * 60)
    print("GYM WEBSITE FEATURES TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_comprehensive_gym_website_feature_detection',
        'test_basic_gym_website_feature_detection',
        'test_outdated_gym_website_feature_detection',
        'test_no_website_data_handling',
        'test_crossfit_specific_features',
        'test_boutique_studio_features',
        'test_feature_scoring_algorithm',
        'test_feature_recommendation_logic',
        'test_integration_with_technology_analysis',
        'test_error_handling_in_feature_analysis'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymWebsiteFeatures(method))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
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
    print("=" * 60)
    
    return success

if __name__ == '__main__':
    run_comprehensive_website_features_test()