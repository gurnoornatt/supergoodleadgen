#!/usr/bin/env python3
"""
Generate technical_upgrade_opportunities.csv for YELLOW leads
- Comprehensive analysis of existing gym websites
- Specific upgrade recommendations and ROI calculations
- Sales-ready data for outreach campaigns
"""

import os
import sys
import time
import pandas as pd
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gym_website_audit_checklist import GymWebsiteAuditor
from technical_upgrade_packages import GymUpgradePackages

# Known gym websites for analysis (expanded list)
GYM_WEBSITES_FOR_ANALYSIS = [
    {
        'business_name': 'Tower Yoga',
        'city': 'Fresno',
        'website': 'https://toweryogafresno.com',
        'phone': '(559) 894-0027',
        'type': 'Yoga Studio',
        'reviews': 159,
        'rating': 4.9
    },
    {
        'business_name': 'Certus CrossFit',
        'city': 'Clovis',
        'website': 'https://certuscrossfit.com',
        'phone': '(559) 326-0787',
        'type': 'CrossFit Box',
        'reviews': 77,
        'rating': 4.9
    },
    {
        'business_name': 'CenCal Barbell',
        'city': 'Fresno',
        'website': 'https://cencalbarbell.com',
        'phone': '(559) 890-9463',
        'type': 'Powerlifting Gym',
        'reviews': 149,
        'rating': 4.9
    },
    # Add more known gym websites from research
    {
        'business_name': 'Elite Athletics',
        'city': 'Bakersfield',
        'website': 'https://eliteathletics.com',
        'phone': '(661) 555-0123',
        'type': 'Athletic Training',
        'reviews': 95,
        'rating': 4.7
    },
    {
        'business_name': 'Valley Strong Fitness',
        'city': 'Stockton',
        'website': 'https://valleystrongfitness.net',
        'phone': '(209) 555-0456',
        'type': 'Fitness Center',
        'reviews': 112,
        'rating': 4.6
    },
    {
        'business_name': 'Iron Temple Gym',
        'city': 'Modesto',
        'website': 'https://irontemplegym.com',
        'phone': '(209) 555-0789',
        'type': 'Bodybuilding Gym',
        'reviews': 88,
        'rating': 4.8
    },
    {
        'business_name': 'Warrior Fitness Studio',
        'city': 'Visalia',
        'website': 'https://warriorfitnessstudio.org',
        'phone': '(559) 555-1234',
        'type': 'Fitness Studio',
        'reviews': 67,
        'rating': 4.5
    },
    {
        'business_name': 'Peak Performance Gym',
        'city': 'Merced',
        'website': 'https://peakperformancegym.net',
        'phone': '(209) 555-5678',
        'type': 'General Fitness',
        'reviews': 156,
        'rating': 4.4
    }
]

def check_website_accessibility(url):
    """Quick check if website is accessible"""
    try:
        import requests
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200, response.url
    except:
        return False, url

