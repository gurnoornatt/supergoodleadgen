#!/usr/bin/env python3
"""
Analyze alternative fitness businesses and create specialized sales approaches
"""

import pandas as pd
import numpy as np
from datetime import datetime
from collections import Counter
import os

def load_and_analyze_businesses():
    """Load the alternative businesses CSV and perform analysis"""
    print("📊 ANALYZING ALTERNATIVE FITNESS BUSINESSES")
    print("="*60)

    # Find the most recent alternative CSV
    csv_files = [f for f in os.listdir('.') if f.startswith('alternative_fitness_businesses_')]
    if not csv_files:
        print("❌ No alternative fitness CSV found!")
        return None

    latest_csv = sorted(csv_files)[-1]
    print(f"📁 Loading: {latest_csv}")

    df = pd.read_csv(latest_csv)
    print(f"📈 Total businesses: {len(df)}")

    return df

def categorize_business_types(df):
    """Enhanced business categorization with more specific types"""
    print("\n🏷️  ENHANCED BUSINESS CATEGORIZATION")
    print("-" * 40)

    def classify_detailed_type(row):
        name = row['business_name'].lower()
        types = str(row['place_types']).lower()
        current_type = row['business_type']

        # More specific categorization
        if any(term in name or term in types for term in ['wellness', 'medical', 'health center', 'clinic']):
            if any(term in name for term in ['spa', 'massage', 'beauty']):
                return "Medical Spa/Wellness"
            elif any(term in name for term in ['chiropractic', 'physical therapy', 'rehab']):
                return "Therapeutic/Rehab Center"
            else:
                return "Health & Wellness Center"

        elif any(term in name or term in types for term in ['yoga', 'pilates', 'meditation', 'mindfulness']):
            return "Mind-Body Studio"

        elif any(term in name or term in types for term in ['dance', 'ballet', 'zumba', 'choreography']):
            return "Dance Studio"

        elif any(term in name or term in types for term in ['martial arts', 'karate', 'jiu-jitsu', 'boxing', 'mma', 'kickboxing', 'judo']):
            return "Martial Arts/Combat Sports"

        elif any(term in name or term in types for term in ['recreation center', 'community center', 'park']):
            if 'park' in name.lower() and 'center' not in name.lower():
                return "Public Park/Recreation"
            else:
                return "Community Recreation Center"

        elif any(term in name or term in types for term in ['sports club', 'country club', 'athletic club']):
            if any(term in name for term in ['golf', 'tennis', 'racquet']):
                return "Country/Racquet Club"
            else:
                return "Athletic/Sports Club"

        elif any(term in name or term in types for term in ['personal training', 'fitness studio', 'gym']):
            if 'personal' in name or 'private' in name:
                return "Personal Training Studio"
            else:
                return "Boutique Fitness Studio"

        else:
            return current_type

    df['detailed_business_type'] = df.apply(classify_detailed_type, axis=1)

    # Count by detailed type
    type_counts = df['detailed_business_type'].value_counts()
    print("\n📊 Business Type Breakdown:")
    for biz_type, count in type_counts.items():
        print(f"   {biz_type}: {count}")

    return df

