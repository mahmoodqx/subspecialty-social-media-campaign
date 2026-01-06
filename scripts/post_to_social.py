#!/usr/bin/env python3
"""
Pipeline 3: Social Media Posting
Posts generated images to Twitter/X using Twitter API v2.

Usage:
    python post_to_social.py --image path/to/image.png --text "Your tweet text"
    python post_to_social.py --image path/to/image.png --text "Your tweet text" --platform twitter
    python post_to_social.py --carousel image1.png image2.png --text "Carousel post"

Options:
    --image         Single image path to post
    --carousel      Multiple image paths (up to 4 for Twitter)
    --text          Post text/caption
    --platform      Platform to post to: twitter (default: twitter)
    --dry-run       Preview post without actually posting
"""

import os
import sys
import argparse
from pathlib import Path

import tweepy

from config import load_env

# Load environment variables
load_env()

# Twitter API credentials
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")


def get_twitter_client() -> tweepy.Client:
    """Get authenticated Twitter API v2 client."""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        raise ValueError("Missing Twitter API credentials in environment")

    return tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET
    )


def get_twitter_api_v1() -> tweepy.API:
    """Get Twitter API v1.1 for media uploads (required for images)."""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        raise ValueError("Missing Twitter API credentials in environment")

    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )

    return tweepy.API(auth)


def upload_media(api_v1: tweepy.API, image_path: str) -> str:
    """Upload image to Twitter and return media_id."""
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    print(f"📤 Uploading: {path.name}")
    media = api_v1.media_upload(str(path))

    return media.media_id_string


def post_to_twitter(
    image_paths: list,
    text: str,
    dry_run: bool = False
) -> dict:
    """
    Post image(s) to Twitter/X.

    Args:
        image_paths: List of image file paths (max 4)
        text: Tweet text
        dry_run: If True, preview without posting

    Returns:
        dict with tweet info or dry run preview
    """

    if len(image_paths) > 4:
        raise ValueError("Twitter allows maximum 4 images per tweet")

    # Validate images exist
    for path in image_paths:
        if not Path(path).exists():
            raise FileNotFoundError(f"Image not found: {path}")

    if dry_run:
        print("\n🔍 DRY RUN - Preview:")
        print(f"   Text: {text}")
        print(f"   Images: {', '.join([Path(p).name for p in image_paths])}")
        print("   (No actual post made)")
        return {"dry_run": True, "text": text, "images": image_paths}

    # Get API clients
    client = get_twitter_client()
    api_v1 = get_twitter_api_v1()

    # Upload media
    media_ids = []
    for path in image_paths:
        media_id = upload_media(api_v1, path)
        media_ids.append(media_id)

    # Create tweet
    print(f"🐦 Posting tweet...")
    response = client.create_tweet(
        text=text,
        media_ids=media_ids
    )

    tweet_id = response.data["id"]
    tweet_url = f"https://twitter.com/user/status/{tweet_id}"

    print(f"✅ Posted successfully!")
    print(f"   Tweet ID: {tweet_id}")
    print(f"   URL: {tweet_url}")

    return {
        "tweet_id": tweet_id,
        "url": tweet_url,
        "text": text,
        "media_ids": media_ids
    }


def post_carousel_to_twitter(
    question_image: str,
    answer_image: str,
    text: str,
    dry_run: bool = False
) -> dict:
    """
    Post a question/answer carousel to Twitter.
    Creates a thread: Question image first, then Answer as reply.

    Args:
        question_image: Path to question card
        answer_image: Path to answer card
        text: Tweet text for question post
        dry_run: If True, preview without posting

    Returns:
        dict with both tweet infos
    """

    if dry_run:
        print("\n🔍 DRY RUN - Carousel Preview:")
        print(f"   Tweet 1 (Question): {text}")
        print(f"   Image: {Path(question_image).name}")
        print(f"   Tweet 2 (Answer): Reply with answer reveal")
        print(f"   Image: {Path(answer_image).name}")
        print("   (No actual posts made)")
        return {"dry_run": True}

    # Get API clients
    client = get_twitter_client()
    api_v1 = get_twitter_api_v1()

    # Upload question image
    print(f"📤 Uploading question card...")
    question_media_id = upload_media(api_v1, question_image)

    # Post question tweet
    print(f"🐦 Posting question...")
    question_response = client.create_tweet(
        text=text,
        media_ids=[question_media_id]
    )
    question_tweet_id = question_response.data["id"]

    # Upload answer image
    print(f"📤 Uploading answer card...")
    answer_media_id = upload_media(api_v1, answer_image)

    # Post answer as reply
    print(f"🐦 Posting answer (reply)...")
    answer_response = client.create_tweet(
        text="Answer reveal 👇",
        media_ids=[answer_media_id],
        in_reply_to_tweet_id=question_tweet_id
    )
    answer_tweet_id = answer_response.data["id"]

    print(f"\n✅ Carousel posted successfully!")
    print(f"   Question: https://twitter.com/user/status/{question_tweet_id}")
    print(f"   Answer:   https://twitter.com/user/status/{answer_tweet_id}")

    return {
        "question_tweet_id": question_tweet_id,
        "answer_tweet_id": answer_tweet_id,
        "question_url": f"https://twitter.com/user/status/{question_tweet_id}",
        "answer_url": f"https://twitter.com/user/status/{answer_tweet_id}"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Post images to social media (Twitter/X)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Single image
    python post_to_social.py --image output/cards/question.png --text "Question of the day!"

    # Multiple images (up to 4)
    python post_to_social.py --carousel img1.png img2.png --text "Check this out"

    # Question/Answer thread
    python post_to_social.py --thread question.png answer.png --text "Can you answer this?"

    # Dry run (preview without posting)
    python post_to_social.py --image output/cards/question.png --text "Test" --dry-run
        """
    )

    parser.add_argument(
        "--image",
        help="Single image path to post"
    )
    parser.add_argument(
        "--carousel",
        nargs="+",
        help="Multiple image paths (max 4 for Twitter)"
    )
    parser.add_argument(
        "--thread",
        nargs=2,
        metavar=("QUESTION", "ANSWER"),
        help="Question and answer images for thread post"
    )
    parser.add_argument(
        "--text",
        required=True,
        help="Post text/caption"
    )
    parser.add_argument(
        "--platform",
        choices=["twitter"],
        default="twitter",
        help="Platform to post to (default: twitter)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview post without actually posting"
    )

    args = parser.parse_args()

    try:
        if args.thread:
            # Thread mode: Question + Answer
            result = post_carousel_to_twitter(
                question_image=args.thread[0],
                answer_image=args.thread[1],
                text=args.text,
                dry_run=args.dry_run
            )

        elif args.carousel:
            # Multiple images in one tweet
            result = post_to_twitter(
                image_paths=args.carousel,
                text=args.text,
                dry_run=args.dry_run
            )

        elif args.image:
            # Single image
            result = post_to_twitter(
                image_paths=[args.image],
                text=args.text,
                dry_run=args.dry_run
            )

        else:
            parser.print_help()
            print("\n❌ Error: Must specify --image, --carousel, or --thread")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
