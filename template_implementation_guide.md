# Google Slides Template Implementation Guide
## Complete Step-by-Step Instructions

## Overview
This guide provides detailed instructions for creating the Pain-Gap Audit PDF template in Google Slides, incorporating professional design, branding, and Make.com automation compatibility.

## Prerequisites
- Google account with Slides access
- Generated design assets (from design_asset_generator.py)
- Brand color palette and typography specifications
- Make.com automation specifications

## Template Creation Process

### Phase 1: Initial Setup

#### Step 1: Create New Google Slides Presentation
1. Go to Google Slides (slides.google.com)
2. Click "Blank presentation"
3. Set slide size to Custom: 16:9 (1920×1080)
4. Name presentation: "Pain-Gap-Audit-Template-v1"

#### Step 2: Configure Master Slide
1. Go to Slide → Edit master
2. Delete existing layouts except the first one
3. Set background to white (#FFFFFF)
4. Configure safe margins: 60px from all edges

### Phase 2: Header Section Design

#### Step 3: Create Header Zone
```css
Position: Top of slide
Height: 120px (11% of slide)
Background: Linear gradient (#ECF0F1 to #FFFFFF)
```

**Implementation**:
1. Insert → Shape → Rectangle
2. Resize to full width × 120px height
3. Position at top of slide
4. Right-click → Format options → Fill color → Gradient
5. Configure gradient: Start #ECF0F1, End #FFFFFF, Direction: Diagonal

#### Step 4: Add Company Logo Placeholder
```css
Position: Top-left corner (80px from left, 30px from top)
Size: 180px × 60px
```

**Implementation**:
1. Insert → Image → Upload from computer
2. Upload placeholder image or create text box
3. Add alt text: "{{COMPANY_LOGO}}"
4. Resize to 180×60px
5. Position in top-left

#### Step 5: Add Main Title
```css
Text: "Website Performance Audit"
Font: Poppins Bold, 28px
Color: #2C3E50
Position: Center of header
```

**Implementation**:
1. Insert → Text box
2. Type: "Website Performance Audit"
3. Format → Font → Poppins (or Arial as fallback)
4. Font size: 28px, Bold
5. Color: #2C3E50
6. Center horizontally in header

#### Step 6: Add Business Name Placeholder
```css
Text: "{{BUSINESS_NAME}}"
Font: Poppins Semi-Bold, 22px
Color: #34495E
Position: Top-right corner
```

**Implementation**:
1. Insert → Text box
2. Type: "{{BUSINESS_NAME}}"
3. Font: Poppins Semi-Bold, 22px
4. Color: #34495E
5. Position in top-right corner
6. Add background: White with subtle shadow

### Phase 3: Main Content Area

#### Step 7: Create Content Grid
1. Use guides to mark columns:
   - Left column: 60px to 1212px (1152px width)
   - Right column: 1252px to 1860px (648px width)
   - Gutter: 40px between columns

#### Step 8: Left Column - Screenshot Area

**Screenshot Container**:
```css
Background: #FFFFFF
Border: 3px solid #E74C3C
Border-radius: 12px
Size: 640px × 480px
Position: Centered in left column
```

**Implementation**:
1. Insert → Shape → Rounded rectangle
2. Resize to 640×480px
3. Fill: White (#FFFFFF)
4. Border: 3px, #E74C3C
5. Corner radius: 12px
6. Position in left column center

**Screenshot Placeholder**:
1. Insert → Image → placeholder image
2. Add alt text: "{{WEBSITE_SCREENSHOT}}"
3. Resize to fit within container (620×460px)
4. Position inside bordered container

**Caption**:
1. Insert → Text box below screenshot
2. Text: "Current Website"
3. Font: Poppins Regular, 14px
4. Color: #7F8C8D
5. Center align

#### Step 9: Right Column - Performance Score

**Score Container**:
```css
Background: Conditional (#E74C3C for RED, #27AE60 for GREEN)
Size: 300px × 200px
Border-radius: 16px
Position: Top of right column
```

**Implementation**:
1. Insert → Shape → Rounded rectangle
2. Resize to 300×200px
3. Fill: #E74C3C (will be conditional in Make.com)
4. Corner radius: 16px
5. Name shape: "score_background"

**Score Text**:
1. Insert → Text box inside score container
2. Text: "{{MOBILE_SCORE}}"
3. Font: Poppins Bold, 48px
4. Color: White (#FFFFFF)
5. Center align

**Score Label**:
1. Insert → Text box below score
2. Text: "/100"
3. Font: Poppins Medium, 16px
4. Color: White (#FFFFFF)
5. Center align

**Performance Label**:
1. Insert → Text box below score
2. Text: "Mobile Performance"
3. Font: Poppins Medium, 16px
4. Color: White (#FFFFFF)
5. Center align

#### Step 10: Right Column - Pain Points Section

**Pain Points Container**:
```css
Background: #FFFFFF
Border: 2px solid #BDC3C7
Border-radius: 12px
Size: 580px × 300px
Position: Below score container
```

**Implementation**:
1. Insert → Shape → Rounded rectangle
2. Resize to 580×300px
3. Fill: White (#FFFFFF)
4. Border: 2px, #BDC3C7
5. Corner radius: 12px

**Pain Points Header**:
1. Insert → Text box
2. Text: "Critical Issues Found:"
3. Font: Poppins Bold, 18px
4. Color: #E74C3C
5. Position at top of container

**Pain Point Bullets**:
Create three text boxes for pain points:

**Pain Point 1**:
1. Insert → Text box
2. Text: "• {{PAIN_POINT_1}}"
3. Font: Poppins Medium, 14px
4. Color: #E74C3C
5. Line height: 1.4

**Pain Point 2**:
1. Insert → Text box
2. Text: "• {{PAIN_POINT_2}}"
3. Font: Poppins Medium, 14px
4. Color: #E74C3C
5. Line height: 1.4

**Pain Point 3**:
1. Insert → Text box
2. Text: "• {{PAIN_POINT_3}}"
3. Font: Poppins Medium, 14px
4. Color: #E74C3C
5. Line height: 1.4

### Phase 4: Footer Section

#### Step 11: Create Footer Zone
```css
Position: Bottom of slide
Height: 120px (11% of slide)
Background: Linear gradient (#34495E to #2C3E50)
```

**Implementation**:
1. Insert → Shape → Rectangle
2. Resize to full width × 120px height
3. Position at bottom of slide
4. Fill: Gradient from #34495E to #2C3E50

#### Step 12: Business Logo Placeholder
```css
Position: Left side of footer
Size: 120px × 40px
Background: White rounded container
```

**Implementation**:
1. Insert → Shape → Rounded rectangle (white background)
2. Size: 140×60px (container)
3. Insert → Image placeholder inside
4. Add alt text: "{{BUSINESS_LOGO}}"
5. Resize image to 120×40px

#### Step 13: Call-to-Action Center
```css
Text: "Get Your FREE $1 Website Audit Call"
Background: #E74C3C
Font: Poppins Bold, 18px
Color: White
Border-radius: 8px
```

**Implementation**:
1. Insert → Shape → Rounded rectangle
2. Fill: #E74C3C
3. Size: 400×60px
4. Corner radius: 8px
5. Insert → Text box on top
6. Text: "Get Your FREE $1 Website Audit Call"
7. Font: Poppins Bold, 18px
8. Color: White
9. Center align

#### Step 14: Contact Information
```css
Position: Right side of footer
Color: White
Font: Poppins Regular, 12px
```

**Phone Number**:
1. Insert → Text box
2. Text: "{{BUSINESS_PHONE}}"
3. Font: Poppins Regular, 12px
4. Color: White

**Website**:
1. Insert → Text box
2. Text: "{{BUSINESS_WEBSITE}}"
3. Font: Poppins Regular, 12px
4. Color: White

### Phase 5: Make.com Configuration

#### Step 15: Name Elements for Make.com
Ensure all placeholder elements have proper names:

1. **Text Elements**:
   - business_name_text
   - mobile_score_text
   - pain_point_1_text
   - pain_point_2_text
   - pain_point_3_text
   - business_phone_text
   - business_website_text

2. **Image Elements**:
   - screenshot_frame
   - business_logo_frame
   - company_logo_frame

3. **Shape Elements**:
   - score_background (for conditional coloring)

#### Step 16: Configure Sharing
1. Click "Share" in top-right
2. Change to "Anyone with the link can edit"
3. Add Make.com service account email as Editor
4. Copy template link/ID for Make.com configuration

### Phase 6: Testing and Validation

#### Step 17: Test with Sample Data
Using the generated test data:

1. **Manual Test**:
   - Replace each placeholder with sample data
   - Check formatting and layout
   - Verify all elements fit properly
   - Test with long business names
   - Test with different score ranges

2. **Automated Validation**:
   - Run make_com_compatibility_validator.py
   - Check validation report
   - Fix any identified issues

#### Step 18: PDF Export Test
1. File → Download → PDF Document (.pdf)
2. Check PDF quality and formatting
3. Verify all elements render correctly
4. Test file size (should be under 2MB)
5. Check print quality if needed

### Phase 7: Make.com Integration Setup

#### Step 19: Create Make.com Scenario
Follow the make_com_automation_setup.md guide:

1. Set up Google Sheets trigger
2. Configure Google Slides modules
3. Set up image replacement
4. Configure conditional formatting
5. Set up PDF export and sharing
6. Test complete workflow

#### Step 20: Production Deployment
1. Create production Google Sheet
2. Set up monitoring and alerting
3. Train team on usage
4. Document troubleshooting procedures

## Quality Assurance Checklist

### Design Quality
- [ ] All brand colors applied correctly
- [ ] Typography hierarchy consistent
- [ ] Layout grid properly implemented
- [ ] Professional appearance maintained
- [ ] Color contrast meets accessibility standards

### Functionality
- [ ] All placeholders properly formatted
- [ ] Make.com can recognize all elements
- [ ] Conditional formatting works
- [ ] PDF export maintains quality
- [ ] File size under 2MB

### Content
- [ ] Professional messaging
- [ ] Clear call-to-action
- [ ] Proper placeholder syntax
- [ ] Error handling for missing data
- [ ] Responsive to content variations

### Integration
- [ ] Make.com scenario configured
- [ ] Google Sheet properly structured
- [ ] Automation triggers correctly
- [ ] Error handling implemented
- [ ] Monitoring set up

## Troubleshooting

### Common Issues

#### Placeholder Not Replaced
- **Cause**: Exact text match required
- **Solution**: Verify placeholder text matches exactly

#### Font Not Loading
- **Cause**: Poppins not available
- **Solution**: Use Arial or system font as fallback

#### Layout Breaking
- **Cause**: Text too long for containers
- **Solution**: Implement text truncation in data processing

#### PDF Quality Poor
- **Cause**: Low resolution export
- **Solution**: Ensure high-quality export settings

#### Colors Not Matching
- **Cause**: Different color profiles
- **Solution**: Use exact hex codes, embed color profiles

This comprehensive implementation guide ensures professional, functional, and automated PDF template creation that meets all business requirements.