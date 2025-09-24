#!/usr/bin/env python3
"""
Technical Upgrade Packages for Existing Gym Websites
- Pre-built upgrade packages based on audit findings
- Specific solutions for common gym website problems
- Tiered pricing and implementation plans
- ROI calculations for each package
"""

import os
import sys
import pandas as pd
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class GymUpgradePackages:
    """Pre-built upgrade packages for gym websites"""

    def __init__(self):
        self.packages = self._define_upgrade_packages()

    def _define_upgrade_packages(self):
        """Define standardized upgrade packages"""
        return {
            'performance_starter': {
                'name': 'Performance Starter Package',
                'description': 'Essential speed and mobile optimization',
                'target_audience': 'Gyms with mobile scores 40-60',
                'price_range': '$497-797',
                'implementation_time': '1-2 weeks',
                'guaranteed_improvements': [
                    'Mobile score increase by 20-30 points',
                    'Page load time reduced by 50%',
                    'Mobile-friendly responsive design'
                ],
                'included_services': [
                    {
                        'service': 'Mobile Viewport Fix',
                        'description': 'Add proper mobile viewport meta tags',
                        'technical_detail': '<meta name="viewport" content="width=device-width, initial-scale=1">',
                        'impact': 'Site displays correctly on mobile devices',
                        'time': '30 minutes'
                    },
                    {
                        'service': 'Image Optimization',
                        'description': 'Compress and resize all images for mobile',
                        'technical_detail': 'Convert to WebP format, implement responsive images',
                        'impact': '40-60% reduction in image file sizes',
                        'time': '2-4 hours'
                    },
                    {
                        'service': 'Text Compression',
                        'description': 'Enable GZIP compression on server',
                        'technical_detail': 'Configure server-level compression for HTML, CSS, JS',
                        'impact': '30-50% reduction in file transfer sizes',
                        'time': '1 hour'
                    },
                    {
                        'service': 'Critical CSS Implementation',
                        'description': 'Inline critical CSS for faster rendering',
                        'technical_detail': 'Extract above-the-fold CSS and inline it',
                        'impact': 'Eliminates render-blocking CSS',
                        'time': '3-4 hours'
                    }
                ],
                'roi_metrics': {
                    'current_monthly_loss': 500,  # From poor mobile performance
                    'expected_monthly_gain': 800,  # From improved conversions
                    'payback_months': 1.2,
                    'annual_roi': 1200
                }
            },

            'conversion_optimizer': {
                'name': 'Conversion Optimizer Package',
                'description': 'Business features and lead generation focus',
                'target_audience': 'Gyms with decent performance but missing business features',
                'price_range': '$797-1297',
                'implementation_time': '2-3 weeks',
                'guaranteed_improvements': [
                    'Online booking system implementation',
                    'Lead capture forms with automation',
                    'Class schedule integration'
                ],
                'included_services': [
                    {
                        'service': 'Online Booking System',
                        'description': 'Full booking system for classes and personal training',
                        'technical_detail': 'Integration with calendar APIs and payment processing',
                        'impact': 'Reduce admin time by 10-15 hours/week',
                        'revenue_impact': '+$500-1500/month from increased bookings'
                    },
                    {
                        'service': 'Membership Lead Capture',
                        'description': 'Optimized forms with email automation',
                        'technical_detail': 'Multi-step forms with CRM integration',
                        'impact': 'Increase conversion rate by 25-40%',
                        'revenue_impact': '+$1000-3000/month from new members'
                    },
                    {
                        'service': 'Class Schedule Display',
                        'description': 'Real-time class schedule with availability',
                        'technical_detail': 'Dynamic schedule with real-time updates',
                        'impact': 'Reduce phone calls by 60-80%',
                        'cost_savings': '$200-500/month in admin time'
                    },
                    {
                        'service': 'Social Proof Integration',
                        'description': 'Member testimonials and success stories',
                        'technical_detail': 'Testimonial carousel with before/after photos',
                        'impact': 'Increase trust and conversion rates',
                        'revenue_impact': '+$300-800/month from trust building'
                    }
                ],
                'roi_metrics': {
                    'current_monthly_loss': 1000,  # From missed opportunities
                    'expected_monthly_gain': 2500,  # From new features
                    'payback_months': 0.8,
                    'annual_roi': 2800
                }
            },

            'complete_transformation': {
                'name': 'Complete Digital Transformation',
                'description': 'Full website overhaul with advanced features',
                'target_audience': 'Gyms with mobile scores <40 or major issues',
                'price_range': '$1497-2497',
                'implementation_time': '3-4 weeks',
                'guaranteed_improvements': [
                    'Mobile score increase to 80+',
                    'Complete responsive redesign',
                    'Advanced business automation'
                ],
                'included_services': [
                    {
                        'service': 'Complete Mobile Redesign',
                        'description': 'Mobile-first responsive design overhaul',
                        'technical_detail': 'Modern CSS Grid/Flexbox layout with mobile optimization',
                        'impact': 'Professional appearance on all devices'
                    },
                    {
                        'service': 'Performance Optimization Suite',
                        'description': 'All performance optimizations included',
                        'technical_detail': 'CDN, caching, compression, image optimization',
                        'impact': '60-80% improvement in load times'
                    },
                    {
                        'service': 'Advanced Booking & CRM',
                        'description': 'Complete member management system',
                        'technical_detail': 'Member portal, class credits, payment processing',
                        'impact': 'Full automation of member management'
                    },
                    {
                        'service': 'SEO Foundation',
                        'description': 'Technical SEO and local search optimization',
                        'technical_detail': 'Schema markup, local SEO, Google My Business optimization',
                        'impact': 'Improved search rankings and local visibility'
                    },
                    {
                        'service': 'Analytics & Conversion Tracking',
                        'description': 'Complete tracking and reporting system',
                        'technical_detail': 'Google Analytics 4, conversion tracking, heat maps',
                        'impact': 'Data-driven marketing and optimization'
                    }
                ],
                'roi_metrics': {
                    'current_monthly_loss': 2000,  # From poor website
                    'expected_monthly_gain': 4000,  # From complete transformation
                    'payback_months': 0.6,
                    'annual_roi': 3500
                }
            },

            'maintenance_retainer': {
                'name': 'Ongoing Maintenance & Optimization',
                'description': 'Monthly maintenance and continuous improvement',
                'target_audience': 'Gyms with existing optimized websites',
                'price_range': '$197-397/month',
                'implementation_time': 'Ongoing',
                'guaranteed_improvements': [
                    'Monthly performance monitoring',
                    'Content updates and security patches',
                    'Ongoing optimization improvements'
                ],
                'included_services': [
                    {
                        'service': 'Performance Monitoring',
                        'description': 'Monthly performance audits and optimization',
                        'technical_detail': 'Automated monitoring with monthly reports',
                        'impact': 'Maintain optimal performance over time'
                    },
                    {
                        'service': 'Security Updates',
                        'description': 'Regular security patches and backups',
                        'technical_detail': 'Plugin updates, security scanning, daily backups',
                        'impact': 'Protect against security threats and data loss'
                    },
                    {
                        'service': 'Content Management',
                        'description': 'Class schedule updates and content changes',
                        'technical_detail': 'Up to 2 hours of content updates per month',
                        'impact': 'Keep website current without staff time'
                    },
                    {
                        'service': 'Conversion Optimization',
                        'description': 'A/B testing and conversion rate improvements',
                        'technical_detail': 'Monthly testing of forms, CTAs, and layouts',
                        'impact': 'Continuous improvement in lead generation'
                    }
                ],
                'roi_metrics': {
                    'monthly_value_add': 800,  # Value provided each month
                    'cost_savings': 400,  # Savings from not hiring staff
                    'roi_percentage': 200,  # 200% ROI monthly
                    'annual_benefit': 4800
                }
            }
        }

    def recommend_package_for_audit(self, audit_results):
        """Recommend appropriate package based on audit results"""
        mobile_score = audit_results.get('mobile_score', 50)
        critical_fixes = len(audit_results.get('critical_fixes', []))
        missing_features = len(audit_results.get('missing_features', []))
        usability_issues = len(audit_results.get('usability_issues', []))

        recommendations = []

        # Determine primary recommendation
        if mobile_score < 40 or critical_fixes >= 3:
            primary_package = 'complete_transformation'
            urgency = 'Critical'
            reasoning = f"Mobile score of {mobile_score}/100 with {critical_fixes} critical issues requires complete overhaul"
        elif mobile_score < 60 or critical_fixes >= 1:
            primary_package = 'performance_starter'
            urgency = 'High'
            reasoning = f"Mobile score of {mobile_score}/100 needs immediate performance optimization"
        elif missing_features >= 2:
            primary_package = 'conversion_optimizer'
            urgency = 'Medium'
            reasoning = f"Good performance but missing {missing_features} key business features"
        else:
            primary_package = 'maintenance_retainer'
            urgency = 'Low'
            reasoning = "Website performing well, focus on maintenance and continuous improvement"

        recommendations.append({
            'package': primary_package,
            'urgency': urgency,
            'reasoning': reasoning,
            'primary': True
        })

        # Add secondary recommendations
        if primary_package != 'maintenance_retainer':
            recommendations.append({
                'package': 'maintenance_retainer',
                'urgency': 'Ongoing',
                'reasoning': 'Recommended after primary package implementation',
                'primary': False
            })

        return recommendations

    def generate_proposal(self, gym_name, audit_results, recommended_packages):
        """Generate detailed proposal document"""
        proposal = {
            'gym_name': gym_name,
            'proposal_date': datetime.now().strftime('%Y-%m-%d'),
            'audit_summary': {
                'mobile_score': audit_results.get('mobile_score', 0),
                'desktop_score': audit_results.get('desktop_score', 0),
                'critical_issues': len(audit_results.get('critical_fixes', [])),
                'quick_wins': len(audit_results.get('quick_wins', [])),
                'missing_features': len(audit_results.get('missing_features', []))
            },
            'recommended_packages': [],
            'total_investment': 0,
            'projected_roi': {},
            'implementation_timeline': []
        }

        total_investment = 0
        total_monthly_benefit = 0

        for rec in recommended_packages:
            if rec['primary']:
                package_key = rec['package']
                package = self.packages[package_key]

                package_proposal = {
                    'name': package['name'],
                    'description': package['description'],
                    'price_range': package['price_range'],
                    'implementation_time': package['implementation_time'],
                    'included_services': package['included_services'],
                    'guaranteed_improvements': package['guaranteed_improvements'],
                    'urgency': rec['urgency'],
                    'reasoning': rec['reasoning']
                }

                proposal['recommended_packages'].append(package_proposal)

                # Calculate investment (use midpoint of range)
                price_range = package['price_range'].replace('$', '').replace('/month', '')
                if '-' in price_range:
                    prices = [int(x) for x in price_range.split('-')]
                    avg_price = sum(prices) / 2
                    total_investment += avg_price

                # Add ROI metrics
                roi_metrics = package.get('roi_metrics', {})
                total_monthly_benefit += roi_metrics.get('expected_monthly_gain', 0)

        proposal['total_investment'] = total_investment
        proposal['projected_roi'] = {
            'total_investment': total_investment,
            'monthly_benefit': total_monthly_benefit,
            'annual_benefit': total_monthly_benefit * 12,
            'roi_percentage': (total_monthly_benefit * 12 / total_investment * 100) if total_investment > 0 else 0,
            'payback_months': total_investment / total_monthly_benefit if total_monthly_benefit > 0 else 999
        }

        return proposal

