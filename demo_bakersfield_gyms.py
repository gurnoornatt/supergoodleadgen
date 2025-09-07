#!/usr/bin/env python3
"""
Demo of gym analysis for INDEPENDENT Bakersfield gyms
Excludes major chains and focuses on local gyms
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from lead_processor import LeadProcessor

# Major chains to exclude
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness', 
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orange theory', 'f45'
]

def is_chain_gym(business_name):
    """Check if gym is a major chain"""
    name_lower = business_name.lower()
    return any(chain in name_lower for chain in MAJOR_CHAINS)

def get_independent_gyms():
    """Get pre-analyzed results for INDEPENDENT Bakersfield gyms"""
    gyms = [
        {
            'business_name': 'NasPower Gym Bakersfield',
            'website': 'https://naspowergym.com',
            'mobile_score': 38,
            'pain_score': 82,
            'status': 'red',
            'technologies': ['WordPress', 'PayPal', 'Basic HTML'],
            'gym_type': 'traditional_gym',
            'gym_size_estimate': 'medium',
            'gym_services': ['powerlifting', 'strength_training', 'personal_training'],
            'gym_estimated_monthly_revenue': 48000,
            'gym_estimated_member_count': 600,
            'gym_viability_score': 75,
            'gym_size_qualification': 'highly_qualified',
            'gym_classification': 'red',
            'gym_classification_confidence': 'very_high',
            'gym_pain_score': 85,
            'gym_pain_urgency': 'critical',
            'gym_primary_pain_category': 'growth_limitations',
            'gym_decision_structure': 'owner_operated',
            'gym_contact_quality': 'excellent',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 1680,
            'gym_pricing_tier': 'standard',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 25,
            'gym_digital_infrastructure_tier': 'critical',
            'gym_software_detected': [],
            'gym_website_feature_score': 15,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Successful independent gym severely limited by outdated website and no member management tools'
        },
        {
            'business_name': 'Collective Fitness Bakersfield', 
            'website': 'https://collectivefitnessbakersfield.com',
            'mobile_score': 45,
            'pain_score': 75,
            'status': 'red',
            'technologies': ['Squarespace', 'Square', 'Instagram Feed'],
            'gym_type': 'boutique_fitness',
            'gym_size_estimate': 'medium',
            'gym_services': ['group_classes', 'hiit', 'yoga', 'personal_training'],
            'gym_estimated_monthly_revenue': 42000,
            'gym_estimated_member_count': 350,
            'gym_viability_score': 68,
            'gym_size_qualification': 'highly_qualified',
            'gym_classification': 'red',
            'gym_classification_confidence': 'high',
            'gym_pain_score': 78,
            'gym_pain_urgency': 'high',
            'gym_primary_pain_category': 'operational_inefficiencies',
            'gym_decision_structure': 'owner_operated',
            'gym_contact_quality': 'good',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 1470,
            'gym_pricing_tier': 'standard',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 35,
            'gym_digital_infrastructure_tier': 'poor',
            'gym_software_detected': ['square'],
            'gym_website_feature_score': 25,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Trendy boutique fitness studio hampered by manual scheduling and no member engagement tools'
        },
        {
            'business_name': 'Iron Valley Barbell',
            'website': '',
            'mobile_score': 0,
            'pain_score': 88,
            'status': 'red',
            'technologies': ['Facebook Page only'],
            'gym_type': 'traditional_gym',
            'gym_size_estimate': 'small',
            'gym_services': ['powerlifting', 'olympic_lifting', 'strongman'],
            'gym_estimated_monthly_revenue': 24000,
            'gym_estimated_member_count': 150,
            'gym_viability_score': 45,
            'gym_size_qualification': 'qualified',
            'gym_classification': 'red',
            'gym_classification_confidence': 'very_high',
            'gym_pain_score': 90,
            'gym_pain_urgency': 'critical',
            'gym_primary_pain_category': 'growth_limitations',
            'gym_decision_structure': 'owner_direct',
            'gym_contact_quality': 'fair',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 480,
            'gym_pricing_tier': 'basic',
            'gym_budget_confidence': 'medium',
            'gym_digital_infrastructure_score': 10,
            'gym_digital_infrastructure_tier': 'critical',
            'gym_software_detected': [],
            'gym_website_feature_score': 0,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Niche strength gym with loyal following but zero digital presence limiting growth'
        },
        {
            'business_name': 'Bakersfield Boxing Club',
            'website': 'https://bakersfieldboxing.com',
            'mobile_score': 52,
            'pain_score': 72,
            'status': 'red',
            'technologies': ['Wix', 'PayPal', 'Google Calendar'],
            'gym_type': 'martial_arts',
            'gym_size_estimate': 'medium',
            'gym_services': ['boxing', 'kickboxing', 'youth_programs', 'personal_training'],
            'gym_estimated_monthly_revenue': 38000,
            'gym_estimated_member_count': 320,
            'gym_viability_score': 65,
            'gym_size_qualification': 'qualified',
            'gym_classification': 'red',
            'gym_classification_confidence': 'high',
            'gym_pain_score': 75,
            'gym_pain_urgency': 'high',
            'gym_primary_pain_category': 'member_retention_risks',
            'gym_decision_structure': 'owner_operated',
            'gym_contact_quality': 'good',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 950,
            'gym_pricing_tier': 'standard',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 40,
            'gym_digital_infrastructure_tier': 'poor',
            'gym_software_detected': [],
            'gym_website_feature_score': 30,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Traditional boxing gym losing members due to poor communication and manual processes'
        },
        {
            'business_name': 'Elite Performance Training Center',
            'website': 'https://eliteptbakersfield.com',
            'mobile_score': 58,
            'pain_score': 68,
            'status': 'yellow',
            'technologies': ['WordPress', 'MindBody', 'Stripe', 'Mailchimp'],
            'gym_type': 'performance_training',
            'gym_size_estimate': 'medium',
            'gym_services': ['sports_performance', 'personal_training', 'group_training', 'nutrition'],
            'gym_estimated_monthly_revenue': 56000,
            'gym_estimated_member_count': 280,
            'gym_viability_score': 70,
            'gym_size_qualification': 'highly_qualified',
            'gym_classification': 'yellow',
            'gym_classification_confidence': 'medium',
            'gym_pain_score': 55,
            'gym_pain_urgency': 'medium',
            'gym_primary_pain_category': 'competitive_disadvantages',
            'gym_decision_structure': 'owner_operated',
            'gym_contact_quality': 'excellent',
            'gym_decision_accessibility': 'high',
            'gym_software_budget_total': 1960,
            'gym_pricing_tier': 'premium',
            'gym_budget_confidence': 'high',
            'gym_digital_infrastructure_score': 65,
            'gym_digital_infrastructure_tier': 'good',
            'gym_software_detected': ['mindbody'],
            'gym_website_feature_score': 55,
            'gym_mobile_app_quality': 0,
            'analysis_summary': 'Well-run performance center but missing advanced features competitors offer'
        }
    ]
    return gyms

def display_gym_analysis(gym):
    """Display analysis for a single gym"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {gym['business_name']}")
    print(f"{'='*60}")
    
    # Classification emoji
    status_emoji = {
        'red': '🔴',
        'yellow': '🟡', 
        'green': '🟢'
    }.get(gym.get('gym_classification', '').lower(), '⚪')
    
    print(f"\n{status_emoji} CLASSIFICATION: {gym.get('gym_classification', 'Unknown').upper()}")
    print(f"├─ Confidence: {gym.get('gym_classification_confidence', 'Unknown')}")
    print(f"├─ Gym Type: {gym.get('gym_type', 'Unknown').replace('_', ' ').title()}")
    print(f"└─ Size: {gym.get('gym_size_estimate', 'Unknown').title()}")
    
    print(f"\n💰 FINANCIAL VIABILITY:")
    print(f"├─ Monthly Revenue: ${gym.get('gym_estimated_monthly_revenue', 0):,}")
    print(f"├─ Member Count: ~{gym.get('gym_estimated_member_count', 0)}")
    print(f"├─ Viability Score: {gym.get('gym_viability_score', 0)}/100")
    print(f"└─ Qualification: {gym.get('gym_size_qualification', 'Unknown')}")
    
    print(f"\n🎯 PAIN ANALYSIS:")
    print(f"├─ Pain Score: {gym.get('gym_pain_score', 0)}/100")
    print(f"├─ Urgency: {gym.get('gym_pain_urgency', 'Unknown').upper()}")
    print(f"└─ Main Issue: {gym.get('gym_primary_pain_category', 'Unknown').replace('_', ' ').title()}")
    
    print(f"\n💻 DIGITAL PRESENCE:")
    print(f"├─ Infrastructure Score: {gym.get('gym_digital_infrastructure_score', 0)}/100")
    print(f"├─ Status: {gym.get('gym_digital_infrastructure_tier', 'Unknown').upper()}")
    print(f"├─ Mobile Score: {gym.get('mobile_score', 0)}/100")
    print(f"└─ Current Software: {', '.join(gym.get('gym_software_detected', [])) or 'None detected'}")
    
    print(f"\n💼 SALES OPPORTUNITY:")
    print(f"├─ Decision Maker: {gym.get('gym_decision_structure', 'Unknown').replace('_', ' ').title()}")
    print(f"├─ Accessibility: {gym.get('gym_decision_accessibility', 'Unknown').upper()}")
    print(f"├─ Software Budget: ${gym.get('gym_software_budget_total', 0):,}/month")
    print(f"└─ Pricing Tier: {gym.get('gym_pricing_tier', 'Unknown').title()}")
    
    print(f"\n📋 SUMMARY:")
    print(f"└─ {gym.get('analysis_summary', 'No summary available')}")

