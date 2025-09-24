#!/usr/bin/env python3
"""
AI Sales Intelligence Agent - Main Entry Point

Processes gym leads using LangChain, Groq API, and Playwright for web analysis
and personalized email generation.

Usage:
    python ai_agent/main.py --input leads.csv --output processed_leads.csv
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Optional
import pandas as pd

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_agent.config.settings import get_config, ConfigurationError  # noqa: E402
from ai_agent.utils.validators import validate_input_csv, print_validation_report  # noqa: E402
from ai_agent.utils.exceptions import ValidationError  # noqa: E402
from ai_agent.data import CSVReader, StateManager, OutputCSVManager  # noqa: E402
from ai_agent.agents.web_renderer import AsyncWebRenderer  # noqa: E402


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="AI Sales Intelligence Agent for Gym Lead Processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python ai_agent/main.py --input gym_leads.csv --output processed_leads.csv
    python ai_agent/main.py --input data/leads.csv

Environment Variables:
    GROQ_API_KEY: Required Groq API key for AI processing
    GROQ_MODEL_NAME: Model name (default: meta-llama/llama-4-scout-17b-16e-instruct)
    CHUNK_SIZE: Processing chunk size (default: 200)
    TIMEOUT_SECONDS: Timeout for operations (default: 15)
        """
    )

    parser.add_argument(
        '--input',
        required=True,
        help='Input CSV file path containing gym leads (must have gym_name and website_url columns)'
    )

    parser.add_argument(
        '--output',
        default='processed_gyms.csv',
        help='Output CSV file path for processed results (default: processed_gyms.csv)'
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Only validate input file and configuration, do not process'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Process data without making API calls (for testing pipeline)'
    )

    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume processing from where it left off (skip existing entries in output)'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging and progress details'
    )

    parser.add_argument(
        '--max-rows',
        type=int,
        help='Maximum number of rows to process (for testing with large files)'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='AI Sales Intelligence Agent v1.0.0'
    )

    return parser.parse_args()


def validate_arguments(args) -> bool:
    """Validate command line arguments"""
    valid = True

    # Validate input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"✗ Input file not found: {args.input}")
        valid = False
    elif not input_path.is_file():
        print(f"✗ Input path is not a file: {args.input}")
        valid = False

    # Validate output directory is writable
    output_path = Path(args.output)
    output_dir = output_path.parent
    if not output_dir.exists():
        print(f"✗ Output directory does not exist: {output_dir}")
        valid = False
    elif not os.access(output_dir, os.W_OK):
        print(f"✗ Output directory is not writable: {output_dir}")
        valid = False

    # Validate max_rows if specified
    if args.max_rows is not None and args.max_rows <= 0:
        print(f"✗ --max-rows must be positive, got: {args.max_rows}")
        valid = False

    # Check for conflicting options
    if args.validate_only and args.dry_run:
        print("✗ Cannot use --validate-only with --dry-run")
        valid = False

    if args.validate_only and args.resume:
        print("✗ Cannot use --validate-only with --resume")
        valid = False

    return valid


def validate_input_file(input_path: str, max_rows: Optional[int] = None,
                        verbose: bool = False) -> bool:
    """Validate input CSV file with comprehensive checks using CSVReader"""
    try:
        # Use CSVReader for validation (includes column mapping)
        csv_reader = CSVReader(input_path, auto_map_columns=True)

        # Get column info with mapping applied
        column_info = csv_reader.get_column_info()

        # Validate the basic structure first
        if not column_info['has_all_required']:
            print(f"✗ Missing required columns after mapping: {column_info['missing_required']}")
            print(f"  Original columns: {column_info['columns']}")
            if column_info['column_mappings']:
                print(f"  Applied mappings: {column_info['column_mappings']}")
            return False

        # Run comprehensive validation from utils
        validation_result = validate_input_csv(input_path, max_rows=max_rows,
                                               sample_urls=5)

        # Print detailed report
        print_validation_report(validation_result, verbose=verbose)

        # Return validation status (accept if CSVReader can handle it)
        return True

    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected validation error: {e}")
        return False


