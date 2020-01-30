#!/usr/bin/env python3

import click
import os
import wave
import glob
from joblib import Parallel, delayed
from webrtc_audio_processing import AP

@click.group()
def cli():
    """
    Apply noise suppression (as provided in WebRTC) to audio recording in WAVE format
    and output to a new file.

    \b
    The available noise suppression levels are as following:
    1 - low (kLowSuppression)
    2 - moderate (kModerateSuppression)
    3 - high (kHighSuppression)

    The noise suppression level is provided via --noisesuppression argument.
    Extra setting `-1` produces output with all three levels

    """
    pass


@cli.command('single', short_help='Process single file')
@click.option("--input", "-in", type=click.Path(exists=True), required=True, help="Path to the audio in WAV format.")
@click.option("--output", "-out", type=click.STRING, default=None, help="Output file or directory.")
@click.option("--noisesuppression", "-ns", type=click.INT, default=3, help="Noise suppression level.", show_default=True)
def single(input, output, noisesuppression):
    reduce_noise_and_write_output(input_path=input, output_path=output, ns=noisesuppression)


@cli.command('multi', short_help='Process multiple files')
@click.option("--input", "-in", type=click.STRING, required=True,
              help="Path to the directory with recordings in WAV format.")
@click.option("--output", "-out", type=click.STRING, default=None, help="Output directory. If directory does "
              "not exist it will be created. The output files will have the same base name as input.")
@click.option("--noisesuppression", "-ns", type=click.INT, default=3, help="Noise suppression level.", show_default=True)
@click.option("--jobs", "-j", type=click.INT, default=-1, help="Number of jobs to run. Defaults to all cores",
              show_default=True)
@click.option("--recursive", "-r", is_flag=True, help="Traverse directory recursively when looking for recordings. "
              "WARNING: if files in different directories have the same names, output files will be overwritten. "
              "This behaviour can be fixed if required.")
def process(input, output, noisesuppression, jobs, recursive):
    if os.path.isdir(input):
        pattern = '/**/*.wav' if recursive else '/*.wav'
        wav_paths = glob.glob(input + pattern, recursive=recursive)
        if not wav_paths:
            print(f'Directory {input} does not have any WAV files')
            if not recursive: print('Consider searching recursively')
        if output:
            os.makedirs(output, exist_ok=True)
        if jobs == 1:
            for path in wav_paths:
                apply_ns(input_path=path, output_path=output, ns=noisesuppression)
        else:
            Parallel(n_jobs=jobs, backend='loky')(delayed(apply_ns)(
                input_path=path,
                output_path=output,
                ns=noisesuppression
            ) for path in wav_paths)
    else:
        print(f'{input} is not a directory.')


def apply_ns(input_path: str, ns: int, output_path=None):
    if ns == -1:
        for ns_level in [1, 2, 3]:
            reduce_noise_and_write_output(input_path, ns_level, output_path)
    else:
        reduce_noise_and_write_output(input_path, ns, output_path)


def reduce_noise_and_write_output(input_path: str, ns: int, output_path=None):
    directory, filename = os.path.split(input_path)
    filename_no_ext, ext = os.path.splitext(filename)
    output_filepath = f'{filename_no_ext}_ns{ns}{ext}'

    if output_path:
        if os.path.isdir(output_path):
            output_filepath = os.path.join(output_path, output_filepath)
        else:
            output_filepath = output_path

    print(f'Processing {input_path} to {output_filepath}')

    with wave.open(input_path, 'rb') as wav, wave.open(output_filepath, 'wb') as out:
        rate = wav.getframerate()
        width = wav.getsampwidth()
        channels = wav.getnchannels()

        out.setnchannels(channels)
        out.setsampwidth(width)
        out.setframerate(rate)

        ap = AP(enable_ns=True)
        ap.set_ns_level(ns)
        ap.set_stream_format(rate, channels, rate, channels)

        frames_size = int(rate * 10 / 1000)  # only support processing 10ms audio each time
        frames_bytes = frames_size * width * channels

        while True:
            data = wav.readframes(frames_size)
            if len(data) != frames_bytes:
                break
            data_out = ap.process_stream(data)
            out.writeframes(data_out)


if __name__ == '__main__':
    cli()



