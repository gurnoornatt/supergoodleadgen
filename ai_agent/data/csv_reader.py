"""
CSV Reader and Column Validator for AI Sales Intelligence Agent
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional, List, Iterator
import logging

from ..utils.exceptions import CSVValidationError
from ..utils.validators import URLValidator


logger = logging.getLogger(__name__)


class CSVReader:
    """Handles CSV file reading and column validation"""

    REQUIRED_COLUMNS = ['gym_name', 'website_url']
    OPTIONAL_COLUMNS = ['phone', 'address', 'city', 'state', 'zip_code', 'google_business_url']

    # Column mapping for different data sources
    COLUMN_MAPPINGS = {
        'business_name': 'gym_name',
        'website': 'website_url'
    }

    def __init__(self, file_path: str, auto_map_columns: bool = True):
        """
        Initialize CSV reader with file path validation

        Args:
            file_path: Path to the CSV file to read
            auto_map_columns: Whether to automatically map column names
        """
        self.file_path = Path(file_path)
        self.auto_map_columns = auto_map_columns
        self._validate_file_exists()
        self._df_cache: Optional[pd.DataFrame] = None
        self._row_count: Optional[int] = None
        self._column_mapping: Dict[str, str] = {}

    def _validate_file_exists(self) -> None:
        """Validate that the file exists and is readable"""
        if not self.file_path.exists():
            raise CSVValidationError(f"File does not exist: {self.file_path}")

        if not self.file_path.is_file():
            raise CSVValidationError(f"Path is not a file: {self.file_path}")

        if not self.file_path.suffix.lower() in ['.csv', '.txt']:
            raise CSVValidationError(
                f"File must be CSV format (.csv/.txt), got: {self.file_path.suffix}")

        if self.file_path.stat().st_size == 0:
            raise CSVValidationError("File is empty")

        # Check for very large files (>100MB)
        size_mb = self.file_path.stat().st_size / (1024 * 1024)
        if size_mb > 100:
            logger.warning(f"Large file detected: {size_mb:.1f}MB. "
                           "Consider processing in smaller chunks.")

    def _detect_column_mappings(self, columns: List[str]) -> Dict[str, str]:
        """
        Detect column mappings automatically

        Args:
            columns: List of column names in the CSV

        Returns:
            Dictionary mapping original -> standard column names
        """
        mappings = {}

        if self.auto_map_columns:
            for original_col, standard_col in self.COLUMN_MAPPINGS.items():
                if original_col in columns:
                    mappings[original_col] = standard_col
                    logger.debug(f"Auto-mapped column: "
                                 f"{original_col} -> {standard_col}")

        return mappings

    def get_column_info(self) -> Dict[str, Any]:
        """
        Get column information without loading full dataset

        Returns:
            Dictionary with column information
        """
        try:
            # Read just the header to get column info
            sample_df = pd.read_csv(self.file_path, nrows=0)
            original_columns = list(sample_df.columns)

            # Detect column mappings
            self._column_mapping = self._detect_column_mappings(original_columns)

            # Apply column mappings to check requirements
            effective_columns = original_columns.copy()
            for original, standard in self._column_mapping.items():
                if original in effective_columns:
                    idx = effective_columns.index(original)
                    effective_columns[idx] = standard

            # Check for required columns after mapping
            missing_required = [col for col in self.REQUIRED_COLUMNS
                                if col not in effective_columns]

            # Check for unexpected columns (original names that aren't mapped or expected)
            expected_columns = set(self.REQUIRED_COLUMNS + self.OPTIONAL_COLUMNS)
            mapped_columns = set(self._column_mapping.keys())
            unexpected_columns = [
                col for col in original_columns
                if (col not in expected_columns and
                    col not in mapped_columns)
            ]

            return {
                'total_columns': len(original_columns),
                'columns': original_columns,
                'effective_columns': effective_columns,
                'column_mappings': self._column_mapping,
                'required_present': [col for col in self.REQUIRED_COLUMNS
                                     if col in effective_columns],
                'missing_required': missing_required,
                'optional_present': [col for col in self.OPTIONAL_COLUMNS
                                     if col in effective_columns],
                'unexpected_columns': unexpected_columns,
                'has_all_required': len(missing_required) == 0
            }

        except Exception as e:
            raise CSVValidationError(f"Failed to read CSV header: {e}")

    def validate_columns(self) -> Dict[str, Any]:
        """
        Validate column structure and content

        Returns:
            Validation result dictionary
        """
        column_info = self.get_column_info()

        validation_result = {
            'file_path': str(self.file_path),
            'column_validation': column_info,
            'data_validation': {},
            'errors': [],
            'warnings': [],
            'validation_passed': True
        }

        # Check for missing required columns
        if column_info['missing_required']:
            validation_result['errors'].append(
                f"Missing required columns: {column_info['missing_required']}")
            validation_result['validation_passed'] = False

        # Warn about unexpected columns
        if column_info['unexpected_columns']:
            validation_result['warnings'].append(
                f"Unexpected columns found: "
                f"{column_info['unexpected_columns']}")

        # If we have required columns, do data validation
        if column_info['has_all_required']:
            try:
                data_validation = self._validate_data_quality()
                validation_result['data_validation'] = data_validation

                # Add warnings for data quality issues
                for col, stats in data_validation.items():
                    if stats.get('null_percentage', 0) > 50:
                        validation_result['warnings'].append(
                            f"Column '{col}' has "
                            f"{stats['null_percentage']:.1f}% missing values")

                    if (col == 'website_url' and
                            stats.get('invalid_url_percentage', 0) > 20):
                        validation_result['warnings'].append(
                            f"Column 'website_url' has "
                            f"{stats['invalid_url_percentage']:.1f}% invalid URLs")

            except Exception as e:
                validation_result['errors'].append(f"Data validation failed: {e}")
                validation_result['validation_passed'] = False

        return validation_result

    def _validate_data_quality(self, sample_size: int = 1000) -> Dict[str, Any]:
        """
        Validate data quality for required columns

        Args:
            sample_size: Number of rows to sample for validation

        Returns:
            Data quality statistics
        """
        # Read a sample for data validation
        try:
            sample_df = pd.read_csv(self.file_path, nrows=sample_size)
            # Apply column mappings
            sample_df = self._apply_column_mappings(sample_df)
        except Exception as e:
            raise CSVValidationError(f"Failed to read CSV data: {e}")

        validation_stats = {}

        for col in self.REQUIRED_COLUMNS:
            if col not in sample_df.columns:
                continue

            col_data = sample_df[col]
            total_rows = len(col_data)

            # Basic statistics
            null_count = col_data.isnull().sum()
            empty_count = (col_data == '').sum() if col_data.dtype == 'object' else 0
            valid_count = total_rows - null_count - empty_count

            stats = {
                'total_rows': total_rows,
                'null_count': null_count,
                'empty_count': empty_count,
                'valid_count': valid_count,
                'null_percentage': ((null_count / total_rows * 100)
                                    if total_rows > 0 else 0),
                'valid_percentage': ((valid_count / total_rows * 100)
                                     if total_rows > 0 else 0)
            }

            # Special validation for website_url column
            if col == 'website_url' and valid_count > 0:
                valid_urls = col_data.dropna()
                valid_urls = valid_urls[valid_urls != '']

                if len(valid_urls) > 0:
                    # Sample up to 100 URLs for validation
                    url_sample = valid_urls.head(min(100, len(valid_urls)))
                    valid_url_count = sum(URLValidator.is_valid_url(url)
                                          for url in url_sample)

                    stats.update({
                        'urls_tested': len(url_sample),
                        'valid_urls': valid_url_count,
                        'invalid_urls': len(url_sample) - valid_url_count,
                        'invalid_url_percentage': (
                            (len(url_sample) - valid_url_count) /
                            len(url_sample) * 100)
                    })

            # Special validation for gym_name column
            if col == 'gym_name' and valid_count > 0:
                valid_names = col_data.dropna()
                valid_names = valid_names[valid_names != '']

                if len(valid_names) > 0:
                    # Check for very short or very long names
                    short_names = (valid_names.str.len() < 3).sum()
                    long_names = (valid_names.str.len() > 100).sum()

                    stats.update({
                        'short_names': short_names,
                        'long_names': long_names,
                        'avg_name_length': valid_names.str.len().mean()
                    })

            validation_stats[col] = stats

        return validation_stats

    def get_row_count(self) -> int:
        """
        Get total number of rows in the CSV file

        Returns:
            Total row count
        """
        if self._row_count is None:
            try:
                # Use efficient row counting without loading data
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self._row_count = sum(1 for line in f) - 1  # Subtract header
            except Exception as e:
                # Fallback to pandas
                try:
                    df = pd.read_csv(self.file_path, usecols=[0])  # Read just first column
                    self._row_count = len(df)
                except Exception:
                    raise CSVValidationError(f"Cannot determine row count: {e}")

        return self._row_count

    def _apply_column_mappings(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply column mappings to a DataFrame

        Args:
            df: DataFrame to apply mappings to

        Returns:
            DataFrame with mapped column names
        """
        if not self._column_mapping:
            # Get column mappings if not already detected
            self.get_column_info()

        if self._column_mapping:
            df = df.rename(columns=self._column_mapping)
            logger.debug(f"Applied column mappings: {self._column_mapping}")

        return df

    def read_csv(self, max_rows: Optional[int] = None) -> pd.DataFrame:
        """
        Read the entire CSV file into memory

        Args:
            max_rows: Maximum number of rows to read

        Returns:
            Pandas DataFrame with standardized column names
        """
        try:
            df = pd.read_csv(self.file_path, nrows=max_rows)

            # Apply column mappings
            df = self._apply_column_mappings(df)

            # Validate required columns exist after mapping
            missing_cols = [col for col in self.REQUIRED_COLUMNS
                            if col not in df.columns]
            if missing_cols:
                raise CSVValidationError(
                    f"Missing required columns after mapping: {missing_cols}")

            logger.info(f"Successfully read CSV: {len(df)} rows, {len(df.columns)} columns")
            return df

        except CSVValidationError:
            raise
        except Exception as e:
            raise CSVValidationError(f"Failed to read CSV file: {e}")

    def create_chunked_reader(self, chunk_size: int = 200) -> Iterator[pd.DataFrame]:
        """
        Create a chunked reader for processing large CSV files

        Args:
            chunk_size: Number of rows per chunk

        Yields:
            DataFrame chunks with standardized column names
        """
        try:
            # Validate columns first
            column_info = self.get_column_info()
            if not column_info['has_all_required']:
                raise CSVValidationError(
                    f"Missing required columns after mapping: "
                    f"{column_info['missing_required']}")

            logger.info(f"Creating chunked reader with chunk_size={chunk_size}")
            if self._column_mapping:
                logger.info(f"Will apply column mappings: {self._column_mapping}")

            # Create the chunked reader
            chunk_reader = pd.read_csv(self.file_path, chunksize=chunk_size)

            chunk_num = 0
            for chunk in chunk_reader:
                chunk_num += 1

                # Apply column mappings to each chunk
                chunk = self._apply_column_mappings(chunk)

                logger.debug(f"Processing chunk {chunk_num}: {len(chunk)} rows")
                yield chunk

        except CSVValidationError:
            raise
        except Exception as e:
            raise CSVValidationError(f"Failed to create chunked reader: {e}")


