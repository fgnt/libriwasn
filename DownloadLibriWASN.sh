#!/bin/bash

echo "Creating md5checksum file"
echo "2327be91485110031181782c1605bd86  LibriWASN_200_0L.zip">check.md5
echo "531549b8528a10e1eb9ee6ad9f800073  LibriWASN_200_0S.zip">>check.md5
echo "b6eecbd9dd4a1a2074b7cd681b722c5c  LibriWASN_200_OV10.zip">>check.md5
echo "1a8ba4ab2d74300fbe8fdb1de31d3379  LibriWASN_200_OV20.zip">>check.md5
echo "8cc0d8561ac9571561e8d5ed628404db  LibriWASN_200_OV30.zip">>check.md5
echo "9d33cdaea1b1c968d8f885c80ce4d761  LibriWASN_200_OV40.zip">>check.md5
echo "e9cbaf2c4e35aeea0ac14c7edf9c181f  LibriWASN_800_0L.zip">>check.md5
echo "aa8442d009dd669c14f680ba20e2143f  LibriWASN_800_0S.zip">>check.md5
echo "5e36a163669bbfaad01c617a6f7e4696  LibriWASN_800_OV10.zip">>check.md5
echo "f8efb703b0dca20a03bbcb2f9ef07a07  LibriWASN_800_OV20.zip">>check.md5
echo "c76c0a22da2e7299b06fe239b7681615  LibriWASN_800_OV30.zip">>check.md5
echo "d3fdc9b79c33025eb0fa353e31a80c71  LibriWASN_800_OV40.zip">>check.md5

echo "Creating Path"
mkdir -p LibriWASN/aux_files
echo "Start Additional file download"
wget https://zenodo.org/record/10952434/files/ccby4.txt -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/10952434/files/LibirWASN200_Picture.png -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/10952434/files/LibriWASN200_Positions.pdf -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/10952434/files/LibriWASN200_Setup.png -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/10952434/files/Positions200.pdf -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/10952434/files/Positions800.pdf -q --show-progress -P LibriWASN/aux_files/
wget https://zenodo.org/record/10952434/files/readme.txt -q --show-progress -P LibriWASN/aux_files/


echo "Start Audio file download"
wget https://zenodo.org/record/10952434/files/LibriWASN_200_0L.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_200_0S.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_200_OV10.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_200_OV20.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_200_OV30.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_200_OV40.zip -q --show-progress

wget https://zenodo.org/record/10952434/files/LibriWASN_800_0L.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_800_0S.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_800_OV10.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_800_OV20.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_800_OV30.zip -q --show-progress
wget https://zenodo.org/record/10952434/files/LibriWASN_800_OV40.zip -q --show-progress

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

echo "Start download of LibriCSS via https://docs.google.com/uc?export=download&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l"
# wget --load-cookies /tmp/cookies.txt "https://docs.google.com/uc?export=download&confirm=$(wget --quiet --save-cookies /tmp/cookies.txt --keep-session-cookies --no-check-certificate 'https://docs.google.com/uc?export=download&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l' -O- | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1\n/p')&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l" -O for_release.zip && rm -rf /tmp/cookies.txt

# echo "Unpack LibriCSS"
# unzip for_release.zip
# rm for_release.zip

echo "Adjust folder structure"
mv LibriWASN/200 LibriWASN/libriwasn_200
mv LibriWASN/800 LibriWASN/libriwasn_800
# mv for_release LibriCSS

