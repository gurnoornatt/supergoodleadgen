#!/usr/bin/env python3
"""
Template Test Data Generator
Generates sample data for testing the Google Slides template placeholders
"""

import json
import random
from typing import Dict, List

class TemplateTestDataGenerator:
    """Generates realistic test data for Google Slides template testing"""
    
    def __init__(self):
        self.business_names = [
            "Riverside Pizzeria",
            "Central Valley Auto Repair", 
            "Fresno Family Dentistry",
            "Modesto Marketing Solutions",
            "Valley View Restaurant",
            "Stockton Legal Services",
            "Merced Home Improvements",
            "Turlock Fitness Center",
            "Bakersfield Beauty Salon",
            "Visalia Veterinary Clinic"
        ]
        
        self.pain_points_low_score = [
            "Slow loading speeds driving customers away",
            "Poor mobile experience losing sales", 
            "Search engines ranking site lower",
            "Outdated design hurting credibility",
            "Missing contact information costing leads",
            "Broken links frustrating visitors",
            "No mobile optimization losing traffic",
            "Poor user experience reducing conversions",
            "Slow page speed increasing bounce rate",
            "Unresponsive design on mobile devices"
        ]
        
        self.pain_points_high_score = [
            "Minor optimization opportunities available",
            "Image compression could improve speed",
            "Small mobile improvements possible",
            "Cache settings could be optimized",
            "Font loading could be streamlined", 
            "Third-party scripts could be optimized",
            "Minor accessibility improvements needed",
            "Form optimization opportunities exist",
            "Social media integration opportunities",
            "SEO meta tags could be enhanced"
        ]
        
        self.phone_numbers = [
            "(559) 555-0123",
            "(209) 555-0456", 
            "(661) 555-0789",
            "(831) 555-0147",
            "(559) 555-0258",
            "(209) 555-0369",
            "(661) 555-0741",
            "(831) 555-0852",
            "(559) 555-0963",
            "(209) 555-0174"
        ]
        
        self.website_domains = [
            "riversidepizza.com",
            "cvautorpair.com",
            "fresnofamilydental.com", 
            "modestomarketing.biz",
            "valleyviewrest.com",
            "stocktonlegal.net",
            "mercedimprovements.com",
            "turlockfitness.gym",
            "bakersfieldbeauty.salon",
            "visaliavet.com"
        ]

    def generate_sample_data(self, count: int = 10) -> List[Dict]:
        """Generate multiple sample data sets for testing"""
        samples = []
        
        for i in range(count):
            business_name = self.business_names[i % len(self.business_names)]
            mobile_score = random.randint(20, 95)
            
            # Choose pain points based on score
            if mobile_score < 60:
                pain_points = random.sample(self.pain_points_low_score, 3)
            else:
                pain_points = random.sample(self.pain_points_high_score, 3)
            
            sample = {
                "BUSINESS_NAME": business_name,
                "MOBILE_SCORE": str(mobile_score),
                "PAIN_POINT_1": pain_points[0],
                "PAIN_POINT_2": pain_points[1], 
                "PAIN_POINT_3": pain_points[2],
                "BUSINESS_PHONE": self.phone_numbers[i % len(self.phone_numbers)],
                "BUSINESS_WEBSITE": f"www.{self.website_domains[i % len(self.website_domains)]}",
                "WEBSITE_SCREENSHOT": f"https://drive.google.com/file/d/screenshot_{i+1}.png",
                "BUSINESS_LOGO": f"https://drive.google.com/file/d/logo_{i+1}.png",
                "COMPANY_LOGO": "https://drive.google.com/file/d/company_logo.png",
                "SCORE_BACKGROUND_COLOR": "#E74C3C" if mobile_score < 60 else "#27AE60",
                "SCORE_STATUS": "RED" if mobile_score < 60 else "GREEN"
            }
            
            samples.append(sample)
            
        return samples

    def generate_edge_case_data(self) -> List[Dict]:
        """Generate edge case test data to test template limits"""
        edge_cases = [
            {
                "test_name": "Very Long Business Name",
                "BUSINESS_NAME": "The Very Long Business Name Restaurant & Catering Services LLC",
                "MOBILE_SCORE": "23",
                "PAIN_POINT_1": "Extremely slow loading speeds are driving away potential customers who expect fast websites",
                "PAIN_POINT_2": "Very poor mobile experience is losing significant sales opportunities daily",
                "PAIN_POINT_3": "Search engines are ranking the site much lower due to performance issues",
                "BUSINESS_PHONE": "(559) 555-1234",
                "BUSINESS_WEBSITE": "www.verylongbusinessnamerestaurant.com",
                "WEBSITE_SCREENSHOT": "https://drive.google.com/file/d/screenshot_long.png",
                "BUSINESS_LOGO": "https://drive.google.com/file/d/logo_long.png",
                "COMPANY_LOGO": "https://drive.google.com/file/d/company_logo.png",
                "SCORE_BACKGROUND_COLOR": "#E74C3C",
                "SCORE_STATUS": "RED"
            },
            {
                "test_name": "Perfect Score",
                "BUSINESS_NAME": "Perfect Site",
                "MOBILE_SCORE": "100",
                "PAIN_POINT_1": "Minor image compression possible",
                "PAIN_POINT_2": "Cache headers could be optimized",
                "PAIN_POINT_3": "Font loading could be improved",
                "BUSINESS_PHONE": "(559) 555-0000",
                "BUSINESS_WEBSITE": "www.perfectsite.com",
                "WEBSITE_SCREENSHOT": "https://drive.google.com/file/d/screenshot_perfect.png",
                "BUSINESS_LOGO": "https://drive.google.com/file/d/logo_perfect.png", 
                "COMPANY_LOGO": "https://drive.google.com/file/d/company_logo.png",
                "SCORE_BACKGROUND_COLOR": "#27AE60",
                "SCORE_STATUS": "GREEN"
            },
            {
                "test_name": "Minimum Score",
                "BUSINESS_NAME": "Broken Site",
                "MOBILE_SCORE": "5",
                "PAIN_POINT_1": "Site completely broken on mobile",
                "PAIN_POINT_2": "Extremely slow loading times",
                "PAIN_POINT_3": "Multiple critical errors found",
                "BUSINESS_PHONE": "(559) 555-9999",
                "BUSINESS_WEBSITE": "www.brokensite.com",
                "WEBSITE_SCREENSHOT": "https://drive.google.com/file/d/screenshot_broken.png",
                "BUSINESS_LOGO": "https://drive.google.com/file/d/logo_broken.png",
                "COMPANY_LOGO": "https://drive.google.com/file/d/company_logo.png",
                "SCORE_BACKGROUND_COLOR": "#E74C3C",
                "SCORE_STATUS": "RED"
            },
            {
                "test_name": "Missing Data Test",
                "BUSINESS_NAME": "Test Business",
                "MOBILE_SCORE": "45",
                "PAIN_POINT_1": "No phone number available",
                "PAIN_POINT_2": "Website URL missing",
                "PAIN_POINT_3": "Logo extraction failed",
                "BUSINESS_PHONE": "",
                "BUSINESS_WEBSITE": "",
                "WEBSITE_SCREENSHOT": "",
                "BUSINESS_LOGO": "",
                "COMPANY_LOGO": "https://drive.google.com/file/d/company_logo.png",
                "SCORE_BACKGROUND_COLOR": "#E74C3C",
                "SCORE_STATUS": "RED"
            }
        ]
        
        return edge_cases

    def save_test_data(self, filename: str = "template_test_data.json"):
        """Save test data to JSON file"""
        test_data = {
            "regular_samples": self.generate_sample_data(10),
            "edge_cases": self.generate_edge_case_data(),
            "template_info": {
                "version": "1.0",
                "total_placeholders": 10,
                "placeholder_types": {
                    "text": ["BUSINESS_NAME", "MOBILE_SCORE", "PAIN_POINT_1", 
                           "PAIN_POINT_2", "PAIN_POINT_3", "BUSINESS_PHONE", "BUSINESS_WEBSITE"],
                    "image": ["WEBSITE_SCREENSHOT", "BUSINESS_LOGO", "COMPANY_LOGO"]
                }
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)
        
        return filename

    def generate_make_com_mapping(self) -> Dict:
        """Generate Make.com variable mapping configuration"""
        mapping = {
            "google_slides_placeholders": {
                "BUSINESS_NAME": {
                    "source": "google_sheets.business_name",
                    "type": "text",
                    "max_length": 50,
                    "required": True
                },
                "MOBILE_SCORE": {
                    "source": "pagespeed_insights.mobile_score",
                    "type": "number",
                    "format": "XX",
                    "conditional_formatting": {
                        "background_color": {
                            "condition": "< 60",
                            "true_value": "#E74C3C",
                            "false_value": "#27AE60"
                        }
                    },
                    "required": True
                },
                "PAIN_POINT_1": {
                    "source": "pain_point_generator.point_1",
                    "type": "text",
                    "max_length": 80,
                    "required": True
                },
                "PAIN_POINT_2": {
                    "source": "pain_point_generator.point_2", 
                    "type": "text",
                    "max_length": 80,
                    "required": True
                },
                "PAIN_POINT_3": {
                    "source": "pain_point_generator.point_3",
                    "type": "text", 
                    "max_length": 80,
                    "required": True
                },
                "BUSINESS_PHONE": {
                    "source": "google_sheets.phone",
                    "type": "text",
                    "format": "(XXX) XXX-XXXX",
                    "required": False
                },
                "BUSINESS_WEBSITE": {
                    "source": "google_sheets.website",
                    "type": "text",
                    "format": "www.example.com",
                    "required": False
                },
                "WEBSITE_SCREENSHOT": {
                    "source": "cloud_storage.screenshot_url",
                    "type": "image",
                    "format": "PNG/JPEG",
                    "required": True
                },
                "BUSINESS_LOGO": {
                    "source": "logo_processor.logo_url",
                    "type": "image", 
                    "format": "PNG",
                    "fallback": "generated_logo",
                    "required": False
                },
                "COMPANY_LOGO": {
                    "source": "static_assets.company_logo",
                    "type": "image",
                    "format": "PNG",
                    "required": True
                }
            }
        }
        
        return mapping

def main():
    """Generate and save test data"""
    generator = TemplateTestDataGenerator()
    
    # Generate and save test data
    filename = generator.save_test_data("template_test_data.json")
    print(f"✅ Test data saved to {filename}")
    
    # Generate Make.com mapping
    mapping = generator.generate_make_com_mapping()
    with open("make_com_mapping.json", 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print("✅ Make.com mapping saved to make_com_mapping.json")
    
    # Display sample data
    samples = generator.generate_sample_data(3)
    print("\n📋 Sample Test Data:")
    for i, sample in enumerate(samples, 1):
        print(f"\nSample {i}:")
        print(f"  Business: {sample['BUSINESS_NAME']}")
        print(f"  Score: {sample['MOBILE_SCORE']}/100 ({sample['SCORE_STATUS']})")
        print(f"  Pain Point 1: {sample['PAIN_POINT_1']}")
        print(f"  Phone: {sample['BUSINESS_PHONE']}")
        print(f"  Website: {sample['BUSINESS_WEBSITE']}")

if __name__ == "__main__":
    main()