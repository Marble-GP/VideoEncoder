# Video Encoder

A simple Python script to convert video files using FFmpeg with user-friendly interface.

## Overview

This tool solves the problem of large file sizes or incompatible formats (webm, mov, etc.) from screen recordings that can't be played on upload destinations. FFmpeg is a powerful solution but can be difficult for general users to use effectively.

## Features

- **Easy to use**: Simple command-line interface with prompts
- **Quality control**: Adjustable quality settings (0-100)
- **Frame scaling**: Resize videos with scale factor (1-100%)
- **Frame rate limiting**: Automatically limits high frame rates (>60fps) to 59.94fps
- **Progress display**: Real-time progress bar and file size information
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Auto-formatting**: Ensures H.264 compatibility with even dimensions

## Requirements

- Python 3.x (standard library only)
- FFmpeg installed and accessible in PATH
- Cross-platform support: Windows/macOS/Linux

## Installation

1. Install FFmpeg on your system
2. Download the Python scripts
3. Run directly - no additional dependencies required

## Usage

```bash
python video_encoder.py
```

### Interface Flow
1. Run the script without arguments
2. Enter the path to the video file you want to convert
3. Set quality (0-100, default: 80)
4. Set frame size scale factor (1-100, default: 100)
5. The converted file will be saved in the same directory with "convert_" prefix

## Output

- Output file: `convert_<original_filename>`
- Format: Automatically converts to MP4 if input is not a common video format
- Location: Same directory as input file

## Technical Details

- **Video codec**: H.264 (libx264)
- **Audio codec**: AAC (128k bitrate)
- **Frame rate**: Limited to 59.94fps for high frame rate inputs
- **Dimensions**: Automatically adjusted to even numbers for H.264 compatibility
- **Preset**: 'faster' for improved encoding speed
- **Threading**: Utilizes multiple CPU cores for faster processing

## Files

- `video_encoder.py`: Basic version
- `video_encoder_fast.py`: Enhanced version with progress display and optimizations

## Author

S.Watanabe

## License

MIT License - see LICENSE file for details