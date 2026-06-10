"""Export processed video data to JSON and CSV formats."""

import json
import os
from typing import List, Dict
from datetime import datetime
import pandas as pd


def export_json(data: List[Dict], output_path: str) -> str:
    """
    Export data to a JSON file.
    
    Args:
        data: List of video data dicts
        output_path: Path to output JSON file
    
    Returns:
        Absolute path to the written file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return os.path.abspath(output_path)


def export_csv(data: List[Dict], output_path: str) -> str:
    """
    Export data to a CSV file.
    
    Args:
        data: List of video data dicts
        output_path: Path to output CSV file
    
    Returns:
        Absolute path to the written file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Flatten topics_discussed list to comma-separated string
    rows = []
    for item in data:
        row = {
            "video_url": item.get("video_url", ""),
            "title": item.get("title", ""),
            "english_transcript": item.get("english_transcript", ""),
            "hindi_transcript": item.get("hindi_transcript", ""),
            "topics_discussed": ", ".join(item.get("topics_discussed", [])),
            "en_available": item.get("en_available", False),
            "hi_available": item.get("hi_available", False),
            "error": item.get("error", ""),
        }
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv(output_path, index=False, encoding="utf-8")
    
    return os.path.abspath(output_path)


def generate_output_paths(channel_name: str = "channel") -> Dict[str, str]:
    """Generate timestamped output file paths."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_dir = os.path.join("output", f"{channel_name}_{timestamp}")
    
    return {
        "json": os.path.join(base_dir, "transcripts.json"),
        "csv": os.path.join(base_dir, "transcripts.csv"),
    }
