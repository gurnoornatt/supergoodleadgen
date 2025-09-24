#!/usr/bin/env python3
"""
Comprehensive Website Audit Checklist for Existing Gym Websites
- Technical performance analysis
- User experience evaluation
- Business feature assessment
- ROI opportunity identification
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime
from urllib.parse import urlparse
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import GooglePageSpeedClient, BuiltWithClient
from config import Config

class GymWebsiteAuditor:
    """Comprehensive website auditor for gym websites"""

    def __init__(self):
        self.pagespeed_client = GooglePageSpeedClient()
        self.builtwith_client = BuiltWithClient()

    def audit_technical_performance(self, url):
        """Comprehensive technical performance audit"""
        print(f"   📱 Technical Performance Analysis...")

        audit_results = {
            'mobile_score': 0,
            'desktop_score': 0,
            'performance_issues': [],
            'critical_fixes': [],
            'quick_wins': [],
            'advanced_optimizations': []
        }

        try:
            # Mobile analysis
            mobile_result = self.pagespeed_client.analyze_url(url, strategy="mobile")
            audit_results['mobile_score'] = mobile_result.get('performance_score', 0)

            # Desktop analysis
            desktop_result = self.pagespeed_client.analyze_url(url, strategy="desktop")
            audit_results['desktop_score'] = desktop_result.get('performance_score', 0)

            # Extract detailed audit data
            mobile_audits = mobile_result.get('raw_data', {}).get('lighthouseResult', {}).get('audits', {})

            # Critical performance issues (immediate fixes needed)
            if mobile_audits.get('first-contentful-paint', {}).get('numericValue', 0) > 3000:
                audit_results['critical_fixes'].append({
                    'issue': 'Slow First Content Paint',
                    'current_value': f"{mobile_audits.get('first-contentful-paint', {}).get('numericValue', 0)/1000:.1f}s",
                    'target': '<2.5s',
                    'impact': 'Users see blank screen too long',
                    'solution': 'Optimize server response time and eliminate render-blocking resources',
                    'estimated_improvement': '20-30 point score increase',
                    'cost': '$500-800'
                })

            if mobile_audits.get('largest-contentful-paint', {}).get('numericValue', 0) > 4000:
                audit_results['critical_fixes'].append({
                    'issue': 'Slow Largest Content Paint',
                    'current_value': f"{mobile_audits.get('largest-contentful-paint', {}).get('numericValue', 0)/1000:.1f}s",
                    'target': '<2.5s',
                    'impact': 'Main content loads too slowly',
                    'solution': 'Optimize images and implement lazy loading',
                    'estimated_improvement': '15-25 point score increase',
                    'cost': '$400-600'
                })

            if mobile_audits.get('cumulative-layout-shift', {}).get('numericValue', 0) > 0.25:
                audit_results['critical_fixes'].append({
                    'issue': 'Severe Layout Shift',
                    'current_value': f"{mobile_audits.get('cumulative-layout-shift', {}).get('numericValue', 0):.3f}",
                    'target': '<0.1',
                    'impact': 'Users accidentally click wrong buttons',
                    'solution': 'Reserve space for images and ads, stabilize fonts',
                    'estimated_improvement': '10-20 point score increase',
                    'cost': '$300-500'
                })

            # Quick wins (easy fixes with high impact)
            if mobile_audits.get('viewport', {}).get('score', 1) == 0:
                audit_results['quick_wins'].append({
                    'issue': 'Missing Mobile Viewport',
                    'impact': 'Site appears broken on mobile devices',
                    'solution': 'Add viewport meta tag',
                    'estimated_improvement': '5-10 point score increase',
                    'cost': '$50-100',
                    'time': '30 minutes'
                })

            if mobile_audits.get('uses-text-compression', {}).get('score', 1) < 0.5:
                audit_results['quick_wins'].append({
                    'issue': 'No Text Compression',
                    'impact': 'Slower loading, higher server costs',
                    'solution': 'Enable GZIP compression',
                    'estimated_improvement': '3-8 point score increase',
                    'cost': '$100-200',
                    'time': '1 hour'
                })

            if mobile_audits.get('uses-responsive-images', {}).get('score', 1) < 0.5:
                audit_results['quick_wins'].append({
                    'issue': 'Unoptimized Images',
                    'impact': 'Slow loading on mobile, high data usage',
                    'solution': 'Implement responsive images and WebP format',
                    'estimated_improvement': '8-15 point score increase',
                    'cost': '$200-400',
                    'time': '2-4 hours'
                })

            # Advanced optimizations (nice to have)
            if mobile_audits.get('unused-css-rules', {}).get('score', 1) < 0.5:
                audit_results['advanced_optimizations'].append({
                    'issue': 'Unused CSS',
                    'impact': 'Larger download size, slower parsing',
                    'solution': 'Remove unused CSS rules and implement critical CSS',
                    'estimated_improvement': '5-10 point score increase',
                    'cost': '$300-600'
                })

            if mobile_audits.get('uses-long-cache-ttl', {}).get('score', 1) < 0.5:
                audit_results['advanced_optimizations'].append({
                    'issue': 'Poor Caching Strategy',
                    'impact': 'Slower repeat visits',
                    'solution': 'Implement proper browser caching',
                    'estimated_improvement': '3-7 point score increase',
                    'cost': '$200-400'
                })

        except Exception as e:
            audit_results['performance_issues'].append(f"Analysis failed: {str(e)}")

        return audit_results

    def audit_user_experience(self, url):
        """User experience and mobile usability audit"""
        print(f"   👥 User Experience Analysis...")

        ux_audit = {
            'mobile_friendly': False,
            'usability_issues': [],
            'ux_improvements': [],
            'accessibility_issues': []
        }

        try:
            # Get mobile PageSpeed data for UX insights
            mobile_result = self.pagespeed_client.analyze_url(url, strategy="mobile")
            mobile_audits = mobile_result.get('raw_data', {}).get('lighthouseResult', {}).get('audits', {})

            # Mobile usability checks
            if mobile_audits.get('viewport', {}).get('score', 1) > 0:
                ux_audit['mobile_friendly'] = True
            else:
                ux_audit['usability_issues'].append({
                    'issue': 'Not Mobile Friendly',
                    'impact': 'Site unusable on phones - losing 60%+ of traffic',
                    'solution': 'Responsive design implementation',
                    'priority': 'Critical',
                    'cost': '$1500-3000'
                })

            # Touch target sizing
            if mobile_audits.get('tap-targets', {}).get('score', 1) < 0.5:
                ux_audit['usability_issues'].append({
                    'issue': 'Small Touch Targets',
                    'impact': 'Users struggle to tap buttons and links',
                    'solution': 'Increase button sizes and spacing',
                    'priority': 'High',
                    'cost': '$300-600'
                })

            # Text readability
            if mobile_audits.get('font-size', {}).get('score', 1) < 0.5:
                ux_audit['usability_issues'].append({
                    'issue': 'Text Too Small on Mobile',
                    'impact': 'Users cannot read content without zooming',
                    'solution': 'Increase base font size to 16px minimum',
                    'priority': 'High',
                    'cost': '$200-400'
                })

            # Accessibility improvements
            if mobile_audits.get('color-contrast', {}).get('score', 1) < 0.9:
                ux_audit['accessibility_issues'].append({
                    'issue': 'Poor Color Contrast',
                    'impact': 'Difficult to read for users with vision issues',
                    'solution': 'Improve text/background contrast ratios',
                    'cost': '$200-400'
                })

            if mobile_audits.get('image-alt', {}).get('score', 1) < 0.9:
                ux_audit['accessibility_issues'].append({
                    'issue': 'Missing Image Alt Text',
                    'impact': 'Poor accessibility and SEO',
                    'solution': 'Add descriptive alt text to all images',
                    'cost': '$300-500'
                })

        except Exception as e:
            ux_audit['usability_issues'].append({'issue': f"UX analysis failed: {str(e)}"})

        return ux_audit

    def audit_business_features(self, url):
        """Business-specific features audit for gyms"""
        print(f"   💼 Business Features Analysis...")

        business_audit = {
            'missing_features': [],
            'conversion_opportunities': [],
            'revenue_opportunities': []
        }

        try:
            # Check for gym-specific features by analyzing page content
            response = requests.get(url, timeout=10)
            content = response.text.lower()

            # Essential gym business features
            if 'class schedule' not in content and 'schedule' not in content:
                business_audit['missing_features'].append({
                    'feature': 'Online Class Scheduling',
                    'impact': 'Members cannot see class times - phone calls increase',
                    'solution': 'Implement class schedule display with real-time updates',
                    'revenue_impact': '+$200-500/month from reduced admin time',
                    'cost': '$800-1500'
                })

            if 'book' not in content and 'reserve' not in content:
                business_audit['missing_features'].append({
                    'feature': 'Online Booking System',
                    'impact': 'Lost revenue from missed appointments',
                    'solution': 'Add online booking for personal training and classes',
                    'revenue_impact': '+$500-1500/month from increased bookings',
                    'cost': '$1200-2500'
                })

            if 'membership' not in content and 'join' not in content:
                business_audit['conversion_opportunities'].append({
                    'opportunity': 'Membership Sign-up Forms',
                    'impact': 'Visitors leave without converting to members',
                    'solution': 'Add prominent membership CTA and lead capture',
                    'revenue_impact': '+$1000-3000/month from increased conversions',
                    'cost': '$600-1200'
                })

            if 'testimonial' not in content and 'review' not in content:
                business_audit['conversion_opportunities'].append({
                    'opportunity': 'Social Proof Display',
                    'impact': 'Visitors unsure about gym quality',
                    'solution': 'Add member testimonials and success stories',
                    'revenue_impact': '+$300-800/month from trust building',
                    'cost': '$400-800'
                })

            # Revenue opportunities
            if 'nutrition' not in content and 'supplement' not in content:
                business_audit['revenue_opportunities'].append({
                    'opportunity': 'Nutrition/Supplement Sales',
                    'impact': 'Missing additional revenue stream',
                    'solution': 'Add nutrition coaching and supplement sales pages',
                    'revenue_impact': '+$500-2000/month from product sales',
                    'cost': '$800-1600'
                })

            if 'personal training' not in content and 'pt' not in content:
                business_audit['revenue_opportunities'].append({
                    'opportunity': 'Personal Training Promotion',
                    'impact': 'High-value services not highlighted',
                    'solution': 'Create dedicated personal training landing pages',
                    'revenue_impact': '+$1000-4000/month from PT sales',
                    'cost': '$600-1200'
                })

        except Exception as e:
            business_audit['missing_features'].append({'feature': f"Business analysis failed: {str(e)}"})

        return business_audit

    def audit_technology_stack(self, url):
        """Technology and security audit"""
        print(f"   🔧 Technology Stack Analysis...")

        tech_audit = {
            'platform': 'Unknown',
            'security_issues': [],
            'technology_upgrades': [],
            'hosting_recommendations': []
        }

        try:
            # Get domain for BuiltWith analysis
            domain = urlparse(url).netloc.replace('www.', '')
            tech_result = self.builtwith_client.analyze_domain(domain)

            technologies = tech_result.get('technologies', [])

            # Identify platform
            cms_platforms = [tech for tech in technologies if 'cms' in tech.get('category', '').lower()]
            if cms_platforms:
                tech_audit['platform'] = cms_platforms[0].get('name', 'Unknown')

            # Security assessment
            ssl_techs = [tech for tech in technologies if 'ssl' in tech.get('name', '').lower()]
            if not ssl_techs:
                tech_audit['security_issues'].append({
                    'issue': 'No SSL Certificate',
                    'impact': 'Site marked as "Not Secure" - loses trust and SEO rankings',
                    'solution': 'Install SSL certificate',
                    'priority': 'Critical',
                    'cost': '$50-200/year'
                })

            # Analytics tracking
            analytics_techs = [tech for tech in technologies if 'analytics' in tech.get('category', '').lower()]
            if not analytics_techs:
                tech_audit['technology_upgrades'].append({
                    'upgrade': 'Analytics Tracking',
                    'impact': 'No data on website performance or user behavior',
                    'solution': 'Install Google Analytics and conversion tracking',
                    'benefit': 'Data-driven marketing decisions',
                    'cost': '$200-400'
                })

            # Modern web standards
            if tech_audit['platform'].lower() in ['wordpress', 'squarespace', 'wix']:
                tech_audit['technology_upgrades'].append({
                    'upgrade': 'Performance Optimization Plugin',
                    'impact': 'Platform not optimized for speed',
                    'solution': f"Install performance optimization for {tech_audit['platform']}",
                    'benefit': '20-40% speed improvement',
                    'cost': '$100-300'
                })

        except Exception as e:
            tech_audit['security_issues'].append({'issue': f"Technology analysis failed: {str(e)}"})

        return tech_audit

    def calculate_roi_potential(self, performance_audit, ux_audit, business_audit):
        """Calculate ROI potential from improvements"""

        roi_calculation = {
            'current_performance_cost': 0,
            'improvement_investment': 0,
            'monthly_revenue_increase': 0,
            'monthly_cost_savings': 0,
            'roi_percentage': 0,
            'payback_months': 0,
            'annual_benefit': 0
        }

        # Calculate current performance costs
        mobile_score = performance_audit.get('mobile_score', 50)
        if mobile_score < 50:
            # Poor performance = high bounce rate = lost revenue
            roi_calculation['current_performance_cost'] = 1000  # $1000/month in lost revenue
        elif mobile_score < 70:
            roi_calculation['current_performance_cost'] = 500   # $500/month in lost revenue

        # Calculate investment needed
        total_investment = 0

        # Technical fixes
        for fix in performance_audit.get('critical_fixes', []):
            cost_range = fix.get('cost', '$0').replace('$', '').replace(',', '')
            if '-' in cost_range:
                avg_cost = sum(int(x) for x in cost_range.split('-')) / 2
                total_investment += avg_cost

        for win in performance_audit.get('quick_wins', []):
            cost_range = win.get('cost', '$0').replace('$', '').replace(',', '')
            if '-' in cost_range:
                avg_cost = sum(int(x) for x in cost_range.split('-')) / 2
                total_investment += avg_cost

        # UX improvements
        for issue in ux_audit.get('usability_issues', []):
            cost_range = issue.get('cost', '$0').replace('$', '').replace(',', '')
            if '-' in cost_range:
                avg_cost = sum(int(x) for x in cost_range.split('-')) / 2
                total_investment += avg_cost

        roi_calculation['improvement_investment'] = total_investment

        # Calculate revenue increases from business features
        monthly_revenue_increase = 0
        for feature in business_audit.get('missing_features', []):
            revenue_impact = feature.get('revenue_impact', '+$0/month')
            if '+$' in revenue_impact and '/month' in revenue_impact:
                revenue_part = revenue_impact.replace('+$', '').replace('/month', '')
                if '-' in revenue_part:
                    avg_revenue = sum(int(x) for x in revenue_part.split('-')) / 2
                    monthly_revenue_increase += avg_revenue

        for opp in business_audit.get('revenue_opportunities', []):
            revenue_impact = opp.get('revenue_impact', '+$0/month')
            if '+$' in revenue_impact and '/month' in revenue_impact:
                revenue_part = revenue_impact.replace('+$', '').replace('/month', '')
                if '-' in revenue_part:
                    avg_revenue = sum(int(x) for x in revenue_part.split('-')) / 2
                    monthly_revenue_increase += avg_revenue

        roi_calculation['monthly_revenue_increase'] = monthly_revenue_increase
        roi_calculation['monthly_cost_savings'] = roi_calculation['current_performance_cost']

        # Calculate ROI
        total_monthly_benefit = monthly_revenue_increase + roi_calculation['current_performance_cost']
        roi_calculation['annual_benefit'] = total_monthly_benefit * 12

        if total_investment > 0:
            roi_calculation['roi_percentage'] = (roi_calculation['annual_benefit'] / total_investment) * 100
            roi_calculation['payback_months'] = total_investment / total_monthly_benefit if total_monthly_benefit > 0 else 999

        return roi_calculation

def main():
    """Main audit function for testing"""
    print("\n" + "="*70)
    print("GYM WEBSITE AUDIT CHECKLIST SYSTEM")
    print("="*70)

    auditor = GymWebsiteAuditor()

    # Test with known gym websites
    test_websites = [
        {'name': 'Tower Yoga', 'url': 'https://toweryogafresno.com'},
        {'name': 'Certus CrossFit', 'url': 'https://certuscrossfit.com'}
    ]

    audit_results = []

    for gym in test_websites:
        print(f"\n🏋️  AUDITING: {gym['name']}")
        print(f"   🌐 URL: {gym['url']}")
        print("-" * 50)

        # Perform comprehensive audit
        performance_audit = auditor.audit_technical_performance(gym['url'])
        ux_audit = auditor.audit_user_experience(gym['url'])
        business_audit = auditor.audit_business_features(gym['url'])
        tech_audit = auditor.audit_technology_stack(gym['url'])
        roi_potential = auditor.calculate_roi_potential(performance_audit, ux_audit, business_audit)

        # Compile results
        result = {
            'gym_name': gym['name'],
            'website_url': gym['url'],
            'audit_date': datetime.now().isoformat(),
            **performance_audit,
            **ux_audit,
            **business_audit,
            **tech_audit,
            **roi_potential
        }

        audit_results.append(result)

        # Display summary
        print(f"\n   📊 AUDIT SUMMARY:")
        print(f"   Mobile Score: {performance_audit['mobile_score']}/100")
        print(f"   Critical Fixes Needed: {len(performance_audit['critical_fixes'])}")
        print(f"   Quick Wins Available: {len(performance_audit['quick_wins'])}")
        print(f"   Missing Business Features: {len(business_audit['missing_features'])}")
        print(f"   ROI Potential: {roi_potential['roi_percentage']:.0f}% annual return")
        print(f"   Payback Period: {roi_potential['payback_months']:.1f} months")

        time.sleep(5)  # Rate limiting

    # Save audit results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.DataFrame(audit_results)
    csv_file = f"gym_website_audit_results_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Audit results saved to: {csv_file}")

    return audit_results

if __name__ == "__main__":
    results = main()