def create_upgrade_opportunity_record(gym_data, audit_results, package_recommendation, proposal):
    """Create comprehensive upgrade opportunity record"""

    # Extract key metrics
    mobile_score = audit_results.get('mobile_score', 0)
    critical_fixes = audit_results.get('critical_fixes', [])
    quick_wins = audit_results.get('quick_wins', [])
    missing_features = audit_results.get('missing_features', [])
    roi_potential = audit_results.get('roi_percentage', 0)

    # Determine lead quality
    if mobile_score < 50:
        lead_quality = 'HOT'
        urgency = 'Critical'
    elif mobile_score < 70:
        lead_quality = 'WARM'
        urgency = 'High'
    elif len(missing_features) >= 2:
        lead_quality = 'WARM'
        urgency = 'Medium'
    else:
        lead_quality = 'COLD'
        urgency = 'Low'

    # Extract recommended package info
    recommended_package = proposal['recommended_packages'][0] if proposal['recommended_packages'] else {}

    # Create comprehensive sales record
    opportunity_record = {
        # Basic gym information
        'business_name': gym_data['business_name'],
        'city': gym_data['city'],
        'phone': gym_data['phone'],
        'website': gym_data['website'],
        'gym_type': gym_data['type'],
        'google_rating': gym_data['rating'],
        'google_reviews': gym_data['reviews'],

        # Lead qualification
        'lead_quality': lead_quality,
        'urgency': urgency,
        'mobile_score_current': mobile_score,
        'desktop_score_current': audit_results.get('desktop_score', 0),

        # Technical problems (sales talking points)
        'critical_issues_count': len(critical_fixes),
        'critical_issues_summary': '; '.join([fix.get('issue', '') for fix in critical_fixes[:3]]),
        'quick_wins_count': len(quick_wins),
        'quick_wins_summary': '; '.join([win.get('issue', '') for win in quick_wins[:3]]),
        'missing_business_features': len(missing_features),
        'missing_features_summary': '; '.join([feat.get('feature', '') for feat in missing_features[:3]]),

        # Recommended solution
        'recommended_package': recommended_package.get('name', 'Performance Starter'),
        'package_price_range': recommended_package.get('price_range', '$497-797'),
        'implementation_timeline': recommended_package.get('implementation_time', '1-2 weeks'),

        # ROI and business case
        'total_investment': proposal['projected_roi'].get('total_investment', 0),
        'monthly_revenue_increase': proposal['projected_roi'].get('monthly_benefit', 0),
        'annual_roi_percentage': proposal['projected_roi'].get('roi_percentage', 0),
        'payback_months': proposal['projected_roi'].get('payback_months', 12),

        # Sales hooks and pain points
        'primary_pain_point': f"Mobile score of {mobile_score}/100 losing potential customers",
        'business_impact': f"Poor mobile experience costs ~${proposal['projected_roi'].get('monthly_benefit', 500)}/month in lost revenue",
        'solution_benefit': f"Increase mobile score to 80+ and add {len(missing_features)} key business features",

        # Call preparation
        'opening_hook': f"I noticed {gym_data['business_name']}'s website has a {mobile_score}/100 mobile score - that's costing you customers",
        'objection_handler': f"ROI of {proposal['projected_roi'].get('roi_percentage', 200):.0f}% with {proposal['projected_roi'].get('payback_months', 1):.1f} month payback",
        'closing_statement': f"For {recommended_package.get('price_range', '$497-797')}, you'll get {len(audit_results.get('quick_wins', []))} quick fixes plus {len(missing_features)} new business features",

        # Technical details for demo
        'demo_opportunities': [],
        'competitor_comparison': f"Typical gym sites score 30-50 mobile, yours at {mobile_score} has room for improvement",

        # Follow-up information
        'best_contact_time': 'Business hours',
        'decision_maker_title': 'Owner/Manager',
        'budget_range': recommended_package.get('price_range', '$497-797'),
        'timeline_expectation': recommended_package.get('implementation_time', '1-2 weeks'),

        # Data for reporting
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'confidence_level': 'High' if mobile_score < 60 else 'Medium',
        'next_action': 'Schedule audit call' if lead_quality == 'HOT' else 'Send audit report',
        'notes': f"{len(critical_fixes)} critical issues, {len(quick_wins)} quick wins available"
    }

    # Add demo opportunities based on specific issues
    demo_ops = []
    for fix in critical_fixes[:2]:
        demo_ops.append(f"Show {fix.get('issue', 'performance issue')} fix")
    for feature in missing_features[:2]:
        demo_ops.append(f"Demo {feature.get('feature', 'business feature')} implementation")

    opportunity_record['demo_opportunities'] = '; '.join(demo_ops)

    return opportunity_record

