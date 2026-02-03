#!/bin/bash
# Generate YouTube video notes
# Usage: ./youtube_notes.sh "VIDEO_URL"

VIDEO_URL="$1"
NOTES_DIR="/root/.openclaw/workspace/notes"

if [ -z "$VIDEO_URL" ]; then
    echo "Usage: $0 <youtube-url>"
    exit 1
fi

mkdir -p "$NOTES_DIR"

echo "Getting video info..."
VIDEO_INFO=$(yt-dlp --dump-json "$VIDEO_URL" 2>/dev/null)
TITLE=$(echo "$VIDEO_INFO" | jq -r '.title' | sed 's/[^a-zA-Z0-9]//g' | head -c 50)
DATE=$(date +%Y-%m-%d)
OUTPUT_FILE="$NOTES_DIR/${TITLE}-${DATE}.md"

echo "Downloading subtitles..."
cd "$NOTES_DIR"
if ! yt-dlp --write-subs --sub-langs "en,zh-Hans" --skip-download "$VIDEO_URL" -o "%(title)s" 2>/dev/null; then
    echo "No subtitles available, using metadata only"
fi

echo "Notes saved to: $OUTPUT_FILE"
echo "TODO: Use LLM to analyze subtitles and generate detailed notes"
