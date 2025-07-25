"""
Comprehensive database of gym and fitness management software platforms
"""
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

class SoftwareCategory(Enum):
    """Categories of gym management software"""
    ALL_IN_ONE = "all_in_one"
    BOUTIQUE_FITNESS = "boutique_fitness"
    CROSSFIT = "crossfit"
    YOGA_PILATES = "yoga_pilates"
    MARTIAL_ARTS = "martial_arts"
    PERSONAL_TRAINING = "personal_training"
    RECREATION_CENTER = "recreation_center"
    CHAIN_FRANCHISE = "chain_franchise"

class SoftwareQuality(Enum):
    """Software quality tiers"""
    PREMIUM = "premium"
    GOOD = "good"
    AVERAGE = "average"
    BASIC = "basic"
    OUTDATED = "outdated"

@dataclass
class GymSoftware:
    """Gym management software information"""
    name: str
    category: SoftwareCategory
    quality: SoftwareQuality
    founded_year: int
    last_updated: int
    pricing_tier: str  # budget, mid_range, premium
    features: List[str]
    technology_stack: List[str]
    detection_signatures: List[str]  # URLs, cookies, JS variables, etc.
    mobile_app: bool
    api_available: bool
    integrations: List[str]
    market_share: str  # high, medium, low, niche
    target_gym_size: List[str]  # small, medium, large
    strengths: List[str]
    weaknesses: List[str]
    website: str

