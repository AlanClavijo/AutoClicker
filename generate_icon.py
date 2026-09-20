from PIL import Image, ImageDraw, ImageFilter

def create_icon():
    # Base size 256x256
    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0)) # transparent background
    draw = ImageDraw.Draw(img)
    
    # 1. Draw rounded container background (charcoal card)
    margin = 8
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=48,
        fill=(30, 30, 36, 255),       # #1E1E24 Background
        outline=(52, 152, 219, 255),   # #3498db Neon Blue Border
        width=5
    )
    
    # 2. Draw a glowing target ring in the center
    # Create a separate layer for blurring the glow
    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    
    ring_radius = 45
    # Green glowing ring
    glow_draw.ellipse(
        [128 - ring_radius, 128 - ring_radius, 128 + ring_radius, 128 + ring_radius],
        outline=(46, 204, 113, 255),  # #2ecc71 Neon Green
        width=8
    )
    # Apply Gaussian blur for the glow effect
    blurred_glow = glow_layer.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, blurred_glow)
    
    # Draw sharp ring on top of the glow
    draw.ellipse(
        [128 - ring_radius, 128 - ring_radius, 128 + ring_radius, 128 + ring_radius],
        outline=(46, 204, 113, 255),
        width=3
    )
    
    # Draw central glowing dot
    dot_radius = 12
    draw.ellipse(
        [128 - dot_radius, 128 - dot_radius, 128 + dot_radius, 128 + dot_radius],
        fill=(52, 152, 219, 255)      # #3498db Neon Blue Dot
    )
    
    # 3. Draw white cursor arrow pointing to the center (128, 128)
    # Mouse cursor coordinates pointing at (128, 128) from bottom-right:
    cursor_poly = [
        (128, 128),     # Tip pointing at center
        (175, 150),     # Right corner
        (155, 165),     # Inside joint
        (175, 210),     # Bottom of tail
        (160, 217),     # Left of tail
        (140, 172),     # Left inside joint
        (125, 180)      # Left corner
    ]
    
    # Draw drop shadow for the cursor on a separate layer
    shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_offset = [(x + 4, y + 4) for (x, y) in cursor_poly]
    shadow_draw.polygon(shadow_offset, fill=(0, 0, 0, 140))
    shadow_blurred = shadow_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, shadow_blurred)
    
    # Draw the sharp white cursor with black outline on the main image
    draw.polygon(cursor_poly, fill=(255, 255, 255, 255), outline=(0, 0, 0, 255), width=2)
    
    # Save as ICO with multiple sizes for Windows Explorer
    ico_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save("app_icon.ico", format="ICO", sizes=ico_sizes)
    print("Icon generated successfully as app_icon.ico")

if __name__ == "__main__":
    create_icon()
