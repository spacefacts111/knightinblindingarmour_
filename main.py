import os
import time
import json
from instagrapi import Client
from PIL import Image
from diffusers import StableDiffusionPipeline
import torch
import subprocess
import random
from gpt4all import GPT4All
import requests

# ===== CONFIG =====
VIDEO_FILE = "final_video.mp4"
IMAGE_FILE = "ai_image.png"
MUSIC_FILE = "ai_music.wav"
CAPTIONS_MODEL = "ggml-gpt4all-j-v1.3-groovy"
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

# ===== AI IMAGE GENERATION (Stable Diffusion) =====
def generate_ai_image(prompt="sad romantic poetry, soft lighting, emotional vibe"):
    print("🎨 Generating AI image...")
    pipe = StableDiffusionPipeline.from_pretrained(
        "runwayml/stable-diffusion-v1-5", torch_dtype=torch.float32
    )
    image = pipe(prompt).images[0]
    image.save(IMAGE_FILE)
    print("✅ Image saved:", IMAGE_FILE)

# ===== AI MUSIC GENERATION (Free Riffusion Samples) =====
def generate_ai_music():
    print("🎵 Generating AI music...")
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

# ===== CAPTION + HASHTAG GENERATION (PURE GPT4All) =====
def generate_caption():
    print("✍️ Generating caption...")
    model = GPT4All(CAPTIONS_MODEL)
    prompt = "Write me a short, sad, poetic, romantic Instagram caption with 5-10 popular sad or romantic hashtags."
    output = model.generate(prompt, max_tokens=60)
    return output.strip()

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
