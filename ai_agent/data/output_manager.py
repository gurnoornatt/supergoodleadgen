"""
Output CSV Manager for AI Sales Intelligence Agent
"""

import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class OutputCSVManager:
    """Manages output CSV structure and writing for gym lead analysis"""

    # Required output columns that we add to original data
    ANALYSIS_COLUMNS = [
        'status',           # processing status: pending, processed, error, skipped
        'error_message',    # error details if processing failed
        'analysis_json',    # JSON string of analysis results
        'generated_email'   # generated email content
    ]

    # Optional metadata columns we may add
    METADATA_COLUMNS = [
        'processing_timestamp',  # when this row was processed
        'processing_version',    # version of the analysis system
        'analysis_confidence',   # confidence score of analysis
        'review_needed'         # flag if human review needed
    ]

    def __init__(self, output_file: str, include_metadata: bool = True):
        """
        Initialize output manager

        Args:
            output_file: Path to output CSV file
            include_metadata: Whether to include metadata columns
        """
        self.output_file = Path(output_file)
        self.include_metadata = include_metadata
        self._original_columns: Optional[List[str]] = None
        self._output_columns: Optional[List[str]] = None

    def define_output_schema(self, input_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Define output CSV schema based on input data

        Args:
            input_df: Input DataFrame to analyze

        Returns:
            Schema definition dictionary
        """
        # Get original columns
        original_columns = list(input_df.columns)
        self._original_columns = original_columns

        # Build output columns list
        output_columns = original_columns.copy()
        output_columns.extend(self.ANALYSIS_COLUMNS)

        if self.include_metadata:
            output_columns.extend(self.METADATA_COLUMNS)

        self._output_columns = output_columns

        schema = {
            'input_columns': original_columns,
            'analysis_columns': self.ANALYSIS_COLUMNS,
            'metadata_columns': self.METADATA_COLUMNS if self.include_metadata else [],
            'output_columns': output_columns,
            'total_columns': len(output_columns),
            'column_mapping': self._create_column_mapping()
        }

        logger.info(f"Defined output schema: {len(original_columns)} input + "
                    f"{len(self.ANALYSIS_COLUMNS)} analysis + "
                    f"{len(self.METADATA_COLUMNS) if self.include_metadata else 0} metadata = "
                    f"{len(output_columns)} total columns")

        return schema

    def _create_column_mapping(self) -> Dict[str, Dict[str, Any]]:
        """
        Create detailed column mapping with types and descriptions

        Returns:
            Column mapping dictionary
        """
        mapping = {}

        # Map original columns (preserve as-is)
        if self._original_columns:
            for col in self._original_columns:
                mapping[col] = {
                    'type': 'original',
                    'dtype': 'object',  # Default to object, will be inferred from data
                    'description': f"Original column: {col}",
                    'required': True if col in ['gym_name', 'website_url'] else False
                }

        # Map analysis columns
        analysis_mapping = {
            'status': {
                'type': 'analysis',
                'dtype': 'object',
                'description': 'Processing status: pending, processed, error, skipped',
                'required': True,
                'default': 'pending'
            },
            'error_message': {
                'type': 'analysis',
                'dtype': 'object',
                'description': 'Error details if processing failed',
                'required': False,
                'default': None
            },
            'analysis_json': {
                'type': 'analysis',
                'dtype': 'object',
                'description': 'JSON string containing analysis results',
                'required': False,
                'default': None
            },
            'generated_email': {
                'type': 'analysis',
                'dtype': 'object',
                'description': 'Generated email content for the gym',
                'required': False,
                'default': None
            }
        }

        # Map metadata columns
        metadata_mapping = {
            'processing_timestamp': {
                'type': 'metadata',
                'dtype': 'object',
                'description': 'ISO timestamp when row was processed',
                'required': False,
                'default': None
            },
            'processing_version': {
                'type': 'metadata',
                'dtype': 'object',
                'description': 'Version of analysis system used',
                'required': False,
                'default': '1.0.0'
            },
            'analysis_confidence': {
                'type': 'metadata',
                'dtype': 'float64',
                'description': 'Confidence score of analysis (0.0-1.0)',
                'required': False,
                'default': None
            },
            'review_needed': {
                'type': 'metadata',
                'dtype': 'bool',
                'description': 'Flag indicating if human review is needed',
                'required': False,
                'default': False
            }
        }

        mapping.update(analysis_mapping)
        if self.include_metadata:
            mapping.update(metadata_mapping)

        return mapping

    def create_output_dataframe(self, input_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create output DataFrame with proper structure

        Args:
            input_df: Input DataFrame

        Returns:
            Empty output DataFrame with proper columns and dtypes
        """
        if self._output_columns is None:
            self.define_output_schema(input_df)

        # Start with input data
        output_df = input_df.copy()

        # Add analysis columns with defaults
        output_df['status'] = 'pending'
        output_df['error_message'] = None
        output_df['analysis_json'] = None
        output_df['generated_email'] = None

        # Add metadata columns if enabled
        if self.include_metadata:
            output_df['processing_timestamp'] = None
            output_df['processing_version'] = '1.0.0'
            output_df['analysis_confidence'] = None
            output_df['review_needed'] = False

        # Ensure column order matches schema
        output_df = output_df[self._output_columns]

        logger.info(f"Created output DataFrame: {len(output_df)} rows, "
                    f"{len(output_df.columns)} columns")
        return output_df

    def serialize_analysis_data(self, analysis_data: Dict[str, Any]) -> str:
        """
        Serialize analysis data to JSON string for CSV storage

        Args:
            analysis_data: Analysis results dictionary

        Returns:
            JSON string safe for CSV storage
        """
        try:
            # Convert to JSON with proper escaping
            json_str = json.dumps(analysis_data, ensure_ascii=True, separators=(',', ':'))

            # Additional CSV safety: escape quotes and newlines
            json_str = json_str.replace('"', '""')  # Escape quotes for CSV
            json_str = json_str.replace('\n', '\\n')  # Escape newlines
            json_str = json_str.replace('\r', '\\r')  # Escape carriage returns

            return json_str

        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize analysis data: {e}")
            return json.dumps({"error": f"Serialization failed: {str(e)}"})

    def deserialize_analysis_data(self, json_str: str) -> Dict[str, Any]:
        """
        Deserialize analysis data from JSON string

        Args:
            json_str: JSON string from CSV

        Returns:
            Analysis data dictionary
        """
        if not json_str or pd.isna(json_str):
            return {}

        try:
            # Reverse CSV escaping
            json_str = json_str.replace('""', '"')  # Unescape quotes
            json_str = json_str.replace('\\n', '\n')  # Unescape newlines
            json_str = json_str.replace('\\r', '\r')  # Unescape carriage returns

            return json.loads(json_str)

        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Failed to deserialize analysis data: {e}")
            return {"error": f"Deserialization failed: {str(e)}"}

    def update_row_results(self, output_df: pd.DataFrame, row_index: int,
                           status: str, analysis_data: Optional[Dict[str, Any]] = None,
                           error_message: Optional[str] = None,
                           generated_email: Optional[str] = None,
                           confidence: Optional[float] = None,
                           review_needed: bool = False) -> None:
        """
        Update a single row with processing results

        Args:
            output_df: Output DataFrame to update
            row_index: Index of row to update
            status: Processing status
            analysis_data: Analysis results dictionary
            error_message: Error message if processing failed
            generated_email: Generated email content
            confidence: Analysis confidence score
            review_needed: Whether human review is needed
        """
        # Update status
        output_df.at[row_index, 'status'] = status

        # Update error message
        if error_message:
            output_df.at[row_index, 'error_message'] = str(error_message)

        # Update analysis data
        if analysis_data:
            serialized_data = self.serialize_analysis_data(analysis_data)
            output_df.at[row_index, 'analysis_json'] = serialized_data

        # Update generated email
        if generated_email:
            # Clean email for CSV storage
            clean_email = str(generated_email).replace('\n', '\\n').replace('\r', '\\r')
            output_df.at[row_index, 'generated_email'] = clean_email

        # Update metadata if enabled
        if self.include_metadata:
            output_df.at[row_index, 'processing_timestamp'] = datetime.utcnow().isoformat()

            if confidence is not None:
                output_df.at[row_index, 'analysis_confidence'] = confidence

            output_df.at[row_index, 'review_needed'] = review_needed

        logger.debug(f"Updated row {row_index} with status: {status}")

    def write_output_csv(self, output_df: pd.DataFrame, append: bool = False) -> None:
        """
        Write output DataFrame to CSV file

        Args:
            output_df: DataFrame to write
            append: Whether to append to existing file
        """
        try:
            # Ensure output directory exists
            self.output_file.parent.mkdir(parents=True, exist_ok=True)

            # Write CSV with proper encoding and escaping
            mode = 'a' if append else 'w'
            header = not append or not self.output_file.exists()

            output_df.to_csv(
                self.output_file,
                mode=mode,
                header=header,
                index=False,
                encoding='utf-8',
                escapechar='\\',
                quoting=1  # QUOTE_ALL for safety
            )

            logger.info(f"{'Appended' if append else 'Wrote'} {len(output_df)} rows "
                        f"to {self.output_file}")

        except Exception as e:
            logger.error(f"Failed to write output CSV: {e}")
            raise

    def read_existing_output(self) -> Optional[pd.DataFrame]:
        """
        Read existing output CSV file

        Returns:
            DataFrame if file exists and is readable, None otherwise
        """
        if not self.output_file.exists():
            return None

        try:
            df = pd.read_csv(self.output_file, encoding='utf-8')
            logger.info(f"Read existing output CSV: {len(df)} rows, {len(df.columns)} columns")
            return df

        except Exception as e:
            logger.error(f"Failed to read existing output CSV: {e}")
            return None

    def validate_output_structure(self, output_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate output DataFrame structure

        Args:
            output_df: DataFrame to validate

        Returns:
            Validation results
        """
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'column_check': {},
            'data_check': {}
        }

        if self._output_columns is None:
            result['errors'].append("Output schema not defined")
            result['valid'] = False
            return result

        # Check columns
        missing_cols = [col for col in self._output_columns if col not in output_df.columns]
        extra_cols = [col for col in output_df.columns if col not in self._output_columns]

        if missing_cols:
            result['errors'].append(f"Missing required columns: {missing_cols}")
            result['valid'] = False

        if extra_cols:
            result['warnings'].append(f"Extra columns found: {extra_cols}")

        result['column_check'] = {
            'expected_columns': len(self._output_columns),
            'actual_columns': len(output_df.columns),
            'missing_columns': missing_cols,
            'extra_columns': extra_cols
        }

        # Check data quality
        if result['valid']:
            # Check for required fields
            required_cols = ['status']
            for col in required_cols:
                if col in output_df.columns:
                    null_count = output_df[col].isnull().sum()
                    if null_count > 0:
                        result['warnings'].append(f"Column '{col}' has {null_count} null values")

        result['data_check'] = {
            'total_rows': len(output_df),
            'pending_rows': ((output_df['status'] == 'pending').sum()
                             if 'status' in output_df.columns else 0),
            'processed_rows': ((output_df['status'] == 'processed').sum()
                               if 'status' in output_df.columns else 0),
            'error_rows': ((output_df['status'] == 'error').sum()
                           if 'status' in output_df.columns else 0)
        }

        logger.info(f"Output validation: {'PASSED' if result['valid'] else 'FAILED'}")
        return result

    def get_processing_summary(self, output_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary of processing status

        Args:
            output_df: Output DataFrame to analyze

        Returns:
            Processing summary
        """
        if 'status' not in output_df.columns:
            return {'error': 'No status column found'}

        status_counts = output_df['status'].value_counts().to_dict()

        summary = {
            'total_rows': len(output_df),
            'status_breakdown': status_counts,
            'completion_rate': (status_counts.get('processed', 0) /
                                len(output_df) * 100) if len(output_df) > 0 else 0,
            'error_rate': (status_counts.get('error', 0) /
                           len(output_df) * 100) if len(output_df) > 0 else 0,
            'pending_count': status_counts.get('pending', 0)
        }

        # Add metadata analysis if available
        if self.include_metadata and 'review_needed' in output_df.columns:
            review_needed_count = output_df['review_needed'].sum()
            summary['review_needed_count'] = review_needed_count
            summary['review_needed_rate'] = (
                (review_needed_count / len(output_df) * 100)
                if len(output_df) > 0 else 0)

        if self.include_metadata and 'analysis_confidence' in output_df.columns:
            confidence_data = output_df['analysis_confidence'].dropna()
            if len(confidence_data) > 0:
                summary['avg_confidence'] = confidence_data.mean()
                summary['min_confidence'] = confidence_data.min()
                summary['max_confidence'] = confidence_data.max()

        return summary


def create_output_manager(output_file: str, include_metadata: bool = True) -> OutputCSVManager:
    """
    Factory function to create OutputCSVManager instance

    Args:
        output_file: Path to output CSV file
        include_metadata: Whether to include metadata columns

    Returns:
        OutputCSVManager instance
    """
    return OutputCSVManager(output_file, include_metadata)
