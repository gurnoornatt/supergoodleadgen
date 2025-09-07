#!/usr/bin/env python3
"""
Scrape real independent gyms in Bakersfield, CA
Filters out major chains and focuses on small/private gyms
"""

import os
import sys
import json
import time
from datetime import datetime
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import SerpApiClient
from config import Config

# Major chains to exclude
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness', 
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness',
    'curves', 'pure barre', 'club pilates', 'the bar method', 'solidcore',
    'corepower yoga', 'soulcycle', 'cyclebar', 'barre3', 'burn boot camp'
]

def is_chain_gym(business_name):
    """Check if gym is a major chain"""
    name_lower = business_name.lower()
    return any(chain in name_lower for chain in MAJOR_CHAINS)

def scrape_bakersfield_gyms():
    """Scrape gyms in Bakersfield, filtering for independent gyms"""
    
    print("\n" + "="*80)
    print("SEARCHING FOR INDEPENDENT GYMS IN BAKERSFIELD, CA")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize API client
    serpapi = SerpApiClient()
    
    # Search queries for different gym types
    search_queries = [
        "gym fitness center Bakersfield CA",
        "crossfit box Bakersfield CA", 
        "martial arts dojo Bakersfield CA",
        "boxing club Bakersfield CA",
        "personal training studio Bakersfield CA",
        "powerlifting gym Bakersfield CA",
        "yoga studio Bakersfield CA",
        "strength training gym Bakersfield CA"
    ]
    
    all_gyms = []
    
    for query in search_queries:
        print(f"\n🔍 Searching: {query}")
        
        try:
            # Search with SerpApi
            results = serpapi.search_google_maps(
                query=query,
                location="Bakersfield, CA",
                max_results=20
            )
            
            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')
                    
                    # Skip chains
                    if is_chain_gym(name):
                        print(f"   ⛔ Skipping chain: {name}")
                        continue
                    
                    # Extract gym info
                    gym_info = {
                        'business_name': name,
                        'address': place.get('address', ''),
                        'phone': place.get('phone', ''),
                        'website': place.get('link', ''),
                        'rating': place.get('rating', 0),
                        'reviews': place.get('reviews', 0),
                        'type': place.get('type', ''),
                        'place_id': place.get('place_id', ''),
                        'position': place.get('position', 0),
                        'query': query,
                        'scraped_at': datetime.now().isoformat()
                    }
                    
                    # Check for indicators of independent gyms
                    independent_indicators = [
                        'owner' in name.lower(),
                        'family' in name.lower(),
                        'local' in name.lower(),
                        gym_info['reviews'] < 500,  # Chains typically have more reviews
                        not any(franchise in name.lower() for franchise in ['franchise', 'llc', 'inc', 'corp'])
                    ]
                    
                    gym_info['independent_score'] = sum(independent_indicators)
                    
                    # Only add if likely independent
                    if gym_info['independent_score'] >= 1:
                        all_gyms.append(gym_info)
                        print(f"   ✅ Found: {name} (Score: {gym_info['independent_score']}/5)")
                    else:
                        print(f"   ⚠️  Possible chain: {name}")
                        
            time.sleep(2)  # Rate limiting
            
        except Exception as e:
            print(f"   ❌ Error searching '{query}': {str(e)}")
            continue
    
    # Remove duplicates based on name
    unique_gyms = {}
    for gym in all_gyms:
        name = gym['business_name']
        if name not in unique_gyms or gym['independent_score'] > unique_gyms[name]['independent_score']:
            unique_gyms[name] = gym
    
    independent_gyms = list(unique_gyms.values())
    
    # Sort by independent score and reviews
    independent_gyms.sort(key=lambda x: (x['independent_score'], x['reviews']), reverse=True)
    
    print(f"\n\n{'='*80}")
    print(f"FOUND {len(independent_gyms)} INDEPENDENT GYMS IN BAKERSFIELD")
    print(f"{'='*80}\n")
    
    # Display results
    for i, gym in enumerate(independent_gyms[:20], 1):  # Top 20
        print(f"{i}. {gym['business_name']}")
        print(f"   📍 {gym['address']}")
        print(f"   📞 {gym['phone']}")
        print(f"   🌐 {gym['website'] or 'No website'}")
        print(f"   ⭐ {gym['rating']} ({gym['reviews']} reviews)")
        print(f"   🏆 Independence Score: {gym['independent_score']}/5")
        print()
    
    # Save to CSV
    df = pd.DataFrame(independent_gyms)
    output_file = f"bakersfield_independent_gyms_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(output_file, index=False)
    print(f"💾 Results saved to: {output_file}")
    
    # Save to JSON for processing
    json_file = f"bakersfield_gyms_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_file, 'w') as f:
        json.dump(independent_gyms, f, indent=2)
    print(f"💾 JSON data saved to: {json_file}")
    
    return independent_gyms

if __name__ == "__main__":
    gyms = scrape_bakersfield_gyms()