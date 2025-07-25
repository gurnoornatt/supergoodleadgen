# Make.com Automation Setup Guide

## Overview
This guide provides complete instructions for setting up Make.com automation to generate Pain-Gap Audit PDFs from Google Slides templates using data from Google Sheets.

## Prerequisites

### Required Make.com Apps
- Google Sheets (for watching new RED leads)
- Google Slides (for template manipulation)
- Google Drive (for PDF storage and sharing)
- HTTP/Webhooks (for error handling)

### Required API Permissions
- Google Slides API: Full access to presentations
- Google Drive API: File creation and sharing
- Google Sheets API: Read and write access

## Scenario Architecture

### 3-Step Make.com Scenario
```
Step 1: Google Sheets → Watch Rows (Trigger)
Step 2: Google Slides → Create from Template + Replace Placeholders
Step 3: Google Drive → Export PDF + Create Share Link + Update Sheet
```

## Detailed Step Configuration

### Step 1: Google Sheets Watch Rows
**Module**: Google Sheets > Watch Rows
**Configuration**:
```json
{
  "spreadsheet_id": "{{GOOGLE_SHEET_ID}}",
  "sheet_name": "RED Leads",
  "table_contains_headers": true,
  "limit": 10,
  "filter": {
    "column": "Status",
    "value": "RED",
    "condition": "equals"
  },
  "watch_column": "PDF Link",
  "trigger_when": "empty"
}
```

**Required Sheet Columns**:
- Business Name
- Mobile Score
- Pain Point 1
- Pain Point 2  
- Pain Point 3
- Business Phone
- Business Website
- Screenshot URL
- Logo URL
- Status (RED/GREEN)
- PDF Link (initially empty)
- Processing Status

### Step 2: Google Slides Template Processing

#### Module 2A: Create Presentation from Template
**Module**: Google Slides > Create a Presentation from Template
**Configuration**:
```json
{
  "template_id": "{{TEMPLATE_PRESENTATION_ID}}",
  "title": "Pain-Gap Audit - {{1.business_name}} - {{formatDate(now; 'YYYY-MM-DD')}}"
}
```

#### Module 2B: Replace Text Placeholders
**Module**: Google Slides > Replace Text
**Configuration**:
```json
{
  "presentation_id": "{{2A.presentation_id}}",
  "replacements": [
    {
      "replaceText": "{{BUSINESS_NAME}}",
      "withText": "{{1.business_name}}"
    },
    {
      "replaceText": "{{MOBILE_SCORE}}",
      "withText": "{{1.mobile_score}}"
    },
    {
      "replaceText": "{{PAIN_POINT_1}}",
      "withText": "{{1.pain_point_1}}"
    },
    {
      "replaceText": "{{PAIN_POINT_2}}",
      "withText": "{{1.pain_point_2}}"
    },
    {
      "replaceText": "{{PAIN_POINT_3}}",
      "withText": "{{1.pain_point_3}}"
    },
    {
      "replaceText": "{{BUSINESS_PHONE}}",
      "withText": "{{1.business_phone}}"
    },
    {
      "replaceText": "{{BUSINESS_WEBSITE}}",
      "withText": "{{1.business_website}}"
    }
  ]
}
```

#### Module 2C: Replace Image Placeholders
**Module**: Google Slides > Replace Image
**Configuration for Screenshot**:
```json
{
  "presentation_id": "{{2A.presentation_id}}",
  "page_object_id": "screenshot_frame",
  "image_url": "{{1.screenshot_url}}",
  "replace_method": "CENTER_INSIDE"
}
```

**Configuration for Business Logo**:
```json
{
  "presentation_id": "{{2A.presentation_id}}",
  "page_object_id": "business_logo_frame", 
  "image_url": "{{1.logo_url}}",
  "replace_method": "CENTER_INSIDE"
}
```

**Configuration for Company Logo**:
```json
{
  "presentation_id": "{{2A.presentation_id}}",
  "page_object_id": "company_logo_frame",
  "image_url": "{{COMPANY_LOGO_URL}}",
  "replace_method": "CENTER_INSIDE"
}
```

