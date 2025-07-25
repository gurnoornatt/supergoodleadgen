import pytest
from lead_processor import LeadProcessor


class TestGymRevenueQualification:
    """Test gym size and revenue qualification system"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.processor = LeadProcessor()
    
    def test_large_crossfit_premium_pricing(self):
        """Test revenue qualification for large CrossFit gym with premium pricing"""
        lead = {
            'business_name': 'Elite CrossFit',
            'gym_size_estimate': 'large',
            'gym_type': 'crossfit',
            'gym_pricing_indicators': ['premium', 'high_price'],
            'reviews_count': 600,
            'rating': 4.8
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Large CrossFit (2500 base * 0.4 multiplier * 1.3 for high reviews = 1300 members)
        # Premium pricing: $200/member = $260,000/month
        assert result['size_qualification'] == 'highly_qualified'
        assert result['revenue_potential'] == 'very_high'
        assert result['estimated_member_count'] == 1300
        assert result['estimated_monthly_revenue'] == 260000
        assert result['revenue_tier'] == 'enterprise'
        assert result['size_tier'] == 'large'
        assert result['viability_score'] >= 70
        assert result['estimated_monthly_software_budget'] == 7800  # 3% of revenue for CrossFit
        assert 'Very high revenue potential ($100K+/month)' in result['qualification_reasons']
        assert 'Good member base size (~1300 members)' in result['qualification_reasons']
        assert 'Excellent reputation (4.5+ rating, 100+ reviews)' in result['qualification_reasons']
    
    def test_medium_traditional_gym_budget_pricing(self):
        """Test revenue qualification for medium traditional gym with budget pricing"""
        lead = {
            'business_name': 'Budget Fitness Center',
            'gym_size_estimate': 'medium',
            'gym_type': 'traditional_gym',
            'gym_pricing_indicators': ['budget_friendly'],
            'reviews_count': 250,
            'rating': 4.2
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Medium traditional (600 base * 1.0 multiplier * 1.1 for reviews = 660 members)
        # Budget pricing: $20/member = $13,200/month
        assert result['size_qualification'] == 'qualified'  # 60 points is qualified
        assert result['revenue_potential'] == 'low'
        assert result['estimated_member_count'] == 660
        assert result['estimated_monthly_revenue'] == 13200
        assert result['revenue_tier'] == 'small'
        assert result['size_tier'] == 'medium'  # 660 members is medium (300-999)
        assert result['viability_score'] >= 50  # Actually gets 60 points
        assert result['estimated_monthly_software_budget'] == 264  # 2% of revenue
        assert 'Low revenue potential ($10K-20K/month)' in result['qualification_reasons']
        assert 'Good member base size (~660 members)' in result['qualification_reasons']
    
    def test_small_personal_training_high_pricing(self):
        """Test revenue qualification for small personal training studio with high pricing"""
        lead = {
            'business_name': 'Elite Personal Training',
            'gym_size_estimate': 'small',
            'gym_type': 'personal_training',
            'gym_pricing_indicators': ['premium'],
            'reviews_count': 40,
            'rating': 4.9
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Small personal training (150 base * 0.2 multiplier * 0.7 for low reviews = 21 members)
        # Premium pricing: $600/member = $12,600/month
        assert result['size_qualification'] == 'unqualified'
        assert result['revenue_potential'] == 'low'
        assert result['estimated_member_count'] == 21
        assert result['estimated_monthly_revenue'] == 12600
        assert result['revenue_tier'] == 'small'
        assert result['size_tier'] == 'micro'
        assert result['viability_score'] < 30
        assert result['estimated_monthly_software_budget'] == 189  # 1.5% of revenue for PT
        assert 'Very small member base (<100 members)' in result['disqualification_reasons']
    
    def test_large_health_club_mid_pricing(self):
        """Test revenue qualification for large health club with mid-tier pricing"""
        lead = {
            'business_name': 'Premier Health Club',
            'gym_size_estimate': 'large',
            'gym_type': 'health_club',
            'gym_pricing_indicators': [],  # No specific indicators = mid
            'reviews_count': 800,
            'rating': 4.5
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Large health club (2500 base * 1.2 multiplier * 1.3 for high reviews = 3900 members)
        # Mid pricing: $80/member = $312,000/month
        assert result['size_qualification'] == 'highly_qualified'
        assert result['revenue_potential'] == 'very_high'
        assert result['estimated_member_count'] == 3900
        assert result['estimated_monthly_revenue'] == 312000
        assert result['revenue_tier'] == 'enterprise'
        assert result['size_tier'] == 'large'
        assert result['viability_score'] >= 70
        assert result['estimated_monthly_software_budget'] == 6240  # 2% of revenue
        assert 'Strong software budget potential (~$6240/month)' in result['qualification_reasons']
    
    def test_boutique_fitness_studio(self):
        """Test revenue qualification for boutique fitness studio"""
        lead = {
            'business_name': 'Boutique Pilates Studio',
            'gym_size_estimate': 'medium',
            'gym_type': 'boutique_fitness',
            'gym_pricing_indicators': ['premium'],
            'reviews_count': 150,
            'rating': 4.7
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Medium boutique (600 base * 0.5 multiplier = 300 members)
        # Premium pricing: $180/member = $54,000/month
        assert result['size_qualification'] == 'highly_qualified'
        assert result['revenue_potential'] == 'high'
        assert result['estimated_member_count'] == 300
        assert result['estimated_monthly_revenue'] == 54000
        assert result['revenue_tier'] == 'large'
        assert result['size_tier'] == 'medium'
        assert result['viability_score'] >= 50
        assert result['estimated_monthly_software_budget'] == 1620  # 3% of revenue for boutique
        assert 'High-growth gym type (boutique_fitness)' in result['qualification_reasons']
    
    def test_unknown_gym_size_and_type(self):
        """Test revenue qualification with unknown gym size and type"""
        lead = {
            'business_name': 'Mystery Gym',
            'gym_size_estimate': 'unknown',
            'gym_type': 'unknown',
            'gym_pricing_indicators': [],
            'reviews_count': 100,
            'rating': 4.0
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Unknown size and type uses defaults
        assert result['size_qualification'] in ['marginally_qualified', 'qualified']
        assert result['estimated_member_count'] == 250  # Default for unknown
        assert result['size_tier'] == 'small'
        assert result['revenue_potential'] in ['low', 'medium']
    
    def test_poor_reputation_disqualification(self):
        """Test impact of poor reputation on qualification"""
        lead = {
            'business_name': 'Bad Reviews Gym',
            'gym_size_estimate': 'large',
            'gym_type': 'fitness_center',
            'gym_pricing_indicators': ['premium'],
            'reviews_count': 200,
            'rating': 3.2
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Large premium gym still qualifies despite poor reputation due to high revenue/size
        assert result['size_qualification'] == 'highly_qualified'
        assert 'Poor reputation (rating < 3.5)' in result['disqualification_reasons']
        assert result['viability_score'] >= 70  # Gets 80 points despite poor reputation
        
        # Test actual disqualification with small gym and poor reputation
        small_poor_gym = {
            'business_name': 'Small Bad Gym',
            'gym_size_estimate': 'small',
            'gym_type': 'traditional_gym',
            'gym_pricing_indicators': ['budget_friendly'],
            'reviews_count': 30,
            'rating': 3.0
        }
        
        result2 = self.processor._qualify_gym_size_and_revenue(small_poor_gym)
        assert result2['size_qualification'] == 'unqualified'
        assert 'Poor reputation (rating < 3.5)' in result2['disqualification_reasons']
        assert result2['viability_score'] < 30
    
    def test_micro_gym_disqualification(self):
        """Test disqualification for very small gyms"""
        lead = {
            'business_name': 'Tiny Yoga Studio',
            'gym_size_estimate': 'small',
            'gym_type': 'yoga_studio',
            'gym_pricing_indicators': ['budget_friendly'],
            'reviews_count': 20,
            'rating': 4.5
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Small yoga (150 base * 0.6 multiplier * 0.7 for low reviews = 63 members)
        # Budget pricing: $60/member = $3,780/month
        assert result['size_qualification'] == 'unqualified'
        assert result['revenue_potential'] == 'very_low'
        assert result['estimated_member_count'] in [62, 63]  # Rounding may vary
        assert result['revenue_tier'] == 'micro'
        assert result['size_tier'] == 'micro'
        assert 'Very low revenue potential (<$10K/month)' in result['disqualification_reasons']
        assert 'Very small member base (<100 members)' in result['disqualification_reasons']
        assert 'Limited software budget (<$500/month)' in result['disqualification_reasons']
    
    def test_martial_arts_school_qualification(self):
        """Test revenue qualification for martial arts school"""
        lead = {
            'business_name': 'Dragon Martial Arts',
            'gym_size_estimate': 'medium',
            'gym_type': 'martial_arts',
            'gym_pricing_indicators': [],
            'reviews_count': 180,
            'rating': 4.6
        }
        
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Medium martial arts (600 base * 0.7 multiplier = 420 members)
        # Mid pricing: $100/member = $42,000/month
        assert result['size_qualification'] == 'qualified'
        assert result['revenue_potential'] == 'medium'
        assert result['estimated_member_count'] == 420
        assert result['estimated_monthly_revenue'] == 42000
        assert result['revenue_tier'] == 'medium'
        assert result['viability_score'] >= 50
    
    def test_software_budget_calculation(self):
        """Test software budget calculation for different gym types"""
        # CrossFit - 3% of revenue
        crossfit_lead = {
            'business_name': 'CrossFit Test',
            'gym_size_estimate': 'medium',
            'gym_type': 'crossfit',
            'gym_pricing_indicators': [],
            'reviews_count': 100,
            'rating': 4.0
        }
        result = self.processor._qualify_gym_size_and_revenue(crossfit_lead)
        expected_budget = int(result['estimated_monthly_revenue'] * 0.03)
        assert result['estimated_monthly_software_budget'] == expected_budget
        
        # Personal training - 1.5% of revenue
        pt_lead = {
            'business_name': 'PT Test',
            'gym_size_estimate': 'medium',
            'gym_type': 'personal_training',
            'gym_pricing_indicators': [],
            'reviews_count': 100,
            'rating': 4.0
        }
        result = self.processor._qualify_gym_size_and_revenue(pt_lead)
        expected_budget = int(result['estimated_monthly_revenue'] * 0.015)
        assert result['estimated_monthly_software_budget'] == expected_budget
        
        # Traditional gym - 2% of revenue
        trad_lead = {
            'business_name': 'Traditional Test',
            'gym_size_estimate': 'medium',
            'gym_type': 'traditional_gym',
            'gym_pricing_indicators': [],
            'reviews_count': 100,
            'rating': 4.0
        }
        result = self.processor._qualify_gym_size_and_revenue(trad_lead)
        expected_budget = int(result['estimated_monthly_revenue'] * 0.02)
        assert result['estimated_monthly_software_budget'] == expected_budget
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        # Test with missing data
        lead = {}
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # With empty data, it still runs with defaults and gets unqualified
        assert result['size_qualification'] == 'unqualified'
        assert result['revenue_potential'] in ['low', 'very_low']
        assert result['viability_score'] < 30
        
        # Test with None values
        lead = {
            'business_name': 'None Gym',
            'gym_size_estimate': None,
            'gym_type': None,
            'reviews_count': None,
            'rating': None
        }
        result = self.processor._qualify_gym_size_and_revenue(lead)
        
        # Should handle gracefully without raising exception
        assert result['size_qualification'] in ['unknown', 'unqualified', 'marginally_qualified', 'qualified', 'highly_qualified']