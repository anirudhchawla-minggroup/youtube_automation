import os
import re
import feedparser
import requests
from django.core.management.base import BaseCommand
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Configuration - Set these in your environment or Django settings
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # e.g. "xoxb-..."
SLACK_CHANNEL = "C07NQ9E7G5S"  # Change to your Slack channel ID

# File to store the last processed video ID
LAST_VIDEO_FILE = Path(__file__).parent.parent.parent / "last_video.txt"

class Command(BaseCommand):
    help = "Checks for new YouTube videos and notifies Slack"

    def handle(self, *args, **options):
        try:
            self.check_for_new_video()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

    def get_latest_video(self):
        """Gets latest video from RSS feed"""
        handle = 'UCAHr-sT0AjrD3sBwr1eRUNg'
        print(f'handledd {handle}')
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={handle}"
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            raise ValueError("No videos found in RSS feed")
        
        latest = feed.entries[0]
        return {
            'id': latest.yt_videoid,
            'title': latest.title,
            'link': latest.link,
            'published': latest.published
        }

    def read_last_video(self):
        """Reads last processed video ID"""
        if LAST_VIDEO_FILE.exists():
            return LAST_VIDEO_FILE.read_text().strip()
        return None

    def write_last_video(self, video_id):
        """Stores the last processed video ID"""
        LAST_VIDEO_FILE.write_text(video_id)

    def send_slack_notification(self, video_info):
        print(f'SLACK_BOT_TOKEN {SLACK_BOT_TOKEN}')
        """Sends notification to Slack"""
        message = (
            f"New video uploaded: *{video_info['title']}*\n"
            #f"Published: {video_info['published']}\n"
            f"Link: {video_info['link']}"
        )
        
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": SLACK_CHANNEL,
            "text": message,
            "unfurl_links": True
        }
        
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers=headers,
            json=payload
        )
        
        if not response.ok:
            raise ValueError(f"Slack API error: {response.text}")

    def check_for_new_video(self):
        """Main logic to check for new videos"""
        self.stdout.write("Checking for new videos...")
        
        # Get video info
        latest_video = self.get_latest_video()
        last_video_id = self.read_last_video()
        
        self.stdout.write(f"Latest video ID: {latest_video['id']}")
        self.stdout.write(f"Last processed ID: {last_video_id or 'None'}")
        
        # Compare with last processed video
        if latest_video['id'] != last_video_id:
            self.stdout.write(self.style.SUCCESS("New video found!"))
            self.send_slack_notification(latest_video)
            self.write_last_video(latest_video['id'])
            self.stdout.write("Notification sent and video ID stored")
        else:
            self.stdout.write("No new videos found")