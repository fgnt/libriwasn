#!/bin/bash

echo "Creating md5checksum file"
echo "70d44a07ab906cda2385a7e7b4a431bd  LibriWASN_200_0L.zip">check.md5
echo "966d40081d67b71f5d337610cd8fb176  LibriWASN_200_0S.zip">>check.md5
echo "e9f0a19c2348a5cd0c9b9e12740a9d72  LibriWASN_200_OV10.zip">>check.md5
echo "7b6fcf5357d7686fa14792c019c8b9c2  LibriWASN_200_OV20.zip">>check.md5
echo "0c3f95be84bb0500a4d8212085c2abcc  LibriWASN_200_OV30.zip">>check.md5
echo "0a4d911240a309397d24c192a96fec11  LibriWASN_200_OV40.zip">>check.md5
echo "2ae30f25ea88d463d8b6f3c79286f160  LibriWASN_800_0L.zip">>check.md5
echo "ec5ffca2ebe184ac1bbc416c61fdab18  LibriWASN_800_0S.zip">>check.md5
echo "eba80ebd3cd868567fbfb3f46e222350  LibriWASN_800_OV10.zip">>check.md5
echo "a45f7d73d1dfa9c0c5a724788d1cd993  LibriWASN_800_OV20.zip">>check.md5
echo "5d681c70dd919af1080a129237d2ef32  LibriWASN_800_OV30.zip">>check.md5
echo "10efa8b713a6dc29a3e3ead4a744f050  LibriWASN_800_OV40.zip">>check.md5

echo "Creating Path"
mkdir -p LibriWASN/aux_files
echo "Start Additional file download"
wget https://zenodo.org/record/7960972/files/ccby4.txt -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/7960972/files/LibirWASN200_Picture.png -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/7960972/files/LibriWASN200_Positions.pdf -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/7960972/files/LibriWASN200_Setup.png -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/7960972/files/Positions200.pdf -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/7960972/files/Positions800.pdf -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/7960972/files/readme.txt -q --show-progress -P LibriWASN/aux_files/


echo "Start Audio file download"
wget https://zenodo.org/record/7960972/files/LibriWASN_200_0L.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_200_0S.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_200_OV10.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_200_OV20.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_200_OV30.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_200_OV40.zip -q --show-progress

wget https://zenodo.org/record/7960972/files/LibriWASN_800_0L.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_800_0S.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_800_OV10.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_800_OV20.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_800_OV30.zip -q --show-progress
wget https://zenodo.org/record/7960972/files/LibriWASN_800_OV40.zip -q --show-progress

echo "Checking md5sums"
if md5sum -c check.md5; then
    # MD5 matched
    echo "Unpack Data"
    FILES="LibriWASN_*.zip"
    for f in $FILES
    do
    echo "Unpack $f" # always double quote "$f" filename
        # do something on $f
        unzip $f
        rm $f
    done

else
    # MD5 didn't match - > ERROR
    echo "ERROR - md5sum not equal - CHECK download and retry."
fi

echo "Clean up"
rm check.md5

echo "Start download of LibriCSS"
wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l" -O for_release.zip && rm -rf /tmp/cookies.txt

echo "Unpack LibriCSS"
unzip for_release.zip
rm for_release.zip

echo "Adjust folder structure"
mv LibriWASN/200 LibriWASN/libriwasn_200
mv LibriWASN/800 LibriWASN/libriwasn_800
mv for_release LibriCSS

