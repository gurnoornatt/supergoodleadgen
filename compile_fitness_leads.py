#!/usr/bin/env python3
"""
Fitness-Focused Lead Compiler for Cold Email Campaigns
Analyzes all CSV files to compile the best 200 weightlifting/fitness-focused leads
Prioritizes general fitness, powerlifting, and strength training over combat sports
Optimizes data structure for cold email campaigns
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

def categorize_business_type(business_name, business_type, place_types):
    """Categorize business for fitness focus scoring"""
    name_lower = business_name.lower()
    type_lower = str(business_type).lower() if business_type else ""

    # Combat sports (lower priority for this campaign)
    combat_keywords = [
        'boxing', 'bjj', 'jiu-jitsu', 'jujitsu', 'martial arts', 'karate',
        'taekwondo', 'tae kwon do', 'kickboxing', 'muay thai', 'mma',
        'mixed martial', 'aikido', 'krav maga', 'fighting', 'self defense',
        'dojo', 'academy', 'kung fu'
    ]

    # High-priority fitness keywords
    fitness_keywords = [
        'gym', 'fitness', 'powerlifting', 'strength', 'weight', 'barbell',
        'iron', 'muscle', 'body', 'training center', 'athletic', 'performance',
        'conditioning', 'crossfit', 'bootcamp', 'transformation'
    ]

    # Specialized fitness (medium priority)
    specialized_keywords = [
        'yoga', 'pilates', 'barre', 'cycling', 'spin', 'dance', 'zumba',
        'hot yoga', 'wellness', 'health club', 'recreation'
    ]

    # Check for combat sports (lowest priority)
    if any(keyword in name_lower for keyword in combat_keywords):
        return 'combat_sports', 1.0

    # Check for high-priority fitness
    if any(keyword in name_lower for keyword in fitness_keywords):
        return 'fitness_focused', 4.0

    # Check for specialized fitness
    if any(keyword in name_lower for keyword in specialized_keywords):
        return 'specialized_fitness', 2.5

    # Default fitness category
    return 'general_fitness', 3.0

def calculate_cold_email_score(row):
    """Calculate cold email suitability score"""
    score = 0

    # Business type priority (40% of score)
    category, type_multiplier = categorize_business_type(
        row.get('business_name', ''),
        row.get('type', ''),
        row.get('place_types', '')
    )
    score += type_multiplier * 10

    # Review count importance (30% of score)
    reviews = row.get('reviews', 0)
    if reviews >= 200:
        score += 30
    elif reviews >= 100:
        score += 25
    elif reviews >= 50:
        score += 20
    elif reviews >= 20:
        score += 15
    elif reviews >= 10:
        score += 10
    else:
        score += 5

    # Rating quality (20% of score)
    rating = row.get('rating', 0)
    if rating >= 4.5:
        score += 20
    elif rating >= 4.0:
        score += 15
    elif rating >= 3.5:
        score += 10
    else:
        score += 5

    # Contact info completeness (10% of score)
    if pd.notna(row.get('phone', '')) and row.get('phone', '') != '':
        score += 5
    if pd.notna(row.get('address', '')) and row.get('address', '') != '':
        score += 5

    return score, category

def generate_cold_email_subject(business_name, pain_point):
    """Generate personalized cold email subject lines"""
    subjects = [
        f"Quick question about {business_name}'s online presence",
        f"Helping {business_name} capture more local leads",
        f"5-minute solution for {business_name}",
        f"{business_name} - Missing 20+ new members monthly?",
        f"Your competitors are stealing {business_name}'s Google traffic"
    ]

    # Customize based on pain point
    pain_str = str(pain_point).lower() if pd.notna(pain_point) else ""
    if 'digital presence' in pain_str:
        return subjects[4]  # Competitor stealing traffic
    elif 'review' in pain_str:
        return subjects[3]  # Missing members
    else:
        return subjects[0]  # Generic question

def generate_cold_email_hook(row):
    """Generate personalized cold email opening hook"""
    name = row['business_name']
    city = row['city']
    reviews = row.get('reviews', 0)
    rating = row.get('rating', 0)

    hooks = []

    # Social proof hook
    if reviews >= 100 and rating >= 4.0:
        hooks.append(f"I noticed {name} has {reviews} reviews with a {rating}★ rating - clearly you're doing something right in {city}!")

    # Local angle hook
    hooks.append(f"I was researching fitness businesses in {city} and {name} caught my attention.")

    # Problem identification hook
    if row.get('lead_score', '') == 'RED':
        hooks.append(f"Quick question - is {name} getting as many new members from Google as you'd like?")

    return hooks[0] if hooks else f"Hi there! I came across {name} and wanted to reach out."

def extract_owner_info(business_name):
    """Extract potential owner/manager info from business name"""
    # Look for personal names in business names
    personal_indicators = [
        r"(\w+)'s", r"(\w+) boxing", r"(\w+) martial", r"(\w+) fitness",
        r"(\w+) gym", r"(\w+) athletics", r"(\w+) training"
    ]

    for pattern in personal_indicators:
        match = re.search(pattern, business_name, re.IGNORECASE)
        if match:
            return match.group(1).title()

    return "Owner"  # Default fallback

def compile_fitness_leads():
    """Main function to compile fitness-focused leads"""

    print("🏋️  FITNESS LEAD COMPILATION ENGINE")
    print("=" * 60)

    all_leads = []

    # Load all CSV files with leads
    files_to_process = [
        ('central_valley_gym_leads_20250916_214958.csv', 'main_gyms'),
        ('alternative_fitness_businesses_20250916_215141.csv', 'alternative_fitness'),
        ('supplemental_gym_leads_20250916_220051.csv', 'supplemental_gyms')
    ]

    for file_path, source in files_to_process:
        try:
            print(f"📂 Loading {file_path}...")
            df = pd.read_csv(file_path)
            df['data_source'] = source
            all_leads.append(df)
            print(f"   ✅ Loaded {len(df)} leads from {source}")
        except FileNotFoundError:
            print(f"   ⚠️  File not found: {file_path}")
            continue

    if not all_leads:
        print("❌ No data files found!")
        return

    # Combine all leads
    print("\n🔄 Combining and processing leads...")
    combined_df = pd.concat(all_leads, ignore_index=True, sort=False)
    print(f"📊 Total combined leads: {len(combined_df)}")

    # Remove duplicates based on business name and phone
    print("🧹 Removing duplicates...")
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset=['business_name', 'phone'], keep='first')
    after_dedup = len(combined_df)
    print(f"   Removed {before_dedup - after_dedup} duplicates")

    # Calculate cold email scores and categorize
    print("📈 Calculating fitness focus scores...")
    scores_and_categories = combined_df.apply(calculate_cold_email_score, axis=1)
    combined_df['cold_email_score'] = [score for score, category in scores_and_categories]
    combined_df['business_category'] = [category for score, category in scores_and_categories]

    # Filter for fitness-focused businesses (exclude combat sports)
    print("🎯 Filtering for fitness-focused businesses...")
    fitness_focused = combined_df[combined_df['business_category'] != 'combat_sports'].copy()
    print(f"   Fitness-focused leads: {len(fitness_focused)}")
    print(f"   Excluded combat sports: {len(combined_df) - len(fitness_focused)}")

    # Sort by cold email score and select top 200
    print("🏆 Selecting top 200 leads...")
    top_leads = fitness_focused.nlargest(200, 'cold_email_score').copy()

    # Generate cold email fields
    print("✉️  Generating cold email content...")
    top_leads['email_subject'] = top_leads.apply(
        lambda row: generate_cold_email_subject(row['business_name'], row.get('primary_pain', '')), axis=1
    )
    top_leads['email_hook'] = top_leads.apply(generate_cold_email_hook, axis=1)
    top_leads['likely_owner'] = top_leads['business_name'].apply(extract_owner_info)

    # Add cold email specific fields
    top_leads['follow_up_timing'] = top_leads['business_category'].map({
        'fitness_focused': '3 days',
        'general_fitness': '5 days',
        'specialized_fitness': '7 days'
    })

    top_leads['email_priority'] = top_leads['cold_email_score'].apply(
        lambda x: 'High' if x >= 60 else 'Medium' if x >= 40 else 'Low'
    )

    # Create cold email optimized output
    cold_email_columns = [
        'business_name', 'likely_owner', 'city', 'address', 'phone',
        'rating', 'reviews', 'business_category', 'cold_email_score',
        'email_priority', 'email_subject', 'email_hook', 'follow_up_timing',
        'primary_pain', 'estimated_monthly_value', 'data_source'
    ]

    # Ensure all columns exist
    for col in cold_email_columns:
        if col not in top_leads.columns:
            top_leads[col] = 'N/A'

    output_df = top_leads[cold_email_columns].copy()

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"top_200_fitness_leads_cold_email_{timestamp}.csv"
    output_df.to_csv(output_file, index=False)

    # Generate summary
    print(f"\n🎯 COMPILATION COMPLETE!")
    print("=" * 60)
    print(f"📧 Cold email leads saved to: {output_file}")
    print(f"📊 Total leads compiled: {len(output_df)}")

    print(f"\n📈 BUSINESS CATEGORY BREAKDOWN:")
    category_counts = output_df['business_category'].value_counts()
    for category, count in category_counts.items():
        avg_score = output_df[output_df['business_category'] == category]['cold_email_score'].mean()
        print(f"   {category}: {count} leads (avg score: {avg_score:.1f})")

    print(f"\n🏙️  CITY DISTRIBUTION:")
    city_counts = output_df['city'].value_counts().head(10)
    for city, count in city_counts.items():
        print(f"   {city}: {count} leads")

    print(f"\n⚡ PRIORITY BREAKDOWN:")
    priority_counts = output_df['email_priority'].value_counts()
    for priority, count in priority_counts.items():
        print(f"   {priority}: {count} leads")

    print(f"\n💰 REVENUE POTENTIAL:")
    high_value = len(output_df[output_df['estimated_monthly_value'].str.contains('400|500|600|700|800|900', na=False)])
    medium_value = len(output_df[output_df['estimated_monthly_value'].str.contains('297|397', na=False)])
    print(f"   High value (>$400/month): {high_value} leads")
    print(f"   Medium value ($297-397/month): {medium_value} leads")

    # Show top 10 leads
    print(f"\n🥇 TOP 10 COLD EMAIL PROSPECTS:")
    for i, row in output_df.head(10).iterrows():
        print(f"   {i+1}. {row['business_name']} ({row['city']}) - Score: {row['cold_email_score']:.1f} - {row['business_category']}")

    return output_df

if __name__ == "__main__":
    leads_df = compile_fitness_leads()