#!/usr/bin/env python3
"""
Pipeline 1: Question/Answer Card Generator
Uses Playwright for local HTML→PNG conversion (free, no API costs).

TWO MODES:
  1. Design Mode: Iterate on templates with sample/preview data
  2. Production Mode: Generate cards from Supabase question bank

Design Mode Usage:
    python generate_card.py --preview question-card
    python generate_card.py --preview answer-card
    python generate_card.py --preview question-card --html templates/question-card.html

Production Mode Usage:
    python generate_card.py --id <question_id> --type question
    python generate_card.py --id <question_id> --type answer
    python generate_card.py --id <question_id> --type carousel

Options:
    --preview       Template name to preview (design iteration mode)
    --html          Path to HTML file (for design mode, overrides template)
    --id            Question ID from Supabase (production mode)
    --type          Card type: question, answer, or carousel (default: carousel)
    --specialty     Override specialty folder (optional)
    --output        Custom output path (optional)
"""

import os
import sys
import argparse
import asyncio
from pathlib import Path
from datetime import datetime

from playwright.async_api import async_playwright

from config import get_supabase_client, load_env
from utils import ensure_dir, sanitize_filename, get_templates_dir, get_output_dir

# Load environment variables
load_env()

# Configuration
TEMPLATES_DIR = get_templates_dir()
OUTPUT_DIR = get_output_dir() / "cards"
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1080


# =============================================================================
# SAMPLE DATA FOR DESIGN ITERATION
# =============================================================================

SAMPLE_QUESTION_DATA = {
    "category": "Ophthalmology - Glaucoma",
    "question_stem": "A 45-year-old woman presents with acute eye pain, blurred vision, and halos around lights. Examination reveals a mid-dilated pupil and corneal edema. Intraocular pressure is 54 mmHg. What is the most appropriate initial management?",
    "option_a": "Topical pilocarpine 2% and oral acetazolamide",
    "option_b": "Laser peripheral iridotomy",
    "option_c": "Trabeculectomy",
    "option_d": "Observation and reassurance",
}

SAMPLE_ANSWER_DATA = {
    "category": "Ophthalmology - Glaucoma",
    "question_stem": "A 45-year-old woman presents with acute eye pain, blurred vision, and halos around lights. Examination reveals a mid-dilated pupil and corneal edema. Intraocular pressure is 54 mmHg. What is the most appropriate initial management?",
    "option_a": "Topical pilocarpine 2% and oral acetazolamide",
    "option_b": "Laser peripheral iridotomy",
    "option_c": "Trabeculectomy",
    "option_d": "Observation and reassurance",
    "class_a": "correct",
    "class_b": "",
    "class_c": "",
    "class_d": "",
    "meta_category": "Glaucoma",
    "topic": "Acute Angle Closure",
    "correct_answer": "A",
    "explanation": "Acute angle-closure glaucoma requires immediate IOP reduction with medical therapy (topical pilocarpine to constrict the pupil and oral/IV acetazolamide to reduce aqueous production) before definitive laser peripheral iridotomy.",
    "key_concept": "Initial management of acute angle closure focuses on medical IOP reduction before laser intervention. Pilocarpine constricts the pupil, pulling the iris away from the trabecular meshwork.",
}


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

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


def load_template(template_name: str) -> str:
    """Load HTML template from file."""
    template_path = TEMPLATES_DIR / f"{template_name}.html"

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def load_html_file(html_path: str) -> str:
    """Load HTML from arbitrary file path."""
    path = Path(html_path)

    if not path.exists():
        raise FileNotFoundError(f"HTML file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def inject_data(template: str, data: dict) -> str:
    """Replace {{placeholders}} with actual data."""
    html = template

    for key, value in data.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value) if value else "")

    return html


async def html_to_png(html: str, output_path: Path) -> Path:
    """Convert HTML to PNG using Playwright (local, free)."""
    ensure_dir(output_path.parent)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": IMAGE_WIDTH, "height": IMAGE_HEIGHT}
        )

        # Load HTML content
        await page.set_content(html, wait_until="networkidle")

        # Screenshot the page
        await page.screenshot(path=str(output_path), type="png")

        await browser.close()

    return output_path


def html_to_png_sync(html: str, output_path: Path) -> Path:
    """Synchronous wrapper for html_to_png."""
    return asyncio.run(html_to_png(html, output_path))


# =============================================================================
# DATA PREPARATION
# =============================================================================

def prepare_question_data(question: dict) -> dict:
    """Prepare data for question card template."""
    specialty = question.get("specialty", "Medicine")
    category = question.get("category", "")

    return {
        "category": f"{specialty} - {category}" if category else specialty,
        "question_stem": question.get("question_stem", ""),
        "option_a": question.get("option_a", ""),
        "option_b": question.get("option_b", ""),
        "option_c": question.get("option_c", ""),
        "option_d": question.get("option_d", ""),
    }


