from PIL import Image, ImageDraw, ImageFont
import os

def generate_icons():
    # Create icons directory if it doesn't exist
    os.makedirs('static/icons', exist_ok=True)
    
    # Create a simple placeholder logo with text if the logo doesn't exist
    if not os.path.exists('static/ekam-logo.png'):
        img = Image.new('RGBA', (512, 512), (13, 110, 253, 255))  # Primary blue
        d = ImageDraw.Draw(img)
        
        # Try to use a nice font if available, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 80)
        except:
            font = ImageFont.load_default()
            
        # Draw E-KAM text
        text = "E-KAM"
        # Get text bounding box
        bbox = d.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        position = ((512 - text_width) // 2, (512 - text_height) // 2)
        d.text(position, text, fill=(255, 255, 255), font=font)
        img.save('static/ekam-logo.png')
        print("Created placeholder logo at static/ekam-logo.png")
    
    # Define required icon sizes
    icon_sizes = [
        ('favicon-16.png', 16),
        ('favicon-32.png', 32),
        ('apple-touch-icon.png', 180),
        ('icon-192.png', 192),
        ('icon-512.png', 512),
        ('icon-512-maskable.png', 512)  # Will be masked by the browser
    ]
    
    for filename, size in icon_sizes:
        # Create a new image with the specified size
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        
        # Load the logo
        try:
            logo = Image.open('static/ekam-logo.png').convert('RGBA')
            
            # Calculate dimensions to maintain aspect ratio
            logo.thumbnail((size, size), Image.Resampling.LANCZOS)
            
            # Calculate position to center the logo
            x = (size - logo.width) // 2
            y = (size - logo.height) // 2
            
            # Paste the logo onto the transparent background
            img.paste(logo, (x, y), logo)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            # Create a simple colored circle as fallback
            d = ImageDraw.Draw(img)
            d.ellipse((0, 0, size, size), fill=(13, 110, 253, 255))
        
        # Save the icon
        img.save(f'static/icons/{filename}', 'PNG')
        print(f"Generated: static/icons/{filename}")

if __name__ == '__main__':
    generate_icons()
