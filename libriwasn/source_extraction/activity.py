import numpy as np

from libriwasn.utils import dilate, erode


def estimate_noise_class(
        priors, th=.2, dilation_kernel_size=101, erosion_kernel_size=101
):
    """
    Estimate which class belongs to the noise based on the priors of a
    spatial mixture model as described in [boeddeker22].

    @inproceedings{boeddeker22,
        author = {Boeddeker, Christoph and Cord-Landwehr, Tobias and
                  von Neumann, Thilo and Haeb-Umbach, Reinhold},
        title = {An Initialization Scheme for Meeting Separation with
                 Spatial Mixture Models},
        booktitle={Proc. INTERSPEECH},
        year = {2022}
    }
    Args:
        priors (numpy.ndarray):
            Priors of the classes of a spatial mixture model
        th (float):
            Threshold for the priors to decide whether the source is
            active of inactive
        dilation_kernel_size (int):
            Size of the dilation kernel used to smooth the estimated activity.
            Must be an odd number.
        erosion_kernel_size (int):
            Size of the erosion kernel used to smooth the estimated activity
            Must be an odd number.

    Returns:
        The index of the class associated with the noise
    """
    activities = np.zeros_like(priors, bool)
    for i, prior in enumerate(priors):
        activities[i] = erode(
            dilate(prior >= th, dilation_kernel_size), erosion_kernel_size
        )
    noise_class = np.argmax(np.sum(activities, -1))
    return noise_class


def estimate_activity(
        prior, th=.5, dilation_kernel_size=161, erosion_kernel_size=81
):
    """
    Estimate the activity of a source based on the prior of a spatial mixture
    model as described in [boeddeker22].

    Args:
        prior (numpy.ndarray):
            Prior of one class of a spatial mixture model
        th (float):
            Threshold for the priors to decide whether the source is
            active of inactive
        dilation_kernel_size (int):
            Size of the dilation kernel used to smooth the estimated activity.
            Must be an odd number.
        erosion_kernel_size (int):
            Size of the erosion kernel used to smooth the estimated activity
            Must be an odd number.

    Returns:
        Estimate of the activity of the source belonging to the prior
    """
    activity = erode(
        dilate(prior >= th, dilation_kernel_size), erosion_kernel_size
    )
    return activity
