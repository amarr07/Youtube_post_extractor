# 🎥 YouTube Data Extractor - Streamlit

A powerful web application built with Streamlit that extracts video data from YouTube channels using the YouTube Data API v3. Get comprehensive analytics including views, likes, comments, and more - all exportable to Excel!

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🔍 **Multi-Channel Support**: Extract data from multiple YouTube channels simultaneously
- 📅 **Custom Date Range**: Select specific date ranges for video extraction
- 📊 **Real-time Progress**: Visual progress tracking during data extraction
- 📈 **Analytics Dashboard**: View statistics including total views, likes, and comments
- 💾 **Excel Export**: Download all extracted data as a formatted Excel file
- 🎨 **User-Friendly Interface**: Clean, intuitive Streamlit web interface
- ⚡ **Fast Processing**: Efficient API calls with pagination support

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- YouTube Data API v3 Key ([Get one here](https://console.cloud.google.com/apis/credentials))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/amarr07/Youtube_extractor_streamlit.git
   cd Youtube_extractor_streamlit
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   
   Create a `.env` file in the project root or set an environment variable:
   ```bash
   export YOUTUBE_API_KEY="your_api_key_here"
   ```
   
   Or on Windows:
   ```cmd
   set YOUTUBE_API_KEY=your_api_key_here
   ```

### Running the App

**Streamlit Web Interface** (Recommended):
```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Command Line Script**:
```bash
python youtube_extractor.py
```

## 📖 How to Use

### Web Interface (app.py)

1. **Enter Channel IDs**: In the sidebar, paste YouTube channel IDs (one per line)
2. **Select Date Range**: Choose start and end dates using the date pickers
3. **Extract Data**: Click the "🚀 Extract Data" button
4. **View Results**: See real-time progress and preview the extracted data
5. **Download**: Click "📥 Download Excel File" to save your data

### Finding Channel IDs

You can find a YouTube channel ID in several ways:

- From channel URL: `youtube.com/channel/CHANNEL_ID_HERE`
- From custom URL: Use a [Channel ID finder tool](https://commentpicker.com/youtube-channel-id.php)
- From video page: Right-click → View Page Source → Search for "channelId"

### Example Channel IDs

```
UCy8qn0KvqhhaD86yBJzpeDQ
UCuK4jszmhyLs-DvHyT3txgA
UC3Uz2h9JD6Ac7LvuJUNQ9bg
```

## 📊 Output Format

The extracted data includes:

| Column | Description |
|--------|-------------|
| `date` | Publication date (YYYY-MM-DD) |
| `video_id` | Unique YouTube video ID |
| `channel_id` | YouTube channel ID |
| `original_title` | Video title |
| `translated_title` | (Reserved for translations) |
| `published_at` | Full publication timestamp |
| `view_count` | Number of views |
| `like_count` | Number of likes |
| `comment_count` | Number of comments |
| `channel_name` | Channel display name |

## 🛠️ Configuration

### API Quota Limits

The YouTube Data API has quota limits:
- **Default quota**: 10,000 units per day
- **Search operation**: 100 units
- **Video details**: 1 unit per video

**Tip**: For large extractions, monitor your quota usage in the [Google Cloud Console](https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas).

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `YOUTUBE_API_KEY` | Your YouTube Data API v3 key | Yes |

## 📦 Project Structure

```
Youtube_extractor_streamlit/
├── app.py                    # Streamlit web application
├── youtube_extractor.py      # Command-line script
├── requirements.txt          # Python dependencies
├── README.md                # This file
└── .gitignore               # Git ignore rules
```

## 🔧 Dependencies

- `streamlit>=1.28.0` - Web interface framework
- `google-api-python-client>=2.100.0` - YouTube API client
- `pandas>=2.0.0` - Data manipulation
- `openpyxl>=3.1.0` - Excel file generation
- `python-dateutil>=2.8.2` - Date parsing utilities

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

- **API Key Security**: Never commit your API key to version control
- **Quota Management**: Be mindful of API quota limits when extracting large amounts of data
- **Rate Limiting**: The API may rate limit requests if too many are made too quickly
- **Data Privacy**: Respect YouTube's Terms of Service and data privacy guidelines

## 🐛 Troubleshooting

### Common Issues

**"API quota exceeded" error**
- Solution: Wait until your quota resets (daily) or request a quota increase

**"No videos found" message**
- Check that the channel IDs are correct
- Verify the date range contains published videos
- Ensure the API key has proper permissions

**Import errors**
- Solution: Make sure all dependencies are installed: `pip install -r requirements.txt`

## 📧 Support

If you encounter any issues or have questions, please [open an issue](https://github.com/amarr07/Youtube_extractor_streamlit/issues) on GitHub.

## 🌟 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Powered by [YouTube Data API v3](https://developers.google.com/youtube/v3)
- Data processing with [Pandas](https://pandas.pydata.org/)

---

Made with ❤️ by [amarr07](https://github.com/amarr07)
