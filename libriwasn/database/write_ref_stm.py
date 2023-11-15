from pathlib import Path

import click
from lazy_dataset.database import JsonDatabase
from meeteval.io.stm import STMLine, STM


@click.command()
@click.option(
    '--json_path',
    '-json',
    type=str,
    default='libriwasn/libriwasn.json',
    help='Path of the database json. Defaults to "libriwasn/libriwasn.json".'
)
@click.option(
    '--stm_path',
    '-stm',
    type=str,
    default=None,
    help=('Base directory of the databases. Defaults to '
          '"ref_transcription.stm" in the same directory as the database json')
)
def main(json_path, stm_path):
    json_path = Path(json_path).absolute()
    if stm_path is not None:
        stm_path = Path(stm_path).absolute()
    else:
        stm_path = json_path.parent / 'ref_transcription.stm'
    assert stm_path.suffix == '.stm', \
        f'Json file must end with ".stm" and not "{stm_path.suffix}"'
    stm_lines = []
    ds = JsonDatabase(json_path)
    ds = ds.get_dataset('libricss')
    for example in ds:
        short_id = f'{example["overlap_condition"]}_{example["session"]}'
        speaker_ids = example['speaker_id']
        transcriptions = example['transcription']
        onset = example['onset']['original_source']
        num_samples = example['num_samples']['original_source']
        for (spk_id, transcription, onset, length) \
                in zip(speaker_ids, transcriptions, onset, num_samples):
            new_line = STMLine(
                filename=short_id,
                channel=0,
                speaker_id=spk_id,
                begin_time=onset,
                end_time=onset + length,
                transcript=transcription,
            )
            stm_lines.append(new_line)
    stm_lines = STM(stm_lines)

    stm_path.parent.mkdir(parents=True, exist_ok=True)
    stm_lines.dump(stm_path)


if __name__ == '__main__':
    main()
