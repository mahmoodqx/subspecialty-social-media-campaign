# Subspecialty Social Content System
## Template & Automation Documentation

---

## Table of Contents
1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Templates](#templates)
   - [Question Card Template](#question-card-template)
   - [Answer Card Template](#answer-card-template)
4. [Placeholder Reference](#placeholder-reference)
5. [Adapting for Other Specialties](#adapting-for-other-specialties)
6. [Python Injection Script](#python-injection-script)
7. [HTMLCSSToImage API Integration](#htmlcsstoimage-api-integration)

---

## Overview

This system generates social media images (1080x1080) for medical education content from a question database. It uses HTML/CSS templates with placeholder variables that get replaced with actual content, then rendered to PNG via HTMLCSSToImage API.

**Content Types:**
- Question Card — Daily engagement post
- Answer Card — Follow-up reveal with explanation

**Target Platforms:**
- Instagram (Feed)
- Twitter/X
- LinkedIn

---

## Folder Structure

```
/subspecialty-content/
├── templates/
│   ├── question-card.html       # Question template with placeholders
│   ├── answer-card.html         # Answer template with placeholders
│   ├── pearl-card.html          # (Future) High-yield fact template
│   └── comparison-card.html     # (Future) A vs B template
│
├── previews/
│   ├── question-card-preview.html   # Preview with sample content
│   └── answer-card-preview.html     # Preview with sample content
│
├── output/
│   ├── ophthalmology/
│   │   ├── questions/
│   │   └── answers/
│   ├── cardiology/              # (Future specialty)
│   └── neurology/               # (Future specialty)
│
├── scripts/
│   ├── generate_card.py         # Main generation script
│   ├── config.py                # API keys, Supabase connection
│   └── utils.py                 # Helper functions
│
├── assets/
│   └── logo.svg                 # Subspecialty logo
│
├── .env                         # Environment variables (API keys)
└── README.md                    # This file
```

---

## Templates

### Question Card Template

**File:** `templates/question-card.html`

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      width: 1080px;
      height: 1080px;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #ffffff;
      color: #1a1a1a;
      padding: 50px;
      display: flex;
      flex-direction: column;
    }

    /* Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 35px;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .logo-icon {
      width: 32px;
      height: 32px;
    }

    .logo-text {
      font-size: 26px;
      font-weight: 700;
      color: #1a1a1a;
      letter-spacing: -0.5px;
    }

    .badge {
      background: #f0fdf4;
      border: 1.5px solid #22c55e;
      color: #16a34a;
      padding: 10px 20px;
      border-radius: 25px;
      font-size: 14px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Category Tag */
    .category {
      display: inline-block;
      background: #f3f4f6;
      color: #6b7280;
      padding: 10px 18px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: 500;
      margin-bottom: 28px;
    }

    /* Question */
    .question-stem {
      font-size: 23px;
      font-weight: 400;
      line-height: 1.55;
      color: #1a1a1a;
      margin-bottom: 35px;
    }

    /* Options */
    .options {
      display: flex;
      flex-direction: column;
      gap: 14px;
      flex-grow: 1;
    }

    .option {
      display: flex;
      align-items: center;
      background: #ffffff;
      border: 1.5px solid #e5e7eb;
      border-radius: 12px;
      padding: 22px 24px;
    }

    .option-letter {
      font-weight: 600;
      font-size: 18px;
      color: #374151;
      margin-right: 14px;
      min-width: 28px;
    }

    .option-text {
      font-size: 18px;
      font-weight: 400;
      color: #374151;
      line-height: 1.4;
    }

    /* Footer */
    .footer {
      margin-top: auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 30px;
      border-top: 1px solid #e5e7eb;
    }

    .footer-logo {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .footer-logo-icon {
      width: 24px;
      height: 24px;
    }

    .footer-logo-text {
      font-size: 18px;
      font-weight: 600;
      color: #1a1a1a;
    }

    .engagement {
      font-size: 18px;
      font-weight: 600;
      color: #1a1a1a;
    }
  </style>
</head>
<body>

  <div class="header">
    <div class="logo">
      <svg class="logo-icon" xmlns="http://www.w3.org/2000/svg" viewBox="2 0 22 23" width="32" height="32">
        <circle cx="7.5" cy="3.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="7.5" cy="11.5" r="3.5" fill="#000000"/>
        <circle cx="7.5" cy="19.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="3.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="11.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="16.5" cy="19.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
      </svg>
      <span class="logo-text">Subspecialty</span>
    </div>
    <div class="badge">Question of the Day</div>
  </div>

  <div class="category">{{category}}</div>

  <div class="question-stem">{{question_stem}}</div>

  <div class="options">
    <div class="option">
      <span class="option-letter">A.</span>
      <span class="option-text">{{option_a}}</span>
    </div>
    <div class="option">
      <span class="option-letter">B.</span>
      <span class="option-text">{{option_b}}</span>
    </div>
    <div class="option">
      <span class="option-letter">C.</span>
      <span class="option-text">{{option_c}}</span>
    </div>
    <div class="option">
      <span class="option-letter">D.</span>
      <span class="option-text">{{option_d}}</span>
    </div>
  </div>

  <div class="footer">
    <div class="footer-logo">
      <svg class="footer-logo-icon" xmlns="http://www.w3.org/2000/svg" viewBox="2 0 22 23" width="24" height="24">
        <circle cx="7.5" cy="3.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="7.5" cy="11.5" r="3.5" fill="#000000"/>
        <circle cx="7.5" cy="19.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="3.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="11.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="16.5" cy="19.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
      </svg>
      <span class="footer-logo-text">Subspecialty</span>
    </div>
    <div class="engagement">Drop your answer below 👇</div>
  </div>

</body>
</html>
```

---

### Answer Card Template

**File:** `templates/answer-card.html`

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      width: 1080px;
      height: 1080px;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: #ffffff;
      color: #1a1a1a;
      padding: 45px;
      display: flex;
      flex-direction: column;
    }

    /* Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 25px;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .logo-icon {
      width: 28px;
      height: 28px;
    }

    .logo-text {
      font-size: 24px;
      font-weight: 700;
      color: #1a1a1a;
      letter-spacing: -0.5px;
    }

    .badge {
      background: #22c55e;
      color: #ffffff;
      padding: 8px 18px;
      border-radius: 25px;
      font-size: 13px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    /* Category Tag */
    .category-tag {
      display: inline-block;
      background: #f3f4f6;
      color: #6b7280;
      padding: 8px 14px;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 18px;
    }

    /* Question */
    .question-stem {
      font-size: 17px;
      font-weight: 400;
      line-height: 1.5;
      color: #1a1a1a;
      margin-bottom: 20px;
    }

    /* Options */
    .options {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-bottom: 16px;
    }

    .option {
      display: flex;
      align-items: center;
      background: #ffffff;
      border: 1.5px solid #e5e7eb;
      border-radius: 10px;
      padding: 14px 18px;
    }

    .option.correct {
      background: #f0fdf4;
      border: 2px solid #22c55e;
    }

    .option-letter {
      font-weight: 600;
      font-size: 15px;
      color: #374151;
      margin-right: 12px;
      min-width: 24px;
    }

    .option.correct .option-letter {
      color: #16a34a;
    }

    .option-text {
      font-size: 15px;
      font-weight: 400;
      color: #374151;
      line-height: 1.4;
    }

    .option.correct .option-text {
      color: #15803d;
      font-weight: 500;
    }

    /* Meta Row */
    .meta-row {
      display: flex;
      background: #f9fafb;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 16px;
      gap: 40px;
    }

    .meta-item {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .meta-label {
      font-size: 12px;
      font-weight: 600;
      color: #6b7280;
    }

    .meta-value {
      font-size: 14px;
      font-weight: 500;
      color: #1a1a1a;
    }

    .meta-value.correct {
      color: #16a34a;
    }

    /* Explanation */
    .explanation {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-left: 4px solid #22c55e;
      padding: 18px 20px;
      border-radius: 0 10px 10px 0;
      margin-bottom: 14px;
    }

    .explanation-title {
      font-size: 14px;
      font-weight: 700;
      color: #1a1a1a;
      margin-bottom: 10px;
    }

    .explanation-text {
      font-size: 14px;
      font-weight: 400;
      color: #374151;
      line-height: 1.6;
    }

    /* Key Concept */
    .key-concept {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-left: 4px solid #6b7280;
      padding: 16px 20px;
      border-radius: 0 10px 10px 0;
      flex-grow: 1;
    }

    .key-concept-title {
      font-size: 13px;
      font-weight: 700;
      color: #1a1a1a;
      margin-bottom: 8px;
    }

    .key-concept-text {
      font-size: 13px;
      font-weight: 400;
      color: #374151;
      line-height: 1.6;
    }

    /* Footer */
    .footer {
      margin-top: auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 20px;
      border-top: 1px solid #e5e7eb;
    }

    .footer-logo {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .footer-logo-icon {
      width: 22px;
      height: 22px;
    }

    .footer-logo-text {
      font-size: 16px;
      font-weight: 600;
      color: #1a1a1a;
    }

    .result {
      font-size: 15px;
      font-weight: 500;
      color: #6b7280;
    }
  </style>
</head>
<body>

  <div class="header">
    <div class="logo">
      <svg class="logo-icon" xmlns="http://www.w3.org/2000/svg" viewBox="2 0 22 23" width="28" height="28">
        <circle cx="7.5" cy="3.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="7.5" cy="11.5" r="3.5" fill="#000000"/>
        <circle cx="7.5" cy="19.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="3.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="11.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="16.5" cy="19.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
      </svg>
      <span class="logo-text">Subspecialty</span>
    </div>
    <div class="badge">Answer Reveal</div>
  </div>

  <div class="category-tag">{{category}}</div>

  <div class="question-stem">{{question_stem}}</div>

  <div class="options">
    <div class="option {{class_a}}">
      <span class="option-letter">A.</span>
      <span class="option-text">{{option_a}}</span>
    </div>
    <div class="option {{class_b}}">
      <span class="option-letter">B.</span>
      <span class="option-text">{{option_b}}</span>
    </div>
    <div class="option {{class_c}}">
      <span class="option-letter">C.</span>
      <span class="option-text">{{option_c}}</span>
    </div>
    <div class="option {{class_d}}">
      <span class="option-letter">D.</span>
      <span class="option-text">{{option_d}}</span>
    </div>
  </div>

  <div class="meta-row">
    <div class="meta-item">
      <span class="meta-label">Category</span>
      <span class="meta-value">{{meta_category}}</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Topic</span>
      <span class="meta-value">{{topic}}</span>
    </div>
    <div class="meta-item">
      <span class="meta-label">Correct Answer</span>
      <span class="meta-value correct">{{correct_answer}}</span>
    </div>
  </div>

  <div class="explanation">
    <div class="explanation-title">Explanation</div>
    <div class="explanation-text">{{explanation}}</div>
  </div>

  <div class="key-concept">
    <div class="key-concept-title">Key Concept</div>
    <div class="key-concept-text">{{key_concept}}</div>
  </div>

  <div class="footer">
    <div class="footer-logo">
      <svg class="footer-logo-icon" xmlns="http://www.w3.org/2000/svg" viewBox="2 0 22 23" width="22" height="22">
        <circle cx="7.5" cy="3.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="7.5" cy="11.5" r="3.5" fill="#000000"/>
        <circle cx="7.5" cy="19.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="3.5" r="3.5" fill="#000000"/>
        <circle cx="16.5" cy="11.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
        <circle cx="16.5" cy="19.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
      </svg>
      <span class="footer-logo-text">Subspecialty</span>
    </div>
    <div class="result">Did you get it right? 🎯</div>
  </div>

</body>
</html>
```

---

## Placeholder Reference

### Question Card Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{category}}` | Specialty and subcategory | `Ophthalmology - Glaucoma` |
| `{{question_stem}}` | Full question text | `A 34-year-old man with...` |
| `{{option_a}}` | Answer option A | `Add topical aqueous suppressant therapy` |
| `{{option_b}}` | Answer option B | `Perform laser peripheral iridotomy` |
| `{{option_c}}` | Answer option C | `Discontinue topical corticosteroid immediately` |
| `{{option_d}}` | Answer option D | `Initiate oral acetazolamide 500 mg twice daily` |

### Answer Card Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{{category}}` | Specialty and subcategory | `Ophthalmology - Glaucoma` |
| `{{question_stem}}` | Full question text (can be shortened) | `A 34-year-old man with...` |
| `{{option_a}}` | Answer option A | `Add topical aqueous suppressant therapy` |
| `{{option_b}}` | Answer option B | `Perform laser peripheral iridotomy` |
| `{{option_c}}` | Answer option C | `Discontinue topical corticosteroid immediately` |
| `{{option_d}}` | Answer option D | `Initiate oral acetazolamide 500 mg twice daily` |
| `{{class_a}}` | CSS class for option A | `correct` or empty |
| `{{class_b}}` | CSS class for option B | `correct` or empty |
| `{{class_c}}` | CSS class for option C | `correct` or empty |
| `{{class_d}}` | CSS class for option D | `correct` or empty |
| `{{meta_category}}` | Short category name | `Glaucoma` |
| `{{topic}}` | Specific topic | `Inflammatory Glaucoma` |
| `{{correct_answer}}` | Letter of correct answer | `A` |
| `{{explanation}}` | Explanation text | `Answer A is correct because...` |
| `{{key_concept}}` | Key takeaway | `Secondary open-angle glaucoma...` |

---

## Adapting for Other Specialties

To add a new specialty (e.g., Cardiology, Neurology):

### 1. Create output folders

```bash
mkdir -p output/cardiology/questions
mkdir -p output/cardiology/answers
```

### 2. Update category in your data

Ensure your Supabase questions have the appropriate category:
- `Cardiology - Arrhythmias`
- `Cardiology - Heart Failure`
- `Neurology - Stroke`
- etc.

### 3. Optional: Customize colors per specialty

You can create specialty-specific templates with different accent colors:

| Specialty | Primary Color | Hex |
|-----------|---------------|-----|
| Ophthalmology | Green | `#22c55e` |
| Cardiology | Red | `#ef4444` |
| Neurology | Purple | `#8b5cf6` |
| Pulmonology | Blue | `#3b82f6` |
| Gastroenterology | Orange | `#f97316` |

To customize, replace `#22c55e` in the template CSS with your specialty color.

---

## Python Injection Script

**File:** `scripts/generate_card.py`

```python
#!/usr/bin/env python3
"""
Subspecialty Social Card Generator
Generates question and answer card images from templates.

Usage:
    python generate_card.py --id <question_id> --type question
    python generate_card.py --id <question_id> --type answer
    python generate_card.py --id <question_id> --type carousel  # Both
"""

import os
import argparse
import requests
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HCTI_USER_ID = os.getenv("HCTI_USER_ID")
HCTI_API_KEY = os.getenv("HCTI_API_KEY")

TEMPLATES_DIR = "templates"
OUTPUT_DIR = "output"


def get_supabase_client():
    """Initialize Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_question(question_id: str) -> dict:
    """Fetch question data from Supabase."""
    supabase = get_supabase_client()
    response = supabase.table("questions").select("*").eq("id", question_id).single().execute()
    return response.data


def load_template(template_name: str) -> str:
    """Load HTML template from file."""
    template_path = os.path.join(TEMPLATES_DIR, f"{template_name}.html")
    with open(template_path, "r") as f:
        return f.read()


def inject_data(template: str, data: dict) -> str:
    """Replace placeholders with actual data."""
    html = template
    for key, value in data.items():
        placeholder = "{{" + key + "}}"
        html = html.replace(placeholder, str(value) if value else "")
    return html


def generate_image(html: str, filename: str) -> str:
    """Send HTML to HTMLCSSToImage API and save result."""
    url = "https://hcti.io/v1/image"
    
    response = requests.post(
        url,
        auth=(HCTI_USER_ID, HCTI_API_KEY),
        json={"html": html}
    )
    
    if response.status_code == 200:
        image_url = response.json()["url"]
        
        # Download and save image
        image_response = requests.get(image_url)
        output_path = os.path.join(OUTPUT_DIR, filename)
        
        with open(output_path, "wb") as f:
            f.write(image_response.content)
        
        print(f"✓ Generated: {output_path}")
        return output_path
    else:
        print(f"✗ Error: {response.text}")
        return None


def prepare_question_data(question: dict) -> dict:
    """Prepare data for question card template."""
    return {
        "category": f"{question.get('specialty', 'Medicine')} - {question.get('category', '')}",
        "question_stem": question.get("question_stem", ""),
        "option_a": question.get("option_a", ""),
        "option_b": question.get("option_b", ""),
        "option_c": question.get("option_c", ""),
        "option_d": question.get("option_d", ""),
    }


def prepare_answer_data(question: dict) -> dict:
    """Prepare data for answer card template."""
    correct = question.get("correct_answer", "A").upper()
    
    return {
        "category": f"{question.get('specialty', 'Medicine')} - {question.get('category', '')}",
        "question_stem": question.get("question_stem", ""),
        "option_a": question.get("option_a", ""),
        "option_b": question.get("option_b", ""),
        "option_c": question.get("option_c", ""),
        "option_d": question.get("option_d", ""),
        "class_a": "correct" if correct == "A" else "",
        "class_b": "correct" if correct == "B" else "",
        "class_c": "correct" if correct == "C" else "",
        "class_d": "correct" if correct == "D" else "",
        "meta_category": question.get("category", ""),
        "topic": question.get("topic", ""),
        "correct_answer": correct,
        "explanation": question.get("explanation", ""),
        "key_concept": question.get("key_concept", ""),
    }


def generate_question_card(question_id: str):
    """Generate question card image."""
    question = fetch_question(question_id)
    template = load_template("question-card")
    data = prepare_question_data(question)
    html = inject_data(template, data)
    
    specialty = question.get("specialty", "general").lower().replace(" ", "-")
    filename = f"{specialty}/questions/{question_id}-question.png"
    
    return generate_image(html, filename)


def generate_answer_card(question_id: str):
    """Generate answer card image."""
    question = fetch_question(question_id)
    template = load_template("answer-card")
    data = prepare_answer_data(question)
    html = inject_data(template, data)
    
    specialty = question.get("specialty", "general").lower().replace(" ", "-")
    filename = f"{specialty}/answers/{question_id}-answer.png"
    
    return generate_image(html, filename)


def main():
    parser = argparse.ArgumentParser(description="Generate social media cards")
    parser.add_argument("--id", required=True, help="Question ID from Supabase")
    parser.add_argument("--type", choices=["question", "answer", "carousel"], 
                        default="carousel", help="Card type to generate")
    
    args = parser.parse_args()
    
    if args.type in ["question", "carousel"]:
        generate_question_card(args.id)
    
    if args.type in ["answer", "carousel"]:
        generate_answer_card(args.id)


if __name__ == "__main__":
    main()
```

---

## HTMLCSSToImage API Integration

### Environment Variables

**File:** `.env`

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key

# HTMLCSSToImage
HCTI_USER_ID=your-user-id
HCTI_API_KEY=your-api-key
```

### API Reference

**Endpoint:** `POST https://hcti.io/v1/image`

**Authentication:** HTTP Basic Auth (User ID : API Key)

**Request Body:**
```json
{
  "html": "<your complete HTML>",
  "css": "",
  "google_fonts": "Inter"
}
```

**Response:**
```json
{
  "url": "https://hcti.io/v1/image/abc123"
}
```

### Rate Limits

| Plan | Images/Month | Cost |
|------|--------------|------|
| Starter | 3,000 | $14/mo |
| Growth | 15,000 | $49/mo |
| Scale | 50,000 | $99/mo |

---

## Logo SVG Reference

The Subspecialty logo consists of 6 dots in a 2x3 grid:
- **Solid dots:** Middle-left, Bottom-left, Top-right
- **Hollow rings:** Top-left, Middle-right, Bottom-right

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="2 0 22 23" width="32" height="32">
  <!-- Top Left - hollow (ring) -->
  <circle cx="7.5" cy="3.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
  <!-- Middle Left - solid -->
  <circle cx="7.5" cy="11.5" r="3.5" fill="#000000"/>
  <!-- Bottom Left - solid -->
  <circle cx="7.5" cy="19.5" r="3.5" fill="#000000"/>
  <!-- Top Right - solid -->
  <circle cx="16.5" cy="3.5" r="3.5" fill="#000000"/>
  <!-- Middle Right - hollow (ring) -->
  <circle cx="16.5" cy="11.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
  <!-- Bottom Right - hollow (ring) -->
  <circle cx="16.5" cy="19.5" r="2.5" fill="none" stroke="#000000" stroke-width="2"/>
</svg>
```

---

## Quick Start

```bash
# 1. Clone/setup project
mkdir subspecialty-content && cd subspecialty-content

# 2. Create folder structure
mkdir -p templates previews output scripts assets

# 3. Copy templates from this document

# 4. Install dependencies
pip install supabase python-dotenv requests

# 5. Configure .env with your API keys

# 6. Generate a card
python scripts/generate_card.py --id your-question-id --type carousel
```

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Created for: Subspecialty (subspecialty.com)*
