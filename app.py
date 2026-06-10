"""Streamlit app for YouTube Transcript Extractor."""

import os
import time
import streamlit as st

from modules.scraper import get_channel_videos
from modules.fetcher import fetch_transcript
from modules.extractor import extract_topics_for_video
from modules.exporter import export_json, export_csv, generate_output_paths

st.set_page_config(
    page_title="YouTube Transcript Extractor",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 YouTube Transcript Extractor")
st.markdown(
    "Extract **English & Hindi transcripts** from any YouTube channel, "
    "generate **topic keywords**, and download results as **JSON or CSV**."
)

# ⚠️ Cloud deployment warning
st.warning(
    "⚠️ **Important:** If you're running this on Streamlit Cloud (or any cloud server), "
    "YouTube will likely **block your IP** after a few requests. "
    "For 1500+ videos, run this app **locally on your own machine** instead. "
    "If you must use cloud, configure a proxy below.",
    icon="⚠️",
)

# Sidebar settings
st.sidebar.header("⚙️ Settings")
delay = st.sidebar.slider("Request delay (seconds)", 0.0, 5.0, 1.0, 0.1)
top_n = st.sidebar.slider("Keywords per language", 5, 30, 15, 1)

# Proxy settings
st.sidebar.divider()
st.sidebar.header("🔌 Proxy (Optional)")
use_proxy = st.sidebar.checkbox("Use proxy", value=False)
proxy_url = st.sidebar.text_input(
    "Proxy URL",
    placeholder="http://user:pass@proxy:port",
    disabled=not use_proxy,
    help="Residential proxy recommended. Free cloud IPs are blocked by YouTube.",
)

# Main input
channel_url = st.text_input(
    "Enter YouTube Channel URL",
    placeholder="https://www.youtube.com/@channelname",
)

# Initialize session state
if "results" not in st.session_state:
    st.session_state.results = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "running" not in st.session_state:
    st.session_state.running = False


def add_log(msg: str):
    st.session_state.logs.append(msg)


if st.button("🚀 Start Extraction", disabled=st.session_state.running):
    if not channel_url.strip():
        st.error("Please enter a valid YouTube channel URL.")
    else:
        st.session_state.running = True
        st.session_state.results = []
        st.session_state.logs = []
        st.rerun()

if st.session_state.running:
    progress_bar = st.progress(0)
    log_container = st.container()
    stats_placeholder = st.empty()
    warning_placeholder = st.empty()

    # Step 1: Scrape channel
    add_log("🔍 Fetching video list from channel...")
    with log_container:
        for log in st.session_state.logs:
            st.text(log)

    try:
        videos = get_channel_videos(channel_url)
    except Exception as e:
        add_log(f"❌ Failed to fetch channel: {e}")
        st.session_state.running = False
        st.rerun()

    total = len(videos)
    if total == 0:
        add_log("⚠️ No videos found. Check the channel URL.")
        st.session_state.running = False
        st.rerun()

    add_log(f"✅ Found {total} videos. Starting transcript extraction...")

    success_count = 0
    fail_count = 0
    ip_blocked = False

    for idx, video in enumerate(videos):
        video_id = video["video_id"]
        title = video.get("title", "")

        # Update progress
        progress = (idx + 1) / total
        progress_bar.progress(min(progress, 0.99))
        stats_placeholder.info(
            f"📊 Processed: {idx + 1}/{total} | ✅ Success: {success_count} | ❌ Failed: {fail_count}"
        )

        add_log(f"[{idx + 1}/{total}] {title[:60]}...")

        # Fetch transcript
        transcript_data = fetch_transcript(video_id, delay=delay, proxy_url=proxy_url if use_proxy else None)

        if "error" in transcript_data:
            err = transcript_data["error"]
            if err in ("IP_BLOCKED", "REQUEST_BLOCKED"):
                ip_blocked = True
                add_log("   🚫 YouTube blocked this IP. Stopping extraction.")
                warning_placeholder.error(
                    "🚫 **YouTube has blocked your IP.**\n\n"
                    "This happens on cloud servers (AWS, GCP, Azure, Streamlit Cloud, etc.).\n\n"
                    "**Solutions:**\n"
                    "1. **Run locally** on your own computer (recommended)\n"
                    "2. Use a **residential proxy** in the sidebar\n"
                    "3. Wait a few hours and try again"
                )
                break
            else:
                add_log(f"   ⚠️ {err}")
            fail_count += 1
        else:
            success_count += 1

        # Build result row
        video_result = {
            "video_url": video["url"],
            "title": title,
            "english_transcript": transcript_data.get("en_transcript", ""),
            "hindi_transcript": transcript_data.get("hi_transcript", ""),
            "en_available": transcript_data.get("en_available", False),
            "hi_available": transcript_data.get("hi_available", False),
        }

        # Extract topics
        try:
            topics = extract_topics_for_video(video_result, top_n=top_n)
            video_result["topics_discussed"] = topics
        except Exception as e:
            video_result["topics_discussed"] = []
            add_log(f"   ⚠️ Topic extraction failed: {e}")

        if "error" in transcript_data:
            video_result["error"] = transcript_data["error"]

        st.session_state.results.append(video_result)

        # Refresh log display
        with log_container:
            for log in st.session_state.logs[-20:]:
                st.text(log)

    progress_bar.empty()
    if ip_blocked:
        add_log("🛑 Extraction stopped due to IP block.")
    else:
        add_log("🏁 Extraction complete!")
    st.session_state.running = False
    st.rerun()

# Show results
if st.session_state.results:
    st.divider()
    st.subheader("📥 Download Results")

    # Generate output files
    paths = generate_output_paths()
    json_path = export_json(st.session_state.results, paths["json"])
    csv_path = export_csv(st.session_state.results, paths["csv"])

    col1, col2 = st.columns(2)

    with col1:
        with open(json_path, "rb") as f:
            st.download_button(
                label="📄 Download JSON",
                data=f,
                file_name=os.path.basename(json_path),
                mime="application/json",
            )

    with col2:
        with open(csv_path, "rb") as f:
            st.download_button(
                label="📊 Download CSV",
                data=f,
                file_name=os.path.basename(csv_path),
                mime="text/csv",
            )

    # Preview
    st.subheader("👁️ Preview (First 5 videos)")
    preview_df = []
    for item in st.session_state.results[:5]:
        preview_df.append({
            "Title": item["title"][:80],
            "URL": item["video_url"],
            "EN": "✅" if item["en_available"] else "❌",
            "HI": "✅" if item["hi_available"] else "❌",
            "Topics": ", ".join(item.get("topics_discussed", [])[:5]),
        })

    st.dataframe(preview_df, use_container_width=True)

    # Stats
    total_results = len(st.session_state.results)
    en_count = sum(1 for r in st.session_state.results if r["en_available"])
    hi_count = sum(1 for r in st.session_state.results if r["hi_available"])
    blocked_count = sum(1 for r in st.session_state.results if r.get("error") in ("IP_BLOCKED", "REQUEST_BLOCKED"))

    st.markdown(
        f"**Stats:** {total_results} videos | "
        f"English transcripts: {en_count} | "
        f"Hindi transcripts: {hi_count}"
        + (f" | 🚫 IP Blocks: {blocked_count}" if blocked_count > 0 else "")
    )
