import os
import re
import feedparser
import requests
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

load_dotenv()
# Configuration - Set these in your environment or Django settings
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")  # e.g. "xoxb-..."
SLACK_CHANNEL = "C0845F94RD0"  # Change to your Slack channel ID
# Google Apps Script URL for persisting the last video ID
G_SCRIPT_URL = os.getenv("G_SCRIPT_URL")  # e.g. "https://script.google.com/macros/s/your_deployment_id/exec"

class Command(BaseCommand):
    help = "Checks for new YouTube videos and notifies Slack using persistent state from Google Apps Script"

    def handle(self, *args, **options):
        try:
            self.check_for_new_video()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))

    def get_latest_video(self):
        """Gets latest video from RSS feed. For this example we hardcode a channel ID."""
        # Here you can either hardcode the channel ID or retrieve it dynamically.
        # For example, 'UCAHr-sT0AjrD3sBwr1eRUNg' is used as a placeholder.
        channel_id = 'UCAHr-sT0AjrD3sBwr1eRUNg'
        self.stdout.write(f"Using channel ID: {channel_id}")
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
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
        """Retrieves the last processed video ID from the Google Apps Script persistent store."""
        if not G_SCRIPT_URL:
            raise ValueError("G_SCRIPT_URL environment variable not set")
        # GET request with ?action=get to the Google Apps Script web app.
        url = f"{G_SCRIPT_URL}?action=get"
        response = requests.get(url)
        if not response.ok:
            raise ValueError(f"Error retrieving last video ID: {response.text}")
        data = response.json()
        # Expecting a JSON payload like: {"lastVideoId": "XYZ"}
        return data.get("lastVideoId", None)

    def write_last_video(self, video_id):
        """Updates the last processed video ID via the Google Apps Script persistent store."""
        if not G_SCRIPT_URL:
            raise ValueError("G_SCRIPT_URL environment variable not set")
        payload = {"videoId": video_id}
        response = requests.post(G_SCRIPT_URL, json=payload)
        if not response.ok:
            raise ValueError(f"Error updating last video ID: {response.text}")

    def send_slack_notification(self, video_info):
        """Sends notification to Slack about the new video."""
        message = (
            f"New video uploaded: *{video_info['title']}*\n"
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
        """Main logic to check for new videos and notify Slack."""
        self.stdout.write("Checking for new videos...")
        
        # Get video info from the RSS feed.
        latest_video = self.get_latest_video()
        last_video_id = self.read_last_video()
        
        self.stdout.write(f"Latest video ID: {latest_video['id']}")
        self.stdout.write(f"Last processed ID: {last_video_id or 'None'}")
        
        # Compare with last processed video
        if latest_video['id'] != last_video_id:
            self.stdout.write(self.style.SUCCESS("New video found!"))
            self.send_slack_notification(latest_video)
            self.write_last_video(latest_video['id'])
            self.stdout.write("Notification sent and video ID updated in persistent store")
        else:
            self.stdout.write("No new videos found")

