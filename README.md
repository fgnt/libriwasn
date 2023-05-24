# libriwasn
Tools and scripts for the LibriWASN data set from zenodo


How to extract the files on Linux OS

  1.) Download file "DownloadLibriWASN.sh" to the desired path, e.g., /your/database/path/
  2.) Adjust permission for execution: chmod u+x DownloadLibriWASN.sh
  3.) Execute from shell: ./DownloadLibriWASN.sh
  
 This will download all files, check sanity by md5sum and uncompresses the files to /your/database/path/LibriWASN/
