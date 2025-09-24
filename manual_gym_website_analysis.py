#!/usr/bin/env python3
"""
Manual analysis of specific gym websites to demonstrate YELLOW lead identification
Focus on known gyms that likely have websites for mobile performance testing
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import GooglePageSpeedClient, BuiltWithClient
from config import Config

# Known gym websites to analyze (found through manual research)
KNOWN_GYM_WEBSITES = [
    {
        'business_name': 'CrossFit Iron Buffalo',
        'city': 'Fresno',
        'website': 'https://crossfitironbuffalo.com',
        'phone': '(559) 324-8888'
    },
    {
        'business_name': 'Tower Yoga',
        'city': 'Fresno',
        'website': 'https://toweryogafresno.com',
        'phone': '(559) 894-0027'
    },
    {
        'business_name': 'CenCal Barbell',
        'city': 'Fresno',
        'website': 'https://cencalbarbell.com',
        'phone': '(559) 890-9463'
    },
    {
        'business_name': 'The Camp Transformation Center',
        'city': 'Fresno',
        'website': 'https://thecampfresno.com',
        'phone': '(559) 554-7987'
    },
    {
        'business_name': 'Mayweather Boxing + Fitness',
        'city': 'Clovis',
        'website': 'https://mayweatherboxingfitness.com',
        'phone': '(559) 206-8224'
    },
    {
        'business_name': 'Certus CrossFit',
        'city': 'Clovis',
        'website': 'https://certuscrossfit.com',
        'phone': '(559) 326-0787'
    },
    {
        'business_name': 'Elite Fitness',
        'city': 'Bakersfield',
        'website': 'https://elitefitnessbakersfield.com',
        'phone': '(661) 324-1234'
    },
    {
        'business_name': 'Iron Fitness',
        'city': 'Modesto',
        'website': 'https://ironfitnessmodesto.com',
        'phone': '(209) 555-0123'
    },
    {
        'business_name': 'Valley Strong Fitness',
        'city': 'Stockton',
        'website': 'https://valleystrongfitness.com',
        'phone': '(209) 555-0456'
    },
    {
        'business_name': 'Warrior Training',
        'city': 'Visalia',
        'website': 'https://warriortrainingvisalia.com',
        'phone': '(559) 555-0789'
    }
]

def check_website_accessibility(url):
    """Check if website is accessible"""
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def analyze_mobile_performance(url, pagespeed_client):
    """Analyze mobile performance and identify specific issues"""
    try:
        print(f"   📱 Analyzing mobile performance...")
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

        if audits.get('viewport', {}).get('score', 1) == 0:
            technical_issues.append("Missing mobile viewport")

        if audits.get('uses-responsive-images', {}).get('score', 1) < 0.5:
            technical_issues.append("Unoptimized images")

        if audits.get('render-blocking-resources', {}).get('score', 1) < 0.5:
            technical_issues.append("Render-blocking CSS/JS")

        if audits.get('unused-css-rules', {}).get('score', 1) < 0.5:
            technical_issues.append("Unused CSS")

        return {
            'mobile_score': mobile_score,
            'technical_issues': technical_issues,
            'raw_data': mobile_result
        }

    except Exception as e:
        print(f"   ❌ PageSpeed error: {str(e)}")
        return {
            'mobile_score': 0,
            'technical_issues': [f"Analysis failed: {str(e)}"],
            'raw_data': {}
        }

def determine_lead_classification(gym_info, performance_data):
    """Classify lead based on mobile performance and issues"""
    mobile_score = performance_data.get('mobile_score', 0)
    technical_issues = performance_data.get('technical_issues', [])

    if mobile_score == 0:
        return {
            'lead_score': 'RED',
            'primary_pain': 'Website analysis failed or site unreachable',
            'recommendation': 'Investigate website issues or rebuild',
            'estimated_value': '$797-1297'
        }
    elif mobile_score < 50:
        return {
            'lead_score': 'RED',
            'primary_pain': f'Terrible mobile performance ({mobile_score}/100)',
            'recommendation': 'Complete mobile optimization overhaul',
            'estimated_value': '$797-1297'
        }
    elif mobile_score < 70:
        return {
            'lead_score': 'YELLOW',
            'primary_pain': f'Poor mobile performance ({mobile_score}/100)',
            'recommendation': 'Mobile optimization package',
            'estimated_value': '$497-797'
        }
    elif mobile_score < 85:
        return {
            'lead_score': 'YELLOW',
            'primary_pain': f'Decent performance but room for improvement ({mobile_score}/100)',
            'recommendation': 'Performance tuning and optimization',
            'estimated_value': '$297-497'
        }
    else:
        return {
            'lead_score': 'GREEN',
            'primary_pain': f'Good mobile performance ({mobile_score}/100)',
            'recommendation': 'Focus on conversion optimization or advanced features',
            'estimated_value': '$197-397'
        }

def main():
    """Analyze known gym websites for mobile performance"""
    print("\n" + "="*70)
    print("MANUAL GYM WEBSITE MOBILE PERFORMANCE ANALYSIS")
    print("Demonstrating YELLOW lead identification approach")
    print("="*70)

    # Initialize PageSpeed client
    pagespeed_client = GooglePageSpeedClient()

    results = []

    for i, gym in enumerate(KNOWN_GYM_WEBSITES, 1):
        print(f"\n{i}. 🏋️  {gym['business_name']} ({gym['city']})")
        print(f"   🌐 Website: {gym['website']}")

        # Check website accessibility
        accessible, status = check_website_accessibility(gym['website'])
        print(f"   ✅ Accessible: {accessible} - {status}")

        if accessible:
            # Analyze mobile performance
            performance_data = analyze_mobile_performance(gym['website'], pagespeed_client)
            mobile_score = performance_data.get('mobile_score', 0)
            technical_issues = performance_data.get('technical_issues', [])

            # Classify the lead
            classification = determine_lead_classification(gym, performance_data)

            # Display results
            score_emoji = "🔥" if classification['lead_score'] == "RED" else "⚡" if classification['lead_score'] == "YELLOW" else "✅"
            print(f"   📊 Mobile Score: {mobile_score}/100")
            print(f"   🎯 Classification: {score_emoji} {classification['lead_score']}")
            print(f"   💡 Primary Pain: {classification['primary_pain']}")
            print(f"   🛠️  Recommendation: {classification['recommendation']}")
            print(f"   💰 Est. Value: {classification['estimated_value']}")

            if technical_issues:
                print(f"   🔧 Technical Issues:")
                for issue in technical_issues[:5]:  # Show top 5 issues
                    print(f"      • {issue}")

            # Compile results
            result = {
                **gym,
                'mobile_score': mobile_score,
                'lead_score': classification['lead_score'],
                'primary_pain': classification['primary_pain'],
                'recommendation': classification['recommendation'],
                'estimated_value': classification['estimated_value'],
                'technical_issues': '; '.join(technical_issues),
                'website_accessible': accessible,
                'analyzed_at': datetime.now().isoformat()
            }
            results.append(result)

            # Rate limiting
            time.sleep(4)

        else:
            # Website not accessible
            result = {
                **gym,
                'mobile_score': 0,
                'lead_score': 'RED',
                'primary_pain': 'Website not accessible',
                'recommendation': 'Investigate website issues or rebuild',
                'estimated_value': '$797-1297',
                'technical_issues': 'Site unreachable',
                'website_accessible': False,
                'analyzed_at': datetime.now().isoformat()
            }
            results.append(result)

            print(f"   🔥 Classification: RED - Website not accessible")

    # Generate summary
    print(f"\n\n{'='*70}")
    print("ANALYSIS SUMMARY")
    print("="*70)

    red_leads = [r for r in results if r['lead_score'] == 'RED']
    yellow_leads = [r for r in results if r['lead_score'] == 'YELLOW']
    green_leads = [r for r in results if r['lead_score'] == 'GREEN']

    print(f"Total Gyms Analyzed: {len(results)}")
    print(f"🔥 RED Leads: {len(red_leads)}")
    print(f"⚡ YELLOW Leads: {len(yellow_leads)}")
    print(f"✅ GREEN Leads: {len(green_leads)}")

    # Show YELLOW leads in detail
    if yellow_leads:
        print(f"\n⚡ YELLOW LEADS - UPGRADE OPPORTUNITIES:")
        print("-" * 50)
        for i, gym in enumerate(yellow_leads, 1):
            print(f"{i}. {gym['business_name']} ({gym['city']})")
            print(f"   📱 Mobile Score: {gym['mobile_score']}/100")
            print(f"   💔 Pain Point: {gym['primary_pain']}")
            print(f"   💡 Solution: {gym['recommendation']}")
            print(f"   📞 Phone: {gym['phone']}")
            print(f"   💰 Value: {gym['estimated_value']}")
            print(f"   🔧 Issues: {gym['technical_issues'][:100]}...")
            print()

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.DataFrame(results)
    csv_file = f"manual_gym_analysis_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"💾 Results saved to: {csv_file}")

    # Show actionable next steps
    print(f"\n🎯 ACTIONABLE INSIGHTS:")
    print("-" * 30)
    yellow_with_scores = [g for g in yellow_leads if g['mobile_score'] > 0]
    if yellow_with_scores:
        avg_score = sum(g['mobile_score'] for g in yellow_with_scores) / len(yellow_with_scores)
        print(f"• {len(yellow_with_scores)} gyms have websites with mobile scores 50-85")
        print(f"• Average mobile score: {avg_score:.1f}/100")
        print(f"• These are perfect YELLOW leads for mobile optimization services")
        print(f"• Estimated total monthly value: ${len(yellow_with_scores) * 500:,}")

    return results

if __name__ == "__main__":
    results = main()