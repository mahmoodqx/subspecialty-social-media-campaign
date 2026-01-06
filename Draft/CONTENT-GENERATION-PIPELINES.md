# Subspecialty Content Generation Pipelines
## Complete System Documentation

---

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Folder Structure](#folder-structure)
4. [Environment Setup](#environment-setup)
5. [Pipeline 1: Question/Answer Cards (Playwright - Local)](#pipeline-1-questionanswer-cards-playwright---local)
6. [Pipeline 2: Infographics/Pearls (Gemini AI)](#pipeline-2-infographicspearls-gemini-ai)
7. [Pipeline 3: Auto-Posting (Twitter/Instagram API)](#pipeline-3-auto-posting-twitterinstagram-api)
8. [Shared Utilities](#shared-utilities)
9. [Terminal Commands Reference](#terminal-commands-reference)
10. [API Reference](#api-reference)
11. [Troubleshooting](#troubleshooting)

---

## Overview

This system provides two content generation pipelines for creating social media images from your medical education question bank, plus an optional auto-posting pipeline:

| Pipeline | Tool | Use Case | Cost |
|----------|------|----------|------|
| **Pipeline 1** | Playwright (Local) | Question/Answer Cards | Free |
| **Pipeline 2** | Gemini AI | Infographics/Pearls | Free tier / ~$0.04/image |
| **Pipeline 3** | Twitter/Instagram API | Auto-posting | Free |

**Target Output:** 1080x1080 PNG images optimized for Instagram, Twitter, and LinkedIn.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SUBSPECIALTY CONTENT GENERATION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌─────────────────┐                                                        │
│   │   YOU (Terminal)│                                                        │
│   └────────┬────────┘                                                        │
│            │                                                                 │
│            │  python generate_card.py --id abc-123 --type carousel           │
│            │  python generate_infographic.py --id abc-123 --type pearl       │
│            │  python post_content.py --image output/card.png --platform twitter│
│            │                                                                 │
│            ▼                                                                 │
│   ┌─────────────────┐         ┌─────────────────┐                           │
│   │    SUPABASE     │◀────────│   config.py     │                           │
│   │  Question Bank  │         │   (credentials) │                           │
│   └────────┬────────┘         └─────────────────┘                           │
│            │                                                                 │
│            │  Fetch question data                                            │
│            ▼                                                                 │
│   ┌────────────────────────────────────────────────────────┐                │
│   │                    ROUTE BY TYPE                        │                │
│   └───────────────────────┬────────────────────────────────┘                │
│                           │                                                  │
│          ┌────────────────┴────────────────┐                                │
│          ▼                                 ▼                                │
│   ┌──────────────┐                  ┌──────────────┐                        │
│   │  PIPELINE 1  │                  │  PIPELINE 2  │                        │
│   │  Cards       │                  │  Infographics│                        │
│   └──────┬───────┘                  └──────┬───────┘                        │
│          │                                 │                                 │
│          ▼                                 ▼                                 │
│   ┌──────────────┐                  ┌──────────────┐                        │
│   │ Load HTML    │                  │ Generate     │                        │
│   │ Template     │                  │ Prompt       │                        │
│   └──────┬───────┘                  └──────┬───────┘                        │
│          │                                 │                                 │
│          ▼                                 ▼                                 │
│   ┌──────────────┐                  ┌──────────────┐                        │
│   │ Inject Data  │                  │ Call Gemini  │                        │
│   │ {{vars}}     │                  │ API          │                        │
│   └──────┬───────┘                  └──────┬───────┘                        │
│          │                                 │                                 │
│          ▼                                 ▼                                 │
│   ┌──────────────┐                  ┌──────────────┐                        │
│   │ Playwright   │                  │ Overlay Logo │                        │
│   │ Screenshot   │                  │ (Python PIL) │                        │
│   │ (Local,Free) │                  └──────┬───────┘                        │
│   └──────┬───────┘                         │                                │
│          │                                 │                                 │
│          ▼                                 ▼                                 │
│   ┌──────────────┐                  ┌──────────────┐                        │
│   │ Save to      │                  │ Preview &    │                        │
│   │ output/cards │                  │ Save         │                        │
│   └──────┬───────┘                  └──────┬───────┘                        │
│          │                                 │                                 │
│          └────────────────┬────────────────┘                                │
│                           ▼                                                  │
│                  ┌────────────────┐                                         │
│                  │  PIPELINE 3    │                                         │
│                  │  Auto-Post     │                                         │
│                  └───────┬────────┘                                         │
│                          │                                                   │
│            ┌─────────────┴─────────────┐                                    │
│            ▼                           ▼                                    │
│     ┌────────────┐              ┌────────────┐                              │
│     │ Twitter    │              │ Instagram  │                              │
│     │ API v2     │              │ Graph API  │                              │
│     └────────────┘              └────────────┘                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Folder Structure

```
/subspecialty-content/
│
├── templates/                      # HTML templates for card generation
│   ├── question-card.html          # Question card template
│   ├── answer-card.html            # Answer reveal template
│   ├── pearl-card.html             # (Future) High-yield fact template
│   └── comparison-card.html        # (Future) A vs B template
│
├── prompts/                        # Gemini prompt templates
│   ├── infographic-base.txt        # Base infographic prompt
│   ├── pearl-prompt.txt            # Clinical pearl prompt
│   ├── comparison-prompt.txt       # A vs B comparison prompt
│   └── styles/                     # Style presets
│       ├── minimal.txt
│       ├── detailed.txt
│       └── visual.txt
│
├── assets/                         # Static assets
│   ├── logo.png                    # Logo for overlay (transparent PNG)
│   ├── logo.svg                    # Logo source file
│   └── fonts/                      # Custom fonts (if needed)
│
├── output/                         # Generated content (gitignored)
│   ├── cards/                      # HTMLCSSToImage output
│   │   ├── ophthalmology/
│   │   │   ├── questions/
│   │   │   └── answers/
│   │   ├── cardiology/
│   │   └── neurology/
│   │
│   ├── infographics/               # Gemini output
│   │   ├── ophthalmology/
│   │   ├── cardiology/
│   │   └── neurology/
│   │
│   └── temp/                       # Temporary preview files
│
├── scripts/                        # Python scripts
│   ├── generate_card.py            # Pipeline 1: Playwright (local)
│   ├── generate_infographic.py     # Pipeline 2: Gemini AI
│   ├── post_content.py             # Pipeline 3: Auto-posting
│   ├── overlay_logo.py             # Shared logo utility
│   ├── config.py                   # Configuration and DB connection
│   └── utils.py                    # Helper functions
│
├── .env                            # Environment variables (gitignored)
├── .env.example                    # Example environment file
├── requirements.txt                # Python dependencies
└── README.md                       # Quick start guide
```

---

## Environment Setup

### 1. Create `.env` file

```bash
# ===========================================
# SUBSPECIALTY CONTENT GENERATOR
# Environment Configuration
# ===========================================

# Supabase (Question Database)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# Google Gemini (Infographic Generation)
GEMINI_API_KEY=your-gemini-api-key

# Twitter API v2 (Auto-posting)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_SECRET=your-access-secret

# Instagram Graph API (Auto-posting) - Optional
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ID=your-business-account-id

# Optional: Default settings
DEFAULT_SPECIALTY=ophthalmology
OUTPUT_FORMAT=png
IMAGE_SIZE=1080
```

### 2. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 3. `requirements.txt`

```
supabase>=2.0.0
python-dotenv>=1.0.0
requests>=2.31.0
Pillow>=10.0.0
google-generativeai>=0.3.0
playwright>=1.40.0
tweepy>=4.14.0
```

### 4. Install Playwright Browser

```bash
# After pip install, run this once:
playwright install chromium
```

---

## Pipeline 1: Question/Answer Cards (Playwright - Local)

### Overview

Template-based generation using local browser screenshot. **Free, no API costs.**

```
You run script with question_id
        ↓
Fetch question from Supabase
        ↓
Inject data into HTML template
        ↓
Save temp HTML file
        ↓
Playwright screenshots HTML → PNG (local, free)
        ↓
Save to output folder
        ↓
Done ✓
```

### Script: `generate_card.py`

```python
#!/usr/bin/env python3
"""
Pipeline 1: Question/Answer Card Generator
Uses Playwright for local HTML → PNG conversion (free, no API).

Usage:
    python generate_card.py --id <question_id> --type question
    python generate_card.py --id <question_id> --type answer
    python generate_card.py --id <question_id> --type carousel
    python generate_card.py --id <question_id> --type carousel --post
    
Options:
    --id          Question ID from Supabase (required)
    --type        Card type: question, answer, or carousel (default: carousel)
    --specialty   Override specialty folder (optional)
    --post        Auto-post to Twitter after generation (optional)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

from playwright.sync_api import sync_playwright

from config import get_supabase_client, load_env
from utils import ensure_dir, sanitize_filename

# Load environment variables
load_env()

# Configuration
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "cards"
TEMP_DIR = Path(__file__).parent.parent / "output" / "temp"


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


def inject_data(template: str, data: dict) -> str:
    """Replace {{placeholders}} with actual data."""
    html = template
    
    for key, value in data.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value) if value else "")
    
    return html


def html_to_png(html_content: str, output_path: Path) -> Path:
    """
    Convert HTML to PNG using Playwright (local, free).
    Screenshots the HTML at exact 1080x1080 dimensions.
    """
    ensure_dir(TEMP_DIR)
    ensure_dir(output_path.parent)
    
    # Save HTML to temp file
    temp_html = TEMP_DIR / f"temp_{datetime.now().strftime('%H%M%S')}.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    # Screenshot with Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.goto(f"file://{temp_html.absolute()}")
        
        # Wait for fonts to load
        page.wait_for_timeout(500)
        
        # Screenshot
        page.screenshot(path=str(output_path), type="png")
        browser.close()
    
    # Cleanup temp file
    temp_html.unlink()
    
    return output_path


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


def generate_card(question_id: str, card_type: str, specialty_override: str = None) -> Path:
    """Generate a single card image."""
    
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
    
    # Generate image locally with Playwright
    print(f"🎨 Generating image (Playwright)...")
    timestamp = datetime.now().strftime("%Y%m%d")
    filename = f"{question_id}-{card_type}-{timestamp}.png"
    output_path = OUTPUT_DIR / specialty_slug / subfolder / filename
    
    html_to_png(html, output_path)
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


def main():
    parser = argparse.ArgumentParser(
        description="Generate question/answer cards from templates (local, free)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python generate_card.py --id abc-123 --type question
    python generate_card.py --id abc-123 --type answer
    python generate_card.py --id abc-123 --type carousel
    python generate_card.py --id abc-123 --type carousel --specialty cardiology
    python generate_card.py --id abc-123 --type carousel --post
        """
    )
    
    parser.add_argument(
        "--id", 
        required=True, 
        help="Question ID from Supabase"
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
        "--post",
        action="store_true",
        help="Auto-post to Twitter after generation"
    )
    
    args = parser.parse_args()
    
    try:
        if args.type == "carousel":
            question_path, answer_path = generate_carousel(args.id, args.specialty)
            paths = [question_path, answer_path]
        else:
            path = generate_card(args.id, args.type, args.specialty)
            paths = [path]
        
        # Optional: Auto-post
        if args.post:
            from post_content import post_to_twitter
            for p in paths:
                post_to_twitter(str(p))
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---

## Pipeline 2: Infographics/Pearls (Gemini AI)

### Overview

AI-generated infographics with iterative review process.

```
You run script with question_id
        ↓
Fetch question from Supabase
        ↓
Generate prompt (from template + question data)
        ↓
Call Gemini API → get image
        ↓
Python overlays your logo
        ↓
Save to temp → Preview opens
        ↓
Happy? → Move to output/infographics/
Unhappy? → Re-run with --regenerate or --prompt
```

### Script: `generate_infographic.py`

```python
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
from utils import ensure_dir, sanitize_filename

# Load environment variables
load_env()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
ASSETS_DIR = Path(__file__).parent.parent / "assets"
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "infographics"
TEMP_DIR = Path(__file__).parent.parent / "output" / "temp"

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
- Be optimized for social media (square format)
- Use a white or light background
- Have excellent text legibility

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
- Be optimized for social media (square format)

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
- Be optimized for social media (square format)

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
        
        # Add logo overlay
        print(f"🏷️ Adding logo overlay...")
        add_logo(str(temp_path), str(LOGO_PATH))
        
        if not preview:
            # Skip preview, save directly
            output_path = move_to_output(temp_path, question_id, specialty, infographic_type)
            print(f"✅ Saved: {output_path}")
            return output_path
        
        # Show preview
        print(f"👁️ Opening preview...")
        open_preview(temp_path)
        
        # Get user approval
        approval = prompt_user_approval()
        
        if approval is True:
            output_path = move_to_output(temp_path, question_id, specialty, infographic_type)
            print(f"✅ Saved: {output_path}")
            return output_path
        
        elif approval is False:
            temp_path.unlink()  # Delete temp file
            print("🗑️ Discarded")
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
```

---

## Pipeline 3: Auto-Posting (Twitter/Instagram API)

### Overview

Post generated images directly to social platforms from the terminal.

```
You run script with image path
        ↓
Load image from output folder
        ↓
Generate caption (optional: from question data)
        ↓
Call Twitter API v2 / Instagram Graph API
        ↓
Post published
        ↓
Done ✓
```

### Script: `post_content.py`

```python
#!/usr/bin/env python3
"""
Pipeline 3: Auto-Post to Social Platforms
Posts images to Twitter and Instagram via their APIs.

Usage:
    python post_content.py --image output/card.png --platform twitter
    python post_content.py --image output/card.png --platform instagram
    python post_content.py --image output/card.png --platform all
    python post_content.py --image output/card.png --platform twitter --caption "Custom caption"

Options:
    --image       Path to image file (required)
    --platform    Platform: twitter, instagram, or all (default: twitter)
    --caption     Custom caption (optional, auto-generated if not provided)
    --question-id Question ID for auto-caption generation (optional)
"""

import os
import sys
import argparse
from pathlib import Path

import tweepy

from config import load_env

# Load environment variables
load_env()

# Twitter API Configuration
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Instagram API Configuration
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_BUSINESS_ID = os.getenv("INSTAGRAM_BUSINESS_ID")


def get_twitter_client() -> tweepy.Client:
    """Get authenticated Twitter API v2 client."""
    return tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET
    )


def get_twitter_api_v1() -> tweepy.API:
    """Get Twitter API v1.1 for media upload (required for images)."""
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )
    return tweepy.API(auth)


def post_to_twitter(image_path: str, caption: str = None) -> str:
    """
    Post image to Twitter.
    
    Args:
        image_path: Path to image file
        caption: Tweet text (max 280 chars)
    
    Returns:
        Tweet URL
    """
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        raise ValueError("Missing Twitter API credentials in .env")
    
    # Default caption
    if not caption:
        caption = "🧠 OKAP Question of the Day\n\nDrop your answer below 👇\n\n#Ophthalmology #OKAP #MedTwitter"
    
    # Truncate if needed
    if len(caption) > 280:
        caption = caption[:277] + "..."
    
    print(f"📤 Uploading image to Twitter...")
    
    # Upload media via v1.1 API
    api_v1 = get_twitter_api_v1()
    media = api_v1.media_upload(image_path)
    
    # Post tweet via v2 API
    client = get_twitter_client()
    response = client.create_tweet(
        text=caption,
        media_ids=[media.media_id]
    )
    
    tweet_id = response.data["id"]
    tweet_url = f"https://twitter.com/user/status/{tweet_id}"
    
    print(f"✅ Posted to Twitter: {tweet_url}")
    return tweet_url


def post_to_instagram(image_path: str, caption: str = None) -> str:
    """
    Post image to Instagram via Graph API.
    
    Note: Requires Facebook Business account and Instagram Business/Creator account.
    Image must be hosted at a public URL (not local file).
    
    Args:
        image_path: Path to image file (will need to be uploaded to public URL first)
        caption: Post caption
    
    Returns:
        Post URL
    """
    import requests
    
    if not all([INSTAGRAM_ACCESS_TOKEN, INSTAGRAM_BUSINESS_ID]):
        raise ValueError("Missing Instagram API credentials in .env")
    
    # Default caption
    if not caption:
        caption = """📌 OKAP Question of the Day

Drop your answer below 👇
Answer reveal coming soon!

💾 Save for board prep
🔗 1,200+ questions at subspecialty.com

#Ophthalmology #OKAP #BoardPrep #MedEd #Residency"""
    
    print(f"📤 Posting to Instagram...")
    
    # Note: Instagram Graph API requires image to be at a public URL
    # You'll need to upload to a hosting service first (e.g., Cloudinary, S3)
    # For now, this is a placeholder that shows the structure
    
    # Step 1: Create media container
    # POST /{ig-user-id}/media?image_url={url}&caption={caption}
    
    # Step 2: Publish media
    # POST /{ig-user-id}/media_publish?creation_id={container-id}
    
    raise NotImplementedError(
        "Instagram posting requires image hosting. "
        "Upload to Cloudinary/S3 first, then use the public URL."
    )


def generate_caption(question_id: str = None, platform: str = "twitter") -> str:
    """Generate caption from question data."""
    
    if not question_id:
        # Default captions
        if platform == "twitter":
            return "🧠 OKAP Question of the Day\n\nDrop your answer below 👇\n\n#Ophthalmology #OKAP #MedTwitter"
        else:  # instagram
            return """📌 OKAP Question of the Day

Drop your answer below 👇
Answer reveal coming soon!

💾 Save for board prep
🔗 subspecialty.com

#Ophthalmology #OKAP #BoardPrep #MedEd #Residency"""
    
    # Fetch question and generate dynamic caption
    from config import get_supabase_client
    
    supabase = get_supabase_client()
    response = supabase.table("questions").select("*").eq("id", question_id).single().execute()
    
    if not response.data:
        return generate_caption(None, platform)
    
    question = response.data
    category = question.get("category", "")
    
    if platform == "twitter":
        return f"🧠 {category} Question\n\nDrop your answer below 👇\n\n#Ophthalmology #OKAP #MedTwitter"
    else:
        return f"""📌 {category} Question

Drop your answer below 👇
Answer reveal coming soon!

💾 Save for board prep
🔗 subspecialty.com

#Ophthalmology #OKAP #BoardPrep #MedEd"""


def main():
    parser = argparse.ArgumentParser(
        description="Post images to social media platforms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python post_content.py --image output/cards/question.png --platform twitter
    python post_content.py --image output/cards/question.png --platform twitter --caption "Custom text"
    python post_content.py --image output/cards/question.png --platform all
        """
    )
    
    parser.add_argument(
        "--image",
        required=True,
        help="Path to image file"
    )
    parser.add_argument(
        "--platform",
        choices=["twitter", "instagram", "all"],
        default="twitter",
        help="Platform to post to (default: twitter)"
    )
    parser.add_argument(
        "--caption",
        help="Custom caption text"
    )
    parser.add_argument(
        "--question-id",
        help="Question ID for auto-generating caption"
    )
    
    args = parser.parse_args()
    
    # Validate image exists
    if not Path(args.image).exists():
        print(f"❌ Image not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    
    # Generate caption if not provided
    caption = args.caption
    
    try:
        if args.platform in ["twitter", "all"]:
            if not caption:
                caption = generate_caption(args.question_id, "twitter")
            post_to_twitter(args.image, caption)
        
        if args.platform in ["instagram", "all"]:
            if not caption:
                caption = generate_caption(args.question_id, "instagram")
            post_to_instagram(args.image, caption)
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Twitter API Setup

1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Create a project and app
3. Get API keys from the dashboard
4. Set up OAuth 1.0a with read/write permissions
5. Generate access tokens

**Free Tier Limits:**
- 1,500 tweets/month
- Media upload included

### Instagram API Setup

Instagram requires:
1. Facebook Business account
2. Instagram Business or Creator account
3. Facebook App with Instagram Graph API permissions
4. Images must be hosted at public URLs (not local files)

**Workaround for local images:**
- Upload to Cloudinary (free tier: 25GB)
- Upload to AWS S3
- Use a simple image hosting API

---

## Shared Utilities

### `config.py`

```python
"""
Configuration and database connection utilities.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv
from supabase import create_client, Client


def load_env():
    """Load environment variables from .env file."""
    load_dotenv()


@lru_cache(maxsize=1)
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    load_env()
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_KEY in environment")
    
    return create_client(url, key)


# Default configuration
class Config:
    DEFAULT_SPECIALTY = os.getenv("DEFAULT_SPECIALTY", "ophthalmology")
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "png")
    IMAGE_SIZE = int(os.getenv("IMAGE_SIZE", "1080"))
```

### `utils.py`

```python
"""
Shared utility functions.
"""

import os
import re
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_filename(name: str) -> str:
    """Convert string to safe filename."""
    # Remove or replace unsafe characters
    name = re.sub(r'[^\w\s-]', '', name)
    name = re.sub(r'[-\s]+', '-', name)
    return name.strip('-').lower()


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)].rsplit(' ', 1)[0] + suffix
```

### `overlay_logo.py`

```python
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
```

---

## Terminal Commands Reference

### Pipeline 1: Cards (HTMLCSSToImage)

```bash
# Generate question card only
python scripts/generate_card.py --id abc-123 --type question

# Generate answer card only
python scripts/generate_card.py --id abc-123 --type answer

# Generate both (carousel)
python scripts/generate_card.py --id abc-123 --type carousel

# Override specialty folder
python scripts/generate_card.py --id abc-123 --type carousel --specialty cardiology
```

### Pipeline 2: Infographics (Gemini)

```bash
# Generate pearl infographic (with preview)
python scripts/generate_infographic.py --id abc-123 --type pearl

# Generate comparison infographic
python scripts/generate_infographic.py --id abc-123 --type comparison

# Use detailed style
python scripts/generate_infographic.py --id abc-123 --style detailed

# Custom prompt
python scripts/generate_infographic.py --id abc-123 --prompt "Create an infographic showing the steps of phacoemulsification surgery"

# Save directly without preview
python scripts/generate_infographic.py --id abc-123 --save

# Override specialty
python scripts/generate_infographic.py --id abc-123 --specialty neurology
```

### Pipeline 3: Auto-Posting

```bash
# Post image to Twitter
python scripts/post_content.py --image output/cards/question.png --platform twitter

# Post with custom caption
python scripts/post_content.py --image output/cards/question.png --platform twitter --caption "Your caption here"

# Generate card AND auto-post in one step
python scripts/generate_card.py --id abc-123 --type carousel --post
```

### Quick Reference Table

| Command | Description |
|---------|-------------|
| `--id <id>` | Question ID (required) |
| `--type question/answer/carousel` | Card type for Pipeline 1 |
| `--type pearl/comparison/concept` | Infographic type for Pipeline 2 |
| `--style minimal/detailed/visual` | Style preset for Gemini |
| `--prompt "..."` | Custom prompt override |
| `--save` | Skip preview, save directly |
| `--specialty <name>` | Override output folder |

---

## API Reference

### Playwright (Local Screenshot)

**No API needed — runs locally.**

**Installation:**
```bash
pip install playwright
playwright install chromium
```

**Usage:**
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1080})
    page.goto("file:///path/to/template.html")
    page.screenshot(path="output.png")
    browser.close()
```

**Cost:** Free (unlimited)

---

### Twitter API v2

**Endpoint (Media Upload):** `POST https://upload.twitter.com/1.1/media/upload.json`
**Endpoint (Tweet):** `POST https://api.twitter.com/2/tweets`

**Authentication:** OAuth 1.0a

**Free Tier Limits:**
- 1,500 tweets/month
- Media upload included
- Read/write access required

**Setup:**
1. Create app at developer.twitter.com
2. Enable OAuth 1.0a with read/write
3. Generate access tokens

---

### Google Gemini API

**Model:** `gemini-2.0-flash-exp` (for image generation)

**Authentication:** API Key

**Image Generation:**
```python
import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel('gemini-2.0-flash-exp')

response = model.generate_content(
    "Create an infographic about...",
    generation_config=genai.GenerationConfig(
        response_mime_type="image/png"
    )
)
```

**Pricing:**
- Free tier: 500 images/day
- Paid: ~$0.039/image

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| `Question not found` | Verify question ID exists in Supabase |
| `Template not found` | Check templates/ folder has correct HTML files |
| `Playwright error` | Run `playwright install chromium` |
| `Gemini API error` | Verify GEMINI_API_KEY is valid |
| `Twitter auth error` | Check all 4 Twitter credentials in .env |
| `Logo not found` | Ensure assets/logo.png exists |
| `Permission denied` | Check file/folder permissions |

### Debug Mode

Add `--debug` flag (if implemented) or set environment variable:

```bash
export DEBUG=1
python scripts/generate_card.py --id abc-123 --type question
```

### Logs

Check output for detailed error messages. Both scripts print progress:
- 📥 Fetching...
- 🔧 Preparing...
- 🎨 Generating...
- ✅ Saved: path/to/file.png
- ❌ Error: description

---

## Quick Start

```bash
# 1. Clone/setup
mkdir subspecialty-content && cd subspecialty-content

# 2. Create folder structure
mkdir -p templates prompts/styles assets output/{cards,infographics,temp} scripts

# 3. Copy scripts from this document

# 4. Create .env
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
GEMINI_API_KEY=your-gemini-key
TWITTER_API_KEY=your-twitter-key
TWITTER_API_SECRET=your-twitter-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_SECRET=your-access-secret
EOF

# 5. Install dependencies
pip install supabase python-dotenv requests Pillow google-generativeai playwright tweepy
playwright install chromium

# 6. Add your logo to assets/logo.png

# 7. Generate content!
python scripts/generate_card.py --id your-question-id --type carousel
python scripts/generate_infographic.py --id your-question-id --type pearl
```

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Created for: Subspecialty (subspecialty.com)*