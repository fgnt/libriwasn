import numpy as np

from libriwasn.utils import dilate, erode


def correlation_matrix_distance(mat_1, mat_2):
    """
    Correlation matrix distance from [herdin05], which can be used, for
    example, to measure the simliarity of two spatial covariance
    matrices (SCMs).

    @inproceedings{herdin05,
      author={Herdin, M. and Czink, N. and Ozcelik, H. and Bonek, E.},
      booktitle={2005 IEEE 61st Vehicular Technology Conference},
      title={Correlation matrix distance, a meaningful measure for evaluation
             of non-stationary {MIMO} channels},
      year={2005},
      volume={1},
      number={},
      pages={136-140 Vol. 1},
      doi={10.1109/VETECS.2005.1543265}}

    Args:
        mat_1 (numpy.ndarray):
            Correlation matrix (Shape: (... x N x N))
        mat_2 (numpy.ndarray):
            Correlation matrix (Shape: (... x N x N))

    Returns:
        Distance between mat_1 and mat_2 (Shape: (...))
    """
    mat_1 = mat_1 / np.linalg.norm(mat_1, axis=(-2, -1), keepdims=True)
    mat_2 = mat_2 / np.linalg.norm(mat_2, axis=(-2, -1), keepdims=True)
    trace = np.einsum('...ij,...ij', mat_1, mat_2.conj()).real
    return 1 - trace


def cluster_scms(scms, merge_th=.5):
    """
    Cluster a set of segment-wise SCM estimates based on the correlation
    matrix distance from [herdin05]. This is used to identify which segments
    belong to the same source position which is directly linked to the spatial
    information represented by the SCM. Assuming fixed source positions this
    results in a first estimate of who speaks which can be used to initialize
    a spatial mixture model.

    Args:
        scms (list):
            List of tuples consisting of (SCM, Segment-ID). SCM is an array of
            shape (number of frequency bins x number of channels
            x number of channels). Segment-ID is an integer which defines to
            which segment the SCM belongs.
        merge_th (float):
            Threshold for the relative intersection ratio between two
            estimates, which segments to of to the speaker, to decide whether
            two segments belong two the same speaker

    Returns:
        List of SCM clusters
    """
    # Estimate the pair-wise similarities between the segment-wise SCMs
    sim_mat = np.zeros((len(scms), len(scms)))
    for i in range(len(scms)):
        for j in range(i+1, len(scms)):
            scm_i = scms[i][0]
            scm_j = scms[j][0]
            sim_mat[i, j] = sim_mat[j, i] = np.mean(
                correlation_matrix_distance(scm_i, scm_j)
            )

    # Decide whether two segments belong to the same source position by
    # comparing the similarity to a threshold. This leads to an activity
    # pattern for each segment indicating in which segments the same source
    # is active. The threshold is derived from the matrix of all similarities
    # utilizing the fact that the are mostly entries belonging to two segments
    # which do not correspond to the same source position. Thus, similarities,
    # which indicate that the same source position belongs to two segments,
    # can be interpreted as outliers. Therefore, the threshold is chosen based
    # on the 3-sigma-rule. Note, that the median absolute deviation is used
    # rather than the standard deviation since it is more robust against
    # outliers.
    th = np.median(sim_mat) - 3 * np.mean(np.abs(sim_mat - np.median(sim_mat)))
    same_spk = sim_mat < th

    # Leader-follower clustering
    clusters = []
    for i, sim in enumerate(same_spk):
        if len(clusters) == 0:
            new_cluster = [[i, ], [sim, ]]
            clusters.append(new_cluster)
            continue
        for cluster in clusters:
            # The already found clusters are represented by the median of the
            # activity patterns of their members
            sim_ref = np.median(cluster[1], 0) >= .5

            # The decision whether a segment belongs to a cluster is made based
            # on the relative intersection of its activity pattern and the
            # actvity pattern belonging to the cluster.
            intersection = np.sum(sim * sim_ref)
            relative_intersection = \
                intersection / np.minimum(np.sum(sim), np.sum(sim_ref) + 1e-18)
            if relative_intersection > merge_th:
                cluster[0].append(i)
                cluster[1].append(sim)
                break
        else:
            new_cluster = [[i, ], [sim, ]]
            clusters.append(new_cluster)
    return clusters


