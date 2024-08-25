import os
import sys
import yt_dlp


def download_playlist(url, audio_only, prefix_index, output_dir, force_replace):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Define a custom logger
    class MyLogger:
        def debug(self, msg):
            # Debugging information from yt_dlp
            pass

        def warning(self, msg):
            pass

        def error(self, msg):
            print(msg)

    # Function to generate the output template and check if files exist
    def generate_outtmpl(path_template, info_dict):
        return path_template % info_dict

    outtmpl_template = '%(playlist_index)03d-%(title)s.%(ext)s' if prefix_index else '%(title)s.%(ext)s'
    outtmpl_path = os.path.join(output_dir, outtmpl_template)

    # Hook to check if the file exists before download starts
    def file_exists_hook(d):
        if d['status'] == 'downloading':
            output_path = generate_outtmpl(outtmpl_path, d['info_dict'])
            if os.path.exists(output_path) and not force_replace:
                print(f"File '{output_path}' already exists and was skipped.")
                return True  # Skip downloading
        return False  # Don't skip

    ydl_opts = {
        'noplaylist': False,             # Ensure that we process the entire playlist
        'yesplaylist': True,
        'logger': MyLogger(),
        'outtmpl': outtmpl_path,         # Output template with optional playlist index
        'progress_hooks': [file_exists_hook],  # Check for existing files
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
            "Usage: python script.py [--audio-only] [--prefix-index] [--output-dir OUTPUT_DIR] [--force-replace] <playlist_url>")
        sys.exit(1)

    # Check for command-line options
    audio_only = '--audio-only' in sys.argv
    prefix_index = '--prefix-index' in sys.argv
    force_replace = '--force-replace' in sys.argv

    output_dir = "output"
    if '--output-dir' in sys.argv:
        output_dir_index = sys.argv.index('--output-dir')
        if output_dir_index + 1 < len(sys.argv):
            output_dir = sys.argv[output_dir_index + 1]
            del sys.argv[output_dir_index:output_dir_index + 2]
        else:
            print("Error: --output-dir option requires a value")
            sys.exit(1)

    # Remove options from sys.argv
    if audio_only:
        sys.argv.remove('--audio-only')
    if prefix_index:
        sys.argv.remove('--prefix-index')
    if force_replace:
        sys.argv.remove('--force-replace')

    if len(sys.argv) != 2:
        print(
            "Usage: python script.py [--audio-only] [--prefix-index] [--output-dir OUTPUT_DIR] [--force-replace] <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]

    if not playlist_url.startswith("http"):
        print("Invalid URL provided.")
        sys.exit(1)

    download_playlist(playlist_url, audio_only, prefix_index,
                      output_dir, force_replace)
