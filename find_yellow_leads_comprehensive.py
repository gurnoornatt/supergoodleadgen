#!/usr/bin/env python3
"""
Comprehensive YELLOW Lead Finder for Central Valley Gyms
- Searches for gyms with existing websites
- Analyzes mobile performance to find upgrade opportunities
- Identifies specific technical problems for sales conversations
- Focuses on mobile scores 40-80 (best upgrade opportunities)
"""

import os
import sys
import json
import time
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import SerpApiClient, GooglePageSpeedClient, BuiltWithClient
from config import Config

# Central Valley cities
CENTRAL_VALLEY_CITIES = [
    'Fresno, CA',
    'Bakersfield, CA',
    'Stockton, CA',
    'Modesto, CA',
    'Visalia, CA',
    'Merced, CA',
    'Clovis, CA'
]

# Search queries that often return gyms with websites
TARGETED_QUERIES = [
    "crossfit gym {city}",
    "personal trainer {city}",
    "yoga studio {city}",
    "martial arts {city}",
    "fitness studio {city}",
    "boxing gym {city}"
]

# Major chains to exclude
MAJOR_CHAINS = [
    'planet fitness', 'in-shape', 'la fitness', '24 hour fitness',
    'anytime fitness', 'crunch fitness', 'gold\'s gym', 'world gym',
    'equinox', 'lifetime fitness', 'orangetheory', 'f45', 'snap fitness',
    'curves', 'pure barre', 'club pilates'
]

def is_chain_gym(business_name):
    """Check if gym is a major chain"""
    name_lower = business_name.lower()
    return any(chain in name_lower for chain in MAJOR_CHAINS)

def extract_domain_from_url(url):
    """Extract clean domain from URL"""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return ""

