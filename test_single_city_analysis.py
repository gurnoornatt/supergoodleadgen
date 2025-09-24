#!/usr/bin/env python3
"""
Test version: Focus on one city to validate the YELLOW lead analysis approach
"""

import os
import sys
import json
import time
import requests
from datetime import datetime
import pandas as pd
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import SerpApiClient, GooglePageSpeedClient, BuiltWithClient
from config import Config

# Test with just Fresno
TEST_CITY = 'Fresno, CA'

# Major chains to exclude
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness',
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness'
]

# Focus on queries that typically have websites
SEARCH_QUERIES = [
    "gym fitness center {city}",
    "crossfit box {city}",
    "personal training studio {city}",
    "yoga studio {city}"
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
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200, f"Status: {response.status_code}"
    except:
        return False, "Website inaccessible"

def main():
    """Test analysis on Fresno gyms only"""
    print("\n" + "="*60)
    print("TESTING YELLOW LEAD ANALYSIS - FRESNO ONLY")
    print("="*60)

    # Initialize API clients
    serpapi = SerpApiClient()
    pagespeed_client = GooglePageSpeedClient()

    all_gyms = []

    print(f"\n🏙️  ANALYZING GYMS IN: {TEST_CITY}")
    print("-" * 50)

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=TEST_CITY)
        print(f"\n🔍 {query}")

        try:
            results = serpapi.search_google_maps(
                query=query,
                location=TEST_CITY,
                max_results=8  # Small number for testing
            )

            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')

                    # Skip chains and duplicates
                    if is_chain_gym(name):
                        print(f"   ⏭️  Skipping chain: {name}")
                        continue

                    if any(gym['business_name'] == name for gym in all_gyms):
                        print(f"   ⏭️  Duplicate: {name}")
                        continue

                    # Extract gym info
                    website_url = place.get('link', '')
                    website_accessible, website_status = check_website_exists(website_url)

                    gym_info = {
                        'business_name': name,
                        'city': TEST_CITY.split(',')[0],
                        'website': website_url,
                        'website_accessible': website_accessible,
                        'phone': place.get('phone', ''),
                        'rating': place.get('rating', 0),
                        'reviews': place.get('reviews', 0)
                    }

                    print(f"   📋 {name}")
                    print(f"      🌐 Website: {website_url if website_url else 'None'}")
                    print(f"      ✅ Accessible: {website_accessible}")

                    # Only analyze websites that exist
                    if website_accessible and website_url:
                        print(f"      📱 Analyzing mobile performance...")

                        try:
                            mobile_result = pagespeed_client.analyze_url(website_url, strategy="mobile")
                            mobile_score = mobile_result.get('performance_score', 0)

                            gym_info['mobile_score'] = mobile_score

                            # Determine lead category
                            if mobile_score < 50:
                                lead_type = "🔥 RED - Poor Mobile"
                                gym_info['lead_score'] = 'RED'
                                gym_info['primary_pain'] = f"Website broken on mobile ({mobile_score}/100)"
                            elif mobile_score < 70:
                                lead_type = "⚡ YELLOW - Needs Optimization"
                                gym_info['lead_score'] = 'YELLOW'
                                gym_info['primary_pain'] = f"Mobile performance issues ({mobile_score}/100)"
                            else:
                                lead_type = "✅ GREEN - Good Performance"
                                gym_info['lead_score'] = 'GREEN'
                                gym_info['primary_pain'] = f"Good mobile performance ({mobile_score}/100)"

                            print(f"      📊 Mobile Score: {mobile_score}/100")
                            print(f"      🎯 Classification: {lead_type}")

                        except Exception as e:
                            print(f"      ❌ PageSpeed Error: {str(e)}")
                            gym_info['mobile_score'] = 0
                            gym_info['lead_score'] = 'RED'
                            gym_info['primary_pain'] = "Website analysis failed"

                        # Add delay between API calls
                        time.sleep(3)

                    else:
                        print(f"      🔥 RED - No functional website")
                        gym_info['mobile_score'] = 0
                        gym_info['lead_score'] = 'RED'
                        gym_info['primary_pain'] = "No functional website"

                    all_gyms.append(gym_info)
                    print()

        except Exception as e:
            print(f"❌ Error with query: {str(e)}")

        time.sleep(2)  # Rate limiting between queries

    # Summary
    print(f"\n{'='*60}")
    print("ANALYSIS SUMMARY")
    print("="*60)

    red_leads = [g for g in all_gyms if g.get('lead_score') == 'RED']
    yellow_leads = [g for g in all_gyms if g.get('lead_score') == 'YELLOW']
    green_leads = [g for g in all_gyms if g.get('lead_score') == 'GREEN']

    print(f"Total Gyms Analyzed: {len(all_gyms)}")
    print(f"🔥 RED Leads: {len(red_leads)}")
    print(f"⚡ YELLOW Leads: {len(yellow_leads)}")
    print(f"✅ GREEN Leads: {len(green_leads)}")

    # Show YELLOW leads with details
    if yellow_leads:
        print(f"\n⚡ YELLOW LEADS - UPGRADE OPPORTUNITIES:")
        for i, gym in enumerate(yellow_leads, 1):
            mobile_score = gym.get('mobile_score', 0)
            print(f"{i}. {gym['business_name']}")
            print(f"   📱 Mobile Score: {mobile_score}/100")
            print(f"   🌐 Website: {gym['website']}")
            print(f"   📞 Phone: {gym.get('phone', 'N/A')}")
            print(f"   ⭐ Rating: {gym.get('rating', 0)} ({gym.get('reviews', 0)} reviews)")
            print()

    # Save test results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.DataFrame(all_gyms)
    csv_file = f"fresno_gym_test_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"💾 Test results saved to: {csv_file}")

    return all_gyms

if __name__ == "__main__":
    gyms = main()