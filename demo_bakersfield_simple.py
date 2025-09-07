#!/usr/bin/env python3
"""
Simple demo of gym analysis for Bakersfield gyms
Shows the analysis results without requiring API keys
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

# Sample pre-analyzed data for Bakersfield gyms
def get_demo_results():
    """Get pre-analyzed results for demonstration"""
    gyms = [
        {
            'business_name': 'In-Shape Health Clubs - Bakersfield',
            'website': 'https://www.inshape.com',
            'mobile_score': 82,
            'pain_score': 45,
            'status': 'yellow',
            'technologies': ['Drupal', 'MindBody', 'Salesforce', 'jQuery', 'Google Analytics'],
            'gym_type': 'health_club',
            'gym_size_estimate': 'large',
            'gym_services': ['personal_training', 'group_classes', 'pool', 'basketball'],
            'gym_estimated_monthly_revenue': 185000,
            'gym_estimated_member_count': 2300,
            'gym_viability_score': 85,
            'gym_size_qualification': 'highly_qualified',
            'gym_classification': 'yellow',
            'gym_classification_confidence': 'high',
            'gym_pain_score': 45,
            'gym_pain_urgency': 'medium',
            'gym_primary_pain_category': 'member_retention_risks',
            'gym_decision_structure': 'corporate',
            'gym_contact_quality': 'good',
            'gym_decision_accessibility': 'low',
            'gym_software_budget_total': 4625,
            'gym_pricing_tier': 'enterprise',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 75,
            'gym_digital_infrastructure_tier': 'good',
            'gym_software_detected': ['mindbody'],
            'gym_website_feature_score': 70,
            'gym_mobile_app_quality': 85,
            'analysis_summary': 'Large health club with solid infrastructure but room for improvement in member engagement tools'
        },
        {
            'business_name': 'CrossFit Bakersfield', 
            'website': 'https://crossfitbakersfield.com',
            'mobile_score': 75,
            'pain_score': 65,
            'status': 'red',
            'technologies': ['WordPress', 'WooCommerce', 'Wodify', 'Stripe'],
            'gym_type': 'crossfit',
            'gym_size_estimate': 'medium',
            'gym_services': ['crossfit', 'personal_training', 'nutrition'],
            'gym_estimated_monthly_revenue': 52000,
            'gym_estimated_member_count': 260,
            'gym_viability_score': 72,
            'gym_size_qualification': 'highly_qualified',
            'gym_classification': 'red',
            'gym_classification_confidence': 'very_high',
            'gym_pain_score': 78,
            'gym_pain_urgency': 'high',
            'gym_primary_pain_category': 'operational_inefficiencies',
            'gym_decision_structure': 'owner_operated',
            'gym_contact_quality': 'excellent',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 1820,
            'gym_pricing_tier': 'standard',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 58,
            'gym_digital_infrastructure_tier': 'average',
            'gym_software_detected': ['wodify'],
            'gym_website_feature_score': 50,
            'gym_mobile_app_quality': 75,
            'analysis_summary': 'Growing CrossFit box with strong community but needs better operational tools'
        },
        {
            'business_name': 'Planet Fitness Bakersfield',
            'website': 'https://www.planetfitness.com/gyms/bakersfield-ca', 
            'mobile_score': 45,
            'pain_score': 35,
            'status': 'red',
            'technologies': ['Custom CMS', 'ABC Financial', 'Mobile App'],
            'gym_type': 'fitness_center',
            'gym_size_estimate': 'large',
            'gym_services': ['general_fitness', 'cardio', 'strength_training'],
            'gym_estimated_monthly_revenue': 124000,
            'gym_estimated_member_count': 3100,
            'gym_viability_score': 90,
            'gym_size_qualification': 'highly_qualified',
            'gym_classification': 'red',
            'gym_classification_confidence': 'high',
            'gym_pain_score': 62,
            'gym_pain_urgency': 'high',
            'gym_primary_pain_category': 'competitive_disadvantages',
            'gym_decision_structure': 'corporate',
            'gym_contact_quality': 'fair',
            'gym_decision_accessibility': 'low',
            'gym_software_budget_total': 3100,
            'gym_pricing_tier': 'enterprise',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 42,
            'gym_digital_infrastructure_tier': 'poor',
            'gym_software_detected': ['abc_financial'],
            'gym_website_feature_score': 40,
            'gym_mobile_app_quality': 60,
            'analysis_summary': 'High-volume budget gym with poor digital experience affecting member satisfaction'
        },
        {
            'business_name': 'Elite Personal Training Studio',
            'website': '',
            'mobile_score': 0,
            'pain_score': 85,
            'status': 'red',
            'technologies': ['Square', 'Calendly'],
            'gym_type': 'personal_training',
            'gym_size_estimate': 'small',
            'gym_services': ['personal_training', 'nutrition', 'custom_programs'],
            'gym_estimated_monthly_revenue': 18000,
            'gym_estimated_member_count': 30,
            'gym_viability_score': 25,
            'gym_size_qualification': 'unqualified',
            'gym_classification': 'red', 
            'gym_classification_confidence': 'very_high',
            'gym_pain_score': 92,
            'gym_pain_urgency': 'critical',
            'gym_primary_pain_category': 'growth_limitations',
            'gym_decision_structure': 'owner_direct',
            'gym_contact_quality': 'good',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 270,
            'gym_pricing_tier': 'basic',
            'gym_budget_confidence': 'medium',
            'gym_digital_infrastructure_score': 15,
            'gym_digital_infrastructure_tier': 'critical',
            'gym_software_detected': [],
            'gym_website_feature_score': 0,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Small PT studio with no digital presence severely limiting growth potential'
        },
        {
            'business_name': 'Bakersfield Barbell Club',
            'website': 'https://bakersfieldbarbell.com',
            'mobile_score': 65,
            'pain_score': 55,
            'status': 'yellow',
            'technologies': ['WordPress', 'PayPal', 'Facebook Pixel'],
            'gym_type': 'traditional_gym',
            'gym_size_estimate': 'medium',
            'gym_services': ['powerlifting', 'strength_training', 'olympic_lifting'],
            'gym_estimated_monthly_revenue': 32000,
            'gym_estimated_member_count': 400,
            'gym_viability_score': 58,
            'gym_size_qualification': 'qualified',
            'gym_classification': 'yellow',
            'gym_classification_confidence': 'medium',
            'gym_pain_score': 58,
            'gym_pain_urgency': 'medium',
            'gym_primary_pain_category': 'revenue_loss_factors',
            'gym_decision_structure': 'owner_operated',
            'gym_contact_quality': 'good',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 640,
            'gym_pricing_tier': 'standard',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 52,
            'gym_digital_infrastructure_tier': 'average',
            'gym_software_detected': [],
            'gym_website_feature_score': 30,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Niche strength gym with loyal base but missing digital tools for growth'
        }
    ]
    return gyms

def display_gym_analysis(gym):
    """Display analysis for a single gym"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {gym['business_name']}")
    print(f"{'='*60}")
    
    print(f"\n📊 ANALYSIS RESULTS:")
    print(f"├─ Gym Type: {gym.get('gym_type', 'Unknown')}")
    print(f"├─ Size Estimate: {gym.get('gym_size_estimate', 'Unknown')}")
    print(f"├─ Classification: {gym.get('gym_classification', 'Unknown').upper()}")
    print(f"└─ Confidence: {gym.get('gym_classification_confidence', 'Unknown')}")
    
    print(f"\n💰 REVENUE & QUALIFICATION:")
    print(f"├─ Est. Monthly Revenue: ${gym.get('gym_estimated_monthly_revenue', 0):,}")
    print(f"├─ Est. Member Count: ~{gym.get('gym_estimated_member_count', 0)}")
    print(f"├─ Viability Score: {gym.get('gym_viability_score', 0)}/100")
    print(f"└─ Qualification: {gym.get('gym_size_qualification', 'Unknown')}")
    
    print(f"\n👥 DECISION MAKERS:")
    print(f"├─ Structure: {gym.get('gym_decision_structure', 'Unknown')}")
    print(f"├─ Contact Quality: {gym.get('gym_contact_quality', 'Unknown')}")
    print(f"└─ Accessibility: {gym.get('gym_decision_accessibility', 'Unknown')}")
    
    print(f"\n💵 SOFTWARE BUDGET:")
    print(f"├─ Est. Monthly Budget: ${gym.get('gym_software_budget_total', 0):,}")
    print(f"├─ Pricing Tier: {gym.get('gym_pricing_tier', 'Unknown')}")
    print(f"└─ Budget Confidence: {gym.get('gym_budget_confidence', 'Unknown')}")
    
    print(f"\n🎯 PAIN POINTS:")
    print(f"├─ Pain Score: {gym.get('gym_pain_score', 0)}/100")
    print(f"├─ Urgency: {gym.get('gym_pain_urgency', 'Unknown')}")
    print(f"└─ Primary Issue: {gym.get('gym_primary_pain_category', 'Unknown').replace('_', ' ').title()}")
    
    print(f"\n💻 DIGITAL INFRASTRUCTURE:")
    print(f"├─ Score: {gym.get('gym_digital_infrastructure_score', 0)}/100")
    print(f"├─ Tier: {gym.get('gym_digital_infrastructure_tier', 'Unknown')}")
    print(f"└─ Software: {', '.join(gym.get('gym_software_detected', [])) or 'None detected'}")
    
    print(f"\n📝 SUMMARY:")
    print(f"└─ {gym.get('analysis_summary', 'No summary available')}")

