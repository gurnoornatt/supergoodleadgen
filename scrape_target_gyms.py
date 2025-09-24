#!/usr/bin/env python3
"""
Targeted gym scraper for specific Central Valley cities
Focuses on: Manteca, Lodi, Clovis, Madera, Hanford, Porterville
Includes comprehensive pain point analysis and lead scoring
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

# Target cities for this focused scraping
TARGET_CITIES = [
    'Manteca, CA',
    'Lodi, CA',
    'Clovis, CA',
    'Madera, CA',
    'Hanford, CA',
    'Porterville, CA'
]

# Major chains to exclude - expanded list for gyms
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness',
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness',
    'curves', 'pure barre', 'club pilates', 'the bar method', 'solidcore',
    'corepower yoga', 'soulcycle', 'cyclebar', 'barre3', 'burn boot camp',
    'crossfit', 'ufc gym', 'ymca', 'title boxing', 'kickboxing',
    'jazzercise', 'zumba', 'stroller strides', 'orange theory',
    'fitness 19', 'charter fitness', 'curves for women', 'snap',
    'powerhouse gym', 'retro fitness', 'youfit', 'fitness connection'
]

# Comprehensive search queries for different gym types
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
    "bootcamp fitness {city}",
    "mma gym {city}",
    "kickboxing gym {city}",
    "weightlifting gym {city}",
    "functional fitness {city}",
    "dance fitness studio {city}",
    "athletic training {city}",
    "fitness studio {city}",
    "health club {city}",
    "wellness center {city}",
    "sports performance {city}"
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
    """Enhanced pain point analysis for gym leads"""
    pain_points = []
    primary_pain = ""
    lead_score = "GREEN"
    recommended_solution = ""
    estimated_monthly_value = "$0"
    urgency_score = 1  # 1-10 scale

    # Extract gym data
    has_website = gym_info.get('website_accessible', False)
    reviews = gym_info.get('reviews', 0)
    rating = gym_info.get('rating', 0)
    gym_type = gym_info.get('type', '').lower()
    name = gym_info.get('business_name', '').lower()
    website_url = gym_info.get('website', '')

    # Critical Pain Points (RED FLAGS)
    if not has_website:
        pain_points.append("No website - losing 73% of potential customers who search online first")
        primary_pain = "Missing digital presence completely"
        lead_score = "RED"
        recommended_solution = "Professional website + Google My Business optimization + online booking"
        estimated_monthly_value = "$497-997"
        urgency_score = 9

    # High-value opportunities
    if reviews > 100 and rating > 4.5 and not has_website:
        pain_points.append("High-rated gym with massive untapped potential - popular but invisible online")
        primary_pain = "GOLDMINE: Popular gym with zero digital presence"
        lead_score = "RED"
        estimated_monthly_value = "$997-1497"
        urgency_score = 10

    # Website exists but likely poor quality
    if has_website:
        pain_points.append("Has website but likely missing: online booking, mobile optimization, lead capture")
        if reviews < 30:
            primary_pain = "Website exists but not generating leads effectively"
            lead_score = "YELLOW"
            recommended_solution = "Website optimization + lead capture system + review generation"
            estimated_monthly_value = "$297-597"
            urgency_score = 5

    # Review-based pain points
    if reviews < 20:
        pain_points.append("Low review count - invisible to local search customers")
        if not primary_pain:
            primary_pain = "Poor online visibility - missing local search traffic"
            lead_score = "YELLOW"
            urgency_score = 6

    if reviews >= 20 and reviews < 100:
        pain_points.append("Moderate reviews but room for growth - need review automation")
        urgency_score = max(urgency_score, 4)

    # Gym-type specific pain points
    if 'crossfit' in gym_type or 'crossfit' in name:
        pain_points.append("CrossFit box needs: WOD posting, class scheduling, member progress tracking")
        if not recommended_solution:
            recommended_solution = "CrossFit management system with WOD posting + member app"
            estimated_monthly_value = "$397-697"
            urgency_score = max(urgency_score, 7)

    if 'martial arts' in gym_type or 'dojo' in name or 'karate' in name or 'jiu' in name:
        pain_points.append("Martial arts needs: belt tracking, student portal, parent communication")
        if not recommended_solution:
            recommended_solution = "Martial arts student management system with belt progression"
            estimated_monthly_value = "$297-597"
            urgency_score = max(urgency_score, 6)

    if 'personal training' in gym_type or 'personal trainer' in name:
        pain_points.append("Personal training needs: client scheduling, progress tracking, payment processing")
        if not recommended_solution:
            recommended_solution = "Personal trainer management system with client portal"
            estimated_monthly_value = "$197-497"
            urgency_score = max(urgency_score, 6)

    if 'yoga' in gym_type or 'yoga' in name:
        pain_points.append("Yoga studio needs: class booking, instructor scheduling, membership management")
        if not recommended_solution:
            recommended_solution = "Yoga studio management system with online booking"
            estimated_monthly_value = "$297-497"
            urgency_score = max(urgency_score, 5)

    if 'pilates' in gym_type or 'pilates' in name:
        pain_points.append("Pilates studio needs: equipment scheduling, small class management, waitlists")
        if not recommended_solution:
            recommended_solution = "Pilates studio management with equipment booking"
            estimated_monthly_value = "$297-497"
            urgency_score = max(urgency_score, 5)

    # Security and access pain points
    if '24 hour' in name or '24hr' in name or 'anytime' in name:
        pain_points.append("24hr access using physical keys - security risk and operational nightmare")
        if lead_score != "RED":
            lead_score = "YELLOW"
        urgency_score = max(urgency_score, 8)

    # Website quality indicators
    if website_url and has_website:
        if 'wix.com' in website_url or 'squarespace.com' in website_url:
            pain_points.append("Using basic website builder - missing gym-specific features")
            urgency_score = max(urgency_score, 4)
        elif 'facebook.com' in website_url:
            pain_points.append("Using Facebook as main website - missing professional presence")
            if lead_score == "GREEN":
                lead_score = "YELLOW"
            urgency_score = max(urgency_score, 7)

    # Set defaults if nothing found
    if not primary_pain:
        primary_pain = "Standard gym needing digital modernization"
        urgency_score = 3

    if not recommended_solution:
        recommended_solution = "Complete gym management system with member portal"
        estimated_monthly_value = "$297-597"

    # Calculate follow-up priority
    if urgency_score >= 8:
        follow_up_priority = "IMMEDIATE - Call today"
    elif urgency_score >= 6:
        follow_up_priority = "HIGH - Call this week"
    elif urgency_score >= 4:
        follow_up_priority = "MEDIUM - Call within 2 weeks"
    else:
        follow_up_priority = "LOW - Email first"

    return {
        'lead_score': lead_score,
        'primary_pain': primary_pain,
        'pain_points': '; '.join(pain_points),
        'recommended_solution': recommended_solution,
        'estimated_monthly_value': estimated_monthly_value,
        'urgency_score': urgency_score,
        'follow_up_priority': follow_up_priority
    }

def scrape_city_gyms(city, serpapi):
    """Scrape gyms for a specific city with comprehensive analysis"""
    print(f"\n🏙️  SCRAPING: {city}")
    print("-" * 80)

    city_gyms = []
    found_names = set()  # Track unique names within city

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        print(f"   🔍 {query}")

        try:
            results = serpapi.search_google_maps(
                query=query,
                location=city,
                max_results=20  # Increased for better coverage
            )

            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')

                    # Skip chains
                    if is_chain_gym(name):
                        continue

                    # Skip duplicates within this city
                    if name in found_names:
                        continue

                    found_names.add(name)

                    # Extract comprehensive gym info
                    website_url = place.get('link', '')
                    website_accessible, website_status = check_website_exists(website_url)

                    gym_info = {
                        'business_name': name,
                        'city': city.split(',')[0],
                        'full_address': place.get('address', ''),
                        'phone': place.get('phone', ''),
                        'website': website_url,
                        'website_accessible': website_accessible,
                        'website_status': website_status,
                        'rating': place.get('rating', 0),
                        'reviews': place.get('reviews', 0),
                        'type': place.get('type', ''),
                        'place_id': place.get('place_id', ''),
                        'google_maps_url': f"https://maps.google.com/?cid={place.get('place_id', '')}",
                        'scraped_at': datetime.now().isoformat(),
                        'search_query': query
                    }

                    # Add comprehensive pain point analysis
                    analysis = analyze_pain_points(gym_info)
                    gym_info.update(analysis)

                    city_gyms.append(gym_info)

                    # Show real-time results with enhanced emoji indicators
                    if analysis['lead_score'] == "RED":
                        score_emoji = "🔥"
                    elif analysis['lead_score'] == "YELLOW":
                        score_emoji = "⚡"
                    else:
                        score_emoji = "✅"

                    urgency_emoji = "🚨" if analysis['urgency_score'] >= 8 else "⏰" if analysis['urgency_score'] >= 6 else "📅"

                    print(f"      {score_emoji}{urgency_emoji} {name} ({analysis['lead_score']}) - {analysis['primary_pain']}")
                    print(f"         💰 {analysis['estimated_monthly_value']} | {analysis['follow_up_priority']}")

            time.sleep(1.5)  # Rate limiting

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            continue

    # Sort by urgency and lead score
    city_gyms.sort(key=lambda x: (x['urgency_score'], {'RED': 3, 'YELLOW': 2, 'GREEN': 1}[x['lead_score']]), reverse=True)

    print(f"   📊 Found {len(city_gyms)} independent gyms in {city}")
    return city_gyms

def main():
    """Main scraping function for target cities"""
    print("\n" + "="*100)
    print("TARGETED GYM LEAD GENERATION - CENTRAL VALLEY FOCUS")
    print("Cities: Manteca, Lodi, Clovis, Madera, Hanford, Porterville")
    print("="*100)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize API client
    serpapi = SerpApiClient()

    all_gyms = []
    city_summaries = []

    # Process each target city
    for city in TARGET_CITIES:
        city_gyms = scrape_city_gyms(city, serpapi)
        all_gyms.extend(city_gyms)

        # Track detailed city summary
        red_count = len([g for g in city_gyms if g['lead_score'] == 'RED'])
        yellow_count = len([g for g in city_gyms if g['lead_score'] == 'YELLOW'])
        green_count = len([g for g in city_gyms if g['lead_score'] == 'GREEN'])
        urgent_count = len([g for g in city_gyms if g['urgency_score'] >= 8])

        city_summaries.append({
            'city': city,
            'total_gyms': len(city_gyms),
            'red_leads': red_count,
            'yellow_leads': yellow_count,
            'green_leads': green_count,
            'urgent_leads': urgent_count,
            'avg_urgency': sum(g['urgency_score'] for g in city_gyms) / len(city_gyms) if city_gyms else 0
        })

        time.sleep(3)  # Rate limiting between cities

    # Remove cross-city duplicates based on name and phone
    unique_gyms = {}
    for gym in all_gyms:
        key = f"{gym['business_name']}_{gym['phone']}"
        if key not in unique_gyms or gym['urgency_score'] > unique_gyms[key]['urgency_score']:
            unique_gyms[key] = gym

    final_gyms = list(unique_gyms.values())

    # Sort by urgency score and lead score priority
    score_priority = {'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    final_gyms.sort(key=lambda x: (x['urgency_score'], score_priority[x['lead_score']], x['reviews']), reverse=True)

    # Generate comprehensive results
    print(f"\n\n{'='*100}")
    print(f"FINAL RESULTS: {len(final_gyms)} UNIQUE INDEPENDENT GYMS")
    print("="*100)

    red_leads = [g for g in final_gyms if g['lead_score'] == 'RED']
    yellow_leads = [g for g in final_gyms if g['lead_score'] == 'YELLOW']
    green_leads = [g for g in final_gyms if g['lead_score'] == 'GREEN']
    urgent_leads = [g for g in final_gyms if g['urgency_score'] >= 8]

    print(f"\n🔥 RED LEADS (Hot): {len(red_leads)}")
    print(f"⚡ YELLOW LEADS (Warm): {len(yellow_leads)}")
    print(f"✅ GREEN LEADS (Cold): {len(green_leads)}")
    print(f"🚨 URGENT LEADS (Call Today): {len(urgent_leads)}")

    # Show top urgent leads
    print(f"\n🎯 TOP 15 MOST URGENT LEADS:")
    print("-" * 100)
    for i, gym in enumerate(final_gyms[:15], 1):
        urgency_indicator = "🚨🚨" if gym['urgency_score'] >= 9 else "🚨" if gym['urgency_score'] >= 8 else "⏰"
        print(f"{i:2d}. {urgency_indicator} {gym['business_name']} ({gym['city']}) - Score: {gym['urgency_score']}/10")
        print(f"     💔 {gym['primary_pain']}")
        print(f"     📞 {gym['phone']} | 💰 {gym['estimated_monthly_value']}")
        print(f"     🎯 {gym['follow_up_priority']}")
        print()

    # City breakdown with enhanced metrics
    print(f"\n📊 DETAILED CITY BREAKDOWN:")
    print("-" * 100)
    for summary in city_summaries:
        print(f"{summary['city']:15} | Total: {summary['total_gyms']:2d} | "
              f"RED: {summary['red_leads']:2d} | YELLOW: {summary['yellow_leads']:2d} | "
              f"URGENT: {summary['urgent_leads']:2d} | Avg Urgency: {summary['avg_urgency']:.1f}/10")

    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Main comprehensive CSV
    df = pd.DataFrame(final_gyms)
    csv_file = f"target_gym_leads_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 All leads saved to: {csv_file}")

    # Hot leads priority CSV
    hot_leads_df = pd.DataFrame(red_leads)
    hot_csv = f"hot_target_gyms_{timestamp}.csv"
    hot_leads_df.to_csv(hot_csv, index=False)
    print(f"🔥 Hot leads saved to: {hot_csv}")

    # Urgent action required CSV
    urgent_leads_df = pd.DataFrame(urgent_leads)
    urgent_csv = f"urgent_gym_leads_{timestamp}.csv"
    urgent_leads_df.to_csv(urgent_csv, index=False)
    print(f"🚨 Urgent leads saved to: {urgent_csv}")

    # City summary CSV
    summary_df = pd.DataFrame(city_summaries)
    summary_csv = f"target_cities_summary_{timestamp}.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"📊 City summary saved to: {summary_csv}")

    print(f"\n✅ MISSION COMPLETE!")
    print(f"🎯 Priority targets: {len(urgent_leads)} urgent leads requiring immediate action")
    print(f"🔥 Hot prospects: {len(red_leads)} RED leads with major pain points")
    print(f"💰 Total potential monthly revenue: ${len(red_leads) * 500 + len(yellow_leads) * 300:,}")

    return final_gyms

if __name__ == "__main__":
    gyms = main()