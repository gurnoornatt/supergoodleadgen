#!/usr/bin/env python3
"""
Comprehensive Central Valley gym scraper to generate 200+ qualified leads
Includes pain point analysis and lead scoring for sales outreach
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

# Central Valley cities to scrape
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
    'Antioch, CA'
]

# Major chains to exclude
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness',
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness',
    'curves', 'pure barre', 'club pilates', 'the bar method', 'solidcore',
    'corepower yoga', 'soulcycle', 'cyclebar', 'barre3', 'burn boot camp',
    'crossfit', 'ufc gym', 'ymca', 'title boxing', 'kickboxing',
    'jazzercise', 'zumba', 'stroller strides'
]

# Search queries for different gym types
SEARCH_QUERIES = [
    "gym fitness center {city}",
    "crossfit box {city}",
    "martial arts dojo {city}",
    "boxing club {city}",
    "personal training studio {city}",
    "powerlifting gym {city}",
    "yoga studio {city}",
    "strength training gym {city}",
    "pilates studio {city}",
    "bootcamp fitness {city}"
]

def is_chain_gym(business_name):
    """Check if gym is a major chain"""
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

def analyze_pain_points(gym_info):
    """Analyze gym's pain points based on digital presence"""
    pain_points = []
    primary_pain = ""
    lead_score = "GREEN"
    recommended_solution = ""
    estimated_monthly_value = "$0"

    has_website = gym_info.get('website_accessible', False)
    reviews = gym_info.get('reviews', 0)
    rating = gym_info.get('rating', 0)
    gym_type = gym_info.get('type', '').lower()
    name = gym_info.get('business_name', '').lower()

    # Analyze pain points
    if not has_website:
        pain_points.append("No website - losing Google traffic to competitors")
        primary_pain = "Missing digital presence completely"
        lead_score = "RED"
        recommended_solution = "Basic website + Google My Business optimization"
        estimated_monthly_value = "$297-497"
    else:
        pain_points.append("Has website but likely missing key features")

    if reviews < 50:
        pain_points.append("Low review count - invisible to new customers")
        if not primary_pain:
            primary_pain = "Poor online visibility"
            lead_score = "YELLOW"

    if '24 hour' in name or '24hr' in name:
        pain_points.append("24hr access likely using physical keys - security risk")
        if lead_score != "RED":
            lead_score = "YELLOW"

    if 'crossfit' in gym_type or 'crossfit' in name:
        pain_points.append("CrossFit box needs WOD posting and class scheduling")
        if not recommended_solution:
            recommended_solution = "CrossFit management system with WOD posting"
            estimated_monthly_value = "$197-397"

    if 'martial arts' in gym_type or 'dojo' in name:
        pain_points.append("Martial arts school needs belt tracking and student portal")
        if not recommended_solution:
            recommended_solution = "Student management system with belt progression"
            estimated_monthly_value = "$197-397"

    if 'personal training' in gym_type:
        pain_points.append("Personal training needs client scheduling and progress tracking")
        if not recommended_solution:
            recommended_solution = "Personal trainer management system"
            estimated_monthly_value = "$97-297"

    if reviews > 200 and rating > 4.5 and not has_website:
        pain_points.append("High-rated gym with major untapped potential")
        primary_pain = "Massive opportunity - popular gym with zero digital presence"
        lead_score = "RED"
        estimated_monthly_value = "$497-997"

    # Set defaults if nothing found
    if not primary_pain:
        primary_pain = "Standard gym needing digital upgrade"

    if not recommended_solution:
        recommended_solution = "Basic gym management system"
        estimated_monthly_value = "$197-397"

    return {
        'lead_score': lead_score,
        'primary_pain': primary_pain,
        'pain_points': '; '.join(pain_points),
        'recommended_solution': recommended_solution,
        'estimated_monthly_value': estimated_monthly_value
    }