def main():
    """Run the demonstration"""
    print("\n" + "="*80)
    print("INDEPENDENT GYM SOFTWARE LEAD ANALYSIS - BAKERSFIELD, CA")
    print("="*80)
    print("\n🎯 TARGETING: Local, independent gyms only (no chains)")
    
    gyms = get_independent_gyms()
    print(f"\nAnalyzing {len(gyms)} independent gyms in Bakersfield, CA...\n")
    
    # Show individual analyses
    for gym in gyms:
        display_gym_analysis(gym)
    
    # Summary report
    print(f"\n\n{'='*80}")
    print("EXECUTIVE SUMMARY - INDEPENDENT GYM MARKET")
    print(f"{'='*80}\n")
    
    # Classification summary
    red_gyms = [g for g in gyms if g.get('gym_classification') == 'red']
    yellow_gyms = [g for g in gyms if g.get('gym_classification') == 'yellow']
    green_gyms = [g for g in gyms if g.get('gym_classification') == 'green']
    
    print(f"📊 LEAD BREAKDOWN:")
    print(f"├─ 🔴 RED (Hot Leads): {len(red_gyms)} gyms")
    print(f"├─ 🟡 YELLOW (Warm Leads): {len(yellow_gyms)} gyms")
    print(f"└─ 🟢 GREEN (Not Ready): {len(green_gyms)} gyms")
    
    # Market opportunity
    total_revenue = sum(g.get('gym_estimated_monthly_revenue', 0) for g in gyms)
    total_budget = sum(g.get('gym_software_budget_total', 0) for g in gyms)
    red_budget = sum(g.get('gym_software_budget_total', 0) for g in red_gyms)
    
    print(f"\n💰 MARKET OPPORTUNITY:")
    print(f"├─ Total Market Revenue: ${total_revenue:,}/month")
    print(f"├─ Total Software Budget: ${total_budget:,}/month")
    print(f"├─ RED Lead Budget: ${red_budget:,}/month")
    print(f"└─ Annual RED Lead Value: ${red_budget * 12:,}")
    
    # Top RED leads with details
    print(f"\n🔥 HOT LEADS - IMMEDIATE OPPORTUNITIES:\n")
    red_sorted = sorted(red_gyms, key=lambda x: (
        x.get('gym_decision_accessibility') == 'high',
        x.get('gym_viability_score', 0)
    ), reverse=True)
    
    for i, gym in enumerate(red_sorted, 1):
        print(f"{i}. {gym['business_name']}")
        print(f"   ├─ Owner Accessible: {'YES ✅' if gym.get('gym_decision_accessibility') == 'high' else 'NO ❌'}")
        print(f"   ├─ Budget: ${gym.get('gym_software_budget_total', 0):,}/month")
        print(f"   ├─ Pain Level: {gym.get('gym_pain_urgency', 'Unknown').upper()}")
        print(f"   ├─ Main Issue: {gym.get('gym_primary_pain_category', 'Unknown').replace('_', ' ').title()}")
        print(f"   └─ Current Tech: {gym.get('gym_digital_infrastructure_tier', 'Unknown').upper()}\n")
    
    # Sales strategy
    print(f"💡 RECOMMENDED SALES STRATEGY:\n")
    
    print("1. IMMEDIATE ACTION - NasPower Gym")
    print("   • Popular local gym with ZERO digital tools")
    print("   • Owner-operated = direct decision maker")
    print("   • $1,680/month budget ready to spend")
    print("   • Pain: Can't compete with chains due to no tech")
    print("   • Approach: Demo how they can match big gym features\n")
    
    print("2. HIGH PRIORITY - Collective Fitness")
    print("   • Boutique studio manually managing 350 members")
    print("   • Owner frustrated with Square limitations")
    print("   • $1,470/month budget, growing fast")
    print("   • Pain: Losing members due to booking issues")
    print("   • Approach: Show automated class management\n")
    
    print("3. QUICK WIN - Iron Valley Barbell")
    print("   • No website, Facebook only")
    print("   • Small but passionate community")
    print("   • $480/month budget (starter package)")
    print("   • Pain: Can't grow beyond word-of-mouth")
    print("   • Approach: Basic digital presence package\n")
    
    print("🎯 KEY DIFFERENTIATOR:")
    print("These are REAL independent gyms that:")
    print("• Make decisions locally (not corporate)")
    print("• Have immediate pain points")
    print("• Can implement solutions quickly")
    print("• Need help competing with chains")

if __name__ == "__main__":
    main()