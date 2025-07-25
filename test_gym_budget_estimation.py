import pytest
from lead_processor import LeadProcessor


class TestGymBudgetEstimation:
    """Test gym software budget estimation system"""
    
    def setup_method(self):
        """Set up test data before each test"""
        self.processor = LeadProcessor()
    
    def test_large_crossfit_high_digital_maturity(self):
        """Test budget estimation for large CrossFit with high digital maturity"""
        lead = {
            'business_name': 'Elite CrossFit Box',
            'gym_estimated_monthly_revenue': 200000,
            'gym_estimated_member_count': 1000,
            'gym_type': 'crossfit',
            'gym_size_estimate': 'large',
            'gym_software_detected': ['mindbody', 'wodify'],
            'gym_digital_infrastructure_score': 85,
            'gym_classification': 'red',
            'gym_franchise_chain': ''
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Base: 200,000 * 3.5% = 7,000
        # Digital maturity high: * 1.3 = 9,100
        # Has software (not basic): no adjustment
        expected_budget = 9100
        
        assert result['estimated_total_budget'] == expected_budget
        assert result['pricing_tier'] == 'enterprise'
        assert result['recommended_package'] == 'enterprise_unlimited'
        assert result['budget_confidence'] == 'high'  # Has all data points
        
        # Check budget breakdown
        assert result['budget_breakdown']['core_platform'] == int(expected_budget * 0.6)
        assert result['budget_breakdown']['mobile_app'] == int(expected_budget * 0.2)
        
        # Check factors
        assert 'High digital maturity (+30% budget)' in result['budget_factors']
        assert any('Enterprise tier:' in f for f in result['budget_factors'])
        
        # Check contract recommendations
        assert result['contract_recommendations']['term'] == 'annual'
        assert result['contract_recommendations']['negotiation_leverage'] == 'high'
        
        # Check competitor spend
        assert result['competitor_spend_estimate'] == int(expected_budget * 1.1)  # CrossFit multiplier
    
    def test_medium_traditional_gym_no_software(self):
        """Test budget estimation for medium traditional gym with no software"""
        lead = {
            'business_name': 'Local Fitness Center',
            'gym_estimated_monthly_revenue': 50000,
            'gym_estimated_member_count': 600,
            'gym_type': 'traditional_gym',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 45,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Base: 50,000 * 2% = 1,000
        # Digital maturity medium: no adjustment
        # No software: * 1.2 = 1,200
        expected_budget = 1200
        
        assert result['estimated_total_budget'] == expected_budget
        assert result['pricing_tier'] == 'professional'
        assert result['recommended_package'] == 'professional_plus'
        assert result['budget_confidence'] == 'high'
        
        # Check factors
        assert 'Limited current software (+20% budget for initial setup)' in result['budget_factors']
        
        # Check contract recommendations for yellow medium gym
        assert result['contract_recommendations']['term'] == 'month-to-month'
        assert result['contract_recommendations']['negotiation_leverage'] == 'low'
    
    def test_small_boutique_low_digital_score(self):
        """Test budget estimation for small boutique with low digital maturity"""
        lead = {
            'business_name': 'Boutique Pilates',
            'gym_estimated_monthly_revenue': 20000,
            'gym_estimated_member_count': 150,
            'gym_type': 'boutique_fitness',
            'gym_size_estimate': 'small',
            'gym_software_detected': ['basic_booking'],
            'gym_digital_infrastructure_score': 30,
            'gym_classification': 'red',
            'gym_franchise_chain': ''
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Base: 20,000 * 3% = 600
        # Digital maturity low: * 0.8 = 480
        # Has basic software: * 1.2 = 576
        expected_budget = 576
        
        assert result['estimated_total_budget'] == expected_budget
        assert result['pricing_tier'] == 'basic'
        assert result['recommended_package'] == 'starter'
        
        # Check factors
        assert 'Low digital maturity (-20% budget)' in result['budget_factors']
        assert 'Limited current software (+20% budget for initial setup)' in result['budget_factors']
    
    def test_franchise_gym_budget(self):
        """Test budget estimation for franchise gym"""
        lead = {
            'business_name': 'Anytime Fitness - Downtown',
            'gym_estimated_monthly_revenue': 150000,
            'gym_estimated_member_count': 1500,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'large',
            'gym_software_detected': ['franchise_system'],
            'gym_digital_infrastructure_score': 70,
            'gym_classification': 'green',
            'gym_franchise_chain': 'Anytime Fitness'
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Check franchise gets annual contract recommendations
        assert result['contract_recommendations']['term'] == 'annual'
        assert result['contract_recommendations']['negotiation_leverage'] == 'high'
        assert 'Multi-location discount' in result['contract_recommendations']['key_terms']
    
    def test_multiple_systems_consolidation(self):
        """Test budget adjustment for gyms with multiple systems"""
        lead = {
            'business_name': 'Overloaded Gym',
            'gym_estimated_monthly_revenue': 80000,
            'gym_estimated_member_count': 800,
            'gym_type': 'health_club',
            'gym_size_estimate': 'medium',
            'gym_software_detected': ['mindbody', 'zenplanner', 'myfitnesspal', 'custom_app'],
            'gym_digital_infrastructure_score': 65,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Has 4 systems - should get consolidation discount
        assert 'Multiple systems in place (-10% for consolidation)' in result['budget_factors']
        
        # Base: 80,000 * 2.5% = 2,000
        # Digital good: * 1.1 = 2,200
        # Multiple systems: * 0.9 = 1,980
        assert result['estimated_total_budget'] == 1980
    
    def test_personal_training_minimal_needs(self):
        """Test budget estimation for personal training studio"""
        lead = {
            'business_name': 'PT Studio',
            'gym_estimated_monthly_revenue': 15000,
            'gym_estimated_member_count': 30,
            'gym_type': 'personal_training',
            'gym_size_estimate': 'small',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 50,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Personal training has lowest base percentage (1.5%)
        # Base: 15,000 * 1.5% = 225
        # No software: * 1.2 = 270
        assert result['estimated_total_budget'] == 270
        assert result['pricing_tier'] == 'basic'
        
        # Should have different budget breakdown (more core, less mobile)
        assert result['budget_breakdown']['core_platform'] == int(270 * 0.7)
        assert result['budget_breakdown']['mobile_app'] == int(270 * 0.15)
    
    def test_pricing_tiers_by_member_count(self):
        """Test correct pricing tier assignment by member count"""
        # Enterprise tier (1000+ members)
        lead_enterprise = {
            'gym_estimated_monthly_revenue': 100000,
            'gym_estimated_member_count': 1200,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'large',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'green',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_enterprise)
        assert result['pricing_tier'] == 'enterprise'
        assert result['recommended_package'] == 'enterprise_unlimited'
        
        # Professional tier (500-999 members)
        lead_professional = {
            'gym_estimated_monthly_revenue': 50000,
            'gym_estimated_member_count': 600,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'green',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_professional)
        assert result['pricing_tier'] == 'professional'
        assert result['recommended_package'] == 'professional_plus'
        
        # Standard tier (200-499 members)
        lead_standard = {
            'gym_estimated_monthly_revenue': 25000,
            'gym_estimated_member_count': 300,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'green',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_standard)
        assert result['pricing_tier'] == 'standard'
        assert result['recommended_package'] == 'standard'
        
        # Basic tier (<200 members)
        lead_basic = {
            'gym_estimated_monthly_revenue': 10000,
            'gym_estimated_member_count': 100,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'small',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'green',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_basic)
        assert result['pricing_tier'] == 'basic'
        assert result['recommended_package'] == 'starter'
    
    def test_roi_projections(self):
        """Test ROI projection calculations"""
        lead = {
            'business_name': 'ROI Test Gym',
            'gym_estimated_monthly_revenue': 100000,
            'gym_estimated_member_count': 1000,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'large',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'red',
            'gym_franchise_chain': ''
        }
        
        result = self.processor._estimate_gym_software_budget(lead)
        
        assert 'roi_projections' in result
        roi = result['roi_projections']
        
        # Check ROI calculations
        assert roi['monthly_efficiency_savings'] == int(result['estimated_total_budget'] * 2.5)
        assert roi['member_retention_value'] > 0  # 2% retention improvement
        assert roi['new_member_acquisition'] > 0  # 5% growth
        assert roi['payback_period_months'] >= 3
        
        # Check ROI is mentioned in factors
        assert any('Projected ROI:' in f for f in result['budget_factors'])
    
    def test_budget_confidence_levels(self):
        """Test budget confidence calculation"""
        # High confidence - all data available
        lead_high = {
            'gym_estimated_monthly_revenue': 50000,
            'gym_estimated_member_count': 500,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'medium',
            'gym_software_detected': ['mindbody'],
            'gym_digital_infrastructure_score': 70,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_high)
        assert result['budget_confidence'] == 'high'
        
        # Medium confidence - missing some data
        lead_medium = {
            'gym_estimated_monthly_revenue': 50000,
            'gym_estimated_member_count': 500,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 0,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_medium)
        assert result['budget_confidence'] == 'medium'
        
        # Low confidence - minimal data
        lead_low = {
            'gym_estimated_monthly_revenue': 0,
            'gym_estimated_member_count': 0,
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 0,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_low)
        assert result['budget_confidence'] == 'low'
    
    def test_competitor_spend_estimates(self):
        """Test competitor spend estimation by gym type"""
        # CrossFit - higher spend
        lead_crossfit = {
            'gym_estimated_monthly_revenue': 50000,
            'gym_estimated_member_count': 300,
            'gym_type': 'crossfit',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_crossfit)
        assert result['competitor_spend_estimate'] == int(result['estimated_total_budget'] * 1.1)
        
        # Traditional gym - lower spend
        lead_traditional = {
            'gym_estimated_monthly_revenue': 50000,
            'gym_estimated_member_count': 600,
            'gym_type': 'traditional_gym',
            'gym_size_estimate': 'medium',
            'gym_software_detected': [],
            'gym_digital_infrastructure_score': 60,
            'gym_classification': 'yellow',
            'gym_franchise_chain': ''
        }
        result = self.processor._estimate_gym_software_budget(lead_traditional)
        assert result['competitor_spend_estimate'] == int(result['estimated_total_budget'] * 0.9)
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        # Test with empty data
        lead = {}
        result = self.processor._estimate_gym_software_budget(lead)
        
        # With empty data, it runs with defaults - revenue 0 means budget 0
        assert result['estimated_total_budget'] == 0
        assert result['budget_confidence'] == 'low'
        # May have default factors even with 0 budget
        assert result['pricing_tier'] in ['basic', 'unknown']
        
        # Test with None values
        lead = {
            'gym_estimated_monthly_revenue': None,
            'gym_estimated_member_count': None,
            'gym_type': None,
            'gym_software_detected': None
        }
        result = self.processor._estimate_gym_software_budget(lead)
        
        # Should handle gracefully
        assert result['estimated_total_budget'] == 0
        assert result['pricing_tier'] == 'unknown'