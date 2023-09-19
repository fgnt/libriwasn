import numpy as np
import scipy
import paderbox as pb


def erode(activity, kernel_size):
    """
    Applies an erosion operation to a given activity

    Args:
        activity:
            Boolean array indicating the activity of a source
        kernel_size:
            Size of the erosion kernel. kernel_size must be an odd number.

    Returns:
        Activity after applying the erosion operation
    """
    assert kernel_size % 2 != 0, f'kernel_size ({kernel_size}) must be odd.'
    activity_eroded = pb.array.interval.zeros(shape=activity.shape)
    activity_intervals = \
        pb.array.interval.ArrayInterval(activity).normalized_intervals
    for (onset, offset) in activity_intervals:
        onset += (kernel_size - 1) // 2
        onset = np.maximum(onset, 0)
        offset -= (kernel_size - 1) // 2
        offset = np.minimum(offset, activity.shape)
        activity_eroded.add_intervals([slice(onset, offset)])
    return np.asarray(activity_eroded)


def dilate(activity, kernel_size):
    """
    Applies a dilation operation to a given activity

    Args:
        activity:
            Boolean array indicating the activity of a source
        kernel_size:
            Size of the dilation kernel. kernel_size must be an odd number.

    Returns:
        Activity after applying the dilation operation
    """
    assert kernel_size % 2 != 0, f'kernel_size ({kernel_size}) must be odd.'
    activity_dilated = pb.array.interval.zeros(shape=activity.shape)
    activity_intervals = \
        pb.array.interval.ArrayInterval(activity).normalized_intervals
    for (onset, offset) in activity_intervals:
        onset -= (kernel_size - 1) // 2
        onset = np.maximum(onset, 0)
        offset += (kernel_size - 1) // 2
        offset = np.minimum(offset, activity.shape)
        activity_dilated.add_intervals([slice(onset, offset)])
    return np.asarray(activity_dilated)


def solve_permutation(activities, ref_activities):
    """
    Solve the permutation between two sets of source activities

    Args:
        activities:
            Activities whose permutation should be solved
        ref_activities:
            Reference activities

    Returns:
        Permutation needed to reorder "activities"
    """
    if len(ref_activities) < len(activities):
        ref_activities = np.pad(
            ref_activities,
            ((0, len(activities) - len(ref_activities)), (0, 0)),
            'constant'
        )
    elif len(ref_activities) > len(activities):
        activities = np.pad(
            activities,
            ((0, len(ref_activities) - len(activities)), (0, 0)),
            'constant'
        )
    assert len(ref_activities) == len(activities), \
        (len(ref_activities), len(activities))
    equal_values = np.zeros((len(activities), len(activities)))
    for i, act in enumerate(activities):
        for j, ref_act in enumerate(ref_activities):
            equal_values[i, j] = np.sum(act == ref_act)
    _, best_permutation = \
        scipy.optimize.linear_sum_assignment(equal_values.T, maximize=True)
    return np.asarray(best_permutation)
