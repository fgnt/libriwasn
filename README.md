<h1 align="center">LibriWASN</h1> 
<h3 align="center">A Data Set for Meeting Separation, Diarization, and Recognition
with Asynchronous Recording Devices</h3>

**NOTE:** This repository currently is **under construction**.
We will update and extend the code within the next weeks.


Tools and reference meeting transcription pipeline of the LibriWASN data set ([preprint](http://arxiv.org/abs/2308.10682), [Zenodo data set link](https://zenodo.org/record/7960972)).

The LibriWASN data set  consists of recordings of the same audio signals which also were played back to record the [LibriCSS](https://github.com/chenzhuo1011/libri_css) data set. 
The data was recorded by nine different devices (five smartphones with a single recording channel and four microphone arrays) resulting in 29 audio channels in total.
Note that the  sampling clocks of the different devices are not synchronized so that there exists a sampling rate offset (SRO) between the recordings of different devices.


# Zenodo
The data set and auxiliary materials are available on [Zenodo](https://zenodo.org/record/7960972).
Available auxiliary:
   * Pictures of the recording setups
   * Speaker and microphone position information 
   * Ground-truth diarization information of who speaks when

# Installation
Clone the repository:
```bash
git clone https://github.com/fgnt/libriwasn.git
```

Install package:
```bash
pip install -e ./libriwasn
```

In order to calculate the concatenated minimum-Permutation Word Error Rate (cpWER), we utilize the [meeteval package](https://github.com/fgnt/meeteval).
This can be installed in the following way:
```bash
pip install cython
git clone https://github.com/fgnt/meeteval
pip install -e ./meeteval[cli]
```

# Download
To download the LibriWASN data set we provide two options stated below.
Note that the LibriCSS is addtionally downloaded because it is used as reference in the experiments and its transcriptions are also used for the LibriWASN data.

##### Download using Python
To download the data to your desired direcetory, e.g., */your/database/path/*, run the following command:
```bash 
python -m libriwasn.databases.download -db /your/database/path/
```

##### Download on Linux OS

  1. Download file *DownloadLibriWASN.sh* to your desired path where the data should be stored, e.g., */your/database/path/*
  
  2. Adjust permission for execution: *chmod u+x DownloadLibriWASN.sh*
  
  3. Execute *./DownloadLibriWASN.sh* from shell. This will download all files, check sanity by md5sum and extract the files to */your/database/path/*.


# Database structure
The downloaded data has the following database structure w.r.t. the path your desired database path:
```
├── LibriWASN
│   ├── aux_files # Additional information about the LibriWASN data set
│   │   ├── LibirWASN200_Picture.png
│   │   ├── ...
│   │   └── Positions800.pdf
│   ├── libriwasn_200 # The LibriWASN^200 data set
│   │   ├── 0L # Different overlap conditionons 
│   │   │    ├── <session0 folder> 
│   │   │    │    ├── record
│   │   │    │    │    ├── Nexus_ntlab_asn_ID_0.wav # (Multi-channel) audio signal(s) recorded by the different devices
│   │   │    │    │    ├── ...
│   │   │    │    │    └── Xiaomi_ntlab_asn_ID_0.wav
│   │   │    │    └── vad
│   │   │    │         └── speaker.csv # Ground-truth diarization information
│   │   │    ├── ...
│   │   │    └── <session9 folder>
│   │   ├── ...
│   │   └── OV40
│   └── libriwasn_800 # The LibriWASN^800 data set
│       ├── 0L 
│       │    ├── <session0 folder> 
│       │    │    └── record
│       │    │         ├── Nexus_ntlab_asn_ID_0.wav
│       │    │         ├── ...
│       │    │         └── Xiaomi_ntlab_asn_ID_0.wav
│       │    ├── ...
│       │    └── <session9 folder>
│       ├── ...
│       └── OV40
└── LibriCSS # The LibriCSS data set
    ├── 0L
    │    ├── <session0 folder>
    │    │    ├── clean
    │    │    │    ├── each_spk.wav # Signals which were played back to record LibriCSS and LibriWASN
    │    │    │    └── mix.wav
    │    │    ├── record
    │    │    │    └── raw_recording.wav # Multi-channel signal recorded by the microphone array
    │    │    └── transcription
    │    │    │    ├── meeting_info.txt # Transcription used for LibriCSS and LibriWASN
    │    │    │    └── segments
    │    ├── ...
    │    └── <session9 folder>
    ├── ...
    ├── OV40
    ├── all_res.json
    ├── redme.txt
    └── segment_libricss.py
```
# Usage of the data set
To run the reference system you first have to create a json file for the database:
```bash
python -m libriwasn.databases.create_json -db /your/database/path/
```

The generated json file has the following structure:
```python
{
    "datasets": {
        "libricss": {
            example_id: {
                "audio_path": {
                    "clean_observation": ...,  # clean speech mixture
                    "observation": ...,        # recorded multi-channel signal
                    "played_signals": ...      # clean signal per speaker
                },
                "num_samples": { 
                    "clean_observation": ...,
                    "observation": ...,
                    "original_source": [..., ...],
                    "played_signals": ...
                },
                "onset": {  # Onset of utterance in samples
                    "original_source": [..., ...]
                }
                "overlap_condition": ..., # 0L, 0S, OV10, OV20, OV30 or OV40
                "session": ..., # session0, session1, ... or session9 
                "source_id": [..., ...], 
                "speaker_id": [..., ...], 
                "transcription": [..., ...],
            }
        },
        "libriwasn200": {
            "audio_path": {
                "clean_observation": ...,
                "observation": {
                    "Nexus": ...,
                    "Pixel6a": ...,
                    "Pixel6b": ...,
                    "Pixel7": ...,
                    "Soundcard": ...,
                    "Xiaomi": ...,
                    "asnupb2": ...,
                    "asnupb4": ...,
                    "asnupb7": ...
                },
                "played_signals": ...
            },
            ...
        },
        "libriwasn800": {
            "audio_path": {
                "clean_observation": ...,
                "observation": {
                    "Nexus": ...,
                    "Pixel6a": ...,
                    "Pixel6b": ...,
                    "Pixel7": ...,
                    "Soundcard": ...,
                    "Xiaomi": ...,
                    "asnupb2": ...,
                    "asnupb4": ...,
                    "asnupb7": ...
                },
                "played_signals": ...
            },
            ...
        }, 
    }
}
```
Note that the onsets of the utterances and also the lengths of the utterances (num_samples) fit to the recording of the *Soundcard*. 
Due to sampling rate offsets (SROs) and sampling time offsets (STOs) of the other devices w.r.t. the *Soundcard* both quantities will not perfectely fit to the recordings of the other devices.  

Create a segmental time mark (STM) file for the reference transcription:
```bash
python -m libriwasn.databases.write_ref_stm --json_path /your/database/path/libriwasn.json
```
This STM file is used when calculating the  concatenated minimum-Permutation Word Error Rate (cpWER).

# Reference sytem
In the following the usage of the reference system will be explained.
Note that the corresponding python scripts also serve as examples showing how to use the database and the different parts of the reference system (mask estimation, beamforming, ...). 


##### Example (LibriWASN<sup>200</sup>: Sys-2)
To run experiments using the reference system change your working directory to your desired experiment directory, e.g. */your/libriwasn_experiment/path/*.
Afterwards, run the following command, for example, to separate the speakers' signals using sys-2 of the experimental section of the paper on LibriWASN<sup>200</sup>:
```bash
python -m libriwasn.reference_system.separate_sources with sys2_libriwasn200 db_json=/your/database/path/libriwasn.json
```
This script will write the separated singals of the speakers into the directory */your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/* and create a json file (*/your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/per_utt.json*) which contains all necessary information to evalute the meeting transcription performance.
Note that the path of the json file is also outputed in the console when the script is finished,

As next step, the separated signals can be trancribed using the created json file as input:
```bash
python -m libriwasn.reference_system.transcribe --json_path /your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/per_utt.json
```
This will create an STM file for the transcription hypothesis: */your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/stm/hyp.stm*.
Again the path of the STM file is outputed in the console when the script is finished.

Finally, the cpWER can be calculated:
```bash
meeteval-wer cpwer -h /your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/stm/hyp.stm -r /your/database/path/ref_transcription.stm
```
This command produces a json file for the average cpWER (*/your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/stm/hyp_cpwer.json*) and another file with a more detailed description per session (*/your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/stm/hyp_cpwer_per_reco.json*).
Finally, run the following command in order to get the cpWER per overlap condition:
```bash
python -m libriwasn.reference_system.wer_per_overlap_condition --json_path /your/libriwasn_experiment/path/separated_sources/sys2_libriwasn200/stm/hyp_cpwer_per_reco.json
```

##### Overview of experiments
To generate the audio data for the different experiments described in the paper run one of the following commands

Clean:
```bash
python -m libriwasn.reference_system.segment_meetings with clean db_json=/your/database/path/libriwasn.json
```
LibriCSS Sys-1:
```bash
python -m libriwasn.reference_system.segment_meetings with libricss db_json=/your/database/path/libriwasn.json
```
LibriCSS Sys-2:
```bash
python -m libriwasn.reference_system.separate_sources with sys2_libriwasn200 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>200</sup> Sys-1:
```bash
python -m libriwasn.reference_system.segment_meetings with libriwasn200 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>200</sup> Sys-2:
```bash
python -m libriwasn.reference_system.separate_sources with sys2_libriwasn200 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>200</sup> Sys-3:
```bash
python -m libriwasn.reference_system.separate_sources with sys3_libriwasn200 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>200</sup> Sys-4:
```bash
python -m libriwasn.reference_system.separate_sources with sys4_libriwasn200 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>800</sup> Sys-1:
```bash
python -m libriwasn.reference_system.segment_meetings with slibriwasn800 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>800</sup> Sys-2:
```bash
python -m libriwasn.reference_system.separate_sources with sys2_libriwasn800 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>800</sup> Sys-3:
```bash
python -m libriwasn.reference_system.separate_sources with sys3_libriwasn800 db_json=/your/database/path/libriwasn.json
```
LibriWASN<sup>800</sup> Sys-4:
```bash
python -m libriwasn.reference_system.separate_sources with sys4_libriwasn800 db_json=/your/database/path/libriwasn.json
```

# Citation
If you are using the LibriWASN data set or this code please cite the following paper:

    @InProceedings{SchTgbHaeb2023,
      Title     = {LibriWASN: A Data Set for Meeting Separation, Diarization, and Recognition with Asynchronous Recording Devices},
      Author    = {Joerg Schmalenstroeer and Tobias Gburrek and Reinhold Haeb-Umbach},
      Booktitle = {ITG conference on Speech Communication (ITG 2023)},
      Year      = {2023},
      Month     = {Sep},
    }