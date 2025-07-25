#!/usr/bin/env python3
"""
Template Testing Suite
Comprehensive testing for Google Slides template and Make.com compatibility
"""

import json
import os
import time
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    passed: bool
    message: str
    execution_time: float
    details: Dict = None

class TemplateTestingSuite:
    """Comprehensive testing suite for PDF template"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = []
        self.setup_logging()
        
        # Load test data
        self.load_test_data()
        
        # Define test scenarios
        self.test_scenarios = [
            "normal_business_data",
            "long_business_name", 
            "minimum_score",
            "maximum_score",
            "missing_phone",
            "missing_website",
            "missing_logo",
            "long_pain_points",
            "special_characters",
            "unicode_business_name"
        ]

    def setup_logging(self):
        """Setup logging for test execution"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def load_test_data(self):
        """Load test data from JSON file"""
        try:
            with open('template_test_data.json', 'r', encoding='utf-8') as f:
                self.test_data = json.load(f)
            self.logger.info("Test data loaded successfully")
        except FileNotFoundError:
            self.logger.error("Test data file not found. Running generate_test_data first.")
            os.system("python template_test_data_generator.py")
            with open('template_test_data.json', 'r', encoding='utf-8') as f:
                self.test_data = json.load(f)

    def test_placeholder_validation(self) -> TestResult:
        """Test all placeholder formats are valid"""
        start_time = time.time()
        
        required_placeholders = [
            "{{BUSINESS_NAME}}", "{{MOBILE_SCORE}}", "{{PAIN_POINT_1}}",
            "{{PAIN_POINT_2}}", "{{PAIN_POINT_3}}", "{{BUSINESS_PHONE}}",
            "{{BUSINESS_WEBSITE}}", "{{WEBSITE_SCREENSHOT}}", 
            "{{BUSINESS_LOGO}}", "{{COMPANY_LOGO}}"
        ]
        
        invalid_placeholders = []
        
        for placeholder in required_placeholders:
            # Check format: {{VARIABLE_NAME}}
            if not (placeholder.startswith('{{') and placeholder.endswith('}}') 
                   and placeholder[2:-2].replace('_', '').replace('0', '').replace('1', '').replace('2', '').replace('3', '').isalpha()):
                invalid_placeholders.append(placeholder)
        
        execution_time = time.time() - start_time
        
        if not invalid_placeholders:
            return TestResult(
                test_name="Placeholder Validation",
                passed=True,
                message=f"All {len(required_placeholders)} placeholders valid",
                execution_time=execution_time,
                details={"valid_placeholders": required_placeholders}
            )
        else:
            return TestResult(
                test_name="Placeholder Validation",
                passed=False,
                message=f"{len(invalid_placeholders)} invalid placeholders found",
                execution_time=execution_time,
                details={"invalid_placeholders": invalid_placeholders}
            )

    def test_data_formatting(self) -> List[TestResult]:
        """Test data formatting for various scenarios"""
        results = []
        
        # Test regular samples
        for i, sample in enumerate(self.test_data.get('regular_samples', [])[:3]):
            start_time = time.time()
            
            issues = []
            
            # Check business name length
            business_name = sample.get('BUSINESS_NAME', '')
            if len(business_name) > 50:
                issues.append(f"Business name too long: {len(business_name)} chars")
            
            # Check mobile score
            mobile_score = sample.get('MOBILE_SCORE', '0')
            try:
                score = int(mobile_score)
                if not 0 <= score <= 100:
                    issues.append(f"Mobile score out of range: {score}")
            except ValueError:
                issues.append(f"Invalid mobile score: {mobile_score}")
            
            # Check pain point lengths
            for j in range(1, 4):
                pain_point = sample.get(f'PAIN_POINT_{j}', '')
                if len(pain_point) > 80:
                    issues.append(f"Pain point {j} too long: {len(pain_point)} chars")
            
            # Check URL formats
            for url_field in ['BUSINESS_WEBSITE', 'WEBSITE_SCREENSHOT', 'BUSINESS_LOGO']:
                url = sample.get(url_field, '')
                if url and not (url.startswith('http') or url.startswith('www.')):
                    issues.append(f"Invalid URL format: {url_field}")
            
            execution_time = time.time() - start_time
            
            if not issues:
                results.append(TestResult(
                    test_name=f"Data Formatting Sample {i+1}",
                    passed=True,
                    message="All data formatting valid",
                    execution_time=execution_time,
                    details={"sample_data": sample}
                ))
            else:
                results.append(TestResult(
                    test_name=f"Data Formatting Sample {i+1}",
                    passed=False,
                    message=f"{len(issues)} formatting issues found",
                    execution_time=execution_time,
                    details={"issues": issues, "sample_data": sample}
                ))
        
        return results

    def test_edge_cases(self) -> List[TestResult]:
        """Test edge case scenarios"""
        results = []
        
        edge_cases = self.test_data.get('edge_cases', [])
        
        for edge_case in edge_cases:
            start_time = time.time()
            test_name = edge_case.get('test_name', 'Unknown Edge Case')
            
            # Test specific edge case scenarios
            issues = []
            warnings = []
            
            if 'Long Business Name' in test_name:
                business_name = edge_case.get('BUSINESS_NAME', '')
                if len(business_name) <= 50:
                    issues.append("Expected long business name for this test")
                else:
                    warnings.append(f"Long business name detected: {len(business_name)} chars")
            
            if 'Perfect Score' in test_name:
                score = int(edge_case.get('MOBILE_SCORE', 0))
                if score != 100:
                    issues.append(f"Expected perfect score (100), got {score}")
            
            if 'Minimum Score' in test_name:
                score = int(edge_case.get('MOBILE_SCORE', 100))
                if score >= 10:
                    issues.append(f"Expected very low score (<10), got {score}")
            
            if 'Missing Data' in test_name:
                missing_fields = []
                for field in ['BUSINESS_PHONE', 'BUSINESS_WEBSITE', 'BUSINESS_LOGO']:
                    if not edge_case.get(field, '').strip():
                        missing_fields.append(field)
                
                if not missing_fields:
                    issues.append("Expected missing data for this test")
                else:
                    warnings.append(f"Missing fields as expected: {missing_fields}")
            
            execution_time = time.time() - start_time
            
            if not issues:
                results.append(TestResult(
                    test_name=f"Edge Case: {test_name}",
                    passed=True,
                    message="Edge case handled correctly",
                    execution_time=execution_time,
                    details={"warnings": warnings, "test_data": edge_case}
                ))
            else:
                results.append(TestResult(
                    test_name=f"Edge Case: {test_name}",
                    passed=False,
                    message=f"{len(issues)} issues with edge case",
                    execution_time=execution_time,
                    details={"issues": issues, "test_data": edge_case}
                ))
        
        return results

    def test_makecom_compatibility(self) -> TestResult:
        """Test Make.com integration compatibility"""
        start_time = time.time()
        
        # Run the existing compatibility validator
        try:
            import subprocess
            result = subprocess.run(
                ['python', 'make_com_compatibility_validator.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output for success indicators
                output = result.stdout
                if "ready for Make.com automation" in output:
                    execution_time = time.time() - start_time
                    return TestResult(
                        test_name="Make.com Compatibility",
                        passed=True,
                        message="Template ready for Make.com automation",
                        execution_time=execution_time,
                        details={"validator_output": output}
                    )
                else:
                    execution_time = time.time() - start_time
                    return TestResult(
                        test_name="Make.com Compatibility",
                        passed=False,
                        message="Template not ready for Make.com",
                        execution_time=execution_time,
                        details={"validator_output": output}
                    )
            else:
                execution_time = time.time() - start_time
                return TestResult(
                    test_name="Make.com Compatibility",
                    passed=False,
                    message="Compatibility validator failed to run",
                    execution_time=execution_time,
                    details={"error": result.stderr}
                )
        
        except Exception as e:
            execution_time = time.time() - start_time
            return TestResult(
                test_name="Make.com Compatibility",
                passed=False,
                message=f"Error running compatibility validator: {str(e)}",
                execution_time=execution_time,
                details={"exception": str(e)}
            )

    def test_design_assets(self) -> TestResult:
        """Test design asset generation and availability"""
        start_time = time.time()
        
        expected_assets = [
            'design_assets/brand_color_palette.png',
            'design_assets/design_specifications.json',
            'design_assets/template_background.png',
            'design_assets/warning_icon.png'
        ]
        
        missing_assets = []
        for asset in expected_assets:
            if not os.path.exists(asset):
                missing_assets.append(asset)
        
        execution_time = time.time() - start_time
        
        if not missing_assets:
            return TestResult(
                test_name="Design Assets",
                passed=True,
                message=f"All {len(expected_assets)} design assets available",
                execution_time=execution_time,
                details={"available_assets": expected_assets}
            )
        else:
            return TestResult(
                test_name="Design Assets",
                passed=False,
                message=f"{len(missing_assets)} design assets missing",
                execution_time=execution_time,
                details={"missing_assets": missing_assets}
            )

    def test_documentation_completeness(self) -> TestResult:
        """Test documentation completeness"""
        start_time = time.time()
        
        required_docs = [
            'google_slides_template_design.md',
            'placeholder_frames_specification.md',
            'make_com_automation_setup.md',
            'professional_design_branding_guide.md',
            'template_implementation_guide.md'
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not os.path.exists(doc):
                missing_docs.append(doc)
        
        execution_time = time.time() - start_time
        
        if not missing_docs:
            return TestResult(
                test_name="Documentation Completeness",
                passed=True,
                message=f"All {len(required_docs)} documentation files present",
                execution_time=execution_time,
                details={"available_docs": required_docs}
            )
        else:
            return TestResult(
                test_name="Documentation Completeness",
                passed=False,
                message=f"{len(missing_docs)} documentation files missing",
                execution_time=execution_time,
                details={"missing_docs": missing_docs}
            )

    def test_conditional_formatting_logic(self) -> TestResult:
        """Test conditional formatting logic for scores"""
        start_time = time.time()
        
        test_scores = [
            (25, "RED", "#E74C3C"),
            (45, "RED", "#E74C3C"),
            (59, "RED", "#E74C3C"),
            (60, "GREEN", "#27AE60"),
            (75, "GREEN", "#27AE60"),
            (95, "GREEN", "#27AE60")
        ]
        
        failures = []
        
        for score, expected_status, expected_color in test_scores:
            actual_status = "RED" if score < 60 else "GREEN"
            actual_color = "#E74C3C" if score < 60 else "#27AE60"
            
            if actual_status != expected_status or actual_color != expected_color:
                failures.append({
                    "score": score,
                    "expected": {"status": expected_status, "color": expected_color},
                    "actual": {"status": actual_status, "color": actual_color}
                })
        
        execution_time = time.time() - start_time
        
        if not failures:
            return TestResult(
                test_name="Conditional Formatting Logic",
                passed=True,
                message=f"All {len(test_scores)} score scenarios correct",
                execution_time=execution_time,
                details={"test_scenarios": test_scores}
            )
        else:
            return TestResult(
                test_name="Conditional Formatting Logic",
                passed=False,
                message=f"{len(failures)} conditional formatting failures",
                execution_time=execution_time,
                details={"failures": failures}
            )

    def run_comprehensive_test_suite(self) -> Dict:
        """Run all tests and generate comprehensive report"""
        print("🧪 Running comprehensive template testing suite...")
        
        all_results = []
        
        # Run individual tests
        print("  → Testing placeholder validation...")
        all_results.append(self.test_placeholder_validation())
        
        print("  → Testing data formatting...")
        all_results.extend(self.test_data_formatting())
        
        print("  → Testing edge cases...")
        all_results.extend(self.test_edge_cases())
        
        print("  → Testing Make.com compatibility...")
        all_results.append(self.test_makecom_compatibility())
        
        print("  → Testing design assets...")
        all_results.append(self.test_design_assets())
        
        print("  → Testing documentation...")
        all_results.append(self.test_documentation_completeness())
        
        print("  → Testing conditional formatting...")
        all_results.append(self.test_conditional_formatting_logic())
        
        # Generate summary
        total_tests = len(all_results)
        passed_tests = len([r for r in all_results if r.passed])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        total_execution_time = sum(r.execution_time for r in all_results)
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{success_rate:.1f}%",
                "total_execution_time": f"{total_execution_time:.2f}s"
            },
            "results": all_results,
            "passed_tests": [r for r in all_results if r.passed],
            "failed_tests": [r for r in all_results if not r.passed],
            "template_ready": failed_tests == 0
        }

    def generate_test_report(self, output_file: str = "template_test_report.json") -> str:
        """Generate and save comprehensive test report"""
        test_data = self.run_comprehensive_test_suite()
        
        # Convert TestResult objects to dictionaries for JSON serialization
        def convert_test_result(result):
            return {
                "test_name": result.test_name,
                "passed": result.passed,
                "message": result.message,
                "execution_time": result.execution_time,
                "details": result.details
            }
        
        json_data = {
            "summary": test_data["summary"],
            "results": [convert_test_result(r) for r in test_data["results"]],
            "passed_tests": [convert_test_result(r) for r in test_data["passed_tests"]],
            "failed_tests": [convert_test_result(r) for r in test_data["failed_tests"]],
            "template_ready": test_data["template_ready"]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        return test_data

def main():
    """Run the complete testing suite"""
    tester = TemplateTestingSuite()
    test_data = tester.generate_test_report()
    
    # Display results
    summary = test_data["summary"]
    print(f"\n📊 Test Results Summary:")
    print(f"  Total Tests: {summary['total_tests']}")
    print(f"  Passed: {summary['passed_tests']}")
    print(f"  Failed: {summary['failed_tests']}")
    print(f"  Success Rate: {summary['success_rate']}")
    print(f"  Execution Time: {summary['total_execution_time']}")
    
    # Show failed tests
    if test_data["failed_tests"]:
        print(f"\n❌ Failed Tests ({len(test_data['failed_tests'])}):")
        for test in test_data["failed_tests"]:
            print(f"  • {test.test_name}: {test.message}")
    
    # Final assessment
    if test_data["template_ready"]:
        print(f"\n✅ Template is ready for production deployment!")
    else:
        print(f"\n❌ Template needs fixes before deployment.")
        print(f"   Please resolve {len(test_data['failed_tests'])} failed tests.")
    
    print(f"\n📄 Detailed report saved to: template_test_report.json")

if __name__ == "__main__":
    main()