def activities_to_soft_masks(
        activities, num_classes, maximum=.8, fft_size=1024,
        kernel_size_erosion=63, kernel_size_dilation=63
):
    """
    Create time-frequency masks from given activities of the  speakers.
    Therefore, the activity is repeated along the frequency dimension.
    Additionally, a class for the  noise, which is assumed to be always active,
    is added. The values of the time-frequency masks have a certain maximum
    value. Furthermore, the values of the masks are also always non-zero even
    if a source is inactive.

    Args:
        activities (numpy.ndarray):
            A first estimate of the spekers' acvtivities (Shape:
            (number of speakers x number of frames))
        num_classes (int):
            Number of classes. This should ideally be the number of speakers
            plus one for the extra class for the noise.
        maximum (float):
            Maximum value of the time-frequency masks
        fft_size (int):
            Size of the FFT to specify the amount of frequency bins
        kernel_size_erosion (int):
            Size of the dilation kernel used to smooth the estimated activity.
            Must be an odd number.
        kernel_size_dilation (int):
            Size of the erosion kernel used to smooth the estimated activity
            Must be an odd number.

    Returns:
        soft_masks (numpy.ndarray):
            First estimate of the time-frequency masks (Shape:
            (fft_size / 2 + 1 x num_classes x number of frames))
        activities (numpy.ndarray):
            Input activities after apply the dilation and erosion function.
    """
    assert len(activities) <= num_classes - 1, \
        'len(activities) must be smaller than num_classes'
    eps = np.finfo(np.float64).eps

    # Smooth the activities using a dialtion and a erosion operation. This is
    # basically used to bridge short pauses of the activities
    activities_smoothed = np.zeros_like(activities)
    for i, activity in enumerate(activities):
        activities_smoothed[i] = \
            erode(dilate(activity, kernel_size_dilation), kernel_size_erosion)
    activities = activities_smoothed

    # If there are less sources given by activities than num_classes, add
    # additional classes, which are always inactive.
    if len(activities) < num_classes - 1:
        activities = np.pad(
            activities, ((0, num_classes - 1 - len(activities)), (0, 0))
        )

    # Add an extra class for the nosie
    activities = np.pad(activities, ((0, 1), (0, 0)), constant_values=1)

    # Create time masks by setting the mask value to
    # (maximum / number of active sources per frame) for all sources being
    # active within a frame. 
    soft_masks = \
        activities / np.maximum(np.sum(activities, axis=0, keepdims=True), eps)
    soft_masks[soft_masks > 0] *= maximum
    remainder = 1 - np.sum(soft_masks, 0)
    remainder = remainder / np.sum(soft_masks == 0, 0)
    for s in range(len(soft_masks)):
        time_mask = soft_masks[s] == 0
        soft_masks[s, time_mask] = remainder[time_mask]

    # Repeat time-masks along the frequency dimension
    soft_masks = np.tile(soft_masks[None], (fft_size // 2 + 1, 1, 1))
    return soft_masks, activities


def get_initialization(
        y, num_spk=8, seg_len=30, single_spk_th=.3, merge_th=.5
):
    """
    Get an initial estimate of time-frequency masks for each source. E.g., this
    can be used to initialize the posteriors of a spatial mixture model. The
    time-frequency masks are estimated based on estimates of the speakers'
    activities which are estimated by clustering segment-wise SCM estimates.

    Args:
        y (numpy.ndarray):
            STFT of the input signals (Shape: (number of channels x
            number of frames x FFT size / 2 + 1)). Note that only the
            non-redundant frequencies are used as input.
        num_spk (int):
            Number of speakers
        seg_len (int):
            Number of frames that form a segment used for SCM estimation
        single_spk_th (float):
            Threshold for the ratio between the largest and the second largest
            eigenvalue used to decide whether a speaker is dominant within a
            segment.
        merge_th (float):
            Threshold for the relative intersection ratio between two
            estimates, which segments to of to the speaker, to decide whether
            two segments belong two the same speaker

    Returns:
        initialization (numpy.ndarray):
            Initial estimate of time-frequency masks (Shape: FFT size / 2 + 1 x
            number of speakers + 1 x number of time frames)
        activities (numpy.ndarray):
            Estimated source activities (Shape: number of speakers + 1 x
            number of time frames)
    """
    num_segments = y.shape[1] // seg_len
    scms = []
    for seg_id in range(num_segments):
        # Segment the meeting into non-overlapping segments and estimate
        # an SCM for each segment
        segment = y[:, seg_id * seg_len:(seg_id + 1) * seg_len]
        scm = np.einsum('c t f, d t f  -> f c d', segment, segment.conj())

        # Perform a rank-1 approximation of the SCMs and check for dominance of
        # a single based on the ration of the largest and the second largest
        # eigenvalue.  If the ratio between both eignevalues is below a certain
        # threshold, the segment is assigned to the noise class.
        eig_vals, eig_vects = np.linalg.eigh(scm)
        if np.mean(eig_vals[:, -2] / eig_vals[:, -1]) <= single_spk_th:
            eig_vects[..., -1] *= eig_vects[:, 0, None, -1].conj()
            eig_vects[..., -1] /= \
                np.abs(eig_vects[..., -1]) + np.finfo(np.float64).eps
            scm_rank1 = np.einsum('f c, f d -> f c d',
                                  eig_vects[..., -1],
                                  eig_vects[..., -1].conj())
            scms.append((scm_rank1, seg_id))

    clusters = cluster_scms(scms, merge_th=merge_th)

    activities = np.zeros((len(clusters), y.shape[1]), bool)
    for i, cluster in enumerate(clusters):
        segments = [scms[i][1] for i in cluster[0]]
        for seg_id in segments:
            activities[i][seg_id*seg_len:(seg_id+1)*seg_len:] = 1

    # It might be that the clustering results in more classes than the number
    # of sources speakers. In this case the according to the
    order = np.argsort([np.sum(a)for a in activities])[::-1]
    activities = activities[order[:num_spk]]

    initialization, activities = \
        activities_to_soft_masks(activities, num_spk + 1)
    return initialization, activities
