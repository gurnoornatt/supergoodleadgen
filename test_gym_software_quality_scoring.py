#!/usr/bin/env python3
"""
Test suite for gym software quality scoring system integration
"""
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor
from gym_software_database import gym_software_db, SoftwareQuality

class TestGymSoftwareQualityScoring(unittest.TestCase):
    """Test gym software quality scoring system integration"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.lead_processor = LeadProcessor()
        
        # Base gym lead for testing
        self.base_gym_lead = {
            'business_name': 'Test Fitness Center',
            'website': 'https://testfitness.com',
            'phone': '(555) 123-4567',
            'address': '123 Fitness St, Fresno, CA',
            'place_id': 'test123',
            'rating': 4.5,
            'reviews': 150,
            'gps_coordinates': {'latitude': 36.7378, 'longitude': -119.7871},
            'status': 'pending',
            'mobile_score': 75,
            'technologies': [],
            'outdated_technologies': [],
            'technology_age_score': 70,
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
            'gym_software_quality_score': 50,
            'gym_software_recommendations': [],
            'gym_software_red_flags': []
        }
    
    def test_premium_software_quality_scoring(self):
        """Test quality scoring for premium software platforms"""
        # Test MindBody (premium platform)
        mindbody_score = gym_software_db.score_software_quality("MindBody")
        
        # Verify premium scoring characteristics
        self.assertGreater(mindbody_score['quality_score'], 85)
        self.assertEqual(mindbody_score['quality_tier'], 'premium')
        self.assertTrue(mindbody_score['mobile_app'])
        self.assertTrue(mindbody_score['api_available'])
        self.assertIn('Excellent choice', mindbody_score['recommendation'])
        
        print(f"✓ MindBody premium scoring: {mindbody_score['quality_score']} points")
        print(f"   Features: {mindbody_score['feature_count']}, Integrations: {mindbody_score['integration_count']}")
    
    def test_outdated_software_quality_scoring(self):
        """Test quality scoring for outdated software platforms"""
        # Test ABC Financial (outdated platform)
        abc_score = gym_software_db.score_software_quality("ABC Financial")
        
        # Verify outdated scoring characteristics
        self.assertLess(abc_score['quality_score'], 40)
        self.assertEqual(abc_score['quality_tier'], 'outdated')
        self.assertFalse(abc_score['mobile_app'])
        self.assertFalse(abc_score['api_available'])
        self.assertIn('Concerning', abc_score['recommendation'])
        
        print(f"✓ ABC Financial outdated scoring: {abc_score['quality_score']} points")
        print(f"   Years since update: {abc_score['years_since_update']}")
    
    def test_software_scoring_factors(self):
        """Test individual factors in software quality scoring"""
        # Test a mid-range platform
        zenplanner_score = gym_software_db.score_software_quality("Zen Planner")
        
        # Verify scoring components are reasonable (Zen Planner scores high due to features/integrations)
        self.assertGreaterEqual(zenplanner_score['quality_score'], 60)
        self.assertEqual(zenplanner_score['quality_tier'], 'good')
        self.assertTrue(zenplanner_score['mobile_app'])  # Should have mobile app
        self.assertTrue(zenplanner_score['api_available'])  # Should have API
        
        # Check that features and integrations contribute to score
        self.assertGreater(zenplanner_score['feature_count'], 4)
        self.assertGreater(zenplanner_score['integration_count'], 2)
        
        print(f"✓ Zen Planner mid-range scoring: {zenplanner_score['quality_score']} points")
        print(f"   Mobile: {zenplanner_score['mobile_app']}, API: {zenplanner_score['api_available']}")
    
    def test_basic_software_quality_scoring(self):
        """Test quality scoring for basic software platforms"""
        # Test Calendly (basic platform)
        calendly_score = gym_software_db.score_software_quality("Calendly")
        
        # Verify basic platform characteristics (Calendly scores higher due to integrations but still basic tier)
        self.assertEqual(calendly_score['quality_tier'], 'basic')
        self.assertIn('not_gym_specific', calendly_score['weaknesses'])
        self.assertIn('Acceptable', calendly_score['recommendation'])
        
        print(f"✓ Calendly basic scoring: {calendly_score['quality_score']} points")
        print(f"   Recommendation: {calendly_score['recommendation']}")
    
    def test_software_quality_integration_with_pain_scoring(self):
        """Test integration of software quality with pain scoring system"""
        # Test with premium software (should result in lower pain)
        premium_lead = self.base_gym_lead.copy()
        premium_lead.update({
            'gym_software_quality_score': 95,  # Premium software
            'gym_software_red_flags': []
        })
        
        premium_scored = self.lead_processor.apply_comprehensive_pain_scoring(premium_lead)
        
        # Test with outdated software (should result in higher pain)
        outdated_lead = self.base_gym_lead.copy()
        outdated_lead.update({
            'gym_software_quality_score': 25,  # Outdated software
            'gym_software_red_flags': ['CRITICAL: Outdated software', 'No mobile app', 'Limited integrations']
        })
        
        outdated_scored = self.lead_processor.apply_comprehensive_pain_scoring(outdated_lead)
        
        # Verify pain scoring differences
        self.assertLess(premium_scored['pain_score'], outdated_scored['pain_score'])
        self.assertIn('gym_software_pain', premium_scored['pain_breakdown'])
        self.assertIn('gym_software_pain', outdated_scored['pain_breakdown'])
        
        # Verify gym software pain component
        self.assertLess(premium_scored['pain_breakdown']['gym_software_pain'], 
                       outdated_scored['pain_breakdown']['gym_software_pain'])
        
        print(f"✓ Pain scoring integration:")
        print(f"   Premium software: {premium_scored['pain_score']:.1f} pain")
        print(f"   Outdated software: {outdated_scored['pain_score']:.1f} pain")
        print(f"   Gym software pain component: {premium_scored['pain_breakdown']['gym_software_pain']:.1f} vs {outdated_scored['pain_breakdown']['gym_software_pain']:.1f}")
    
    def test_quality_scoring_weight_distribution(self):
        """Test that gym software quality has proper weight in pain scoring"""
        # Create lead with varying software quality but consistent other scores
        base_scores = {
            'mobile_score': 70,
            'technology_age_score': 70,
            'technology_flags': [],
            'gym_software_red_flags': []
        }
        
        # Test different software quality levels
        quality_levels = [20, 50, 80, 95]
        pain_scores = []
        
        for quality in quality_levels:
            test_lead = self.base_gym_lead.copy()
            test_lead.update(base_scores)
            test_lead['gym_software_quality_score'] = quality
            
            scored_lead = self.lead_processor.apply_comprehensive_pain_scoring(test_lead)
            pain_scores.append(scored_lead['pain_score'])
        
        # Verify pain scores decrease as software quality increases
        for i in range(1, len(pain_scores)):
            self.assertLess(pain_scores[i], pain_scores[i-1], 
                           f"Pain should decrease as software quality improves: {pain_scores}")
        
        # Verify reasonable impact of software quality (30% weight)
        total_pain_range = pain_scores[0] - pain_scores[-1]
        self.assertGreater(total_pain_range, 15, "Software quality should have significant impact on pain score")
        
        print(f"✓ Quality weight distribution test:")
        for i, (quality, pain) in enumerate(zip(quality_levels, pain_scores)):
            print(f"   Quality {quality}: Pain {pain:.1f}")
    
    def test_software_red_flags_integration(self):
        """Test that software red flags properly contribute to pain scoring"""
        # Create lead with red flags
        red_flag_lead = self.base_gym_lead.copy()
        red_flag_lead.update({
            'mobile_score': 70,
            'technology_age_score': 70,
            'technology_flags': [],
            'gym_software_quality_score': 40,  # Already problematic
            'gym_software_red_flags': [
                'CRITICAL: Outdated software technology',
                'No mobile app available',
                'Limited integration capabilities'
            ]
        })
        
        # Compare with same lead but no red flags
        no_flag_lead = red_flag_lead.copy()
        no_flag_lead['gym_software_red_flags'] = []
        
        red_flag_scored = self.lead_processor.apply_comprehensive_pain_scoring(red_flag_lead)
        no_flag_scored = self.lead_processor.apply_comprehensive_pain_scoring(no_flag_lead)
        
        # Verify red flags increase pain
        self.assertGreater(red_flag_scored['pain_score'], no_flag_scored['pain_score'])
        self.assertGreater(red_flag_scored['pain_breakdown']['gym_software_pain'], 
                          no_flag_scored['pain_breakdown']['gym_software_pain'])
        
        # Verify red flags appear in pain factors
        pain_factors_text = ' '.join(red_flag_scored['pain_factors'])
        self.assertIn('gym software', pain_factors_text.lower())
        
        print(f"✓ Red flags integration:")
        print(f"   With red flags: {red_flag_scored['pain_score']:.1f} pain")
        print(f"   Without red flags: {no_flag_scored['pain_score']:.1f} pain")
        print(f"   Red flag impact: +{red_flag_scored['pain_score'] - no_flag_scored['pain_score']:.1f} pain points")
    
    def test_comprehensive_software_analysis_workflow(self):
        """Test complete workflow from software detection to pain scoring"""
        # Mock technologies that should detect MindBody
        mock_technologies = [
            {'name': 'MindBody Online', 'category': 'Fitness Management'},
            {'name': 'Healcode Widget', 'category': 'Booking System'},
            {'name': 'jQuery', 'category': 'JavaScript Libraries'}
        ]
        
        # Test complete gym software analysis
        analysis = self.lead_processor._analyze_gym_software(mock_technologies, 'https://mindbodyonline.com')
        
        # Verify comprehensive analysis results
        self.assertIn('Mindbody', analysis['detected_software'])
        self.assertGreater(analysis['overall_quality_score'], 80)
        self.assertIn('MindBody', analysis['software_scores'])
        self.assertGreater(len(analysis['recommendations']), 0)
        
        # Verify detailed scoring information
        mindbody_details = analysis['software_scores']['MindBody']
        self.assertIn('quality_score', mindbody_details)
        self.assertIn('mobile_app', mindbody_details)
        self.assertIn('api_available', mindbody_details)
        self.assertIn('strengths', mindbody_details)
        self.assertIn('weaknesses', mindbody_details)
        
        print(f"✓ Comprehensive workflow test:")
        print(f"   Detected: {', '.join(analysis['detected_software'])}")
        print(f"   Overall quality: {analysis['overall_quality_score']}")
        print(f"   Recommendations: {len(analysis['recommendations'])}")
    
    def test_error_handling_in_quality_scoring(self):
        """Test error handling in quality scoring system"""
        # Test with non-existent software
        fake_score = gym_software_db.score_software_quality("Non-Existent Software")
        self.assertIn('error', fake_score)
        
        # Test analysis with malformed data
        malformed_analysis = self.lead_processor._analyze_gym_software([], None)
        self.assertIsInstance(malformed_analysis, dict)
        self.assertIn('detected_software', malformed_analysis)
        self.assertIsInstance(malformed_analysis['overall_quality_score'], (int, float))
        
        print("✓ Error handling works correctly in quality scoring system")

def run_comprehensive_quality_scoring_test():
    """Run all gym software quality scoring tests and provide detailed report"""
    print("=" * 60)
    print("GYM SOFTWARE QUALITY SCORING TEST SUITE")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_premium_software_quality_scoring',
        'test_outdated_software_quality_scoring', 
        'test_software_scoring_factors',
        'test_basic_software_quality_scoring',
        'test_software_quality_integration_with_pain_scoring',
        'test_quality_scoring_weight_distribution',
        'test_software_red_flags_integration',
        'test_comprehensive_software_analysis_workflow',
        'test_error_handling_in_quality_scoring'
    ]
    
    for method in test_methods:
        test_suite.addTest(TestGymSoftwareQualityScoring(method))
    
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
    run_comprehensive_quality_scoring_test()