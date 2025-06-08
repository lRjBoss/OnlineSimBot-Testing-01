from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import subprocess
import whisper
import argostranslate.translate
from piper import PiperVoice
import os

# Telegram Bot Token (इसे @BotFather से लें)
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# Piper TTS Hindi Model
VOICE_MODEL = "hindi_model.onnx"
VOICE_CONFIG = "hindi_config.json"

# Step 1: Video Download करें
async def download_video(update: Update, url: str):
    await update.message.reply_text("📥 Video download कर रहा हूँ...")
    cmd = f"yt-dlp -f 'bestvideo[ext=mp4]+bestaudio[ext=m4a]' -o 'input_video.%(ext)s' {url}"
    subprocess.run(cmd, shell=True, check=True)
    return "input_video.mp4"

# Step 2: Audio निकालें और Transcribe करें
async def transcribe_audio(video_path: str):
    audio_path = "audio.wav"
    subprocess.run(f"ffmpeg -i {video_path} -vn -acodec pcm_s16le -ar 16000 -ac 1 {audio_path}", shell=True)
    
    model = whisper.load_model("medium")
    result = model.transcribe(audio_path, language="ja")  # जापानी के लिए
    return result["text"]

# Step 3: Hindi में Translate करें
async def translate_to_hindi(text: str):
    # Japanese -> English
    translated_en = argostranslate.translate.translate(text, "ja", "en")
    # English -> Hindi
    translated_hi = argostranslate.translate.translate(translated_en, "en", "hi")
    return translated_hi

# Step 4: Hindi Audio Generate करें
async def generate_hindi_audio(text: str, output_path="dub_audio.wav"):
    voice = PiperVoice.load(VOICE_MODEL, config_path=VOICE_CONFIG)
    audio = voice.synthesize(text)
    with open(output_path, "wb") as f:
        f.write(audio)

# Step 5: नया Video बनाएँ
async def merge_video_audio(original_video: str, output_video="output.mp4"):
    cmd = f"ffmpeg -i {original_video} -i dub_audio.wav -c:v copy -map 0:v:0 -map 1:a:0 {output_video}"
    subprocess.run(cmd, shell=True)

# Step 6: Telegram Bot Handlers
async def start(update: Update, context):
    await update.message.reply_text("नमस्ते! किसी भी एनीमे/मूवी का YouTube लिंक भेजें, मैं उसे हिंदी डब करके दूंगा!")

async def handle_video_link(update: Update, context):
    url = update.message.text
    
    try:
        # सारे steps एक साथ
        video_path = await download_video(update, url)
        transcript = await transcribe_audio(video_path)
        hindi_text = await translate_to_hindi(transcript)
        await generate_hindi_audio(hindi_text)
        await merge_video_audio(video_path)
        
        # Final video भेजें
        await update.message.reply_video(video=open("output.mp4", "rb"), caption="ये रहा आपका हिंदी डब वीडियो! 😊")
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# Bot शुरू करें
def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_video_link))
    
    application.run_polling()

if __name__ == "__main__":
    main()