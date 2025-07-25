#!/usr/bin/env python3
"""
Design Asset Generator
Creates visual assets for the Google Slides template including fallback logos and design elements
"""

import os
import hashlib
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List, Dict
import colorsys
import json

class DesignAssetGenerator:
    """Generates design assets for the PDF template"""
    
    def __init__(self):
        self.brand_colors = {
            'primary_red': '#E74C3C',
            'authority_blue': '#2C3E50', 
            'success_green': '#27AE60',
            'body_gray': '#34495E',
            'support_gray': '#7F8C8D',
            'light_gray': '#BDC3C7',
            'background': '#ECF0F1',
            'white': '#FFFFFF'
        }
        
        self.assets_dir = "design_assets"
        self.create_assets_directory()

    def create_assets_directory(self):
        """Create directory for design assets"""
        if not os.path.exists(self.assets_dir):
            os.makedirs(self.assets_dir)

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def generate_business_name_color(self, business_name: str) -> str:
        """Generate consistent color based on business name"""
        # Create hash of business name
        hash_object = hashlib.md5(business_name.encode())
        hash_hex = hash_object.hexdigest()
        
        # Use first 6 characters as color, but ensure it's not too light
        base_color = f"#{hash_hex[:6]}"
        rgb = self.hex_to_rgb(base_color)
        
        # Ensure minimum darkness for readability
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        
        # Ensure saturation is at least 0.6 and value is at least 0.4
        s = max(s, 0.6)
        v = max(v, 0.4)
        v = min(v, 0.8)  # Not too bright
        
        rgb = colorsys.hsv_to_rgb(h, s, v)
        return f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}"

    def create_fallback_logo(self, business_name: str, size: Tuple[int, int] = (400, 120)) -> str:
        """Create fallback logo for businesses without logos"""
        
        # Generate color based on business name
        bg_color = self.generate_business_name_color(business_name)
        
        # Create image
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw rounded rectangle background
        margin = 8
        corner_radius = 12
        
        # Draw rounded rectangle
        draw.rounded_rectangle(
            [(margin, margin), (size[0] - margin, size[1] - margin)],
            corner_radius,
            fill=self.hex_to_rgb(bg_color)
        )
        
        # Add gradient effect (simulate with overlapping rectangles)
        overlay = Image.new('RGBA', size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Light overlay for gradient effect
        overlay_draw.rounded_rectangle(
            [(margin, margin), (size[0] - margin, size[1] // 2)],
            corner_radius,
            fill=(255, 255, 255, 30)
        )
        
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fall back to default if unavailable
        try:
            # Try different font sizes to fit text
            font_size = min(size[1] // 3, 32)
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                font = None
        
        # Prepare text
        display_name = business_name.upper()
        if len(display_name) > 20:
            display_name = display_name[:17] + "..."
        
        # Get text dimensions
        if font:
            bbox = draw.textbbox((0, 0), display_name, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width = len(display_name) * 8
            text_height = 16
        
        # Center text
        text_x = (size[0] - text_width) // 2
        text_y = (size[1] - text_height) // 2
        
        # Draw text with shadow
        shadow_offset = 2
        draw.text((text_x + shadow_offset, text_y + shadow_offset), display_name, 
                 fill=(0, 0, 0, 100), font=font)
        draw.text((text_x, text_y), display_name, fill=(255, 255, 255, 255), font=font)
        
        # Save logo
        filename = f"fallback_logo_{business_name.replace(' ', '_').lower()}.png"
        filepath = os.path.join(self.assets_dir, filename)
        img.save(filepath, 'PNG')
        
        return filepath

    def create_performance_score_badge(self, score: int, size: Tuple[int, int] = (200, 200)) -> str:
        """Create performance score badge"""
        
        # Determine color based on score
        if score < 60:
            bg_color = self.brand_colors['primary_red']
            status = "RED"
        else:
            bg_color = self.brand_colors['success_green']  
            status = "GREEN"
        
        # Create circular badge
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw circle
        margin = 20
        draw.ellipse(
            [(margin, margin), (size[0] - margin, size[1] - margin)],
            fill=self.hex_to_rgb(bg_color)
        )
        
        # Add inner shadow effect
        shadow_margin = margin + 10
        draw.ellipse(
            [(shadow_margin, shadow_margin), (size[0] - shadow_margin, size[1] - shadow_margin)],
            outline=(0, 0, 0, 50),
            width=2
        )
        
        # Try to load font
        try:
            score_font = ImageFont.truetype("arial.ttf", 48)
            label_font = ImageFont.truetype("arial.ttf", 16)
        except:
            score_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
        
        # Draw score
        score_text = str(score)
        score_bbox = draw.textbbox((0, 0), score_text, font=score_font)
        score_width = score_bbox[2] - score_bbox[0]
        score_height = score_bbox[3] - score_bbox[1]
        
        score_x = (size[0] - score_width) // 2
        score_y = (size[1] - score_height) // 2 - 10
        
        draw.text((score_x, score_y), score_text, fill=(255, 255, 255), font=score_font)
        
        # Draw "/100" label
        label_text = "/100"
        label_bbox = draw.textbbox((0, 0), label_text, font=label_font)
        label_width = label_bbox[2] - label_bbox[0]
        
        label_x = (size[0] - label_width) // 2
        label_y = score_y + score_height + 5
        
        draw.text((label_x, label_y), label_text, fill=(255, 255, 255, 200), font=label_font)
        
        # Save badge
        filename = f"score_badge_{score}_{status.lower()}.png"
        filepath = os.path.join(self.assets_dir, filename)
        img.save(filepath, 'PNG')
        
        return filepath

    def create_pain_point_icons(self, size: Tuple[int, int] = (24, 24)) -> List[str]:
        """Create warning icons for pain points"""
        
        icons = []
        
        # Warning triangle icon
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw warning triangle
        center_x, center_y = size[0] // 2, size[1] // 2
        triangle_size = min(size) // 2 - 2
        
        triangle_points = [
            (center_x, center_y - triangle_size),
            (center_x - triangle_size, center_y + triangle_size),
            (center_x + triangle_size, center_y + triangle_size)
        ]
        
        draw.polygon(triangle_points, fill=self.hex_to_rgb(self.brand_colors['primary_red']))
        
        # Draw exclamation mark
        try:
            font = ImageFont.truetype("arial.ttf", 14)
        except:
            font = ImageFont.load_default()
        
        draw.text((center_x - 3, center_y - 8), "!", fill=(255, 255, 255), font=font)
        
        # Save icon
        filename = "warning_icon.png"
        filepath = os.path.join(self.assets_dir, filename)
        img.save(filepath, 'PNG')
        icons.append(filepath)
        
        return icons

    def create_template_background(self, size: Tuple[int, int] = (1920, 1080)) -> str:
        """Create professional background for template"""
        
        # Create gradient background
        img = Image.new('RGB', size, self.hex_to_rgb(self.brand_colors['white']))
        draw = ImageDraw.Draw(img)
        
        # Add subtle gradient overlay
        for y in range(size[1]):
            alpha = int(255 * (1 - y / size[1] * 0.1))
            color = (self.hex_to_rgb(self.brand_colors['background'])[0], 
                    self.hex_to_rgb(self.brand_colors['background'])[1],
                    self.hex_to_rgb(self.brand_colors['background'])[2])
            
            if y < 100:  # Header area
                draw.line([(0, y), (size[0], y)], fill=color)
        
        # Save background
        filename = "template_background.png"
        filepath = os.path.join(self.assets_dir, filename)
        img.save(filepath, 'PNG')
        
        return filepath

    def generate_sample_assets(self) -> Dict:
        """Generate sample assets for testing"""
        
        sample_businesses = [
            "Riverside Pizzeria",
            "Central Valley Auto Repair",
            "Fresno Family Dentistry"
        ]
        
        sample_scores = [25, 45, 85]
        
        generated_assets = {
            'fallback_logos': [],
            'score_badges': [],
            'icons': [],
            'backgrounds': []
        }
        
        # Generate fallback logos
        for business in sample_businesses:
            logo_path = self.create_fallback_logo(business)
            generated_assets['fallback_logos'].append({
                'business': business,
                'path': logo_path
            })
        
        # Generate score badges
        for score in sample_scores:
            badge_path = self.create_performance_score_badge(score)
            generated_assets['score_badges'].append({
                'score': score,
                'path': badge_path
            })
        
        # Generate icons
        icon_paths = self.create_pain_point_icons()
        generated_assets['icons'] = icon_paths
        
        # Generate background
        bg_path = self.create_template_background()
        generated_assets['backgrounds'].append(bg_path)
        
        return generated_assets

    def create_brand_color_palette(self) -> str:
        """Create visual color palette reference"""
        
        palette_width = 800
        palette_height = 600
        color_height = palette_height // len(self.brand_colors)
        
        img = Image.new('RGB', (palette_width, palette_height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 24)
            small_font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        y_offset = 0
        for color_name, hex_color in self.brand_colors.items():
            # Draw color rectangle
            color_rect_width = 200
            draw.rectangle(
                [(0, y_offset), (color_rect_width, y_offset + color_height)],
                fill=self.hex_to_rgb(hex_color)
            )
            
            # Draw color name and hex
            text_x = color_rect_width + 20
            text_y = y_offset + color_height // 2 - 20
            
            draw.text((text_x, text_y), color_name.replace('_', ' ').title(), 
                     fill=(0, 0, 0), font=font)
            draw.text((text_x, text_y + 30), hex_color, 
                     fill=(100, 100, 100), font=small_font)
            
            y_offset += color_height
        
        # Save palette
        filename = "brand_color_palette.png"
        filepath = os.path.join(self.assets_dir, filename)
        img.save(filepath, 'PNG')
        
        return filepath

    def generate_design_specs_json(self) -> str:
        """Generate JSON file with design specifications"""
        
        specs = {
            "brand_colors": self.brand_colors,
            "typography": {
                "primary_font": "Poppins",
                "font_weights": {
                    "light": 300,
                    "regular": 400,
                    "medium": 500,
                    "semi_bold": 600,
                    "bold": 700
                },
                "font_sizes": {
                    "main_title": 28,
                    "business_name": 22,
                    "section_header": 18,
                    "body_text": 14,
                    "pain_points": 14,
                    "cta": 18,
                    "supporting": 12
                }
            },
            "layout": {
                "page_size": {
                    "width": 1920,
                    "height": 1080,
                    "aspect_ratio": "16:9"
                },
                "zones": {
                    "header_height": 120,
                    "content_height": 840,
                    "footer_height": 120
                },
                "margins": {
                    "outer": 60,
                    "inner": 40,
                    "safe_zone": 40
                },
                "columns": {
                    "left_width": 1152,
                    "right_width": 648,
                    "gutter": 40
                }
            },
            "placeholder_mapping": {
                "text_placeholders": [
                    "{{BUSINESS_NAME}}",
                    "{{MOBILE_SCORE}}",
                    "{{PAIN_POINT_1}}",
                    "{{PAIN_POINT_2}}",
                    "{{PAIN_POINT_3}}",
                    "{{BUSINESS_PHONE}}",
                    "{{BUSINESS_WEBSITE}}"
                ],
                "image_placeholders": [
                    "{{WEBSITE_SCREENSHOT}}",
                    "{{BUSINESS_LOGO}}",
                    "{{COMPANY_LOGO}}"
                ]
            }
        }
        
        filename = "design_specifications.json"
        filepath = os.path.join(self.assets_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(specs, f, indent=2, ensure_ascii=False)
        
        return filepath

def main():
    """Generate all design assets"""
    
    generator = DesignAssetGenerator()
    
    print("🎨 Generating design assets...")
    
    # Generate sample assets
    assets = generator.generate_sample_assets()
    
    # Generate brand color palette
    palette_path = generator.create_brand_color_palette()
    
    # Generate design specifications
    specs_path = generator.generate_design_specs_json()
    
    print(f"\n✅ Design assets generated successfully!")
    print(f"📁 Assets directory: {generator.assets_dir}/")
    print(f"\n📊 Generated Assets:")
    print(f"  • {len(assets['fallback_logos'])} fallback logos")
    print(f"  • {len(assets['score_badges'])} score badges")
    print(f"  • {len(assets['icons'])} icons")
    print(f"  • {len(assets['backgrounds'])} background")
    print(f"  • Brand color palette: {palette_path}")
    print(f"  • Design specifications: {specs_path}")
    
    print(f"\n🎯 Sample Fallback Logos:")
    for logo in assets['fallback_logos']:
        print(f"  • {logo['business']}: {logo['path']}")
    
    print(f"\n📈 Sample Score Badges:")
    for badge in assets['score_badges']:
        print(f"  • Score {badge['score']}: {badge['path']}")

if __name__ == "__main__":
    main()