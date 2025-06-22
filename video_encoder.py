#!/usr/bin/env python3
import subprocess
import readline
import sys
import re
from pathlib import Path


def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_duration(input_path):
    """Get video duration in seconds"""
    try:
        cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration', 
               '-of', 'csv=p=0', str(input_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return float(result.stdout.strip())
    except:
        return None


def parse_ffmpeg_progress(line, total_duration):
    """Parse ffmpeg progress from stderr output"""
    # Look for time=XX:XX:XX.XX pattern
    time_match = re.search(r'time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})', line)
    if time_match:
        hours, minutes, seconds, centiseconds = map(int, time_match.groups())
        current_time = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
        if total_duration and total_duration > 0:
            progress = min(current_time / total_duration * 100, 100)
            return progress, current_time
    return None, None


def display_progress(progress, current_time, total_duration):
    """Display progress bar and percentage"""
    bar_length = 50
    filled_length = int(bar_length * progress / 100)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    
    if total_duration:
        time_str = f"{current_time:.1f}s / {total_duration:.1f}s"
    else:
        time_str = f"{current_time:.1f}s"
    
    print(f'\r[{bar}] {progress:.1f}% {time_str}', end='', flush=True)


def get_user_input():
    while True:
        file_path = input("変換するファイルのパスを入力してください: ").strip()
        if not file_path:
            print("ファイルパスを入力してください。")
            continue
        
        path = Path(file_path)
        if not path.exists():
            print("指定されたファイルが存在しません。")
            continue
        
        if not path.is_file():
            print("指定されたパスはファイルではありません。")
            continue
        
        break
    
    while True:
        quality_input = input("品質を入力してください (0-100, デフォルト: 80): ").strip()
        if not quality_input:
            quality = 80
            break
        
        try:
            quality = int(quality_input)
            if 0 <= quality <= 100:
                break
            else:
                print("品質は0から100の間で入力してください。")
        except ValueError:
            print("数値を入力してください。")
    
    while True:
        scale_input = input("フレームサイズの倍率を入力してください (1-100, デフォルト: 100): ").strip()
        if not scale_input:
            scale = 100
            break
        
        try:
            scale = int(scale_input)
            if 1 <= scale <= 100:
                break
            else:
                print("倍率は1から100の間で入力してください。")
        except ValueError:
            print("数値を入力してください。")
    
    return path, quality, scale


def convert_video(input_path, quality, scale):
    input_file = Path(input_path)
    output_file = input_file.parent / f"convert_{input_file.name}"
    
    if output_file.suffix.lower() not in ['.mp4', '.avi', '.mov', '.mkv']:
        output_file = output_file.with_suffix('.mp4')
    
    # Get video duration for progress calculation
    total_duration = get_video_duration(input_file)
    
    crf = 51 - int(quality * 0.51)
    
    cmd = [
        'ffmpeg',
        '-i', str(input_file),
        '-c:v', 'libx264',
        '-crf', str(crf),
        '-preset', 'faster',  # Changed from 'medium' to 'faster' for speed
        '-threads', '4',      # Use all available CPU cores
        '-c:a', 'aac',
        '-b:a', '128k'
    ]
    
    # Build video filter
    if scale != 100:
        scale_filter = f"scale=trunc(iw*{scale/100}/2)*2:trunc(ih*{scale/100}/2)*2"
        video_filter = scale_filter
    else:
        video_filter = 'scale=trunc(iw/2)*2:trunc(ih/2)*2'
    
    # Add frame rate limit
    video_filter += ',fps=fps=min(source_fps\\,59.94)'
    cmd.extend(['-vf', video_filter])
    
    # Add progress reporting
    cmd.extend(['-progress', 'pipe:1', '-y', str(output_file)])
    
    print(f"変換開始: {input_file.name} -> {output_file.name}")
    if total_duration:
        print(f"動画の長さ: {total_duration:.1f}秒")
    print("変換中...")
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, 
                                 text=True, bufsize=1, universal_newlines=True)
        
        # Monitor progress
        while True:
            output = process.stderr.readline()
            if output == '' and process.poll() is not None:
                break
            
            if output:
                progress, current_time = parse_ffmpeg_progress(output, total_duration)
                if progress is not None:
                    display_progress(progress, current_time, total_duration)
        
        # Wait for process to complete
        process.wait()
        
        if process.returncode == 0:
            # Get output file size
            file_size = output_file.stat().st_size
            if file_size >= 1024 * 1024 * 1024:  # GB
                size_str = f"{file_size / (1024 * 1024 * 1024):.1f} GB"
            elif file_size >= 1024 * 1024:  # MB
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            elif file_size >= 1024:  # KB
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size} B"
            
            print(f"\n変換完了: {output_file}")
            print(f"出力ファイルサイズ: {size_str}")
            return True
        else:
            print(f"\n変換エラー: 終了コード {process.returncode}")
            stderr_output = process.stderr.read() if process.stderr else ""
            if stderr_output:
                print(f"エラーメッセージ: {stderr_output}")
            return False
            
    except Exception as e:
        print(f"\n変換エラー: {e}")
        return False


def main():
    print("動画変換ツール")
    print("=" * 20)
    
    if not check_ffmpeg():
        print("エラー: ffmpegが見つかりません。ffmpegをインストールしてください。")
        sys.exit(1)
    
    try:
        input_path, quality, scale = get_user_input()
        success = convert_video(input_path, quality, scale)
        
        if success:
            print("変換が正常に完了しました。")
        else:
            print("変換に失敗しました。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n変換がキャンセルされました。")
        sys.exit(0)
    except Exception as e:
        print(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()