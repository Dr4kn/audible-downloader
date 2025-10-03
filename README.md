# Audible Audiobook Downloader

A robust Docker container that automatically downloads and converts your Audible audiobooks from AAX/AAXC to M4B format with built-in integrity verification and self-healing capabilities.

## ✨ Key Features

- **🔄 Automatic Downloads**: Checks every 6 hours for new books in your library
- **🔧 Self-Healing**: Built-in integrity verification automatically fixes corrupted files
- **📚 Smart Organization**: Uses [AudioBookShelf](https://www.audiobookshelf.org/docs#book-directory-structure) directory structure
- **🛡️ Robust Error Handling**: Gracefully handles failures and continues processing
- **📊 Integrity Monitoring**: Comprehensive verification tools with automatic fixes
- **💾 DRM Removal**: Converts AAX/AAXC files using your account's activation bytes

## 📁 Directory Structure

```
Author/
├── Series/
│   ├── 1 - Year - Book Title {Narrator}/
│   │   └── book.m4b
│   └── 2 - Year - Book Title {Narrator}/
└── Standalone Book/
    └── book.m4b
```

# 🚀 Quick Start

## Build and Run

1. **Build the Docker image**:

   ```bash
   docker build -t audible-downloader .
   ```

2. **Run the container**:

   ```bash
   docker run -d \
       --name=audiobookDownloader \
       -e AUDIOBOOK_FOLDERS='True' \
       -e SLEEP_DURATION='2h' \
       -v /path/to/config:/config \
       -v /path/to/audiobooks:/audiobooks \
       audible-downloader
   ```

   **Windows PowerShell example**:

   ```powershell
   docker run -d `
       --name=audiobookDownloader `
       -e AUDIOBOOK_FOLDERS='True' `
       -v "C:\path\to\config:/config" `
       -v "C:\path\to\audiobooks:/audiobooks" `
       audible-downloader
   ```

## 🔐 Initial Setup

1. **Start the container** using the commands above

2. **Configure Audible authentication**:

   ```bash
   docker exec -it audiobookDownloader audible quickstart
   ```

   - Follow the prompts to authenticate with your Audible account
   - Choose browser login when prompted
   - Complete any captcha challenges
   - The auth file will be saved automatically

3. **Verify setup**:
   ```bash
   docker logs audiobookDownloader
   ```

# 🔍 Integrity Verification Utility

The container includes a powerful integrity verification tool that can check and automatically fix issues with your audiobook collection.

## Manual Verification

### Basic Usage

**Check collection health**:

```powershell
.\verify_integrity.ps1
```

**Detailed verification**:

```powershell
.\verify_integrity.ps1 -Verbose
```

**Quick check (skip file validation)**:

```powershell
.\verify_integrity.ps1 -Quick
```

### Automatic Fixes

**Preview what would be fixed**:

```powershell
.\verify_integrity.ps1 -DryRun -Fix
```

**Automatically fix all issues**:

```powershell
.\verify_integrity.ps1 -Fix
```

**Detailed verification with auto-fix**:

```powershell
.\verify_integrity.ps1 -Verbose -Fix
```

### Direct Docker Usage

```bash
# Basic verification
docker exec -it audiobookDownloader python /app/verify_integrity.py

# Detailed output
docker exec -it audiobookDownloader python /app/verify_integrity.py --verbose

# Auto-fix issues
docker exec -it audiobookDownloader python /app/verify_integrity.py --fix

# Preview fixes
docker exec -it audiobookDownloader python /app/verify_integrity.py --dry-run --fix
```

## What Gets Verified

- ✅ **File Existence**: Ensures all "downloaded" books have actual files
- ✅ **File Integrity**: Validates audio files aren't corrupted using FFprobe
- ✅ **Database Consistency**: Checks for mismatched records
- ✅ **Orphaned Files**: Finds audiobook files not tracked in database
- ✅ **Path Validation**: Verifies correct directory structure

## Auto-Fix Capabilities

- 🔧 **Missing Files**: Resets download status for re-downloading
- 🔧 **Corrupted Files**: Deletes bad files and marks for re-download
- 🔧 **Database Issues**: Updates inconsistent records
- 🔧 **File Conflicts**: Handles overwrites during re-downloads

## Built-in Automation

The integrity verification runs automatically **every 6 hours** as part of the download cycle:

1. Update library from Audible
2. **🔍 Run integrity check and auto-fix**
3. Download new/fixed audiobooks
4. Convert and organize files
5. Wait 6 hours and repeat

# 🛠️ Advanced Usage

## Environment Variables

- `AUDIOBOOK_FOLDERS='True'`: Enable organized folder structure (recommended)
- `AUDIBLE_CONFIG_DIR=/config`: Configuration directory (default)
- `SLEEP_DURATION='6h'`: Time between download checks (default: 6h, supports: s/m/h/d)

## Container Management

**View logs**:

```bash
docker logs audiobookDownloader
```

**Follow live logs**:

```bash
docker logs -f audiobookDownloader
```

**Stop container**:

```bash
docker stop audiobookDownloader
```

**Restart container**:

```bash
docker restart audiobookDownloader
```

## Manual Download Cycle

Force an immediate download cycle:

```bash
docker exec -it audiobookDownloader python /app/audiobookDownloader.py
```

# 🔧 Troubleshooting

## Common Issues

**Authentication Problems**: Re-run `audible quickstart` in the container
**Download Failures**: Check logs and verify internet connectivity  
**Corrupted Files**: Run `.\verify_integrity.ps1 -Fix` to auto-repair
**Missing Books**: Integrity verification will reset them for re-download

## Support

This enhanced version includes comprehensive error handling and self-healing capabilities. Most issues are automatically detected and resolved.
