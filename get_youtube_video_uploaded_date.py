import requests
import re

API_URL = "https://www.youtube.com/youtubei/v1/browse?prettyPrint=false"

# Headers copied from your browser request; update values as needed.
headers = {
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8,de;q=0.7",
    "authorization": "SAPISIDHASH 1741340171_8eeb5b332f0deada9f4e102861c83108079c4ea3_u SAPISID1PHASH 1741340171_8eeb5b332f0deada9f4e102861c83108079c4ea3_u SAPISID3PHASH 1741340171_8eeb5b332f0deada9f4e102861c83108079c4ea3_u",
    "content-type": "application/json",
    "cookie": (
        "PREF=f6=40000000&f7=100&tz=Europe.Berlin&f4=4000000; "
        "NID=520=GEd5G3QT12DxyjEPgx-3xYBVipLCrSAQYGZKAf2giO0Oc8RygvdqM-c0E2EvHYKPJgnV9IFcdVoCZuxk7fWpyfoV3FgjJJTp33SpAfNjHOBBgdITNIIUzcxPhJxJP8xAc4nFrnazQ9iIMLYiEcvnEWcn5-HZ1RBVrPaeqoXmKtiHc_fu28pGkrsCRii3KQtpM9tu0z2VyI0U3PD0cX5g6vlgeOtImZzp5ByUodDk_2BVpLw0VKbIiQGcpi2Fe-vP_Z1mCniuZzp_Z_U9VKPoSHyK3kiXk2jztEjBj6TpMxWqfHgob2yCdZqfmSTeAxTjn6QaMa5Ec7UUxo9VzDU4C-rVBnp5t_boq1betqA; "
        "LOGIN_INFO=AFmmF2swRQIhAKpNsdS67rqznkXxNF40lZ3Falc9wsQO9DUTxSKIdwbCAiBhj51g49L_UFE9NHIDKySOAl1Ti6MH6Fs-hIUG7aScqQ:QUQ3MjNmd0d1dWluU0cwYmhzXzFxN0VKcTNBRVFHRWZYbWNpV1Y0UkdZQ2RRaDI5UVhOUzNyeWJkTk9NV3A3Tm5Kb1MyY1hfNll3TXVRTWJSTXBfbzZ5eTRCaks0a2Y3ZHBfeFVzVTJMaGg1Mko0REJ5Z1pqMkZRamJYNnY5QmdDNjFQRzg2RlZnazhXNG12eXZHSVJ0UWtuQ3prb1ZBd1J3; "
        "origin=https://www.youtube.com; "
        "referer=https://www.youtube.com/@MarkMeldrum/videos; "
        "sec-ch-ua=\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"; "
        "sec-ch-ua-arch=arm; "
        "sec-ch-ua-bitness=64; "
        "sec-ch-ua-form-factors=Desktop; "
        "sec-ch-ua-full-version=133.0.6943.142; "
        "sec-ch-ua-full-version-list=\"Not(A:Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"133.0.6943.142\", \"Chromium\";v=\"133.0.6943.142\"; "
        "sec-ch-ua-mobile=?0; "
        "sec-ch-ua-model=\"\"; "
        "sec-ch-ua-platform=macOS; "
        "sec-ch-ua-platform-version=14.5.0; "
        "sec-ch-ua-wow64=?0; "
        "sec-fetch-dest=empty; "
        "sec-fetch-mode=same-origin; "
        "sec-fetch-site=same-origin; "
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.142 Safari/537.36; "
        "x-client-data=CIS2yQEIo7bJAQipncoBCIj5ygEIlqHLAQj/ossBCIagzQEIusjNAQiA1s4BCODXzgEIyNzOAQjY4s4BCIPkzgEIruTOAQjg5M4BGPTJzQE=; "
        "x-goog-authuser=0; "
        "x-goog-visitor-id=CgtQcU1zZEpnQTdjUSjE-aq-BjIKCgJERRIEEgAgRA%3D%3D; "
        "x-origin=https://www.youtube.com; "
        "x-youtube-bootstrap-logged-in=true; "
        "x-youtube-client-name=1; "
        "x-youtube-client-version=2.20250304.01.00"
    ),
    "origin": "https://www.youtube.com",
    "referer": "https://www.youtube.com/@MarkMeldrum/videos",
    "sec-ch-ua": "\"Not(A:Brand\";v=\"99\", \"Google Chrome\";v=\"133\", \"Chromium\";v=\"133\"",
    "sec-ch-ua-arch": "arm",
    "sec-ch-ua-bitness": "64",
    "sec-ch-ua-form-factors": "Desktop",
    "sec-ch-ua-full-version": "133.0.6943.142",
    "sec-ch-ua-full-version-list": "\"Not(A:Brand\";v=\"99.0.0.0\", \"Google Chrome\";v=\"133.0.6943.142\", \"Chromium\";v=\"133.0.6943.142\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": "",
    "sec-ch-ua-platform": "macOS",
    "sec-ch-ua-platform-version": "14.5.0",
    "sec-ch-ua-wow64": "?0",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "same-origin",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.6943.142 Safari/537.36",
    "x-client-data": "CIS2yQEIo7bJAQipncoBCIj5ygEIlqHLAQj/ossBCIagzQEIusjNAQiA1s4BCODXzgEIyNzOAQjY4s4BCIPkzgEIruTOAQjg5M4BGPTJzQE=",
    "x-goog-authuser": "0",
    "x-goog-visitor-id": "CgtQcU1zZEpnQTdjUSjE-aq-BjIKCgJERRIEEgAgRA%3D%3D",
    "x-origin": "https://www.youtube.com",
    "x-youtube-bootstrap-logged-in": "true",
    "x-youtube-client-name": "1",
    "x-youtube-client-version": "2.20250304.01.00"
}

