#!/usr/bin/env python3
"""
Create specialized solution packages for each fitness business type
with custom features and pricing per vertical
"""

import pandas as pd
from datetime import datetime
import json

def create_specialized_solutions():
    """Create specialized solution packages for each business type"""

    # Read the existing specialized fitness data
    df = pd.read_csv('specialized_fitness_with_pain_points_20250916_215722.csv')

    # Define specialized solution packages
    solution_packages = {
        'Dance Studios': {
            'package_name': 'DanceStudio Pro',
            'core_features': [
                'Online class registration and scheduling',
                'Recital management system with costume ordering',
                'Parent portal with progress tracking',
                'Performance video sharing platform',
                'Competition registration and team management',
                'Student skill assessment and advancement tracking',
                'Payment processing and billing automation',
                'Teacher scheduling and substitute management',
                'Studio calendar and event coordination',
                'Email/SMS notifications for parents'
            ],
            'premium_features': [
                'Advanced choreography planning tools',
                'Competition scoring and judging system',
                'Social media integration for showcases',
                'Multi-location management',
                'Advanced reporting and analytics',
                'Custom mobile app branding'
            ],
            'pricing': {
                'starter': '$197/month',
                'professional': '$397/month',
                'enterprise': '$697/month'
            },
            'setup_fee': '$299',
            'contract_length': '12 months',
            'target_pain_points': [
                'Manual class scheduling causing double-bookings',
                'Parent communication chaos before recitals',
                'Lost revenue from missed payments',
                'Competition registration nightmares',
                'No digital presence losing students to competitors'
            ]
        },

        'Tennis Clubs': {
            'package_name': 'TennisClub Manager',
            'core_features': [
                'Court booking and reservation system',
                'Tournament bracket management',
                'Ladder ranking and league organization',
                'Pro shop inventory management',
                'Lesson scheduling with instructor matching',
                'Member management and access control',
                'Equipment rental and maintenance tracking',
                'Rain delay and court condition updates',
                'Automated billing and membership renewals',
                'Player statistics and match history'
            ],
            'premium_features': [
                'Advanced tournament seeding algorithms',
                'Integration with tennis rating systems',
                'Weather monitoring and automatic notifications',
                'Pro shop e-commerce platform',
                'Advanced player analytics',
                'Custom club mobile app'
            ],
            'pricing': {
                'starter': '$297/month',
                'professional': '$597/month',
                'enterprise': '$997/month'
            },
            'setup_fee': '$499',
            'contract_length': '12 months',
            'target_pain_points': [
                'Phone-based court booking causing conflicts',
                'Manual tournament management chaos',
                'Lost revenue from unused court time',
                'Member retention issues',
                'Outdated systems driving members away'
            ]
        },

        'Swimming/Aquatic Centers': {
            'package_name': 'AquaCenter Pro',
            'core_features': [
                'Swim lesson skill progression tracking',
                'Pool scheduling for multiple activities',
                'Safety certification and instructor management',
                'Water quality monitoring and reporting',
                'Equipment rental and maintenance logs',
                'Student progress reports for parents',
                'Lifeguard scheduling and certification tracking',
                'Pool party and event booking',
                'Automated billing and payment processing',
                'Emergency contact and medical information'
            ],
            'premium_features': [
                'Advanced swim analytics and technique tracking',
                'Integration with swim timing systems',
                'Competitive team management',
                'Advanced safety compliance reporting',
                'Custom parent mobile app',
                'Multi-facility management'
            ],
            'pricing': {
                'starter': '$347/month',
                'professional': '$647/month',
                'enterprise': '$1147/month'
            },
            'setup_fee': '$399',
            'contract_length': '12 months',
            'target_pain_points': [
                'Manual lesson scheduling conflicts',
                'Lost track of student skill progression',
                'Safety compliance documentation chaos',
                'Parent communication inefficiencies',
                'Revenue leakage from poor scheduling'
            ]
        },

        'Boxing/Martial Arts': {
            'package_name': 'MartialsArts Master',
            'core_features': [
                'Belt rank progression and testing schedules',
                'Student skill assessment and tracking',
                'Tournament registration and bracket management',
                'Equipment inventory and rental system',
                'Class scheduling and instructor assignment',
                'Safety waiver and insurance management',
                'Sparring partner matching system',
                'Training session intensity tracking',
                'Automated billing and membership management',
                'Parent communication portal'
            ],
            'premium_features': [
                'Advanced technique video analysis',
                'Competition performance analytics',
                'Multi-discipline curriculum management',
                'Advanced safety incident reporting',
                'Custom dojo mobile app',
                'Franchise management tools'
            ],
            'pricing': {
                'starter': '$247/month',
                'professional': '$497/month',
                'enterprise': '$797/month'
            },
            'setup_fee': '$349',
            'contract_length': '12 months',
            'target_pain_points': [
                'Manual belt testing and rank tracking',
                'Tournament organization nightmares',
                'Equipment management chaos',
                'Student retention issues',
                'Safety compliance documentation'
            ]
        },

        'Wellness/Medical Spa': {
            'package_name': 'WellnessPro Suite',
            'core_features': [
                'HIPAA-compliant appointment scheduling',
                'Patient health history and progress tracking',
                'Treatment protocol and compliance monitoring',
                'Insurance billing and claim processing',
                'Staff certification and continuing education tracking',
                'Equipment maintenance and safety protocols',
                'Client communication and follow-up automation',
                'Inventory management for treatments and products',
                'Financial reporting and analytics',
                'Secure patient portal access'
            ],
            'premium_features': [
                'Advanced treatment outcome analytics',
                'Telehealth integration',
                'Advanced billing and insurance optimization',
                'Multi-location practice management',
                'Custom patient mobile app',
                'AI-powered treatment recommendations'
            ],
            'pricing': {
                'starter': '$597/month',
                'professional': '$997/month',
                'enterprise': '$1697/month'
            },
            'setup_fee': '$799',
            'contract_length': '12 months',
            'target_pain_points': [
                'Manual scheduling causing appointment conflicts',
                'HIPAA compliance documentation nightmares',
                'Insurance claim processing delays',
                'Patient progress tracking inefficiencies',
                'Revenue leakage from billing errors'
            ]
        },

        'Recreation Centers': {
            'package_name': 'RecCenter Commander',
            'core_features': [
                'Multi-facility scheduling and booking system',
                'Program registration for diverse activities',
                'Membership management for community programs',
                'Event planning and facility rental coordination',
                'Equipment checkout and maintenance tracking',
                'Community outreach and program promotion',
                'Staff scheduling and certification management',
                'Financial reporting and budget tracking',
                'Safety incident reporting and management',
                'Automated communication system'
            ],
            'premium_features': [
                'Advanced facility utilization analytics',
                'Community engagement insights',
                'Grant management and reporting',
                'Advanced security and access control',
                'Custom community mobile app',
                'Multi-department coordination tools'
            ],
            'pricing': {
                'starter': '$447/month',
                'professional': '$797/month',
                'enterprise': '$1297/month'
            },
            'setup_fee': '$599',
            'contract_length': '12 months',
            'target_pain_points': [
                'Facility booking conflicts and double-bookings',
                'Program registration chaos',
                'Equipment management inefficiencies',
                'Community engagement challenges',
                'Budget tracking and financial oversight'
            ]
        }
    }

    # Create solution records for each business
    solution_records = []

    for index, row in df.iterrows():
        category = row['specialized_category']
        if category in solution_packages:
            package = solution_packages[category]

            # Determine recommended tier based on business size and reviews
            reviews = row['reviews']
            if reviews > 500:
                recommended_tier = 'enterprise'
                monthly_price = package['pricing']['enterprise']
                estimated_annual_value = int(package['pricing']['enterprise'].replace('$', '').replace('/month', '')) * 12
            elif reviews > 100:
                recommended_tier = 'professional'
                monthly_price = package['pricing']['professional']
                estimated_annual_value = int(package['pricing']['professional'].replace('$', '').replace('/month', '')) * 12
            else:
                recommended_tier = 'starter'
                monthly_price = package['pricing']['starter']
                estimated_annual_value = int(package['pricing']['starter'].replace('$', '').replace('/month', '')) * 12

            # Add setup fee to first year
            setup_fee = int(package['setup_fee'].replace('$', ''))
            total_first_year_value = estimated_annual_value + setup_fee

            solution_record = {
                'business_name': row['business_name'],
                'city': row['city'],
                'phone': row['phone'],
                'specialized_category': category,
                'lead_score': row['lead_score'],
                'current_reviews': reviews,
                'current_rating': row['rating'],
                'solution_package': package['package_name'],
                'recommended_tier': recommended_tier.title(),
                'monthly_price': monthly_price,
                'setup_fee': package['setup_fee'],
                'estimated_annual_value': f"${estimated_annual_value:,}",
                'total_first_year_value': f"${total_first_year_value:,}",
                'contract_length': package['contract_length'],
                'core_features': '; '.join(package['core_features'][:5]),  # Top 5 features
                'premium_features': '; '.join(package['premium_features'][:3]),  # Top 3 premium
                'key_pain_points_addressed': '; '.join(package['target_pain_points'][:3]),
                'competitive_advantage': f"Specialized {category.lower()} solution vs generic gym software",
                'implementation_timeline': '2-4 weeks',
                'roi_timeline': '3-6 months',
                'success_metrics': 'Increased bookings, reduced admin time, improved customer satisfaction',
                'next_action': 'Schedule demo call to show specialized features',
                'demo_script_focus': f"Show {category.lower()}-specific features that generic software lacks",
                'objection_handling': 'Address cost concerns with ROI calculator and payment plans',
                'closing_approach': 'Limited-time setup fee discount for early adopters',
                'created_at': datetime.now().isoformat()
            }

            solution_records.append(solution_record)

    # Create DataFrame and sort by business value
    solutions_df = pd.DataFrame(solution_records)

    # Sort by lead score (RED first) and then by annual value
    score_priority = {'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    solutions_df['score_priority'] = solutions_df['lead_score'].map(score_priority)
    solutions_df['annual_value_numeric'] = solutions_df['estimated_annual_value'].str.replace('$', '').str.replace(',', '').astype(int)
    solutions_df = solutions_df.sort_values(['score_priority', 'annual_value_numeric'], ascending=[False, False])
    solutions_df = solutions_df.drop(['score_priority', 'annual_value_numeric'], axis=1)

    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'specialized_fitness_solutions_{timestamp}.csv'
    solutions_df.to_csv(csv_filename, index=False)

    # Create summary report
    print("\n" + "="*80)
    print("SPECIALIZED FITNESS SOLUTION PACKAGES")
    print("="*80)
    print(f"Total solution packages created: {len(solutions_df)}")

    # Revenue potential by category
    print(f"\n💰 REVENUE POTENTIAL BY CATEGORY:")
    category_revenue = solutions_df.groupby('specialized_category').agg({
        'total_first_year_value': lambda x: x.str.replace('$', '').str.replace(',', '').astype(int).sum(),
        'business_name': 'count'
    }).reset_index()

    for index, row in category_revenue.iterrows():
        category = row['specialized_category']
        total_revenue = f"${row['total_first_year_value']:,}"
        business_count = row['business_name']
        avg_value = f"${row['total_first_year_value'] // business_count:,}"
        print(f"  {category}: {business_count} businesses = {total_revenue} total ({avg_value} avg)")

    # Lead quality breakdown
    print(f"\n🎯 SOLUTION PACKAGES BY LEAD QUALITY:")
    lead_breakdown = solutions_df['lead_score'].value_counts()
    red_revenue = solutions_df[solutions_df['lead_score'] == 'RED']['total_first_year_value'].str.replace('$', '').str.replace(',', '').astype(int).sum()
    yellow_revenue = solutions_df[solutions_df['lead_score'] == 'YELLOW']['total_first_year_value'].str.replace('$', '').str.replace(',', '').astype(int).sum()

    print(f"  🔥 RED LEADS: {lead_breakdown.get('RED', 0)} packages = ${red_revenue:,} potential")
    print(f"  ⚡ YELLOW LEADS: {lead_breakdown.get('YELLOW', 0)} packages = ${yellow_revenue:,} potential")

    # Top revenue opportunities
    print(f"\n🏆 TOP 10 HIGHEST VALUE OPPORTUNITIES:")
    for i, (idx, lead) in enumerate(solutions_df.head(10).iterrows(), 1):
        print(f"{i}. {lead['business_name']} ({lead['city']}) - {lead['specialized_category']}")
        print(f"   💰 {lead['total_first_year_value']} first year ({lead['recommended_tier']} tier)")
        print(f"   📞 {lead['phone']}")
        print(f"   🎯 Key feature: {lead['core_features'].split(';')[0]}")
        print()

    # Total addressable market
    total_market = solutions_df['total_first_year_value'].str.replace('$', '').str.replace(',', '').astype(int).sum()
    print(f"💎 TOTAL ADDRESSABLE MARKET: ${total_market:,} in first year revenue potential")

    print(f"\n💾 Solution packages saved to: {csv_filename}")
    return csv_filename, solutions_df

if __name__ == "__main__":
    csv_file, df = create_specialized_solutions()