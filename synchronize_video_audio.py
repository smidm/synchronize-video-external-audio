import subprocess
from audio_offset_finder import find_offset
import argparse
import tempfile
import os
import shutil

def synchronize_video_audio(video_in, audio_in, video_out, find_offset_sample_rate=8000, verbose=False):
    temp_dir = tempfile.mkdtemp()
    extracted_audio_filename = os.path.join(temp_dir, 'extracted_audio.wav')
    command = ['ffmpeg', '-i', video_in, extracted_audio_filename, '-loglevel']
    if verbose:
        command.append('info')
    else:
        command.append('warning')
    subprocess.check_output(command)

    #                            offset of                within
    offset0, score0 = find_offset(extracted_audio_filename, audio_in, find_offset_sample_rate)
    offset1, score1 = find_offset(audio_in, extracted_audio_filename, find_offset_sample_rate)

    shutil.rmtree(temp_dir) 

    if score0 > score1:
        # internal audio starts later
        ratio = score0 / score1
        offset = offset0 / find_offset_sample_rate
    else:
        # external audio starts later
        ratio = score1 / score0
        offset = -offset1 / find_offset_sample_rate
        
    if verbose:
        print('score ratio {}, offset {} s'.format(ratio, offset))

    command = ['ffmpeg', '-i', video_in, '-itsoffset', str(offset), '-i', audio_in, '-map', '0:v', '-map', '1:0', '-vcodec', 'copy', video_out, '-loglevel']
    if verbose:
        command.append('info')
    else:
        command.append('warning')
    subprocess.check_output(command)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Replace an audio track in a video file with a synchronized external audio track", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('video', type=str, help='Input video file')
    parser.add_argument('audio', type=str, help='Input audio file')
    parser.add_argument('output', type=str, help='Output video file')
    parser.add_argument('--verbose', default=False, type=bool, help='Verbose output')
    args = parser.parse_args()
    synchronize_video_audio(args.video, args.audio, args.output, verbose=args.verbose)
    
        

