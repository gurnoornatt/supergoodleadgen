#!/usr/bin/env python3
"""
Test suite for gym-specific lead data fields and extraction functionality
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor
from config import Config

class TestGymLeadFields(unittest.TestCase):
    """Test gym-specific lead data field extraction"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
        
        # Sample gym data for testing
        self.sample_gym_results = [
            {
                'title': 'CrossFit Central Valley',
                'website': 'https://crossfitcv.com',
                'phone': '(559) 123-4567',
                'address': '123 Fitness St, Fresno, CA 93720',
                'place_id': 'test123',
                'rating': 4.8,
                'reviews': 245,
                'gps_coordinates': {'latitude': 36.7378, 'longitude': -119.7871},
                'snippet': 'Premier CrossFit gym with personal training and group classes',
                'type': 'Gym, Fitness Center'
            },
            {
                'title': 'Serenity Yoga Studio',
                'website': 'https://serenityyoga.com',
                'phone': '(559) 987-6543',
                'address': '456 Zen Ave, Bakersfield, CA 93301',
                'place_id': 'test456',
                'rating': 4.5,
                'reviews': 89,
                'gps_coordinates': {'latitude': 35.3733, 'longitude': -119.0187},
                'snippet': 'Intimate yoga studio offering vinyasa, hatha, and meditation classes',
                'type': 'Yoga Studio'
            },
            {
                'title': 'Planet Fitness',
                'website': 'https://planetfitness.com',
                'phone': '(559) 555-0123',
                'address': '789 Mall Dr, Modesto, CA 95350',
                'place_id': 'test789',
                'rating': 4.2,
                'reviews': 1250,
                'gps_coordinates': {'latitude': 37.6391, 'longitude': -120.9969},
                'snippet': 'Chain fitness center with cardio equipment, free weights, and 24/7 access',
                'type': 'Gym, Health Club'
            }
        ]
    
    def test_gym_specific_fields_extraction(self):
        """Test that gym-specific fields are properly extracted"""
        # Test CrossFit gym
        crossfit_lead = self.lead_processor._process_maps_result(self.sample_gym_results[0])
        
        # Verify gym-specific fields exist
        gym_fields = [
            'gym_type', 'gym_size_estimate', 'gym_services', 'gym_location_type',
            'gym_membership_model', 'gym_equipment_types', 'gym_operating_hours',
            'gym_pricing_indicators', 'gym_target_demographic', 'gym_franchise_chain',
            'gym_years_in_business', 'gym_staff_size_estimate', 'gym_digital_presence_score',
            'gym_software_needs_score'
        ]
        
        for field in gym_fields:
            self.assertIn(field, crossfit_lead, f"Missing gym field: {field}")
        
        print("✓ All gym-specific fields are present in lead structure")
    
    def test_gym_type_detection(self):
        """Test gym type detection logic"""
        test_cases = [
            ('CrossFit Central Valley crossfit gym', 'crossfit'),
            ('Serenity Yoga Studio yoga classes', 'boutique_fitness'),
            ('Planet Fitness gym fitness center', 'traditional_gym'),
            ('Karate Dojo martial arts school', 'martial_arts'),
            ('Community Recreation Center ymca', 'recreation_center'),
            ('Dance Studio ballet salsa', 'dance_studio'),
            ('Personal Training Services 1-on-1', 'personal_training')
        ]
        
        for text, expected_type in test_cases:
            result = self.lead_processor._determine_gym_type(text.lower())
            self.assertEqual(result, expected_type, f"Failed to detect {expected_type} from '{text}'")
        
        print("✓ Gym type detection working correctly")
    
    def test_gym_size_estimation(self):
        """Test gym size estimation logic"""
        # Test review-based estimation (aligned with implementation thresholds)
        large_gym = {'reviews': 1200, 'rating': 4.0, 'title': 'Mega Fitness Center'}  # > 1000 reviews
        medium_gym = {'reviews': 350, 'rating': 4.2, 'title': 'Local Gym'}  # 200-500 range
        small_gym = {'reviews': 50, 'rating': 4.5, 'title': 'Small Studio'}  # < 200
        
        self.assertEqual(self.lead_processor._estimate_gym_size(large_gym, ''), 'large')
        self.assertEqual(self.lead_processor._estimate_gym_size(medium_gym, ''), 'medium')
        self.assertEqual(self.lead_processor._estimate_gym_size(small_gym, ''), 'small')
        
        # Test text-based overrides
        self.assertEqual(self.lead_processor._estimate_gym_size({'reviews': 50, 'title': 'Boutique Studio'}, 'boutique intimate studio'), 'small')
        self.assertEqual(self.lead_processor._estimate_gym_size({'reviews': 50, 'title': '24 Hour Fitness'}, 'large chain franchise 24/7'), 'large')
        
        print("✓ Gym size estimation working correctly")
    
    def test_gym_services_extraction(self):
        """Test gym services extraction"""
        test_text = "yoga pilates personal training group classes swimming pool childcare nutrition"
        services = self.lead_processor._extract_gym_services(test_text)
        
        expected_services = ['yoga', 'pilates', 'personal_training', 'group_classes', 'swimming', 'childcare', 'nutrition']
        for service in expected_services:
            self.assertIn(service, services, f"Missing service: {service}")
        
        print(f"✓ Extracted {len(services)} services correctly")
    
    def test_franchise_chain_identification(self):
        """Test franchise/chain identification"""
        test_cases = [
            ('Planet Fitness', 'Planet Fitness'),
            ('24 Hour Fitness', '24 Hour Fitness'),
            ('CrossFit Downtown', 'Crossfit'),
            ('LA Fitness Center', 'La Fitness'),
            ('Independent Gym', ''),
            ('YMCA Community Center', 'Ymca')
        ]
        
        for business_name, expected_chain in test_cases:
            result = self.lead_processor._identify_franchise_chain(business_name.lower())
            self.assertEqual(result, expected_chain, f"Failed chain detection for {business_name}")
        
        print("✓ Franchise chain identification working correctly")
    
    def test_digital_presence_scoring(self):
        """Test digital presence scoring"""
        full_presence = {
            'website': 'https://test.com',
            'place_id': 'test123',
            'reviews': 200,
            'rating': 4.5,
            'photos': ['photo1', 'photo2']
        }
        
        minimal_presence = {
            'place_id': 'test456'
        }
        
        full_score = self.lead_processor._calculate_digital_presence_score(full_presence)
        minimal_score = self.lead_processor._calculate_digital_presence_score(minimal_presence)
        
        self.assertGreater(full_score, minimal_score)
        self.assertGreaterEqual(full_score, 70)  # Should have high score
        self.assertLessEqual(minimal_score, 30)  # Should have low score
        
        print(f"✓ Digital presence scoring: Full={full_score}, Minimal={minimal_score}")
    
    def test_software_needs_scoring(self):
        """Test software needs scoring"""
        # Traditional gym with complex services should have high score
        high_need_score = self.lead_processor._calculate_software_needs_score(
            'traditional_gym', 'large', ['personal_training', 'group_classes', 'childcare', 'nutrition']
        )
        
        # Simple dance studio should have lower score
        low_need_score = self.lead_processor._calculate_software_needs_score(
            'dance_studio', 'small', ['group_classes']
        )
        
        self.assertGreater(high_need_score, low_need_score)
        self.assertGreaterEqual(high_need_score, 80)
        self.assertLessEqual(low_need_score, 70)
        
        print(f"✓ Software needs scoring: High need={high_need_score}, Low need={low_need_score}")
    
    def test_complete_gym_data_extraction(self):
        """Test complete gym data extraction pipeline"""
        for i, sample_result in enumerate(self.sample_gym_results):
            lead = self.lead_processor._process_maps_result(sample_result)
            
            # Verify basic fields
            self.assertEqual(lead['business_name'], sample_result['title'])
            self.assertEqual(lead['website'], sample_result['website'])
            
            # Verify gym-specific fields are populated
            self.assertIsNotNone(lead['gym_type'])
            self.assertIsNotNone(lead['gym_size_estimate'])
            self.assertIsInstance(lead['gym_services'], list)
            self.assertIsNotNone(lead['gym_location_type'])
            self.assertIsInstance(lead['gym_digital_presence_score'], int)
            self.assertIsInstance(lead['gym_software_needs_score'], int)
            
            print(f"✓ Complete data extraction for {sample_result['title']}")
            print(f"   Type: {lead['gym_type']}, Size: {lead['gym_size_estimate']}")
            print(f"   Services: {len(lead['gym_services'])}, Software Need: {lead['gym_software_needs_score']}")
    
    def test_gym_fields_in_csv_output(self):
        """Test that gym fields are included in CSV output structure"""
        # Create sample leads with gym data
        sample_leads = [self.lead_processor._process_maps_result(result) for result in self.sample_gym_results]
        
        # Test CSV column order includes gym fields
        import pandas as pd
        df = pd.DataFrame(sample_leads)
        
        gym_columns = [
            'gym_type', 'gym_size_estimate', 'gym_services', 'gym_location_type',
            'gym_membership_model', 'gym_equipment_types', 'gym_operating_hours',
            'gym_pricing_indicators', 'gym_target_demographic', 'gym_franchise_chain',
            'gym_years_in_business', 'gym_staff_size_estimate', 'gym_digital_presence_score',
            'gym_software_needs_score'
        ]
        
        for column in gym_columns:
            self.assertIn(column, df.columns, f"Missing gym column in CSV: {column}")
        
        print("✓ All gym columns present in CSV output structure")
    
    def test_edge_cases_and_error_handling(self):
        """Test edge cases and error handling in gym data extraction"""
        # Test with minimal data
        minimal_result = {
            'title': 'Test Gym',
            'website': '',
            'phone': '',
            'address': '',
            'place_id': '',
            'rating': 0,
            'reviews': 0,
            'gps_coordinates': {}
        }
        
        lead = self.lead_processor._process_maps_result(minimal_result)
        
        # Should not crash and should have default values
        self.assertIsNotNone(lead)
        self.assertEqual(lead['business_name'], 'Test Gym')
        self.assertIsInstance(lead['gym_services'], list)
        self.assertIsInstance(lead['gym_equipment_types'], list)
        self.assertIsInstance(lead['gym_pricing_indicators'], list)
        
        print("✓ Edge case handling working correctly")

def run_comprehensive_gym_fields_test():
    """Run all gym field tests and provide detailed report"""
    print("=" * 60)
    print("GYM LEAD FIELDS TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_gym_specific_fields_extraction',
        'test_gym_type_detection', 
        'test_gym_size_estimation',
        'test_gym_services_extraction',
        'test_franchise_chain_identification',
        'test_digital_presence_scoring',
        'test_software_needs_scoring',
        'test_complete_gym_data_extraction',
        'test_gym_fields_in_csv_output',
        'test_edge_cases_and_error_handling'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymLeadFields(method))
    
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
    run_comprehensive_gym_fields_test()