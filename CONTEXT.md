# ABM03 Outreach - Project Context

## Overview
This project manages automated Instagram posting for Album 3 outreach using GitHub-hosted media and secure environment variable configuration.

## Active Scripts (Clean & Secure)

### Main Workflow Scripts
- **upload_and_post_story.py** - ⭐ PRIMARY: Upload to GitHub and post to Instagram Stories in one command
- **github_uploader.py** - Upload files to GitHub repository and get public URLs
- **post_story.py** - Post to Instagram Stories using existing public URL

### Configuration
- **.env** - Environment variables (gitignored, never committed)
- **.env.example** - Template with placeholder values (safe to commit)

## Repository Strategy

**Two separate repositories:**
1. **album-3-instagram-automation** (this repo) - Scripts and automation code
2. **album-3-changelog-media** - Media storage for public URLs

**Benefits:**
- Clean separation of code and media
- Private scripts, public media access
- No large files in code repo
- Secure token management

## Security

### ✅ Safe Practices
- All tokens in `.env` file (gitignored)
- No hardcoded credentials in scripts
- Fresh repository with clean git history
- Environment variable based configuration

### 🔒 Token Management
Required tokens in `.env`:
- `GITHUB_TOKEN` - For uploading media to GitHub
- `GITHUB_REPO` - Format: `username/repo-name`
- `INSTAGRAM_ACCESS_TOKEN` - Long-lived token from Meta
- `INSTAGRAM_ACCOUNT_ID` - Your Instagram Business Account ID

## Usage

### Quick Start
```bash
# Upload local file to GitHub and post to Instagram Story
python3 scripts/upload_and_post_story.py "path/to/image.png" "IMAGE"
python3 scripts/upload_and_post_story.py "path/to/video.mp4" "VIDEO"
```

### Advanced Usage
```bash
# Just upload to GitHub (get URL)
python3 scripts/github_uploader.py "path/to/file.png"
# Returns: https://raw.githubusercontent.com/username/repo/master/media/file.png

# Post existing URL to Instagram
python3 scripts/post_story.py "https://example.com/image.png" "IMAGE"
```

## Content Directories (Local Only - Not in Git)
- **InstagramHighlights/** - Generated image content
- **StoryVideos/** - Video content
- **AudioSnippets/** - Audio files

## Current Status
- ✅ GitHub-based media hosting
- ✅ Secure environment variable configuration
- ✅ Clean git history (no exposed tokens)
- ✅ Working Instagram Stories automation
- ✅ Long-lived Instagram tokens (60-day expiry)

## Legacy Files
The `scripts/` directory contains some legacy scripts from previous implementations (Dropbox-based, etc.). Only the three main scripts listed above are actively maintained and secure.
