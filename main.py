import os
import time
import json
import subprocess
import random
import requests
from instagrapi import Client

# ===== CONFIG =====
VIDEO_FILE = "final_video.mp4"
IMAGE_FILE = "ai_image.jpg"
MUSIC_FILE = "ai_music.mp3"
POST_SCHEDULE = 86400  # 1 post every 24 hours

cl = Client()

# ===== LOGIN (COOKIE SESSION METHOD ONLY) =====
def ig_login():
    if os.path.exists("session.json"):
        print("✅ Loading Instagram session from cookies...")
        with open("session.json", "r") as f:
            cookies = json.load(f)
        try:
            cl.login_by_sessionid(cookies["sessionid"])
            print("✅ Session loaded successfully! (No login challenge)")
        except Exception as e:
            print(f"❌ Failed to load session: {e}")
            exit()
    else:
        print("❌ No session.json found! Please export your cookies (sessionid, csrftoken, ds_user_id).")
        exit()

# ===== IMAGE FETCH (Free Dark Poetic Images) =====
def generate_ai_image():
    print("🎨 Fetching sad/poetic image...")
    keywords = ["sad", "lonely", "moody", "rain", "poetic", "love"]
    query = random.choice(keywords)
    url = f"https://source.unsplash.com/1080x1920/?{query}"
    r = requests.get(url)
    with open(IMAGE_FILE, "wb") as f:
        f.write(r.content)
    print(f"✅ Image saved: {IMAGE_FILE}")

# ===== MUSIC GENERATION (Free Samples) =====
def generate_ai_music():
    print("🎵 Downloading AI music sample...")
    url = random.choice([
        "https://cdn.pixabay.com/download/audio/2023/01/26/audio_d29cb9bce2.mp3",
        "https://cdn.pixabay.com/download/audio/2023/01/27/audio_37c6f542b1.mp3"
    ])
    r = requests.get(url)
    with open(MUSIC_FILE, "wb") as f:
        f.write(r.content)
    print("✅ Music saved:", MUSIC_FILE)

# ===== VIDEO CREATION (FFmpeg) =====
def create_video():
    print("🎬 Creating video...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", IMAGE_FILE,
        "-i", MUSIC_FILE,
        "-vf", "zoompan=z='zoom+0.001':d=125,format=yuv420p",
        "-t", "15",
        "-pix_fmt", "yuv420p",
        VIDEO_FILE
    ]
    subprocess.run(cmd)
    print("✅ Video created:", VIDEO_FILE)

# ===== CAPTION + HASHTAG GENERATION (Lightweight Built-In) =====
def generate_caption():
    captions = [
        "i talk to the moon because you stopped listening",
        "hearts don’t break, they just keep beating with cracks inside",
        "sometimes loving means letting go, even if it kills you",
        "your ghost sleeps in my bed and i still make room for it",
        "the nights feel longer when you miss someone you can’t have"
    ]
    hashtags = [
        "#sadquotes", "#brokenhearts", "#poetic", "#lonely", "#lovehurts",
        "#deepsadness", "#romanticvibes", "#heartbreak"
    ]
    caption = random.choice(captions) + "\n\n" + " ".join(random.sample(hashtags, 5))
    print("✍️ Generated caption:", caption)
    return caption

# ===== POST TO INSTAGRAM =====
def post_instagram(video_file, caption):
    print("📤 Posting to Instagram...")
    cl.clip_upload(video_file, caption)
    print("✅ Post published successfully!")

# ===== MAIN BOT LOGIC =====
def run_once():
    generate_ai_image()
    generate_ai_music()
    create_video()
    caption = generate_caption()
    post_instagram(VIDEO_FILE, caption)

def run_forever():
    while True:
        run_once()
        print("⏳ Waiting for next scheduled post...")
        time.sleep(POST_SCHEDULE)

if __name__ == "__main__":
    ig_login()
    print("🚀 Running one-time test post immediately...")
    run_once()
    print("✅ Test post complete! Switching to daily auto-posting...")
    run_forever()
