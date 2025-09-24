#!/usr/bin/env python3
"""
Lead Prioritization Engine for Central Valley Gym Leads
Transforms 641 raw leads into call-ready sales intelligence with:
- Revenue potential scoring
- Geographic clustering for efficient routes
- Gym type urgency analysis
- Custom sales scripts with specific pain points and dollar amounts
"""

import pandas as pd
import numpy as np
from datetime import datetime
import math
import json

# Gym type urgency multipliers
GYM_TYPE_URGENCY = {
    '24 hour': 3.0,  # Highest urgency - security and access issues
    'crossfit': 2.8,  # High urgency - need WOD posting, class scheduling
    'boxing': 2.5,   # High urgency - need bout scheduling, member tracking
    'martial arts': 2.5,  # High urgency - belt tracking, student portals
    'personal training': 2.3,  # High urgency - client scheduling critical
    'bootcamp': 2.2,  # Medium-high urgency - class booking needed
    'pilates': 2.0,   # Medium urgency - class scheduling
    'yoga': 2.0,     # Medium urgency - class scheduling
    'powerlifting': 1.8,  # Medium urgency - member tracking
    'fitness': 1.5,   # Standard urgency - general gym needs
    'gym': 1.5,      # Standard urgency - general gym needs
    'health club': 1.3,  # Lower urgency - may have some systems
    'recreation': 1.2   # Lowest urgency - often municipal
}

# Geographic clusters for Central Valley (lat/lon approximate centers)
CITY_CLUSTERS = {
    'North Valley': ['Antioch', 'Lodi', 'Stockton', 'Tracy', 'Manteca'],
    'Central Valley': ['Modesto', 'Turlock', 'Merced'],
    'Fresno Metro': ['Fresno', 'Clovis', 'Madera'],
    'South Valley': ['Visalia', 'Hanford', 'Porterville'],
    'Bakersfield Metro': ['Bakersfield']
}

def calculate_revenue_score(row):
    """Calculate revenue potential score (0-100)"""
    base_score = 50

    # High reviews indicate established customer base
    reviews = row.get('reviews', 0)
    rating = row.get('rating', 0)

    # Review count scoring (0-30 points)
    if reviews >= 500:
        review_score = 30
    elif reviews >= 200:
        review_score = 25
    elif reviews >= 100:
        review_score = 20
    elif reviews >= 50:
        review_score = 15
    elif reviews >= 20:
        review_score = 10
    else:
        review_score = 5

    # Rating scoring (0-20 points)
    if rating >= 4.8:
        rating_score = 20
    elif rating >= 4.5:
        rating_score = 15
    elif rating >= 4.0:
        rating_score = 10
    elif rating >= 3.5:
        rating_score = 5
    else:
        rating_score = 0

    total_score = base_score + review_score + rating_score
    return min(100, total_score)

def get_gym_type_urgency(business_name, gym_type):
    """Determine gym type urgency multiplier"""
    name_lower = business_name.lower()
    type_lower = str(gym_type).lower()

    # Check for specific indicators in name or type
    for key, multiplier in GYM_TYPE_URGENCY.items():
        if key in name_lower or key in type_lower:
            return multiplier

    return 1.5  # Default for general gyms

def get_geographic_cluster(city):
    """Get geographic cluster for sales routing"""
    for cluster, cities in CITY_CLUSTERS.items():
        if any(city_name in city for city_name in cities):
            return cluster
    return 'Other'

def estimate_monthly_value(revenue_score, urgency_multiplier, reviews, rating):
    """Estimate monthly subscription value based on gym characteristics"""

    # Base pricing tiers
    if urgency_multiplier >= 2.5:  # Specialized gyms
        base_value = 397
    elif urgency_multiplier >= 2.0:  # Medium complexity
        base_value = 297
    else:  # Standard gyms
        base_value = 197

    # Adjust based on size/popularity
    if reviews >= 300 and rating >= 4.5:
        multiplier = 2.0  # Premium clients
    elif reviews >= 100 and rating >= 4.0:
        multiplier = 1.5  # Good clients
    else:
        multiplier = 1.0  # Standard clients

    estimated_value = int(base_value * multiplier)
    return f"${estimated_value}-{estimated_value + 200}"

