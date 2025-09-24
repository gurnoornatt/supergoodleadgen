"""
State Manager for resumption logic in AI Sales Intelligence Agent
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, Set, List
import logging


logger = logging.getLogger(__name__)


class StateManager:
    """Manages processing state and resumption logic"""

    def __init__(self, input_file: str, output_file: str):
        """
        Initialize state manager

        Args:
            input_file: Path to input CSV file
            output_file: Path to output CSV file
        """
        self.input_file = Path(input_file)
        self.output_file = Path(output_file)
        self._processed_urls: Optional[Set[str]] = None
        self._output_exists = False
        self._output_valid = False
        self._last_processed_index: Optional[int] = None

    def analyze_existing_output(self) -> Dict[str, Any]:
        """
        Analyze existing output file to determine state

        Returns:
            Analysis results including processed URLs and validity
        """
        result = {
            'output_exists': False,
            'output_valid': False,
            'processed_count': 0,
            'processed_urls': set(),
            'corrupted': False,
            'corruption_details': [],
            'can_resume': False,
            'errors': []
        }

        if not self.output_file.exists():
            logger.info("No existing output file found - starting fresh")
            return result

        result['output_exists'] = True
        logger.info(f"Found existing output file: {self.output_file}")

        try:
            # Try to read the output file
            output_df = pd.read_csv(self.output_file)
            logger.info(f"Successfully read output file: {len(output_df)} rows")

            # Validate basic structure
            if 'website_url' not in output_df.columns:
                result['errors'].append("Output file missing 'website_url' column")
                result['corrupted'] = True
                return result

            # Extract processed URLs
            processed_urls = set()
            for idx, row in output_df.iterrows():
                url = row.get('website_url')
                if pd.notna(url) and url != '':
                    processed_urls.add(str(url).strip())

            result['processed_urls'] = processed_urls
            result['processed_count'] = len(processed_urls)
            result['output_valid'] = True
            result['can_resume'] = True

            # Check for corruption indicators
            corruption_checks = self._check_output_corruption(output_df)
            result.update(corruption_checks)

            logger.info(f"Output analysis: {len(processed_urls)} unique URLs processed")

        except pd.errors.EmptyDataError:
            result['errors'].append("Output file is empty")
            result['corrupted'] = True
        except pd.errors.ParserError as e:
            result['errors'].append(f"Output file parsing error: {e}")
            result['corrupted'] = True
        except Exception as e:
            result['errors'].append(f"Unexpected error reading output file: {e}")
            result['corrupted'] = True

        # Cache results
        self._output_exists = result['output_exists']
        self._output_valid = result['output_valid']
        self._processed_urls = result['processed_urls']

        return result

    def _check_output_corruption(self, output_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Check for corruption indicators in output file

        Args:
            output_df: Output DataFrame to check

        Returns:
            Corruption analysis results
        """
        corruption_result = {
            'corrupted': False,
            'corruption_details': []
        }

        # Check 1: Completely empty rows
        empty_rows = output_df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            corruption_result['corruption_details'].append(
                f"{empty_rows} completely empty rows found")

        # Check 2: Missing critical data in recent rows
        if len(output_df) > 0:
            last_10_rows = output_df.tail(10)
            missing_urls = last_10_rows['website_url'].isnull().sum()
            if missing_urls > 5:  # More than half of last 10 rows missing URLs
                corruption_result['corruption_details'].append(
                    f"High missing URL rate in recent rows: {missing_urls}/10")

        # Check 3: Duplicate URLs (should not happen in normal processing)
        if 'website_url' in output_df.columns:
            valid_urls = output_df['website_url'].dropna()
            valid_urls = valid_urls[valid_urls != '']
            duplicates = valid_urls.duplicated().sum()
            if duplicates > 0:
                corruption_result['corruption_details'].append(
                    f"{duplicates} duplicate URLs found")

        # Mark as corrupted if we found issues
        if corruption_result['corruption_details']:
            corruption_result['corrupted'] = True
            logger.warning(f"Output corruption detected: "
                           f"{len(corruption_result['corruption_details'])} issues")

        return corruption_result

    def find_resume_point(self, input_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Find the point where processing should resume

        Args:
            input_df: Input DataFrame to compare against

        Returns:
            Resume point analysis
        """
        result = {
            'can_resume': False,
            'resume_from_index': 0,
            'total_input_rows': len(input_df),
            'already_processed': 0,
            'remaining_to_process': len(input_df),
            'resume_percentage': 0.0,
            'errors': []
        }

        # Validate input has required column
        if 'website_url' not in input_df.columns:
            result['errors'].append("Input file missing 'website_url' column")
            return result

        # If no existing output, start from beginning
        if not self._output_exists or not self._output_valid:
            logger.info("No valid output file - starting from beginning")
            return result

        # Get processed URLs
        if self._processed_urls is None:
            output_analysis = self.analyze_existing_output()
            if not output_analysis['can_resume']:
                return result

        processed_urls = self._processed_urls
        logger.info(f"Comparing against {len(processed_urls)} processed URLs")

        # Strategy: Find all processed rows, then determine resume point
        processed_indices = []
        processed_count = 0

        for idx, row in input_df.iterrows():
            url = row.get('website_url')
            if pd.notna(url) and url != '':
                url_clean = str(url).strip()
                if url_clean in processed_urls:
                    processed_indices.append(idx)
                    processed_count += 1

        # Determine resume point
        if processed_indices:
            # Sort indices to find consecutive sequence from beginning
            processed_indices.sort()

            # Find the longest consecutive sequence from the beginning
            last_consecutive_index = -1
            for i, idx in enumerate(processed_indices):
                if idx == i:  # Consecutive from 0
                    last_consecutive_index = idx
                else:
                    break

            # Special case: if all rows are processed, no need to continue
            if processed_count == len(input_df):
                resume_index = len(input_df)  # Resume beyond end (nothing to do)
                remaining = 0
            else:
                # Resume from the next position after last consecutive
                resume_index = last_consecutive_index + 1
                remaining = len(input_df) - resume_index

            result.update({
                'can_resume': True,
                'resume_from_index': resume_index,
                'already_processed': processed_count,
                'remaining_to_process': remaining,
                'resume_percentage': (processed_count / len(input_df) * 100)
            })

            logger.info(f"Resume point found: index {resume_index}, "
                        f"{processed_count} URLs processed, "
                        f"{remaining} remaining")

        else:
            logger.info("No processed URLs found in input - starting fresh")

        return result

    def create_resumable_chunks(self, input_df: pd.DataFrame,
                                chunk_size: int = 200) -> List[Dict[str, Any]]:
        """
        Create chunks for processing, skipping already processed data

        Args:
            input_df: Input DataFrame
            chunk_size: Size of each chunk

        Returns:
            List of chunk information dictionaries
        """
        # Find resume point
        resume_info = self.find_resume_point(input_df)

        if not resume_info['can_resume'] or resume_info['resume_from_index'] == 0:
            # Process everything
            start_index = 0
            logger.info("Creating chunks for full dataset")
        else:
            # Skip already processed data
            start_index = resume_info['resume_from_index']
            logger.info(f"Creating chunks starting from index {start_index} "
                        f"(skipping {resume_info['already_processed']} processed rows)")

        # Create chunk definitions
        chunks = []
        total_rows = len(input_df)
        current_index = start_index

        chunk_num = 1
        while current_index < total_rows:
            end_index = min(current_index + chunk_size, total_rows)
            chunk_rows = end_index - current_index

            chunks.append({
                'chunk_number': chunk_num,
                'start_index': current_index,
                'end_index': end_index,
                'chunk_size': chunk_rows,
                'is_partial': chunk_rows < chunk_size,
                'data_slice': input_df.iloc[current_index:end_index].copy()
            })

            current_index = end_index
            chunk_num += 1

        logger.info(f"Created {len(chunks)} chunks for processing "
                    f"({total_rows - start_index} total rows)")

        return chunks

    def validate_resume_integrity(self, input_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate that resumption is safe and consistent

        Args:
            input_df: Input DataFrame

        Returns:
            Integrity validation results
        """
        result = {
            'is_safe': True,
            'warnings': [],
            'errors': [],
            'input_analysis': {},
            'consistency_check': {}
        }

        try:
            # Analyze input file
            total_input_urls = set()
            for idx, row in input_df.iterrows():
                url = row.get('website_url')
                if pd.notna(url) and url != '':
                    total_input_urls.add(str(url).strip())

            result['input_analysis'] = {
                'total_rows': len(input_df),
                'unique_urls': len(total_input_urls),
                'has_duplicates': len(total_input_urls) < len(input_df)
            }

            # Check consistency with processed data
            if self._processed_urls:
                processed_urls = self._processed_urls

                # URLs in output but not in input
                orphaned_urls = processed_urls - total_input_urls
                if orphaned_urls:
                    result['warnings'].append(
                        f"{len(orphaned_urls)} URLs in output not found in input")

                # URLs in input that were processed
                overlap = processed_urls & total_input_urls
                result['consistency_check'] = {
                    'processed_urls_in_input': len(overlap),
                    'orphaned_urls': len(orphaned_urls),
                    'overlap_percentage': (len(overlap) / len(processed_urls) * 100
                                           if processed_urls else 0)
                }

                # Safety check: if too many orphaned URLs, might be unsafe
                if len(orphaned_urls) > len(processed_urls) * 0.5:
                    result['errors'].append(
                        "Too many orphaned URLs - input file may have changed significantly")
                    result['is_safe'] = False

        except Exception as e:
            result['errors'].append(f"Integrity validation failed: {e}")
            result['is_safe'] = False

        return result

    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state

        Returns:
            State summary
        """
        if not hasattr(self, '_state_summary'):
            # Analyze on first call
            output_analysis = self.analyze_existing_output()
            self._state_summary = {
                'input_file': str(self.input_file),
                'output_file': str(self.output_file),
                'output_exists': output_analysis['output_exists'],
                'output_valid': output_analysis['output_valid'],
                'processed_count': output_analysis['processed_count'],
                'can_resume': output_analysis['can_resume'],
                'corruption_detected': output_analysis['corrupted']
            }

        return self._state_summary

    def backup_corrupted_output(self) -> Optional[str]:
        """
        Create a backup of corrupted output file

        Returns:
            Path to backup file if created, None otherwise
        """
        if not self.output_file.exists():
            return None

        try:
            backup_path = self.output_file.with_suffix('.corrupted.backup.csv')

            # Copy the corrupted file
            import shutil
            shutil.copy2(self.output_file, backup_path)

            logger.info(f"Created backup of corrupted output: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"Failed to backup corrupted output: {e}")
            return None
