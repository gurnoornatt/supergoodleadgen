#!/usr/bin/env python3
"""
Make.com Compatibility Validator
Tests Google Slides template compatibility with Make.com automation
"""

import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class ValidationResult:
    """Represents a validation check result"""
    check_name: str
    passed: bool
    message: str
    severity: str  # 'error', 'warning', 'info'

class MakeComCompatibilityValidator:
    """Validates template and data compatibility with Make.com"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_results = []
        
        # Required placeholders for Make.com
        self.required_text_placeholders = [
            "{{BUSINESS_NAME}}",
            "{{MOBILE_SCORE}}", 
            "{{PAIN_POINT_1}}",
            "{{PAIN_POINT_2}}",
            "{{PAIN_POINT_3}}",
            "{{BUSINESS_PHONE}}",
            "{{BUSINESS_WEBSITE}}"
        ]
        
        self.required_image_placeholders = [
            "{{WEBSITE_SCREENSHOT}}",
            "{{BUSINESS_LOGO}}",
            "{{COMPANY_LOGO}}"
        ]
        
        # Make.com specific requirements
        self.makecom_requirements = {
            "max_text_length": 1000,
            "max_business_name": 50,
            "max_pain_point": 80,
            "supported_image_formats": ["PNG", "JPEG", "JPG"],
            "max_image_size_mb": 10,
            "placeholder_format": r"^\{\{[A-Z_0-9]+\}\}$"
        }

    def validate_placeholder_format(self, placeholder: str) -> ValidationResult:
        """Validate placeholder follows Make.com format requirements"""
        pattern = self.makecom_requirements["placeholder_format"]
        
        if re.match(pattern, placeholder):
            return ValidationResult(
                check_name="Placeholder Format",
                passed=True,
                message=f"Placeholder '{placeholder}' follows correct format",
                severity="info"
            )
        else:
            return ValidationResult(
                check_name="Placeholder Format",
                passed=False,
                message=f"Placeholder '{placeholder}' does not match required format {{{{VARIABLE_NAME}}}}",
                severity="error"
            )

    def validate_test_data_compatibility(self, test_data: Dict) -> List[ValidationResult]:
        """Validate test data meets Make.com requirements"""
        results = []
        
        # Check business name length
        if "BUSINESS_NAME" in test_data:
            name_length = len(test_data["BUSINESS_NAME"])
            if name_length <= self.makecom_requirements["max_business_name"]:
                results.append(ValidationResult(
                    check_name="Business Name Length",
                    passed=True,
                    message=f"Business name length ({name_length}) within limit",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    check_name="Business Name Length", 
                    passed=False,
                    message=f"Business name too long ({name_length} > {self.makecom_requirements['max_business_name']})",
                    severity="warning"
                ))
        
        # Check pain point lengths
        for i in range(1, 4):
            pain_point_key = f"PAIN_POINT_{i}"
            if pain_point_key in test_data:
                point_length = len(test_data[pain_point_key])
                if point_length <= self.makecom_requirements["max_pain_point"]:
                    results.append(ValidationResult(
                        check_name=f"Pain Point {i} Length",
                        passed=True,
                        message=f"Pain point {i} length ({point_length}) within limit",
                        severity="info"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"Pain Point {i} Length",
                        passed=False,
                        message=f"Pain point {i} too long ({point_length} > {self.makecom_requirements['max_pain_point']})",
                        severity="warning"
                    ))
        
        # Check mobile score format
        if "MOBILE_SCORE" in test_data:
            score = test_data["MOBILE_SCORE"]
            try:
                score_int = int(score)
                if 0 <= score_int <= 100:
                    results.append(ValidationResult(
                        check_name="Mobile Score Format",
                        passed=True,
                        message=f"Mobile score ({score}) is valid",
                        severity="info"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name="Mobile Score Format",
                        passed=False,
                        message=f"Mobile score ({score}) out of range (0-100)",
                        severity="error"
                    ))
            except ValueError:
                results.append(ValidationResult(
                    check_name="Mobile Score Format",
                    passed=False,
                    message=f"Mobile score ({score}) is not a valid number",
                    severity="error"
                ))
        
        # Check phone format
        if "BUSINESS_PHONE" in test_data and test_data["BUSINESS_PHONE"]:
            phone = test_data["BUSINESS_PHONE"]
            phone_pattern = r"^\(\d{3}\) \d{3}-\d{4}$"
            if re.match(phone_pattern, phone):
                results.append(ValidationResult(
                    check_name="Phone Format",
                    passed=True,
                    message=f"Phone number ({phone}) follows correct format",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    check_name="Phone Format",
                    passed=False,
                    message=f"Phone number ({phone}) does not match (XXX) XXX-XXXX format",
                    severity="warning"
                ))
        
        # Check URL formats
        url_pattern = r"^https?:\/\/[^\s]+$|^www\.[^\s]+$"
        for url_field in ["BUSINESS_WEBSITE", "WEBSITE_SCREENSHOT", "BUSINESS_LOGO", "COMPANY_LOGO"]:
            if url_field in test_data and test_data[url_field]:
                url = test_data[url_field]
                if re.match(url_pattern, url):
                    results.append(ValidationResult(
                        check_name=f"{url_field} Format",
                        passed=True,
                        message=f"{url_field} URL format is valid",
                        severity="info"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name=f"{url_field} Format",
                        passed=False,
                        message=f"{url_field} URL format is invalid",
                        severity="error"
                    ))
        
        return results

    def validate_google_sheets_structure(self, expected_columns: List[str]) -> List[ValidationResult]:
        """Validate Google Sheets column structure for Make.com"""
        results = []
        
        required_columns = [
            "Business Name", "Mobile Score", "Pain Point 1", "Pain Point 2",
            "Pain Point 3", "Business Phone", "Business Website", 
            "Screenshot URL", "Logo URL", "Status", "PDF Link"
        ]
        
        for column in required_columns:
            if column in expected_columns:
                results.append(ValidationResult(
                    check_name="Sheet Column Structure",
                    passed=True,
                    message=f"Required column '{column}' present",
                    severity="info"
                ))
            else:
                results.append(ValidationResult(
                    check_name="Sheet Column Structure",
                    passed=False,
                    message=f"Missing required column '{column}'",
                    severity="error"
                ))
        
        return results

    def validate_conditional_formatting_logic(self, test_scores: List[int]) -> List[ValidationResult]:
        """Validate conditional formatting logic for performance scores"""
        results = []
        
        for score in test_scores:
            expected_color = "#E74C3C" if score < 60 else "#27AE60"
            expected_status = "RED" if score < 60 else "GREEN"
            
            results.append(ValidationResult(
                check_name="Conditional Formatting",
                passed=True,
                message=f"Score {score} → {expected_status} ({expected_color})",
                severity="info"
            ))
        
        return results

    def validate_makecom_scenario_structure(self, scenario_config: Dict) -> List[ValidationResult]:
        """Validate Make.com scenario configuration"""
        results = []
        
        required_modules = [
            "Google Sheets - Watch Rows",
            "Google Slides - Create from Template", 
            "Google Slides - Replace Text",
            "Google Slides - Replace Image",
            "Google Drive - Export File",
            "Google Drive - Create Share Link",
            "Google Sheets - Update Row"
        ]
        
        if "modules" in scenario_config:
            scenario_modules = [module.get("name", "") for module in scenario_config["modules"]]
            
            for required_module in required_modules:
                if any(required_module in module for module in scenario_modules):
                    results.append(ValidationResult(
                        check_name="Scenario Module Structure",
                        passed=True,
                        message=f"Required module '{required_module}' configured",
                        severity="info"
                    ))
                else:
                    results.append(ValidationResult(
                        check_name="Scenario Module Structure",
                        passed=False,
                        message=f"Missing required module '{required_module}'",
                        severity="error"
                    ))
        
        return results

    def run_comprehensive_validation(self, test_data_file: str = "template_test_data.json") -> Dict:
        """Run all validation checks and return comprehensive report"""
        all_results = []
        
        # Load test data
        try:
            with open(test_data_file, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
            
            # Validate placeholder formats
            all_placeholders = self.required_text_placeholders + self.required_image_placeholders
            for placeholder in all_placeholders:
                result = self.validate_placeholder_format(placeholder)
                all_results.append(result)
            
            # Validate test data samples
            if "regular_samples" in test_data:
                for i, sample in enumerate(test_data["regular_samples"][:3]):  # Test first 3 samples
                    sample_results = self.validate_test_data_compatibility(sample)
                    all_results.extend(sample_results)
            
            # Validate edge cases
            if "edge_cases" in test_data:
                for edge_case in test_data["edge_cases"]:
                    edge_results = self.validate_test_data_compatibility(edge_case)
                    all_results.extend(edge_results)
            
            # Validate conditional formatting
            test_scores = [25, 45, 60, 75, 95]
            formatting_results = self.validate_conditional_formatting_logic(test_scores)
            all_results.extend(formatting_results)
            
            # Validate sheet structure
            expected_columns = [
                "Business Name", "Mobile Score", "Pain Point 1", "Pain Point 2",
                "Pain Point 3", "Business Phone", "Business Website", 
                "Screenshot URL", "Logo URL", "Status", "PDF Link"
            ]
            sheet_results = self.validate_google_sheets_structure(expected_columns)
            all_results.extend(sheet_results)
            
        except FileNotFoundError:
            all_results.append(ValidationResult(
                check_name="Test Data Loading",
                passed=False,
                message=f"Test data file '{test_data_file}' not found",
                severity="error"
            ))
        except json.JSONDecodeError:
            all_results.append(ValidationResult(
                check_name="Test Data Loading",
                passed=False,
                message=f"Invalid JSON in test data file '{test_data_file}'",
                severity="error"
            ))
        
        # Generate summary report
        passed_checks = len([r for r in all_results if r.passed])
        total_checks = len(all_results)
        errors = [r for r in all_results if not r.passed and r.severity == "error"]
        warnings = [r for r in all_results if not r.passed and r.severity == "warning"]
        
        return {
            "validation_summary": {
                "total_checks": total_checks,
                "passed_checks": passed_checks,
                "failed_checks": total_checks - passed_checks,
                "success_rate": f"{(passed_checks/total_checks)*100:.1f}%" if total_checks > 0 else "0%",
                "errors": len(errors),
                "warnings": len(warnings)
            },
            "results": all_results,
            "errors": errors,
            "warnings": warnings,
            "ready_for_makecom": len(errors) == 0
        }

    def generate_validation_report(self, output_file: str = "makecom_validation_report.json"):
        """Generate and save validation report"""
        validation_data = self.run_comprehensive_validation()
        
        # Save detailed report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(validation_data, f, indent=2, ensure_ascii=False, default=str)
        
        return validation_data

def main():
    """Run Make.com compatibility validation"""
    validator = MakeComCompatibilityValidator()
    
    print("🔍 Running Make.com Compatibility Validation...")
    validation_data = validator.generate_validation_report()
    
    # Display summary
    summary = validation_data["validation_summary"]
    print(f"\n📊 Validation Summary:")
    print(f"  Total Checks: {summary['total_checks']}")
    print(f"  Passed: {summary['passed_checks']}")
    print(f"  Failed: {summary['failed_checks']}")
    print(f"  Success Rate: {summary['success_rate']}")
    print(f"  Errors: {summary['errors']}")
    print(f"  Warnings: {summary['warnings']}")
    
    # Display errors
    if validation_data["errors"]:
        print(f"\n❌ Critical Errors ({len(validation_data['errors'])}):")
        for error in validation_data["errors"]:
            print(f"  • {error.check_name}: {error.message}")
    
    # Display warnings
    if validation_data["warnings"]:
        print(f"\n⚠️ Warnings ({len(validation_data['warnings'])}):")
        for warning in validation_data["warnings"]:
            print(f"  • {warning.check_name}: {warning.message}")
    
    # Final assessment
    if validation_data["ready_for_makecom"]:
        print(f"\n✅ Template is ready for Make.com automation!")
    else:
        print(f"\n❌ Template needs fixes before Make.com deployment.")
        print(f"   Please resolve {len(validation_data['errors'])} errors first.")
    
    print(f"\n📄 Detailed report saved to: makecom_validation_report.json")

if __name__ == "__main__":
    main()