#!/usr/bin/env python3
"""
Pipeline 2: AI Infographic Generator
Uses Google Gemini API to generate educational infographics.

Usage:
    python generate_infographic.py --id <question_id> --type pearl
    python generate_infographic.py --id <question_id> --type comparison
    python generate_infographic.py --id <question_id> --regenerate
    python generate_infographic.py --id <question_id> --prompt "custom instructions"

Options:
    --id            Question ID from Supabase (required)
    --type          Infographic type: pearl, comparison, concept (default: pearl)
    --regenerate    Generate new image with same prompt
    --prompt        Custom prompt override
    --style         Style preset: minimal, detailed, visual (default: minimal)
    --preview       Show preview before saving (default: True)
    --save          Save directly without preview
    --specialty     Override specialty folder
"""

import os
import sys
import argparse
import subprocess
import platform
from pathlib import Path
from datetime import datetime
import shutil

import google.generativeai as genai
from PIL import Image

from config import get_supabase_client, load_env
from overlay_logo import add_logo
from utils import ensure_dir, sanitize_filename, get_prompts_dir, get_assets_dir, get_output_dir

# Load environment variables
load_env()

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

PROMPTS_DIR = get_prompts_dir()
ASSETS_DIR = get_assets_dir()
OUTPUT_DIR = get_output_dir() / "infographics"
TEMP_DIR = get_output_dir() / "temp"

LOGO_PATH = ASSETS_DIR / "logo.png"


def fetch_question(question_id: str) -> dict:
    """Fetch question data from Supabase."""
    supabase = get_supabase_client()

    response = (
        supabase.table("questions")
        .select("*")
        .eq("id", question_id)
        .single()
        .execute()
    )

    if not response.data:
        raise ValueError(f"Question not found: {question_id}")

    return response.data


def load_prompt_template(prompt_type: str, style: str = "minimal") -> str:
    """Load and combine prompt templates."""

    # Base prompt for infographic type
    base_prompt_path = PROMPTS_DIR / f"{prompt_type}-prompt.txt"

    if base_prompt_path.exists():
        with open(base_prompt_path, "r") as f:
            base_prompt = f.read()
    else:
        base_prompt = get_default_prompt(prompt_type)

    # Style modifier
    style_path = PROMPTS_DIR / "styles" / f"{style}.txt"

    if style_path.exists():
        with open(style_path, "r") as f:
            style_prompt = f.read()
    else:
        style_prompt = ""

    return f"{base_prompt}\n\n{style_prompt}".strip()


def get_default_prompt(prompt_type: str) -> str:
    """Return default prompts if template files don't exist."""

    prompts = {
        "pearl": """Create an educational medical infographic about the following clinical concept.

The infographic should:
- Be visually clean and professional
- Use a modern, minimal design aesthetic
- Have clear hierarchy of information
- Include relevant icons or simple illustrations
- Be optimized for social media (square format, 1080x1080)
- Use a white or light background
- Have excellent text legibility
- NOT include any watermarks or attribution text

Topic: {topic}
Key Concept: {key_concept}

Style: Clean medical education infographic suitable for resident physicians.""",

        "comparison": """Create a side-by-side comparison infographic for medical education.

The infographic should:
- Clearly compare two conditions/treatments/concepts
- Use a split layout (left vs right)
- Include key differentiating features
- Be visually balanced
- Use color coding to distinguish the two sides
- Be optimized for social media (square format, 1080x1080)
- NOT include any watermarks or attribution text

Comparison: {topic_a} vs {topic_b}
Key Differences: {key_points}

Style: Clean, professional medical education comparison chart.""",

        "concept": """Create an educational infographic explaining this medical concept.

The infographic should:
- Break down the concept into digestible parts
- Use visual elements to aid understanding
- Include a clear flow or structure
- Be suitable for medical trainees
- Use professional, clean design
- Be optimized for social media (square format, 1080x1080)
- NOT include any watermarks or attribution text

Concept: {topic}
Details: {explanation}

Style: Educational, clear, professional medical infographic."""
    }

    return prompts.get(prompt_type, prompts["pearl"])


def build_prompt(template: str, question: dict, custom_prompt: str = None) -> str:
    """Build final prompt from template and question data."""

    if custom_prompt:
        return custom_prompt

    # Replace placeholders with question data
    prompt = template.format(
        topic=question.get("topic", question.get("category", "")),
        key_concept=question.get("key_concept", question.get("explanation", "")),
        explanation=question.get("explanation", ""),
        category=question.get("category", ""),
        topic_a=question.get("topic_a", ""),
        topic_b=question.get("topic_b", ""),
        key_points=question.get("key_points", ""),
    )

    return prompt


def generate_with_gemini(prompt: str) -> bytes:
    """Call Gemini API to generate image."""

    if not GOOGLE_API_KEY:
        raise ValueError("Missing GOOGLE_API_KEY in environment")

    model = genai.GenerativeModel('gemini-2.0-flash-exp')

    response = model.generate_content(
        prompt,
        generation_config=genai.GenerationConfig(
            response_mime_type="image/png"
        )
    )

    # Extract image data from response
    if response.parts:
        for part in response.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                return part.inline_data.data

    raise Exception("No image generated by Gemini")


