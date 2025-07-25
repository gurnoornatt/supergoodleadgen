# Placeholder Frames Implementation Specification

## Overview
This document specifies the exact implementation of placeholder frames for dynamic content in the Google Slides template, ensuring compatibility with Make.com automation.

## Placeholder Frame Specifications

### 1. Website Screenshot Placeholder
**Location**: Left column, main content area
**Dimensions**: 400px × 300px
**Placeholder Implementation**:
```
Frame Type: Image placeholder
Frame Name: "screenshot_frame"
Alt Text: "{{WEBSITE_SCREENSHOT}}"
Default Image: Gray rectangle with "Website Screenshot" text
Border: 2px solid #E74C3C
Corner Radius: 8px
Caption: Text box below with "Current Website"
```

**Make.com Mapping**:
- Variable: `{{WEBSITE_SCREENSHOT}}`
- Source: Cloud storage URL from screenshot capture module
- Format: PNG/JPEG image
- Fallback: Default placeholder image if screenshot fails

### 2. Business Logo Placeholder
**Location**: Footer section, left side
**Dimensions**: 100px × 30px
**Placeholder Implementation**:
```
Frame Type: Image placeholder
Frame Name: "business_logo_frame"
Alt Text: "{{BUSINESS_LOGO}}"
Default Image: Colored rectangle with "LOGO" text
Background: Transparent
Alignment: Left-aligned in footer
```

**Make.com Mapping**:
- Variable: `{{BUSINESS_LOGO}}`
- Source: Extracted logo URL or generated fallback
- Format: PNG with transparency
- Fallback: Generated colored rectangle with business name

### 3. Company Logo Placeholder
**Location**: Header section, top-left
**Dimensions**: 120px × 40px
**Placeholder Implementation**:
```
Frame Type: Image placeholder
Frame Name: "company_logo_frame"
Alt Text: "{{COMPANY_LOGO}}"
Default Image: Your company logo
Background: Transparent
Alignment: Top-left corner
```

**Make.com Mapping**:
- Variable: `{{COMPANY_LOGO}}`
- Source: Static company logo URL
- Format: PNG with transparency
- Fallback: Company name text if logo unavailable

### 4. Three Pain Points Bullets
**Location**: Right column, below performance score
**Placeholder Implementation**:

#### Bullet Point 1
```
Frame Type: Text box
Frame Name: "pain_point_1"
Placeholder Text: "{{PAIN_POINT_1}}"
Font: Poppins Regular, 14px
Color: #34495E
Bullet Style: Red circle (•)
Max Characters: 80
```

#### Bullet Point 2
```
Frame Type: Text box
Frame Name: "pain_point_2"
Placeholder Text: "{{PAIN_POINT_2}}"
Font: Poppins Regular, 14px
Color: #34495E
Bullet Style: Red circle (•)
Max Characters: 80
```

#### Bullet Point 3
```
Frame Type: Text box
Frame Name: "pain_point_3"
Placeholder Text: "{{PAIN_POINT_3}}"
Font: Poppins Regular, 14px
Color: #34495E
Bullet Style: Red circle (•)
Max Characters: 80
```

**Make.com Mapping**:
- Variables: `{{PAIN_POINT_1}}`, `{{PAIN_POINT_2}}`, `{{PAIN_POINT_3}}`
- Source: Generated based on performance and technology analysis
- Format: Plain text strings
- Fallback: Generic pain points if analysis fails

### 5. Business Information Placeholders

#### Business Name
**Location**: Header section, top-right
```
Frame Type: Text box
Frame Name: "business_name"
Placeholder Text: "{{BUSINESS_NAME}}"
Font: Poppins Medium, 18px
Color: #34495E
Max Characters: 50
Alignment: Right-aligned
```

#### Mobile Performance Score
**Location**: Right column, performance section
```
Frame Type: Text box
Frame Name: "mobile_score"
Placeholder Text: "{{MOBILE_SCORE}}"
Font: Poppins Bold, 36px
Color: White
Background: Conditional (Red/Green)
Format: "XX/100"
```

#### Business Phone
**Location**: Footer section, right side
```
Frame Type: Text box
Frame Name: "business_phone"
Placeholder Text: "{{BUSINESS_PHONE}}"
Font: Poppins Regular, 12px
Color: #7F8C8D
Format: "(XXX) XXX-XXXX"
```

