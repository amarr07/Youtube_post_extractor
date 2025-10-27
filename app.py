"""
Streamlit UI for YouTube Data API v3 Video Scraper
This app provides a web interface to fetch videos from YouTube channels and download the data as Excel.
"""

import streamlit as st
from datetime import datetime, date
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import openpyxl
from typing import List, Dict, Any
import io
import os

# YouTube Data API v3 Configuration
API_KEY = os.getenv("YOUTUBE_API_KEY", "")  # Get API key from environment variable
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


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
        except Exception as e:
            st.error(f"Error initializing YouTube API client: {e}")
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
                st.warning(f"API quota exceeded for channel {channel_id}")
            else:
                st.error(f"HTTP Error for channel {channel_id}: {e}")
        except Exception as e:
            st.error(f"Error fetching videos from channel {channel_id}: {e}")
        
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
                st.warning(f"API quota exceeded for video {video_id}")
            else:
                st.error(f"HTTP Error for video {video_id}: {e}")
            return {}
        except Exception as e:
            return {}
    
    def extract_all_videos(
        self,
        channel_ids: List[str],
        start_date: str,
        end_date: str,
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Extract all videos from multiple channels within date range.
        
        Args:
            channel_ids: List of YouTube channel IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of complete video data dictionaries
        """
        all_videos = []
        total_channels = len(channel_ids)
        
        for idx, channel_id in enumerate(channel_ids):
            if progress_callback:
                progress_callback(idx, total_channels, channel_id)
            
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
                    video["date"] = ""
                
                all_videos.append(video)
        
        return all_videos


def create_excel_file(data: List[Dict[str, Any]]) -> bytes:
    """
    Create an Excel file from video data and return as bytes.
    
    Args:
        data: List of video data dictionaries
        
    Returns:
        Excel file as bytes
    """
    # Define column order
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
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
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
    
    output.seek(0)
    return output.getvalue()


def main():
    """Main Streamlit app function."""
    
    # Page configuration
    st.set_page_config(
        page_title="YouTube Data Extractor",
        page_icon="🎥",
        layout="wide"
    )
    
    # Title and description
    st.title("🎥 YouTube Data Extractor")
    st.markdown("""
    Extract video data from YouTube channels using the YouTube Data API v3.
    Enter channel IDs and select a date range to get video statistics.
    """)
    
    # Sidebar for inputs
    st.sidebar.header("📝 Input Parameters")
    
    # Channel IDs input
    st.sidebar.subheader("Channel IDs")
    channel_ids_input = st.sidebar.text_area(
        "Enter YouTube Channel IDs (one per line)",
        value="",
        height=150,
        help="Enter one or more YouTube channel IDs, each on a new line"
    )
    
    # Date range picker
    st.sidebar.subheader("Date Range")
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date(2025, 9, 16),
            help="Select the start date for video search"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date(2025, 9, 28),
            help="Select the end date for video search"
        )
    
    # Validate dates
    if start_date > end_date:
        st.sidebar.error("⚠️ Start date must be before end date!")
        return
    
    # Extract button
    extract_button = st.sidebar.button("🚀 Extract Data", type="primary", use_container_width=True)
    
    # Main content area
    if extract_button:
        # Parse channel IDs
        channel_ids = [cid.strip() for cid in channel_ids_input.split('\n') if cid.strip()]
        
        if not channel_ids:
            st.error("⚠️ Please enter at least one channel ID!")
            return
        
        # Display extraction info
        st.info(f"📊 Extracting data from {len(channel_ids)} channel(s) between {start_date} and {end_date}")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(current, total, channel_id):
            progress = (current + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"Processing channel {current + 1}/{total}: {channel_id}")
        
        try:
            # Initialize extractor
            extractor = YouTubeDataExtractor(API_KEY)
            
            # Extract videos
            videos_data = extractor.extract_all_videos(
                channel_ids,
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                progress_callback=update_progress
            )
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            if videos_data:
                st.success(f"✅ Successfully extracted {len(videos_data)} videos!")
                
                # Display preview
                st.subheader("📋 Data Preview")
                df_preview = pd.DataFrame(videos_data)
                st.dataframe(df_preview.head(10), use_container_width=True)
                
                # Statistics
                st.subheader("📈 Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Videos", len(videos_data))
                
                with col2:
                    total_views = sum(v.get("view_count", 0) for v in videos_data)
                    st.metric("Total Views", f"{total_views:,}")
                
                with col3:
                    total_likes = sum(v.get("like_count", 0) for v in videos_data)
                    st.metric("Total Likes", f"{total_likes:,}")
                
                with col4:
                    total_comments = sum(v.get("comment_count", 0) for v in videos_data)
                    st.metric("Total Comments", f"{total_comments:,}")
                
                # Download button
                st.subheader("💾 Download Data")
                excel_data = create_excel_file(videos_data)
                
                st.download_button(
                    label="📥 Download Excel File",
                    data=excel_data,
                    file_name=f"youtube_data_{start_date}_{end_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                
            else:
                st.warning("⚠️ No videos found in the specified date range.")
                
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")
            progress_bar.empty()
            status_text.empty()
    
    else:
        # Show instructions when no extraction is running
        st.info("""
        ### 📖 How to Use:
        1. **Enter Channel IDs**: In the sidebar, enter YouTube channel IDs (one per line)
        2. **Select Date Range**: Choose start and end dates for your search
        3. **Extract Data**: Click the "Extract Data" button
        4. **Download**: Once complete, download the Excel file with all video data
        
        ### 💡 Tips:
        - You can find a channel ID in the URL of a YouTube channel page
        - The API has quota limits, so be mindful when extracting large amounts of data
        - Each video extraction counts towards your API quota
        """)
        
        # Example
        with st.expander("📝 Example Channel IDs"):
            st.code("""UCy8qn0KvqhhaD86yBJzpeDQ
UCuK4jszmhyLs-DvHyT3txgA
UC3Uz2h9JD6Ac7LvuJUNQ9bg""")


if __name__ == "__main__":
    main()
