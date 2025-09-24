#!/usr/bin/env python3
"""
Cross-reference gym data to find gaps, new gyms, and calculate market penetration
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

# Target cities for analysis
TARGET_CITIES = ['Manteca', 'Lodi', 'Clovis', 'Madera', 'Hanford', 'Porterville']

def load_agent1_data():
    """Load Agent 1's comprehensive Central Valley data"""
    try:
        df = pd.read_csv('central_valley_gym_leads_20250916_214958.csv')
        print(f"✅ Loaded Agent 1 data: {len(df)} total gyms")

        # Filter for target cities
        target_df = df[df['city'].isin(TARGET_CITIES)].copy()
        print(f"📍 Found {len(target_df)} gyms in target cities from Agent 1")

        return df, target_df
    except FileNotFoundError:
        print("❌ Agent 1 data file not found")
        return pd.DataFrame(), pd.DataFrame()

def load_our_target_data():
    """Load our target city scraping results"""
    # Look for our target city files
    import glob

    our_files = []
    for pattern in ['*target*gym*.csv', '*manteca*.csv', '*lodi*.csv', '*clovis*.csv',
                   '*madera*.csv', '*hanford*.csv', '*porterville*.csv', '*progress*.csv']:
        our_files.extend(glob.glob(pattern))

    if not our_files:
        print("❌ No target city files found from our scraping")
        return pd.DataFrame()

    print(f"📂 Found {len(our_files)} files from our scraping:")
    for file in our_files:
        print(f"   - {file}")

    # Load and combine all our data
    all_data = []
    for file in our_files:
        try:
            df = pd.read_csv(file)
            df['source_file'] = file
            all_data.append(df)
            print(f"   ✅ Loaded {len(df)} gyms from {file}")
        except Exception as e:
            print(f"   ❌ Error loading {file}: {e}")

    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        print(f"📊 Combined our data: {len(combined_df)} total entries")
        return combined_df
    else:
        return pd.DataFrame()

def normalize_gym_name(name):
    """Normalize gym names for comparison"""
    if pd.isna(name):
        return ""

    # Convert to lowercase and remove common variations
    normalized = str(name).lower().strip()

    # Remove common suffixes/prefixes
    suffixes_to_remove = [
        'gym', 'fitness', 'center', 'club', 'studio', 'academy', 'training',
        'llc', 'inc', 'ltd', 'corp', '&', 'and', 'the'
    ]

    for suffix in suffixes_to_remove:
        normalized = re.sub(f'\\b{suffix}\\b', '', normalized)

    # Remove extra spaces and special characters
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()

    return normalized

def normalize_phone(phone):
    """Normalize phone numbers for comparison"""
    if pd.isna(phone):
        return ""

    # Extract just digits
    digits_only = re.sub(r'\D', '', str(phone))

    # Return last 10 digits if longer (remove country code)
    if len(digits_only) > 10:
        return digits_only[-10:]

    return digits_only

