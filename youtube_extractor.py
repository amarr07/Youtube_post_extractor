"""
YouTube Data API v3 Video Scraper
This script fetches videos from specified YouTube channels and saves the data to an Excel file.
"""

import os
from datetime import datetime, timezone
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openpyxl
from typing import List, Dict, Optional, Any

# YouTube Data API v3 Configuration
API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # Get API key from environment variable
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Target channel IDs
CHANNEL_IDS = [
    "UCy8qn0KvqhhaD86yBJzpeDQ",
    "UCuK4jszmhyLs-DvHyT3txgA",
    "UC3Uz2h9JD6Ac7LvuJUNQ9bg",
    "UCC0bFdwsgiA-roI9M4DTKXw",
    "UC-qeNGhgJkhWyJ5DGBZJF5w",
    "UCGS0EgqqGl1HosGfiq51cVg"
]

# Date range for video search
START_DATE = "2025-09-16"
END_DATE = "2025-09-28"


class YouTubeDataExtractor:
    def __init__(self, api_key: str):
        """Initialize YouTube Data API client."""
        self.api_key = api_key
        self.youtube = None
        self._initialize_client()
    
    def _initialize_client(self) -> None:
        """Initialize the YouTube API client."""
        try:
            self.youtube = build(
                YOUTUBE_API_SERVICE_NAME,
                YOUTUBE_API_VERSION,
                developerKey=self.api_key
            )
            print("YouTube API client initialized successfully.")
        except Exception as e:
            print(f"Error initializing YouTube API client: {e}")
            raise
    
    def get_videos_from_channel(
        self,
        channel_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Fetch all videos from a channel within the specified date range.
        
        Args:
            channel_id: YouTube channel ID
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of video data dictionaries
        """
        videos = []
        next_page_token = None
        
        # Convert dates to RFC 3339 format
        start_datetime = f"{start_date}T00:00:00Z"
        end_datetime = f"{end_date}T23:59:59Z"
        
        try:
            while True:
                # Search for videos in the channel within date range
                search_response = self.youtube.search().list(
                    part="id,snippet",
                    channelId=channel_id,
                    maxResults=50,
                    order="date",
                    publishedAfter=start_datetime,
                    publishedBefore=end_datetime,
                    type="video",
                    pageToken=next_page_token
                ).execute()
                
                for item in search_response.get("items", []):
                    video_id = item["id"]["videoId"]
                    video_data = {
                        "video_id": video_id,
                        "channel_id": channel_id,
                        "original_title": item["snippet"]["title"],
                        "published_at": item["snippet"]["publishedAt"],
                    }
                    videos.append(video_data)
                
                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    break
                    
        except HttpError as e:
            if e.resp.status == 403:
                print(f"API quota exceeded for channel {channel_id}")
            else:
                print(f"HTTP Error for channel {channel_id}: {e}")
        except Exception as e:
            print(f"Error fetching videos from channel {channel_id}: {e}")
        
        print(f"Found {len(videos)} videos from channel {channel_id}")
        return videos
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Fetch detailed statistics and information for a specific video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary containing video statistics and details
        """
        try:
            video_response = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()
            
            if not video_response.get("items"):
                print(f"No details found for video {video_id}")
                return {}
            
            video_item = video_response["items"][0]
            snippet = video_item.get("snippet", {})
            statistics = video_item.get("statistics", {})
            
            return {
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
                "channel_name": snippet.get("channelTitle", "")
            }
            
        except HttpError as e:
            if e.resp.status == 403:
                print(f"API quota exceeded for video {video_id}")
            else:
                print(f"HTTP Error for video {video_id}: {e}")
            return {}
        except Exception as e:
            print(f"Error fetching details for video {video_id}: {e}")
            return {}
    
    def extract_all_videos(
        self,
        channel_ids: List[str],
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """
        Extract all videos from multiple channels within date range.
        
        Args:
            channel_ids: List of YouTube channel IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            
        Returns:
            List of complete video data dictionaries
        """
        all_videos = []
        
        for channel_id in channel_ids:
            print(f"Processing channel: {channel_id}")
            channel_videos = self.get_videos_from_channel(
                channel_id, start_date, end_date
            )
            
            # Get detailed statistics for each video
            for video in channel_videos:
                video_details = self.get_video_details(video["video_id"])
                video.update(video_details)
                
                # Add missing fields with default values
                video.setdefault("translated_title", "")
                video.setdefault("view_count", 0)
                video.setdefault("like_count", 0)
                video.setdefault("comment_count", 0)
                video.setdefault("channel_name", "")
                
                # Format the date
                try:
                    date_obj = datetime.fromisoformat(
                        video["published_at"].replace("Z", "+00:00")
                    )
                    video["date"] = date_obj.strftime("%Y-%m-%d")
                except Exception as e:
                    print(f"Error formatting date for video {video['video_id']}: {e}")
                    video["date"] = ""
                
                all_videos.append(video)
        
        return all_videos


def save_to_excel(data: List[Dict[str, Any]], filename: str) -> None:
    """
    Save video data to an Excel file with specified column order.
    
    Args:
        data: List of video data dictionaries
        filename: Output Excel filename
    """
    if not data:
        print("No data to save.")
        return
    
    # Define column order as specified
    columns = [
        "date",
        "video_id",
        "channel_id",
        "original_title",
        "translated_title",
        "published_at",
        "view_count",
        "like_count",
        "comment_count",
        "channel_name"
    ]
    
    # Create DataFrame with specified column order
    df = pd.DataFrame(data, columns=columns)
    
    # Fill missing values
    df = df.fillna({
        "translated_title": "",
        "view_count": 0,
        "like_count": 0,
        "comment_count": 0,
        "channel_name": "",
        "date": ""
    })
    
    try:
        # Save to Excel file
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='YouTube_Videos')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['YouTube_Videos']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"Data successfully saved to {filename}")
        print(f"Total videos saved: {len(df)}")
        
    except Exception as e:
        print(f"Error saving to Excel: {e}")


def main():
    """Main function to run the YouTube data extraction process."""
    
    # Validate API key
    if API_KEY == "YOUR_YOUTUBE_API_KEY_HERE":
        print("Error: Please set your YouTube Data API key in the API_KEY variable.")
        return
    
    try:
        # Initialize YouTube data extractor
        extractor = YouTubeDataExtractor(API_KEY)
        
        print("Starting YouTube data extraction...")
        print(f"Date range: {START_DATE} to {END_DATE}")
        print(f"Channels to process: {len(CHANNEL_IDS)}")
        
        # Extract all videos
        videos_data = extractor.extract_all_videos(
            CHANNEL_IDS,
            START_DATE,
            END_DATE
        )
        
        # Save to Excel
        if videos_data:
            save_to_excel(videos_data, "youtube_data.xlsx")
        else:
            print("No videos found in the specified date range.")
            
    except Exception as e:
        print(f"An error occurred during execution: {e}")
        raise


if __name__ == "__main__":
    main()