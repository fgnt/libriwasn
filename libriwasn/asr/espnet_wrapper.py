import itertools
import socket

import dlp_mpi
from espnet_model_zoo.downloader import ModelDownloader
from espnet2.bin.asr_inference import Speech2Text
import numpy as np
import paderbox as pb
from paderwasn.synchronization.utils import VoiceActivityDetector
import torch


def segment_audio(sig, max_len=192000, min_pause=4000, min_seg_len=16000):
    """
    Cut a speech signal into smaller segments if the signal is longer than an
    upper limit. Therefore, an energy-based voice activity detection is used to
    find speech pauses. Each speech pause which has a certain length can be
    used as point where the signal could be splitted. This segmentation is
    needed for the ASR system defined below as described in [boeddeker23]: 'For
    the pretrained ASR system named “base”, we observed a strange behavior for
    long segments, hence we split long ctivities at silence positions,
    according to  At,k, such that no segment is longer than 12s.'

    @article{boeddeker23,
      title={TS-SEP: Joint Diarization and Separation Conditioned
             on Estimated Speaker Embeddings},
      author={Christoph Boeddeker, Aswin Shanmugam Subramanian, Gordon Wichern,
              Reinhold Haeb-Umbach, and Jonathan Le Roux},
      journal={IEEE Transactions on audio, speech, and language processing},
      year={2023},
      publisher={IEEE}
    }

    Args:
        sig:
            Signal wo be segmented
        max_len:
            Maximum segment length. Note that there might be situations
            in which there are no sufficient speech pauses to guarantee that
            all segments are smaller than max_len. In this case also segments
            which are longer than max_len are allowed. We experienced that
            the ASR model also works properly if the segments are up
            to 24s long.
        min_pause:
            Minimum length of a speech pause to be considered as possible point
            where the signal can be spliTted.
        min_seg_len:
            Minimum allowed length for a speech segment

    Returns:
        The segmented signal
    """
    poss_points_2_cut = []
    num_cuts = int(np.ceil(len(sig) / max_len) - 1)
    if num_cuts == 0:
        return [sig,]
    energy = np.sum(
        pb.array.segment_axis(sig[abs(sig) > 1e-3], 1024, 256, end='cut') ** 2,
        axis=-1
    )
    th = 3 * np.min(energy)
    vad = VoiceActivityDetector(th, len_smooth_win=0)
    act = vad(sig)
    for (on, off) in pb.array.interval.ArrayInterval(act == 0).intervals:
        if off - on >= min_pause:
            poss_points_2_cut.append((on + off) // 2)
    num_cuts = np.minimum(num_cuts, len(poss_points_2_cut))
    if num_cuts == 0:
        return [sig,]
    while True:
        if num_cuts == 1:
            point = \
                np.argmin([abs(p - len(sig) // 2) for p in poss_points_2_cut])
            point = poss_points_2_cut[point]
            segments = [sig[:point], sig[point:]]
            if np.min([len(seg) for seg in segments]) < min_seg_len:
                return [sig, ]
            return segments
        else:
            combinations = []
            min_lens = []
            cs = itertools.combinations(poss_points_2_cut, r=num_cuts)
            for combination in cs:
                combination = [0, ] + list(combination) + [len(sig), ]
                cost = np.min([combination[i] - combination[i - 1] for i in
                               range(1, len(combination))])
                min_lens.append(cost)
                combinations.append(combination)
            choice = np.argmax(min_lens)
            points_2_cut = combinations[choice]
            segments = [sig[points_2_cut[i]:points_2_cut[i + 1]]
                        for i in range(len(points_2_cut) - 1)]
            cost = min_lens[choice]
            if cost < min_seg_len:
                num_cuts -= 1
                if num_cuts == 0:
                    return [sig, ]
            else:
                return segments


class ESPnetASR:
    def __init__(self, model_dir=None, enable_gpu=False):
        """
        Wrapper around the Espnet to  use the pretrained model from [watanabe201]

        @misc{watanabe201,
          author    = {Shinji Watanabe},
          title     = {{ESPnet2 pretrained automatic speech recognition model,
                        https://doi.org/10.5281/zenodo.3966501}},
          month     = jul,
          year      = 2020,
          publisher = {Zenodo},
          doi       = {10.5281/zenodo.3966501},
          url       = {https://doi.org/10.5281/zenodo.3966501}
        }
        Args:
            model_dir:
                Directory where the pretrained ASR model should be stored.
                By default the model is downloaded into the directory of the
                 espnet_modelzoo module.
            enable_gpu:
                If True GPU-based decoding is used if a GPU is available.
        """
        model_tag = ('Shinji Watanabe/librispeech_asr_train_asr_'
                     'transformer_e18_raw_bpe_sp_valid.acc.best')
        d = ModelDownloader(model_dir)
        self.espnet_model_kwargs = d.download_and_unpack(model_tag)
        self.enable_gpu = enable_gpu

        if not dlp_mpi.IS_MASTER or dlp_mpi.SIZE == 1:
            try:
                self.speech2text = self.load_model()
            except EOFError as e:
                # Sometimes following Error occurs, when multiple workers
                # are used:
                #     EOFError: Ran out of input

                raise Exception(
                    socket.gethostname(),
                    self.espnet_model_kwargs.get('asr_model_file', '???')
                ) from e

            except RuntimeError as e:
                # Sometimes the following Error occurs:
                #     RuntimeError: unexpected EOF, expected 495801 more bytes.
                #     The file might be corrupted.
                # Issue reports can be found online, where it is reproducable.

                print('#' * 79)
                print(
                    'WARNING: Load failed. Retry a second time in two seconds.'
                )
                print('#' * 79)
                import time
                time.sleep(2)
                self.speech2text = self.load_model()

    def load_model(self):
        device = 'cpu'
        if self.enable_gpu and torch.cuda.is_available():
            assert dlp_mpi.SIZE == 1, \
                'Parellelization is not supported for GPU-based decoding'
            device = 'cuda'
        speech2text = Speech2Text(  # Speech2Text.from_pretrained
            **self.espnet_model_kwargs,
            # Decoding parameters are not included in the model file
            device=device,
            maxlenratio=0.0,
            minlenratio=0.0,
            beam_size=20,
            ctc_weight=0.3,
            lm_weight=0.5,
            penalty=0.0,
            nbest=1,
        )
        return speech2text

    def apply_asr(self, file):
        """
        Apply the ASR-system

        Args:
            file:
                File in which the signal, to be transcribed, is stored.

        Returns:
            The transcription belonging to the signal stored in the file.
        """
        speech = pb.io.load_audio(file)
        assert speech.ndim == 1, speech.shape
        text = ''
        segments = segment_audio(speech)
        for seg in segments:
            nbests = self.speech2text(seg)
            text_segment, *_ = nbests[0]
            if len(text) == 0:
                text += text_segment
            else:
                text += ' ' + text_segment
        return text
