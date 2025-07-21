"""
Main script for Pain-Gap Audit Automation - Task 1 Implementation
"""
import argparse
from pathlib import Path
from config import Config
from logger_config import setup_logger
from lead_processor import LeadProcessor

logger = setup_logger(__name__)

def main():
    """Main function to run the lead generation and analysis pipeline"""
    parser = argparse.ArgumentParser(description='Pain-Gap Audit Automation - Lead Processing')
    parser.add_argument('--category', type=str, default='restaurants', 
                       help='Business category to search for')
    parser.add_argument('--city', type=str, default='Fresno, CA',
                       help='City to search in')
    parser.add_argument('--limit', type=int, default=20,
                       help='Maximum number of leads to process')
    parser.add_argument('--max-results', type=int, default=100,
                       help='Maximum number of leads to scrape from Google Maps')
    parser.add_argument('--output', type=str, default='leads_output.csv',
                       help='Output CSV filename')
    parser.add_argument('--test-apis', action='store_true',
                       help='Test API connections only')
    
    args = parser.parse_args()
    
    try:
        # Validate configuration
        logger.info("Starting Pain-Gap Audit Automation - Task 1")
        logger.info("Validating configuration...")
        Config.validate_config()
        logger.info("Configuration validated successfully")
        
        # Test APIs if requested
        if args.test_apis:
            test_api_connections()
            return
        
        # Initialize processor
        processor = LeadProcessor()
        
        # Search for leads
        logger.info(f"Searching for {args.category} in {args.city} (max {args.max_results} results)")
        query = f"{args.category} in {args.city}"
        leads = processor.extract_leads_from_maps(query, args.city, args.max_results)
        
        if not leads:
            logger.warning("No leads found from Google Maps search")
            return
        
        # Limit number of leads for testing
        if args.limit:
            leads = leads[:args.limit]
            logger.info(f"Limited to {len(leads)} leads for processing")
        
        # Process leads through analysis pipeline
        logger.info("Starting lead analysis pipeline...")
        processed_leads = processor.process_lead_batch(leads)
        
        # Save results
        output_file = processor.save_leads_to_csv(processed_leads, args.output)
        
        # Print summary
        red_leads = [lead for lead in processed_leads if lead['status'] == 'red']
        green_leads = [lead for lead in processed_leads if lead['status'] == 'green']
        error_leads = [lead for lead in processed_leads if lead['status'] == 'error']
        
        logger.info("="*50)
        logger.info("PROCESSING SUMMARY")
        logger.info("="*50)
        logger.info(f"Total leads processed: {len(processed_leads)}")
        logger.info(f"RED flag leads (mobile score < {Config.RED_FLAG_MOBILE_SCORE_THRESHOLD}): {len(red_leads)}")
        logger.info(f"GREEN leads: {len(green_leads)}")
        logger.info(f"Error leads: {len(error_leads)}")
        logger.info(f"Results saved to: {output_file}")
        
        if red_leads:
            logger.info("\nRED FLAG LEADS:")
            for lead in red_leads:
                score = lead.get('mobile_score', 'N/A')
                logger.info(f"  - {lead['business_name']}: {score}/100")
        
        logger.info("Task 1 completed successfully!")
        
    except Exception as e:
        logger.error(f"Critical error in main execution: {e}")
        raise

def test_api_connections():
    """Test all API connections"""
    logger.info("Testing API connections...")
    
    from api_client import SerpApiClient, GooglePageSpeedClient, BuiltWithClient
    
    # Test SerpApi
    logger.info("Testing SerpApi connection...")
    try:
        serp_client = SerpApiClient()
        test_result = serp_client.search_google_maps("test restaurant", "Fresno, CA")
        logger.info(f"✓ SerpApi working - Found {len(test_result.get('local_results', []))} results")
    except Exception as e:
        logger.error(f"✗ SerpApi failed: {e}")
    
    # Test Google PageSpeed
    logger.info("Testing Google PageSpeed Insights...")
    try:
        pagespeed_client = GooglePageSpeedClient()
        test_result = pagespeed_client.analyze_url("https://example.com")
        score = test_result.get('performance_score', 'N/A')
        logger.info(f"✓ PageSpeed Insights working - Test score: {score}/100")
    except Exception as e:
        logger.error(f"✗ PageSpeed Insights failed: {e}")
    
    # Test BuiltWith
    logger.info("Testing BuiltWith API...")
    try:
        builtwith_client = BuiltWithClient()
        test_result = builtwith_client.analyze_domain("example.com")
        tech_count = len(test_result.get('technologies', []))
        if 'error' in test_result:
            logger.warning(f"⚠ BuiltWith API key issue: {test_result['error']}")
        else:
            logger.info(f"✓ BuiltWith working - Found {tech_count} technologies")
    except Exception as e:
        logger.error(f"✗ BuiltWith failed: {e}")
    
    logger.info("API connection testing completed")

if __name__ == "__main__":
    main()