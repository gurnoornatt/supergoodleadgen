#!/usr/bin/env python3
"""
Before/After ROI Calculator for Gym Website Improvements
- Detailed financial impact analysis
- Industry-specific metrics and benchmarks
- Visual ROI presentations for sales conversations
- Custom ROI reports for each gym
"""

import pandas as pd
from datetime import datetime, timedelta
import json
import os

class GymWebsiteROICalculator:
    """Calculate detailed ROI for gym website improvements"""

    def __init__(self):
        # Industry benchmarks for gyms
        self.gym_benchmarks = {
            'average_monthly_members': 300,
            'average_membership_fee': 45,
            'average_personal_training_rate': 75,
            'website_conversion_rate_poor': 0.015,  # 1.5% for poor mobile sites
            'website_conversion_rate_good': 0.035,  # 3.5% for optimized sites
            'mobile_traffic_percentage': 0.65,     # 65% of traffic is mobile
            'bounce_rate_poor_mobile': 0.75,       # 75% bounce on poor mobile
            'bounce_rate_good_mobile': 0.45,       # 45% bounce on good mobile
            'local_search_percentage': 0.40,       # 40% find gyms via local search
            'online_booking_increase': 0.25,       # 25% increase with online booking
            'class_schedule_call_reduction': 0.70   # 70% reduction in schedule calls
        }

    def calculate_current_losses(self, gym_data, mobile_score):
        """Calculate current monthly losses from poor website performance"""

        # Extract gym data
        monthly_members = gym_data.get('estimated_members', self.gym_benchmarks['average_monthly_members'])
        avg_membership = gym_data.get('membership_fee', self.gym_benchmarks['average_membership_fee'])
        monthly_revenue = monthly_members * avg_membership

        # Estimate website traffic
        monthly_website_visitors = monthly_members * 3  # Assumption: 3x members visit site monthly
        mobile_visitors = monthly_website_visitors * self.gym_benchmarks['mobile_traffic_percentage']

        losses = {
            'lost_memberships': 0,
            'lost_pt_sessions': 0,
            'admin_time_costs': 0,
            'lost_local_search': 0,
            'total_monthly_loss': 0
        }

        # Mobile performance losses
        if mobile_score < 50:
            # Severe mobile issues
            mobile_conversion_loss = mobile_visitors * (self.gym_benchmarks['website_conversion_rate_good'] - 0.01)
            losses['lost_memberships'] = mobile_conversion_loss * avg_membership

            # High bounce rate = lost PT opportunities
            pt_loss_rate = (self.gym_benchmarks['bounce_rate_poor_mobile'] - self.gym_benchmarks['bounce_rate_good_mobile'])
            losses['lost_pt_sessions'] = mobile_visitors * pt_loss_rate * 0.05 * self.gym_benchmarks['average_personal_training_rate']

        elif mobile_score < 70:
            # Moderate mobile issues
            mobile_conversion_loss = mobile_visitors * (self.gym_benchmarks['website_conversion_rate_good'] - 0.02)
            losses['lost_memberships'] = mobile_conversion_loss * avg_membership * 0.6
            losses['lost_pt_sessions'] = mobile_visitors * 0.15 * 0.03 * self.gym_benchmarks['average_personal_training_rate']

        # Admin time costs (phone calls for info that should be on website)
        if 'missing_class_schedule' in str(gym_data.get('missing_features', '')):
            # Estimate 2 hours/day of calls that could be avoided
            losses['admin_time_costs'] = 2 * 22 * 15  # 2 hrs/day * 22 workdays * $15/hr

        # Local search visibility losses
        if mobile_score < 60:
            # Poor mobile scores hurt local SEO
            search_traffic_loss = monthly_website_visitors * self.gym_benchmarks['local_search_percentage'] * 0.30
            losses['lost_local_search'] = search_traffic_loss * 0.025 * avg_membership

        losses['total_monthly_loss'] = sum(losses.values())

        return losses

    def calculate_improvement_benefits(self, gym_data, current_score, target_score, implemented_features):
        """Calculate monthly benefits from website improvements"""

        monthly_members = gym_data.get('estimated_members', self.gym_benchmarks['average_monthly_members'])
        avg_membership = gym_data.get('membership_fee', self.gym_benchmarks['average_membership_fee'])
        monthly_website_visitors = monthly_members * 3
        mobile_visitors = monthly_website_visitors * self.gym_benchmarks['mobile_traffic_percentage']

        benefits = {
            'increased_memberships': 0,
            'increased_pt_bookings': 0,
            'admin_time_savings': 0,
            'improved_retention': 0,
            'new_revenue_streams': 0,
            'total_monthly_benefit': 0
        }

        # Mobile performance improvements
        score_improvement = target_score - current_score
        if score_improvement > 20:
            # Significant improvement in conversions
            conversion_increase = mobile_visitors * 0.02  # 2% conversion increase
            benefits['increased_memberships'] = conversion_increase * avg_membership

            # Better UX = more PT bookings
            benefits['increased_pt_bookings'] = mobile_visitors * 0.015 * self.gym_benchmarks['average_personal_training_rate']

        # Feature-specific benefits
        if 'online_booking' in implemented_features:
            booking_increase = monthly_members * self.gym_benchmarks['online_booking_increase'] * avg_membership * 0.10
            benefits['increased_memberships'] += booking_increase

            # PT booking increase
            pt_booking_increase = monthly_members * 0.15 * 2 * self.gym_benchmarks['average_personal_training_rate']
            benefits['increased_pt_bookings'] += pt_booking_increase

        if 'class_schedule' in implemented_features:
            # Reduce admin time significantly
            call_reduction_savings = 2 * 22 * 15 * self.gym_benchmarks['class_schedule_call_reduction']
            benefits['admin_time_savings'] = call_reduction_savings

        if 'member_portal' in implemented_features:
            # Improved retention
            retention_improvement = monthly_members * avg_membership * 0.05  # 5% retention improvement
            benefits['improved_retention'] = retention_improvement

        if 'nutrition_sales' in implemented_features:
            # New revenue stream
            supplement_revenue = monthly_members * 25  # $25/month average supplement sales
            benefits['new_revenue_streams'] = supplement_revenue

        benefits['total_monthly_benefit'] = sum(benefits.values())

        return benefits

    def calculate_implementation_costs(self, package_type, custom_features=None):
        """Calculate one-time and ongoing costs"""

        cost_structures = {
            'performance_starter': {
                'one_time': 650,
                'monthly': 0,
                'implementation_weeks': 1.5
            },
            'conversion_optimizer': {
                'one_time': 1050,
                'monthly': 0,
                'implementation_weeks': 2.5
            },
            'complete_transformation': {
                'one_time': 2000,
                'monthly': 0,
                'implementation_weeks': 4
            },
            'maintenance_retainer': {
                'one_time': 0,
                'monthly': 300,
                'implementation_weeks': 0.5
            }
        }

        return cost_structures.get(package_type, cost_structures['performance_starter'])

    def generate_roi_analysis(self, gym_data, current_mobile_score, package_type, implemented_features):
        """Generate comprehensive ROI analysis"""

        # Define target scores based on package
        target_scores = {
            'performance_starter': 75,
            'conversion_optimizer': 70,
            'complete_transformation': 85,
            'maintenance_retainer': current_mobile_score + 5
        }

        target_score = target_scores.get(package_type, 75)

        # Calculate current losses
        current_losses = self.calculate_current_losses(gym_data, current_mobile_score)

        # Calculate improvement benefits
        benefits = self.calculate_improvement_benefits(
            gym_data, current_mobile_score, target_score, implemented_features
        )

        # Calculate costs
        costs = self.calculate_implementation_costs(package_type)

        # ROI calculations
        total_monthly_gain = benefits['total_monthly_benefit'] + current_losses['total_monthly_loss']
        annual_benefit = total_monthly_gain * 12
        total_investment = costs['one_time'] + (costs['monthly'] * 12)

        roi_percentage = (annual_benefit / total_investment * 100) if total_investment > 0 else 0
        payback_months = total_investment / total_monthly_gain if total_monthly_gain > 0 else 999

        # Create comprehensive analysis
        roi_analysis = {
            # Current situation
            'current_mobile_score': current_mobile_score,
            'target_mobile_score': target_score,
            'score_improvement': target_score - current_mobile_score,

            # Current losses
            'current_monthly_losses': current_losses,
            'current_annual_losses': current_losses['total_monthly_loss'] * 12,

            # Improvement benefits
            'improvement_benefits': benefits,
            'monthly_benefit_total': benefits['total_monthly_benefit'],
            'annual_benefit_total': benefits['total_monthly_benefit'] * 12,

            # Combined impact
            'total_monthly_gain': total_monthly_gain,
            'total_annual_gain': annual_benefit,

            # Investment
            'implementation_costs': costs,
            'total_investment': total_investment,

            # ROI metrics
            'roi_percentage': roi_percentage,
            'payback_months': payback_months,
            'break_even_date': (datetime.now() + timedelta(days=payback_months * 30)).strftime('%Y-%m-%d'),

            # Business metrics
            'revenue_multiple': annual_benefit / total_investment if total_investment > 0 else 0,
            'monthly_roi': (total_monthly_gain / total_investment * 100) if total_investment > 0 else 0,

            # Risk assessment
            'confidence_level': 'High' if current_mobile_score < 60 else 'Medium',
            'risk_factors': [],
            'success_indicators': []
        }

        # Add risk factors and success indicators
        if current_mobile_score < 40:
            roi_analysis['risk_factors'].append('Extremely poor current performance - high upside potential')
            roi_analysis['success_indicators'].append('Immediate traffic increase expected')

        if 'online_booking' in implemented_features:
            roi_analysis['success_indicators'].append('Booking system will show direct revenue attribution')

        if roi_analysis['payback_months'] < 3:
            roi_analysis['success_indicators'].append('Very quick payback period indicates strong ROI')

        return roi_analysis

    def create_before_after_comparison(self, roi_analysis, gym_data):
        """Create visual before/after comparison"""

        comparison = {
            'before': {
                'mobile_score': roi_analysis['current_mobile_score'],
                'monthly_revenue_loss': roi_analysis['current_monthly_losses']['total_monthly_loss'],
                'annual_impact': roi_analysis['current_annual_losses'],
                'user_experience': 'Poor mobile experience, high bounce rate',
                'business_efficiency': 'High admin time, missed opportunities',
                'competitive_position': 'Behind competitors with better mobile sites'
            },
            'after': {
                'mobile_score': roi_analysis['target_mobile_score'],
                'monthly_revenue_gain': roi_analysis['total_monthly_gain'],
                'annual_impact': roi_analysis['total_annual_gain'],
                'user_experience': 'Excellent mobile experience, easy conversions',
                'business_efficiency': 'Automated booking, reduced admin time',
                'competitive_position': 'Leading local gyms in digital experience'
            },
            'improvement': {
                'score_increase': roi_analysis['score_improvement'],
                'monthly_swing': roi_analysis['total_monthly_gain'] + roi_analysis['current_monthly_losses']['total_monthly_loss'],
                'annual_swing': roi_analysis['total_annual_gain'] + roi_analysis['current_annual_losses'],
                'roi_percentage': roi_analysis['roi_percentage'],
                'payback_months': roi_analysis['payback_months']
            }
        }

        return comparison

    def generate_sales_presentation_data(self, roi_analysis, gym_data, comparison):
        """Generate data optimized for sales presentations"""

        presentation_data = {
            'executive_summary': {
                'investment': roi_analysis['total_investment'],
                'annual_return': roi_analysis['total_annual_gain'],
                'roi_percentage': f"{roi_analysis['roi_percentage']:.0f}%",
                'payback_period': f"{roi_analysis['payback_months']:.1f} months",
                'confidence': roi_analysis['confidence_level']
            },
            'problem_statement': {
                'current_mobile_score': f"{roi_analysis['current_mobile_score']}/100",
                'monthly_losses': f"${roi_analysis['current_monthly_losses']['total_monthly_loss']:,.0f}",
                'annual_losses': f"${roi_analysis['current_annual_losses']:,.0f}",
                'main_issues': []
            },
            'solution_benefits': {
                'score_improvement': f"+{roi_analysis['score_improvement']} points",
                'monthly_gain': f"${roi_analysis['total_monthly_gain']:,.0f}",
                'annual_gain': f"${roi_analysis['total_annual_gain']:,.0f}",
                'key_features': []
            },
            'financial_projection': {
                'year_1_net': roi_analysis['total_annual_gain'] - roi_analysis['total_investment'],
                'year_2_net': roi_analysis['total_annual_gain'],
                'year_3_net': roi_analysis['total_annual_gain'],
                'three_year_total': (roi_analysis['total_annual_gain'] * 3) - roi_analysis['total_investment']
            },
            'next_steps': {
                'implementation_timeline': roi_analysis['implementation_costs']['implementation_weeks'],
                'break_even_date': roi_analysis['break_even_date'],
                'first_results_timeline': '2-4 weeks after launch'
            }
        }

        # Populate problem issues
        if roi_analysis['current_mobile_score'] < 50:
            presentation_data['problem_statement']['main_issues'].append('Mobile site severely broken')
        if roi_analysis['current_monthly_losses']['admin_time_costs'] > 0:
            presentation_data['problem_statement']['main_issues'].append('High admin costs from phone calls')
        if roi_analysis['current_monthly_losses']['lost_memberships'] > 200:
            presentation_data['problem_statement']['main_issues'].append('Significant membership losses')

        return presentation_data

