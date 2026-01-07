"""
Shared utility functions.
"""

import os
import re
from pathlib import Path
from functools import lru_cache

from openai import OpenAI
from dotenv import load_dotenv


# Character limits for each card element
CHAR_LIMITS = {
    # Question card
    "question_stem_question": 420,      # ~8 lines at 22px
    "option": 100,                       # ~2 lines at 17px

    # Answer card (more compact)
    "question_stem_answer": 380,        # ~6 lines at 17px (enough for clinical vignette)
    "explanation": 1800,                 # ~24 lines at 14px (must fit all 4 answers with detail)
    "key_concept": 400,                  # ~6 lines at 13px
}


def _get_openai_client():
    """Get configured OpenAI client."""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    return OpenAI(api_key=api_key)


def smart_truncate(
    text: str,
    max_chars: int,
    field_type: str = "general",
    use_llm: bool = True
) -> str:
    """
    Intelligently truncate/summarize text to fit within character limit.

    Args:
        text: The text to potentially truncate
        max_chars: Maximum character count allowed
        field_type: Type of field (question_stem, option, explanation, key_concept)
        use_llm: Whether to use LLM for summarization (default True)

    Returns:
        Text that fits within the character limit
    """
    if not text:
        return text

    # For explanations, ALWAYS format through LLM for consistent HTML structure
    # For other fields, only process if over the limit
    is_explanation = "explanation" in field_type.lower()
    if not is_explanation and len(text) <= max_chars:
        return text

    if not use_llm:
        # Fallback: simple truncation at word boundary (no ellipsis)
        truncated = text[:max_chars].rsplit(' ', 1)[0]
        return truncated

    # Use GPT-4o to intelligently summarize
    try:
        client = _get_openai_client()

        # Special handling for medical explanations - preserve answer structure
        if "explanation" in field_type.lower():
            system_prompt = """You are a medical content editor formatting explanations for display.

STRICT FORMATTING RULES:
1. Include ALL 4 answers (A, B, C, D) - never skip any
2. Use HTML tags ONLY - no markdown (no ** or __ formatting)
3. Format each answer label as: <strong>Answer X</strong> (using HTML strong tags)
4. Put a <br> tag AFTER each answer explanation (except the last one) to create line breaks
5. The correct answer says "is correct because", wrong answers say "is incorrect because"
6. PRESERVE AS MUCH DETAIL AS POSSIBLE - include full clinical reasoning if it fits within the character limit
7. Only shorten/summarize if the text exceeds the character limit
8. Do NOT include clinical pearls, tips, or extra commentary - ONLY the 4 answer explanations
9. Output ONLY the formatted text, nothing else

IMPORTANT: Always list the CORRECT answer FIRST, then the incorrect answers.

EXAMPLE OUTPUT FORMAT (correct answer first):
<strong>Answer B</strong> is correct because [full reasoning].<br>
<strong>Answer A</strong> is incorrect because [full reasoning].<br>
<strong>Answer C</strong> is incorrect because [full reasoning].<br>
<strong>Answer D</strong> is incorrect because [full reasoning]."""
        else:
            system_prompt = "You are a medical content editor. Rewrite text to fit character limits while preserving accuracy. Output only the rewritten text, nothing else."

        # Build prompt based on field type
        if "explanation" in field_type.lower():
            prompt = f"""Reformat this medical explanation to under {max_chars} characters.

MANDATORY FORMAT - follow exactly:
1. Use <strong>Answer X</strong> HTML tags for labels (NOT markdown **)
2. Add <br> tag after each answer (except last) for line breaks
3. Include all 4 answers (A, B, C, D)
4. Identify which answer is CORRECT from the original text
5. NO clinical pearls or extra tips - only the 4 answer explanations
6. PRESERVE FULL DETAIL when possible - only summarize if needed to fit the {max_chars} char limit
7. Include specific clinical details, imaging findings, and differentiating features

OUTPUT FORMAT (CORRECT ANSWER FIRST, then incorrect ones):
<strong>Answer [correct letter]</strong> is correct because [full reasoning].<br>
<strong>Answer [wrong]</strong> is incorrect because [full reasoning].<br>
<strong>Answer [wrong]</strong> is incorrect because [full reasoning].<br>
<strong>Answer [wrong]</strong> is incorrect because [full reasoning].

Original ({len(text)} chars, limit {max_chars}):
{text}"""
        else:
            prompt = f"""Rewrite the following {field_type} text to be under {max_chars} characters while preserving the key clinical information.

RULES:
- Output ONLY the rewritten text, nothing else
- Do NOT add any prefixes like "Here is..." or "The rewritten text is..."
- Keep medical terminology accurate
- Must be under {max_chars} characters
- Do not use ellipsis (...)
- Write complete sentences

Original text ({len(text)} chars):
{text}"""

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=700,
            temperature=0.3
        )

        # Track token usage and cost
        usage = response.usage
        input_cost = (usage.prompt_tokens / 1_000_000) * 2.50  # $2.50 per 1M input
        output_cost = (usage.completion_tokens / 1_000_000) * 10.00  # $10 per 1M output
        total_cost = input_cost + output_cost
        print(f"   💰 GPT-4o: {usage.prompt_tokens} in + {usage.completion_tokens} out = ${total_cost:.4f}")

        summarized = response.choices[0].message.content.strip()

        # Verify it fits
        if len(summarized) <= max_chars:
            return summarized
        else:
            # LLM didn't respect limit - truncate at sentence boundary
            truncated = summarized[:max_chars]
            # Find last complete sentence
            for end_char in ['. ', '.<br>', '.</strong>']:
                last_period = truncated.rfind(end_char)
                if last_period > max_chars * 0.5:  # At least half the content
                    return truncated[:last_period + 1]
            # Fallback: truncate at word boundary
            return truncated.rsplit(' ', 1)[0]

    except Exception as e:
        print(f"Warning: GPT-4o summarization failed ({e}), using simple truncation")
        # Truncate at sentence boundary
        truncated = text[:max_chars]
        last_period = truncated.rfind('. ')
        if last_period > max_chars * 0.5:
            return truncated[:last_period + 1]
        return truncated.rsplit(' ', 1)[0]


