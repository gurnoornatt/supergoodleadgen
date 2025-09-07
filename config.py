"""
Configuration settings for Pain-Gap Audit Automation Script
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys
    SERPAPI_KEY = os.getenv('SERPAPI_KEY')
    GOOGLE_PAGESPEED_API_KEY = os.getenv('GOOGLE_PAGESPEED_API_KEY')
    BUILTWITH_API_KEY = os.getenv('BUILTWITH_API_KEY')
    GOOGLE_SHEETS_API_KEY = os.getenv('GOOGLE_SHEETS_API_KEY')
    
    # Google Sheets Configuration
    GOOGLE_SHEETS_SPREADSHEET_ID = os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID')
    GOOGLE_SHEETS_RANGE = os.getenv('GOOGLE_SHEETS_RANGE', 'Sheet1!A:Z')
    
    # Cloud Storage
    GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
    
    # Project Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 30))
    
    # Performance Thresholds
    RED_FLAG_MOBILE_SCORE_THRESHOLD = 60
    
    # Central Valley Cities (target locations)
    CENTRAL_VALLEY_CITIES = [
        'Fresno, CA',
        'Bakersfield, CA',
        'Stockton, CA',
        'Modesto, CA',
        'Visalia, CA',
        'Merced, CA',
        'Turlock, CA',
        'Hanford, CA',
        'Clovis, CA',
        'Madera, CA'
    ]
    
    # Business Categories for scraping
    BUSINESS_CATEGORIES = [
        'restaurants',
        'retail stores',
        'auto repair',
        'beauty salons',
        'fitness centers',
        'medical offices',
        'legal services',
        'real estate',
        'contractors'
    ]
    
    # Gym and Fitness Categories for specialized scraping
    GYM_FITNESS_CATEGORIES = [
        'gyms',
        'fitness centers',
        'health clubs',
        'personal trainers',
        'yoga studios',
        'pilates studios',
        'crossfit gyms',
        'martial arts schools',
        'dance studios',
        'sports clubs',
        'recreation centers',
        'swimming pools',
        'tennis clubs',
        'boxing gyms',
        'bootcamp fitness',
        'cycle studios',
        'rock climbing gyms',
        'wellness centers',
        'physical therapy',
        'sports medicine clinics'
    ]

    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present"""
        required_keys = [
            'SERPAPI_KEY',
            'GOOGLE_PAGESPEED_API_KEY',
            'GOOGLE_SHEETS_API_KEY'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(cls, key):
                missing_keys.append(key)
        
        if missing_keys:
            raise ValueError(f"Missing required configuration keys: {', '.join(missing_keys)}")
        
        return True