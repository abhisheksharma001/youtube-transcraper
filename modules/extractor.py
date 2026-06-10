"""Keyword/topic extractor from transcripts using frequency analysis."""

import re
import string
from collections import Counter
from typing import List, Dict

# English stopwords
EN_STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours",
    "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers",
    "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves",
    "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does",
    "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until",
    "while", "of", "at", "by", "for", "with", "through", "during", "before", "after",
    "above", "below", "up", "down", "in", "out", "on", "off", "over", "under", "again",
    "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
    "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will",
    "just", "don", "should", "now", "to", "from", "like", "also", "get", "go", "one",
    "two", "would", "could", "may", "might", "must", "shall", "know", "think", "see",
    "way", "make", "well", "back", "much", "good", "new", "first", "last", "long",
    "great", "little", "own", "other", "old", "right", "big", "high", "different",
    "small", "large", "next", "early", "young", "important", "few", "public", "bad",
    "same", "able", "yeah", "um", "uh", "oh", "okay", "ok", "lot", "kind", "actually",
    "really", "even", "still", "thing", "things", "guys", "guy", "people", "person",
    "want", "need", "gonna", "wanna", "gonna", "gotta", "cause", "cause", "let", "lets",
    "come", "came", "coming", "say", "said", "saying", "look", "looking", "looked",
    "take", "taking", "took", "taken", "use", "using", "used", "work", "working",
    "worked", "try", "trying", "tried", "give", "giving", "gave", "given", "find",
    "finding", "found", "tell", "telling", "told", "ask", "asking", "asked", "seem",
    "seems", "seemed", "feel", "feeling", "felt", "become", "becoming", "became",
    "leave", "leaving", "left", "put", "putting", "mean", "means", "meant", "keep",
    "keeping", "kept", "let", "letting", "help", "helping", "helped", "show", "showing",
    "showed", "shown", "hear", "hearing", "heard", "play", "playing", "played", "run",
    "running", "ran", "move", "moving", "moved", "live", "living", "lived", "believe",
    "believing", "believed", "bring", "bringing", "brought", "happen", "happening",
    "happened", "stand", "standing", "stood", "lose", "losing", "lost", "pay", "paying",
    "paid", "meet", "meeting", "met", "include", "including", "included", "continue",
    "continuing", "continued", "set", "setting", "learn", "learning", "learned",
    "change", "changing", "changed", "lead", "leading", "led", "understand",
    "understanding", "understood", "watch", "watching", "watched", "follow",
    "following", "followed", "stop", "stopping", "stopped", "create", "creating",
    "created", "speak", "speaking", "spoke", "spoken", "read", "reading", "allow",
    "allowing", "allowed", "add", "adding", "added", "spend", "spending", "spent",
    "grow", "growing", "grew", "grown", "open", "opening", "opened", "walk",
    "walking", "walked", "offer", "offering", "offered", "remember", "remembering",
    "remembered", "love", "loving", "loved", "consider", "considering", "considered",
    "appear", "appearing", "appeared", "buy", "buying", "bought", "wait", "waiting",
    "waited", "serve", "serving", "served", "die", "dying", "died", "send", "sending",
    "sent", "expect", "expecting", "expected", "build", "building", "built", "stay",
    "staying", "stayed", "fall", "falling", "fell", "fallen", "cut", "cutting",
    "reach", "reaching", "reached", "kill", "killing", "killed", "remain",
    "remaining", "remained", "video", "videos", "subscribe", "channel", "youtube",
}

