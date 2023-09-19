import numpy as np
import paderbox as pb
from paderwasn.synchronization.sro_estimation import DynamicWACD
from paderwasn.synchronization.sync import compensate_sro
from paderwasn.synchronization.utils import VoiceActivityDetector


def estimate_sros(sigs):
    """
    Estimate the sampling rate offsets (SROs) of the signals w.r.t. the first
    channel using the dynamic weighted average coherence drift (DWACD) method

    Args:
        sigs:
            List of N audio channels

    Returns:
        N-1 SRO-trajectories w.r.t. the first channel
    """
    sro_estimator = DynamicWACD()
    ref_sig = sigs[0]
    sros = []
    energy = np.sum(
        pb.array.segment_axis(ref_sig[ref_sig > 0], 1024, 256, end='cut') ** 2,
        axis=-1
    )
    th = np.min(energy)
    vad = VoiceActivityDetector(3 * th, len_smooth_win=0)
    ref_act = vad(ref_sig)
    for ch_id in range(1, len(sigs)):
        sig = sigs[ch_id]
        energy = np.sum(
            pb.array.segment_axis(
                sig[sig > 0], 1024, 256, end='cut'
            ) ** 2, axis=-1
        )
        th = np.min(energy)
        vad = VoiceActivityDetector(3 * th, len_smooth_win=0)
        act = vad(sigs[ch_id])
        sro = sro_estimator(sig, ref_sig, act, ref_act)
        sros.append(sro)
    return sros


def compensate_for_sros(sigs, sros):
    """
    Compensate for the given SROs via an STFT-resampling

    Args:
        sigs:
            List of N audio channels
        sros:
            Lift of N-1 SRO-trajectories

    Returns:
        Signals after compensation for SROs
    """
    synced_sigs = np.zeros((len(sigs), len(sigs[0])))
    synced_sigs[0] = sigs[0].copy()
    for ch_id, sro in enumerate(sros):
        synced_sig = compensate_sro(sigs[ch_id + 1], sro)
        if len(synced_sig) > synced_sigs.shape[-1]:
            synced_sigs[ch_id + 1] = synced_sig[:synced_sigs.shape[-1]]
        elif len(synced_sig) < synced_sigs.shape[-1]:
            synced_sigs[ch_id + 1, :len(synced_sig)] = synced_sig
        else:
            synced_sigs[ch_id + 1] = synced_sig
    return synced_sigs
