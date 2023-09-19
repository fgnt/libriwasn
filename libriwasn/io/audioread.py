import paderbox as pb


def load_signals(
        example, devices=None, ref_device=None,
        single_ch=True, return_devices=False
):
    assert isinstance(example['audio_path']['observation'], dict)
    audio_paths = example['audio_path']['observation']
    if isinstance(devices, str):
        devices = [devices, ]
    if devices is None:
        devices = [device_id for device_id in audio_paths.keys()]
    if ref_device is not None:
        assert ref_device in devices
        devices.remove(ref_device)
        devices = [ref_device,] + devices
    sigs = []
    for device in devices:
        sigs_device = pb.io.load_audio(audio_paths[device])
        if sigs_device.ndim == 1:
            sigs.append(sigs_device)
        elif single_ch:
            sigs.append(sigs_device[0])
        else:
            sigs.append(sigs_device)
    if len(sigs) == 1:
        sigs = sigs[0]
    if return_devices:
        return sigs, devices
    return sigs