def find_missing_gyms(agent1_data, our_data):
    """Find gyms that Agent 1 missed in target cities"""

    if our_data.empty:
        print("❌ No our data to compare")
        return pd.DataFrame()

    # Filter our data for target cities
    our_target = our_data[our_data['city'].isin(TARGET_CITIES)].copy()

    # Normalize names and phones for comparison
    agent1_data['normalized_name'] = agent1_data['business_name'].apply(normalize_gym_name)
    agent1_data['normalized_phone'] = agent1_data['phone'].apply(normalize_phone)

    our_target['normalized_name'] = our_target['business_name'].apply(normalize_gym_name)
    our_target['normalized_phone'] = our_target['phone'].apply(normalize_phone)

    # Create comparison keys
    agent1_keys = set()
    for _, row in agent1_data.iterrows():
        # Multiple matching strategies
        if row['normalized_name']:
            agent1_keys.add(f"{row['city']}_{row['normalized_name']}")
        if row['normalized_phone']:
            agent1_keys.add(f"{row['city']}_{row['normalized_phone']}")

    # Find gyms in our data that aren't in Agent 1's data
    missing_gyms = []

    for _, row in our_target.iterrows():
        city = row['city']
        name_key = f"{city}_{row['normalized_name']}" if row['normalized_name'] else None
        phone_key = f"{city}_{row['normalized_phone']}" if row['normalized_phone'] else None

        # Check if this gym is missing from Agent 1's data
        found_match = False

        if name_key and name_key in agent1_keys:
            found_match = True
        if phone_key and phone_key in agent1_keys:
            found_match = True

        if not found_match:
            # This is a gym Agent 1 missed
            missing_gyms.append(row)

    if missing_gyms:
        missing_df = pd.DataFrame(missing_gyms)
        print(f"🔍 Found {len(missing_df)} gyms that Agent 1 missed")
        return missing_df
    else:
        print("✅ No missing gyms found - Agent 1 captured everything")
        return pd.DataFrame()

def identify_recent_gyms(gym_data):
    """Identify potentially recently opened gyms based on review count and dates"""

    if gym_data.empty:
        return pd.DataFrame()

    # Criteria for "recently opened":
    # 1. Low review count (< 50)
    # 2. Recent scraping date
    # 3. Good rating despite low reviews (suggests new but quality)

    recent_criteria = (
        (gym_data['reviews'] < 50) &
        (gym_data['reviews'] > 5) &  # Not too new (has some reviews)
        (gym_data['rating'] >= 4.0)  # Good quality despite being new
    )

    recent_gyms = gym_data[recent_criteria].copy()
    recent_gyms['likely_new_reason'] = 'Low review count with high rating suggests recent opening'

    print(f"🆕 Identified {len(recent_gyms)} potentially recently opened gyms")

    return recent_gyms

def calculate_market_penetration():
    """Calculate estimated market penetration per city"""

    # Estimated total fitness businesses per city (based on population and demographics)
    city_estimates = {
        'Manteca': {'population': 87000, 'estimated_fitness_businesses': 25},
        'Lodi': {'population': 68000, 'estimated_fitness_businesses': 20},
        'Clovis': {'population': 120000, 'estimated_fitness_businesses': 35},
        'Madera': {'population': 66000, 'estimated_fitness_businesses': 18},
        'Hanford': {'population': 57000, 'estimated_fitness_businesses': 15},
        'Porterville': {'population': 62000, 'estimated_fitness_businesses': 16}
    }

    return city_estimates

