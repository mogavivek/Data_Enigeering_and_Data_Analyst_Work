import requests
import json
import polars as pl # polars is the faster version of pandas


# define url API
channel_url = "https://www.youtube.com/@OpenAI/videos"

# Initialize to so store the video data
video_record_list=[]