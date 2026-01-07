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
from utils import ensure_dir, sanitize_filename, get_templates_dir, get_output_dir, process_card_data

# Load environment variables
load_env()

# Configuration
TEMPLATES_DIR = get_templates_dir()
OUTPUT_BASE_DIR = Path("/Users/mk/Documents/Subspecialty Questions-Answers")
IMAGE_WIDTH = 1080
IMAGE_HEIGHT = 1350  # 4:5 portrait ratio - optimal for Instagram, works well on Twitter/X
DEVICE_SCALE_FACTOR = 2  # 2x resolution (outputs 2160x2700 images)


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
    "difficulty": "medium",
    "difficulty_label": "●● Intermediate",
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
    "difficulty": "medium",
    "difficulty_label": "●● Intermediate",
}


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def fetch_question(question_id: str) -> dict:
    """Fetch question data from Supabase with specialty/subspecialty names."""
    supabase = get_supabase_client()

    # Fetch question with related specialty and subspecialty
    response = (
        supabase.table("questions")
        .select("*, medical_specialties(id, name, code), subspecialties(id, name, code)")
        .eq("id", question_id)
        .single()
        .execute()
    )

    if not response.data:
        raise ValueError(f"Question not found: {question_id}")

    question = response.data

    # Extract specialty and subspecialty names
    specialty_data = question.get("medical_specialties", {})
    subspecialty_data = question.get("subspecialties", {})

    question["specialty_name"] = specialty_data.get("name", "Medicine") if specialty_data else "Medicine"
    question["subspecialty_name"] = subspecialty_data.get("name", "") if subspecialty_data else ""

    return question


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
    """Convert HTML to PNG using Playwright (local, free) at 2x resolution."""
    ensure_dir(output_path.parent)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={"width": IMAGE_WIDTH, "height": IMAGE_HEIGHT},
            device_scale_factor=DEVICE_SCALE_FACTOR  # 2x for high-res output
        )

        # Load HTML content
        await page.set_content(html, wait_until="networkidle")

        # Screenshot the page (outputs at 2160x2160 with scale factor 2)
        await page.screenshot(path=str(output_path), type="png")

        await browser.close()

    return output_path


def html_to_png_sync(html: str, output_path: Path) -> Path:
    """Synchronous wrapper for html_to_png."""
    return asyncio.run(html_to_png(html, output_path))


# =============================================================================
# DATA PREPARATION
# =============================================================================

# Difficulty labels mapping
DIFFICULTY_LABELS = {
    "easy": "● Basic",
    "medium": "●● Intermediate",
    "hard": "●●● Advanced",
}


def prepare_question_data(question: dict) -> dict:
    """Prepare data for question card template."""
    specialty_name = question.get("specialty_name", "Medicine")
    subspecialty_name = question.get("subspecialty_name", "")

    # Format: "Specialty - Subspecialty" (e.g., "Ophthalmology - Glaucoma")
    if subspecialty_name:
        category = f"{specialty_name} - {subspecialty_name}"
    else:
        category = specialty_name

    # Get difficulty
    difficulty = question.get("difficulty", "medium")
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "●● Intermediate")

    return {
        "category": category,
        "question_stem": question.get("question_stem", ""),
        "option_a": question.get("option_a", ""),
        "option_b": question.get("option_b", ""),
        "option_c": question.get("option_c", ""),
        "option_d": question.get("option_d", ""),
        "difficulty": difficulty,
        "difficulty_label": difficulty_label,
    }