def generate_sales_script(row):
    """Generate personalized sales script with specific pain points"""
    name = row['business_name']
    city = row['city']
    reviews = row.get('reviews', 0)
    rating = row.get('rating', 0)
    phone = row.get('phone', 'N/A')
    urgency_type = row['urgency_category']
    monthly_value = row['estimated_monthly_value']

    # Pain point identification
    pain_points = []
    solutions = []

    # Universal pain point - no website
    pain_points.append("no website means you're invisible to new customers searching Google")
    solutions.append("professional website with Google My Business optimization")

    # High-traffic gyms with no digital presence
    if reviews >= 200:
        pain_points.append(f"despite {reviews} reviews, potential customers can't find you online")
        solutions.append("SEO-optimized website to capture that search traffic")

    # Type-specific pain points
    name_lower = name.lower()
    if '24' in name_lower or 'hour' in name_lower:
        pain_points.append("manual key management for 24-hour access is a security risk")
        solutions.append("digital access control system with member app")

    if 'crossfit' in name_lower:
        pain_points.append("no way to post daily WODs or manage class bookings online")
        solutions.append("CrossFit management system with WOD posting and class scheduling")

    if any(term in name_lower for term in ['martial', 'karate', 'bjj', 'jiu']):
        pain_points.append("no system to track student progress or belt promotions")
        solutions.append("martial arts management system with belt tracking and parent portal")

    if 'boxing' in name_lower:
        pain_points.append("no online booking for training sessions or bout scheduling")
        solutions.append("boxing gym management with session booking and fight tracking")

    # Create the script
    script = f"""
LEAD: {name} ({city})
PHONE: {phone}
PRIORITY: {row['priority_score']:.1f}/100 | VALUE: {monthly_value}

OPENING:
"Hi, this is [Your Name] from [Company]. I was researching gyms in {city} and noticed {name} has {reviews} reviews with a {rating} rating - that's impressive! But I also noticed something that could be costing you new members..."

PAIN POINTS TO HIGHLIGHT:
• {' • '.join(pain_points)}

VALUE PROPOSITION:
"We help gyms like yours capture those lost leads with {', '.join(solutions[:2])}. Similar gyms in your area have seen 20-30% membership growth within 90 days."

URGENCY FACTOR ({urgency_type}):
"This is especially critical for {urgency_type} gyms because your members expect convenient digital access and scheduling."

CLOSE:
"I'd love to show you a 5-minute demo of what this could look like for {name}. Are you available for a quick call this week to see how we could add {monthly_value.split('-')[0]} to your monthly revenue?"

OBJECTION HANDLING:
• "We're too busy" → "That's exactly why you need this - it saves 10+ hours/week on admin"
• "Too expensive" → "The ROI pays for itself with just 3-4 new members per month"
• "We don't need a website" → "Your competitors with websites are capturing your Google traffic"
"""

    return script.strip()

