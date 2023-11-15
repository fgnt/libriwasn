"""
Perform source separation on LibriCSS / LibriWASN. This corresponds to 'sys-2',
'sys-3' and 'sys-4' in the experiments of the LibriWASN paper. Firstly,
time-frequency masks are estimated using a complex Angular Central Gaussian
Mixture Model (cACGMM). Afterwards, the speakers' signals are extracted via
beamforming.

Example calls:
python -m libriwasn.reference_system.separate_sources with sys2_libricss db_json=/path/to/libriwasn.json
python -m libriwasn.reference_system.separate_sources with sys3_libriwasn200 db_json=/path/to/libriwasn.json
python -m libriwasn.reference_system.separate_sources with sys4_libriwasn800 db_json=/path/to/libriwasn.json
"""
from pathlib import Path

import dlp_mpi
from lazy_dataset.database import JsonDatabase
import paderbox as pb
from sacred import Experiment

from libriwasn.io.audioread import load_signals
from libriwasn.synchronization.sro import estimate_sros, compensate_for_sros
from libriwasn.mask_estimation.initialization import get_initialization
from libriwasn.mask_estimation.cacgmm import get_tf_masks
from libriwasn.source_extraction.separation import separate_sources


exp = Experiment('Separate sources')


@exp.config
def config():
    db_json = None
    storage_dir = None
    data_set = None
    devices_cacgmm = None
    devices_mvdr = None
    ref_device_sync = 'asnupb4'


@exp.named_config
def sys2_libricss():
    storage_dir = 'separated_sources/sys2_libricss/'
    data_set = 'libricss'


@exp.named_config
def sys2_libriwasn200():
    storage_dir = 'separated_sources/sys2_libriwasn200/'
    data_set = 'libriwasn200'
    devices_cacgmm = 'asnupb4'
    devices_mvdr = 'asnupb4'


@exp.named_config
def sys3_libriwasn200():
    storage_dir = 'separated_sources/sys3_libriwasn200/'
    data_set = 'libriwasn200'
    devices_cacgmm = 'asnupb4'
    devices_mvdr = None


@exp.named_config
def sys4_libriwasn200():
    storage_dir = 'separated_sources/sys4_libriwasn200/'
    data_set = 'libriwasn200'


@exp.named_config
def sys2_libriwasn800():
    storage_dir = 'separated_sources/sys2_libriwasn800/'
    data_set = 'libriwasn800'
    devices_cacgmm = 'asnupb4'
    devices_mvdr = 'asnupb4'


@exp.named_config
def sys3_libriwasn800():
    storage_dir = 'separated_sources/sys3_libriwasn800/'
    data_set = 'libriwasn800'
    devices_cacgmm = 'asnupb4'
    devices_mvdr = None


@exp.named_config
def sys4_libriwasn800():
    storage_dir = 'separated_sources/sys4_libriwasn800/'
    data_set = 'libriwasn800'


@exp.automain
def separate_sources(
        db_json, storage_dir, data_set, devices_cacgmm,
        devices_mvdr, ref_device_sync
):
    msg = 'You have to specify, where your LibriWASN database-json is stored.'
    assert db_json is not None, msg
    storage_dir = Path(storage_dir).absolute()
    segment_json = storage_dir / 'per_utt.json'
    ds = JsonDatabase(db_json)
    ds = ds.get_dataset(data_set)

    enhanced_segments = {}
    for example in dlp_mpi.split_managed(ds, allow_single_worker=True):
        ex_id = example['example_id']
        audio_root = \
            storage_dir / example['overlap_condition'] / example["example_id"]

        # estimate time frequency masks
        if isinstance(devices_cacgmm, str):
            single_ch = False
        else:
            single_ch = True

        sigs, devices = load_signals(
            example, devices=devices_cacgmm, single_ch=single_ch,
            ref_device=ref_device_sync, return_devices=True
        )
        if len(devices) > 1:
            sros = estimate_sros(sigs)
            sigs = compensate_for_sros(sigs, sros)
            del sros  # reduce memory consumption
        y = pb.transform.stft(sigs)

        mm_init, mm_guide = get_initialization(y)
        masks, priors = get_tf_masks(y, mm_init, mm_guide)

        # separate sources
        if devices_cacgmm != devices_mvdr:
            if isinstance(devices_cacgmm, str):
                single_ch = False
            else:
                single_ch = True

            sigs, devices = load_signals(
                example, devices=devices_cacgmm, single_ch=single_ch,
                ref_device=ref_device_sync, return_devices=True
            )
            if len(devices) > 1:
                sros = estimate_sros(sigs)
                sigs = compensate_for_sros(sigs, sros)
                del sros  # reduce memory consumption
            y = pb.transform.stft(sigs)
        separated_sigs, segment_onsets = separate_sources(y, masks, priors)

        for spk_id in range(len(separated_sigs)):
            path_sep_sigs_target = audio_root / str(spk_id)
            sigs_spk = separated_sigs[spk_id]
            onsets_spk = segment_onsets[spk_id]
            for idx, sig in enumerate(sigs_spk):
                if not path_sep_sigs_target.exists():
                    path_sep_sigs_target.mkdir(parents=True)
                segment_id = f'{ex_id}_{spk_id}_{idx}'
                audio_path = \
                    path_sep_sigs_target / f'enhanced{spk_id}_{idx}.wav'
                short_id = \
                    f'{example["overlap_condition"]}_{example["session"]}'
                enhanced_segments[segment_id] = {
                    "audio_path": audio_path,
                    "dataset": "eval",
                    "short_id": short_id,
                    "speaker_id": str(spk_id),
                    "start_sample": onsets_spk[idx],
                    "stop_sample": onsets_spk[idx] + len(sig)
                }
                pb.io.dump_audio(sig, audio_path)
        # reduce memory consumption
        del sigs, y, mm_init, mm_guide, masks, priors, separated_sigs

    all_enh_segments = dlp_mpi.gather(enhanced_segments, root=dlp_mpi.MASTER)
    if dlp_mpi.IS_MASTER:
        all_segments_flattened = {}
        for seg in all_enh_segments:
            all_segments_flattened.update(seg)
        pb.io.dump_json(
            all_segments_flattened, segment_json
        )
        print(f'Wrote: {segment_json}', flush=True)
