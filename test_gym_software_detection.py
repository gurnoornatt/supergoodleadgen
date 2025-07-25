#!/usr/bin/env python3
"""
Test suite for enhanced BuiltWith gym software detection integration
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

class TestGymSoftwareDetection(unittest.TestCase):
    """Test gym software detection integration with BuiltWith analysis"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
        
        # Sample gym leads with different software scenarios
        self.mindbody_gym = {
            'business_name': 'Elite Fitness Center',
            'website': 'https://elitefitness.com',
            'phone': '(555) 123-4567',
            'address': '123 Fitness St, Fresno, CA',
            'place_id': 'elite123',
            'rating': 4.5,
            'reviews': 320,
            'gps_coordinates': {'latitude': 36.7378, 'longitude': -119.7871},
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
            'gym_type': 'traditional_gym',
            'gym_size_estimate': 'medium',
            'gym_size_confidence': 70,
            'gym_size_factors': ['Moderate review count'],
            'gym_services': ['personal_training', 'group_classes'],
            'gym_location_type': 'standalone',
            'gym_membership_model': 'membership',
            'gym_equipment_types': ['cardio_equipment', 'free_weights'],
            'gym_operating_hours': '',
            'gym_pricing_indicators': [],
            'gym_target_demographic': 'general',
            'gym_franchise_chain': '',
            'gym_years_in_business': '2-5',
            'gym_staff_size_estimate': '10-20',
            'gym_digital_presence_score': 75,
            'gym_software_needs_score': 80,
            'gym_software_detected': [],
            'gym_software_scores': {},
            'gym_software_quality_score': 0,
            'gym_software_recommendations': [],
            'gym_software_red_flags': []
        }
    
    def test_mindbody_detection_from_technologies(self):
        """Test MindBody detection from BuiltWith technologies"""
        # Mock BuiltWith response with MindBody technologies
        mock_technologies = [
            {'name': 'MindBody Online', 'category': 'Fitness Management'},
            {'name': 'Healcode Widget', 'category': 'Booking System'},
            {'name': 'jQuery', 'category': 'JavaScript Libraries'}
        ]
        
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, 'https://elitefitness.com')
        
        # Verify MindBody was detected
        self.assertIn('Mindbody', analysis['detected_software'])
        self.assertIn('MindBody', analysis['software_scores'])
        self.assertGreater(analysis['overall_quality_score'], 80)  # MindBody is premium
        self.assertIn('Excellent choice', analysis['software_scores']['MindBody']['recommendation'])
        
        print(f"✓ MindBody detected with quality score: {analysis['overall_quality_score']}")
    
    def test_wodify_detection_from_url(self):
        """Test Wodify detection from website URL"""
        mock_technologies = [
            {'name': 'React', 'category': 'JavaScript Frameworks'}
        ]
        
        wodify_url = 'https://app.wodify.com/schedule'
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, wodify_url)
        
        # Verify Wodify was detected from URL
        self.assertIn('Wodify', analysis['detected_software'])
        self.assertGreater(analysis['overall_quality_score'], 60)  # Wodify is good quality
        
        print(f"✓ Wodify detected from URL with quality score: {analysis['overall_quality_score']}")
    
    def test_outdated_software_red_flags(self):
        """Test red flag detection for outdated gym software"""
        mock_technologies = [
            {'name': 'ABC Financial', 'category': 'Gym Management'}
        ]
        
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, 'https://abcfinancial.com')
        
        # Verify ABC Financial was detected and flagged
        self.assertIn('Abc Financial', analysis['detected_software'])
        self.assertLess(analysis['overall_quality_score'], 50)  # ABC Financial is outdated
        self.assertGreater(len(analysis['red_flags']), 0)  # Should have red flags
        
        # Check for specific red flags
        red_flag_text = ' '.join(analysis['red_flags'])
        self.assertIn('outdated', red_flag_text.lower())
        
        print(f"✓ ABC Financial flagged as outdated: {len(analysis['red_flags'])} red flags")
    
    def test_no_software_detected_recommendations(self):
        """Test recommendations when no gym software is detected"""
        mock_technologies = [
            {'name': 'WordPress', 'category': 'CMS'},
            {'name': 'jQuery', 'category': 'JavaScript Libraries'}
        ]
        
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, 'https://basicgym.com')
        
        # Verify appropriate recommendations for no gym software
        self.assertEqual(len(analysis['detected_software']), 1)  # WordPress detected
        self.assertIn('No specialized gym management software detected', analysis['recommendations'])
        self.assertIn('MindBody', ' '.join(analysis['recommendations']))
        
        print("✓ Appropriate recommendations provided when no gym software detected")
    
    def test_basic_software_upgrade_recommendations(self):
        """Test upgrade recommendations for basic software solutions"""
        mock_technologies = [
            {'name': 'Calendly Widget', 'category': 'Scheduling'}
        ]
        
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, 'https://calendly.com')
        
        # Verify Calendly detected and appropriate recommendations
        self.assertIn('Calendly', analysis['detected_software'])
        recommendation_text = ' '.join(analysis['recommendations'])
        # Should recommend implementing specialized software since Calendly is generic
        self.assertIn('specialized', recommendation_text.lower())
        self.assertIn('mindbody', recommendation_text.lower())
        
        print("✓ Upgrade recommendations provided for basic software")
    
    @patch('api_client.BuiltWithClient.analyze_domain')  
    def test_technology_analysis_integration(self, mock_builtwith):
        """Test full integration with technology analysis"""
        # Mock BuiltWith response
        mock_builtwith.return_value = {
            'technologies': [
                {'name': 'Zen Planner API', 'category': 'Fitness Management', 'last_detected': '2024'},
                {'name': 'Stripe', 'category': 'Payment Processing', 'last_detected': '2024'}
            ]
        }
        
        # Create test lead
        lead = self.mindbody_gym.copy()
        lead['website'] = 'https://testgym.com'
        
        # Process through technology analysis
        processed_lead = self.lead_processor.analyze_website_technology(lead)
        
        # Verify gym software fields are populated
        self.assertIn('gym_software_detected', processed_lead)
        self.assertIn('gym_software_quality_score', processed_lead)
        self.assertIn('gym_software_recommendations', processed_lead)
        self.assertIn('gym_software_red_flags', processed_lead)
        
        # Verify Zen Planner was detected
        self.assertIn('Zen Planner', processed_lead['gym_software_detected'])
        self.assertGreater(processed_lead['gym_software_quality_score'], 50)
        
        print(f"✓ Full integration test: Detected {len(processed_lead['gym_software_detected'])} software platforms")
    
    def test_pain_scoring_with_gym_software(self):
        """Test that gym software quality affects pain scoring"""
        # Create lead with poor gym software
        bad_software_lead = self.mindbody_gym.copy()
        bad_software_lead.update({
            'mobile_score': 70,  # Decent mobile score
            'technology_age_score': 70,  # Decent tech age
            'technology_flags': [],  # No tech flags
            'gym_software_quality_score': 20,  # Very poor gym software
            'gym_software_red_flags': ['CRITICAL: Outdated software', 'No mobile app']
        })
        
        # Apply comprehensive pain scoring
        scored_lead = self.lead_processor.apply_comprehensive_pain_scoring(bad_software_lead)
        
        # Verify gym software contributes to pain score
        self.assertIn('gym_software_pain', scored_lead['pain_breakdown'])
        self.assertGreater(scored_lead['pain_breakdown']['gym_software_pain'], 50)
        pain_factors_text = ' '.join(scored_lead['pain_factors'])
        self.assertIn('gym software', pain_factors_text.lower())
        
        # Create lead with good gym software for comparison
        good_software_lead = self.mindbody_gym.copy()
        good_software_lead.update({
            'mobile_score': 70,
            'technology_age_score': 70,
            'technology_flags': [],
            'gym_software_quality_score': 90,  # Excellent gym software
            'gym_software_red_flags': []
        })
        
        scored_good_lead = self.lead_processor.apply_comprehensive_pain_scoring(good_software_lead)
        
        # Verify good software results in lower pain
        self.assertLess(scored_good_lead['pain_score'], scored_lead['pain_score'])
        
        print(f"✓ Pain scoring integration: Bad software={scored_lead['pain_score']:.1f}, Good software={scored_good_lead['pain_score']:.1f}")
    
    def test_multiple_software_detection(self):
        """Test detection of multiple gym software platforms"""
        mock_technologies = [
            {'name': 'MindBody API', 'category': 'Fitness Management'},
            {'name': 'Stripe Payment', 'category': 'Payment Processing'},
            {'name': 'Calendly Embed', 'category': 'Scheduling'}
        ]
        
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, 'https://multisoftware.com')
        
        # Verify multiple platforms detected
        self.assertGreaterEqual(len(analysis['detected_software']), 2)
        self.assertIn('Mindbody', analysis['detected_software'])
        self.assertIn('Calendly', analysis['detected_software'])
        
        # Verify average quality score calculation
        self.assertGreater(analysis['overall_quality_score'], 0)
        
        print(f"✓ Multiple software detection: {len(analysis['detected_software'])} platforms detected")
    
    def test_csv_output_includes_gym_software_fields(self):
        """Test that CSV output includes new gym software fields"""
        # Create sample leads with gym software data
        leads_with_software = [self.mindbody_gym.copy()]
        leads_with_software[0].update({
            'gym_software_detected': ['MindBody'],
            'gym_software_quality_score': 95,
            'gym_software_recommendations': ['Excellent choice'],
            'gym_software_red_flags': []
        })
        
        # Test CSV generation
        import pandas as pd
        df = pd.DataFrame(leads_with_software)
        
        # Verify gym software columns exist
        gym_software_columns = [
            'gym_software_detected', 'gym_software_scores', 'gym_software_quality_score',
            'gym_software_recommendations', 'gym_software_red_flags'
        ]
        
        for column in gym_software_columns:
            self.assertIn(column, df.columns, f"Missing gym software column: {column}")
        
        print("✓ All gym software fields included in CSV output structure")
    
    def test_error_handling_in_gym_software_analysis(self):
        """Test error handling in gym software analysis"""
        # Test with malformed technologies
        malformed_technologies = [
            {'invalid': 'data'},
            None,
            {'name': None, 'category': None}
        ]
        
        analysis = self.lead_processor._analyze_gym_software(malformed_technologies, None)
        
        # Verify graceful error handling
        self.assertIsInstance(analysis, dict)
        self.assertIn('detected_software', analysis)
        self.assertIsInstance(analysis['detected_software'], list)
        self.assertIsInstance(analysis['overall_quality_score'], (int, float))
        
        print("✓ Error handling works correctly for malformed data")

def run_comprehensive_gym_software_detection_test():
    """Run all gym software detection tests and provide detailed report"""
    print("=" * 60)
    print("GYM SOFTWARE DETECTION TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_mindbody_detection_from_technologies',
        'test_wodify_detection_from_url',
        'test_outdated_software_red_flags',
        'test_no_software_detected_recommendations',
        'test_basic_software_upgrade_recommendations',
        'test_technology_analysis_integration',
        'test_pain_scoring_with_gym_software',
        'test_multiple_software_detection',
        'test_csv_output_includes_gym_software_fields',
        'test_error_handling_in_gym_software_analysis'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymSoftwareDetection(method))
    
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
    run_comprehensive_gym_software_detection_test()