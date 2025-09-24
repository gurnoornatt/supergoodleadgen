#!/usr/bin/env python3
"""
Create specialized fitness CSV with pain points analysis
Filters existing data for dance studios, climbing gyms, pools, tennis, golf, cycling, rehab
"""

import pandas as pd
from datetime import datetime

def create_specialized_fitness_csv():
    """Create specialized fitness CSV from existing alternative fitness data"""

    # Read the existing alternative fitness data
    df = pd.read_csv('alternative_fitness_businesses_20250916_215141.csv')

    # Define specialized fitness categories and their pain points
    specialized_categories = {
        'Dance Studios': {
            'keywords': ['dance', 'ballet', 'studio', 'choreography', 'ballroom'],
            'pain_points': [
                'Online class scheduling and registration system needed',
                'Parent communication portal for progress updates',
                'Recital management and costume ordering',
                'Competition registration and team management',
                'Performance video sharing platform',
                'Student progress tracking and skill assessments'
            ],
            'solutions': [
                'Dance studio management software with parent portal',
                'Online registration and payment processing',
                'Student progress tracking system',
                'Recital and competition management tools'
            ],
            'monthly_value': '$297-697'
        },
        'Swimming/Aquatic Centers': {
            'keywords': ['aquatic', 'swimming', 'pool', 'swim'],
            'pain_points': [
                'Swim lesson skill progression tracking',
                'Pool scheduling for multiple activities (lessons, lap swimming, parties)',
                'Safety certification and instructor management',
                'Equipment rental and maintenance tracking',
                'Water quality monitoring and reporting',
                'Membership management for different access levels'
            ],
            'solutions': [
                'Aquatic center management system',
                'Swim lesson scheduling and progress tracking',
                'Pool reservation and activity management',
                'Safety compliance and certification tracking'
            ],
            'monthly_value': '$397-897'
        },
        'Boxing/Martial Arts': {
            'keywords': ['boxing', 'martial', 'combat', 'karate', 'jiu-jitsu'],
            'pain_points': [
                'Belt rank progression and testing schedules',
                'Equipment inventory and rental management',
                'Tournament registration and bracket management',
                'Training session intensity and progress tracking',
                'Safety waiver and insurance management',
                'Sparring partner matching system'
            ],
            'solutions': [
                'Martial arts school management system',
                'Belt progression and testing tracking',
                'Tournament and competition management',
                'Training progress and technique tracking'
            ],
            'monthly_value': '$297-597'
        },
        'Wellness/Medical Spa': {
            'keywords': ['wellness', 'spa', 'medical spa', 'therapy'],
            'pain_points': [
                'Appointment scheduling and treatment tracking',
                'Client health history and progress documentation',
                'Treatment protocol and compliance monitoring',
                'Insurance billing and claim processing',
                'Staff certification and continuing education tracking',
                'Equipment maintenance and safety protocols'
            ],
            'solutions': [
                'Medical spa practice management system',
                'Client health tracking and documentation',
                'Appointment scheduling and billing integration',
                'Compliance and certification management'
            ],
            'monthly_value': '$697-1497'
        },
        'Recreation Centers': {
            'keywords': ['recreation', 'community', 'park'],
            'pain_points': [
                'Multi-facility scheduling and booking system',
                'Program registration for diverse activities',
                'Membership management for community programs',
                'Event planning and facility rental coordination',
                'Equipment checkout and maintenance tracking',
                'Community outreach and program promotion'
            ],
            'solutions': [
                'Community recreation management system',
                'Multi-facility booking and scheduling',
                'Program registration and member management',
                'Event coordination and facility rental tools'
            ],
            'monthly_value': '$497-997'
        }
    }

    # Create specialized fitness records
    specialized_records = []

    for index, row in df.iterrows():
        business_name = str(row['business_name']).lower()
        business_type = str(row['business_type']).lower()
        place_types = str(row['place_types']).lower()

        # Categorize each business
        matched_category = None
        for category, details in specialized_categories.items():
            if any(keyword in business_name or keyword in business_type or keyword in place_types
                   for keyword in details['keywords']):
                matched_category = category
                break

        if matched_category:
            category_details = specialized_categories[matched_category]

            # Create specialized record
            specialized_record = {
                'business_name': row['business_name'],
                'city': row['city'],
                'address': row['address'],
                'phone': row['phone'],
                'website': row['website'] if pd.notna(row['website']) else 'None',
                'website_accessible': row['website_accessible'],
                'rating': row['rating'],
                'reviews': row['reviews'],
                'specialized_category': matched_category,
                'original_business_type': row['business_type'],
                'lead_score': 'RED' if not row['website_accessible'] and row['reviews'] > 100 else
                            'YELLOW' if not row['website_accessible'] else 'GREEN',
                'primary_pain_point': category_details['pain_points'][0],
                'specialized_pain_points': '; '.join(category_details['pain_points']),
                'recommended_solutions': '; '.join(category_details['solutions']),
                'estimated_monthly_value': category_details['monthly_value'],
                'assessment_notes': row['assessment_notes'],
                'scraped_at': datetime.now().isoformat()
            }

            specialized_records.append(specialized_record)

    # Create DataFrame and sort by priority
    specialized_df = pd.DataFrame(specialized_records)

    # Sort by lead score (RED first) and then by reviews
    score_priority = {'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    specialized_df['score_priority'] = specialized_df['lead_score'].map(score_priority)
    specialized_df = specialized_df.sort_values(['score_priority', 'reviews'], ascending=[False, False])
    specialized_df = specialized_df.drop('score_priority', axis=1)

    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f'specialized_fitness_with_pain_points_{timestamp}.csv'
    specialized_df.to_csv(csv_filename, index=False)

    # Create summary report
    print("\n" + "="*80)
    print("SPECIALIZED FITNESS BUSINESSES WITH PAIN POINT ANALYSIS")
    print("="*80)
    print(f"Total specialized fitness businesses found: {len(specialized_df)}")

    # Category breakdown
    print(f"\n📊 CATEGORY BREAKDOWN:")
    category_counts = specialized_df['specialized_category'].value_counts()
    for category, count in category_counts.items():
        red_count = len(specialized_df[(specialized_df['specialized_category'] == category) &
                                     (specialized_df['lead_score'] == 'RED')])
        print(f"  {category}: {count} businesses ({red_count} RED leads)")

    # Lead quality breakdown
    print(f"\n🎯 LEAD QUALITY BREAKDOWN:")
    red_leads = specialized_df[specialized_df['lead_score'] == 'RED']
    yellow_leads = specialized_df[specialized_df['lead_score'] == 'YELLOW']
    green_leads = specialized_df[specialized_df['lead_score'] == 'GREEN']

    print(f"  🔥 RED LEADS (Hot): {len(red_leads)}")
    print(f"  ⚡ YELLOW LEADS (Warm): {len(yellow_leads)}")
    print(f"  ✅ GREEN LEADS (Cold): {len(green_leads)}")

    # Top RED leads
    print(f"\n🔥 TOP 10 HOTTEST SPECIALIZED FITNESS LEADS:")
    for i, (idx, lead) in enumerate(red_leads.head(10).iterrows(), 1):
        print(f"{i}. {lead['business_name']} ({lead['city']}) - {lead['specialized_category']}")
        print(f"   💔 {lead['primary_pain_point']}")
        print(f"   📞 {lead['phone']}")
        print(f"   💰 {lead['estimated_monthly_value']}")
        print(f"   ⭐ {lead['rating']} stars ({lead['reviews']} reviews)")
        print()

    print(f"💾 Specialized fitness leads saved to: {csv_filename}")
    return csv_filename, specialized_df

if __name__ == "__main__":
    csv_file, df = create_specialized_fitness_csv()