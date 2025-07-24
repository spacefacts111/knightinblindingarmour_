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

# ===== LOGIN (COOKIES ONLY) =====
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
        print("❌ No session.json found! Create one with your IG cookies.")
        exit()

# ===== FETCH SAD/POETIC IMAGE =====
def generate_image():
    print("🎨 Fetching image...")
    keywords = ["sad", "poetic", "love", "lonely", "heartbreak", "rain"]
    query = random.choice(keywords)
    url = f"https://source.unsplash.com/1080x1920/?{query}"
    r = requests.get(url)
    with open(IMAGE_FILE, "wb") as f:
        f.write(r.content)
    print(f"✅ Image saved: {IMAGE_FILE}")

# ===== MUSIC DOWNLOAD =====
def generate_music():
    print("🎵 Downloading music...")
    url = random.choice([
        "https://cdn.pixabay.com/download/audio/2023/01/26/audio_d29cb9bce2.mp3",
        "https://cdn.pixabay.com/download/audio/2023/01/27/audio_37c6f542b1.mp3"
    ])
    r = requests.get(url)
    with open(MUSIC_FILE, "wb") as f:
        f.write(r.content)
    print(f"✅ Music saved: {MUSIC_FILE}")

# ===== CREATE VIDEO (FIXED ENCODING) =====
def create_video():
    print("🎬 Creating video...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", IMAGE_FILE,
        "-i", MUSIC_FILE,
        "-vf", "scale=720:1280,zoompan=z='zoom+0.001':d=125,format=yuv420p",
        "-t", "15",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        VIDEO_FILE
    ]
    subprocess.run(cmd)
    if os.path.exists(VIDEO_FILE):
        print(f"✅ Video created: {VIDEO_FILE}")
    else:
        print("❌ Video was not created properly.")
        exit()

# ===== CAPTION + HASHTAG GENERATION =====
def generate_caption():
    captions = [
        "i talk to the moon because you stopped listening",
        "hearts don’t break, they just keep beating with cracks inside",
        "sometimes loving means letting go, even if it kills you",
        "your ghost sleeps in my bed and i still make room for it",
        "the nights feel longer when you miss someone you can’t have",
        "she left, but her perfume stayed in my lungs",
        "his smile was the saddest thing i ever loved"
    ]
    hashtags = [
        "#sadquotes", "#brokenhearts", "#poetic", "#lonely", "#lovehurts",
        "#deepsadness", "#romanticvibes", "#heartbreak", "#lostlove", "#relatable"
    ]
    return random.choice(captions) + "\n\n" + " ".join(random.sample(hashtags, 6))

# ===== POST TO INSTAGRAM (CHECK + DELAY) =====
def post_instagram(video_file, caption):
    print("📤 Preparing to post...")
    time.sleep(3)  # Give Railway time to finalize the file
    if not os.path.exists(video_file):
        print("❌ Video file not found, cannot upload.")
        exit()
    print("📤 Posting to Instagram...")
    cl.clip_upload(video_file, caption)
    print("✅ Post published successfully!")

# ===== BOT LOGIC =====
def run_once():
    generate_image()
    generate_music()
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
