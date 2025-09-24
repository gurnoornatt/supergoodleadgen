"""
Input validation utilities for AI Sales Intelligence Agent
"""

import re
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from .exceptions import CSVValidationError, URLValidationError


class URLValidator:
    """Validates website URLs for proper format and accessibility"""

    # Common URL patterns for websites
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    # Common domain extensions for businesses
    BUSINESS_DOMAINS = {'.com', '.org', '.net', '.biz', '.info', '.us', '.co'}

    @classmethod
    def is_valid_url(cls, url: str) -> bool:
        """Check if URL is properly formatted"""
        if not url or not isinstance(url, str):
            return False

        url = url.strip()
        if not url:
            return False

        # Add http:// if missing protocol
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'

        return bool(cls.URL_PATTERN.match(url))

    @classmethod
    def normalize_url(cls, url: str) -> str:
        """Normalize URL format for consistent processing"""
        if not url or not isinstance(url, str):
            raise URLValidationError(f"Invalid URL: {url}")

        url = url.strip()
        if not url:
            raise URLValidationError("Empty URL")

        # Add http:// if missing protocol
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'

        # Validate format
        if not cls.is_valid_url(url):
            raise URLValidationError(f"Invalid URL format: {url}")

        # Remove trailing slash for consistency
        return url.rstrip('/')

    @classmethod
    def extract_domain(cls, url: str) -> str:
        """Extract domain from URL"""
        try:
            normalized = cls.normalize_url(url)
            parsed = urlparse(normalized)
            return parsed.netloc.lower()
        except Exception as e:
            raise URLValidationError(f"Could not extract domain from {url}: {e}")

    @classmethod
    def validate_business_url(cls, url: str) -> Dict[str, Any]:
        """Comprehensive validation for business URLs"""
        result = {
            'url': url,
            'is_valid': False,
            'normalized': None,
            'domain': None,
            'warnings': [],
            'errors': []
        }

        try:
            # Basic validation
            if not url or pd.isna(url):
                result['errors'].append("URL is empty or null")
                return result

            # Normalize URL
            normalized = cls.normalize_url(url)
            result['normalized'] = normalized
            result['domain'] = cls.extract_domain(normalized)

            # Check for suspicious domains
            domain = result['domain']
            social_media = ['facebook', 'instagram', 'twitter', 'linkedin']
            if any(suspicious in domain for suspicious in social_media):
                result['warnings'].append(
                    "URL appears to be a social media profile, not a business website")

            # Check for common parking/placeholder domains
            parking_domains = ['godaddy', 'namecheap', 'parking']
            if any(parking in domain for parking in parking_domains):
                result['warnings'].append("URL appears to be a parked domain")

            # Check for localhost or IP addresses (suspicious for business)
            if 'localhost' in domain or re.match(r'\d+\.\d+\.\d+\.\d+', domain):
                result['warnings'].append("URL uses localhost or IP address")

            result['is_valid'] = True

        except URLValidationError as e:
            result['errors'].append(str(e))
        except Exception as e:
            result['errors'].append(f"Unexpected validation error: {e}")

        return result