def save_temp_image(image_data: bytes, question_id: str) -> Path:
    """Save image to temp directory."""
    ensure_dir(TEMP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_path = TEMP_DIR / f"{question_id}_{timestamp}.png"

    with open(temp_path, "wb") as f:
        f.write(image_data)

    return temp_path


def open_preview(image_path: Path):
    """Open image in default viewer."""
    system = platform.system()

    if system == "Darwin":  # macOS
        subprocess.run(["open", str(image_path)])
    elif system == "Windows":
        os.startfile(str(image_path))
    else:  # Linux
        subprocess.run(["xdg-open", str(image_path)])


def prompt_user_approval() -> bool:
    """Ask user if they want to save the image."""
    while True:
        response = input("\n💾 Save this image? [y/n/r(egenerate)]: ").lower().strip()

        if response in ["y", "yes"]:
            return True
        elif response in ["n", "no"]:
            return False
        elif response in ["r", "regenerate"]:
            return None  # Signal to regenerate
        else:
            print("Please enter 'y' to save, 'n' to discard, or 'r' to regenerate")


def move_to_output(temp_path: Path, question_id: str, specialty: str, infographic_type: str) -> Path:
    """Move approved image to output directory."""

    specialty_slug = sanitize_filename(specialty.lower())
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{question_id}-{infographic_type}-{timestamp}.png"

    output_path = OUTPUT_DIR / specialty_slug / filename
    ensure_dir(output_path.parent)

    shutil.move(str(temp_path), str(output_path))

    return output_path


def generate_infographic(
    question_id: str,
    infographic_type: str = "pearl",
    style: str = "minimal",
    custom_prompt: str = None,
    preview: bool = True,
    specialty_override: str = None
) -> Path:
    """Generate an infographic with optional preview and iteration."""

    # Fetch question
    print(f"📥 Fetching question: {question_id}")
    question = fetch_question(question_id)

    specialty = specialty_override or question.get("specialty", "general")

    while True:
        # Build prompt
        print(f"📝 Building prompt ({infographic_type}, {style})...")
        template = load_prompt_template(infographic_type, style)
        prompt = build_prompt(template, question, custom_prompt)

        # Generate image
        print(f"🎨 Generating infographic with Gemini...")
        image_data = generate_with_gemini(prompt)

        # Save to temp
        temp_path = save_temp_image(image_data, question_id)
        print(f"📁 Temp saved: {temp_path}")

        # Add logo overlay if logo exists
        if LOGO_PATH.exists():
            print(f"🏷️  Adding logo overlay...")
            add_logo(str(temp_path), str(LOGO_PATH))
        else:
            print(f"⚠️  Logo not found at {LOGO_PATH}, skipping overlay")

        if not preview:
            # Skip preview, save directly
            output_path = move_to_output(temp_path, question_id, specialty, infographic_type)
            print(f"✅ Saved: {output_path}")
            return output_path

        # Show preview
        print(f"👁️  Opening preview...")
        open_preview(temp_path)

        # Get user approval
        approval = prompt_user_approval()

        if approval is True:
            output_path = move_to_output(temp_path, question_id, specialty, infographic_type)
            print(f"✅ Saved: {output_path}")
            return output_path

        elif approval is False:
            temp_path.unlink()  # Delete temp file
            print("🗑️  Discarded")
            return None

        else:  # Regenerate
            temp_path.unlink()
            print("🔄 Regenerating...")
            continue


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI infographics from question data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_infographic.py --id abc-123 --type pearl
    python generate_infographic.py --id abc-123 --type comparison
    python generate_infographic.py --id abc-123 --style detailed
    python generate_infographic.py --id abc-123 --prompt "Create an infographic about..."
    python generate_infographic.py --id abc-123 --save  # Skip preview
        """
    )

    parser.add_argument(
        "--id",
        required=True,
        help="Question ID from Supabase"
    )
    parser.add_argument(
        "--type",
        choices=["pearl", "comparison", "concept"],
        default="pearl",
        help="Infographic type (default: pearl)"
    )
    parser.add_argument(
        "--style",
        choices=["minimal", "detailed", "visual"],
        default="minimal",
        help="Style preset (default: minimal)"
    )
    parser.add_argument(
        "--prompt",
        help="Custom prompt override"
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Generate new image with same settings"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        default=True,
        help="Show preview before saving (default)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save directly without preview"
    )
    parser.add_argument(
        "--specialty",
        help="Override specialty folder"
    )

    args = parser.parse_args()

    try:
        generate_infographic(
            question_id=args.id,
            infographic_type=args.type,
            style=args.style,
            custom_prompt=args.prompt,
            preview=not args.save,
            specialty_override=args.specialty
        )

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
