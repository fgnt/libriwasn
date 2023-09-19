"""
Segment the meetings using oracle information about who speaks when (see Sys-1
in the experiments of the LibriWASN paper). Note that this script can also be
used to reproduce the reference results for 'Clean (played back LibriSpeech
utterances)' in the LibriWASN paper.

Example calls:
python -m libriwasn.reference_system.segment_meetings with clean db_json=/path/to/libriwasn.json
python -m libriwasn.reference_system.segment_meetings with libricss db_json=/path/to/libriwasn.json
python -m libriwasn.reference_system.segment_meetings with libriwasn200 db_json=/path/to/libriwasn.json
python -m libriwasn.reference_system.segment_meetings with libriwasn800 db_json=/path/to/libriwasn.json
"""
from pathlib import Path

import dlp_mpi
from lazy_dataset.database import JsonDatabase
import numpy as np
import paderbox as pb
from paderwasn.synchronization.utils import VoiceActivityDetector
from sacred import Experiment

from libriwasn.synchronization.sro import estimate_sros
from libriwasn.synchronization.utils import ref_time_to_mic_time
from libriwasn.utils import solve_permutation


exp = Experiment('Segment meetings')


@exp.config
def config():
    db_json = None
    storage_dir = None
    data_set = None
    audio_key = 'observation'
    device = 'Pixel7'
    margin = 320


@exp.named_config
def clean():
    storage_dir = 'clean/'
    data_set = 'libricss'
    audio_key = 'played_signals'
    margin = 0


@exp.named_config
def libricss():
    storage_dir = 'segmented/libricss/'
    data_set = 'libricss'


@exp.named_config
def libriwasn200():
    storage_dir = 'segmented/libriwasn200/'
    data_set = 'libriwasn200'


@exp.named_config
def libriwasn800():
    storage_dir = 'segmented/libriwasn800/'
    data_set = 'libriwasn800'


@exp.automain
def segment_audio(
        db_json, storage_dir, data_set, audio_key, device, margin
):
    msg = 'You have to specify, where your LibriWASN database-json is stored.'
    assert db_json is not None, msg
    msg = (f'data_set ({data_set}) has to be chosen from '
           f'["libricss", "libriwasn200", "libriwasn800"]')
    assert data_set in ['libricss', 'libriwasn200', 'libriwasn800'], msg
    assert storage_dir is not None,\
        'You have to specify where the signals should be stored.'
    storage_dir = Path(storage_dir).absolute()
    segment_json = storage_dir / 'per_utt.json'
    ds = JsonDatabase(db_json)
    ds = ds.get_dataset(data_set)

    segmented = {}
    sro = None
    for example in dlp_mpi.split_managed(ds, allow_single_worker=True):
        ex_id = example['example_id']
        audio_root = storage_dir / example['overlap_condition'] / ex_id

        if audio_key == 'played_signals':
            sigs = pb.io.load_audio(example['audio_path']['played_signals'])
        elif isinstance(example['audio_path'][audio_key], str):
            # LibriCSS and 'clean'
            sig = pb.io.load_audio(example['audio_path'][audio_key])
            if sig.ndim > 1:
                sig = sig[0]
        else:
            # LibriWASN
            msg = (f'device ({device}) has to be chosen from '
                   f'{list(example["audio_path"][audio_key].keys())}')
            assert device in list(example['audio_path'][audio_key].keys()), msg
            sig = pb.io.load_audio(example['audio_path'][audio_key][device])
            if sig.ndim > 1:
                sig = sig[0]
            # The onsets and offsets specified in the database json are
            # synchronous to the recordings of the 'Soundcard'. Since all other
            # devices have a sampling rate offset w.r.t. the 'Soundcard' the
            # onsets and offsets have to be adapted to match the recordings
            # of the other devices.
            if device != 'Soundcard':
                ref_ch = pb.io.load_audio(
                    example['audio_path'][audio_key]['Soundcard']
                )
                if ref_ch.ndim > 1:
                    ref_ch = ref_ch[0]
                sigs = [ref_ch, sig]
                sro = estimate_sros(sigs)
                sro = sro[0]

        onsets = example['onset']['original_source']
        num_samples = example['num_samples']['original_source']
        speaker_ids = example['speaker_id']

        activities = {}
        for onset, n_smpls, spk_id in zip(onsets, num_samples, speaker_ids):
            if spk_id not in activities:
                activities[spk_id] = []
            offset = onset + n_smpls
            if sro is not None:
                onset = ref_time_to_mic_time(onset, sro)
                offset = ref_time_to_mic_time(offset, sro)
            # Manipulate onset and offset to compensate for the signals time of
            # flight (TOF) and tiny errors of the time alignment, e.g., due to
            # small errors of the sampling rate offset estimates or small
            # sampling time offsets
            activities[spk_id].append(
                (onset - margin, offset + margin)
            )

        if audio_key == 'played_signals':
            ref_activities = np.zeros_like(sigs, bool)
            for i, sig in enumerate(sigs):
                energy = np.sum(
                    pb.array.segment_axis(sig[sig > 0], 1024, 256,
                                          end='cut') ** 2,
                    axis=-1
                )
                th = np.min(energy)
                vad = VoiceActivityDetector(3 * th)
                ref_activities[i] = vad(sig)[:len(sig)]
            activities_ = np.zeros_like(sigs, bool)
            for i, act_intervals in enumerate(activities.values()):
                for (onset, offset) in act_intervals:
                    activities_[i, onset:offset] = 1
            permutation = solve_permutation(activities_, ref_activities)
            spk_ids = list(activities.keys())
            activities_ = list(activities.values())
            activities = {spk_ids[i]:activities_[i] for i in permutation}

        for i, (spk_id, act_intervals) in enumerate(activities.items()):
            if audio_key == 'played_signals':
                sig = sigs[i]
            path_sep_sigs_target = audio_root / str(spk_id)
            segments = []
            num_samples = []
            onsets = []
            for (onset, offset) in act_intervals:
                segments.append(sig[onset:offset])
                onsets.append(onset)
                num_samples.append(offset-onset)
            for idx, segment in enumerate(segments):
                path_sep_sigs_target.mkdir(parents=True, exist_ok=True)
                segment_id = f'{ex_id}_{spk_id}_{idx}'
                audio_path = \
                    path_sep_sigs_target / f'segmented{spk_id}_{idx}.wav'
                short_id = \
                    f'{example["overlap_condition"]}_{example["session"]}'
                segmented[segment_id] = {
                    "audio_path": audio_path,
                    "short_id": short_id,
                    "speaker_id": str(spk_id),
                    "start_sample": onsets[idx],
                    "stop_sample": onsets[idx] + num_samples[idx]
                }
                pb.io.dump_audio(segment, audio_path)

    all_segments = dlp_mpi.gather(segmented, root=dlp_mpi.MASTER)
    if dlp_mpi.IS_MASTER:
        all_segments_flattened = {}
        for seg in all_segments:
            all_segments_flattened.update(seg)
        pb.io.dump_json(
            all_segments_flattened, segment_json
        )
        print(f'Wrote {segment_json}')