#### Module 2D: Apply Conditional Formatting
**Module**: Google Slides > Update Shape Properties
**Configuration**:
```json
{
  "presentation_id": "{{2A.presentation_id}}",
  "page_object_id": "score_background",
  "shape_properties": {
    "shapeBackgroundFill": {
      "solidFill": {
        "color": {
          "rgbColor": "{{if(1.mobile_score < 60; parseColor('#E74C3C'); parseColor('#27AE60'))}}"
        }
      }
    }
  }
}
```

### Step 3: PDF Export and Storage

#### Module 3A: Export as PDF
**Module**: Google Drive > Export a File
**Configuration**:
```json
{
  "file_id": "{{2A.presentation_id}}",
  "format": "pdf",
  "file_name": "Pain-Gap-Audit-{{1.business_name}}-{{formatDate(now; 'YYYY-MM-DD')}}.pdf"
}
```

#### Module 3B: Upload PDF to Designated Folder
**Module**: Google Drive > Upload a File
**Configuration**:
```json
{
  "folder_id": "{{PDF_STORAGE_FOLDER_ID}}",
  "file_name": "{{3A.file_name}}",
  "data": "{{3A.data}}",
  "convert": false
}
```

#### Module 3C: Create Public Share Link
**Module**: Google Drive > Create a Share Link
**Configuration**:
```json
{
  "file_id": "{{3B.file_id}}",
  "access": "anyone",
  "role": "reader"
}
```

#### Module 3D: Update Google Sheet with PDF Link
**Module**: Google Sheets > Update a Row
**Configuration**:
```json
{
  "spreadsheet_id": "{{GOOGLE_SHEET_ID}}",
  "sheet_name": "RED Leads",
  "row": "{{1.__row_number__}}",
  "values": {
    "PDF Link": "{{3C.webViewLink}}",
    "Processing Status": "Completed",
    "PDF Generated": "{{formatDate(now; 'YYYY-MM-DD HH:mm:ss')}}"
  }
}
```

## Error Handling Configuration

### Error Handler Module
**Module**: Tools > Error Handler
**Configuration**:
```json
{
  "scope": "all_modules",
  "fallback_action": "update_sheet_with_error",
  "retry_attempts": 3,
  "retry_interval": 60
}
```

### Error Logging Module
**Module**: Google Sheets > Add a Row
**Configuration**:
```json
{
  "spreadsheet_id": "{{ERROR_LOG_SHEET_ID}}",
  "sheet_name": "Processing Errors",
  "values": {
    "Timestamp": "{{formatDate(now; 'YYYY-MM-DD HH:mm:ss')}}",
    "Business Name": "{{1.business_name}}",
    "Error Type": "{{error.type}}",
    "Error Message": "{{error.message}}",
    "Step Failed": "{{error.module}}",
    "Original Row": "{{1.__row_number__}}"
  }
}
```

## Template Requirements for Make.com

### Google Slides Template Setup

#### Required Named Elements
```json
{
  "text_elements": [
    "business_name_text",
    "mobile_score_text", 
    "pain_point_1_text",
    "pain_point_2_text",
    "pain_point_3_text",
    "business_phone_text",
    "business_website_text"
  ],
  "image_elements": [
    "screenshot_frame",
    "business_logo_frame",
    "company_logo_frame"
  ],
  "shape_elements": [
    "score_background"
  ]
}
```

#### Template Sharing Configuration
- **Share with**: Make.com service account email
- **Permission Level**: Editor
- **Template Location**: Shared Google Drive folder
- **Template Naming**: "Pain-Gap-Audit-Template-v1"

### Google Sheets Data Format

#### Required Column Headers (Exact Names)
```
Column A: Business Name
Column B: Mobile Score  
Column C: Pain Point 1
Column D: Pain Point 2
Column E: Pain Point 3
Column F: Business Phone
Column G: Business Website
Column H: Screenshot URL
Column I: Logo URL
Column J: Status
Column K: PDF Link
Column L: Processing Status
Column M: PDF Generated
Column N: Error Notes
```

