from libriwasn.source_extraction.activity import (
    estimate_noise_class,
    estimate_activity
)
from libriwasn.source_extraction.beamformer import segment_wise_beamforming


def separate_sources(y, masks, priors):
    """
    Wrapper to extract the signals of all speakers via beamforming

    Args:
        y (numpy.ndarray):
            STFT of the multi-channel speech mixture (Shape: number of channels
            x number of frames x  FFT size / 2 + 1). Note that only the
            non-redundant frequencies are used as input.
        masks (numpy.ndarray):
            Time-frequency masks (Shape: (number of speakers + 1
            x FFT size / 2 + 1 x number of frames))
        priors (numpy.ndarray):
            Prior probabilities of the spatial mixture model (Shape:
            (number of speakers + 1 x number of frames)))

    Returns:
        sig_segments (Nested list):
            List of lists of enhanced signal segments per speaker.
        segment_onsets (Nested list):
            List of lists of the onsets of the enhanced signal segments
            per speaker.
    """
    noise_class = estimate_noise_class(priors)
    sig_segments = []
    segment_onsets = []
    for target_spk in range(len(masks)):
        if target_spk == noise_class:
            continue
        activity = estimate_activity(priors[target_spk])
        sig_segments_spk, segment_onsets_spk = \
            segment_wise_beamforming(target_spk, y, masks, activity)
        sig_segments.append(sig_segments_spk)
        segment_onsets.append(segment_onsets_spk)
    return sig_segments, segment_onsets
