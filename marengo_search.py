
from twelvelabs import TwelveLabs
import json
import requests
import os
from moviepy import *
from dotenv import load_dotenv
from moviepy import VideoFileClip

# Load .env file
load_dotenv()

class TwelveLabsSearch:
    # Initialize the TwelveLabs client once in the constructor
    def __init__(self):
        self.api_key = os.getenv("TWELVE_LABS_KEY")
        # import pdb; pdb.set_trace()
        self.client = TwelveLabs(api_key=self.api_key)

    @staticmethod
    def save_json(query_results, file_name):
        # Save the data as a list of lists of JSON objects
        with open(file_name, 'w') as json_file:
            json.dump(query_results, json_file, indent=4)

    def query(self, query_text_list, file_name=None):
        all_results = []  # List of lists of dictionaries

        for query_text in query_text_list:
            search_results = self.client.search.query(
                index_id=os.getenv("INDEX_ID"),
                query_text=query_text,
                # query={"text": query_text},
                
                # query = {
                #     "$not": {
                #         "origin": {
                #             "text": query_text
                #         },
                #         "sub": {
                #             "$or": [
                #                 {
                #                     "text": "News Anchor"
                #                 },
                #                 {
                #                     "text": "Podcast"
                #                 }
                #             ]
                #         }
                #     }
                # },

                options=["visual","audio"]
            )
            
            query_result = []  # List of dictionaries for this query
            while True:
                
                try:
                    # Retrieve each page of search results
                    page_data = next(search_results)
                    for clip in page_data:  # Limiting to 3 results per page
                        query_result.append({
                            "video_id": clip.video_id,
                            "score": clip.score,
                            "start": clip.start,
                            "end": clip.end,
                            "confidence": clip.confidence,
                            # "metadata": clip.metadata,
                        })
                except StopIteration:
                    break
            all_results.append(query_result)  # Append this query's results as a list

        if file_name:
            self.save_json(all_results, file_name)

        return all_results  # List of lists of dictionaries
    
    @staticmethod
    def get_video_info(video_id):
        api_key= os.getenv("TWELVE_LABS_KEY")

        index_id=os.getenv("INDEX_ID")
        url = f"https://api.twelvelabs.io/v1.3/indexes/{index_id}/videos/{video_id}"
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }
        
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            video_info = response.json()  # Parse response as JSON
            return video_info
        elif response.status_code == 400:
            print("The request has failed. Check your parameters.")
            return None
        else:
            print(f"Error: Status code {response.status_code}")
            return None

            
    def search_video(query):
        query_text_list = [
        query,
        ]
        
        file_name = "data/data.json"
        
        searcher = TwelveLabsSearch()
        # Call with a list of queries and a file name to save the combined results as JSON
        results = searcher.query(query_text_list, file_name=file_name)
        
        # import pdb; pdb.set_trace()
        video_info = TwelveLabsSearch.get_video_info(video_id=results[0][0]['video_id'])
        video_url = video_info['hls']['video_url']
        # import pdb; pdb.set_trace()  
        searcher.download_and_crop_video(video_url,'extracted_clip.mp4')#, results[0][0]['start'], results[0][0]['end'])
        return ('extracted_clip.mp4', results[0][0]['start'])



def download_and_crop_video(video_url, output_path):   #, start_time, end_time):
    try:
        print(f"Loading video from {video_url}...")
        
        # Load the video directly from the URL using MoviePy
        clip = VideoFileClip(video_url)
        
        # print(f"Cropping video from {start_time} to {end_time} seconds...")
        
        # Extract the subclip
        # subclip = clip.subclip(start_time, end_time)
        
        # Write the subclip to the output file
        clip.write_videofile(output_path, codec="libx264")
        
        print(f"Video cropped successfully and saved to {output_path}")
    
    except Exception as e:
        print("Error processing video:", str(e))
        
    finally:
        # Close the clips to release resources
        if 'clip' in locals():
            clip.close()
        # if 'subclip' in locals():
        #     subclip.close()