def prepare_answer_data(question: dict) -> dict:
    """Prepare data for answer card template."""
    correct = question.get("correct_answer", "A").upper()
    specialty = question.get("specialty", "Medicine")
    category = question.get("category", "")

    return {
        "category": f"{specialty} - {category}" if category else specialty,
        "question_stem": question.get("question_stem", ""),
        "option_a": question.get("option_a", ""),
        "option_b": question.get("option_b", ""),
        "option_c": question.get("option_c", ""),
        "option_d": question.get("option_d", ""),
        "class_a": "correct" if correct == "A" else "",
        "class_b": "correct" if correct == "B" else "",
        "class_c": "correct" if correct == "C" else "",
        "class_d": "correct" if correct == "D" else "",
        "meta_category": category,
        "topic": question.get("topic", ""),
        "correct_answer": correct,
        "explanation": question.get("explanation", ""),
        "key_concept": question.get("key_concept", ""),
    }


# =============================================================================
# DESIGN MODE (Template Iteration)
# =============================================================================

def preview_template(template_name: str, html_path: str = None, output_name: str = None) -> Path:
    """
    Generate a preview image from template with sample data.
    Used for design iteration before finalizing templates.
    """
    print(f"🎨 DESIGN MODE: Previewing template")

    # Load HTML
    if html_path:
        print(f"📄 Loading HTML from: {html_path}")
        html = load_html_file(html_path)
    else:
        print(f"📄 Loading template: {template_name}")
        html = load_template(template_name)

    # Determine which sample data to use
    if "answer" in template_name.lower():
        data = SAMPLE_ANSWER_DATA
        print(f"📝 Using sample ANSWER data")
    else:
        data = SAMPLE_QUESTION_DATA
        print(f"📝 Using sample QUESTION data")

    # Inject sample data
    html = inject_data(html, data)

    # Generate image with Playwright
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_name or f"preview-{template_name}-{timestamp}.png"
    output_path = OUTPUT_DIR / "previews" / filename

    print(f"🖼️  Rendering with Playwright...")
    html_to_png_sync(html, output_path)
    print(f"✅ Preview saved: {output_path}")

    return output_path


# =============================================================================
# PRODUCTION MODE (Question Bank Injection)
# =============================================================================

def generate_card(question_id: str, card_type: str, specialty_override: str = None) -> Path:
    """Generate a single card image from Supabase question data."""

    # Fetch question
    print(f"📥 Fetching question: {question_id}")
    question = fetch_question(question_id)

    # Determine specialty folder
    specialty = specialty_override or question.get("specialty", "general")
    specialty_slug = sanitize_filename(specialty.lower())

    # Load template and prepare data
    if card_type == "question":
        template = load_template("question-card")
        data = prepare_question_data(question)
        subfolder = "questions"
    else:  # answer
        template = load_template("answer-card")
        data = prepare_answer_data(question)
        subfolder = "answers"

    # Inject data into template
    print(f"🔧 Preparing {card_type} card...")
    html = inject_data(template, data)

    # Generate image with Playwright
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{question_id}-{card_type}-{timestamp}.png"
    output_path = OUTPUT_DIR / specialty_slug / subfolder / filename

    print(f"🖼️  Rendering with Playwright...")
    html_to_png_sync(html, output_path)
    print(f"✅ Saved: {output_path}")

    return output_path


def generate_carousel(question_id: str, specialty_override: str = None) -> tuple:
    """Generate both question and answer cards."""
    question_path = generate_card(question_id, "question", specialty_override)
    answer_path = generate_card(question_id, "answer", specialty_override)

    print(f"\n🎠 Carousel complete!")
    print(f"   Question: {question_path}")
    print(f"   Answer:   {answer_path}")

    return question_path, answer_path


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Generate question/answer cards from templates (Playwright)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
DESIGN MODE (iterate on templates):
    python generate_card.py --preview question-card
    python generate_card.py --preview answer-card
    python generate_card.py --preview question-card --html path/to/custom.html

PRODUCTION MODE (generate from question bank):
    python generate_card.py --id abc-123 --type question
    python generate_card.py --id abc-123 --type answer
    python generate_card.py --id abc-123 --type carousel
    python generate_card.py --id abc-123 --type carousel --specialty cardiology
        """
    )

    # Design mode arguments
    parser.add_argument(
        "--preview",
        metavar="TEMPLATE",
        help="Preview template with sample data (design mode)"
    )
    parser.add_argument(
        "--html",
        metavar="PATH",
        help="Path to HTML file (for design mode)"
    )

    # Production mode arguments
    parser.add_argument(
        "--id",
        help="Question ID from Supabase (production mode)"
    )
    parser.add_argument(
        "--type",
        choices=["question", "answer", "carousel"],
        default="carousel",
        help="Card type to generate (default: carousel)"
    )
    parser.add_argument(
        "--specialty",
        help="Override specialty folder"
    )
    parser.add_argument(
        "--output",
        help="Custom output filename"
    )

    args = parser.parse_args()

    try:
        # DESIGN MODE
        if args.preview:
            preview_template(
                template_name=args.preview,
                html_path=args.html,
                output_name=args.output
            )

        # PRODUCTION MODE
        elif args.id:
            if args.type == "carousel":
                generate_carousel(args.id, args.specialty)
            else:
                generate_card(args.id, args.type, args.specialty)

        else:
            parser.print_help()
            print("\n❌ Error: Must specify either --preview (design) or --id (production)")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