async def process_gym_leads(input_file: str, output_file: str, max_rows: Optional[int] = None,
                            resume: bool = False, dry_run: bool = False, verbose: bool = False,
                            config=None) -> bool:
    """
    Process gym leads using the new data pipeline

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        max_rows: Maximum rows to process
        resume: Whether to resume from existing output
        dry_run: Whether to skip API calls
        verbose: Whether to show detailed progress
        config: Configuration object

    Returns:
        True if processing succeeded, False otherwise
    """
    try:
        print(f"\n📊 Processing gym leads: {input_file}")
        print(f"📤 Output will be saved to: {output_file}")

        # Initialize CSV reader
        csv_reader = CSVReader(input_file, auto_map_columns=True)

        # Validate CSV structure
        column_info = csv_reader.get_column_info()
        if not column_info['has_all_required']:
            print(f"✗ Missing required columns: {column_info['missing_required']}")
            return False

        row_count = csv_reader.get_row_count()
        print(f"📈 Input file: {row_count} total rows")

        if max_rows:
            process_rows = min(max_rows, row_count)
            print(f"🔢 Processing limited to: {process_rows} rows")
        else:
            process_rows = row_count

        # Initialize state manager for resumption
        state_manager = StateManager(input_file, output_file)

        # Initialize output manager
        output_manager = OutputCSVManager(output_file, include_metadata=True)

        # Load input data
        input_df = csv_reader.read_csv(max_rows=max_rows)
        print(f"✓ Loaded input data: {len(input_df)} rows, {len(input_df.columns)} columns")

        # Define output schema
        schema = output_manager.define_output_schema(input_df)
        print(f"✓ Defined output schema: {schema['total_columns']} total columns")

        # Check for existing output and resume capability
        if resume:
            output_analysis = state_manager.analyze_existing_output()
            if output_analysis['can_resume']:
                print(f"🔄 Found existing output: {output_analysis['processed_count']} "
                      f"rows already processed")

                # Find resume point
                resume_info = state_manager.find_resume_point(input_df)
                if resume_info['can_resume'] and resume_info['already_processed'] > 0:
                    print(f"⏭️  Resuming from index {resume_info['resume_from_index']}")
                    print(f"   Already processed: {resume_info['already_processed']} rows")
                    print(f"   Remaining: {resume_info['remaining_to_process']} rows")
                else:
                    print("🆕 No valid resume point found - starting from beginning")
            else:
                print("🆕 No valid existing output found - starting fresh")
        else:
            print("🆕 Starting fresh (resume not enabled)")

        # Create output DataFrame
        output_df = output_manager.create_output_dataframe(input_df)

        # Create processing chunks
        chunk_size = getattr(config, 'chunk_size', 200) if config else 200
        chunks = state_manager.create_resumable_chunks(input_df, chunk_size=chunk_size)
        print(f"📦 Created {len(chunks)} processing chunks of {chunk_size} rows each")

        # Initialize web renderer for non-dry-run processing
        web_renderer = None
        if not dry_run:
            timeout_seconds = getattr(config, 'timeout_seconds', 15) if config else 15
            web_renderer = AsyncWebRenderer(
                max_workers=5,  # Parallel website processing
                timeout_seconds=timeout_seconds,
                headless=True,
                block_resources=True  # Block images/CSS for faster loading
            )
            await web_renderer.start()
            print(f"🌐 Web renderer initialized with {web_renderer.max_workers} workers")

        # Process chunks
        total_processed = 0
        total_errors = 0

        try:
            for chunk_info in chunks:
                chunk_num = chunk_info['chunk_number']
                chunk_data = chunk_info['data_slice']
                chunk_size_actual = len(chunk_data)

                print(f"\n🔄 Processing chunk {chunk_num}: {chunk_size_actual} rows")

                # Collect URLs for batch processing
                urls_to_render = []
                row_data = []

                # First pass: collect data and URLs for batch processing
                for idx, (row_idx, row) in enumerate(chunk_data.iterrows()):
                    try:
                        gym_name = row.get('gym_name', 'Unknown')
                        website_url = row.get('website_url', '')

                        # Handle NaN values from pandas
                        if pd.isna(gym_name):
                            gym_name = 'Unknown'
                        if pd.isna(website_url):
                            website_url = ''

                        # Convert to strings for safety
                        gym_name = str(gym_name)
                        website_url = str(website_url)

                        # Store row data for later processing
                        row_info = {
                            'row_idx': row_idx,
                            'gym_name': gym_name,
                            'website_url': website_url,
                            'original_row': row
                        }
                        row_data.append(row_info)

                        # Add to rendering queue if has URL and not dry run
                        if website_url and not dry_run:
                            urls_to_render.append(website_url)

                        if verbose:
                            display_url = website_url[:50] if website_url else '(no website)'
                            print(f"  Queued: {gym_name} | {display_url}")

                    except Exception as e:
                        print(f"    ✗ Error queuing row {row_idx}: {e}")
                        total_errors += 1

                # Batch render websites
                render_results = {}
                if urls_to_render and web_renderer:
                    print(f"  🌐 Rendering {len(urls_to_render)} websites...")
                    batch_results = await web_renderer.render_websites(urls_to_render)

                    # Create lookup dictionary by URL
                    for result in batch_results:
                        render_results[result.url] = result

                    successful_renders = sum(1 for r in batch_results if r.success)
                    print(f"  ✓ Rendered {successful_renders}/{len(urls_to_render)} websites successfully")

                # Second pass: process results and update output
                for row_info in row_data:
                    try:
                        row_idx = row_info['row_idx']
                        gym_name = row_info['gym_name']
                        website_url = row_info['website_url']

                        if dry_run:
                            # Simulate processing without API calls
                            analysis_data = {
                                'website_analysis': {
                                    'has_website': bool(website_url),
                                    'dry_run_mode': True
                                },
                                'business_analysis': {
                                    'gym_name': gym_name,
                                    'simulated': True
                                }
                            }

                            generated_email = f"Dry run email for {gym_name}"
                            status = 'processed'
                            confidence = 0.95

                        else:
                            # Process with real web rendering results
                            render_result = render_results.get(website_url) if website_url else None

                            if render_result and render_result.success:
                                # Successfully rendered website
                                analysis_data = {
                                    'website_analysis': {
                                        'has_website': True,
                                        'website_accessible': True,
                                        'title': render_result.title,
                                        'html_size': len(render_result.html_content),
                                        'render_time': render_result.render_time_seconds,
                                        'final_url': render_result.final_url
                                    },
                                    'business_analysis': {
                                        'gym_name': gym_name,
                                        'html_content_available': True
                                    }
                                }
                                status = 'rendered'
                                confidence = 0.90
                            elif render_result and not render_result.success:
                                # Failed to render website
                                analysis_data = {
                                    'website_analysis': {
                                        'has_website': True,
                                        'website_accessible': False,
                                        'error_type': render_result.error_type,
                                        'error_message': render_result.error_message
                                    },
                                    'business_analysis': {
                                        'gym_name': gym_name,
                                        'html_content_available': False
                                    }
                                }
                                status = 'render_failed'
                                confidence = 0.30
                            else:
                                # No website URL
                                analysis_data = {
                                    'website_analysis': {
                                        'has_website': False,
                                        'website_accessible': False
                                    },
                                    'business_analysis': {
                                        'gym_name': gym_name,
                                        'html_content_available': False
                                    }
                                }
                                status = 'no_website'
                                confidence = 0.10

                            # Placeholder email generation (TODO: Replace with real AI email generation)
                            generated_email = f"Placeholder email for {gym_name} - AI generation pending"

                        # Update row in output DataFrame
                        output_manager.update_row_results(
                            output_df, row_idx,
                            status=status,
                            analysis_data=analysis_data,
                            generated_email=generated_email,
                            confidence=confidence,
                            review_needed=(status in ['render_failed', 'no_website'])
                        )

                        total_processed += 1

                    except Exception as e:
                        print(f"    ✗ Error processing row {row_idx}: {e}")

                        # Mark row as error
                        output_manager.update_row_results(
                            output_df, row_idx,
                            status='error',
                            error_message=str(e)
                        )

                        total_errors += 1

                # Write chunk to output file (append mode)
                chunk_output = output_df.iloc[chunk_info['start_index']:chunk_info['end_index']]
                append_mode = chunk_num > 1  # Append for all chunks except the first
                output_manager.write_output_csv(chunk_output, append=append_mode)

                print(f"  ✓ Chunk {chunk_num} completed and saved")

        finally:
            # Clean up web renderer
            if web_renderer:
                await web_renderer.close()
                print("🌐 Web renderer closed")

        # Generate final summary
        print("\n📊 Processing Summary:")
        print(f"   Total rows processed: {total_processed}")
        print(f"   Total errors: {total_errors}")
        if (total_processed + total_errors) > 0:
            print(f"   Success rate: {(total_processed / (total_processed + total_errors) * 100):.1f}%")

        # Show web renderer statistics if available
        if web_renderer:
            stats = web_renderer.get_statistics()
            if stats['total_requests'] > 0:
                print(f"\n🌐 Web Rendering Statistics:")
                print(f"   Websites processed: {stats['total_requests']}")
                print(f"   Successful renders: {stats['successful_renders']}")
                print(f"   Failed renders: {stats['failed_renders']}")
                print(f"   Success rate: {stats['success_rate']:.1%}")
                print(f"   Average render time: {stats['average_render_time']:.2f}s")

        # Validate final output
        validation = output_manager.validate_output_structure(output_df)
        if validation['valid']:
            print("✓ Output validation passed")
        else:
            print(f"⚠️  Output validation warnings: {validation['warnings']}")
            if validation['errors']:
                print(f"✗ Output validation errors: {validation['errors']}")

        # Generate processing summary
        summary = output_manager.get_processing_summary(output_df)
        print(f"   Final status breakdown: {summary['status_breakdown']}")
        print(f"   Completion rate: {summary['completion_rate']:.1f}%")

        return True

    except Exception as e:
        print(f"✗ Processing failed: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        return False


def main():
    """Main entry point"""
    print("AI Sales Intelligence Agent v1.0.0")
    print("=" * 50)

    # Parse arguments
    args = parse_arguments()

    try:
        # Validate arguments first
        if not validate_arguments(args):
            sys.exit(1)

        # Load and validate configuration
        config = get_config()
        config.validate()
        print("✓ Configuration valid")

        # Display configuration (masked)
        config_display = config.display_config()
        print("  Model: {}".format(config_display['model_name']))
        print("  API Key: {}".format(config_display['groq_api_key']))

        if args.verbose:
            print("  Chunk size: {}".format(config_display['chunk_size']))
            print("  Max retries: {}".format(config_display['max_retries']))
            print("  Timeout: {}s".format(config_display['timeout_seconds']))

        # Validate input file
        if not validate_input_file(args.input, args.max_rows, args.verbose):
            sys.exit(1)

        # If validation only, exit here
        if args.validate_only:
            print("\n✓ Validation complete - ready to process")
            return

        # Show processing mode
        if args.dry_run:
            print("\n🧪 DRY RUN MODE - No API calls will be made")
        elif args.resume:
            print("\n🔄 RESUME MODE - Will skip existing processed entries")

        # Process data using new pipeline (async)
        success = asyncio.run(process_gym_leads(
            input_file=args.input,
            output_file=args.output,
            max_rows=args.max_rows,
            resume=args.resume,
            dry_run=args.dry_run,
            verbose=args.verbose,
            config=config
        ))

        if success:
            print("\n✓ Processing completed successfully")
        else:
            print("\n✗ Processing failed")
            sys.exit(1)

    except ConfigurationError as e:
        print(f"✗ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
