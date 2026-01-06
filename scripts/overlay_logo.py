"""
Logo overlay utility for adding branding to generated images.
"""

from PIL import Image
from pathlib import Path


def add_logo(
    image_path: str,
    logo_path: str,
    position: str = "bottom-left",
    padding: int = 40,
    logo_width: int = 180,
    opacity: float = 1.0
) -> str:
    """
    Overlay logo on image.

    Args:
        image_path: Path to the image to modify
        logo_path: Path to the logo file (PNG with transparency)
        position: Logo position (bottom-left, bottom-right, top-left, top-right)
        padding: Padding from edges in pixels
        logo_width: Desired logo width in pixels
        opacity: Logo opacity (0.0 to 1.0)

    Returns:
        Path to the modified image
    """

    # Open images
    img = Image.open(image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    # Resize logo maintaining aspect ratio
    ratio = logo_width / logo.width
    new_height = int(logo.height * ratio)
    logo = logo.resize((logo_width, new_height), Image.Resampling.LANCZOS)

    # Apply opacity if needed
    if opacity < 1.0:
        alpha = logo.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity))
        logo.putalpha(alpha)

    # Calculate position
    positions = {
        "bottom-left": (padding, img.height - logo.height - padding),
        "bottom-right": (img.width - logo.width - padding, img.height - logo.height - padding),
        "top-left": (padding, padding),
        "top-right": (img.width - logo.width - padding, padding),
        "center": ((img.width - logo.width) // 2, (img.height - logo.height) // 2),
    }

    x, y = positions.get(position, positions["bottom-left"])

    # Paste logo with transparency
    img.paste(logo, (x, y), logo)

    # Convert back to RGB if needed and save
    if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        img = img.convert("RGB")

    img.save(image_path)

    return image_path


def add_text_watermark(
    image_path: str,
    text: str,
    position: str = "bottom-right",
    font_size: int = 24,
    color: tuple = (0, 0, 0, 128),
    padding: int = 20
) -> str:
    """
    Add text watermark to image.

    Args:
        image_path: Path to the image
        text: Watermark text
        position: Text position
        font_size: Font size
        color: RGBA color tuple
        padding: Padding from edges

    Returns:
        Path to the modified image
    """
    from PIL import ImageDraw, ImageFont

    img = Image.open(image_path).convert("RGBA")

    # Create transparent overlay
    txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)

    # Use default font (or specify custom font path)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Calculate position
    positions = {
        "bottom-left": (padding, img.height - text_height - padding),
        "bottom-right": (img.width - text_width - padding, img.height - text_height - padding),
        "top-left": (padding, padding),
        "top-right": (img.width - text_width - padding, padding),
    }

    x, y = positions.get(position, positions["bottom-right"])

    # Draw text
    draw.text((x, y), text, font=font, fill=color)

    # Composite and save
    img = Image.alpha_composite(img, txt_layer)
    img.save(image_path)

    return image_path


if __name__ == "__main__":
    # Quick test
    import sys

    if len(sys.argv) >= 3:
        add_logo(sys.argv[1], sys.argv[2])
        print(f"Logo added to {sys.argv[1]}")
    else:
        print("Usage: python overlay_logo.py <image_path> <logo_path>")