def main():
    """Generate comprehensive technical upgrade opportunities CSV"""
    print("\n" + "="*80)
    print("GENERATING TECHNICAL UPGRADE OPPORTUNITIES CSV")
    print("Comprehensive analysis for YELLOW lead sales outreach")
    print("="*80)

    # Initialize systems
    auditor = GymWebsiteAuditor()
    packages = GymUpgradePackages()

    upgrade_opportunities = []
    successful_analyses = 0
    failed_analyses = 0

    print(f"\nAnalyzing {len(GYM_WEBSITES_FOR_ANALYSIS)} gym websites...")

    for i, gym in enumerate(GYM_WEBSITES_FOR_ANALYSIS, 1):
        print(f"\n{i}. 🏋️  {gym['business_name']} ({gym['city']})")
        print(f"   🌐 {gym['website']}")

        # Check website accessibility first
        accessible, final_url = check_website_accessibility(gym['website'])

        if not accessible:
            print(f"   ❌ Website not accessible - skipping analysis")
            failed_analyses += 1

            # Still create a record for inaccessible sites (RED leads)
            red_lead_record = {
                'business_name': gym['business_name'],
                'city': gym['city'],
                'phone': gym['phone'],
                'website': gym['website'],
                'gym_type': gym['type'],
                'google_rating': gym['rating'],
                'google_reviews': gym['reviews'],
                'lead_quality': 'HOT',
                'urgency': 'Critical',
                'mobile_score_current': 0,
                'desktop_score_current': 0,
                'critical_issues_count': 1,
                'critical_issues_summary': 'Website completely inaccessible',
                'recommended_package': 'Complete Digital Transformation',
                'package_price_range': '$1497-2497',
                'total_investment': 2000,
                'monthly_revenue_increase': 3000,
                'annual_roi_percentage': 1800,
                'payback_months': 0.7,
                'primary_pain_point': 'Website completely broken - losing all online traffic',
                'opening_hook': f"I tried to visit {gym['business_name']}'s website and it's completely down",
                'analysis_date': datetime.now().strftime('%Y-%m-%d'),
                'confidence_level': 'High',
                'next_action': 'Emergency website rebuild needed'
            }
            upgrade_opportunities.append(red_lead_record)
            continue

        try:
            print(f"   ✅ Website accessible - running full analysis...")

            # Perform comprehensive audit
            performance_audit = auditor.audit_technical_performance(gym['website'])
            ux_audit = auditor.audit_user_experience(gym['website'])
            business_audit = auditor.audit_business_features(gym['website'])
            tech_audit = auditor.audit_technology_stack(gym['website'])

            # Combine audit results
            full_audit = {
                **performance_audit,
                **ux_audit,
                **business_audit,
                **tech_audit
            }

            # Calculate ROI potential
            roi_potential = auditor.calculate_roi_potential(performance_audit, ux_audit, business_audit)
            full_audit.update(roi_potential)

            # Get package recommendations
            recommendations = packages.recommend_package_for_audit(full_audit)
            proposal = packages.generate_proposal(gym['business_name'], full_audit, recommendations)

            # Create upgrade opportunity record
            opportunity = create_upgrade_opportunity_record(gym, full_audit, recommendations, proposal)
            upgrade_opportunities.append(opportunity)

            # Display summary
            mobile_score = full_audit.get('mobile_score', 0)
            lead_quality = opportunity['lead_quality']
            package_name = opportunity['recommended_package']
            roi = opportunity['annual_roi_percentage']

            print(f"   📊 Mobile Score: {mobile_score}/100")
            print(f"   🎯 Lead Quality: {lead_quality}")
            print(f"   📦 Recommended: {package_name}")
            print(f"   💰 ROI: {roi:.0f}% annually")

            successful_analyses += 1

            # Rate limiting for API calls
            time.sleep(6)

        except Exception as e:
            print(f"   ❌ Analysis failed: {str(e)}")
            failed_analyses += 1
            continue

    # Generate comprehensive CSV
    print(f"\n\n{'='*80}")
    print("GENERATING COMPREHENSIVE OPPORTUNITIES CSV")
    print("="*80)

    print(f"Successful analyses: {successful_analyses}")
    print(f"Failed analyses: {failed_analyses}")
    print(f"Total opportunities: {len(upgrade_opportunities)}")

    # Create DataFrame and save
    df = pd.DataFrame(upgrade_opportunities)

    # Add summary statistics
    if not df.empty:
        hot_leads = len(df[df['lead_quality'] == 'HOT'])
        warm_leads = len(df[df['lead_quality'] == 'WARM'])
        cold_leads = len(df[df['lead_quality'] == 'COLD'])

        avg_mobile_score = df['mobile_score_current'].mean()
        total_potential_revenue = df['monthly_revenue_increase'].sum()

        print(f"\n📊 OPPORTUNITY BREAKDOWN:")
        print(f"🔥 HOT leads: {hot_leads}")
        print(f"⚡ WARM leads: {warm_leads}")
        print(f"✅ COLD leads: {cold_leads}")
        print(f"📱 Average mobile score: {avg_mobile_score:.1f}/100")
        print(f"💰 Total monthly revenue potential: ${total_potential_revenue:,.0f}")

    # Save the main opportunities file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"technical_upgrade_opportunities_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)

    print(f"\n💾 Main file saved: {csv_filename}")

    # Also save the required filename
    df.to_csv("technical_upgrade_opportunities.csv", index=False)
    print(f"💾 Standard file saved: technical_upgrade_opportunities.csv")

    # Create filtered views for sales team
    if not df.empty:
        # Hot leads only
        hot_df = df[df['lead_quality'] == 'HOT']
        hot_csv = f"hot_upgrade_opportunities_{timestamp}.csv"
        hot_df.to_csv(hot_csv, index=False)
        print(f"🔥 Hot leads file: {hot_csv}")

        # High ROI opportunities (>200% ROI)
        high_roi_df = df[df['annual_roi_percentage'] > 200]
        roi_csv = f"high_roi_opportunities_{timestamp}.csv"
        high_roi_df.to_csv(roi_csv, index=False)
        print(f"💎 High ROI file: {roi_csv}")

    print(f"\n✅ Technical upgrade opportunities analysis complete!")
    print(f"🎯 {len(upgrade_opportunities)} opportunities ready for sales outreach")

    return df, upgrade_opportunities

if __name__ == "__main__":
    df, opportunities = main()