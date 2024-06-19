import paderbox as pb
import numpy as np

def load_signals(
        example, devices=None, ref_device=None,
        single_ch=True, return_devices=False, same_len=False
):
    """
    Load audio signals from libriwasn and select devices and number of channels

    Args:
        example (dict):
            Entry of libriwasn json specifying the parameters of the current
            example which needs to include the pathes to the audio files.

        devices (None, str, list):
            If None, all devices provided in libriwasn are loaded.
            If str, only load signals of this device.
            If list, only load the devices provided by the list elements.

        ref_device (str):
            Reference device that is used during processing and whose
            signals are returned first in the result.

        single_ch (bool, list):
            If False, load all channels for each device. Otherwise,
            only the first channel is loaded. If a device list is provided
            and single_ch is bool, the condition gets applied for all devices.
            Alternatively, a list with each element of type bool stating the
            channel selection for each device in the order of the device list.

        return_devices (bool):
            If True, return list of the devices in the order of the loaded
            signals with reference device in the first place.

        same_len (bool):
            If True, return numpy.array of signals where signals
            are padded to the maximum length of all channels.

    Returns:
        Audio signals of selected devices and channels
        [ [ref_device_channel_1 ...], [device_1_channel_1, ...], ...]

    """

    assert isinstance(example['audio_path']['observation'], dict)
    audio_paths = example['audio_path']['observation']
    if isinstance(devices, list):
        _devices = devices.copy()
    if isinstance(devices, str):
        _devices = [devices, ]
        assert devices in audio_paths.keys()
    if devices is None:
        _devices = [device_id for device_id in audio_paths.keys()]
    if ref_device is not None:
        assert ref_device in _devices
        _devices.remove(ref_device)
        _devices = [ref_device,] + _devices
    sigs = []
    if type(single_ch) != list:
        single_ch = [single_ch for i in range(len(_devices))]
    assert len(single_ch) == len(_devices)
    for use_single_channel, device in zip(single_ch, _devices):
        sigs_device = pb.io.load_audio(audio_paths[device])
        if sigs_device.ndim == 1:
            sigs.append(sigs_device)
        elif use_single_channel:
            sigs.append(sigs_device[0])
        else:
            sigs.append(sigs_device)
    if len(sigs) == 1:
        sigs = sigs[0]
    elif same_len:
        num_chs = 0
        max_len = 0
        for _sig in sigs:
            if _sig.ndim == 1:
                num_chs += 1
                max_len = np.maximum(max_len, len(_sig))
            else:
                num_chs += _sig.shape[0]
                max_len = np.maximum(max_len, _sig.shape[-1])

        sigs_temp = np.zeros((num_chs, max_len))
        ch = 0
        for dev_sig in sigs:
            if dev_sig.ndim == 2:
                for ch_sig in dev_sig:
                    sigs_temp[ch, :len(ch_sig)] = ch_sig
                    ch += 1
            else:
                sigs_temp[ch, :len(dev_sig)] = dev_sig
                ch += 1
        sigs = sigs_temp

    if return_devices:
        return sigs, _devices
    return sigs