# Initial payload for the channel (using its browseId)
payload = {
    "context": {
        "client": {
            "clientName": "WEB",
            "clientVersion": "2.20250304.01.00"
        }
    },
    "browseId": "UCAHr-sT0AjrD3sBwr1eRUNg"
}

TARGET_YEAR = 2024

def extract_video_items(data):
    """
    Extract the list of video items from the API response.
    Adjust this function if YouTube changes its JSON structure.
    """
    try:
        items = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0] \
                     ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0] \
                     ["itemSectionRenderer"]["contents"]
    except Exception as e:
        print("Error extracting items:", e)
        items = []
    return items

def extract_continuation(data):
    """
    Extract the continuation token for pagination.
    """
    try:
        continuation = data["contents"]["twoColumnBrowseResultsRenderer"]["tabs"][0] \
                          ["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0] \
                          ["itemSectionRenderer"]["contents"][-1]["continuationItemRenderer"]["continuationEndpoint"] \
                          ["continuationCommand"]["token"]
        return continuation
    except Exception:
        return None

def video_published_in_2024(item):
    """
    Determine if the video item appears to have been published in 2024.
    This example checks for the substring "2024" in the publishedTimeText.
    """
    try:
        published_text = item.get("videoRenderer", {}).get("publishedTimeText", {}).get("simpleText", "")
        if "2024" in published_text:
            return True
    except Exception as e:
        print("Error checking published year:", e)
    return False

def extract_videos_2024(items):
    """
    Filter the list of video items to only include those published in 2024.
    """
    videos = []
    for item in items:
        if "videoRenderer" in item and video_published_in_2024(item):
            videos.append(item)
    return videos

def main():
    all_videos_2024 = []
    continuation = None
    session = requests.Session()

    while True:
        if continuation:
            payload["continuation"] = continuation
        else:
            payload.pop("continuation", None)

        response = session.post(API_URL, headers=headers, json=payload)
        print(f'response22 {response.content}')
        if response.status_code != 200:
            print("Error:", response.status_code)
            break

        data = response.json()
        items = extract_video_items(data)
        videos_2024 = extract_videos_2024(items)
        all_videos_2024.extend(videos_2024)
        print(f"Fetched {len(items)} items, found {len(videos_2024)} videos from 2024, total so far: {len(all_videos_2024)}")

        continuation = extract_continuation(data)
        if not continuation:
            print("Reached end of results.")
            break

    print(f"\nTotal videos from 2024: {len(all_videos_2024)}")
    for video in all_videos_2024:
        video_id = video["videoRenderer"].get("videoId")
        print(f"https://www.youtube.com/watch?v={video_id}")

if __name__ == "__main__":
    main()
