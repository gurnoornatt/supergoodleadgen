#!/usr/bin/env python3
"""
Enhanced Central Valley gym scraper focused on YELLOW leads:
- Gyms that HAVE websites but with poor mobile performance (< 60/100)
- Specific technical problems that can be upgraded
- Focus on upgrade opportunities rather than complete website builds
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

# Central Valley cities for targeted gym search
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
    'Porterville, CA'
]

# Major chains to exclude - focus on independent gyms
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness',
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness',
    'curves', 'pure barre', 'club pilates', 'the bar method', 'solidcore',
    'corepower yoga', 'soulcycle', 'cyclebar', 'barre3', 'burn boot camp',
    'crossfit', 'ufc gym', 'ymca', 'title boxing', 'kickboxing'
]

# Search queries targeting gyms with likely websites
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
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200, f"Status: {response.status_code}"
    except:
        return False, "Website inaccessible"

def analyze_mobile_performance(url, pagespeed_client):
    """Analyze mobile performance and identify specific issues"""
    if not url:
        return None

    try:
        # Analyze mobile performance
        mobile_result = pagespeed_client.analyze_url(url, strategy="mobile")
        mobile_score = mobile_result.get('performance_score', 0)

        # Extract specific issues from PageSpeed data
        raw_data = mobile_result.get('raw_data', {})
        lighthouse_result = raw_data.get('lighthouseResult', {})
        audits = lighthouse_result.get('audits', {})

        # Identify specific technical problems
        technical_issues = []

        # Check for common mobile issues
        if audits.get('first-contentful-paint', {}).get('score', 1) < 0.5:
            technical_issues.append("Slow first content paint (>3s)")

        if audits.get('largest-contentful-paint', {}).get('score', 1) < 0.5:
            technical_issues.append("Slow largest content paint (>4s)")

        if audits.get('cumulative-layout-shift', {}).get('score', 1) < 0.5:
            technical_issues.append("Layout shift issues")

        if audits.get('speed-index', {}).get('score', 1) < 0.5:
            technical_issues.append("Slow speed index")

        if audits.get('viewport', {}).get('score', 1) == 0:
            technical_issues.append("Missing mobile viewport")

        if audits.get('uses-responsive-images', {}).get('score', 1) < 0.5:
            technical_issues.append("Unoptimized images")

        if audits.get('render-blocking-resources', {}).get('score', 1) < 0.5:
            technical_issues.append("Render-blocking resources")

        if audits.get('unused-css-rules', {}).get('score', 1) < 0.5:
            technical_issues.append("Unused CSS")

        if audits.get('uses-text-compression', {}).get('score', 1) < 0.5:
            technical_issues.append("Missing text compression")

        return {
            'mobile_score': mobile_score,
            'technical_issues': technical_issues,
            'raw_data': mobile_result
        }

    except Exception as e:
        print(f"   ⚠️  PageSpeed error: {str(e)}")
        return {
            'mobile_score': 0,
            'technical_issues': ["PageSpeed analysis failed"],
            'raw_data': {}
        }

def analyze_technology_stack(url, builtwith_client):
    """Analyze website technology for upgrade opportunities"""
    if not url:
        return None

    try:
        domain = urlparse(url).netloc.replace('www.', '')
        tech_result = builtwith_client.analyze_domain(domain)

        technologies = tech_result.get('technologies', [])

        # Categorize technologies
        cms = []
        ecommerce = []
        hosting = []
        security = []
        analytics = []

        for tech in technologies:
            category = tech.get('category', '').lower()
            name = tech.get('name', '')

            if 'cms' in category or 'content management' in category:
                cms.append(name)
            elif 'ecommerce' in category or 'shopping' in category:
                ecommerce.append(name)
            elif 'hosting' in category or 'cdn' in category:
                hosting.append(name)
            elif 'security' in category or 'ssl' in category:
                security.append(name)
            elif 'analytics' in category or 'tracking' in category:
                analytics.append(name)

        # Identify upgrade opportunities
        upgrade_opportunities = []

        if not cms:
            upgrade_opportunities.append("No modern CMS detected - using outdated platform")
        elif any('wordpress' in c.lower() for c in cms):
            upgrade_opportunities.append("WordPress site - likely needs mobile optimization")

        if not security or not any('ssl' in s.lower() for s in security):
            upgrade_opportunities.append("Missing SSL certificate")

        if not analytics:
            upgrade_opportunities.append("No analytics tracking installed")

        if not ecommerce and 'gym' in url.lower():
            upgrade_opportunities.append("No online booking/payment system")

        return {
            'cms': cms,
            'ecommerce': ecommerce,
            'hosting': hosting,
            'security': security,
            'analytics': analytics,
            'upgrade_opportunities': upgrade_opportunities
        }

    except Exception as e:
        print(f"   ⚠️  BuiltWith error: {str(e)}")
        return {
            'cms': [],
            'ecommerce': [],
            'hosting': [],
            'security': [],
            'analytics': [],
            'upgrade_opportunities': ["Technology analysis failed"]
        }

def determine_lead_score_and_recommendations(gym_info, performance_data, tech_data):
    """Determine lead score and specific recommendations based on analysis"""
    has_website = gym_info.get('website_accessible', False)
    mobile_score = performance_data.get('mobile_score', 0) if performance_data else 0
    technical_issues = performance_data.get('technical_issues', []) if performance_data else []
    upgrade_opportunities = tech_data.get('upgrade_opportunities', []) if tech_data else []

    # Primary focus: YELLOW leads with upgrade opportunities
    if has_website and mobile_score > 0:
        if mobile_score < 60:
            # RED lead - poor mobile performance but has website
            lead_score = "RED"
            primary_pain = f"Website exists but terrible mobile score ({mobile_score}/100)"
            recommended_solution = "Mobile optimization package"
            estimated_value = "$497-797"

            if mobile_score < 30:
                primary_pain = f"Website completely broken on mobile ({mobile_score}/100)"
                estimated_value = "$797-1297"

        elif mobile_score < 80:
            # YELLOW lead - decent website with room for improvement
            lead_score = "YELLOW"
            primary_pain = f"Good website but mobile improvements needed ({mobile_score}/100)"
            recommended_solution = "Performance optimization"
            estimated_value = "$297-497"

        else:
            # GREEN lead - good performance but check for other opportunities
            lead_score = "GREEN"
            primary_pain = f"Good mobile performance ({mobile_score}/100)"
            recommended_solution = "Advanced features or conversion optimization"
            estimated_value = "$197-397"

            # Upgrade to YELLOW if significant opportunities exist
            if len(upgrade_opportunities) >= 2:
                lead_score = "YELLOW"
                primary_pain = f"Good performance but missing key features"
                recommended_solution = "Feature enhancement package"
                estimated_value = "$397-597"

    else:
        # No website or inaccessible
        lead_score = "RED"
        primary_pain = "No functional website"
        recommended_solution = "Complete website build"
        estimated_value = "$797-1297"

    # Compile specific issues for follow-up
    all_issues = []
    all_issues.extend(technical_issues)
    all_issues.extend(upgrade_opportunities)

    return {
        'lead_score': lead_score,
        'primary_pain': primary_pain,
        'technical_issues': '; '.join(all_issues) if all_issues else 'None identified',
        'recommended_solution': recommended_solution,
        'estimated_monthly_value': estimated_value,
        'mobile_score': mobile_score
    }

def scrape_city_gyms_with_analysis(city, serpapi, pagespeed_client, builtwith_client):
    """Scrape gyms and perform detailed technical analysis"""
    print(f"\n🏙️  ANALYZING GYMS IN: {city}")
    print("-" * 60)

    city_gyms = []
    analyzed_count = 0

    for query_template in SEARCH_QUERIES:
        query = query_template.format(city=city)
        print(f"   🔍 {query}")

        try:
            results = serpapi.search_google_maps(
                query=query,
                location=city,
                max_results=10  # Limit to focus on quality analysis
            )

            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')

                    # Skip chains and duplicates
                    if is_chain_gym(name):
                        continue

                    if any(gym['business_name'] == name for gym in city_gyms):
                        continue

                    # Extract basic gym info
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
                        'analyzed_at': datetime.now().isoformat()
                    }

                    # Only analyze websites that exist
                    if website_accessible and website_url:
                        print(f"      📱 Analyzing: {name}")

                        # Perform mobile performance analysis
                        performance_data = analyze_mobile_performance(website_url, pagespeed_client)

                        # Perform technology analysis
                        tech_data = analyze_technology_stack(website_url, builtwith_client)

                        # Determine lead score and recommendations
                        analysis = determine_lead_score_and_recommendations(gym_info, performance_data, tech_data)

                        # Add analysis data to gym info
                        gym_info.update(analysis)

                        # Add detailed technical data
                        if performance_data:
                            gym_info['mobile_performance_score'] = performance_data.get('mobile_score', 0)

                        if tech_data:
                            gym_info['cms_platform'] = ', '.join(tech_data.get('cms', []))
                            gym_info['has_ecommerce'] = len(tech_data.get('ecommerce', [])) > 0
                            gym_info['has_analytics'] = len(tech_data.get('analytics', [])) > 0

                        analyzed_count += 1

                        # Show real-time results
                        score_emoji = "🔥" if analysis['lead_score'] == "RED" else "⚡" if analysis['lead_score'] == "YELLOW" else "✅"
                        mobile_score = analysis.get('mobile_score', 0)
                        print(f"         {score_emoji} {analysis['lead_score']} - Mobile: {mobile_score}/100 - {analysis['primary_pain']}")

                        # Rate limiting for API calls
                        time.sleep(3)

                    else:
                        # Still add gyms without websites as RED leads
                        analysis = determine_lead_score_and_recommendations(gym_info, None, None)
                        gym_info.update(analysis)

                        score_emoji = "🔥"
                        print(f"      {score_emoji} {name} (RED) - {analysis['primary_pain']}")

                    city_gyms.append(gym_info)

            time.sleep(1)  # Rate limiting between queries

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            continue

    print(f"   📊 Found {len(city_gyms)} gyms, {analyzed_count} with detailed analysis")
    return city_gyms

def main():
    """Main function to find YELLOW lead gyms with upgrade opportunities"""
    print("\n" + "="*80)
    print("CENTRAL VALLEY GYM ANALYSIS - YELLOW LEADS FOCUS")
    print("Finding gyms with websites that need mobile/technical upgrades")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize API clients
    serpapi = SerpApiClient()
    pagespeed_client = GooglePageSpeedClient()
    builtwith_client = BuiltWithClient()

    all_gyms = []
    city_summaries = []

    # Process each city with detailed analysis
    for city in CENTRAL_VALLEY_CITIES:
        city_gyms = scrape_city_gyms_with_analysis(city, serpapi, pagespeed_client, builtwith_client)
        all_gyms.extend(city_gyms)

        # Track city summary
        red_count = len([g for g in city_gyms if g.get('lead_score') == 'RED'])
        yellow_count = len([g for g in city_gyms if g.get('lead_score') == 'YELLOW'])
        green_count = len([g for g in city_gyms if g.get('lead_score') == 'GREEN'])

        city_summaries.append({
            'city': city,
            'total_gyms': len(city_gyms),
            'red_leads': red_count,
            'yellow_leads': yellow_count,
            'green_leads': green_count
        })

        time.sleep(2)  # Rate limiting between cities

    # Remove duplicates and sort by priority
    unique_gyms = {}
    for gym in all_gyms:
        key = f"{gym['business_name']}_{gym['phone']}"
        if key not in unique_gyms:
            unique_gyms[key] = gym

    final_gyms = list(unique_gyms.values())

    # Sort: YELLOW leads with mobile scores 40-80 first (best upgrade opportunities)
    def sort_priority(gym):
        score = gym.get('lead_score', 'GREEN')
        mobile_score = gym.get('mobile_score', 0)
        reviews = gym.get('reviews', 0)

        if score == 'YELLOW' and 40 <= mobile_score <= 80:
            return (4, mobile_score, reviews)  # Highest priority
        elif score == 'RED' and mobile_score > 0:
            return (3, mobile_score, reviews)  # RED with existing website
        elif score == 'YELLOW':
            return (2, mobile_score, reviews)  # Other YELLOW leads
        elif score == 'RED':
            return (1, mobile_score, reviews)  # RED without website
        else:
            return (0, mobile_score, reviews)  # GREEN leads

    final_gyms.sort(key=sort_priority, reverse=True)

    # Generate summary report
    print(f"\n\n{'='*80}")
    print(f"ANALYSIS COMPLETE: {len(final_gyms)} UNIQUE GYMS ANALYZED")
    print("="*80)

    red_leads = [g for g in final_gyms if g.get('lead_score') == 'RED']
    yellow_leads = [g for g in final_gyms if g.get('lead_score') == 'YELLOW']
    green_leads = [g for g in final_gyms if g.get('lead_score') == 'GREEN']

    # Focus on YELLOW leads with mobile scores
    yellow_with_websites = [g for g in yellow_leads if g.get('mobile_score', 0) > 0]

    print(f"\n🎯 YELLOW LEADS WITH UPGRADE OPPORTUNITIES: {len(yellow_with_websites)}")
    print(f"🔥 RED LEADS (Poor/No Website): {len(red_leads)}")
    print(f"✅ GREEN LEADS (Good Performance): {len(green_leads)}")

    # Show top YELLOW leads with specific technical issues
    print(f"\n⚡ TOP 15 YELLOW LEADS - BEST UPGRADE OPPORTUNITIES:")
    print("-" * 60)
    for i, gym in enumerate(yellow_with_websites[:15], 1):
        mobile_score = gym.get('mobile_score', 0)
        print(f"{i}. {gym['business_name']} ({gym['city']})")
        print(f"   📱 Mobile Score: {mobile_score}/100")
        print(f"   🔧 Issues: {gym.get('technical_issues', 'None identified')}")
        print(f"   💡 Solution: {gym.get('recommended_solution', 'Standard optimization')}")
        print(f"   📞 {gym.get('phone', 'No phone')}")
        print(f"   💰 Value: {gym.get('estimated_monthly_value', '$297-497')}")
        print()

    # Save results with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Complete dataset
    df = pd.DataFrame(final_gyms)
    csv_file = f"gym_technical_analysis_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"💾 Complete analysis saved to: {csv_file}")

    # YELLOW leads only (best upgrade opportunities)
    yellow_df = pd.DataFrame(yellow_with_websites)
    yellow_csv = f"yellow_gym_leads_{timestamp}.csv"
    yellow_df.to_csv(yellow_csv, index=False)
    print(f"⚡ YELLOW leads saved to: {yellow_csv}")

    # City summary
    summary_df = pd.DataFrame(city_summaries)
    summary_csv = f"city_technical_summary_{timestamp}.csv"
    summary_df.to_csv(summary_csv, index=False)
    print(f"📊 City summary saved to: {summary_csv}")

    print(f"\n✅ ANALYSIS COMPLETE!")
    print(f"🎯 Focus on {len(yellow_with_websites)} YELLOW leads with specific upgrade opportunities")
    print(f"💡 These gyms have websites but need mobile optimization or feature upgrades")

    return final_gyms, yellow_with_websites

if __name__ == "__main__":
    all_gyms, yellow_leads = main()