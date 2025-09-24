#!/usr/bin/env python3
"""
Specialized Fitness Business Scraper for Central Valley
Targets: dance studios, rock climbing gyms, swimming pools, tennis clubs,
golf fitness, cycling studios, rehabilitation centers
Generates specialized pain point analysis for each business type
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import SerpApiClient
from config import Config

# Central Valley cities - comprehensive list
CENTRAL_VALLEY_CITIES = [
    'Bakersfield, CA',
    'Fresno, CA',
    'Stockton, CA',
    'Modesto, CA',
    'Visalia, CA',
    'Merced, CA',
    'Turlock, CA',
    'Tracy, CA',
    'Manteca, CA',
    'Lodi, CA',
    'Clovis, CA',
    'Madera, CA',
    'Hanford, CA',
    'Porterville, CA',
    'Antioch, CA',
    'Salinas, CA',
    'Chico, CA',
    'Fairfield, CA',
    'Vacaville, CA',
    'San Ramon, CA',
    'Livermore, CA',
    'Pleasanton, CA',
    'Dublin, CA',
    'Concord, CA',
    'Walnut Creek, CA',
    'Pittsburg, CA',
    'Brentwood, CA',
    'Oakley, CA',
    'Rio Vista, CA',
    'Lathrop, CA',
    'Ripon, CA',
    'Escalon, CA',
    'Riverbank, CA',
    'Oakdale, CA',
    'Waterford, CA',
    'Hughson, CA',
    'Keyes, CA',
    'Empire, CA',
    'Ceres, CA',
    'Patterson, CA',
    'Newman, CA',
    'Gustine, CA',
    'Los Banos, CA',
    'Dos Palos, CA',
    'Chowchilla, CA',
    'Atwater, CA',
    'Livingston, CA',
    'Winton, CA',
    'Hilmar, CA',
    'Stevinson, CA',
    'Le Grand, CA',
    'Planada, CA',
    'Delhi, CA',
    'Ballico, CA',
    'Cressey, CA',
    'Snelling, CA',
    'Hornitos, CA',
    'Catheys Valley, CA',
    'Coulterville, CA',
    'Bear Valley, CA',
    'Mariposa, CA',
    'Midpines, CA',
    'El Portal, CA',
    'Yosemite, CA'
]

# Specialized fitness business search queries
SPECIALIZED_QUERIES = {
    'dance_studios': [
        "dance studio {city}",
        "ballet studio {city}",
        "hip hop dance {city}",
        "ballroom dance {city}",
        "contemporary dance {city}",
        "jazz dance studio {city}",
        "dance academy {city}",
        "dance school {city}"
    ],
    'rock_climbing': [
        "rock climbing gym {city}",
        "climbing wall {city}",
        "bouldering gym {city}",
        "indoor climbing {city}",
        "climbing center {city}"
    ],
    'swimming': [
        "swimming pool {city}",
        "swim school {city}",
        "aquatic center {city}",
        "swim lessons {city}",
        "lap pool {city}",
        "water aerobics {city}"
    ],
    'tennis': [
        "tennis club {city}",
        "tennis court {city}",
        "tennis academy {city}",
        "tennis lessons {city}",
        "racquet club {city}"
    ],
    'golf_fitness': [
        "golf fitness {city}",
        "golf training {city}",
        "golf simulator {city}",
        "golf lessons {city}",
        "golf academy {city}",
        "golf performance {city}"
    ],
    'cycling': [
        "cycling studio {city}",
        "spin class {city}",
        "indoor cycling {city}",
        "bike studio {city}",
        "cycling fitness {city}"
    ],
    'rehabilitation': [
        "physical therapy {city}",
        "rehabilitation center {city}",
        "sports therapy {city}",
        "physical rehabilitation {city}",
        "physiotherapy {city}",
        "sports medicine {city}",
        "injury rehabilitation {city}"
    ]
}

# Major chains to exclude
MAJOR_CHAINS = [
    'planet fitness', 'la fitness', '24 hour fitness', 'anytime fitness',
    'orangetheory', 'f45', 'soulcycle', 'cyclebar', 'pure barre',
    'club pilates', 'corepower yoga', 'ymca', 'kaiser permanente',
    'dignity health', 'adventist health', 'sutter health', 'stanford health'
]

def is_chain_business(business_name):
    """Check if business is a major chain"""
    name_lower = business_name.lower()
    return any(chain in name_lower for chain in MAJOR_CHAINS)

def check_website_exists(url):
    """Check if website exists and is accessible"""
    if not url or url == '':
        return False, "No website"

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200, f"Status: {response.status_code}"
    except:
        return False, "Website inaccessible"

def analyze_specialized_pain_points(business_info, business_type):
    """Analyze specialized pain points based on business type and digital presence"""
    pain_points = []
    primary_pain = ""
    lead_score = "GREEN"
    recommended_solution = ""
    estimated_monthly_value = "$0"

    has_website = business_info.get('website_accessible', False)
    reviews = business_info.get('reviews', 0)
    rating = business_info.get('rating', 0)
    name = business_info.get('business_name', '').lower()

    # Base digital presence analysis
    if not has_website:
        pain_points.append("No website - missing online bookings and class schedules")
        primary_pain = "Zero digital presence"
        lead_score = "RED"

    if reviews < 30:
        pain_points.append("Low review count - invisible to new customers searching online")
        if lead_score != "RED":
            lead_score = "YELLOW"

    # Specialized pain points by business type
    if business_type == 'dance_studios':
        pain_points.extend([
            "Dance studios need online class scheduling and recital management",
            "Parents want progress tracking and performance videos",
            "Competition registration and costume ordering systems missing"
        ])
        if not has_website:
            primary_pain = "Dance parents expect online registration and communication"
            recommended_solution = "Dance studio management system with parent portal"
            estimated_monthly_value = "$297-497"
        else:
            recommended_solution = "Enhanced dance studio features (recitals, competitions)"
            estimated_monthly_value = "$197-397"

    elif business_type == 'rock_climbing':
        pain_points.extend([
            "Climbers need route difficulty tracking and progress logging",
            "Day pass vs membership management for casual climbers",
            "Equipment rental and safety waiver systems needed"
        ])
        if not has_website:
            primary_pain = "Climbing community expects digital route tracking"
            recommended_solution = "Climbing gym management with route tracking"
            estimated_monthly_value = "$397-597"
        else:
            recommended_solution = "Route tracking and climbing progress features"
            estimated_monthly_value = "$197-397"

    elif business_type == 'swimming':
        pain_points.extend([
            "Swim lessons need skill level progression tracking",
            "Pool scheduling for lap swimmers vs lessons vs parties",
            "Water safety certification and instructor management"
        ])
        if not has_website:
            primary_pain = "Parents need online lesson booking and progress reports"
            recommended_solution = "Swim school management with skill tracking"
            estimated_monthly_value = "$397-697"
        else:
            recommended_solution = "Enhanced swim lesson management features"
            estimated_monthly_value = "$197-397"

    elif business_type == 'tennis':
        pain_points.extend([
            "Court booking system needed for members and lessons",
            "Tournament organization and ladder ranking systems",
            "Pro shop inventory and racquet stringing services"
        ])
        if not has_website:
            primary_pain = "Tennis players expect online court booking"
            recommended_solution = "Tennis club management with court scheduling"
            estimated_monthly_value = "$497-797"
        else:
            recommended_solution = "Enhanced tennis features (tournaments, rankings)"
            estimated_monthly_value = "$297-497"

    elif business_type == 'golf_fitness':
        pain_points.extend([
            "Golf swing analysis and lesson booking systems needed",
            "Tee time coordination with local courses",
            "Equipment fitting and custom club services"
        ])
        if not has_website:
            primary_pain = "Golfers expect online lesson booking and swing analysis"
            recommended_solution = "Golf training center management system"
            estimated_monthly_value = "$497-997"
        else:
            recommended_solution = "Golf-specific features (swing analysis, course integration)"
            estimated_monthly_value = "$297-597"

    elif business_type == 'cycling':
        pain_points.extend([
            "Class intensity tracking and heart rate monitoring",
            "Bike maintenance and reservation systems",
            "Virtual ride integration and performance tracking"
        ])
        if not has_website:
            primary_pain = "Cyclists expect performance tracking and class booking"
            recommended_solution = "Cycling studio management with performance tracking"
            estimated_monthly_value = "$297-497"
        else:
            recommended_solution = "Enhanced cycling features (performance, virtual rides)"
            estimated_monthly_value = "$197-397"

    elif business_type == 'rehabilitation':
        pain_points.extend([
            "Patient progress tracking and exercise prescription",
            "Insurance claim processing and appointment scheduling",
            "Home exercise program delivery and compliance tracking"
        ])
        if not has_website:
            primary_pain = "Patients expect online scheduling and progress tracking"
            recommended_solution = "Physical therapy practice management system"
            estimated_monthly_value = "$697-1497"
            lead_score = "RED"  # Higher value for healthcare
        else:
            recommended_solution = "Enhanced PT features (progress tracking, home exercises)"
            estimated_monthly_value = "$397-797"

    # High-potential indicators
    if reviews > 100 and rating > 4.5 and not has_website:
        pain_points.append("High-rated business with massive untapped digital potential")
        primary_pain = f"Popular {business_type.replace('_', ' ')} with zero digital presence"
        lead_score = "RED"
        # Increase value estimate for popular businesses
        current_max = int(estimated_monthly_value.split('-')[1].replace('$', ''))
        estimated_monthly_value = f"${current_max}-{current_max * 2}"

    # Set defaults if nothing found
    if not primary_pain:
        primary_pain = f"Standard {business_type.replace('_', ' ')} needing digital upgrade"

    if not recommended_solution:
        recommended_solution = f"Basic {business_type.replace('_', ' ')} management system"
        estimated_monthly_value = "$197-397"

    return {
        'business_type': business_type.replace('_', ' ').title(),
        'lead_score': lead_score,
        'primary_pain': primary_pain,
        'pain_points': '; '.join(pain_points),
        'recommended_solution': recommended_solution,
        'estimated_monthly_value': estimated_monthly_value
    }

def scrape_specialized_businesses(city, business_type, queries, serpapi):
    """Scrape specialized fitness businesses for a specific city and type"""
    print(f"\n🏙️  SCRAPING {business_type.upper().replace('_', ' ')} in {city}")
    print("-" * 60)

    businesses = []

    for query_template in queries:
        query = query_template.format(city=city)
        print(f"   🔍 {query}")

        try:
            results = serpapi.search_google_maps(
                query=query,
                location=city,
                max_results=20  # More results for specialized businesses
            )

            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')

                    # Skip chains
                    if is_chain_business(name):
                        continue

                    # Check if already found this business
                    if any(biz['business_name'] == name for biz in businesses):
                        continue

                    # Extract business info
                    website_url = place.get('link', '')
                    website_accessible, website_status = check_website_exists(website_url)

                    business_info = {
                        'business_name': name,
                        'city': city.split(',')[0],
                        'address': place.get('address', ''),
                        'phone': place.get('phone', ''),
                        'website': website_url,
                        'website_accessible': website_accessible,
                        'website_status': website_status,
                        'rating': place.get('rating', 0),
                        'reviews': place.get('reviews', 0),
                        'type': place.get('type', ''),
                        'place_id': place.get('place_id', ''),
                        'scraped_at': datetime.now().isoformat()
                    }

                    # Add specialized pain point analysis
                    analysis = analyze_specialized_pain_points(business_info, business_type)
                    business_info.update(analysis)

                    businesses.append(business_info)

                    # Show real-time results
                    score_emoji = "🔥" if analysis['lead_score'] == "RED" else "⚡" if analysis['lead_score'] == "YELLOW" else "✅"
                    print(f"      {score_emoji} {name} ({analysis['lead_score']}) - {analysis['primary_pain']}")

            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            continue

    print(f"   📊 Found {len(businesses)} {business_type.replace('_', ' ')} businesses in {city}")
    return businesses

def main():
    """Main scraping function for specialized fitness businesses"""
    print("\n" + "="*80)
    print("SPECIALIZED FITNESS BUSINESS LEAD GENERATION")
    print("Targeting dance studios, climbing gyms, pools, tennis, golf, cycling, rehab")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize API client
    serpapi = SerpApiClient()

    all_businesses = []
    type_summaries = []

    # Process each business type across all cities
    for business_type, queries in SPECIALIZED_QUERIES.items():
        print(f"\n{'='*60}")
        print(f"PROCESSING {business_type.upper().replace('_', ' ')} BUSINESSES")
        print("="*60)

        type_businesses = []

        for city in CENTRAL_VALLEY_CITIES:
            city_businesses = scrape_specialized_businesses(city, business_type, queries, serpapi)
            type_businesses.extend(city_businesses)
            all_businesses.extend(city_businesses)

            time.sleep(1)  # Rate limiting between cities

        # Track business type summary
        red_count = len([b for b in type_businesses if b['lead_score'] == 'RED'])
        yellow_count = len([b for b in type_businesses if b['lead_score'] == 'YELLOW'])
        green_count = len([b for b in type_businesses if b['lead_score'] == 'GREEN'])

        type_summaries.append({
            'business_type': business_type.replace('_', ' ').title(),
            'total_businesses': len(type_businesses),
            'red_leads': red_count,
            'yellow_leads': yellow_count,
            'green_leads': green_count
        })

        print(f"\n📊 {business_type.replace('_', ' ').title()} Summary: {len(type_businesses)} total ({red_count} RED, {yellow_count} YELLOW)")

        time.sleep(2)  # Rate limiting between business types

    # Remove duplicates based on name and phone
    unique_businesses = {}
    for business in all_businesses:
        key = f"{business['business_name']}_{business['phone']}"
        if key not in unique_businesses:
            unique_businesses[key] = business

    final_businesses = list(unique_businesses.values())

    # Sort by lead score priority and reviews
    score_priority = {'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    final_businesses.sort(key=lambda x: (score_priority[x['lead_score']], x['reviews']), reverse=True)

    # Print summary
    print(f"\n\n{'='*80}")
    print(f"FINAL RESULTS: {len(final_businesses)} UNIQUE SPECIALIZED FITNESS BUSINESSES")
    print("="*80)

    red_leads = [b for b in final_businesses if b['lead_score'] == 'RED']
    yellow_leads = [b for b in final_businesses if b['lead_score'] == 'YELLOW']
    green_leads = [b for b in final_businesses if b['lead_score'] == 'GREEN']

    print(f"\n🔥 RED LEADS (Hot): {len(red_leads)}")
    print(f"⚡ YELLOW LEADS (Warm): {len(yellow_leads)}")
    print(f"✅ GREEN LEADS (Cold): {len(green_leads)}")

    # Show top 10 RED leads
    print(f"\n🎯 TOP 10 HOTTEST SPECIALIZED FITNESS LEADS:")
    for i, business in enumerate(red_leads[:10], 1):
        print(f"{i}. {business['business_name']} ({business['city']}) - {business['business_type']}")
        print(f"   💔 {business['primary_pain']}")
        print(f"   📞 {business['phone']}")
        print(f"   💰 {business['estimated_monthly_value']}")
        print()

    # Business type breakdown
    print(f"\n📊 BUSINESS TYPE BREAKDOWN:")
    for summary in type_summaries:
        print(f"{summary['business_type']}: {summary['total_businesses']} businesses ({summary['red_leads']} RED, {summary['yellow_leads']} YELLOW)")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Main CSV for sales team
    df = pd.DataFrame(final_businesses)
    csv_file = f"specialized_fitness_leads_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Specialized fitness leads saved to: {csv_file}")

    # Hot leads only CSV
    hot_leads_df = pd.DataFrame(red_leads)
    hot_csv = f"hot_specialized_fitness_leads_{timestamp}.csv"
    hot_leads_df.to_csv(hot_csv, index=False)
    print(f"🔥 Hot specialized leads only saved to: {hot_csv}")

    # Business type summary
    summary_df = pd.DataFrame(type_summaries)
    summary_csv = f"specialized_fitness_summary_{timestamp}.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"📊 Business type summary saved to: {summary_csv}")

    print(f"\n✅ MISSION COMPLETE: {len(final_businesses)} specialized fitness leads ready!")
    print(f"🎯 Priority target: {len(red_leads)} RED leads with immediate specialized pain points")

    return final_businesses

if __name__ == "__main__":
    businesses = main()