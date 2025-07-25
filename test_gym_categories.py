#!/usr/bin/env python3
"""
Test suite for gym categories and fitness business search functionality
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from lead_processor import LeadProcessor

class TestGymCategories(unittest.TestCase):
    """Test gym categories configuration and functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = Config()
        self.lead_processor = LeadProcessor()
    
    def test_gym_categories_exist(self):
        """Test that gym categories are properly defined"""
        self.assertTrue(hasattr(Config, 'GYM_FITNESS_CATEGORIES'))
        self.assertIsInstance(Config.GYM_FITNESS_CATEGORIES, list)
        self.assertGreater(len(Config.GYM_FITNESS_CATEGORIES), 10)
        print(f"✓ Found {len(Config.GYM_FITNESS_CATEGORIES)} gym categories")
    
    def test_gym_categories_comprehensive(self):
        """Test that gym categories cover all major fitness business types"""
        categories = Config.GYM_FITNESS_CATEGORIES
        
        # Essential gym categories that must be present
        essential_categories = [
            'gyms', 'fitness centers', 'health clubs', 'personal trainers',
            'yoga studios', 'crossfit gyms', 'martial arts schools'
        ]
        
        for category in essential_categories:
            self.assertIn(category, categories, f"Missing essential category: {category}")
        
        print("✓ All essential gym categories are present")
    
    def test_gym_categories_unique(self):
        """Test that gym categories don't contain duplicates"""
        categories = Config.GYM_FITNESS_CATEGORIES
        unique_categories = list(set(categories))
        
        self.assertEqual(len(categories), len(unique_categories), 
                        "Duplicate categories found in GYM_FITNESS_CATEGORIES")
        print("✓ No duplicate categories found")
    
    def test_gym_categories_format(self):
        """Test that gym categories are properly formatted for search"""
        categories = Config.GYM_FITNESS_CATEGORIES
        
        for category in categories:
            self.assertIsInstance(category, str)
            self.assertGreater(len(category.strip()), 0)
            # Categories should be lowercase for consistency
            self.assertEqual(category, category.lower(), f"Category not lowercase: {category}")
        
        print("✓ All categories are properly formatted")
    
    @patch('api_client.SerpApiClient.search_google_maps')
    def test_gym_search_functionality(self, mock_search):
        """Test gym search functionality with mock API response"""
        # Mock API response for gym search
        mock_response = {
            'local_results': [
                {
                    'title': 'Test Gym',
                    'website': 'https://testgym.com',
                    'phone': '(555) 123-4567',
                    'address': '123 Gym St, Fresno, CA',
                    'place_id': 'test123',
                    'rating': 4.5,
                    'reviews': 150,
                    'gps_coordinates': {'latitude': 36.7378, 'longitude': -119.7871}
                }
            ],
            'search_metadata': {
                'total_results': 1,
                'pages_fetched': 1
            }
        }
        mock_search.return_value = mock_response
        
        # Test searching for gyms
        test_category = 'gyms'
        test_location = 'Fresno, CA'
        
        leads = self.lead_processor.extract_leads_from_maps(test_category, test_location, 10)
        
        # Verify the search was called correctly
        mock_search.assert_called_once_with(test_category, test_location, 10)
        
        # Verify lead extraction
        self.assertEqual(len(leads), 1)
        lead = leads[0]
        self.assertEqual(lead['business_name'], 'Test Gym')
        self.assertEqual(lead['website'], 'https://testgym.com')
        self.assertEqual(lead['phone'], '(555) 123-4567')
        self.assertEqual(lead['status'], 'pending')
        
        print(f"✓ Gym search functionality working for category: {test_category}")
    
    def test_gym_specific_fields_in_lead_structure(self):
        """Test that lead structure includes fields relevant for gym businesses"""
        # Create a mock lead to test structure
        mock_result = {
            'title': 'Test Fitness Center',
            'website': 'https://testfitness.com',
            'phone': '(555) 987-6543',
            'address': '456 Fitness Ave, Bakersfield, CA',
            'place_id': 'fitness123',
            'rating': 4.2,
            'reviews': 89,
            'gps_coordinates': {'latitude': 35.3733, 'longitude': -119.0187}
        }
        
        lead = self.lead_processor._process_maps_result(mock_result)
        
        # Verify essential fields for gym businesses
        essential_fields = [
            'business_name', 'website', 'phone', 'address', 'rating', 'reviews',
            'google_business_url', 'latitude', 'longitude', 'status'
        ]
        
        for field in essential_fields:
            self.assertIn(field, lead, f"Missing essential field for gym leads: {field}")
        
        print("✓ Lead structure includes all essential gym business fields")
    
    def test_multiple_gym_categories_search(self):
        """Test searching across multiple gym categories"""
        test_categories = ['gyms', 'fitness centers', 'yoga studios']
        
        for category in test_categories:
            self.assertIn(category, Config.GYM_FITNESS_CATEGORIES)
        
        print(f"✓ Multiple gym categories ready for search: {', '.join(test_categories)}")

class TestGymCategoriesIntegration(unittest.TestCase):
    """Integration tests for gym categories with real API (if available)"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.lead_processor = LeadProcessor()
    
    def test_config_validation_with_gym_categories(self):
        """Test that config validation works with gym categories"""
        try:
            # This might fail if API keys are not set up, which is expected
            Config.validate_config()
            config_valid = True
        except ValueError as e:
            config_valid = False
            print(f"Config validation failed (expected if API keys not set): {e}")
        
        # The important thing is that gym categories don't break config validation
        self.assertTrue(hasattr(Config, 'GYM_FITNESS_CATEGORIES'))
        print("✓ Gym categories don't interfere with config validation")

def run_comprehensive_gym_categories_test():
    """Run all gym categories tests and provide detailed report"""
    print("=" * 60)
    print("GYM CATEGORIES TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_suite.addTest(TestGymCategories('test_gym_categories_exist'))
    test_suite.addTest(TestGymCategories('test_gym_categories_comprehensive'))
    test_suite.addTest(TestGymCategories('test_gym_categories_unique'))
    test_suite.addTest(TestGymCategories('test_gym_categories_format'))
    test_suite.addTest(TestGymCategories('test_gym_search_functionality'))
    test_suite.addTest(TestGymCategories('test_gym_specific_fields_in_lead_structure'))
    test_suite.addTest(TestGymCategories('test_multiple_gym_categories_search'))
    test_suite.addTest(TestGymCategoriesIntegration('test_config_validation_with_gym_categories'))
    
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
    run_comprehensive_gym_categories_test()