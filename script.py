import os
import sys
import yt_dlp


def download_playlist(url, audio_only, prefix_index, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    video_urls = {}

    # Define a custom logger
    class MyLogger:
        def debug(self, msg):
            # Debugging information from yt_dlp
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    # Hook to collect filenames
    def my_hook(d):
        if d['status'] == 'finished':
            video_urls[d['info_dict']['playlist_index']
                       ] = d['info_dict']['filename']

    ydl_opts = {
        'noplaylist': False,             # Ensure that we process the entire playlist
        'yesplaylist': True,
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
        # Output template with optional playlist index
        'outtmpl': os.path.join(output_dir, '%(playlist_index)03d-%(title)s.%(ext)s') if prefix_index else os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    if audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',   # Only download audio
            'postprocessors': [{          # Extract audio using ffmpeg or avconv
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',  # Change to your preferred format
                'preferredquality': '192',
            }]
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',  # Download best quality video + audio
            'merge_output_format': 'mp4',          # Ensure video and audio are merged
        })

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python script.py [--audio-only] [--prefix-index] [--output-dir OUTPUT_DIR] <playlist_url>")
        sys.exit(1)

    audio_only = '--audio-only' in sys.argv
    prefix_index = '--prefix-index' in sys.argv

    output_dir = "output"
    if '--output-dir' in sys.argv:
        output_dir_index = sys.argv.index('--output-dir')
        if output_dir_index + 1 < len(sys.argv):
            output_dir = sys.argv[output_dir_index + 1]
            del sys.argv[output_dir_index:output_dir_index + 2]
        else:
            print("Error: --output-dir option requires a value")
            sys.exit(1)

    if audio_only:
        sys.argv.remove('--audio-only')
    if prefix_index:
        sys.argv.remove('--prefix-index')

    if len(sys.argv) != 2:
        print(
            "Usage: python script.py [--audio-only] [--prefix-index] [--output-dir OUTPUT_DIR] <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]

    if not playlist_url.startswith("http"):
        print("Invalid URL provided.")
        sys.exit(1)

    download_playlist(playlist_url, audio_only, prefix_index, output_dir)