# Hindi stopwords (common)
HI_STOPWORDS = {
    "का", "की", "के", "को", "ने", "से", "में", "पर", "है", "हैं", "था", "थी", "थे",
    "हो", "होगा", "होगी", "होंगे", "कर", "करता", "करती", "करते", "किया", "की",
    "किए", "रहा", "रही", "रहे", "गया", "गई", "गए", "आ", "और", "या", "लेकिन",
    "कि", "जो", "सो", "तो", "वह", "वे", "यह", "ये", "इस", "उस", "जब", "तब",
    "क्यों", "क्या", "कहाँ", "कैसे", "सब", "सभी", "हर", "कुछ", "थोड़ा", "बहुत",
    "ज्यादा", "कम", "अधिक", "अब", "फिर", "बाद", "पहले", "दिन", "साल", "बार",
    "लिए", "तक", "साथ", "बीच", "ऊपर", "नीचे", "आगे", "पीछे", "द्वारा", "हुआ",
    "हुई", "हुए", "जाता", "जाती", "जाते", "आता", "आती", "आते", "लगता", "लगती",
    "लगते", "देता", "देती", "देते", "लेता", "लेती", "लेते", "पाता", "पाती", "पाते",
    "चाहिए", "सकता", "सकती", "सकते", "रहता", "रहती", "रहते", "वाला", "वाली",
    "वाले", "ही", "भी", "ना", "नहीं", "मत", "अगर", "चाहे", "भले", "जैसे",
    "तैसे", "जहाँ", "वहाँ", "कभी", "कहीं", "कोई", "किसी", "अपना", "अपनी",
    "अपने", "मेरा", "मेरी", "मेरे", "तुम्हारा", "तुम्हारी", "तुम्हारे", "हमारा",
    "हमारी", "हमारे", "इन", "उन", "जिन", "जिस", "इसे", "उसे", "इसी", "उसी",
    "इतना", "उतना", "जितना", "ऐसा", "वैसा", "कैसा", "कैसी", "कैसे", "जैसा",
    "तैसा", "वैसी", "वैसे", "ऐसी", "ऐसे", "न", "हां", "हाँ", "शुक्रिया",
    "धन्यवाद", "कृपया", "माफ", "स्वागत", "नमस्ते", "नमस्कार", "अलविदा",
    "फिरमिलेंगे", "ठीक", "हाँजी", "हुजूर", "जी", "जनाब", "महोदय",
}


def clean_text(text: str) -> str:
    """Remove URLs, extra whitespace, and normalize text."""
    text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def extract_keywords(text: str, top_n: int = 15) -> List[str]:
    """
    Extract top keywords from text using frequency analysis.
    
    Args:
        text: Input transcript text
        top_n: Number of top keywords to return
    
    Returns:
        List of keyword strings
    """
    if not text:
        return []
    
    text = clean_text(text)
    
    # Remove punctuation but keep spaces and Hindi characters
    # Hindi range: \u0900-\u097F
    # Keep English letters, Hindi characters, and spaces
    cleaned = re.sub(r"[^a-zA-Z\u0900-\u097F\s]", " ", text)
    
    words = cleaned.split()
    
    # Filter stopwords and short words
    filtered = []
    for w in words:
        if len(w) < 2:
            continue
        # English word check
        if w.isascii():
            if w not in EN_STOPWORDS:
                filtered.append(w)
        else:
            # Hindi word check
            if w not in HI_STOPWORDS:
                filtered.append(w)
    
    # Also extract bigrams for better topic phrases
    bigrams = []
    for i in range(len(filtered) - 1):
        w1, w2 = filtered[i], filtered[i + 1]
        # Only combine same-script bigrams
        if w1.isascii() == w2.isascii():
            bigrams.append(f"{w1} {w2}")
    
    # Weight bigrams slightly higher
    counter = Counter(filtered)
    bigram_counter = Counter(bigrams)
    
    # Combine: unigrams + weighted bigrams
    combined = counter.copy()
    for bg, count in bigram_counter.items():
        combined[bg] = combined.get(bg, 0) + count * 1.5
    
    top = combined.most_common(top_n)
    return [word for word, _ in top]


def extract_topics_for_video(video_data: Dict, top_n: int = 15) -> List[str]:
    """
    Extract topics from both English and Hindi transcripts.
    
    Args:
        video_data: Dict with en_transcript and hi_transcript
        top_n: Number of keywords per language
    
    Returns:
        Combined list of unique keywords
    """
    # Support both key naming conventions
    en_text = video_data.get("english_transcript", "") or video_data.get("en_transcript", "")
    hi_text = video_data.get("hindi_transcript", "") or video_data.get("hi_transcript", "")
    
    en_keywords = extract_keywords(en_text, top_n)
    hi_keywords = extract_keywords(hi_text, top_n)
    
    # Combine and deduplicate while preserving order
    seen = set()
    result = []
    for kw in en_keywords + hi_keywords:
        if kw not in seen:
            seen.add(kw)
            result.append(kw)
    
    return result[:top_n * 2]
