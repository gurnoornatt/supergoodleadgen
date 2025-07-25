#!/usr/bin/env python3
"""
Test suite for gym mobile app detection functionality
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

class TestGymMobileAppDetection(unittest.TestCase):
    """Test gym mobile app detection functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
    
    def test_premium_software_mobile_app_detection(self):
        """Test detection of mobile apps for premium software platforms"""
        # Test MindBody (premium platform with excellent mobile app)
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'Premium Fitness Center',
            'https://premiumfitness.com',
            ['mindbody', 'stripe']
        )
        
        # Verify premium mobile app detection
        self.assertTrue(analysis['has_mobile_app'])
        self.assertIn('iOS', analysis['app_platforms'])
        self.assertIn('Android', analysis['app_platforms'])
        self.assertGreaterEqual(analysis['app_quality_score'], 80)
        self.assertIn('Excellent mobile app', analysis['app_recommendations'][0])
        
        print(f"✓ MindBody mobile app: Quality score {analysis['app_quality_score']}")
        print(f"   Platforms: {', '.join(analysis['app_platforms'])}")
    
    def test_multiple_software_mobile_app_quality(self):
        """Test mobile app quality calculation with multiple software platforms"""
        # Test gym using multiple software platforms
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'Multi-Platform Gym',
            'https://multiplatform.com',
            ['Zen Planner', 'Wodify', 'Stripe']
        )
        
        # Verify multiple platform mobile app analysis
        self.assertTrue(analysis['has_mobile_app'])
        self.assertGreater(analysis['app_quality_score'], 70)  # Average of Zen Planner (75) and Wodify (80)
        self.assertIn('iOS', analysis['app_platforms'])
        self.assertIn('Android', analysis['app_platforms'])
        
        print(f"✓ Multi-platform mobile app: Quality score {analysis['app_quality_score']}")
        print(f"   Recommendation: {analysis['app_recommendations'][0]}")
    
    def test_basic_software_mobile_app_issues(self):
        """Test mobile app issues for basic/generic software platforms"""
        # Test gym using only basic solutions
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'Basic Gym Setup',
            'https://basicgym.com',
            ['square', 'calendly', 'wordpress']
        )
        
        # Verify mobile app issues detected
        self.assertFalse(analysis['has_mobile_app'])
        self.assertEqual(analysis['app_quality_score'], 0)
        self.assertIn('No dedicated gym mobile app detected', analysis['app_quality_issues'])
        self.assertIn('CRITICAL: Implement dedicated gym mobile app', analysis['app_recommendations'])
        
        # Verify specific issues
        self.assertIn('Members likely cannot book classes via mobile app', analysis['app_quality_issues'])
        self.assertIn('Missing mobile-first member experience', analysis['app_quality_issues'])
        
        print(f"✓ Basic software mobile issues: {len(analysis['app_quality_issues'])} issues detected")
        print(f"   Critical recommendation: {analysis['app_recommendations'][0]}")
    
    def test_no_software_mobile_app_analysis(self):
        """Test mobile app analysis when no software is detected"""
        # Test gym with no detected software
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'No Software Gym',
            'https://nosoftware.com',
            []
        )
        
        # Verify critical mobile app issues
        self.assertFalse(analysis['has_mobile_app'])
        self.assertEqual(analysis['app_quality_score'], 0)
        self.assertGreater(len(analysis['app_quality_issues']), 0)
        self.assertIn('CRITICAL: Implement dedicated gym mobile app', analysis['app_recommendations'])
        
        print(f"✓ No software detected: {len(analysis['app_recommendations'])} recommendations")
    
    def test_outdated_software_mobile_app_issues(self):
        """Test mobile app issues for outdated software platforms"""
        # Test gym using outdated software
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'Outdated Gym Systems',
            'https://outdatedgym.com',
            ['abc_financial', 'perfect_gym']
        )
        
        # Verify outdated software mobile issues
        self.assertFalse(analysis['has_mobile_app'])
        self.assertIn('Outdated software platform with poor mobile support', analysis['app_quality_issues'])
        self.assertIn('Mobile app likely has limited functionality', analysis['app_quality_issues'])
        self.assertIn('Upgrade to modern platform for better mobile experience', analysis['app_recommendations'])
        
        print(f"✓ Outdated software issues: {len(analysis['app_quality_issues'])} issues identified")
    
    def test_mobile_responsive_fallback_detection(self):
        """Test mobile responsiveness fallback when no dedicated app"""
        # Test gym with mobile-responsive website but no app
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'Mobile Responsive Gym',
            'https://responsivegym.com',
            ['wordpress', 'bootstrap', 'stripe']
        )
        
        # Verify mobile responsive fallback
        self.assertFalse(analysis['has_mobile_app'])
        # Should detect mobile responsiveness and provide specific recommendation
        mobile_responsive_rec = any('Mobile-responsive website detected' in rec for rec in analysis['app_recommendations'])
        self.assertTrue(mobile_responsive_rec, "Should detect mobile-responsive website")
        
        print("✓ Mobile responsive fallback detected correctly")
    
    def test_no_mobile_solution_critical_issues(self):
        """Test critical issues when no mobile solution exists"""
        # Test gym with no mobile solution at all
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'No Mobile Gym',
            'https://nomobile.com',
            ['old_php', 'mysql']  # No mobile indicators
        )
        
        # Verify critical mobile issues
        self.assertFalse(analysis['has_mobile_app'])
        self.assertIn('Neither mobile app nor mobile-responsive website detected', analysis['app_quality_issues'])
        self.assertIn('URGENT: Implement mobile-responsive website as minimum requirement', analysis['app_recommendations'])
        
        print("✓ Critical mobile issues detected for gym with no mobile solution")
    
    def test_crossfit_specific_mobile_app_detection(self):
        """Test mobile app detection for CrossFit-specific software"""
        # Test CrossFit gym using Wodify
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'CrossFit Box',
            'https://crossfitbox.com',
            ['wodify', 'stripe']
        )
        
        # Verify CrossFit-specific mobile app detection
        self.assertTrue(analysis['has_mobile_app'])
        self.assertEqual(analysis['app_quality_score'], 80)  # Wodify quality score
        self.assertIn('iOS', analysis['app_platforms'])
        self.assertIn('Android', analysis['app_platforms'])
        
        print(f"✓ CrossFit mobile app: Wodify quality score {analysis['app_quality_score']}")
    
    def test_boutique_studio_mobile_app_detection(self):
        """Test mobile app detection for boutique fitness studio software"""
        # Test boutique studio using Glofox
        analysis = self.lead_processor._analyze_gym_mobile_app(
            'Boutique Fitness Studio',
            'https://boutiquestudio.com',
            ['glofox', 'zoom', 'stripe']
        )
        
        # Verify boutique-specific mobile app detection
        self.assertTrue(analysis['has_mobile_app'])
        self.assertEqual(analysis['app_quality_score'], 75)  # Glofox quality score
        self.assertIn('Good mobile app solution in use', analysis['app_recommendations'][0])
        
        print(f"✓ Boutique studio mobile app: Glofox quality score {analysis['app_quality_score']}")
    
    def test_mobile_app_quality_scoring_algorithm(self):
        """Test mobile app quality scoring algorithm accuracy"""
        # Test different software combinations and expected scores
        test_scenarios = [
            (['MindBody'], 85),  # Premium single platform
            (['Zen Planner', 'Wodify'], 77.5),  # Average of 75 and 80
            (['TeamUp', 'PushPress'], 67.5),  # Average of 70 and 65
            (['ClubReady'], 60),  # Lower quality single platform
            (['Square', 'Calendly'], 0)  # No gym-specific mobile apps
        ]
        
        for i, (software_list, expected_score) in enumerate(test_scenarios):
            analysis = self.lead_processor._analyze_gym_mobile_app(
                f'Test Gym {i+1}',
                f'https://testgym{i+1}.com',
                software_list
            )
            
            actual_score = analysis['app_quality_score']
            self.assertEqual(actual_score, expected_score, 
                           f"Score mismatch for {software_list}: expected {expected_score}, got {actual_score}")
            
            print(f"✓ Quality scoring test {i+1}: {actual_score} (expected {expected_score})")
    
    def test_integration_with_technology_analysis(self):
        """Test integration with existing technology analysis pipeline"""
        # Create a test lead with mobile app capable software
        test_lead = {
            'business_name': 'Test Mobile Gym',
            'website': 'https://testmobilegym.com',
            'status': 'pending',
            'technologies': [
                {'name': 'Glofox API', 'category': 'Fitness Management'},
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
            
            # Verify mobile app fields are populated
            self.assertIn('gym_mobile_app_available', processed_lead)
            self.assertIn('gym_mobile_app_platforms', processed_lead)
            self.assertIn('gym_mobile_app_quality_score', processed_lead)
            self.assertIn('gym_mobile_app_quality_issues', processed_lead)
            self.assertIn('gym_mobile_app_recommendations', processed_lead)
            self.assertIn('gym_mobile_app_detection_method', processed_lead)
            
            # Verify reasonable values for Glofox
            self.assertTrue(processed_lead['gym_mobile_app_available'])
            self.assertEqual(processed_lead['gym_mobile_app_quality_score'], 75)
            self.assertIn('iOS', processed_lead['gym_mobile_app_platforms'])
            self.assertIn('Android', processed_lead['gym_mobile_app_platforms'])
            
            print(f"✓ Integration test: Mobile app available = {processed_lead['gym_mobile_app_available']}")
            print(f"   Quality score: {processed_lead['gym_mobile_app_quality_score']}")
            print(f"   Platforms: {', '.join(processed_lead['gym_mobile_app_platforms'])}")
    
    def test_error_handling_in_mobile_app_analysis(self):
        """Test error handling in mobile app analysis"""
        # Test with malformed inputs
        analysis = self.lead_processor._analyze_gym_mobile_app(
            None,  # Invalid business name
            '',    # Empty website
            ['invalid_software']
        )
        
        # Verify graceful error handling
        self.assertIsInstance(analysis, dict)
        self.assertIn('has_mobile_app', analysis)
        self.assertIn('app_quality_score', analysis)
        self.assertIsInstance(analysis['app_quality_score'], (int, float))
        self.assertIsInstance(analysis['has_mobile_app'], bool)
        
        print("✓ Error handling works correctly for malformed mobile app analysis data")

def run_comprehensive_mobile_app_detection_test():
    """Run all gym mobile app detection tests and provide detailed report"""
    print("=" * 60)
    print("GYM MOBILE APP DETECTION TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_premium_software_mobile_app_detection',
        'test_multiple_software_mobile_app_quality',
        'test_basic_software_mobile_app_issues',
        'test_no_software_mobile_app_analysis',
        'test_outdated_software_mobile_app_issues',
        'test_mobile_responsive_fallback_detection',
        'test_no_mobile_solution_critical_issues',
        'test_crossfit_specific_mobile_app_detection',
        'test_boutique_studio_mobile_app_detection',
        'test_mobile_app_quality_scoring_algorithm',
        'test_integration_with_technology_analysis',
        'test_error_handling_in_mobile_app_analysis'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymMobileAppDetection(method))
    
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
    run_comprehensive_mobile_app_detection_test()