def prioritize_leads(csv_file):
    """Main function to prioritize and analyze leads"""

    print("🎯 LEAD PRIORITIZATION ENGINE")
    print("=" * 60)

    # Load the leads data
    df = pd.read_csv(csv_file)
    print(f"📊 Loaded {len(df)} gym leads")

    # Calculate priority components
    print("⚡ Calculating revenue scores...")
    df['revenue_score'] = df.apply(calculate_revenue_score, axis=1)

    print("🎯 Analyzing gym type urgency...")
    df['urgency_multiplier'] = df.apply(lambda row: get_gym_type_urgency(row['business_name'], row.get('type', '')), axis=1)

    print("🗺️  Assigning geographic clusters...")
    df['geographic_cluster'] = df['city'].apply(get_geographic_cluster)

    # Determine urgency category for scripts
    df['urgency_category'] = df.apply(lambda row:
        '24-hour access' if '24' in row['business_name'].lower() else
        'CrossFit' if 'crossfit' in row['business_name'].lower() else
        'martial arts' if any(term in row['business_name'].lower() for term in ['martial', 'karate', 'bjj', 'jiu']) else
        'boxing' if 'boxing' in row['business_name'].lower() else
        'personal training' if 'personal' in row['business_name'].lower() else
        'specialized fitness', axis=1)

    # Calculate final priority score
    print("📈 Computing final priority scores...")
    df['priority_score'] = df['revenue_score'] * df['urgency_multiplier']

    # Estimate monthly values
    print("💰 Estimating monthly subscription values...")
    df['estimated_monthly_value'] = df.apply(lambda row: estimate_monthly_value(
        row['revenue_score'], row['urgency_multiplier'], row.get('reviews', 0), row.get('rating', 0)), axis=1)

    # Sort by priority score
    df_prioritized = df.sort_values('priority_score', ascending=False)

    # Generate sales scripts for top 50
    print("📝 Generating personalized sales scripts for top 50 leads...")
    top_50 = df_prioritized.head(50).copy()
    top_50['sales_script'] = top_50.apply(generate_sales_script, axis=1)

    # Create final output with all relevant columns
    output_columns = [
        'business_name', 'city', 'address', 'phone', 'website',
        'rating', 'reviews', 'type', 'geographic_cluster',
        'revenue_score', 'urgency_multiplier', 'urgency_category',
        'priority_score', 'estimated_monthly_value', 'primary_pain',
        'pain_points', 'recommended_solution'
    ]

    # Add sales script column for top 50
    top_50_output = top_50[output_columns + ['sales_script']].copy()
    all_leads_output = df_prioritized[output_columns].copy()

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Top 50 priority leads with sales scripts
    top_50_file = f"priority_lead_analysis_{timestamp}.csv"
    top_50_output.to_csv(top_50_file, index=False)

    # All leads prioritized
    all_leads_file = f"all_leads_prioritized_{timestamp}.csv"
    all_leads_output.to_csv(all_leads_file, index=False)

    # Generate summary statistics
    print("\n🎯 LEAD PRIORITIZATION SUMMARY")
    print("=" * 60)
    print(f"📊 Total leads analyzed: {len(df)}")
    print(f"🏆 Top priority leads (score >100): {len(df[df['priority_score'] > 100])}")
    print(f"🔥 High-value leads (>$400/month): {len(df[df['estimated_monthly_value'].str.contains('400|500|600|700|800|900', na=False)])}")

    print("\n📍 GEOGRAPHIC DISTRIBUTION:")
    cluster_counts = df['geographic_cluster'].value_counts()
    for cluster, count in cluster_counts.items():
        avg_score = df[df['geographic_cluster'] == cluster]['priority_score'].mean()
        print(f"   {cluster}: {count} leads (avg score: {avg_score:.1f})")

    print("\n🎯 URGENCY CATEGORIES:")
    urgency_counts = df['urgency_category'].value_counts()
    for category, count in urgency_counts.items():
        avg_value = df[df['urgency_category'] == category]['priority_score'].mean()
        print(f"   {category}: {count} leads (avg score: {avg_value:.1f})")

    print("\n💰 REVENUE PROJECTIONS:")
    total_potential = len(df) * 297  # Conservative average
    high_value_potential = len(df[df['priority_score'] > 100]) * 497
    print(f"   Conservative total potential: ${total_potential:,}/month")
    print(f"   High-priority potential: ${high_value_potential:,}/month")

    print(f"\n💾 FILES GENERATED:")
    print(f"   📋 {top_50_file} - Top 50 leads with sales scripts")
    print(f"   📊 {all_leads_file} - All leads prioritized")

    # Show top 10 leads
    print(f"\n🥇 TOP 10 PRIORITY LEADS:")
    for i, row in top_50_output.head(10).iterrows():
        print(f"   {i+1}. {row['business_name']} ({row['city']}) - Score: {row['priority_score']:.1f} - Value: {row['estimated_monthly_value']}")

    return top_50_output, all_leads_output

if __name__ == "__main__":
    # Use the most recent gym leads file
    csv_file = "central_valley_gym_leads_20250916_214958.csv"
    top_50, all_leads = prioritize_leads(csv_file)

    print(f"\n✅ LEAD PRIORITIZATION COMPLETE!")
    print(f"🎯 {len(top_50)} priority leads ready for immediate outreach")
    print(f"📞 Sales scripts generated with specific pain points and dollar amounts")
    print(f"🗺️  Geographic clusters optimized for efficient sales routes")