def main():
    """Run the demonstration"""
    print("\n" + "="*80)
    print("GYM SOFTWARE LEAD ANALYSIS DEMO - BAKERSFIELD, CA")
    print("="*80 + "\n")
    
    gyms = get_demo_results()
    print(f"Analyzing {len(gyms)} gyms in Bakersfield, CA...")
    
    # Show individual analyses
    for gym in gyms:
        display_gym_analysis(gym)
    
    # Summary report
    print(f"\n\n{'='*80}")
    print("SUMMARY REPORT - BAKERSFIELD GYM MARKET")
    print(f"{'='*80}\n")
    
    # Classification summary
    red_gyms = [g for g in gyms if g.get('gym_classification') == 'red']
    yellow_gyms = [g for g in gyms if g.get('gym_classification') == 'yellow']
    green_gyms = [g for g in gyms if g.get('gym_classification') == 'green']
    
    print(f"📊 LEAD CLASSIFICATION:")
    print(f"├─ 🔴 RED (Hot Leads): {len(red_gyms)}")
    print(f"├─ 🟡 YELLOW (Warm Leads): {len(yellow_gyms)}")
    print(f"└─ 🟢 GREEN (Not Ready): {len(green_gyms)}")
    
    # Qualification summary
    highly_qualified = [g for g in gyms if g.get('gym_size_qualification') == 'highly_qualified']
    qualified = [g for g in gyms if g.get('gym_size_qualification') == 'qualified']
    
    print(f"\n💰 REVENUE QUALIFICATION:")
    print(f"├─ Highly Qualified: {len(highly_qualified)}")
    print(f"├─ Qualified: {len(qualified)}")
    print(f"└─ Total Qualified: {len(highly_qualified) + len(qualified)}/{len(gyms)}")
    
    # Market insights
    total_revenue = sum(g.get('gym_estimated_monthly_revenue', 0) for g in gyms)
    total_members = sum(g.get('gym_estimated_member_count', 0) for g in gyms)
    total_software_budget = sum(g.get('gym_software_budget_total', 0) for g in gyms)
    
    print(f"\n📈 MARKET INSIGHTS:")
    print(f"├─ Total Monthly Revenue: ${total_revenue:,}")
    print(f"├─ Total Members: {total_members:,}")
    print(f"├─ Total Software Budget: ${total_software_budget:,}/month")
    print(f"└─ Annual Software Market: ${total_software_budget * 12:,}")
    
    # Top opportunities
    print(f"\n🎯 TOP OPPORTUNITIES (RED LEADS):")
    red_sorted = sorted(red_gyms, key=lambda x: x.get('gym_viability_score', 0), reverse=True)
    for i, gym in enumerate(red_sorted[:3], 1):
        print(f"\n{i}. {gym['business_name']}")
        print(f"   ├─ Viability Score: {gym.get('gym_viability_score', 0)}/100")
        print(f"   ├─ Software Budget: ${gym.get('gym_software_budget_total', 0):,}/month")
        print(f"   ├─ Decision Access: {gym.get('gym_decision_accessibility', 'Unknown')}")
        print(f"   └─ Pain: {gym.get('gym_primary_pain_category', 'Unknown').replace('_', ' ').title()}")
    
    # Sales recommendations
    print(f"\n💼 SALES APPROACH RECOMMENDATIONS:")
    print(f"\n1. HIGH PRIORITY - Planet Fitness Bakersfield")
    print(f"   • Large franchise with poor digital infrastructure (42/100)")
    print(f"   • 3,100 members suffering from competitive disadvantages")
    print(f"   • $3,100/month budget potential")
    print(f"   • Approach: Enterprise sales, focus on standardization")
    
    print(f"\n2. QUICK WIN - CrossFit Bakersfield")
    print(f"   • Owner-operated with high accessibility")
    print(f"   • Strong pain in operational inefficiencies")
    print(f"   • $1,820/month budget, owner makes decisions")
    print(f"   • Approach: Relationship building, 1-3 month cycle")
    
    print(f"\n3. NURTURE - Elite Personal Training")
    print(f"   • Critical need but limited budget ($270/month)")
    print(f"   • No website = severe growth limitations")
    print(f"   • High owner accessibility for quick decisions")
    print(f"   • Approach: Start with basic package, consultative")

if __name__ == "__main__":
    main()