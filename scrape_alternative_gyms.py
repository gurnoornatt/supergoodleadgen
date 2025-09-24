#!/usr/bin/env python3
"""
Alternative gym scraper using diverse search terms to capture fitness businesses
that the main scraper might miss. Creates independent CSV output.
"""

import os
import sys
import time
import requests
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import SerpApiClient

# Target Central Valley cities
TARGET_CITIES = [
    'Bakersfield, CA',
    'Fresno, CA',
    'Stockton, CA',
    'Modesto, CA'
]

# Alternative search terms to find gyms the main scraper might miss
ALTERNATIVE_SEARCH_TERMS = [
    "fitness studio",
    "health club",
    "athletic center",
    "recreation center",
    "wellness center",
    "sports club"
]

# Major chains to exclude (same as main scraper)
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness',
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness',
    'curves', 'pure barre', 'club pilates', 'the bar method', 'solidcore',
    'corepower yoga', 'soulcycle', 'cyclebar', 'barre3', 'burn boot camp',
    'crossfit', 'ufc gym', 'ymca', 'title boxing', 'kickboxing',
    'jazzercise', 'zumba', 'stroller strides'
]

def is_chain_business(business_name):
    """Check if business is a major chain"""
    name_lower = business_name.lower()
    return any(chain in name_lower for chain in MAJOR_CHAINS)

def check_website_status(url):
    """Check if website exists and is accessible"""
    if not url or url == '':
        return False, "No website provided"

    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200, f"HTTP {response.status_code}"
    except requests.exceptions.RequestException as e:
        return False, f"Connection error: {str(e)[:50]}"

def classify_business_type(business_name, types):
    """Classify the type of fitness business"""
    name_lower = business_name.lower()
    types_lower = ' '.join(types).lower() if types else ''

    # Check for specific business types
    if any(term in name_lower or term in types_lower for term in ['yoga', 'pilates']):
        return "Mind-Body Studio"
    elif any(term in name_lower or term in types_lower for term in ['martial arts', 'karate', 'jiu-jitsu', 'boxing', 'mma']):
        return "Martial Arts/Combat Sports"
    elif any(term in name_lower or term in types_lower for term in ['dance', 'ballet', 'studio']):
        return "Dance/Movement Studio"
    elif any(term in name_lower or term in types_lower for term in ['wellness', 'health', 'medical', 'therapy']):
        return "Wellness Center"
    elif any(term in name_lower or term in types_lower for term in ['recreation', 'community', 'athletic center']):
        return "Community Recreation"
    elif any(term in name_lower or term in types_lower for term in ['sports', 'club']):
        return "Sports Club"
    else:
        return "General Fitness"

def assess_lead_quality(business_info):
    """Assess lead quality based on digital presence and characteristics"""
    score = "GREEN"  # Default
    notes = []

    # Website assessment
    if not business_info['website_accessible']:
        score = "RED"
        notes.append("No functional website")

    # Review count assessment
    reviews = business_info.get('reviews', 0)
    if reviews < 25:
        notes.append("Low review count")
        if score == "GREEN":
            score = "YELLOW"
    elif reviews > 100:
        notes.append("High review engagement")

    # Rating assessment
    rating = business_info.get('rating', 0)
    if rating < 4.0 and reviews > 10:
        notes.append("Below average rating")
        if score == "GREEN":
            score = "YELLOW"
    elif rating >= 4.5 and reviews > 20:
        notes.append("Excellent reputation")

    # Business type specific notes
    biz_type = business_info.get('business_type', '')
    if biz_type in ['Mind-Body Studio', 'Martial Arts/Combat Sports']:
        notes.append("Specialized niche market")
    elif biz_type == 'Community Recreation':
        notes.append("Potential large membership base")

    return {
        'lead_quality': score,
        'assessment_notes': '; '.join(notes) if notes else 'Standard assessment'
    }

def scrape_alternative_gyms(city, search_term, serpapi):
    """Scrape gyms using alternative search terms"""
    query = f"{search_term} {city}"
    print(f"   🔍 Searching: {search_term}")

    found_businesses = []

    try:
        results = serpapi.search_google_maps(
            query=query,
            location=city,
            max_results=20  # More results for alternative terms
        )

        if results and 'local_results' in results:
            for place in results['local_results']:
                name = place.get('title', '')

                # Skip major chains
                if is_chain_business(name):
                    continue

                # Extract basic info
                website_url = place.get('link', '')
                website_accessible, website_status = check_website_status(website_url)
                place_types = place.get('type', '').split(' · ') if place.get('type') else []

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
                    'place_types': ' | '.join(place_types),
                    'business_type': classify_business_type(name, place_types),
                    'search_term_found': search_term,
                    'place_id': place.get('place_id', ''),
                    'scraped_timestamp': datetime.now().isoformat()
                }

                # Assess lead quality
                assessment = assess_lead_quality(business_info)
                business_info.update(assessment)

                found_businesses.append(business_info)

                # Show progress
                quality_emoji = "🔥" if assessment['lead_quality'] == "RED" else "⚡" if assessment['lead_quality'] == "YELLOW" else "✅"
                print(f"      {quality_emoji} {name} ({business_info['business_type']}) - {assessment['lead_quality']}")

        time.sleep(1)  # Rate limiting

    except Exception as e:
        print(f"      ❌ Error searching {search_term}: {str(e)}")

    return found_businesses

