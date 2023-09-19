import numpy as np


def ref_time_to_mic_time(
        sample_idx, sro, block_size_sro_traj=8192, block_shift_sro_traj=2048
):
    """
    Shift the value of the given sample index by the SRO-induced time shift

    Args:
        sample_idx:
            Sample index which should be manipulated w.r.t. the given SRO
        sro:
            SRO-trajctory on a block-wise level
        block_size_sro_traj:
            Size of one block belonging to the SRO-trajctory
        block_shift_sro_traj:
            Shift of one block belonging to the SRO-trajctory

    Returns:
        Sample index + SRO-induced time-shift
    """
    if (block_size_sro_traj - block_shift_sro_traj) // 2 > sample_idx:
        block_idx = 0
    else:
        block_idx = (
                (sample_idx - (block_size_sro_traj - block_shift_sro_traj) // 2)
                // block_shift_sro_traj
        )
    block_idx = int(block_idx)
    center_block = block_size_sro_traj / 2 + block_idx * block_shift_sro_traj

    if np.isscalar(sro):
        shift_sro = (sro * 1e-6 * block_size_sro_traj / 2
                     + block_idx * block_shift_sro_traj * sro * 1e-6)
        shift_sro += (sample_idx - center_block) * sro
    else:
        shift_sro = sro[0] * 1e-6 * block_size_sro_traj / 2
        if block_idx >= 1:
            shift_sro += \
                np.sum(sro[1:block_idx+1] * 1e-6) * block_shift_sro_traj
        shift_sro += (sample_idx - center_block) * sro[block_idx] * 1e-6
    sample_idx = np.round(sample_idx + shift_sro)
    return int(sample_idx)