def scrape_city_gyms(city, serpapi):
    """Scrape gyms for a specific city"""
    print(f"\n🏙️  SCRAPING: {city}")
    print("-" * 60)

    city_gyms = []

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        print(f"   🔍 {query}")

        try:
            results = serpapi.search_google_maps(
                query=query,
                location=city,
                max_results=15
            )

            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')

                    # Skip chains
                    if is_chain_gym(name):
                        continue

                    # Check if already found this gym
                    if any(gym['business_name'] == name for gym in city_gyms):
                        continue

                    # Extract gym info
                    website_url = place.get('link', '')
                    website_accessible, website_status = check_website_exists(website_url)

                    gym_info = {
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

                    # Add pain point analysis
                    analysis = analyze_pain_points(gym_info)
                    gym_info.update(analysis)

                    city_gyms.append(gym_info)

                    # Show real-time results
                    score_emoji = "🔥" if analysis['lead_score'] == "RED" else "⚡" if analysis['lead_score'] == "YELLOW" else "✅"
                    print(f"      {score_emoji} {name} ({analysis['lead_score']}) - {analysis['primary_pain']}")

            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            continue

    print(f"   📊 Found {len(city_gyms)} independent gyms in {city}")
    return city_gyms

def main():
    """Main scraping function"""
    print("\n" + "="*80)
    print("CENTRAL VALLEY GYM LEAD GENERATION")
    print("Targeting 200+ independent gyms with pain point analysis")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize API client
    serpapi = SerpApiClient()

    all_gyms = []
    city_summaries = []

    # Process each city
    for city in CENTRAL_VALLEY_CITIES:
        city_gyms = scrape_city_gyms(city, serpapi)
        all_gyms.extend(city_gyms)

        # Track city summary
        red_count = len([g for g in city_gyms if g['lead_score'] == 'RED'])
        yellow_count = len([g for g in city_gyms if g['lead_score'] == 'YELLOW'])
        green_count = len([g for g in city_gyms if g['lead_score'] == 'GREEN'])

        city_summaries.append({
            'city': city,
            'total_gyms': len(city_gyms),
            'red_leads': red_count,
            'yellow_leads': yellow_count,
            'green_leads': green_count
        })

        time.sleep(2)  # Rate limiting between cities

    # Remove duplicates based on name and phone
    unique_gyms = {}
    for gym in all_gyms:
        key = f"{gym['business_name']}_{gym['phone']}"
        if key not in unique_gyms:
            unique_gyms[key] = gym

    final_gyms = list(unique_gyms.values())

    # Sort by lead score priority and reviews
    score_priority = {'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    final_gyms.sort(key=lambda x: (score_priority[x['lead_score']], x['reviews']), reverse=True)

    # Print summary
    print(f"\n\n{'='*80}")
    print(f"FINAL RESULTS: {len(final_gyms)} UNIQUE INDEPENDENT GYMS")
    print("="*80)

    red_leads = [g for g in final_gyms if g['lead_score'] == 'RED']
    yellow_leads = [g for g in final_gyms if g['lead_score'] == 'YELLOW']
    green_leads = [g for g in final_gyms if g['lead_score'] == 'GREEN']

    print(f"\n🔥 RED LEADS (Hot): {len(red_leads)}")
    print(f"⚡ YELLOW LEADS (Warm): {len(yellow_leads)}")
    print(f"✅ GREEN LEADS (Cold): {len(green_leads)}")

    # Show top 10 RED leads
    print(f"\n🎯 TOP 10 HOTTEST LEADS:")
    for i, gym in enumerate(red_leads[:10], 1):
        print(f"{i}. {gym['business_name']} ({gym['city']})")
        print(f"   💔 {gym['primary_pain']}")
        print(f"   📞 {gym['phone']}")
        print(f"   💰 {gym['estimated_monthly_value']}")
        print()

    # City breakdown
    print(f"\n📊 CITY BREAKDOWN:")
    for summary in city_summaries:
        print(f"{summary['city']}: {summary['total_gyms']} gyms ({summary['red_leads']} RED, {summary['yellow_leads']} YELLOW)")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Main CSV for sales team
    df = pd.DataFrame(final_gyms)
    csv_file = f"central_valley_gym_leads_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Sales leads saved to: {csv_file}")

    # Hot leads only CSV
    hot_leads_df = pd.DataFrame(red_leads)
    hot_csv = f"hot_gym_leads_{timestamp}.csv"
    hot_leads_df.to_csv(hot_csv, index=False)
    print(f"🔥 Hot leads only saved to: {hot_csv}")

    # Summary report
    summary_df = pd.DataFrame(city_summaries)
    summary_csv = f"city_summary_{timestamp}.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"📊 City summary saved to: {summary_csv}")

    print(f"\n✅ MISSION COMPLETE: {len(final_gyms)} leads ready for sales outreach!")
    print(f"🎯 Priority target: {len(red_leads)} RED leads with immediate pain points")

    return final_gyms

if __name__ == "__main__":
    gyms = main()