def find_website_from_google_search(business_name, city):
    """Try to find website by googling the business name"""
    # This is a placeholder - in production you might use:
    # - Google Custom Search API
    # - Manual research
    # - Website pattern matching

    # Common website patterns for gyms
    clean_name = re.sub(r'[^a-zA-Z0-9\s]', '', business_name.lower())
    words = clean_name.split()

    potential_domains = []

    # Pattern 1: businessname + city
    if len(words) >= 2:
        potential_domains.append(f"https://{words[0]}{words[1]}{city.split(',')[0].lower()}.com")
        potential_domains.append(f"https://{words[0]}{words[1]}.com")

    # Pattern 2: just business name
    if len(words) >= 1:
        potential_domains.append(f"https://{words[0]}.com")
        potential_domains.append(f"https://{clean_name.replace(' ', '')}.com")

    # Test each potential domain
    for domain in potential_domains:
        try:
            response = requests.head(domain, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return domain, True
        except:
            continue

    return "", False

def check_website_accessibility(url):
    """Check if website is accessible and return real URL"""
    if not url:
        return False, "", "No URL provided"

    try:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        response = requests.head(url, timeout=10, allow_redirects=True)
        if response.status_code == 200:
            return True, response.url, f"Success: {response.status_code}"
        else:
            return False, "", f"HTTP {response.status_code}"
    except Exception as e:
        return False, "", f"Error: {str(e)}"

def analyze_mobile_performance_detailed(url, pagespeed_client):
    """Comprehensive mobile performance analysis"""
    try:
        print(f"      📱 Running PageSpeed analysis...")
        mobile_result = pagespeed_client.analyze_url(url, strategy="mobile")
        mobile_score = mobile_result.get('performance_score', 0)

        # Extract detailed audit results
        raw_data = mobile_result.get('raw_data', {})
        lighthouse_result = raw_data.get('lighthouseResult', {})
        audits = lighthouse_result.get('audits', {})

        # Detailed performance metrics
        performance_details = {}

        # Core Web Vitals
        fcp_audit = audits.get('first-contentful-paint', {})
        performance_details['fcp_score'] = fcp_audit.get('score', 1)
        performance_details['fcp_value'] = fcp_audit.get('numericValue', 0) / 1000  # Convert to seconds

        lcp_audit = audits.get('largest-contentful-paint', {})
        performance_details['lcp_score'] = lcp_audit.get('score', 1)
        performance_details['lcp_value'] = lcp_audit.get('numericValue', 0) / 1000

        cls_audit = audits.get('cumulative-layout-shift', {})
        performance_details['cls_score'] = cls_audit.get('score', 1)
        performance_details['cls_value'] = cls_audit.get('numericValue', 0)

        # Speed Index
        si_audit = audits.get('speed-index', {})
        performance_details['speed_index_score'] = si_audit.get('score', 1)
        performance_details['speed_index_value'] = si_audit.get('numericValue', 0) / 1000

        # Specific technical issues with business impact
        technical_issues = []
        business_impact = []

        # Critical issues (>3s load time)
        if performance_details['fcp_value'] > 3:
            technical_issues.append(f"Very slow first paint ({performance_details['fcp_value']:.1f}s)")
            business_impact.append("Visitors leave before seeing content")

        if performance_details['lcp_value'] > 4:
            technical_issues.append(f"Extremely slow largest content ({performance_details['lcp_value']:.1f}s)")
            business_impact.append("Poor user experience, high bounce rate")

        if performance_details['cls_value'] > 0.25:
            technical_issues.append(f"Severe layout shifting (CLS: {performance_details['cls_value']:.3f})")
            business_impact.append("Users accidentally click wrong buttons")

        # Mobile-specific issues
        if audits.get('viewport', {}).get('score', 1) == 0:
            technical_issues.append("Missing mobile viewport tag")
            business_impact.append("Site looks broken on phones")

        if audits.get('uses-responsive-images', {}).get('score', 1) < 0.5:
            technical_issues.append("Images not optimized for mobile")
            business_impact.append("Slow loading, high data usage")

        if audits.get('render-blocking-resources', {}).get('score', 1) < 0.5:
            technical_issues.append("Render-blocking CSS/JavaScript")
            business_impact.append("Blank screen while loading")

        # SEO and user experience issues
        if audits.get('uses-text-compression', {}).get('score', 1) < 0.5:
            technical_issues.append("Missing text compression")
            business_impact.append("Slower loading, higher costs")

        return {
            'mobile_score': mobile_score,
            'performance_details': performance_details,
            'technical_issues': technical_issues,
            'business_impact': business_impact,
            'total_issues': len(technical_issues),
            'raw_data': mobile_result
        }

    except Exception as e:
        print(f"      ❌ PageSpeed error: {str(e)}")
        return {
            'mobile_score': 0,
            'performance_details': {},
            'technical_issues': [f"Analysis failed: {str(e)}"],
            'business_impact': ["Cannot analyze website performance"],
            'total_issues': 1,
            'raw_data': {}
        }

def classify_yellow_lead_opportunity(gym_info, performance_data):
    """Classify and score the YELLOW lead opportunity"""
    mobile_score = performance_data.get('mobile_score', 0)
    technical_issues = performance_data.get('technical_issues', [])
    business_impact = performance_data.get('business_impact', [])
    total_issues = performance_data.get('total_issues', 0)

    # Lead classification
    if mobile_score == 0:
        lead_score = 'RED'
        priority = 'High'
        pain_point = 'Website analysis failed or unreachable'
        solution = 'Investigate and fix website issues'
        monthly_value = '$797-1297'
        confidence = 'Low'
    elif mobile_score < 40:
        lead_score = 'RED'
        priority = 'High'
        pain_point = f'Website completely broken on mobile ({mobile_score}/100)'
        solution = 'Complete mobile redesign and optimization'
        monthly_value = '$997-1597'
        confidence = 'High'
    elif mobile_score < 60:
        lead_score = 'YELLOW'
        priority = 'High'
        pain_point = f'Poor mobile performance hurting business ({mobile_score}/100)'
        solution = 'Mobile optimization package'
        monthly_value = '$597-997'
        confidence = 'High'
    elif mobile_score < 75:
        lead_score = 'YELLOW'
        priority = 'Medium'
        pain_point = f'Good site but missing mobile optimization ({mobile_score}/100)'
        solution = 'Performance tuning and mobile enhancements'
        monthly_value = '$397-697'
        confidence = 'Medium'
    elif mobile_score < 85:
        lead_score = 'YELLOW'
        priority = 'Low'
        pain_point = f'Decent performance with room for improvement ({mobile_score}/100)'
        solution = 'Advanced optimization and conversion features'
        monthly_value = '$297-497'
        confidence = 'Medium'
    else:
        lead_score = 'GREEN'
        priority = 'Low'
        pain_point = f'Good mobile performance ({mobile_score}/100)'
        solution = 'Focus on conversion optimization or advanced features'
        monthly_value = '$197-397'
        confidence = 'Low'

    # Adjust based on number of technical issues
    if total_issues >= 4 and lead_score == 'GREEN':
        lead_score = 'YELLOW'
        priority = 'Medium'
        pain_point = f'Good performance but multiple fixable issues'

    # Create sales pitch elements
    sales_hooks = []
    if 'high bounce rate' in ' '.join(business_impact).lower():
        sales_hooks.append("High bounce rate losing customers")
    if 'slow loading' in ' '.join(business_impact).lower():
        sales_hooks.append("Slow site frustrating mobile users")
    if 'broken' in ' '.join(business_impact).lower():
        sales_hooks.append("Mobile site appears broken")

    return {
        'lead_score': lead_score,
        'priority': priority,
        'mobile_score': mobile_score,
        'primary_pain': pain_point,
        'recommended_solution': solution,
        'estimated_monthly_value': monthly_value,
        'confidence_level': confidence,
        'technical_issues_count': total_issues,
        'technical_issues': '; '.join(technical_issues),
        'business_impact': '; '.join(business_impact),
        'sales_hooks': '; '.join(sales_hooks) if sales_hooks else 'Standard mobile optimization benefits'
    }

def find_gyms_with_websites(city, serpapi):
    """Find gyms that likely have websites"""
    print(f"\n🏙️  SEARCHING FOR GYMS WITH WEBSITES: {city}")
    print("-" * 60)

    city_gyms = []

    for query_template in TARGETED_QUERIES:
        query = query_template.format(city=city)
        print(f"   🔍 {query}")

        try:
            results = serpapi.search_google_maps(
                query=query,
                location=city,
                max_results=5  # Limit for focused analysis
            )

            if results and 'local_results' in results:
                for place in results['local_results']:
                    name = place.get('title', '')

                    # Skip chains and duplicates
                    if is_chain_gym(name):
                        continue

                    if any(gym['business_name'] == name for gym in city_gyms):
                        continue

                    # Try to find website
                    website_url = place.get('link', '')

                    # If no website from Google Maps, try to find it
                    if not website_url:
                        potential_website, found = find_website_from_google_search(name, city)
                        if found:
                            website_url = potential_website

                    gym_info = {
                        'business_name': name,
                        'city': city.split(',')[0],
                        'address': place.get('address', ''),
                        'phone': place.get('phone', ''),
                        'website': website_url,
                        'rating': place.get('rating', 0),
                        'reviews': place.get('reviews', 0),
                        'type': place.get('type', ''),
                        'found_at': datetime.now().isoformat()
                    }

                    city_gyms.append(gym_info)

                    # Show what we found
                    website_status = f"Website: {website_url}" if website_url else "No website found"
                    print(f"      📋 {name} - {website_status}")

            time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")
            continue

    print(f"   📊 Found {len(city_gyms)} gyms")
    return city_gyms

def main():
    """Main function to find and analyze YELLOW lead opportunities"""
    print("\n" + "="*80)
    print("COMPREHENSIVE YELLOW LEAD FINDER - CENTRAL VALLEY GYMS")
    print("Finding gyms with websites that need mobile optimization")
    print("="*80)
    print(f"\nStarted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize API clients
    serpapi = SerpApiClient()
    pagespeed_client = GooglePageSpeedClient()

    all_results = []
    city_summaries = []

    # Process each city
    for city in CENTRAL_VALLEY_CITIES:
        # Find gyms with potential websites
        city_gyms = find_gyms_with_websites(city, serpapi)

        # Analyze each gym with a website
        yellow_count = 0
        red_count = 0
        green_count = 0

        for gym in city_gyms:
            website_url = gym.get('website', '')

            if website_url:
                print(f"\n   🎯 ANALYZING: {gym['business_name']}")
                print(f"      🌐 URL: {website_url}")

                # Check accessibility
                accessible, final_url, status = check_website_accessibility(website_url)
                gym['website_accessible'] = accessible
                gym['final_url'] = final_url
                gym['access_status'] = status

                if accessible:
                    # Perform detailed mobile analysis
                    performance_data = analyze_mobile_performance_detailed(final_url, pagespeed_client)

                    # Classify the opportunity
                    classification = classify_yellow_lead_opportunity(gym, performance_data)

                    # Merge all data
                    result = {**gym, **classification, **performance_data}

                    # Count by type
                    if classification['lead_score'] == 'YELLOW':
                        yellow_count += 1
                        emoji = "⚡"
                    elif classification['lead_score'] == 'RED':
                        red_count += 1
                        emoji = "🔥"
                    else:
                        green_count += 1
                        emoji = "✅"

                    # Show results
                    mobile_score = classification['mobile_score']
                    print(f"      {emoji} {classification['lead_score']} - Mobile: {mobile_score}/100")
                    print(f"      💡 {classification['primary_pain']}")
                    print(f"      🛠️  {classification['recommended_solution']}")
                    print(f"      💰 {classification['estimated_monthly_value']}")

                    if classification['technical_issues_count'] > 0:
                        print(f"      🔧 {classification['technical_issues_count']} technical issues identified")

                    all_results.append(result)

                    # Rate limiting
                    time.sleep(4)

                else:
                    print(f"      ❌ Website not accessible: {status}")
                    # Still add as RED lead
                    red_result = {
                        **gym,
                        'lead_score': 'RED',
                        'mobile_score': 0,
                        'primary_pain': 'Website not accessible',
                        'recommended_solution': 'Fix website or rebuild',
                        'estimated_monthly_value': '$797-1297',
                        'technical_issues': 'Site unreachable',
                        'website_accessible': False
                    }
                    all_results.append(red_result)
                    red_count += 1

        # City summary
        city_summaries.append({
            'city': city,
            'total_gyms': len(city_gyms),
            'yellow_leads': yellow_count,
            'red_leads': red_count,
            'green_leads': green_count
        })

        print(f"\n   📊 {city} Summary: {yellow_count} YELLOW, {red_count} RED, {green_count} GREEN")
        time.sleep(2)  # Rate limiting between cities

    # Generate comprehensive report
    print(f"\n\n{'='*80}")
    print("COMPREHENSIVE ANALYSIS RESULTS")
    print("="*80)

    yellow_leads = [r for r in all_results if r.get('lead_score') == 'YELLOW']
    red_leads = [r for r in all_results if r.get('lead_score') == 'RED']
    green_leads = [r for r in all_results if r.get('lead_score') == 'GREEN']

    print(f"\nTotal Gyms Analyzed: {len(all_results)}")
    print(f"⚡ YELLOW Leads (Upgrade Opportunities): {len(yellow_leads)}")
    print(f"🔥 RED Leads (Major Issues): {len(red_leads)}")
    print(f"✅ GREEN Leads (Good Performance): {len(green_leads)}")

    # Focus on YELLOW leads - the money makers
    if yellow_leads:
        # Sort by priority and mobile score
        yellow_leads.sort(key=lambda x: (
            3 if x.get('priority') == 'High' else 2 if x.get('priority') == 'Medium' else 1,
            x.get('mobile_score', 0)
        ), reverse=True)

        print(f"\n⚡ TOP YELLOW LEADS - BEST UPGRADE OPPORTUNITIES:")
        print("-" * 70)

        for i, gym in enumerate(yellow_leads[:10], 1):
            print(f"{i}. {gym['business_name']} ({gym['city']})")
            print(f"   📱 Mobile Score: {gym.get('mobile_score', 0)}/100 ({gym.get('priority', 'Medium')} Priority)")
            print(f"   💔 Pain: {gym.get('primary_pain', 'Performance issues')}")
            print(f"   💡 Solution: {gym.get('recommended_solution', 'Mobile optimization')}")
            print(f"   📞 Phone: {gym.get('phone', 'Not available')}")
            print(f"   💰 Value: {gym.get('estimated_monthly_value', '$297-497')}")
            print(f"   🎯 Sales Hook: {gym.get('sales_hooks', 'Mobile optimization benefits')}")
            if gym.get('technical_issues_count', 0) > 0:
                print(f"   🔧 Issues: {gym.get('technical_issues', '')[:100]}...")
            print()

    # Save comprehensive results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # All results
    df_all = pd.DataFrame(all_results)
    csv_all = f"comprehensive_gym_analysis_{timestamp}.csv"
    df_all.to_csv(csv_all, index=False)
    print(f"💾 Complete analysis saved to: {csv_all}")

    # YELLOW leads only
    if yellow_leads:
        df_yellow = pd.DataFrame(yellow_leads)
        csv_yellow = f"yellow_leads_comprehensive_{timestamp}.csv"
        df_yellow.to_csv(csv_yellow, index=False)
        print(f"⚡ YELLOW leads saved to: {csv_yellow}")

    # City summary
    df_summary = pd.DataFrame(city_summaries)
    csv_summary = f"city_analysis_summary_{timestamp}.csv"
    df_summary.to_csv(csv_summary, index=False)
    print(f"📊 City summary saved to: {csv_summary}")

    # Final insights
    if yellow_leads:
        avg_score = sum(g.get('mobile_score', 0) for g in yellow_leads) / len(yellow_leads)
        high_priority = len([g for g in yellow_leads if g.get('priority') == 'High'])

        print(f"\n🎯 ACTIONABLE BUSINESS INSIGHTS:")
        print("-" * 40)
        print(f"• {len(yellow_leads)} YELLOW leads identified")
        print(f"• {high_priority} high-priority opportunities")
        print(f"• Average mobile score: {avg_score:.1f}/100")
        print(f"• Estimated total monthly value: ${len(yellow_leads) * 500:,}")
        print(f"• Perfect for mobile optimization sales conversations")

    return all_results, yellow_leads

if __name__ == "__main__":
    all_results, yellow_leads = main()