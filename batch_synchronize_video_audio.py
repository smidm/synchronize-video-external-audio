import os
from synchronize_video_audio import synchronize_video_audio
import argparse
import tqdm


def get_files_sorted(search_dir):
    files = [os.path.join(search_dir, f) for f in os.listdir(search_dir) 
            if os.path.isfile(os.path.join(search_dir, f))]
    files.sort(key=lambda x: os.path.getmtime(x))
    return files

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Batch replace audio tracks in video files with synchronized external audio tracks", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('video', type=str, help='Input video files directory')
    parser.add_argument('audio', type=str, help='Input audio files directory')
    parser.add_argument('output', type=str, help='Output video files directory')
    args = parser.parse_args()
    
    video_files = get_files_sorted(args.video)
    assert video_files
    audio_files = get_files_sorted(args.audio)
    assert audio_files
    assert len(video_files) == len(audio_files)
    
    for video, audio in tqdm.tqdm(zip(video_files, audio_files)):
        filename, ext = os.path.splitext(os.path.basename(video))
        synchronize_video_audio(video, audio, os.path.join(args.output, filename + '.mp4'))
