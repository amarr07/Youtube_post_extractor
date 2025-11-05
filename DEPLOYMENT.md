# 🚀 Streamlit Cloud Deployment Guide

## ✅ Pre-Deployment Checklist

- [x] Project consolidated to single `app.py` file
- [x] API key removed from code (using .env locally and st.secrets for cloud)
- [x] `.gitignore` configured to exclude sensitive files
- [x] Code pushed to public repo: https://github.com/amarr07/Youtube_post_extractor.git
- [x] Documentation updated with deployment instructions

## 🔐 Security Verification

✅ **Protected files (NOT in git):**
- `.env` (local API key)
- `.streamlit/secrets.toml` (local secrets)
- `youtube_data.xlsx` (output files)

✅ **Tracked files (safe to push):**
- `.env.example` (template without real keys)
- `.streamlit/secrets.toml.example` (template)
- `app.py` (no hardcoded keys)
- `requirements.txt`
- `README.md`
- `.gitignore`

## 📋 Streamlit Cloud Deployment Steps

### 1. Go to Streamlit Cloud
Visit: https://share.streamlit.io

### 2. Sign in with GitHub
Use your GitHub account to authenticate

### 3. Create New App
- Click **"New app"**
- Repository: `amarr07/Youtube_post_extractor`
- Branch: `main`
- Main file path: `app.py`

### 4. Configure Secrets (IMPORTANT!)
Click **"Advanced settings"** → **"Secrets"**

Add this configuration:
```toml
YOUTUBE_API_KEY = "your_actual_youtube_api_key_here"
```

**⚠️ Replace `your_actual_youtube_api_key_here` with your real YouTube Data API v3 key**

### 5. Deploy
- Click **"Deploy!"**
- Wait for build to complete (2-3 minutes)
- Your app will be live at: `https://your-app-name.streamlit.app`

## 🔄 How Auto-Deployment Works

After initial deployment, any push to the `main` branch will automatically trigger a redeployment:

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin main

# Streamlit Cloud automatically redeploys
```

## 🧪 Testing Locally Before Deployment

1. Ensure `.env` file exists with your API key:
```bash
YOUTUBE_API_KEY=your_key_here
```

2. Run locally:
```bash
streamlit run app.py
```

3. Test all features before pushing

## 📊 Monitoring Your Deployed App

On Streamlit Cloud dashboard:
- View app logs
- Monitor resource usage
- Manage secrets
- View analytics

## 🔑 Getting Your YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **YouTube Data API v3**
4. Go to **Credentials** → **Create Credentials** → **API Key**
5. Copy the API key
6. Add restrictions (optional but recommended):
   - Application restrictions: HTTP referrers
   - API restrictions: YouTube Data API v3

## 🐛 Troubleshooting

### "API key not configured" error
- Check secrets are properly set in Streamlit Cloud dashboard
- Ensure secret key name is exactly: `YOUTUBE_API_KEY`

### "Quota exceeded" error
- YouTube API has daily quota limits (10,000 units by default)
- Monitor usage in Google Cloud Console
- Request quota increase if needed

### App not updating
- Check GitHub push was successful
- Force reboot app in Streamlit Cloud dashboard
- Clear cache and rerun

## 📞 Support

- Streamlit Docs: https://docs.streamlit.io
- YouTube API Docs: https://developers.google.com/youtube/v3
- Repository Issues: https://github.com/amarr07/Youtube_post_extractor/issues

---

**Last Updated:** November 5, 2025
**Status:** ✅ Ready for deployment
