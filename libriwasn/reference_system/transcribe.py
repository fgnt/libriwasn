"""
Transcribe a set of audio files

Example calls:
python -m libriwasn.reference_system.transcribe --json_path /path/to/per_utt.json
python -m libriwasn.reference_system.transcribe --json_path /path/to/per_utt.json --enable_gpu=True

Call 'python -m libriwasn.reference_system.transcribe --help' to get an overview of all options
"""
from pathlib import Path

import click
import dlp_mpi
import lazy_dataset.database
import paderbox as pb
from meeteval.io.stm import STMLine, STM

from libriwasn.asr.espnet_wrapper import ESPnetASR


@click.command()
@click.option(
    '--json_path',
    type=str,
    default=None,
    help=('Path of the json-file, which specifies the utterances to be '
          'described. Defaults to "libriwasn/libriwasn.json".')
)
@click.option(
    '--output_dir',
    type=str,
    default=None,
    help=('Path where the hypothesis of the transcription should be stored. '
          'Defaults to the parent directory of the json.')
)
@click.option(
    '--asr_model_dir',
    type=str,
    default=None,
    help=('Path where the ASR model should be stored. Defaults to the Espnet '
          'modelzoo directory in your environment')
)
@click.option(
    '--enable_gpu',
    type=bool,
    default=False,
    help='Enabe GPU-based decoding. GPU-based decoding is disabled by default'
)
def main(json_path, output_dir, asr_model_dir, enable_gpu):
    assert json_path is not None
    json_path = Path(json_path).absolute()
    if output_dir is not None:
        output_dir = Path(output_dir).absolute()

    apply_asr = \
        ESPnetASR(model_dir=asr_model_dir, enable_gpu=enable_gpu).apply_asr
    stm_lines = []
    data = lazy_dataset.from_dict(pb.io.load(json_path))
    for utt in dlp_mpi.split_managed(data, allow_single_worker=True):
        audio_path = utt['audio_path']
        text = apply_asr(audio_path)
        stm_lines.append(STMLine(
            filename=utt['short_id'],
            channel='0',
            speaker_id=utt['speaker_id'],
            begin_time=utt['start_sample'],
            end_time=utt['stop_sample'],
            transcript=text,
        ))

    stm_lines = dlp_mpi.gather(stm_lines)
    if dlp_mpi.IS_MASTER:
        if output_dir is None:
            file = json_path.parent / 'stm' / 'hyp.stm'
        else:
            file = Path(output_dir) / 'stm' / 'hyp.stm'

        file.parent.mkdir(parents=True, exist_ok=True)
        stm_lines = [
            lines
            for stm_lines__worker in stm_lines
            for lines in stm_lines__worker
        ]
        stm_lines = STM(stm_lines)
        stm_lines.dump(file)
        print(f'Wrote {file}', flush=True)


if __name__ == '__main__':
    main()