def analyze_data():
    """Main analysis function"""
    print("\n" + "="*80)
    print("GYM DATA CROSS-REFERENCE ANALYSIS")
    print("="*80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Load data
    print("\n📊 LOADING DATA...")
    agent1_all, agent1_target = load_agent1_data()
    our_data = load_our_target_data()

    if agent1_all.empty:
        print("❌ Cannot proceed without Agent 1 data")
        return

    # Analyze each target city
    print(f"\n🏙️ CITY-BY-CITY ANALYSIS...")
    print("-" * 60)

    city_estimates = calculate_market_penetration()
    results = []
    all_missing = []
    all_recent = []

    for city in TARGET_CITIES:
        print(f"\n📍 {city.upper()}")

        # Agent 1 data for this city
        agent1_city = agent1_target[agent1_target['city'] == city]

        # Our data for this city
        our_city = our_data[our_data['city'] == city] if not our_data.empty else pd.DataFrame()

        # Find missing gyms
        missing = find_missing_gyms(agent1_city, our_city)
        if not missing.empty:
            missing['analysis_type'] = 'Agent1_missed'
            all_missing.append(missing)

        # Find recent gyms from combined data
        combined_city = pd.concat([agent1_city, our_city], ignore_index=True) if not our_city.empty else agent1_city
        if not combined_city.empty:
            # Remove duplicates
            combined_city = combined_city.drop_duplicates(subset=['business_name'], keep='first')

            recent = identify_recent_gyms(combined_city)
            if not recent.empty:
                recent['analysis_type'] = 'Recently_opened'
                all_recent.append(recent)

        # Calculate penetration
        total_found = len(combined_city) if not combined_city.empty else len(agent1_city)
        estimated_total = city_estimates[city]['estimated_fitness_businesses']
        penetration = (total_found / estimated_total) * 100

        results.append({
            'city': city,
            'population': city_estimates[city]['population'],
            'agent1_gyms': len(agent1_city),
            'our_additional_gyms': len(our_city),
            'total_found': total_found,
            'estimated_total_market': estimated_total,
            'market_penetration_pct': round(penetration, 1),
            'missing_gyms_found': len(missing) if not missing.empty else 0,
            'recent_gyms_identified': len(recent) if not recent.empty else 0
        })

        print(f"   Agent 1 found: {len(agent1_city)} gyms")
        print(f"   Our additional: {len(our_city)} gyms")
        print(f"   Total discovered: {total_found} gyms")
        print(f"   Market penetration: {round(penetration, 1)}% of estimated {estimated_total} total")
        print(f"   Missing gyms found: {len(missing) if not missing.empty else 0}")
        print(f"   Recent gyms: {len(recent) if not recent.empty else 0}")

    # Create supplemental leads file
    print(f"\n📄 CREATING SUPPLEMENTAL LEADS FILE...")

    supplemental_gyms = []

    # Add all missing gyms
    if all_missing:
        missing_df = pd.concat(all_missing, ignore_index=True)
        supplemental_gyms.append(missing_df)
        print(f"   Added {len(missing_df)} gyms Agent 1 missed")

    # Add recent gyms
    if all_recent:
        recent_df = pd.concat(all_recent, ignore_index=True)
        supplemental_gyms.append(recent_df)
        print(f"   Added {len(recent_df)} recently opened gyms")

    # Create final supplemental file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if supplemental_gyms:
        supplemental_df = pd.concat(supplemental_gyms, ignore_index=True)

        # Remove duplicates
        supplemental_df = supplemental_df.drop_duplicates(subset=['business_name', 'city'], keep='first')

        # Sort by urgency and lead score
        if 'urgency_score' in supplemental_df.columns:
            supplemental_df = supplemental_df.sort_values(['urgency_score', 'lead_score'], ascending=[False, True])

        supp_file = f"supplemental_gym_leads_{timestamp}.csv"
        supplemental_df.to_csv(supp_file, index=False)
        print(f"   💾 Saved {len(supplemental_df)} supplemental leads to: {supp_file}")
    else:
        print("   ℹ️  No supplemental leads to save")

    # Save market analysis
    market_df = pd.DataFrame(results)
    market_file = f"market_penetration_analysis_{timestamp}.csv"
    market_df.to_csv(market_file, index=False)
    print(f"   💾 Saved market analysis to: {market_file}")

    # Print summary
    print(f"\n📊 FINAL SUMMARY")
    print("-" * 60)

    total_agent1 = sum(r['agent1_gyms'] for r in results)
    total_additional = sum(r['our_additional_gyms'] for r in results)
    total_found = sum(r['total_found'] for r in results)
    avg_penetration = sum(r['market_penetration_pct'] for r in results) / len(results)

    print(f"Agent 1 found: {total_agent1} gyms in target cities")
    print(f"Our additional: {total_additional} gyms")
    print(f"Total discovered: {total_found} gyms")
    print(f"Average market penetration: {avg_penetration:.1f}%")

    if supplemental_gyms:
        print(f"Supplemental leads created: {len(pd.concat(supplemental_gyms, ignore_index=True))} gyms")

    print(f"\n✅ Analysis complete!")

    return results

if __name__ == "__main__":
    results = analyze_data()