#!/usr/bin/env python3
"""
Create a summary of solution packages by category
"""

import pandas as pd

def create_solution_summary():
    """Create a summary of solution packages by category"""

    df = pd.read_csv('specialized_fitness_solutions_20250916_220058.csv')

    print("\n" + "="*80)
    print("SPECIALIZED FITNESS SOLUTION PACKAGES - DETAILED BREAKDOWN")
    print("="*80)

    categories = df['specialized_category'].unique()

    for category in categories:
        category_df = df[df['specialized_category'] == category]
        print(f"\n{'='*60}")
        print(f"{category.upper()} SOLUTIONS")
        print("="*60)

        # Get solution package details
        package_name = category_df.iloc[0]['solution_package']
        core_features = category_df.iloc[0]['core_features']

        print(f"📦 Package: {package_name}")
        print(f"🎯 Key Features: {core_features}")

        # Pricing tiers
        tiers = category_df['recommended_tier'].value_counts()
        pricing_info = category_df.groupby('recommended_tier')['monthly_price'].first()

        print(f"\n💰 Pricing Tiers:")
        for tier in ['Starter', 'Professional', 'Enterprise']:
            if tier in tiers.index:
                count = tiers[tier]
                price = pricing_info[tier]
                print(f"   {tier}: {price} ({count} businesses)")

        # Top opportunities
        red_leads = category_df[category_df['lead_score'] == 'RED'].head(3)
        if not red_leads.empty:
            print(f"\n🔥 Top RED Lead Opportunities:")
            for i, (idx, lead) in enumerate(red_leads.iterrows(), 1):
                print(f"   {i}. {lead['business_name']} ({lead['city']}) - {lead['total_first_year_value']} potential")
                print(f"      📞 {lead['phone']} | ⭐ {lead['current_rating']} ({lead['current_reviews']} reviews)")

        # Revenue summary
        total_revenue = category_df['total_first_year_value'].str.replace('$', '').str.replace(',', '').astype(int).sum()
        avg_revenue = total_revenue // len(category_df)
        print(f"\n📊 Category Summary: {len(category_df)} businesses | ${total_revenue:,} total revenue | ${avg_revenue:,} average")

    print(f"\n{'='*80}")
    print("OVERALL MARKET SUMMARY")
    print("="*80)

    total_businesses = len(df)
    total_market_value = df['total_first_year_value'].str.replace('$', '').str.replace(',', '').astype(int).sum()
    red_leads_total = len(df[df['lead_score'] == 'RED'])
    red_revenue = df[df['lead_score'] == 'RED']['total_first_year_value'].str.replace('$', '').str.replace(',', '').astype(int).sum()

    print(f"🎯 Total Businesses: {total_businesses}")
    print(f"💰 Total Market Value: ${total_market_value:,}")
    print(f"🔥 RED Leads: {red_leads_total} businesses (${red_revenue:,} revenue potential)")
    print(f"📈 Average Deal Size: ${total_market_value // total_businesses:,}")

if __name__ == "__main__":
    create_solution_summary()