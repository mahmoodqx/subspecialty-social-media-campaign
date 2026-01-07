#!/usr/bin/env python3
"""
Quick Card Generator
Just run: python3 generate.py

Prompts for Question ID and generates both Question and Answer cards.

Output: /Users/mk/Documents/Subspecialty Questions-Answers/{topic}_{date}/
        - question.png
        - answer.png
"""

import sys
import os

# Add scripts to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

from generate_card import generate_carousel


def main():
    print("")
    print("🎴 Subspecialty Card Generator")
    print("=" * 50)
    print("")

    question_id = input("📋 Paste Question ID: ").strip()

    if not question_id:
        print("❌ No ID provided. Exiting.")
        sys.exit(1)

    print("")
    print(f"🚀 Generating cards for: {question_id}")
    print("-" * 50)

    try:
        question_path, answer_path = generate_carousel(question_id)

        print("")
        print("=" * 50)
        print("✅ Done! Cards saved:")
        print(f"   📋 Question: {question_path.name}")
        print(f"   📋 Answer:   {answer_path.name}")
        print(f"   📁 Folder:   {question_path.parent}")
        print("")

        # Open the output folder
        os.system(f'open "{question_path.parent}"')

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
