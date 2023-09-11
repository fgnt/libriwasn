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
The data set and auxiliary materials are availabe on [Zenodo](https://zenodo.org/record/7960972).  
Available auxiliary:
   * Pictures of the recording setups
   * Speaker and microphone position information 
   * Ground-truth diarization information of who speaks when

# Download
To download the LibriWASN data set we provide two options stated below.
Note that the LibriCSS is addtionally downloades because it is used as reference in the experiments and its transcriptions are also used for the LibriWASN data.

##### Download using Python
To download the data to your desired direcetory, e.g., */your/database/path/*, run the following command:
```bash 
python -m libriwasn.databases.download -db /your/database/path/
```

##### Download on Linux OS

  1. Download file *DownloadLibriWASN.sh* to your desired path where the data should be stored, e.g., */your/database/path/*
  
  2. Adjust permission for execution: *chmod u+x DownloadLibriWASN.sh*
  
  3. Execute *./DownloadLibriWASN.sh* from shell. This will download all files, check sanity by md5sum and extract the files to */your/database/path/*.


# Database Structure
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


# Citation
If you are using the LibriWASN data set or this code please cite the following paper:

    @InProceedings{SchTgbHaeb2023,
      Title     = {LibriWASN: A Data Set for Meeting Separation, Diarization, and Recognition with Asynchronous Recording Devices},
      Author    = {Joerg Schmalenstroeer and Tobias Gburrek and Reinhold Haeb-Umbach},
      Booktitle = {ITG conference on Speech Communication (ITG 2023)},
      Year      = {2023},
      Month     = {Sep},
    }