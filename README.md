# libriwasn
Tools and scripts for the LibriWASN data set from zenodo

Installation
========

How to extract the files on Linux OS

  1.) Download file "DownloadLibriWASN.sh" to the desired path, e.g., /your/database/path/
  
  2.) Adjust permission for execution: chmod u+x DownloadLibriWASN.sh
  
  3.) Execute from shell: ./DownloadLibriWASN.sh
  
 This will download all files, check sanity by md5sum and uncompresses the files to /your/database/path/LibriWASN/


Citation
========

To cite this implementation, you can cite the following paper::

    @InProceedings{SchTgbHaeb2023,
      Title     = {LibriWASN: A Data Set for Meeting Separation, Diarization, and Recognition with Asynchronous Recording Devices},
      Author    = {Joerg Schmalenstroeer and Tobias Gburrek and Reinhold Haeb-Umbach},
      Booktitle = {ITG conference on Speech Communication (ITG 2023)},
      Year      = {2023},
      Month     = {Sep},
    }

To view the paper for a preview see arXiv <http://arxiv.org/abs/2308.10682>.
