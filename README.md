<h1 align="center">LibriWASN</h1> 
<h3 align="center">A Data Set for Meeting Separation, Diarization, and Recognition
with Asynchronous Recording Devices</h3>

**NOTE:** This repository currently is **under construction**.
We will update and extend the code within the next weeks.


Tools and reference meeting transcription pipeline of the LibriWASN data set ([preprint](http://arxiv.org/abs/2308.10682), [Zenodo data set link](https://zenodo.org/record/7960972)).

The LibriWASN data set  consists of recordings of the same audio signals which also were played back to record the [LibriCSS](https://github.com/chenzhuo1011/libri_css) data set. 
The data was recorded by nine different devices (five smartphones with a single recording channel and four microphone arrays) resulting in 29 audio channels in total.
Note that the  sampling clocks of the different devices are not synchronized so that there exists a sampling rate offset (SRO) between the recordings of different devices.


Zenodo
======
The data set and auxiliary materials are availabe on [Zenodo](https://zenodo.org/record/7960972).  
Available auxiliary:
   * Pictures of the recording setups
   * Speaker and microphone position information 
   * Ground-truth diarization information of who speaks when


Download
========

How to extract the files on Linux OS

  1.) Download file "DownloadLibriWASN.sh" to the desired path, e.g., /your/database/path/
  
  2.) Adjust permission for execution: chmod u+x DownloadLibriWASN.sh
  
  3.) Execute from shell: ./DownloadLibriWASN.sh
  
 This will download all files, check sanity by md5sum and uncompresses the files to /your/database/path/LibriWASN/


Citation
========

If you are using the LibriWASN data set or this code please cite the following paper:

    @InProceedings{SchTgbHaeb2023,
      Title     = {LibriWASN: A Data Set for Meeting Separation, Diarization, and Recognition with Asynchronous Recording Devices},
      Author    = {Joerg Schmalenstroeer and Tobias Gburrek and Reinhold Haeb-Umbach},
      Booktitle = {ITG conference on Speech Communication (ITG 2023)},
      Year      = {2023},
      Month     = {Sep},
    }