class CSVValidator:
    """Validates CSV files for gym lead processing"""

    REQUIRED_COLUMNS = ['gym_name', 'website_url']
    OPTIONAL_COLUMNS = ['phone', 'address', 'city', 'state', 'zip_code', 'google_business_url']

    @classmethod
    def validate_file_format(cls, file_path: str) -> None:
        """Validate basic file format and readability"""
        path = Path(file_path)

        if not path.exists():
            raise CSVValidationError(f"File does not exist: {file_path}")

        if not path.is_file():
            raise CSVValidationError(f"Path is not a file: {file_path}")

        if path.suffix.lower() not in ['.csv', '.txt']:
            raise CSVValidationError(f"File must be CSV format (.csv), got: {path.suffix}")

        if path.stat().st_size == 0:
            raise CSVValidationError("File is empty")

        if path.stat().st_size > 100 * 1024 * 1024:  # 100MB limit
            size_mb = path.stat().st_size / 1024 / 1024
            raise CSVValidationError(f"File too large: {size_mb:.1f}MB (max 100MB)")

    @classmethod
    def validate_csv_structure(cls, df: pd.DataFrame, file_path: str) -> Dict[str, Any]:
        """Validate CSV structure and content"""
        result = {
            'file_path': file_path,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'missing_required': [],
            'empty_rows': 0,
            'duplicate_rows': 0,
            'data_quality': {},
            'warnings': [],
            'errors': []
        }

        # Check required columns
        missing_required = [col for col in cls.REQUIRED_COLUMNS if col not in df.columns]
        if missing_required:
            result['missing_required'] = missing_required
            result['errors'].append(f"Missing required columns: {missing_required}")

        # Check for completely empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        result['empty_rows'] = empty_rows
        if empty_rows > 0:
            result['warnings'].append(f"{empty_rows} completely empty rows found")

        # Check for duplicate rows
        duplicate_rows = df.duplicated().sum()
        result['duplicate_rows'] = duplicate_rows
        if duplicate_rows > 0:
            result['warnings'].append(f"{duplicate_rows} duplicate rows found")

        # Validate data quality for required columns
        for col in cls.REQUIRED_COLUMNS:
            if col in df.columns:
                col_data = df[col]
                null_count = col_data.isnull().sum()
                empty_count = (col_data == '').sum() if col_data.dtype == 'object' else 0

                result['data_quality'][col] = {
                    'null_count': null_count,
                    'empty_count': empty_count,
                    'valid_count': len(col_data) - null_count - empty_count,
                    'fill_rate': ((len(col_data) - null_count - empty_count) /
                                  len(col_data) * 100)
                }

                # More than 50% missing
                if null_count + empty_count > len(col_data) * 0.5:
                    missing_total = null_count + empty_count
                    missing_pct = missing_total / len(col_data) * 100
                    result['warnings'].append(
                        f"Column '{col}' has {missing_total} missing values "
                        f"({missing_pct:.1f}%)")

        return result

    @classmethod
    def validate_url_column(cls, df: pd.DataFrame, url_column: str = 'website_url',
                            sample_size: int = 10) -> Dict[str, Any]:
        """Validate URL column with sampling for performance"""
        result = {
            'column': url_column,
            'total_urls': 0,
            'valid_urls': 0,
            'invalid_urls': 0,
            'sample_validations': [],
            'warnings': [],
            'errors': []
        }

        if url_column not in df.columns:
            result['errors'].append(f"URL column '{url_column}' not found")
            return result

        url_series = df[url_column].dropna()
        result['total_urls'] = len(url_series)

        if result['total_urls'] == 0:
            result['warnings'].append(f"No URLs found in column '{url_column}'")
            return result

        # Sample URLs for detailed validation
        sample_urls = url_series.head(sample_size) if len(url_series) >= sample_size else url_series

        for idx, url in enumerate(sample_urls):
            validation = URLValidator.validate_business_url(url)
            result['sample_validations'].append({
                'index': idx,
                'url': url,
                'validation': validation
            })

            if validation['is_valid']:
                result['valid_urls'] += 1
            else:
                result['invalid_urls'] += 1

        # Quick format check for all URLs
        all_valid = url_series.apply(URLValidator.is_valid_url)
        result['format_valid_count'] = all_valid.sum()
        result['format_invalid_count'] = len(url_series) - all_valid.sum()

        if result['format_invalid_count'] > 0:
            result['warnings'].append(f"{result['format_invalid_count']} URLs have invalid format")

        return result

    @classmethod
    def validate_gym_names(cls, df: pd.DataFrame, name_column: str = 'gym_name') -> Dict[str, Any]:
        """Validate gym name column"""
        result = {
            'column': name_column,
            'total_names': 0,
            'empty_names': 0,
            'short_names': 0,
            'long_names': 0,
            'warnings': [],
            'errors': []
        }

        if name_column not in df.columns:
            result['errors'].append(f"Name column '{name_column}' not found")
            return result

        names = df[name_column]
        result['total_names'] = len(names)

        # Count empty/null names
        empty_names = names.isnull().sum() + (names == '').sum()
        result['empty_names'] = empty_names

        if empty_names > 0:
            result['warnings'].append(f"{empty_names} empty gym names found")

        # Check name lengths
        valid_names = names.dropna()
        valid_names = valid_names[valid_names != '']

        if len(valid_names) > 0:
            short_names = (valid_names.str.len() < 3).sum()
            long_names = (valid_names.str.len() > 100).sum()

            result['short_names'] = short_names
            result['long_names'] = long_names

            if short_names > 0:
                result['warnings'].append(
                    f"{short_names} gym names are very short (< 3 characters)")

            if long_names > 0:
                result['warnings'].append(
                    f"{long_names} gym names are very long (> 100 characters)")

        return result


