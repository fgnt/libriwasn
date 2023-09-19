from einops import rearrange

import numpy as np
from pb_bss.distribution.complex_angular_central_gaussian import (
    ComplexAngularCentralGaussian,
    ComplexAngularCentralGaussianTrainer,
    normalize_observation
)
from pb_bss.distribution.cacgmm import estimate_mixture_weight, CACGMM
from pb_bss.distribution.mixture_model_utils import (
    apply_inline_permutation_alignment
)
from pb_bss.permutation_alignment import DHTVPermutationAlignment


def _cacgmm_e_step(y, models, inline_permutation_aligner):
    posteriors = []
    quadratic_forms = []
    for f in range(len(y)):
        affiliation, quadratic_form, _ = models[f]._predict(
            y[f],
            affiliation_eps=1e-10,
        )
        posteriors.append(affiliation)
        quadratic_forms.append(quadratic_form)
    posteriors = np.asarray(posteriors)
    quadratic_forms = np.asarray(quadratic_forms)

    if inline_permutation_aligner is not None:
        posteriors, quadratic_forms = apply_inline_permutation_alignment(
            affiliation=posteriors,
            quadratic_form=quadratic_forms,
            weight_constant_axis=-3,
            aligner=inline_permutation_aligner,
        )
    return posteriors, quadratic_forms


def _cacgmm_m_step(y, posteriors, quadratic_forms):
    weight = estimate_mixture_weight(
        affiliation=posteriors,
        saliency=None,
        weight_constant_axis=-3,
    )
    models = []
    for f in range(len(y)):
        cacg = ComplexAngularCentralGaussianTrainer()._fit(
            y=y[f, None, :, :],
            saliency=posteriors[f],
            quadratic_form=quadratic_forms[f],
            hermitize=True,
            covariance_norm='eigenvalue',
            eigenvalue_floor=1e-10,
        )
        models.append(CACGMM(weight=weight[0], cacg=cacg))
    return models, weight


def get_tf_masks(
        y, initialization, guide, guided_iter=40, non_guided_iter=10
):
    """
    Estimate time frequency masks using a CACGMM. In the first EM-iterations
    a guide is utilized to omit that the model diverges too much from the
    initialization in very noisy conditions.

    Args:
        y (numpy.ndarray):
            STFT of the input signals (Shape: (number of channels x
            number of frames x FFT size / 2 + 1)). Note that only the
            non-redundant frequencies are used as input.
        initialization (numpy.ndarray):
            Initial estimate for the posteriors of the CACGMM (Shape:
            (FFT size / 2 + 1 x number of speakers + 1 x number of frames))
        guide (numpy.ndarray):
            Guide (boolean array of actvitities per source) used in the first
            EM-iterations (Shape: (number of speakers + 1 x number of frames))
        guided_iter:
            Number of guided iterations
        non_guided_iter:
            Number of iterations without using the guide

    Returns:
        Time-frequency masks (Shape: (number of speakers + 1 x FFT size / 2 + 1
        x number of frames))
    """
    num_iter = guided_iter + non_guided_iter
    fft_size = int((y.shape[-1] - 1) * 2)
    permutation_alignment = \
        DHTVPermutationAlignment.from_stft_size(fft_size)

    y = rearrange(y, 'c t f -> f t c')
    y = normalize_observation(y)

    posteriors = initialization
    quadratic_forms = np.ones(initialization.shape, dtype=y.real.dtype)
    models = None
    for i in range(num_iter):
        if i < guided_iter:
            guide = guide
        else:
            guide = None
        if models is not None:
            posteriors, quadratic_forms = \
                _cacgmm_e_step(y, models, permutation_alignment)
        if guide is not None:
            posteriors *= guide[None]
            denominator = np.maximum(
                np.sum(posteriors, axis=-2, keepdims=True),
                np.finfo(posteriors.dtype).tiny,
            )
            posteriors /= denominator
        models, priors = _cacgmm_m_step(y, posteriors, quadratic_forms)

    tf_masks, _ = _cacgmm_e_step(y, models, permutation_alignment)
    tf_masks = rearrange(tf_masks, 'f c t  -> c f t')
    return tf_masks, priors.squeeze(0)
