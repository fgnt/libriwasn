import hashlib
from pathlib import Path
import shutil
from subprocess import run

import click
from paderbox.io.download import download_file
from paderbox.io.download import extract_file
from paderbox.io.download import download_file_list
from tqdm import tqdm


def check_md5(file_name, check_sum, blocksize=8192):
    hasher = hashlib.md5()
    with open(file_name, 'rb') as file:
        block = file.read(blocksize)
        while len(block) > 0:
            hasher.update(block)
            block = file.read(blocksize)
    assert hasher.hexdigest() == check_sum, \
        'md5sum not equal. Please check the download and retry.'


def download_files(files, database_path):
    progress = tqdm(
        files, desc="{0: <25s}".format('Download files')
    )
    downloaded_files = []
    for file in progress:
        file_name = file.split('/')[-1]
        downloaded_files.append(
            download_file(
                file,
                database_path / file_name
            )
        )
    return downloaded_files


def extract_files(downloaded_files):
    progress = tqdm(
        downloaded_files, desc="{0: <25s}".format('Extract files')
    )
    for file in progress:
        extract_file(file)


def download_aux_files(database_path):
    print('Download auxiliary material of LibriWASN')
    files = [
        'https://zenodo.org/record/10952434/files/ccby4.txt',
        'https://zenodo.org/record/10952434/files/LibirWASN200_Picture.png',
        'https://zenodo.org/record/10952434/files/LibriWASN200_Positions.pdf',
        'https://zenodo.org/record/10952434/files/LibriWASN200_Setup.png',
        'https://zenodo.org/record/10952434/files/Positions200.pdf',
        'https://zenodo.org/record/10952434/files/Positions800.pdf',
        'https://zenodo.org/record/10952434/files/readme.txt',
    ]
    download_file_list(files, database_path)
    target_dir = database_path / 'LibriWASN' / 'aux_files'
    target_dir.mkdir(parents=True, exist_ok=True)
    for file in files:
        file_name = file.split('/')[-1]
        shutil.move(database_path / file_name, target_dir / file_name)


def download_libriwasn200(database_path):
    print('Download LibriWASN 200')
    files = [
        'https://zenodo.org/record/10952434/files/LibriWASN_200_0L.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_200_0S.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_200_OV10.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_200_OV20.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_200_OV30.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_200_OV40.zip'
    ]
    md5_checksums = [
        '2327be91485110031181782c1605bd86',
        '531549b8528a10e1eb9ee6ad9f800073',
        'b6eecbd9dd4a1a2074b7cd681b722c5c',
        '1a8ba4ab2d74300fbe8fdb1de31d3379',
        '8cc0d8561ac9571561e8d5ed628404db',
        '9d33cdaea1b1c968d8f885c80ce4d761'
    ]
    downloaded_files = download_files(files, database_path)
    for file, check_sum in zip(downloaded_files, md5_checksums):
        check_md5(file, check_sum)
    print('Extract LibriWASN 200')
    extract_files(downloaded_files)
    shutil.move(database_path / 'LibriWASN' / '200',
                database_path / 'LibriWASN' / 'libriwasn_200')


def download_libriwasn800(database_path):
    print('Download LibriWASN 800')
    files = [
        'https://zenodo.org/record/10952434/files/LibriWASN_800_0L.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_800_0S.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_800_OV10.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_800_OV20.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_800_OV30.zip',
        'https://zenodo.org/record/10952434/files/LibriWASN_800_OV40.zip'
    ]
    md5_checksums = [
        'e9cbaf2c4e35aeea0ac14c7edf9c181f',
        'aa8442d009dd669c14f680ba20e2143f',
        '5e36a163669bbfaad01c617a6f7e4696',
        'f8efb703b0dca20a03bbcb2f9ef07a07',
        'c76c0a22da2e7299b06fe239b7681615',
        'd3fdc9b79c33025eb0fa353e31a80c71'
    ]
    downloaded_files = download_files(files, database_path)
    for file, check_sum in zip(downloaded_files, md5_checksums):
        check_md5(file, check_sum)
    print('Extract LibriWASN 800')
    extract_files(downloaded_files)
    shutil.move(database_path / 'LibriWASN' / '800',
                database_path / 'LibriWASN' / 'libriwasn_800')


def download_libricss(database_path):
    print('Download LibriCSS')
    link = 'https://docs.google.com/uc?export=download' \
           '&id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l'
    if shutil.which('gdown'):
        run(['gdown', link, '-Olibricss.zip'])
    else:
        raise OSError(
            'gdown is not installed, You have to install it'
            ' to be able to download LibriCSS.'
        )
    print('Extract LibriCSS')
    extract_file(database_path / 'libricss.zip')
    shutil.move(database_path / 'for_release', database_path / 'LibriCSS')


@click.command()
@click.option(
    '--database_path',
    '-db',
    type=str,
    default='libriwasn/',
    help='Base directory for the databases. Defaults to "libriwasn/".'
)
def main(database_path):
    database_path = Path(database_path).expanduser().absolute()
    download_aux_files(database_path)
    download_libriwasn200(database_path)
    download_libriwasn800(database_path)
    download_libricss(database_path)


if __name__ == '__main__':
    main()
