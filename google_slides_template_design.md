# Pain-Gap Audit PDF Template Design Specification

## Template Overview
This document provides the complete design specification for the Google Slides template used to generate Pain-Gap Audit PDFs through Make.com automation.

## Template Dimensions
- **Format**: Standard Google Slides (16:9 aspect ratio)
- **Size**: 10" x 5.625" (when exported as PDF)
- **Orientation**: Landscape

## Layout Structure

### Header Section (Top 15%)
- **Company Logo Placeholder**: 
  - Position: Top-left corner
  - Size: 120px × 40px
  - Placeholder text: `{{COMPANY_LOGO}}`
  - Background: Transparent

- **Title**:
  - Position: Top-center
  - Text: "Website Performance Audit"
  - Font: Poppins Bold, 24px
  - Color: #2C3E50 (Dark Blue-Gray)

- **Business Name**:
  - Position: Top-right
  - Text: `{{BUSINESS_NAME}}`
  - Font: Poppins Medium, 18px
  - Color: #34495E (Medium Gray)

### Main Content Area (Middle 70%)

#### Left Column (60% width)
**Website Screenshot Placeholder**:
- Position: Left side of main content
- Size: 400px × 300px
- Placeholder: `{{WEBSITE_SCREENSHOT}}`
- Border: 2px solid #E74C3C (Red)
- Corner radius: 8px
- Caption below: "Current Website"

#### Right Column (40% width)

**Performance Score Section**:
- Background: #E74C3C (Red) for scores < 60
- Background: #27AE60 (Green) for scores ≥ 60
- Padding: 15px
- Corner radius: 8px

**Mobile Performance Score**:
- Large number: `{{MOBILE_SCORE}}/100`
- Font: Poppins Bold, 36px
- Color: White
- Label: "Mobile Performance"
- Font: Poppins Medium, 14px

**Pain Points Section**:
- Title: "Critical Issues Found:"
- Font: Poppins Bold, 16px
- Color: #2C3E50

**Three Bullet Points**:
1. `{{PAIN_POINT_1}}`
2. `{{PAIN_POINT_2}}`
3. `{{PAIN_POINT_3}}`
- Font: Poppins Regular, 14px
- Color: #34495E
- Line spacing: 1.5
- Bullet style: Red circles (•)

### Footer Section (Bottom 15%)

**Left Side**:
- **Business Logo Placeholder**:
  - Size: 100px × 30px
  - Placeholder: `{{BUSINESS_LOGO}}`
  - Fallback: Colored rectangle with business name

**Center**:
- **Call-to-Action**:
  - Text: "Get Your FREE $1 Website Audit Call"
  - Font: Poppins Bold, 16px
  - Color: #E74C3C
  - Background: White with red border

**Right Side**:
- **Contact Information**:
  - Phone: `{{BUSINESS_PHONE}}`
  - Website: `{{BUSINESS_WEBSITE}}`
  - Font: Poppins Regular, 12px
  - Color: #7F8C8D

## Color Palette
- **Primary Red**: #E74C3C (Used for alerts, borders, CTA)
- **Primary Blue**: #2C3E50 (Headers, important text)
- **Secondary Gray**: #34495E (Body text)
- **Light Gray**: #7F8C8D (Supporting text)
- **Success Green**: #27AE60 (Good performance scores)
- **Background**: #FFFFFF (White)

## Typography
- **Primary Font**: Poppins (Google Fonts)
- **Weights Used**: 
  - Regular (400)
  - Medium (500)
  - Bold (700)

## Make.com Placeholder Mapping

### Dynamic Content Placeholders:
1. `{{BUSINESS_NAME}}` - Business name from lead data
2. `{{WEBSITE_SCREENSHOT}}` - Full-page screenshot URL from cloud storage
3. `{{BUSINESS_LOGO}}` - Extracted or generated logo URL
4. `{{MOBILE_SCORE}}` - PageSpeed Insights mobile score (0-100)
5. `{{PAIN_POINT_1}}` - First identified pain point
6. `{{PAIN_POINT_2}}` - Second identified pain point  
7. `{{PAIN_POINT_3}}` - Third identified pain point
8. `{{BUSINESS_PHONE}}` - Business phone number
9. `{{BUSINESS_WEBSITE}}` - Business website URL
10. `{{COMPANY_LOGO}}` - Your company/agency logo

### Conditional Formatting:
- Performance score background color changes based on score:
  - Score < 60: Red background (#E74C3C)
  - Score ≥ 60: Green background (#27AE60)

## Pain Points Logic
The three pain points should be automatically generated based on:
1. **Performance Issues**: If mobile score < 60
   - "Slow loading speeds driving customers away"
   - "Poor mobile experience losing sales"
   - "Search engines ranking site lower"

2. **Technology Issues**: Based on BuiltWith analysis
   - "Outdated technology reducing security"
   - "Missing modern features competitors have"
   - "Poor mobile responsiveness"

## File Organization
- **Template Name**: "Pain-Gap-Audit-Template-v1"
- **Location**: Google Drive > Templates folder
- **Sharing**: Editor access for Make.com service account
- **Version Control**: Template versioned as v1, v2, etc.

## Make.com Integration Requirements

### Google Slides Module Setup:
1. **Create Presentation from Template**: Use template ID
2. **Replace Placeholders**: Map each placeholder to corresponding data
3. **Export as PDF**: Generate PDF version
4. **Upload to Drive**: Save PDF to designated folder
5. **Update Sheet**: Write PDF link back to Google Sheet

### Required Permissions:
- Google Slides API: Create, read, update presentations
- Google Drive API: Upload files, create public links
- Google Sheets API: Read data, update cells

## Quality Assurance Checklist
- [ ] All placeholders properly formatted for Make.com
- [ ] Color contrast meets accessibility standards
- [ ] Text is readable at PDF export resolution
- [ ] Layout works with various business name lengths
- [ ] Screenshot placeholder maintains aspect ratio
- [ ] Logo fallback system implemented
- [ ] Phone number formatting consistent
- [ ] CTA prominently displayed
- [ ] Professional appearance maintained
- [ ] Template exports correctly as PDF

## Implementation Notes
1. Create template in Google Slides with exact placeholder text
2. Test each placeholder replacement with sample data
3. Verify PDF export quality and formatting
4. Ensure Make.com can access and modify template
5. Test conditional formatting for performance scores
6. Validate layout with long/short business names
7. Confirm color accuracy in PDF export
8. Test with various screenshot dimensions