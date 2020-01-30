# denoise - WIP 

## Handy commands

#### Parallel convert PCM to WAV and normalize

```bash
find . -name '*.raw' -type f -print0 | parallel -0 ffmpeg -f s16le -ar 48000 -ac 1 -i {} -filter:a loudnorm output_dir/{.}.wav
``` 

Parameters:

* `-f s16le` - signed 16-bit little endian samples
* `-ar 48000` - sample rate 48kHz
* `-ac 1` - 1 channel (mono)
* `-i file.raw` - input file
* `-filter:a loudnorm` [EBU R128 loudness normalization](https://ffmpeg.org/ffmpeg-filters.html#loudnorm)

Replacement strings `{}` notion explained in [Parallel cheat sheet](https://www.gnu.org/software/parallel/parallel_cheat.pdf).

#### Parallel convert all to WAV and normalize

`find . -name '*.*' -type f -print0 | parallel -0 ffmpeg -i {} -filter:a loudnorm -ar 48000 -ac 1 ALL/{/.}.wav`

## Notes

Noise-only recordings go to a single PCM (RAW) file (e.g. `noise.raw`), while clean speech to another one (e.g. `speech.raw`)

Once we have both, features can be extracted. By default, a single feature vector is created with 480 samples, which for 48khz gives us 10 millisecond (`480 samples / 48000 samples / second = 0.01s`) recording.  Why 10 ms? `WebRTC` seems to process audio in 10 ms chunks.

`./tools/denoise_training output/voice.raw output/noise.raw 4193143 > output/training.f32`