import feedparser
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "List all YouTube video links published in 2024 for a given channel."

    def handle(self, *args, **options):
        CHANNEL_ID = "UCAHr-sT0AjrD3sBwr1eRUNg"
        RSS_URL = f"https://www.youtube.com/feeds/videos.xml?channel_id={CHANNEL_ID}"
        TARGET_YEAR = 2024

        def get_videos_published_in_year(year):
            feed = feedparser.parse(RSS_URL)
            video_links = []
            for entry in feed.entries:
                # Check if the published_parsed attribute exists and matches the target year
                if hasattr(entry, "published_parsed") and entry.published_parsed.tm_year == year:
                    video_links.append(entry.link)
            return video_links

        videos = get_videos_published_in_year(TARGET_YEAR)
        if videos:
            self.stdout.write(f"Videos published in {TARGET_YEAR}:")
            for link in videos:
                self.stdout.write(link)
        else:
            self.stdout.write(f"No videos found for the year {TARGET_YEAR}.")