def main():
    """Test the ROI calculator with sample data"""
    print("\n" + "="*70)
    print("GYM WEBSITE ROI CALCULATOR")
    print("Before/After Financial Impact Analysis")
    print("="*70)

    calculator = GymWebsiteROICalculator()

    # Sample gym data for testing
    sample_gyms = [
        {
            'name': 'Tower Yoga',
            'data': {
                'estimated_members': 250,
                'membership_fee': 65,
                'missing_features': 'missing_class_schedule, no_online_booking'
            },
            'current_mobile_score': 71,
            'package': 'conversion_optimizer',
            'features': ['online_booking', 'class_schedule', 'member_portal']
        },
        {
            'name': 'Certus CrossFit',
            'data': {
                'estimated_members': 180,
                'membership_fee': 85,
                'missing_features': 'no_online_booking'
            },
            'current_mobile_score': 66,
            'package': 'performance_starter',
            'features': ['mobile_optimization', 'online_booking']
        }
    ]

    roi_reports = []

    for gym in sample_gyms:
        print(f"\n🏋️  ROI ANALYSIS: {gym['name']}")
        print("-" * 50)

        # Generate ROI analysis
        roi_analysis = calculator.generate_roi_analysis(
            gym['data'],
            gym['current_mobile_score'],
            gym['package'],
            gym['features']
        )

        # Create before/after comparison
        comparison = calculator.create_before_after_comparison(roi_analysis, gym['data'])

        # Generate sales presentation data
        presentation = calculator.generate_sales_presentation_data(roi_analysis, gym['data'], comparison)

        # Display key metrics
        print(f"Current Mobile Score: {roi_analysis['current_mobile_score']}/100")
        print(f"Target Mobile Score: {roi_analysis['target_mobile_score']}/100")
        print(f"Monthly Losses (Current): ${roi_analysis['current_monthly_losses']['total_monthly_loss']:,.0f}")
        print(f"Monthly Benefits (After): ${roi_analysis['total_monthly_gain']:,.0f}")
        print(f"Total Investment: ${roi_analysis['total_investment']:,.0f}")
        print(f"Annual ROI: {roi_analysis['roi_percentage']:.0f}%")
        print(f"Payback Period: {roi_analysis['payback_months']:.1f} months")

        # Compile report
        full_report = {
            'gym_name': gym['name'],
            'analysis_date': datetime.now().isoformat(),
            'roi_analysis': roi_analysis,
            'before_after_comparison': comparison,
            'sales_presentation': presentation
        }

        roi_reports.append(full_report)

    # Save comprehensive ROI reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save as JSON for detailed analysis
    json_filename = f"gym_roi_analysis_{timestamp}.json"
    with open(json_filename, 'w') as f:
        json.dump(roi_reports, f, indent=2)

    print(f"\n💾 Detailed ROI analysis saved: {json_filename}")

    # Create CSV summary for spreadsheet analysis
    summary_data = []
    for report in roi_reports:
        roi = report['roi_analysis']
        summary_data.append({
            'gym_name': report['gym_name'],
            'current_mobile_score': roi['current_mobile_score'],
            'target_mobile_score': roi['target_mobile_score'],
            'monthly_current_loss': roi['current_monthly_losses']['total_monthly_loss'],
            'monthly_benefit_after': roi['total_monthly_gain'],
            'total_investment': roi['total_investment'],
            'annual_roi_percentage': roi['roi_percentage'],
            'payback_months': roi['payback_months'],
            'year_1_net_benefit': roi['total_annual_gain'] - roi['total_investment'],
            'confidence_level': roi['confidence_level']
        })

    df = pd.DataFrame(summary_data)
    csv_filename = f"gym_roi_summary_{timestamp}.csv"
    df.to_csv(csv_filename, index=False)

    print(f"📊 ROI summary CSV saved: {csv_filename}")

    print(f"\n✅ ROI Calculator complete!")
    print(f"📈 Generated detailed financial analysis for {len(roi_reports)} gyms")

    return roi_reports, df

if __name__ == "__main__":
    reports, summary_df = main()