def create_specialized_solutions(df):
    """Create specialized sales approaches and ROI calculations for each business type"""
    print("\n💡 CREATING SPECIALIZED BUSINESS SOLUTIONS")
    print("-" * 50)

    # Define specialized solutions for each business type
    business_solutions = {
        "Health & Wellness Center": {
            "primary_pain_points": [
                "Patient appointment scheduling inefficiencies",
                "No online booking system",
                "Poor digital patient communication",
                "Missing telehealth capabilities"
            ],
            "recommended_solution": "Healthcare Practice Management System with Patient Portal",
            "key_features": [
                "Online appointment booking",
                "Patient communication portal",
                "Telehealth integration",
                "Insurance verification",
                "HIPAA-compliant messaging"
            ],
            "monthly_value_range": "$497-$997",
            "roi_calculation": "Save 15+ hours/week on admin tasks, reduce no-shows by 30%",
            "target_decision_maker": "Practice Manager/Office Manager",
            "sales_approach": "Focus on patient satisfaction and operational efficiency"
        },

        "Medical Spa/Wellness": {
            "primary_pain_points": [
                "No online booking for spa services",
                "Manual client management",
                "Missing marketing automation",
                "No client retention system"
            ],
            "recommended_solution": "Spa Management System with Client Retention Tools",
            "key_features": [
                "Service booking system",
                "Client history tracking",
                "Automated marketing campaigns",
                "Membership management",
                "Photo documentation"
            ],
            "monthly_value_range": "$297-$697",
            "roi_calculation": "Increase bookings by 40%, improve client retention by 25%",
            "target_decision_maker": "Spa Owner/Manager",
            "sales_approach": "Emphasize luxury client experience and revenue growth"
        },

        "Mind-Body Studio": {
            "primary_pain_points": [
                "Class scheduling complexity",
                "No waitlist management",
                "Missing membership management",
                "Poor instructor scheduling"
            ],
            "recommended_solution": "Studio Management System with Class Scheduling",
            "key_features": [
                "Class booking and waitlists",
                "Membership tracking",
                "Instructor management",
                "Payment processing",
                "Mobile app for clients"
            ],
            "monthly_value_range": "$197-$497",
            "roi_calculation": "Fill classes to 85% capacity, reduce admin time by 20 hours/week",
            "target_decision_maker": "Studio Owner",
            "sales_approach": "Focus on community building and class optimization"
        },

        "Dance Studio": {
            "primary_pain_points": [
                "Complex recital and performance planning",
                "Student progress tracking difficulties",
                "Parent communication challenges",
                "Costume and music management chaos"
            ],
            "recommended_solution": "Dance Studio Management with Performance Tools",
            "key_features": [
                "Student progress tracking",
                "Recital planning tools",
                "Parent communication portal",
                "Costume/music management",
                "Video lesson library"
            ],
            "monthly_value_range": "$197-$397",
            "roi_calculation": "Save 10+ hours/week on recital planning, improve parent satisfaction",
            "target_decision_maker": "Studio Owner/Director",
            "sales_approach": "Emphasize student development and parent engagement"
        },

        "Martial Arts/Combat Sports": {
            "primary_pain_points": [
                "Belt progression tracking complexity",
                "Tournament registration management",
                "Student skill assessment difficulties",
                "Family billing complications"
            ],
            "recommended_solution": "Martial Arts Management with Belt Tracking",
            "key_features": [
                "Belt progression system",
                "Tournament management",
                "Skill assessment tools",
                "Family billing",
                "Sparring partner matching"
            ],
            "monthly_value_range": "$197-$497",
            "roi_calculation": "Streamline belt testing, improve student retention by 20%",
            "target_decision_maker": "Dojo Owner/Head Instructor",
            "sales_approach": "Focus on tradition, discipline, and student achievement"
        },

        "Community Recreation Center": {
            "primary_pain_points": [
                "Multiple program registration complexity",
                "Facility booking conflicts",
                "Large member database management",
                "Event coordination challenges"
            ],
            "recommended_solution": "Community Center Management Platform",
            "key_features": [
                "Program registration system",
                "Facility booking calendar",
                "Member database",
                "Event management",
                "Volunteer coordination"
            ],
            "monthly_value_range": "$697-$1497",
            "roi_calculation": "Handle 50% more programs, reduce booking conflicts by 80%",
            "target_decision_maker": "Recreation Director",
            "sales_approach": "Emphasize community service and operational efficiency"
        },

        "Personal Training Studio": {
            "primary_pain_points": [
                "Client scheduling inefficiencies",
                "Workout plan management chaos",
                "Progress tracking difficulties",
                "Payment collection challenges"
            ],
            "recommended_solution": "Personal Training Management System",
            "key_features": [
                "Client scheduling",
                "Workout plan builder",
                "Progress tracking",
                "Payment automation",
                "Nutrition planning"
            ],
            "monthly_value_range": "$97-$297",
            "roi_calculation": "Train 20% more clients, reduce admin time by 15 hours/week",
            "target_decision_maker": "Head Trainer/Owner",
            "sales_approach": "Focus on client results and trainer efficiency"
        },

        "Country/Racquet Club": {
            "primary_pain_points": [
                "Tee time/court booking system outdated",
                "Member communication ineffective",
                "Event planning complexity",
                "Pro shop inventory management"
            ],
            "recommended_solution": "Country Club Management Platform",
            "key_features": [
                "Tee time/court booking",
                "Member directory",
                "Event management",
                "Pro shop POS",
                "Tournament organization"
            ],
            "monthly_value_range": "$497-$1297",
            "roi_calculation": "Increase facility utilization by 30%, improve member satisfaction",
            "target_decision_maker": "Club Manager/General Manager",
            "sales_approach": "Emphasize prestige, member experience, and exclusivity"
        },

        "Athletic/Sports Club": {
            "primary_pain_points": [
                "Team registration complexity",
                "Game scheduling conflicts",
                "Equipment management issues",
                "League management chaos"
            ],
            "recommended_solution": "Sports Club Management System",
            "key_features": [
                "Team registration",
                "Game scheduling",
                "Equipment tracking",
                "League management",
                "Statistics tracking"
            ],
            "monthly_value_range": "$297-$697",
            "roi_calculation": "Manage 50% more teams, reduce scheduling conflicts",
            "target_decision_maker": "Athletic Director/Club President",
            "sales_approach": "Focus on competitive advantage and team management"
        },

        "Boutique Fitness Studio": {
            "primary_pain_points": [
                "Class capacity optimization",
                "Membership retention challenges",
                "Instructor scheduling difficulties",
                "Equipment maintenance tracking"
            ],
            "recommended_solution": "Boutique Fitness Management Platform",
            "key_features": [
                "Class booking system",
                "Membership management",
                "Instructor scheduling",
                "Equipment tracking",
                "Performance analytics"
            ],
            "monthly_value_range": "$197-$497",
            "roi_calculation": "Increase class utilization by 25%, improve retention by 15%",
            "target_decision_maker": "Studio Owner",
            "sales_approach": "Emphasize personalized experience and community building"
        },

        "Public Park/Recreation": {
            "primary_pain_points": [
                "Limited budget for digital solutions",
                "Public program registration inefficiencies",
                "Maintenance scheduling challenges",
                "Community engagement difficulties"
            ],
            "recommended_solution": "Public Recreation Management (Budget-Friendly)",
            "key_features": [
                "Simple program registration",
                "Maintenance scheduling",
                "Community event calendar",
                "Volunteer management",
                "Basic website integration"
            ],
            "monthly_value_range": "$97-$297",
            "roi_calculation": "Serve 30% more community members, reduce admin overhead",
            "target_decision_maker": "Parks & Recreation Director",
            "sales_approach": "Focus on community service and budget efficiency"
        },

        "Therapeutic/Rehab Center": {
            "primary_pain_points": [
                "Patient progress tracking complexity",
                "Insurance billing complications",
                "Appointment scheduling inefficiencies",
                "Exercise prescription management"
            ],
            "recommended_solution": "Therapy Practice Management System",
            "key_features": [
                "Patient progress tracking",
                "Insurance billing",
                "Appointment scheduling",
                "Exercise prescription tools",
                "Outcome measurement"
            ],
            "monthly_value_range": "$397-$897",
            "roi_calculation": "Improve patient outcomes by 20%, reduce billing errors by 50%",
            "target_decision_maker": "Clinic Director/Head Therapist",
            "sales_approach": "Focus on patient outcomes and clinical efficiency"
        }
    }

    return business_solutions

