from einops import rearrange

import numpy as np
import paderbox as pb
from pb_bss.extraction.beamformer import get_mvdr_vector_souden
from pb_bss.extraction.beamformer import get_power_spectral_density_matrix


def segment_wise_beamforming(
        target_spk, y, masks, activity, frame_size=1024,
        frame_shift=256, min_segment_len=40
):
    """
    Extract the target speaker's signal from a speech mixture. First, the
    meeting is cut into segments of continuous activity of the target speaker.
    Afterwards the target speaker's signal is extracted per segment using a
    minimum-variance distortionless response (MVDR) beamformer in the
    formulation of [Souden2010MVDR].

    @article{Souden2010MVDR,
        title={On optimal frequency-domain multichannel linear filtering for
               noise reduction},
        author={Souden, Mehrez and Benesty, Jacob and Affes, Sofi{\`e}ne},
        journal={IEEE Transactions on audio, speech, and language processing},
        volume={18},
        number={2},
        pages={260--276},
        year={2010},
        publisher={IEEE}
    }
    Args:
        target_spk (int):
            Identifier of the speaker whose signal should be extracted.
        y (numpy.ndarray):
            STFT of the multi-channel speech mixture (Shape: number of channels
            x number of frames x  FFT size / 2 + 1). Note that only the
            non-redundant frequencies are used as input.
        masks (numpy.ndarray):
            Time-frequency masks (Shape: (number of speakers + 1
            x FFT size / 2 + 1 x number of frames))
        activity (array-like):
            Activity of the target speaker as boolean array. This is used to
            segment the meeting defined by periods of continuous activity.
        frame_size (int):
            Frame size used to calculate the STFT.
        frame_shift (int):
            Frame shift used to calculate the STFT.
        min_segment_len (int):
            Minimum length of continuous activity

    Returns:
        sig_segments (list of np.ndarrays):
            List of extracted ``utterances´´ of the given target speaker.
        segment_onsets (list):
            List of the onsets of the segments on which beamforming was done.
    """
    segments = pb.array.interval.ArrayInterval(activity).intervals
    sig_segments = []
    segment_onsets = []
    for (onset, offset) in segments:
        if offset - onset < min_segment_len:
            continue
        stft_buffer = y[:, onset:offset].copy()
        mask_target = masks[target_spk, :, onset:offset]
        interference_mask = 1 - mask_target
        interference_scm = get_power_spectral_density_matrix(
            rearrange(stft_buffer, 'c t f -> f c t'),
            interference_mask,
            normalize=False
        )
        interference_scm += \
            np.finfo(np.float64).eps * np.eye(y.shape[0])[None]
        scm_target = get_power_spectral_density_matrix(
            rearrange(stft_buffer, 'c t f -> f c t'),
            mask_target,
            normalize=False
        )
        bf_vec = get_mvdr_vector_souden(scm_target, interference_scm)
        bf_output = \
            np.zeros((offset - onset, stft_buffer.shape[-1]), np.complex128)
        for l in range(offset - onset):
            bf_output[l] = \
                np.einsum('fc, cf-> f', np.conj(bf_vec), stft_buffer[:, l])
        enh_sig = pb.transform.istft(
            bf_output, size=frame_size, shift=frame_shift, fading=False
        )
        sig_segments.append(enh_sig)
        onset_time_domain = \
            pb.transform.module_stft.stft_frame_index_to_sample_index(
                onset, window_length=frame_size,
                shift=frame_shift, mode='first'
            )
        segment_onsets.append(onset_time_domain)
    return sig_segments, segment_onsets