def process_card_data(data: dict, card_type: str = "question") -> dict:
    """
    Process card data, truncating any fields that exceed character limits.

    Args:
        data: Dictionary of card data with text fields
        card_type: Either "question" or "answer"

    Returns:
        Processed data with all fields within limits
    """
    processed = data.copy()

    # Question stem limit depends on card type
    stem_key = "question_stem"
    if stem_key in processed and processed[stem_key]:
        limit = CHAR_LIMITS[f"question_stem_{card_type}"]
        processed[stem_key] = smart_truncate(
            processed[stem_key],
            limit,
            field_type="medical question"
        )

    # Process options
    for opt in ["option_a", "option_b", "option_c", "option_d"]:
        if opt in processed and processed[opt]:
            processed[opt] = smart_truncate(
                processed[opt],
                CHAR_LIMITS["option"],
                field_type="answer option"
            )

    # Answer card specific fields
    if card_type == "answer":
        if "explanation" in processed and processed["explanation"]:
            processed["explanation"] = smart_truncate(
                processed["explanation"],
                CHAR_LIMITS["explanation"],
                field_type="medical explanation"
            )

        if "key_concept" in processed and processed["key_concept"]:
            processed["key_concept"] = smart_truncate(
                processed["key_concept"],
                CHAR_LIMITS["key_concept"],
                field_type="key concept summary"
            )

    return processed


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


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_templates_dir() -> Path:
    """Get templates directory path."""
    return get_project_root() / "templates"


def get_output_dir() -> Path:
    """Get output directory path."""
    return get_project_root() / "output"


def get_assets_dir() -> Path:
    """Get assets directory path."""
    return get_project_root() / "assets"


def get_prompts_dir() -> Path:
    """Get prompts directory path."""
    return get_project_root() / "prompts"
