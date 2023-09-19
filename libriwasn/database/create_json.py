from copy import deepcopy
from pathlib import Path

import click
import numpy as np
import paderbox as pb


def read_tsv(path):
    return [line.split('\t') for line in path.read_text().split('\n') if line]


def create_database(database_path: Path, sample_rate=16000):
    def get_info_libriwasn(audio_root):
        file_paths = {}
        num_samples = {}
        for file in audio_root.glob('*.wav'):
            file = str(file)
            file_id = file.split('/')[-1]
            if file_id == 'raw_recording.wav':
                continue
            device_id = file_id.split('_')[0]
            if device_id == 'Raspi':
                device_id = file_id.split('_')[2]
            num_samples[device_id] = pb.io.audioread.audio_length(file)
            file_paths[device_id] = file
        return file_paths, num_samples

    overlap_conditions = ['0L', '0S', 'OV10', 'OV20', 'OV30', 'OV40']
    database = {}
    libricss_set = database['libricss'] = {}
    libriwasn_200_set = database['libriwasn200'] = {}
    libriwasn_800_set = database['libriwasn800'] = {}
    for cond in overlap_conditions:
        for meeting_path in (database_path / 'LibriCSS' / cond).glob('*'):
            meeting_id = meeting_path.name
            session_id = meeting_id.split('_')[-2]
            onsets = []
            num_samples = []
            transcriptions = []
            speaker_ids = []
            source_ids = []
            meeting_info = read_tsv(
                meeting_path / 'transcription' / 'meeting_info.txt'
            )
            for (start_time, end_time, speaker, utterance_id, transcription) \
                    in meeting_info[1:]:
                speaker_ids.append(speaker)
                source_ids.append(utterance_id)
                onsets.append(int(float(start_time) * sample_rate))
                num_samples.append(
                    int((float(end_time)-float(start_time))*sample_rate)
                )
                transcriptions.append(transcription)

            num_samples_obs = pb.io.audioread.audio_length(
                meeting_path / 'record' / 'raw_recording.wav'
            )
            num_samples_clean_obs = pb.io.audioread.audio_length(
                meeting_path / 'clean' / 'mix.wav'
            )
            num_samples_played = pb.io.audioread.audio_length(
                meeting_path / 'clean' / 'each_spk.wav'
            )
            libricss_set[f'{meeting_id}'] = {
                    'audio_path': {
                        'observation': str(
                            meeting_path / 'record' / 'raw_recording.wav'
                        ),
                        'clean_observation': str(
                            meeting_path / 'clean' / 'mix.wav'
                        ),
                        'played_signals': str(
                            meeting_path / 'clean' / 'each_spk.wav'
                        ),
                    },
                    'speaker_id': speaker_ids,
                    'source_id': source_ids,
                    'onset': {'original_source': onsets},
                    'num_samples': {
                        'original_source': num_samples,
                        'observation': num_samples_obs,
                        'clean_observation': num_samples_clean_obs,
                        'played_signals': num_samples_played
                    },
                    'transcription': transcriptions,
                    'overlap_condition': cond,
                    'session': session_id
            }

            onsets_libriwasn = \
                [np.maximum(onset - 32000, 0) for onset in onsets]
            libriwasn_200_example = libriwasn_200_set[f'{meeting_id}'] = \
                deepcopy(libricss_set[f'{meeting_id}'])
            file_paths, num_samples = get_info_libriwasn(
                database_path / 'LibriWASN' / 'libriwasn_200'/
                cond / meeting_id / 'record'
            )
            libriwasn_200_example['audio_path']['observation'] = file_paths
            libriwasn_200_example['onset']['original_source'] = \
                onsets_libriwasn
            libriwasn_200_example['num_samples']['observation'] = num_samples

            libriwasn_800_example = libriwasn_800_set[f'{meeting_id}'] = \
                deepcopy(libricss_set[f'{meeting_id}'])
            file_paths, num_samples = get_info_libriwasn(
                database_path / 'LibriWASN' / 'libriwasn_800' /
                cond / meeting_id / 'record'
            )
            libriwasn_800_example['audio_path']['observation'] = file_paths
            libriwasn_800_example['onset']['original_source'] = \
                onsets_libriwasn
            libriwasn_800_example['num_samples']['observation'] = num_samples
    return database


@click.command()
@click.option(
    '--database_path',
    '-db',
    type=str,
    default='libriwasn/',
    help='Base directory of the databases. Defaults to "libriwasn/".'
)
@click.option(
    '--json_path',
    '-json',
    type=str,
    default='libriwasn/libriwasn.json',
    help=('Path of the json-file to be created. '
          'Defaults to "libriwasn/libriwasn.json".')
)
def main(database_path, json_path):
    database_path = Path(database_path).absolute()
    json_path = Path(json_path).absolute()
    assert json_path.suffix == '.json', \
        f'Json file must end with ".json" and not "{json_path.suffix}"'
    database = create_database(database_path)
    database = {
        'datasets': database,
    }
    pb.io.dump_json(database, json_path, create_path=True, indent=4)
    print(f'Wrote {json_path}')


if __name__ == '__main__':
    main()
