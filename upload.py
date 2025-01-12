# from twelvelabs import TwelveLabs
# from twelvelabs.models.task import Task

# def upload_video(file):
#     client = TwelveLabs(api_key="API_KEY")

#     task = client.task.create(
#       index_id="670c03c94f6c89db01c65be5",
#       file = file         #"./data/merged_video.mp4"
#     )
      
#     return task.video_id 


# def download_youtube_video(url, path=""):
#     # Use yt-dlp to download video
#     import yt_dlp
#     ydl_opts = {
#         'format': 'best',
#         'outtmpl': f'{path}/%(title)s.%(ext)s',  # Save the video title as filename
#     }
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.download([url])
#     print("Video download completed!")


import os
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task
import yt_dlp



from dotenv import load_dotenv


# Load .env file
load_dotenv()

def download_and_upload_video(youtube_url, api_key=os.getenv("TWELVE_LABS_KEY"), index_id=os.getenv("INDEX_ID"), path="./temp_video"):
    # Create a TwelveLabs client
    client = TwelveLabs(api_key=api_key)

    # Download the YouTube video
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{path}/%(title)s.%(ext)s',  # Save the video title as filename
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([youtube_url])
    
    print("Video download completed!")

    # Get the downloaded video path (assuming only one video is downloaded)
    downloaded_video_path = next((f for f in os.listdir(path) if f.endswith(('.mp4', '.mkv', '.webm'))), None)
    if not downloaded_video_path:
        raise FileNotFoundError("No video file found in the download directory.")

    # Upload the video to Twelve Labs
    file_path = os.path.join(path, downloaded_video_path)
    task = client.task.create(
        index_id=index_id,
        file=file_path
    )

    print(f"Video uploaded successfully. Video ID: {task.video_id}")

    # Delete the downloaded video file
    os.remove(file_path)
    print(f"Temporary video file {file_path} deleted.")

# Example usage
# download_and_upload_video("https://youtu.be/Qf6OVR8MLnU?si=5fA3ojCw_zzo97FM")