#### Business Website
**Location**: Footer section, right side
```
Frame Type: Text box
Frame Name: "business_website"
Placeholder Text: "{{BUSINESS_WEBSITE}}"
Font: Poppins Regular, 12px
Color: #7F8C8D
Format: "www.example.com"
```

## Make.com Placeholder Syntax

### Text Placeholders
```
Standard Format: {{VARIABLE_NAME}}
Examples:
- {{BUSINESS_NAME}}
- {{MOBILE_SCORE}}
- {{PAIN_POINT_1}}
```

### Image Placeholders
```
Standard Format: {{IMAGE_VARIABLE_NAME}}
Examples:
- {{WEBSITE_SCREENSHOT}}
- {{BUSINESS_LOGO}}
- {{COMPANY_LOGO}}
```

### Conditional Placeholders
```
Performance Score Background:
- If MOBILE_SCORE < 60: Background = #E74C3C (Red)
- If MOBILE_SCORE ≥ 60: Background = #27AE60 (Green)
```

## Implementation Steps for Google Slides

### Step 1: Create Base Layout
1. Set slide dimensions to 16:9 landscape
2. Create header, main content, and footer sections
3. Apply background color (#FFFFFF)

### Step 2: Insert Placeholder Frames
1. **Image Placeholders**:
   - Insert > Image > Upload placeholder images
   - Right-click > Alt text > Add placeholder variable
   - Resize to exact dimensions specified

2. **Text Placeholders**:
   - Insert > Text box
   - Type placeholder variable exactly as specified
   - Apply formatting (font, size, color)
   - Position according to layout

### Step 3: Apply Styling
1. Set fonts to Poppins (ensure it's available)
2. Apply color scheme consistently
3. Set proper alignment and spacing
4. Add borders and corner radius where specified

### Step 4: Test Placeholder Recognition
1. Share template with Make.com service account
2. Test each placeholder with sample data
3. Verify formatting is maintained
4. Check conditional formatting works

## Validation Checklist

### Text Placeholders
- [ ] All text placeholders use exact {{VARIABLE}} syntax
- [ ] Font formatting applied correctly
- [ ] Character limits respected
- [ ] Alignment matches specification
- [ ] Color codes are exact

### Image Placeholders
- [ ] Image frames sized correctly
- [ ] Alt text contains placeholder variables
- [ ] Default images are appropriate
- [ ] Borders and styling applied
- [ ] Transparency handled properly

### Layout Validation
- [ ] All elements positioned correctly
- [ ] Spacing is consistent
- [ ] No overlapping elements
- [ ] Responsive to content length variations
- [ ] Professional appearance maintained

### Make.com Compatibility
- [ ] Template shared with proper permissions
- [ ] All placeholders recognized by Make.com
- [ ] Variable mapping works correctly
- [ ] Conditional formatting functions
- [ ] PDF export maintains quality

## Error Handling

### Missing Data Scenarios
1. **No Screenshot**: Show default placeholder image
2. **No Logo**: Use generated colored rectangle
3. **Missing Phone**: Hide phone field
4. **No Website**: Show "Contact for details"
5. **Low Score Data**: Use fallback pain points

### Text Overflow
- Business names > 50 chars: Truncate with "..."
- Pain points > 80 chars: Wrap to next line
- Phone numbers: Format consistently
- Websites: Remove "http://" prefix

### Image Quality Issues
- Screenshots: Ensure minimum 800x600 resolution
- Logos: Maintain aspect ratio, add padding if needed
- Company logo: Use high-resolution version

## Testing Data Set

### Sample Variables for Testing
```json
{
  "BUSINESS_NAME": "Riverside Pizzeria",
  "MOBILE_SCORE": "45",
  "PAIN_POINT_1": "Slow loading speeds driving customers away",
  "PAIN_POINT_2": "Poor mobile experience losing sales",
  "PAIN_POINT_3": "Search engines ranking site lower",
  "BUSINESS_PHONE": "(559) 555-0123",
  "BUSINESS_WEBSITE": "www.riversidepizza.com",
  "WEBSITE_SCREENSHOT": "https://drive.google.com/screenshot123.png",
  "BUSINESS_LOGO": "https://drive.google.com/logo456.png",
  "COMPANY_LOGO": "https://drive.google.com/company789.png"
}
```

This specification ensures that all placeholder frames are properly implemented for seamless Make.com automation integration.