def check_for_duplicates():
    """Check for duplicates with main gym scraper"""
    print("\n🔍 CHECKING FOR DUPLICATES WITH MAIN GYM SCRAPER")
    print("-" * 50)

    # Look for main gym scraper files
    main_gym_files = [f for f in os.listdir('.') if f.startswith('central_valley_gym_leads_')]

    if not main_gym_files:
        print("ℹ️  No main gym scraper files found - cannot check duplicates")
        return None

    latest_main = sorted(main_gym_files)[-1]
    print(f"📁 Main gym file: {latest_main}")

    try:
        main_df = pd.read_csv(latest_main)
        print(f"📊 Main gym leads: {len(main_df)}")
        return main_df
    except:
        print("❌ Could not load main gym file")
        return None

def generate_specialized_csv(df, solutions, main_df=None):
    """Generate the specialized business solutions CSV"""
    print("\n📄 GENERATING SPECIALIZED_BUSINESS_SOLUTIONS.CSV")
    print("-" * 55)

    specialized_data = []

    for _, row in df.iterrows():
        business_type = row['detailed_business_type']
        solution = solutions.get(business_type, solutions['Boutique Fitness Studio'])  # Default fallback

        # Check for duplicates
        is_duplicate = False
        duplicate_source = ""
        if main_df is not None:
            # Check by business name and phone
            name_match = main_df['business_name'].str.lower().str.contains(row['business_name'].lower(), na=False, regex=False).any()
            phone_match = False
            if pd.notna(row['phone']) and row['phone'] != '':
                try:
                    phone_match = main_df['phone'].str.contains(row['phone'], na=False, regex=False).any()
                except:
                    phone_match = False

            if name_match or phone_match:
                is_duplicate = True
                duplicate_source = "main_gym_scraper"

        # Calculate priority score
        priority_score = 0
        if row['lead_quality'] == 'RED':
            priority_score += 3
        elif row['lead_quality'] == 'YELLOW':
            priority_score += 2
        else:
            priority_score += 1

        if row['reviews'] > 100:
            priority_score += 2
        elif row['reviews'] > 50:
            priority_score += 1

        if row['rating'] >= 4.5:
            priority_score += 1

        specialized_record = {
            'business_name': row['business_name'],
            'city': row['city'],
            'address': row['address'],
            'phone': row['phone'],
            'website': row['website'],
            'rating': row['rating'],
            'reviews': row['reviews'],
            'business_type': business_type,
            'search_term_found': row['search_term_found'],
            'lead_quality': row['lead_quality'],
            'is_duplicate': is_duplicate,
            'duplicate_source': duplicate_source,
            'priority_score': priority_score,
            'primary_pain_points': ' | '.join(solution['primary_pain_points']),
            'recommended_solution': solution['recommended_solution'],
            'key_features': ' | '.join(solution['key_features']),
            'monthly_value_range': solution['monthly_value_range'],
            'roi_calculation': solution['roi_calculation'],
            'target_decision_maker': solution['target_decision_maker'],
            'sales_approach': solution['sales_approach'],
            'specialized_notes': f"Found via '{row['search_term_found']}' search"
        }

        specialized_data.append(specialized_record)

    # Create DataFrame and sort by priority
    specialized_df = pd.DataFrame(specialized_data)
    specialized_df = specialized_df.sort_values(['priority_score', 'reviews'], ascending=[False, False])

    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"specialized_business_solutions_{timestamp}.csv"
    specialized_df.to_csv(filename, index=False)

    print(f"✅ Created: {filename}")
    return specialized_df, filename