def main():
    """Main function to run alternative gym scraping"""
    print("\n" + "="*80)
    print("ALTERNATIVE FITNESS BUSINESS SCRAPER")
    print("Using diverse search terms to find missed opportunities")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Cities: {', '.join([city.split(',')[0] for city in TARGET_CITIES])}")
    print(f"Search terms: {', '.join(ALTERNATIVE_SEARCH_TERMS)}")

    # Initialize API client
    serpapi = SerpApiClient()

    all_businesses = []
    city_results = {}

    # Process each city
    for city in TARGET_CITIES:
        print(f"\n🏙️  PROCESSING: {city}")
        print("-" * 60)

        city_businesses = []

        # Try each alternative search term
        for search_term in ALTERNATIVE_SEARCH_TERMS:
            term_results = scrape_alternative_gyms(city, search_term, serpapi)
            city_businesses.extend(term_results)
            time.sleep(0.5)  # Brief pause between searches

        # Remove duplicates within city (by name and phone)
        unique_city_businesses = {}
        for business in city_businesses:
            key = f"{business['business_name']}_{business['phone']}"
            if key not in unique_city_businesses:
                unique_city_businesses[key] = business

        city_unique = list(unique_city_businesses.values())
        all_businesses.extend(city_unique)

        # Track city summary
        red_count = len([b for b in city_unique if b['lead_quality'] == 'RED'])
        yellow_count = len([b for b in city_unique if b['lead_quality'] == 'YELLOW'])
        green_count = len([b for b in city_unique if b['lead_quality'] == 'GREEN'])

        city_results[city] = {
            'total': len(city_unique),
            'red': red_count,
            'yellow': yellow_count,
            'green': green_count
        }

        print(f"   📊 {city.split(',')[0]}: {len(city_unique)} unique businesses found")
        time.sleep(1)  # Pause between cities

    # Remove global duplicates
    final_unique_businesses = {}
    for business in all_businesses:
        key = f"{business['business_name']}_{business['phone']}"
        if key not in final_unique_businesses:
            final_unique_businesses[key] = business

    final_businesses = list(final_unique_businesses.values())

    # Sort by lead quality and reviews
    quality_priority = {'RED': 3, 'YELLOW': 2, 'GREEN': 1}
    final_businesses.sort(
        key=lambda x: (quality_priority[x['lead_quality']], x['reviews']),
        reverse=True
    )

    # Generate summary
    print(f"\n\n{'='*80}")
    print(f"ALTERNATIVE SCRAPER RESULTS: {len(final_businesses)} UNIQUE BUSINESSES")
    print("="*80)

    # Count by quality
    red_leads = [b for b in final_businesses if b['lead_quality'] == 'RED']
    yellow_leads = [b for b in final_businesses if b['lead_quality'] == 'YELLOW']
    green_leads = [b for b in final_businesses if b['lead_quality'] == 'GREEN']

    print(f"\n🔥 HIGH PRIORITY (RED): {len(red_leads)}")
    print(f"⚡ MEDIUM PRIORITY (YELLOW): {len(yellow_leads)}")
    print(f"✅ LOW PRIORITY (GREEN): {len(green_leads)}")

    # Count by business type
    type_counts = {}
    for business in final_businesses:
        biz_type = business['business_type']
        type_counts[biz_type] = type_counts.get(biz_type, 0) + 1

    print(f"\n📊 BUSINESS TYPE BREAKDOWN:")
    for biz_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"   {biz_type}: {count}")

    # Show top prospects
    print(f"\n🎯 TOP 10 PROSPECTS:")
    for i, business in enumerate(final_businesses[:10], 1):
        print(f"{i}. {business['business_name']} ({business['city']})")
        print(f"   📍 Type: {business['business_type']}")
        print(f"   🎯 Quality: {business['lead_quality']} - {business['assessment_notes']}")
        print(f"   📞 {business['phone']}")
        print()

    # City breakdown
    print(f"\n🏙️  CITY BREAKDOWN:")
    for city, stats in city_results.items():
        city_name = city.split(',')[0]
        print(f"   {city_name}: {stats['total']} ({stats['red']} RED, {stats['yellow']} YELLOW, {stats['green']} GREEN)")

    # Save to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"alternative_fitness_businesses_{timestamp}.csv"

    df = pd.DataFrame(final_businesses)
    df.to_csv(csv_filename, index=False)

    print(f"\n💾 Results saved to: {csv_filename}")
    print(f"✅ Alternative scraper complete: {len(final_businesses)} businesses found using diverse search terms")

    return final_businesses

if __name__ == "__main__":
    businesses = main()