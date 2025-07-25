#!/usr/bin/env python3
"""
Test suite for gym software database functionality
"""
import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gym_software_database import (
    GymSoftwareDatabase, 
    SoftwareCategory, 
    SoftwareQuality,
    gym_software_db
)

class TestGymSoftwareDatabase(unittest.TestCase):
    """Test gym software database functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.db = gym_software_db
    
    def test_database_initialization(self):
        """Test that database initializes properly"""
        self.assertIsInstance(self.db, GymSoftwareDatabase)
        self.assertGreater(len(self.db.software_db), 10)
        self.assertGreater(len(self.db.detection_map), 50)
        print(f"✓ Database initialized with {len(self.db.software_db)} software platforms")
        print(f"✓ Detection map contains {len(self.db.detection_map)} signatures")
    
    def test_software_retrieval_by_name(self):
        """Test retrieving software by name"""
        # Test exact name matches
        mindbody = self.db.get_software_by_name("MindBody")
        self.assertIsNotNone(mindbody)
        self.assertEqual(mindbody.name, "MindBody")
        self.assertEqual(mindbody.quality, SoftwareQuality.PREMIUM)
        
        zenplanner = self.db.get_software_by_name("Zen Planner")
        self.assertIsNotNone(zenplanner)
        self.assertEqual(zenplanner.category, SoftwareCategory.ALL_IN_ONE)
        
        # Test case insensitivity and spacing
        wodify = self.db.get_software_by_name("wodify")
        self.assertIsNotNone(wodify)
        self.assertEqual(wodify.category, SoftwareCategory.CROSSFIT)
        
        print("✓ Software retrieval by name working correctly")
    
    def test_software_detection_from_technologies(self):
        """Test detecting software from BuiltWith technology list"""
        # Mock BuiltWith technologies
        mock_technologies = [
            {"name": "MindBody API", "category": "Analytics"},
            {"name": "jQuery", "category": "JavaScript Libraries"},
            {"name": "healcode-widget", "category": "Widgets"},
        ]
        
        detected = self.db.detect_software_from_technologies(mock_technologies)
        self.assertIn("mindbody", detected)
        
        # Test Wodify detection
        wodify_tech = [
            {"name": "Wodify Core", "category": "Fitness Management"},
            {"name": "React", "category": "JavaScript Frameworks"}
        ]
        
        detected_wodify = self.db.detect_software_from_technologies(wodify_tech)
        self.assertIn("wodify", detected_wodify)
        
        print("✓ Technology-based software detection working")
    
    def test_software_detection_from_url(self):
        """Test detecting software from URL patterns"""
        # Test various URL patterns
        test_urls = [
            ("https://widgets.mindbodyonline.com/booking", ["mindbody"]),
            ("https://app.zenplanner.com/login", ["zen_planner"]),
            ("http://myaccount.wodify.com", ["wodify"]),
            ("https://goteamup.com/schedule", ["teamup"]),
            ("https://normal-website.com", [])
        ]
        
        for url, expected in test_urls:
            detected = self.db.detect_software_from_url(url)
            for exp in expected:
                self.assertIn(exp, detected, f"Failed to detect {exp} from {url}")
        
        print("✓ URL-based software detection working")
    
    def test_software_categorization(self):
        """Test retrieving software by category"""
        crossfit_software = self.db.get_software_by_category(SoftwareCategory.CROSSFIT)
        self.assertGreater(len(crossfit_software), 0)
        
        # Verify all returned software are actually CrossFit category
        for software in crossfit_software:
            self.assertEqual(software.category, SoftwareCategory.CROSSFIT)
        
        boutique_software = self.db.get_software_by_category(SoftwareCategory.BOUTIQUE_FITNESS)
        self.assertGreater(len(boutique_software), 0)
        
        print(f"✓ Found {len(crossfit_software)} CrossFit software platforms")
        print(f"✓ Found {len(boutique_software)} boutique fitness platforms")
    
    def test_software_quality_filtering(self):
        """Test filtering software by quality"""
        premium_software = self.db.get_software_by_quality(SoftwareQuality.PREMIUM)
        self.assertGreater(len(premium_software), 0)
        
        outdated_software = self.db.get_software_by_quality(SoftwareQuality.OUTDATED)
        self.assertGreater(len(outdated_software), 0)
        
        for software in premium_software:
            self.assertEqual(software.quality, SoftwareQuality.PREMIUM)
        
        print(f"✓ Found {len(premium_software)} premium software platforms")
        print(f"✓ Found {len(outdated_software)} outdated software platforms")
    
    def test_outdated_software_detection(self):
        """Test detecting outdated software"""
        outdated = self.db.get_outdated_software(2023)
        self.assertGreater(len(outdated), 0)
        
        # Verify all returned software are actually outdated
        for software in outdated:
            self.assertLessEqual(software.last_updated, 2023)
        
        print(f"✓ Found {len(outdated)} software platforms not updated since 2023")
    
    def test_software_quality_scoring(self):
        """Test software quality scoring system"""
        # Test premium software
        mindbody_score = self.db.score_software_quality("MindBody")
        self.assertIsInstance(mindbody_score, dict)
        self.assertIn("quality_score", mindbody_score)
        self.assertGreater(mindbody_score["quality_score"], 80)  # Should be high quality
        
        # Test outdated software
        abc_score = self.db.score_software_quality("ABC Financial")
        self.assertLess(abc_score["quality_score"], 50)  # Should be low quality
        
        # Test non-existent software
        fake_score = self.db.score_software_quality("NonExistent Software")
        self.assertIn("error", fake_score)
        
        print(f"✓ MindBody quality score: {mindbody_score['quality_score']}")
        print(f"✓ ABC Financial quality score: {abc_score['quality_score']}")
    
    def test_software_scoring_components(self):
        """Test individual components of software scoring"""
        glofox_score = self.db.score_software_quality("Glofox")
        
        # Verify score components are present
        required_fields = [
            "software_name", "quality_score", "quality_tier", 
            "last_updated", "mobile_app", "api_available",
            "feature_count", "integration_count", "strengths", 
            "weaknesses", "recommendation"
        ]
        
        for field in required_fields:
            self.assertIn(field, glofox_score, f"Missing field: {field}")
        
        # Test score reasonableness
        self.assertGreaterEqual(glofox_score["quality_score"], 0)
        self.assertLessEqual(glofox_score["quality_score"], 100)
        
        print(f"✓ Glofox comprehensive scoring: {glofox_score['quality_score']} points")
        print(f"   Features: {glofox_score['feature_count']}, Integrations: {glofox_score['integration_count']}")
    
    def test_comprehensive_software_coverage(self):
        """Test that database covers major software categories"""
        all_software = self.db.get_all_software_names()
        
        # Must-have software platforms
        essential_platforms = [
            "MindBody", "Zen Planner", "Wodify", "Glofox", "TeamUp",
            "WellnessLiving", "ClubReady", "Calendly", "Square"
        ]
        
        for platform in essential_platforms:
            self.assertIn(platform, all_software, f"Missing essential platform: {platform}")
        
        print(f"✓ Database covers {len(all_software)} software platforms")
        print("✓ All essential platforms are included")
    
    def test_detection_signature_coverage(self):
        """Test that detection signatures are comprehensive"""
        # Test that major platforms have multiple detection methods
        mindbody = self.db.get_software_by_name("MindBody")
        self.assertGreater(len(mindbody.detection_signatures), 3)
        
        wodify = self.db.get_software_by_name("Wodify")
        self.assertGreater(len(wodify.detection_signatures), 2)
        
        # Test that signatures are unique and don't conflict
        all_signatures = []
        for software in self.db.software_db.values():
            all_signatures.extend(software.detection_signatures)
        
        # Check for reasonable number of unique signatures
        unique_signatures = set(all_signatures)
        self.assertGreater(len(unique_signatures), 50)
        
        print(f"✓ {len(unique_signatures)} unique detection signatures")
        print(f"✓ Average {len(all_signatures)/len(self.db.software_db):.1f} signatures per platform")
    
    def test_database_statistics(self):
        """Test database statistics generation"""
        stats = self.db.get_database_stats()
        
        required_stats = [
            "total_software_count", "category_breakdown", 
            "quality_breakdown", "outdated_software_count", 
            "detection_signatures"
        ]
        
        for stat in required_stats:
            self.assertIn(stat, stats)
        
        # Verify reasonable numbers
        self.assertGreater(stats["total_software_count"], 10)
        self.assertGreater(stats["detection_signatures"], 50)
        self.assertGreater(stats["outdated_software_count"], 0)
        
        print("✓ Database statistics:")
        print(f"   Total software: {stats['total_software_count']}")
        print(f"   Detection signatures: {stats['detection_signatures']}")
        print(f"   Outdated platforms: {stats['outdated_software_count']}")
    
    def test_real_world_detection_scenarios(self):
        """Test realistic detection scenarios"""
        # Scenario 1: Gym using MindBody
        mindbody_tech = [
            {"name": "Healcode", "category": "Booking Widget"},
            {"name": "MindBody Online", "category": "Fitness Management"},
        ]
        detected = self.db.detect_software_from_technologies(mindbody_tech)
        self.assertIn("mindbody", detected)
        
        # Scenario 2: CrossFit gym using Wodify
        wodify_url = "https://app.wodify.com/Schedule/CalendarListViewEntry.aspx"
        detected_url = self.db.detect_software_from_url(wodify_url)
        self.assertIn("wodify", detected_url)
        
        # Scenario 3: Small studio using basic solution
        calendly_tech = [{"name": "Calendly Widget", "category": "Scheduling"}]
        detected_basic = self.db.detect_software_from_technologies(calendly_tech)
        self.assertIn("calendly", detected_basic)
        
        print("✓ Real-world detection scenarios working correctly")

def run_comprehensive_gym_software_database_test():
    """Run all gym software database tests and provide detailed report"""
    print("=" * 60)
    print("GYM SOFTWARE DATABASE TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_database_initialization',
        'test_software_retrieval_by_name', 
        'test_software_detection_from_technologies',
        'test_software_detection_from_url',
        'test_software_categorization',
        'test_software_quality_filtering',
        'test_outdated_software_detection',
        'test_software_quality_scoring',
        'test_software_scoring_components',
        'test_comprehensive_software_coverage',
        'test_detection_signature_coverage',
        'test_database_statistics',
        'test_real_world_detection_scenarios'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymSoftwareDatabase(method))
    
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
    run_comprehensive_gym_software_database_test()