def main():
    """Test the upgrade package system"""
    print("\n" + "="*70)
    print("TECHNICAL UPGRADE PACKAGES SYSTEM")
    print("="*70)

    packages = GymUpgradePackages()

    # Display all available packages
    print("\n📦 AVAILABLE UPGRADE PACKAGES:")
    print("-" * 50)

    for key, package in packages.packages.items():
        print(f"\n{package['name']}")
        print(f"Price: {package['price_range']}")
        print(f"Target: {package['target_audience']}")
        print(f"Timeline: {package['implementation_time']}")
        print(f"Services: {len(package['included_services'])} included")

    # Test with sample audit data
    sample_audit = {
        'mobile_score': 45,
        'desktop_score': 65,
        'critical_fixes': [
            {'issue': 'Slow First Content Paint'},
            {'issue': 'Poor Layout Shift'}
        ],
        'quick_wins': [
            {'issue': 'Missing Viewport'},
            {'issue': 'No Text Compression'}
        ],
        'missing_features': [
            {'feature': 'Online Booking'},
            {'feature': 'Class Schedule'}
        ],
        'usability_issues': [
            {'issue': 'Small Touch Targets'}
        ]
    }

    print(f"\n\n🎯 PACKAGE RECOMMENDATION TEST:")
    print("-" * 40)

    recommendations = packages.recommend_package_for_audit(sample_audit)
    proposal = packages.generate_proposal("Sample Gym", sample_audit, recommendations)

    print(f"Gym: {proposal['gym_name']}")
    print(f"Mobile Score: {proposal['audit_summary']['mobile_score']}/100")
    print(f"Critical Issues: {proposal['audit_summary']['critical_issues']}")

    print(f"\n📋 RECOMMENDED PACKAGE:")
    for package in proposal['recommended_packages']:
        print(f"• {package['name']}")
        print(f"  Price: {package['price_range']}")
        print(f"  Urgency: {package['urgency']}")
        print(f"  Reasoning: {package['reasoning']}")

    print(f"\n💰 ROI PROJECTION:")
    roi = proposal['projected_roi']
    print(f"Investment: ${roi['total_investment']:,.0f}")
    print(f"Annual Benefit: ${roi['annual_benefit']:,.0f}")
    print(f"ROI: {roi['roi_percentage']:.0f}%")
    print(f"Payback: {roi['payback_months']:.1f} months")

    return packages, proposal

if __name__ == "__main__":
    packages, proposal = main()