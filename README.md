# Album 3 Instagram Automation

Clean automation scripts for posting Instagram Stories with media hosted on GitHub.

## Setup

1. **Create a `.env` file** in the project root (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Add your tokens to `.env`**:
   - `GITHUB_TOKEN`: Personal access token from https://github.com/settings/tokens (with `repo` scope)
   - `GITHUB_REPO`: Your media repository (e.g., `username/album-3-media`)
   - `INSTAGRAM_ACCESS_TOKEN`: From Meta Graph API Explorer
   - `INSTAGRAM_ACCOUNT_ID`: Your Instagram Business Account ID

3. **Install dependencies** (if needed):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install requests
   ```

## Main Scripts

### `upload_and_post_story.py` (Recommended)

Upload a local file to GitHub and post it to Instagram Stories in one command.

```bash
python3 scripts/upload_and_post_story.py "path/to/image.png" "IMAGE"
python3 scripts/upload_and_post_story.py "path/to/video.mp4" "VIDEO"
```

**What it does:**
1. Uploads your file to GitHub (gets public URL)
2. Uploads to Instagram using that URL
3. Posts as an Instagram Story

### `github_uploader.py`

Upload a file to GitHub and get a public URL (can be used separately).

```bash
python3 scripts/github_uploader.py "path/to/file.png"
# Returns: https://raw.githubusercontent.com/username/repo/master/media/file.png
```

### `post_story.py`

Post to Instagram Stories using an existing public URL.

```bash
python3 scripts/post_story.py "https://example.com/image.png" "IMAGE"
python3 scripts/post_story.py "https://example.com/video.mp4" "VIDEO"
```

## Security Notes

- Never commit `.env` file (it's in `.gitignore`)
- `.env.example` should only contain placeholder values
- Revoke and regenerate tokens if they're ever exposed in git history

## Legacy Scripts

Other scripts in the `scripts/` directory are from previous implementations and may use outdated methods (Dropbox, hardcoded values, etc.). They're kept for reference but not actively maintained.
