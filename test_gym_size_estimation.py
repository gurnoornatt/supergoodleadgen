#!/usr/bin/env python3
"""
Test suite for enhanced gym size estimation logic
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

class TestGymSizeEstimation(unittest.TestCase):
    """Test enhanced gym size estimation algorithms"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
        
        # Test data for different gym sizes
        self.large_gym_data = [
            {
                'title': 'Planet Fitness',
                'reviews': 1250,
                'rating': 4.2,
                'snippet': 'Large chain fitness center with 24/7 access and multiple locations',
                'type': 'Gym, Health Club'
            },
            {
                'title': 'LA Fitness Center',
                'reviews': 800,
                'rating': 4.0,
                'snippet': 'Full service gym with huge facility and complete equipment',
                'type': 'Fitness Center'
            }
        ]
        
        self.medium_gym_data = [
            {
                'title': 'Central Valley Fitness',
                'reviews': 150,
                'rating': 4.3,
                'snippet': 'Established local gym with complete fitness facilities',
                'type': 'Gym'
            },
            {
                'title': 'CrossFit Downtown',
                'reviews': 220,
                'rating': 4.6,
                'snippet': 'Complete CrossFit facility with multiple rooms and various equipment',
                'type': 'CrossFit Gym'
            }
        ]
        
        self.small_gym_data = [
            {
                'title': 'Serenity Yoga Studio',
                'reviews': 45,
                'rating': 4.8,
                'snippet': 'Intimate boutique yoga studio with personal attention',
                'type': 'Yoga Studio'
            },
            {
                'title': 'Elite Personal Training',
                'reviews': 25,
                'rating': 4.9,
                'snippet': 'Private personal training studio with exclusive 1-on-1 sessions',
                'type': 'Personal Trainer'
            }
        ]
    
    def test_large_gym_estimation(self):
        """Test estimation for large gyms"""
        for gym_data in self.large_gym_data:
            size, details = self.lead_processor._estimate_gym_size_with_details(
                gym_data, 
                f"{gym_data['title'].lower()} {gym_data['snippet'].lower()}"
            )
            
            self.assertEqual(size, 'large', f"Failed to identify {gym_data['title']} as large")
            self.assertGreater(details['size_score'], 80, f"Score too low for {gym_data['title']}")
            self.assertGreater(details['confidence_level'], 60, f"Confidence too low for {gym_data['title']}")
            
            print(f"✓ {gym_data['title']}: {size} (score: {details['size_score']}, confidence: {details['confidence_level']}%)")
    
    def test_medium_gym_estimation(self):
        """Test estimation for medium gyms"""
        for gym_data in self.medium_gym_data:
            size, details = self.lead_processor._estimate_gym_size_with_details(
                gym_data, 
                f"{gym_data['title'].lower()} {gym_data['snippet'].lower()}"
            )
            
            self.assertEqual(size, 'medium', f"Failed to identify {gym_data['title']} as medium")
            self.assertGreaterEqual(details['size_score'], 30, f"Score too low for {gym_data['title']}")
            self.assertLess(details['size_score'], 80, f"Score too high for {gym_data['title']}")
            
            print(f"✓ {gym_data['title']}: {size} (score: {details['size_score']}, confidence: {details['confidence_level']}%)")
    
    def test_small_gym_estimation(self):
        """Test estimation for small gyms"""
        for gym_data in self.small_gym_data:
            size, details = self.lead_processor._estimate_gym_size_with_details(
                gym_data, 
                f"{gym_data['title'].lower()} {gym_data['snippet'].lower()}"
            )
            
            self.assertEqual(size, 'small', f"Failed to identify {gym_data['title']} as small")
            self.assertLess(details['size_score'], 30, f"Score too high for {gym_data['title']}")
            
            print(f"✓ {gym_data['title']}: {size} (score: {details['size_score']}, confidence: {details['confidence_level']}%)")
    
    def test_franchise_chain_detection_in_sizing(self):
        """Test that franchise chains are properly weighted in size estimation"""
        test_cases = [
            ('Planet Fitness Downtown', 800, 'large'),
            ('Anytime Fitness', 150, 'medium'),  # Mid-size chain
            ('Independent Gym', 150, 'medium'),  # No chain bonus
        ]
        
        for name, reviews, expected_size in test_cases:
            gym_data = {
                'title': name,
                'reviews': reviews,
                'rating': 4.0,
                'snippet': 'Fitness center'
            }
            
            size, details = self.lead_processor._estimate_gym_size_with_details(
                gym_data, 
                name.lower()
            )
            
            self.assertEqual(size, expected_size, f"Chain sizing failed for {name}")
            
            # Check if franchise was detected in factors
            if 'planet fitness' in name.lower() or 'anytime fitness' in name.lower():
                chain_mentioned = any('chain' in factor.lower() for factor in details['confidence_factors'])
                self.assertTrue(chain_mentioned, f"Chain not detected in factors for {name}")
            
            print(f"✓ Chain detection for {name}: {size}")
    
    def test_text_indicators_influence(self):
        """Test that text indicators properly influence size estimation"""
        base_gym = {
            'title': 'Test Gym',
            'reviews': 300,  # Higher base to allow upgrade to large
            'rating': 4.0,
            'snippet': ''
        }
        
        # Test large indicators
        large_text = 'huge facility with multiple locations and 24/7 access'
        size_large, details_large = self.lead_processor._estimate_gym_size_with_details(
            base_gym, large_text
        )
        
        # Test small indicators
        small_text = 'boutique intimate studio with personal private training'
        size_small, details_small = self.lead_processor._estimate_gym_size_with_details(
            base_gym, small_text
        )
        
        self.assertEqual(size_large, 'large', "Large text indicators didn't upgrade size")
        self.assertEqual(size_small, 'small', "Small text indicators didn't downgrade size")
        
        print(f"✓ Text indicators: Large upgrade working, Small downgrade working")
    
    def test_business_type_influence(self):
        """Test that business type influences size estimation"""
        base_data = {
            'title': 'Test Facility',
            'reviews': 100,  # Base medium score
            'rating': 4.0,
            'snippet': ''
        }
        
        # Recreation center should tend larger
        rec_size, rec_details = self.lead_processor._estimate_gym_size_with_details(
            base_data, 'community recreation center ymca'
        )
        
        # Personal training should tend smaller
        pt_size, pt_details = self.lead_processor._estimate_gym_size_with_details(
            base_data, 'personal training 1-on-1 sessions'
        )
        
        # Recreation center should have higher score than personal training
        self.assertGreater(rec_details['size_score'], pt_details['size_score'],
                          "Recreation center should score higher than personal training")
        
        print(f"✓ Business type influence: Recreation={rec_size} (score: {rec_details['size_score']}), "
              f"Personal Training={pt_size} (score: {pt_details['size_score']})")
    
    def test_confidence_level_calculation(self):
        """Test confidence level calculation"""
        # High-data gym should have high confidence
        high_data_gym = {
            'title': 'Planet Fitness',
            'reviews': 1000,
            'rating': 4.5,
            'snippet': 'Large chain fitness center with 24/7 access in shopping center'
        }
        
        size, details = self.lead_processor._estimate_gym_size_with_details(
            high_data_gym, 
            f"{high_data_gym['title'].lower()} {high_data_gym['snippet'].lower()}"
        )
        
        self.assertGreater(details['confidence_level'], 80, "High-data gym should have high confidence")
        self.assertGreater(len(details['confidence_factors']), 3, "Should have multiple confidence factors")
        
        print(f"✓ Confidence calculation: {details['confidence_level']}% with {len(details['confidence_factors'])} factors")
    
    def test_edge_cases(self):
        """Test edge cases in size estimation"""
        # Minimal data
        minimal_gym = {
            'title': 'Gym',
            'reviews': 0,
            'rating': 0,
            'snippet': ''
        }
        
        size, details = self.lead_processor._estimate_gym_size_with_details(minimal_gym, 'gym')
        
        self.assertIsInstance(size, str)
        self.assertIn(size, ['small', 'medium', 'large'])
        self.assertIsInstance(details['confidence_factors'], list)
        self.assertGreaterEqual(details['confidence_level'], 0)
        
        print(f"✓ Edge case handling: Minimal data -> {size} (confidence: {details['confidence_level']}%)")
    
    def test_size_estimation_integration(self):
        """Test integration with lead processing"""
        test_gym = {
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
        }
        
        lead = self.lead_processor._process_maps_result(test_gym)
        
        # Verify size estimation fields are populated
        self.assertIn('gym_size_estimate', lead)
        self.assertIn('gym_size_confidence', lead)
        self.assertIn('gym_size_factors', lead)
        
        self.assertIsInstance(lead['gym_size_estimate'], str)
        self.assertIsInstance(lead['gym_size_confidence'], (int, float))
        self.assertIsInstance(lead['gym_size_factors'], list)
        
        print(f"✓ Integration test: {lead['business_name']}")
        print(f"   Size: {lead['gym_size_estimate']}, Confidence: {lead['gym_size_confidence']}%")
        print(f"   Factors: {len(lead['gym_size_factors'])} factors identified")
    
    def test_backward_compatibility(self):
        """Test that the original _estimate_gym_size method still works"""
        test_data = {
            'title': 'Test Gym',
            'reviews': 300,
            'rating': 4.0
        }
        
        # Original method should still work
        size = self.lead_processor._estimate_gym_size(test_data, 'test gym')
        self.assertIn(size, ['small', 'medium', 'large'])
        
        print(f"✓ Backward compatibility: Original method returns {size}")

def run_comprehensive_gym_size_test():
    """Run all gym size estimation tests and provide detailed report"""
    print("=" * 60)
    print("GYM SIZE ESTIMATION TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_large_gym_estimation',
        'test_medium_gym_estimation', 
        'test_small_gym_estimation',
        'test_franchise_chain_detection_in_sizing',
        'test_text_indicators_influence',
        'test_business_type_influence',
        'test_confidence_level_calculation',
        'test_edge_cases',
        'test_size_estimation_integration',
        'test_backward_compatibility'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymSizeEstimation(method))
    
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
    run_comprehensive_gym_size_test()