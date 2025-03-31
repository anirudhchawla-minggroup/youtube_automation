import os
import tempfile
import whisper
import yt_dlp
from django.core.management.base import BaseCommand
import requests
import datetime
import re
from glob import glob
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve sensitive data from environment variables.
VIDEO_URL = os.getenv("VIDEO_URL", "https://www.youtube.com/watch?v=kMb7mM_vxWo")
WEB_APP_URL = os.getenv("WEB_APP_URL")
# OPENAI_API_KEY will be used in the summarize_text function

def download_audio(video_url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        video_id = info_dict.get("id", None)
        filename = os.path.join(output_dir, f"{video_id}.mp3")
    return filename

def transcribe_audio(audio_path):
    # Load Whisper model (choose model size as needed: tiny, base, small, etc.)
    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    return result["text"]

def summarize_text(text):
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    prompt = (
        "Please provide a summary which tells me what he is talking about market conditions, "
        "I just need market news summary in bullet points for the following text:\n\n"
        f"{text}\n\n"
        "Ensure that the summary is concise and formatted as bullet points. "
        "Also I need summary in chunks giving me start and end time of that chunk along with "
        "that youtube video link so if i click on that link video time starts from start time of that chunk."
    )
    
    response = openai.ChatCompletion.create(
        model="o3-mini",  # or any other model you prefer
        messages=[
            {"role": "user", "content": prompt}
        ],
    )
    
    summary_result = response.choices[0].message.content
    return summary_result

def update_google_sheet(summary_text, video_link, web_app_url):
    import re, datetime, requests

    def time_to_seconds(time_str):
        """Convert time in MM:SS format to seconds"""
        m, s = time_str.split(':')
        return int(m) * 60 + int(s)
    
    # Remove header and footer from the summary text if present.
    header_pattern = r'^.*?─────────────────────────────'
    footer_pattern = r'─────────────────────────────.*?$'
    clean_text = re.sub(header_pattern, '', summary_text, flags=re.DOTALL)
    clean_text = re.sub(footer_pattern, '', clean_text, flags=re.DOTALL)
    
    # Split by chunk separators (lines with dashes)
    chunks = re.split(r'(?:\r?\n)+─────────────────────────────(?:\r?\n)+', clean_text.strip())
    
    rows = []
    for chunk in chunks:
        if not chunk.strip():
            continue
            
        # Extract chunk information.
        # Expected format: 
        # "Chunk 1: <Title> (<start>:<sec>–<end>:<sec>)"
        # Followed by bullet points (lines starting with •) 
        # and a Link line that we want to ignore.
        chunk_match = re.match(
            r'Chunk \d+: (.*?) \((\d+:\d+)[–-](\S+)\)\s*((?:•.*(?:\n|$))+)',
            chunk.strip(),
            re.DOTALL
        )
        
        if chunk_match:
            title = chunk_match.group(1).strip()
            start_time = chunk_match.group(2).strip()
            end_time = chunk_match.group(3).strip()
            bullet_points = chunk_match.group(4).strip()
            
            # Remove any trailing Link line from the bullet points.
            bullet_points = re.sub(r'\s*Link: https?://\S+\s*$', '', bullet_points, flags=re.DOTALL)
            
            # Create timestamped video link using start time.
            start_seconds = time_to_seconds(start_time)
            summary_part_link = f"{video_link}&t={start_seconds}s"
            
            # Get today's date.
            video_date = datetime.datetime.now().strftime("%Y-%m-%d")
            duration_of_summary = f"{start_time} - {end_time}"
            
            # Create a row for this chunk.
            row = [
                video_date,
                video_link,
                title,
                bullet_points,
                duration_of_summary,
                summary_part_link
            ]
            rows.append(row)
            print(f"Processed chunk: {title} ({duration_of_summary})")
    
    if not rows:
        print("No valid chunks found in the summary text.")
        return
    
    # Send all rows to Google Sheets via the web app.
    payload_all = {"rows": rows}
    response = requests.post(web_app_url, json=payload_all)
    
    if response.ok:
        print(f"Successfully added {len(rows)} rows to Google Sheet")
        for i, row in enumerate(rows, 1):
            print(f"Row {i}: {row[2]} ({row[4]})")
    else:
        print("Failed to add rows. Response:", response.text)

def time_to_seconds(time_str):
    """Convert time in MM:SS format to seconds"""
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)

class Command(BaseCommand):
    help = "Process YouTube video transcription and update Google Sheet with summary chunks."

    def handle(self, *args, **options):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Uncomment the following to download and transcribe audio if needed:
            # print("Downloading audio to temporary directory...")
            # audio_file = download_audio(VIDEO_URL, temp_dir)
            # print("Audio downloaded to:", audio_file)
            # print("Transcribing audio with Whisper...")
            # transcript = transcribe_audio(audio_file)
            # with open("transcript.txt", "w", encoding="utf-8") as file:
            #     file.write(transcript)
            
            # Read transcript from file
            with open("transcript.txt", "r", encoding="utf-8") as file:
                transcript = file.read()
            
            # Check if summary.txt exists and has data; otherwise, generate it.
            if os.path.exists("summary.txt") and os.path.getsize("summary.txt") > 0:
                with open("summary.txt", "r", encoding="utf-8") as file:
                    summary = file.read()
                print("\nSummary loaded from summary.txt:")
                print(summary)
            else:
                summary = summarize_text(transcript)
                print("\nSummary (bullet points) generated:")
                print(summary)
                with open("summary.txt", "w", encoding="utf-8") as file:
                    file.write(summary)
            
            video_link = VIDEO_URL
            # WEB_APP_URL is loaded from the environment.
            
            # Update the Google Sheet with summary chunks.
            update_google_sheet(summary, video_link, WEB_APP_URL)
            print("\nSummary parts appended to Google Sheet.")