class CSVProcessor:
    """Processes CSV data with chunking and validation"""

    def __init__(self, csv_reader: CSVReader):
        """
        Initialize processor with CSV reader

        Args:
            csv_reader: CSVReader instance
        """
        self.csv_reader = csv_reader
        self.processed_count = 0
        self.error_count = 0

    def get_processable_rows(self, chunk: pd.DataFrame) -> pd.DataFrame:
        """
        Filter chunk to get only processable rows

        Args:
            chunk: DataFrame chunk

        Returns:
            Filtered DataFrame with only valid rows
        """
        # Start with all rows
        valid_mask = pd.Series([True] * len(chunk), index=chunk.index)

        # Filter out rows with missing gym_name
        if 'gym_name' in chunk.columns:
            valid_mask &= chunk['gym_name'].notna()
            valid_mask &= (chunk['gym_name'] != '')

        # Filter out rows with missing or invalid website_url
        if 'website_url' in chunk.columns:
            valid_mask &= chunk['website_url'].notna()
            valid_mask &= (chunk['website_url'] != '')

            # Additional URL validation
            for idx in chunk.index:
                if valid_mask[idx]:
                    url = chunk.loc[idx, 'website_url']
                    if not URLValidator.is_valid_url(str(url)):
                        valid_mask[idx] = False

        # Get filtered data
        processable_chunk = chunk[valid_mask].copy()

        # Log filtering results
        filtered_count = len(chunk) - len(processable_chunk)
        if filtered_count > 0:
            logger.debug(f"Filtered out {filtered_count} invalid rows from chunk")

        return processable_chunk

    def validate_chunk(self, chunk: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate a chunk of data

        Args:
            chunk: DataFrame chunk to validate

        Returns:
            Validation results
        """
        result = {
            'total_rows': len(chunk),
            'valid_rows': 0,
            'invalid_rows': 0,
            'missing_gym_name': 0,
            'missing_website_url': 0,
            'invalid_urls': 0,
            'errors': []
        }

        try:
            processable_chunk = self.get_processable_rows(chunk)
            result['valid_rows'] = len(processable_chunk)
            result['invalid_rows'] = result['total_rows'] - result['valid_rows']

            # Count specific issues
            if 'gym_name' in chunk.columns:
                result['missing_gym_name'] = (
                    chunk['gym_name'].isnull().sum() +
                    (chunk['gym_name'] == '').sum()
                )

            if 'website_url' in chunk.columns:
                result['missing_website_url'] = (
                    chunk['website_url'].isnull().sum() +
                    (chunk['website_url'] == '').sum()
                )

                # Count invalid URLs
                valid_urls = chunk['website_url'].dropna()
                valid_urls = valid_urls[valid_urls != '']
                if len(valid_urls) > 0:
                    invalid_count = sum(
                        1 for url in valid_urls
                        if not URLValidator.is_valid_url(str(url))
                    )
                    result['invalid_urls'] = invalid_count

        except Exception as e:
            result['errors'].append(f"Chunk validation failed: {e}")

        return result

    def process_chunks(self, chunk_size: int = 200,
                       max_chunks: Optional[int] = None) -> Iterator[Dict[str, Any]]:
        """
        Process CSV file in chunks

        Args:
            chunk_size: Number of rows per chunk
            max_chunks: Maximum number of chunks to process

        Yields:
            Processing results for each chunk
        """
        chunk_reader = self.csv_reader.create_chunked_reader(chunk_size)

        chunks_processed = 0

        for chunk in chunk_reader:
            # Check if we've hit the max chunks limit
            if max_chunks and chunks_processed >= max_chunks:
                break

            chunks_processed += 1

            # Validate and process chunk
            validation_result = self.validate_chunk(chunk)
            processable_chunk = self.get_processable_rows(chunk)

            result = {
                'chunk_number': chunks_processed,
                'chunk_size': len(chunk),
                'processable_rows': len(processable_chunk),
                'validation': validation_result,
                'data': processable_chunk
            }

            # Update counters
            self.processed_count += len(processable_chunk)
            self.error_count += validation_result['invalid_rows']

            yield result

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics

        Returns:
            Processing statistics
        """
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'total_count': self.processed_count + self.error_count,
            'success_rate': ((self.processed_count /
                              (self.processed_count + self.error_count) * 100)
                             if (self.processed_count + self.error_count) > 0 else 0)
        }
