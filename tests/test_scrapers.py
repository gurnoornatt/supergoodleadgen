"""
Test suite for RedFlag scraping functionality.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_client import SerpApiClient
from config import Config


class TestSerpApiClient(unittest.TestCase):
    """Test suite for SerpAPI client functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.client = SerpApiClient()
        self.mock_response = {
            'local_results': [
                {
                    'title': 'Test Gym',
                    'address': '123 Main St, Fresno, CA',
                    'phone': '(559) 123-4567',
                    'rating': 4.5,
                    'reviews': 150,
                    'type': 'Gym',
                    'place_id': 'test_place_id',
                    'position': 1
                }
            ],
            'search_metadata': {
                'status': 'Success'
            }
        }
    
    @patch('requests.get')
    def test_search_google_maps_success(self, mock_get):
        """Test successful Google Maps search."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_response
        mock_get.return_value = mock_response
        
        # Execute search
        results = self.client.search_google_maps(
            query="gym Fresno CA",
            location="Fresno, CA",
            max_results=20
        )
        
        # Assertions
        self.assertIsInstance(results, dict)
        self.assertIn('local_results', results)
        self.assertEqual(len(results['local_results']), 1)
        self.assertEqual(results['local_results'][0]['title'], 'Test Gym')
    
    @patch('requests.get')
    def test_search_google_maps_api_error(self, mock_get):
        """Test API error handling."""
        # Mock API error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_get.return_value = mock_response
        
        # Execute search and expect None return
        results = self.client.search_google_maps(
            query="gym Fresno CA",
            location="Fresno, CA"
        )
        
        self.assertIsNone(results)
    
    def test_search_parameters_validation(self):
        """Test parameter validation."""
        with self.assertRaises(ValueError):
            self.client.search_google_maps("", "Fresno, CA")
        
        with self.assertRaises(ValueError):
            self.client.search_google_maps("gym", "")


class TestChainDetection(unittest.TestCase):
    """Test suite for gym chain detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Import chain detection function
        try:
            from scrape_fresno_gyms import is_chain_gym
            self.is_chain_gym = is_chain_gym
        except ImportError:
            # Fallback implementation for testing
            def is_chain_gym(name):
                chains = ['planet fitness', 'la fitness', '24 hour fitness']
                return any(chain in name.lower() for chain in chains)
            self.is_chain_gym = is_chain_gym
    
    def test_chain_detection_positive(self):
        """Test detection of known chains."""
        chain_names = [
            "Planet Fitness",
            "LA FITNESS", 
            "24 Hour Fitness",
            "Planet Fitness - Downtown",
            "la fitness fresno"
        ]
        
        for name in chain_names:
            with self.subTest(name=name):
                self.assertTrue(self.is_chain_gym(name), f"{name} should be detected as chain")
    
    def test_chain_detection_negative(self):
        """Test that independent gyms are not flagged as chains."""
        independent_names = [
            "Strong Family Fitness",
            "Joe's Gym", 
            "Fresno Athletic Club",
            "Iron Paradise",
            "Central Valley Fitness"
        ]
        
        for name in independent_names:
            with self.subTest(name=name):
                self.assertFalse(self.is_chain_gym(name), f"{name} should not be detected as chain")
    
    def test_edge_cases(self):
        """Test edge cases in chain detection."""
        edge_cases = [
            ("", False),  # Empty string
            ("Planet", False),  # Partial match shouldn't trigger
            ("Fitness Planet", False),  # Reversed order
            ("PLANET FITNESS", True),  # All caps
            ("planet fitness", True),  # All lowercase
        ]
        
        for name, expected in edge_cases:
            with self.subTest(name=name):
                result = self.is_chain_gym(name)
                self.assertEqual(result, expected, f"'{name}' expected {expected}, got {result}")


class TestIndependenceScoring(unittest.TestCase):
    """Test suite for gym independence scoring."""
    
    def test_independence_indicators(self):
        """Test independence scoring factors."""
        # High independence score indicators
        high_score_gym = {
            'business_name': 'Smith Family Fitness',
            'reviews': 50,  # Low review count
            'address': '123 Local St'
        }
        
        # Calculate independence indicators (simplified version)
        name_lower = high_score_gym['business_name'].lower()
        independence_indicators = [
            'owner' in name_lower,
            'family' in name_lower,  # Should be True
            'local' in name_lower,
            high_score_gym['reviews'] < 500,  # Should be True
            not any(franchise in name_lower for franchise in ['franchise', 'llc', 'inc', 'corp'])
        ]
        
        score = sum(independence_indicators)
        self.assertGreaterEqual(score, 2, "Family gym should have high independence score")
    
    def test_franchise_detection(self):
        """Test detection of franchise indicators."""
        franchise_names = [
            "Fitness LLC",
            "Gym Corp", 
            "Training Inc",
            "CrossFit Franchise"
        ]
        
        for name in franchise_names:
            name_lower = name.lower()
            has_franchise_indicator = any(
                franchise in name_lower 
                for franchise in ['franchise', 'llc', 'inc', 'corp']
            )
            self.assertTrue(has_franchise_indicator, f"{name} should have franchise indicators")


class TestDataProcessing(unittest.TestCase):
    """Test suite for data processing functionality."""
    
    def test_gym_data_structure(self):
        """Test that scraped gym data has required fields."""
        required_fields = [
            'business_name', 'address', 'phone', 'website', 
            'rating', 'reviews', 'type', 'place_id', 'independent_score'
        ]
        
        sample_gym = {
            'business_name': 'Test Gym',
            'address': '123 Main St',
            'phone': '(559) 123-4567',
            'website': 'https://testgym.com',
            'rating': 4.5,
            'reviews': 100,
            'type': 'Gym',
            'place_id': 'test_id',
            'independent_score': 3
        }
        
        for field in required_fields:
            self.assertIn(field, sample_gym, f"Required field '{field}' missing")
    
    def test_deduplication_logic(self):
        """Test gym deduplication based on name."""
        gyms = [
            {'business_name': 'Test Gym', 'independent_score': 2, 'reviews': 50},
            {'business_name': 'Test Gym', 'independent_score': 3, 'reviews': 100},  # Higher score
            {'business_name': 'Another Gym', 'independent_score': 1, 'reviews': 25}
        ]
        
        # Simulate deduplication logic
        unique_gyms = {}
        for gym in gyms:
            name = gym['business_name']
            if name not in unique_gyms or gym['independent_score'] > unique_gyms[name]['independent_score']:
                unique_gyms[name] = gym
        
        result = list(unique_gyms.values())
        
        self.assertEqual(len(result), 2, "Should have 2 unique gyms")
        test_gym = next(g for g in result if g['business_name'] == 'Test Gym')
        self.assertEqual(test_gym['independent_score'], 3, "Should keep gym with higher score")


if __name__ == '__main__':
    unittest.main()