def main():
    """Main analysis function"""
    print("\n" + "="*80)
    print("ALTERNATIVE BUSINESS ANALYSIS & SPECIALIZATION")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load and analyze businesses
    df = load_and_analyze_businesses()
    if df is None:
        return

    # Enhanced categorization
    df = categorize_business_types(df)

    # Create specialized solutions
    solutions = create_specialized_solutions(df)

    # Check for duplicates
    main_df = check_for_duplicates()

    # Generate specialized CSV
    specialized_df, filename = generate_specialized_csv(df, solutions, main_df)

    # Analysis summary
    print(f"\n📊 ANALYSIS SUMMARY")
    print("-" * 30)
    print(f"Total businesses analyzed: {len(df)}")
    print(f"Unique business types: {df['detailed_business_type'].nunique()}")

    if main_df is not None:
        duplicates = specialized_df['is_duplicate'].sum()
        print(f"Duplicates with main scraper: {duplicates}")
        print(f"Unique new leads: {len(df) - duplicates}")

    # Top business types
    print(f"\n🏆 TOP BUSINESS TYPES:")
    type_counts = df['detailed_business_type'].value_counts().head(5)
    for i, (biz_type, count) in enumerate(type_counts.items(), 1):
        print(f"{i}. {biz_type}: {count} businesses")

    # High-priority leads
    high_priority = specialized_df[specialized_df['priority_score'] >= 5]
    print(f"\n🎯 HIGH-PRIORITY LEADS: {len(high_priority)}")

    print(f"\n💾 Specialized solutions saved to: {filename}")
    print("✅ Analysis complete!")

    return specialized_df

if __name__ == "__main__":
    result = main()