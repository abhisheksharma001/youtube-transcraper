"""Transcript fetcher using youtube-transcript-api."""

import time
from typing import Dict
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    CouldNotRetrieveTranscript,
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


def fetch_transcript(video_id: str, delay: float = 0.5) -> Dict:
    """
    Fetch English and Hindi transcripts for a YouTube video.

    Args:
        video_id: YouTube video ID
        delay: Seconds to sleep after request (rate limiting)

    Returns:
        Dict with keys: video_id, en_transcript, hi_transcript, en_available, hi_available
    """
    result = {
        "video_id": video_id,
        "en_transcript": "",
        "hi_transcript": "",
        "en_available": False,
        "hi_available": False,
    }

    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
    except TranscriptsDisabled:
        result["error"] = "Transcripts disabled"
        time.sleep(delay)
        return result
    except VideoUnavailable:
        result["error"] = "Video unavailable"
        time.sleep(delay)
        return result
    except CouldNotRetrieveTranscript as e:
        result["error"] = f"Could not retrieve transcript: {e}"
        time.sleep(delay)
        return result
    except Exception as e:
        result["error"] = str(e)
        time.sleep(delay)
        return result

    # Try English – prefer manual, fallback to auto-generated
    for transcript in transcript_list:
        if transcript.language_code.startswith("en"):
            try:
                fetched = transcript.fetch()
                result["en_transcript"] = " ".join([s.text for s in fetched])
                result["en_available"] = True
                break
            except Exception:
                pass

    # Try Hindi – prefer manual, fallback to auto-generated
    for transcript in transcript_list:
        if transcript.language_code.startswith("hi"):
            try:
                fetched = transcript.fetch()
                result["hi_transcript"] = " ".join([s.text for s in fetched])
                result["hi_available"] = True
                break
            except Exception:
                pass

    # If neither found, try direct fetch as last resort
    if not result["en_available"]:
        try:
            fetched = api.fetch(video_id, languages=["en"])
            result["en_transcript"] = " ".join([s.text for s in fetched])
            result["en_available"] = True
        except (NoTranscriptFound, CouldNotRetrieveTranscript):
            pass
        except Exception:
            pass

    if not result["hi_available"]:
        try:
            fetched = api.fetch(video_id, languages=["hi"])
            result["hi_transcript"] = " ".join([s.text for s in fetched])
            result["hi_available"] = True
        except (NoTranscriptFound, CouldNotRetrieveTranscript):
            pass
        except Exception:
            pass

    if not result["en_available"] and not result["hi_available"]:
        result["error"] = "No English or Hindi transcript available"

    time.sleep(delay)
    return result
