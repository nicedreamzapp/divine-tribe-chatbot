#!/usr/bin/env python3
"""
YouTube Knowledge Builder
Pulls transcripts from Divine Tribe YouTube channel and builds knowledge base
"""

import json
import os
import re
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi

# Divine Tribe video library - add video IDs here
# Format: {'video_id': 'title/topic'}
DIVINE_TRIBE_VIDEOS = {
    'B6j5fwEhHI8': 'V5 Pico Plus Settings and Autofire Guide',
    # Add more videos as we discover them
}

def get_transcript(video_id: str) -> str:
    """Pull transcript from a YouTube video"""
    try:
        ytt = YouTubeTranscriptApi()
        transcript = ytt.fetch(video_id)
        full_text = ' '.join([s.text for s in transcript.snippets])
        return full_text
    except Exception as e:
        print(f"Error getting transcript for {video_id}: {e}")
        return None


def extract_settings_from_transcript(text: str) -> dict:
    """Extract settings mentioned in transcript"""
    settings = {
        'tcr_values': [],
        'wattages': [],
        'temperatures': [],
        'tips': []
    }

    # Find TCR mentions
    tcr_pattern = r'tcr[^\d]*(\d{2,3})'
    for match in re.finditer(tcr_pattern, text.lower()):
        settings['tcr_values'].append(int(match.group(1)))

    # Find wattage mentions
    watt_pattern = r'(\d{2,3})\s*(?:watts?|w\b)'
    for match in re.finditer(watt_pattern, text.lower()):
        settings['wattages'].append(int(match.group(1)))

    # Find temperature mentions
    temp_pattern = r'(\d{3,4})\s*(?:degrees?|°|f\b)'
    for match in re.finditer(temp_pattern, text.lower()):
        settings['temperatures'].append(int(match.group(1)))

    return settings


def build_knowledge_base():
    """Build knowledge base from all Divine Tribe videos"""
    knowledge = {
        'last_updated': datetime.now().isoformat(),
        'videos': {},
        'extracted_settings': {}
    }

    for video_id, title in DIVINE_TRIBE_VIDEOS.items():
        print(f"Processing: {title} ({video_id})")

        transcript = get_transcript(video_id)
        if transcript:
            settings = extract_settings_from_transcript(transcript)

            knowledge['videos'][video_id] = {
                'title': title,
                'transcript': transcript,
                'url': f'https://youtube.com/watch?v={video_id}',
                'settings': settings
            }

            print(f"  - TCR values found: {settings['tcr_values']}")
            print(f"  - Wattages found: {settings['wattages']}")
            print(f"  - Temperatures found: {settings['temperatures']}")

    # Save knowledge base
    output_file = 'youtube_knowledge.json'
    with open(output_file, 'w') as f:
        json.dump(knowledge, f, indent=2)

    print(f"\nKnowledge base saved to {output_file}")
    return knowledge


def search_videos(query: str, knowledge: dict) -> list:
    """Search video transcripts for relevant content"""
    query_lower = query.lower()
    results = []

    for video_id, video_data in knowledge.get('videos', {}).items():
        transcript = video_data.get('transcript', '').lower()
        if query_lower in transcript:
            # Find relevant snippet
            idx = transcript.find(query_lower)
            start = max(0, idx - 100)
            end = min(len(transcript), idx + 200)
            snippet = transcript[start:end]

            results.append({
                'video_id': video_id,
                'title': video_data.get('title'),
                'url': video_data.get('url'),
                'snippet': f"...{snippet}..."
            })

    return results


if __name__ == "__main__":
    print("=== Divine Tribe YouTube Knowledge Builder ===\n")
    knowledge = build_knowledge_base()

    print("\n=== Test Search ===")
    results = search_videos("tcr", knowledge)
    for r in results:
        print(f"\nFound in: {r['title']}")
        print(f"URL: {r['url']}")
        print(f"Snippet: {r['snippet'][:150]}...")