def prepare_answer_data(question: dict) -> dict:
    """Prepare data for answer card template."""
    correct = question.get("correct_answer", "A").upper()
    specialty_name = question.get("specialty_name", "Medicine")
    subspecialty_name = question.get("subspecialty_name", "")

    # Format: "Specialty - Subspecialty" (e.g., "Ophthalmology - Glaucoma")
    if subspecialty_name:
        category = f"{specialty_name} - {subspecialty_name}"
    else:
        category = specialty_name

    # Get difficulty
    difficulty = question.get("difficulty", "medium")
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "●● Intermediate")

    return {
        "category": category,
        "question_stem": question.get("question_stem", ""),
        "option_a": question.get("option_a", ""),
        "option_b": question.get("option_b", ""),
        "option_c": question.get("option_c", ""),
        "option_d": question.get("option_d", ""),
        "class_a": "correct" if correct == "A" else "",
        "class_b": "correct" if correct == "B" else "",
        "class_c": "correct" if correct == "C" else "",
        "class_d": "correct" if correct == "D" else "",
        "meta_category": subspecialty_name or specialty_name,
        "topic": question.get("concept_name", "") or question.get("topic", ""),
        "correct_answer": correct,
        "explanation": question.get("explanation", ""),
        "key_concept": question.get("key_concept", ""),
        "difficulty": difficulty,
        "difficulty_label": difficulty_label,
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

    # Determine which sample data to use and card type
    if "answer" in template_name.lower():
        data = SAMPLE_ANSWER_DATA.copy()
        card_type = "answer"
        print(f"📝 Using sample ANSWER data")
    else:
        data = SAMPLE_QUESTION_DATA.copy()
        card_type = "question"
        print(f"📝 Using sample QUESTION data")

    # Process data through smart truncation (uses LLM if text exceeds limits)
    print(f"📏 Checking text lengths and summarizing if needed...")
    data = process_card_data(data, card_type)

    # Inject sample data
    html = inject_data(html, data)

    # Generate image with Playwright
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_name or f"preview-{template_name}-{timestamp}.png"
    output_path = get_output_dir() / "previews" / filename

    print(f"🖼️  Rendering with Playwright...")
    html_to_png_sync(html, output_path)
    print(f"✅ Preview saved: {output_path}")

    return output_path


# =============================================================================
# PRODUCTION MODE (Question Bank Injection)
# =============================================================================

def generate_carousel(question_id: str) -> tuple:
    """
    Generate both question and answer cards in a single folder.

    Output: /Users/mk/Documents/Subspecialty Questions/Answers/{topic}_{date}/
            - question.png
            - answer.png
    """
    # Fetch question with specialty/subspecialty data
    print(f"📥 Fetching question: {question_id}")
    question = fetch_question(question_id)

    # Get topic name for folder
    subspecialty_name = question.get("subspecialty_name", "")
    topic = question.get("topic", subspecialty_name) or "General"
    topic_slug = sanitize_filename(topic)

    # Create output folder: {topic}_{date}
    timestamp = datetime.now().strftime("%Y%m%d")
    folder_name = f"{topic_slug}_{timestamp}"
    output_folder = OUTPUT_BASE_DIR / folder_name
    ensure_dir(output_folder)

    print(f"📁 Output folder: {output_folder}")

    # Prepare data for both cards
    question_data = prepare_question_data(question)
    answer_data = prepare_answer_data(question)

    # Process through smart truncation (GPT-4o if text exceeds limits)
    print(f"📏 Checking text lengths and summarizing if needed...")
    question_data = process_card_data(question_data, "question")
    answer_data = process_card_data(answer_data, "answer")

    # Load templates
    question_template = load_template("question-card")
    answer_template = load_template("answer-card")

    # Generate Question Card
    print(f"🔧 Generating question card...")
    question_html = inject_data(question_template, question_data)
    question_path = output_folder / "question.png"
    html_to_png_sync(question_html, question_path)
    print(f"✅ Saved: {question_path}")

    # Generate Answer Card
    print(f"🔧 Generating answer card...")
    answer_html = inject_data(answer_template, answer_data)
    answer_path = output_folder / "answer.png"
    html_to_png_sync(answer_html, answer_path)
    print(f"✅ Saved: {answer_path}")

    # Generate caption and print to terminal for easy copy
    caption = generate_caption(question)
    print("")
    print("=" * 50)
    print("📋 COPY THIS CAPTION:")
    print("=" * 50)
    print(caption)
    print("=" * 50)

    return question_path, answer_path


def generate_caption(question: dict) -> str:
    """Generate ready-to-post social media caption."""
    subspecialty = question.get("subspecialty_name", "Medicine")
    specialty = question.get("specialty_name", "Medicine")

    # Use first word of subspecialty for cleaner title (e.g., "Retina" instead of "Retina and Vitreous")
    subspecialty_short = subspecialty.split()[0] if subspecialty else "Medical"

    # Hashtag from specialty (remove spaces)
    hashtag = f"#{specialty.replace(' ', '')}"

    return f"""📚 {subspecialty_short} Question of the Day

Can you get it right?
Swipe to see the answer! 👉

Drop your answer in the comments before checking! ⬇️

🔔 Follow @SubspecialtyHQ for daily board-style questions!
🔗 subspecialty.com

{hashtag}"""


def generate_card(question_id: str, card_type: str) -> Path:
    """Generate a single card (for backwards compatibility)."""
    question_path, answer_path = generate_carousel(question_id)
    return question_path if card_type == "question" else answer_path


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