#### Data Validation Rules
- **Mobile Score**: Number, 0-100
- **Status**: Data validation list ["RED", "GREEN"]
- **URLs**: Format validation for proper URL structure
- **Phone**: Format "(XXX) XXX-XXXX"

## Make.com Service Account Setup

### Required Google Cloud Configuration
1. **Create Service Account**:
   - Project: Pain-Gap-Audit-Automation
   - Service Account Name: makecom-automation
   - Role: Editor

2. **Enable APIs**:
   - Google Slides API
   - Google Drive API  
   - Google Sheets API

3. **Generate Key**:
   - Key Type: JSON
   - Store securely for Make.com configuration

### Make.com Connection Setup
1. **Add Google Connection**:
   - Connection Type: Google (Service Account)
   - Upload JSON key file
   - Test connection with sample operation

2. **Connection Permissions**:
   - Slides: Create, read, update presentations
   - Drive: Create files, manage sharing
   - Sheets: Read data, update cells

## Testing and Validation

### Pre-Launch Testing Checklist
- [ ] Template placeholders correctly mapped
- [ ] All image replacements working
- [ ] Conditional formatting functioning
- [ ] PDF export quality acceptable
- [ ] Share links generated correctly
- [ ] Sheet updates successful
- [ ] Error handling triggers properly
- [ ] Processing time under 2 minutes per lead

### Test Data Scenarios
1. **Normal Case**: Valid business data, all fields populated
2. **Missing Logo**: Business logo URL empty or invalid
3. **Long Business Name**: Name exceeding 50 characters
4. **Perfect Score**: Mobile score of 100
5. **Minimum Score**: Mobile score under 10
6. **Missing Phone/Website**: Empty contact fields

### Performance Monitoring
- **Success Rate**: Target >95% successful PDF generation
- **Processing Time**: Target <2 minutes per lead
- **Error Rate**: Target <5% failures requiring manual intervention
- **Queue Management**: Handle up to 50 concurrent requests

## Deployment Steps

### Phase 1: Template and Sheet Setup
1. Create Google Slides template with all placeholders
2. Set up Google Sheet with proper column structure
3. Configure folder structure in Google Drive
4. Test template manually with sample data

### Phase 2: Make.com Scenario Development
1. Create new Make.com scenario
2. Configure each module according to specifications
3. Set up error handling and logging
4. Test with small batch of leads

### Phase 3: Integration Testing
1. Connect Python script to write RED leads to sheet
2. Verify Make.com triggers on new rows
3. Test complete pipeline end-to-end
4. Validate PDF quality and accessibility

### Phase 4: Production Deployment
1. Configure production Google Sheet
2. Set up monitoring and alerting
3. Train VA on accessing completed PDFs
4. Document troubleshooting procedures

## Troubleshooting Guide

### Common Issues and Solutions

#### Template Not Found
- **Cause**: Incorrect template ID or sharing permissions
- **Solution**: Verify template sharing and ID accuracy

#### Placeholder Not Replaced
- **Cause**: Exact text match required, case-sensitive
- **Solution**: Check placeholder text matches exactly

#### Image Replacement Failed
- **Cause**: Invalid URL or inaccessible image
- **Solution**: Validate image URLs and accessibility

#### PDF Export Failed
- **Cause**: Presentation too large or corrupted
- **Solution**: Check presentation integrity and size

#### Sheet Update Failed
- **Cause**: Row moved or sheet structure changed
- **Solution**: Verify sheet structure and row references

### Performance Optimization
- **Batch Processing**: Group multiple leads when possible
- **Image Optimization**: Compress images before upload
- **Template Optimization**: Minimize template complexity
- **Caching**: Cache static assets like company logo
- **Monitoring**: Set up alerts for processing delays

This setup ensures reliable, automated PDF generation with comprehensive error handling and monitoring capabilities.