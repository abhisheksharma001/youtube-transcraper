# 🎬 YouTube Transcript Extractor

Extract **English & Hindi transcripts** from any YouTube channel, generate **topic keywords** via frequency analysis, and download results as **JSON or CSV**.

## Features

- 🔗 **Channel URL input** — paste any YouTube channel URL
- 🌍 **Dual-language transcripts** — fetches both English and Hindi if available
- 🔑 **Auto topic extraction** — extracts top keywords using frequency analysis
- 📊 **JSON + CSV export** — structured data ready for analysis
- ⚡ **Progress tracking** — real-time progress bar and logs
- 🆓 **Zero API keys** — completely free, uses open-source libraries

## Requirements

- Python 3.8+
- Internet connection
- No paid API keys needed

## Setup

```bash
# 1. Clone or navigate to the project folder
cd youtube-transcript-extractor

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

## Usage

1. **Paste** a YouTube channel URL (e.g., `https://www.youtube.com/@channelname`)
2. **Adjust settings** in the sidebar if needed (request delay, keyword count)
3. Click **"Start Extraction"**
4. **Wait** for processing (see performance estimate below)
5. **Download** JSON or CSV when complete

## Output Formats

### JSON
```json
[
  {
    "video_url": "https://www.youtube.com/watch?v=...",
    "title": "Video Title",
    "english_transcript": "Full English transcript text...",
    "hindi_transcript": "Full Hindi transcript text...",
    "topics_discussed": ["keyword1", "keyword2", "..."],
    "en_available": true,
    "hi_available": true
  }
]
```

### CSV
Columns: `video_url`, `title`, `english_transcript`, `hindi_transcript`, `topics_discussed`, `en_available`, `hi_available`

## Performance Estimate

| Step | Time (approx) |
|------|---------------|
| Channel scraping | 1–2 minutes |
| Transcript fetching | 0.5–2 sec per video |
| Keyword extraction | <1 sec per video |
| **Total for 1500 videos** | **20–50 minutes** |

> Tip: Use the sidebar delay slider to avoid rate-limiting if processing large channels.

## Future: Going Public

To share this tool publicly:

1. **Deploy on Streamlit Cloud** (free)
   - Push code to GitHub
   - Connect repo to [share.streamlit.io](https://share.streamlit.io)
   
2. **Or deploy on Hugging Face Spaces** (free)
   - Create a Docker Space
   - Add `Dockerfile` with Streamlit setup

3. **For multi-user scale**, add:
   - Redis + Celery for background job queues
   - Authentication (OAuth)
   - SQLite/PostgreSQL for result storage
   - AI summaries (swap `extractor.py` with OpenAI/local LLM)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No videos found | Check the channel URL is correct and public |
| Transcripts disabled | Some creators disable captions — these are skipped |
| Rate limited | Increase the "Request delay" slider in sidebar |
| Hindi not found | Only videos with Hindi captions will have Hindi text |

## License

MIT — free for personal and commercial use.