def validate_input_csv(file_path: str, max_rows: Optional[int] = None,
                       sample_urls: int = 10) -> Dict[str, Any]:
    """
    Comprehensive CSV validation for gym leads

    Args:
        file_path: Path to CSV file
        max_rows: Maximum rows to read (for testing)
        sample_urls: Number of URLs to validate in detail

    Returns:
        Validation result dictionary
    """
    result = {
        'file_path': file_path,
        'validation_passed': False,
        'file_validation': {},
        'structure_validation': {},
        'url_validation': {},
        'name_validation': {},
        'summary': {
            'total_errors': 0,
            'total_warnings': 0,
            'processable_rows': 0
        }
    }

    try:
        # Step 1: File format validation
        CSVValidator.validate_file_format(file_path)

        # Step 2: Read and validate CSV structure
        df = pd.read_csv(file_path, nrows=max_rows)
        structure_result = CSVValidator.validate_csv_structure(df, file_path)
        result['structure_validation'] = structure_result

        # If critical errors, stop here
        if structure_result['errors']:
            result['summary']['total_errors'] = len(structure_result['errors'])
            return result

        # Step 3: Validate URLs
        url_result = CSVValidator.validate_url_column(df, sample_size=sample_urls)
        result['url_validation'] = url_result

        # Step 4: Validate gym names
        name_result = CSVValidator.validate_gym_names(df)
        result['name_validation'] = name_result

        # Step 5: Calculate summary
        total_errors = (len(structure_result['errors']) +
                        len(url_result['errors']) +
                        len(name_result['errors']))

        total_warnings = (len(structure_result['warnings']) +
                          len(url_result['warnings']) +
                          len(name_result['warnings']))

        # Calculate processable rows (rows with valid gym_name and website_url)
        processable_rows = len(df)
        if 'gym_name' in df.columns and 'website_url' in df.columns:
            valid_mask = (df['gym_name'].notna() &
                          (df['gym_name'] != '') &
                          df['website_url'].notna() &
                          (df['website_url'] != ''))
            processable_rows = valid_mask.sum()

        result['summary'] = {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'processable_rows': processable_rows,
            'total_rows': len(df)
        }

        # Validation passes if no critical errors
        result['validation_passed'] = total_errors == 0

    except CSVValidationError as e:
        result['file_validation'] = {'error': str(e)}
        result['summary']['total_errors'] = 1
    except Exception as e:
        result['file_validation'] = {'error': f"Unexpected error: {e}"}
        result['summary']['total_errors'] = 1

    return result


def print_validation_report(validation_result: Dict[str, Any], verbose: bool = False) -> None:
    """Print a formatted validation report"""
    result = validation_result
    summary = result['summary']

    print(f"\n📊 CSV Validation Report: {result['file_path']}")
    print("=" * 60)

    # Summary
    if summary['total_errors'] == 0:
        print("✅ VALIDATION PASSED")
    else:
        print("❌ VALIDATION FAILED")

    print(f"Total Errors: {summary['total_errors']}")
    print(f"Total Warnings: {summary['total_warnings']}")

    if 'total_rows' in summary:
        print(f"Total Rows: {summary['total_rows']}")
        print(f"Processable Rows: {summary['processable_rows']}")

    # Detailed results
    if verbose or summary['total_errors'] > 0:

        # Structure validation
        if 'structure_validation' in result:
            struct = result['structure_validation']
            print("\n📋 Structure:")
            columns_str = ', '.join(struct['columns'])
            print("  Columns: {} ({})".format(struct['column_count'], columns_str))
            if struct['missing_required']:
                print("  ❌ Missing required: {}".format(struct['missing_required']))
            if struct['warnings']:
                for warning in struct['warnings']:
                    print("  ⚠️  {}".format(warning))

        # URL validation
        if 'url_validation' in result:
            url_val = result['url_validation']
            print("\n🔗 URLs:")
            if 'total_urls' in url_val:
                print("  Total URLs: {}".format(url_val['total_urls']))
                if 'format_valid_count' in url_val:
                    print("  Format Valid: {}".format(url_val['format_valid_count']))
                    print("  Format Invalid: {}".format(url_val['format_invalid_count']))
            if 'warnings' in url_val and url_val['warnings']:
                for warning in url_val['warnings']:
                    print("  ⚠️  {}".format(warning))
            if 'errors' in url_val and url_val['errors']:
                for error in url_val['errors']:
                    print("  ❌ {}".format(error))

        # Name validation
        if 'name_validation' in result:
            name_val = result['name_validation']
            print("\n🏋️ Gym Names:")
            if 'total_names' in name_val:
                print("  Total: {}".format(name_val['total_names']))
                print("  Empty: {}".format(name_val['empty_names']))
            if 'warnings' in name_val and name_val['warnings']:
                for warning in name_val['warnings']:
                    print("  ⚠️  {}".format(warning))
            if 'errors' in name_val and name_val['errors']:
                for error in name_val['errors']:
                    print("  ❌ {}".format(error))

    print("=" * 60)