class GymSoftwareDatabase:
    """Database of gym management software platforms"""
    
    def __init__(self):
        self.software_db = self._build_database()
        self.detection_map = self._build_detection_map()
    
    def _build_database(self) -> Dict[str, GymSoftware]:
        """Build comprehensive gym software database"""
        
        software_list = [
            # Tier 1 - Premium All-in-One Solutions
            GymSoftware(
                name="MindBody",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.PREMIUM,
                founded_year=2001,
                last_updated=2024,
                pricing_tier="premium",
                features=["scheduling", "payments", "marketing", "reporting", "mobile_app", "pos", "retail", "staff_management"],
                technology_stack=["javascript", "react", "asp.net", "microsoft_azure"],
                detection_signatures=[
                    "mindbodyonline.com",
                    "mindbody.io",
                    "mb-api",
                    "mindbody-widget",
                    "healcode",
                    "_mb_",
                    "mbclient",
                    "mindbody api",
                    "mindbody"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["quickbooks", "mailchimp", "facebook", "google", "apple_pay", "stripe"],
                market_share="high",
                target_gym_size=["small", "medium", "large"],
                strengths=["comprehensive_features", "mobile_app", "integrations", "marketing_tools"],
                weaknesses=["expensive", "complex_setup", "learning_curve"],
                website="https://www.mindbodyonline.com"
            ),
            
            GymSoftware(
                name="Zen Planner",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.GOOD,
                founded_year=2010,
                last_updated=2024,
                pricing_tier="mid_range",
                features=["scheduling", "payments", "member_management", "wod_tracking", "mobile_app", "reporting"],
                technology_stack=["javascript", "php", "mysql", "aws"],
                detection_signatures=[
                    "zenplanner.com",
                    "zp-api",
                    "zenplanner-widget",
                    "zpapi",
                    "zen-planner",
                    "zen planner api",
                    "zen planner",
                    "zenplanner"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "paypal", "mailchimp", "constantcontact"],
                market_share="medium",
                target_gym_size=["small", "medium"],
                strengths=["crossfit_focused", "wod_tracking", "affordable", "good_support"],
                weaknesses=["limited_marketing", "basic_reporting", "outdated_ui"],
                website="https://zenplanner.com"
            ),
            
            GymSoftware(
                name="Wodify",
                category=SoftwareCategory.CROSSFIT,
                quality=SoftwareQuality.GOOD,
                founded_year=2012,
                last_updated=2024,
                pricing_tier="mid_range",
                features=["wod_tracking", "scheduling", "payments", "performance_tracking", "mobile_app", "leaderboards"],
                technology_stack=["javascript", "react", "ruby", "postgresql", "aws"],
                detection_signatures=[
                    "wodify.com",
                    "wodify-core",
                    "wodify-api",
                    "wodify-widget",
                    "wodifycore",
                    "wodify core",
                    "wodify"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "quickbooks", "mailchimp"],
                market_share="medium",
                target_gym_size=["small", "medium"],
                strengths=["crossfit_specialized", "performance_tracking", "community_features", "mobile_first"],
                weaknesses=["crossfit_only", "limited_general_fitness", "pricing"],
                website="https://www.wodify.com"
            ),
            
            GymSoftware(
                name="Glofox",
                category=SoftwareCategory.BOUTIQUE_FITNESS,
                quality=SoftwareQuality.GOOD,
                founded_year=2014,
                last_updated=2024,
                pricing_tier="mid_range",
                features=["scheduling", "payments", "mobile_app", "marketing", "livestreaming", "virtual_classes"],
                technology_stack=["javascript", "react", "node.js", "mongodb", "aws"],
                detection_signatures=[
                    "glofox.com",
                    "glofox-api",
                    "glofox-widget",
                    "gfx-",
                    "glofox-booking",
                    "glofox"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "zoom", "mailchimp", "facebook", "instagram"],
                market_share="medium",
                target_gym_size=["small", "medium"],
                strengths=["boutique_focused", "virtual_classes", "modern_ui", "marketing_tools"],
                weaknesses=["newer_platform", "limited_large_gym_features", "pricing"],
                website="https://www.glofox.com"
            ),
            
            GymSoftware(
                name="TeamUp",
                category=SoftwareCategory.BOUTIQUE_FITNESS,
                quality=SoftwareQuality.GOOD,
                founded_year=2015,
                last_updated=2024,
                pricing_tier="budget",
                features=["scheduling", "payments", "member_management", "mobile_app", "waitlists"],
                technology_stack=["javascript", "vue.js", "php", "mysql"],
                detection_signatures=[
                    "goteamup.com",
                    "teamup-api",
                    "teamup-widget",
                    "tu-booking",
                    "teamup-schedule"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "paypal", "mailchimp", "zapier"],
                market_share="medium",
                target_gym_size=["small", "medium"],
                strengths=["affordable", "simple_setup", "good_mobile_app", "flexible_pricing"],
                weaknesses=["limited_features", "basic_reporting", "no_pos"],
                website="https://goteamup.com"
            ),
            
            # Tier 2 - Mid-Range Solutions
            GymSoftware(
                name="WellnessLiving",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.GOOD,
                founded_year=2016,
                last_updated=2024,
                pricing_tier="mid_range",
                features=["scheduling", "payments", "marketing", "mobile_app", "pos", "rewards", "automated_marketing"],
                technology_stack=["javascript", "php", "mysql", "aws"],
                detection_signatures=[
                    "wellnessliving.com",
                    "wl-api",
                    "wellnessliving-widget",
                    "wlv3",
                    "wellness-living"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["quickbooks", "mailchimp", "facebook", "google", "stripe"],
                market_share="medium",
                target_gym_size=["small", "medium"],
                strengths=["automated_marketing", "rewards_program", "comprehensive_features", "good_value"],
                weaknesses=["newer_platform", "limited_customization", "learning_curve"],
                website="https://www.wellnessliving.com"
            ),
            
            GymSoftware(
                name="ClubReady",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.AVERAGE,
                founded_year=2004,
                last_updated=2023,
                pricing_tier="mid_range",
                features=["member_management", "billing", "access_control", "reporting", "mobile_app", "pos"],
                technology_stack=["javascript", "asp.net", "sql_server", "azure"],
                detection_signatures=[
                    "clubready.com",
                    "cr-api",
                    "clubready-widget",
                    "clubready-portal",
                    "crms"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["quickbooks", "stripe", "paypal", "mailchimp"],
                market_share="medium",
                target_gym_size=["medium", "large"],
                strengths=["established_platform", "access_control", "billing_management", "reporting"],
                weaknesses=["dated_ui", "complex_setup", "expensive", "poor_mobile_experience"],
                website="https://clubready.com"
            ),
            
            GymSoftware(
                name="PushPress",
                category=SoftwareCategory.CROSSFIT,
                quality=SoftwareQuality.GOOD,
                founded_year=2013,
                last_updated=2024,
                pricing_tier="budget",
                features=["scheduling", "payments", "wod_tracking", "member_management", "mobile_app"],
                technology_stack=["javascript", "ruby", "postgresql", "heroku"],
                detection_signatures=[
                    "pushpress.com",
                    "pushpress-api",
                    "pp-widget",
                    "pushpress-core",
                    "ppcore"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "mailchimp", "quickbooks"],
                market_share="low",
                target_gym_size=["small"],
                strengths=["affordable", "crossfit_focused", "simple_setup", "good_support"],
                weaknesses=["limited_features", "small_market_share", "basic_reporting"],
                website="https://www.pushpress.com"
            ),
            
            GymSoftware(
                name="Pike13",
                category=SoftwareCategory.BOUTIQUE_FITNESS,
                quality=SoftwareQuality.GOOD,
                founded_year=2011,
                last_updated=2024,
                pricing_tier="mid_range",
                features=["scheduling", "payments", "client_management", "staff_management", "mobile_app", "reporting"],
                technology_stack=["javascript", "ruby", "postgresql", "aws"],
                detection_signatures=[
                    "pike13.com",
                    "pike13-api",
                    "p13-widget",
                    "pike13-schedule",
                    "p13api"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "quickbooks", "mailchimp", "constantcontact"],
                market_share="low",
                target_gym_size=["small", "medium"],
                strengths=["service_business_focused", "good_scheduling", "staff_management", "flexible"],
                weaknesses=["not_gym_specific", "complex_pricing", "learning_curve"],
                website="https://www.pike13.com"
            ),
            
            # Tier 3 - Basic/Budget Solutions
            GymSoftware(
                name="Acuity Scheduling",
                category=SoftwareCategory.PERSONAL_TRAINING,
                quality=SoftwareQuality.AVERAGE,
                founded_year=2006,
                last_updated=2024,
                pricing_tier="budget",
                features=["scheduling", "payments", "calendar_sync", "automated_reminders", "intake_forms"],
                technology_stack=["javascript", "php", "mysql"],
                detection_signatures=[
                    "acuityscheduling.com",
                    "acuity-api",
                    "acuity-widget",
                    "acuity-embed",
                    "squarespace-scheduling"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "paypal", "quickbooks", "mailchimp", "zoom"],
                market_share="medium",
                target_gym_size=["small"],
                strengths=["affordable", "easy_setup", "good_scheduling", "squarespace_integration"],
                weaknesses=["not_gym_specific", "limited_features", "no_member_management"],
                website="https://acuityscheduling.com"
            ),
            
            GymSoftware(
                name="Calendly",
                category=SoftwareCategory.PERSONAL_TRAINING,
                quality=SoftwareQuality.BASIC,
                founded_year=2013,
                last_updated=2024,
                pricing_tier="budget",
                features=["scheduling", "calendar_sync", "automated_reminders", "video_conferencing"],
                technology_stack=["javascript", "react", "ruby", "postgresql"],
                detection_signatures=[
                    "calendly.com",
                    "calendly-widget",
                    "calendly-embed",
                    "calendly-api",
                    "calendly widget",
                    "calendly"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["zoom", "google_meet", "stripe", "paypal", "salesforce"],
                market_share="high",
                target_gym_size=["small"],
                strengths=["very_affordable", "extremely_easy", "great_integrations", "popular"],
                weaknesses=["not_gym_specific", "no_member_management", "no_payments", "basic_features"],
                website="https://calendly.com"
            ),
            
            # Tier 4 - Outdated/Legacy Solutions
            GymSoftware(
                name="ABC Financial",
                category=SoftwareCategory.CHAIN_FRANCHISE,
                quality=SoftwareQuality.OUTDATED,
                founded_year=1981,
                last_updated=2022,
                pricing_tier="premium",
                features=["member_management", "billing", "access_control", "reporting", "collections"],
                technology_stack=["asp.net", "sql_server", "legacy_systems"],
                detection_signatures=[
                    "abcfinancial.com",
                    "abc-financial",
                    "abcf-",
                    "abc-billing"
                ],
                mobile_app=False,
                api_available=False,
                integrations=["limited"],
                market_share="low",
                target_gym_size=["large"],
                strengths=["established", "enterprise_focused", "billing_management"],
                weaknesses=["outdated_technology", "poor_ui", "expensive", "no_mobile", "limited_features"],
                website="https://www.abcfinancial.com"
            ),
            
            GymSoftware(
                name="Perfect Gym",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.AVERAGE,
                founded_year=2009,
                last_updated=2023,
                pricing_tier="mid_range",
                features=["member_management", "access_control", "billing", "mobile_app", "reporting", "pos"],
                technology_stack=["javascript", "asp.net", "sql_server", "azure"],
                detection_signatures=[
                    "perfectgym.com",
                    "perfect-gym",
                    "pg-api",
                    "perfectgym-widget"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "paypal", "quickbooks"],
                market_share="low",
                target_gym_size=["medium", "large"],
                strengths=["comprehensive", "access_control", "european_focused"],
                weaknesses=["complex", "expensive", "limited_us_market", "outdated_ui"],
                website="https://www.perfectgym.com"
            ),
            
            # Specialized Solutions
            GymSoftware(
                name="My Best Studio",
                category=SoftwareCategory.YOGA_PILATES,
                quality=SoftwareQuality.AVERAGE,
                founded_year=2014,
                last_updated=2023,
                pricing_tier="budget",
                features=["scheduling", "payments", "member_management", "mobile_app", "class_packages"],
                technology_stack=["javascript", "php", "mysql"],
                detection_signatures=[
                    "mybeststudio.com",
                    "mbs-api",
                    "mybeststudio-widget",
                    "mbs-schedule"
                ],
                mobile_app=True,
                api_available=False,
                integrations=["stripe", "paypal", "mailchimp"],
                market_share="niche",
                target_gym_size=["small"],
                strengths=["yoga_focused", "affordable", "class_packages", "simple"],
                weaknesses=["limited_features", "small_market", "basic_reporting", "no_api"],
                website="https://www.mybeststudio.com"
            ),
            
            GymSoftware(
                name="RhinoFit",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.AVERAGE,
                founded_year=2006,
                last_updated=2023,
                pricing_tier="mid_range",
                features=["member_management", "scheduling", "billing", "pos", "access_control", "mobile_app"],
                technology_stack=["javascript", "php", "mysql", "aws"],
                detection_signatures=[
                    "rhinofit.ca",
                    "rhinofit-api",
                    "rhino-fit",
                    "rf-widget"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["stripe", "quickbooks", "mailchimp"],
                market_share="niche",
                target_gym_size=["small", "medium"],
                strengths=["canadian_focused", "comprehensive", "good_support"],
                weaknesses=["limited_us_market", "dated_ui", "complex_pricing"],
                website="https://www.rhinofit.ca"
            ),
            
            # Generic/Non-Fitness Solutions Often Used by Gyms
            GymSoftware(
                name="Square",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.BASIC,
                founded_year=2009,
                last_updated=2024,
                pricing_tier="budget",
                features=["payments", "pos", "basic_scheduling", "invoicing", "inventory"],
                technology_stack=["javascript", "react", "ruby", "java"],
                detection_signatures=[
                    "squareup.com",
                    "square-api",
                    "square-payment",
                    "sq-widget",
                    "square-pos"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["quickbooks", "mailchimp", "woocommerce", "shopify"],
                market_share="high",
                target_gym_size=["small"],
                strengths=["very_affordable", "easy_setup", "good_payments", "popular"],
                weaknesses=["not_gym_specific", "no_member_management", "basic_scheduling", "limited_gym_features"],
                website="https://squareup.com"
            ),
            
            GymSoftware(
                name="Stripe",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.BASIC,
                founded_year=2010,
                last_updated=2024,
                pricing_tier="budget",
                features=["payments", "invoicing", "subscriptions", "basic_scheduling"],
                technology_stack=["javascript", "react", "ruby", "python"],
                detection_signatures=[
                    "stripe.com",
                    "stripe-api",
                    "stripe payment",
                    "stripe-js",
                    "stripe"
                ],
                mobile_app=True,
                api_available=True,
                integrations=["quickbooks", "mailchimp", "zapier", "many_others"],
                market_share="high",
                target_gym_size=["small"],
                strengths=["excellent_payments", "easy_integration", "reliable", "popular"],
                weaknesses=["not_gym_specific", "no_member_management", "limited_gym_features"],
                website="https://stripe.com"
            ),
            
            GymSoftware(
                name="WordPress + Plugins",
                category=SoftwareCategory.ALL_IN_ONE,
                quality=SoftwareQuality.BASIC,
                founded_year=2003,
                last_updated=2024,
                pricing_tier="budget",
                features=["website", "basic_scheduling", "payments", "blog", "customizable"],
                technology_stack=["wordpress", "php", "mysql", "javascript"],
                detection_signatures=[
                    "wp-content",
                    "wp-includes",
                    "wordpress",
                    "woocommerce",
                    "amelia-booking",
                    "bookly"
                ],
                mobile_app=False,
                api_available=True,
                integrations=["stripe", "paypal", "mailchimp", "woocommerce"],
                market_share="high",
                target_gym_size=["small"],
                strengths=["very_affordable", "highly_customizable", "lots_of_plugins", "seo_friendly"],
                weaknesses=["diy_setup", "maintenance_required", "security_concerns", "not_gym_specific"],
                website="https://wordpress.org"
            )
        ]
        
        # Convert to dictionary with name as key
        return {software.name.lower().replace(" ", "_"): software for software in software_list}
    
    def _build_detection_map(self) -> Dict[str, str]:
        """Build map of detection signatures to software names"""
        detection_map = {}
        
        for software_key, software in self.software_db.items():
            for signature in software.detection_signatures:
                detection_map[signature.lower()] = software_key
        
        return detection_map
    
    def get_software_by_name(self, name: str) -> GymSoftware:
        """Get software by name"""
        key = name.lower().replace(" ", "_")
        return self.software_db.get(key)
    
    def detect_software_from_technologies(self, technologies: List[Dict[str, Any]]) -> List[str]:
        """Detect gym software from BuiltWith technology list"""
        detected_software = []
        
        for tech in technologies:
            tech_name = tech.get('name', '').lower()
            tech_category = tech.get('category', '').lower()
            combined_text = f"{tech_name} {tech_category}"
            
            # Check against detection signatures
            for signature, software_key in self.detection_map.items():
                if signature in combined_text:
                    if software_key not in detected_software:
                        detected_software.append(software_key)
        
        return detected_software
    
    def detect_software_from_url(self, url: str) -> List[str]:
        """Detect software from URL patterns"""
        detected_software = []
        url_lower = url.lower()
        
        for signature, software_key in self.detection_map.items():
            if signature in url_lower:
                if software_key not in detected_software:
                    detected_software.append(software_key)
        
        return detected_software
    
    def get_software_by_category(self, category: SoftwareCategory) -> List[GymSoftware]:
        """Get all software in a specific category"""
        return [software for software in self.software_db.values() 
                if software.category == category]
    
    def get_software_by_quality(self, quality: SoftwareQuality) -> List[GymSoftware]:
        """Get all software of a specific quality tier"""
        return [software for software in self.software_db.values() 
                if software.quality == quality]
    
    def get_outdated_software(self, cutoff_year: int = 2022) -> List[GymSoftware]:
        """Get software that hasn't been updated recently"""
        return [software for software in self.software_db.values() 
                if software.last_updated <= cutoff_year]
    
    def score_software_quality(self, software_name: str) -> Dict[str, Any]:
        """Score software quality based on multiple factors"""
        software = self.get_software_by_name(software_name)
        if not software:
            return {"error": "Software not found"}
        
        # Base quality score
        quality_scores = {
            SoftwareQuality.PREMIUM: 90,
            SoftwareQuality.GOOD: 75,
            SoftwareQuality.AVERAGE: 60,
            SoftwareQuality.BASIC: 40,
            SoftwareQuality.OUTDATED: 20
        }
        
        base_score = quality_scores[software.quality]
        
        # Adjust for recency
        current_year = 2024
        years_since_update = current_year - software.last_updated
        if years_since_update > 2:
            base_score -= years_since_update * 10
        
        # Adjust for features
        feature_bonus = min(len(software.features) * 2, 20)
        base_score += feature_bonus
        
        # Mobile app bonus
        if software.mobile_app:
            base_score += 10
        
        # API availability bonus
        if software.api_available:
            base_score += 5
        
        # Integration bonus
        integration_bonus = min(len(software.integrations) * 1, 10)
        base_score += integration_bonus
        
        # Ensure score is between 0-100
        final_score = max(0, min(100, base_score))
        
        return {
            "software_name": software.name,
            "quality_score": final_score,
            "quality_tier": software.quality.value,
            "last_updated": software.last_updated,
            "years_since_update": years_since_update,
            "mobile_app": software.mobile_app,
            "api_available": software.api_available,
            "feature_count": len(software.features),
            "integration_count": len(software.integrations),
            "strengths": software.strengths,
            "weaknesses": software.weaknesses,
            "recommendation": self._get_recommendation(final_score, software)
        }
    
    def _get_recommendation(self, score: int, software: GymSoftware) -> str:
        """Get recommendation based on software score"""
        if score >= 80:
            return "Excellent choice - modern, feature-rich platform"
        elif score >= 70:
            return "Good choice - solid platform with good features"
        elif score >= 50:
            return "Acceptable - basic platform that meets minimum needs"
        elif score >= 30:
            return "Concerning - limited features, may need upgrade"
        else:
            return "RED FLAG - outdated platform, urgent upgrade recommended"
    
    def get_all_software_names(self) -> List[str]:
        """Get list of all software names for reference"""
        return [software.name for software in self.software_db.values()]
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the software database"""
        total_count = len(self.software_db)
        
        category_counts = {}
        for category in SoftwareCategory:
            category_counts[category.value] = len(self.get_software_by_category(category))
        
        quality_counts = {}
        for quality in SoftwareQuality:
            quality_counts[quality.value] = len(self.get_software_by_quality(quality))
        
        outdated_count = len(self.get_outdated_software())
        
        return {
            "total_software_count": total_count,
            "category_breakdown": category_counts,
            "quality_breakdown": quality_counts,
            "outdated_software_count": outdated_count,
            "detection_signatures": len(self.detection_map)
        }

# Singleton instance
gym_software_db = GymSoftwareDatabase()