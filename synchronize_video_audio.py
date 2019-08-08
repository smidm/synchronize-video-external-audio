from audio_offset_finder import find_offset
import subprocess
import argparse
import tempfile
import os
import shutil
import warnings


def synchronize_video_audio(video_in, audio_in, video_out, 
    find_offset_sample_rate=8000, verbose=False, include_original_audio=False, extracted_audio_length_s=None):
    temp_dir = tempfile.mkdtemp()
    if extracted_audio_length_s is None:
        duration_cmd = []
    else:
        duration_cmd = ['-t', str(extracted_audio_length_s)]
    extracted_audio_filename = os.path.join(temp_dir, 'extracted_audio.wav')
    command = ['ffmpeg', '-i', video_in] + duration_cmd + [extracted_audio_filename, '-loglevel']
    if verbose:
        command.append('info')
        print(' '.join(command))
    else:
        command.append('warning')
    subprocess.check_output(command)

    #                            offset of                within
    offset0, score0 = find_offset(extracted_audio_filename, audio_in, find_offset_sample_rate)
    offset1, score1 = find_offset(audio_in, extracted_audio_filename, find_offset_sample_rate)

    shutil.rmtree(temp_dir) 

    if score0 > score1:
        # internal audio starts later
        offset = offset0 / find_offset_sample_rate
        score = score0
    else:
        # external audio starts later
        offset = -offset1 / find_offset_sample_rate
        score = score1

    if score < 10:
        warnings.warn('Synchronization score is low ({:.1f})!'.format(score))
        
    if verbose or video_out is None:
        print('offset of video file audio within external audio: {} s, score: {}'.format(offset, score))

    if video_out is not None:
        if include_original_audio:
            original_audio_cmd = ['-map', '0:1']
        else:
            original_audio_cmd = []
        # for map syntax see https://trac.ffmpeg.org/wiki/Map https://ffmpeg.org/ffmpeg.html#Advanced-options
        command = ['ffmpeg', '-i', video_in, '-itsoffset', str(offset), '-i', audio_in,
         '-map', '0:v', '-map', '1:0'] + original_audio_cmd + ['-vcodec', 'copy',
         video_out, '-loglevel']

        if verbose:
            command.append('info')
            print(' '.join(command))
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
    parser.add_argument('--output', type=str, default=None, required=False, help='Output video file')
    parser.add_argument('--verbose', default=False, type=bool, help='Verbose output')
    parser.add_argument('--keep-original-audio', default=False, type=bool, help='Keep original audio track as a secondary audio')
    args = parser.parse_args()
    synchronize_video_audio(args.video, args.audio, args.output, verbose=args.verbose,
                            include_original_audio=args.keep_original_audio)
