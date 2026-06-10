"""Robust CLI script to extract transcripts with anti-rate-limiting measures."""

import sys
import json
import time
import random
from datetime import datetime
from modules.scraper import get_channel_videos
from modules.fetcher import fetch_transcript
from modules.extractor import extract_topics_for_video
from modules.exporter import export_json, export_csv

CHANNEL_URL = "https://www.youtube.com/@BhajanSaar"
BASE_DELAY = 5.0          # seconds between requests
JITTER_MAX = 3.0          # random extra delay (0 to N seconds)
TOP_N = 15
BATCH_SIZE = 10           # pause longer between batches
BATCH_PAUSE = 15.0        # seconds to rest between batches
MAX_RETRIES = 3           # retry on transient failures
CHECKPOINT_EVERY = 10     # save progress every N videos


def jittered_delay():
    """Sleep for base delay plus random jitter."""
    d = BASE_DELAY + random.uniform(0, JITTER_MAX)
    time.sleep(d)


def fetch_with_retry(video_id, proxy_url=None):
    """Fetch transcript with exponential backoff on rate limits."""
    for attempt in range(1, MAX_RETRIES + 1):
        result = fetch_transcript(video_id, delay=0, proxy_url=proxy_url)

        err = result.get("error", "")
        if err not in ("IP_BLOCKED", "REQUEST_BLOCKED", "No English or Hindi transcript available"):
            return result

        # If blocked or empty, wait longer and retry
        if attempt < MAX_RETRIES:
            backoff = (2 ** attempt) * 5 + random.uniform(0, 5)
            print(f"      ⏳ Rate limit suspected. Backing off {backoff:.1f}s (retry {attempt}/{MAX_RETRIES})...")
            time.sleep(backoff)

    return result


def main():
    print("=" * 70)
    print(f"🎬 YouTube Transcript Extractor - @BhajanSaar")
    print(f"   Base delay: {BASE_DELAY}s | Jitter: 0-{JITTER_MAX}s | Batch pause: {BATCH_PAUSE}s")
    print("=" * 70)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Fetching video list...")
    videos = get_channel_videos(CHANNEL_URL)
    total = len(videos)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Found {total} videos.")

    # Ask user if they want to resume from checkpoint
    checkpoint_files = sorted([
        f for f in os.listdir("output") if f.startswith("checkpoint_") and f.endswith(".json")
    ])

    start_idx = 0
    results = []
    if checkpoint_files:
        print(f"\n💾 Found checkpoints: {', '.join(checkpoint_files)}")
        ans = input("Resume from latest checkpoint? (y/n): ").strip().lower()
        if ans in ("y", "yes"):
            latest = checkpoint_files[-1]
            with open(f"output/{latest}", "r", encoding="utf-8") as f:
                results = json.load(f)
            start_idx = len(results)
            print(f"   Resuming from video {start_idx + 1} ({len(results)} already done)")

    print(f"\n{'-' * 70}")
    print(f"Starting extraction from video {start_idx + 1}/{total}")
    print(f"Press Ctrl+C at any time to stop (checkpoint saved every {CHECKPOINT_EVERY} videos)")
    print(f"{'-' * 70}\n")

    success_count = 0
    fail_count = 0
    ip_blocked_count = 0

    for idx in range(start_idx, total):
        video = videos[idx]
        video_id = video["video_id"]
        title = video.get("title", "")

        print(f"[{idx + 1}/{total}] {title[:65]}...", end=" ", flush=True)

        jittered_delay()
        transcript_data = fetch_with_retry(video_id)

        if "error" in transcript_data:
            err = transcript_data["error"]
            if err in ("IP_BLOCKED", "REQUEST_BLOCKED"):
                ip_blocked_count += 1
                print(f"[BLOCKED]")
                if ip_blocked_count >= 2:
                    print(f"\n🚫 IP blocked {ip_blocked_count} times. Stopping.")
                    print(f"   ➡️  Restart your WiFi/mobile hotspot, then resume from checkpoint.")
                    break
            else:
                print(f"[FAIL]")
            fail_count += 1
        else:
            en = "EN" if transcript_data['en_available'] else ""
            hi = "HI" if transcript_data['hi_available'] else ""
            print(f"[OK {en}{hi}]")
            success_count += 1

        result = {
            "video_url": video["url"],
            "title": title,
            "english_transcript": transcript_data.get("en_transcript", ""),
            "hindi_transcript": transcript_data.get("hi_transcript", ""),
            "en_available": transcript_data.get("en_available", False),
            "hi_available": transcript_data.get("hi_available", False),
        }

        if "error" in transcript_data:
            result["error"] = transcript_data["error"]

        try:
            topics = extract_topics_for_video(result, top_n=TOP_N)
            result["topics_discussed"] = topics
        except Exception as e:
            result["topics_discussed"] = []

        results.append(result)

        # Checkpoint save
        if (idx + 1) % CHECKPOINT_EVERY == 0:
            cp_path = f"output/checkpoint_{idx + 1}.json"
            with open(cp_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"  💾 Saved checkpoint ({idx + 1} videos)")

        # Batch pause
        if (idx + 1) % BATCH_SIZE == 0 and idx + 1 < total:
            pause = BATCH_PAUSE + random.uniform(0, 5)
            print(f"  ⏸️  Batch complete. Pausing {pause:.1f}s...")
            time.sleep(pause)

    print(f"\n{'-' * 70}")
    print(f"Done! Total: {len(results)} | ✅ Success: {success_count} | ❌ Fail: {fail_count} | 🚫 Blocks: {ip_blocked_count}")

    # Export final files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = f"output/bhajansaar_{timestamp}.json"
    csv_path = f"output/bhajansaar_{timestamp}.csv"

    export_json(results, json_path)
    export_csv(results, csv_path)

    print(f"\n📄 JSON: {json_path}")
    print(f"📊 CSV:  {csv_path}")


if __name__ == "__main__":
    import os
    main()
