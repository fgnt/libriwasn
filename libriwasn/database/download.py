import hashlib
from pathlib import Path
import shutil

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
        'https://zenodo.org/record/7960972/files/ccby4.txt',
        'https://zenodo.org/record/7960972/files/LibirWASN200_Picture.png',
        'https://zenodo.org/record/7960972/files/LibriWASN200_Positions.pdf',
        'https://zenodo.org/record/7960972/files/LibriWASN200_Setup.png',
        'https://zenodo.org/record/7960972/files/Positions200.pdf',
        'https://zenodo.org/record/7960972/files/Positions800.pdf',
        'https://zenodo.org/record/7960972/files/readme.txt',
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
        'https://zenodo.org/record/7960972/files/LibriWASN_200_0L.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_200_0S.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_200_OV10.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_200_OV20.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_200_OV30.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_200_OV40.zip'
    ]
    md5_checksums = [
        '70d44a07ab906cda2385a7e7b4a431bd',
        '966d40081d67b71f5d337610cd8fb176',
        'e9f0a19c2348a5cd0c9b9e12740a9d72',
        '7b6fcf5357d7686fa14792c019c8b9c2',
        '0c3f95be84bb0500a4d8212085c2abcc',
        '0a4d911240a309397d24c192a96fec11'
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
        'https://zenodo.org/record/7960972/files/LibriWASN_800_0L.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_800_0S.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_800_OV10.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_800_OV20.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_800_OV30.zip',
        'https://zenodo.org/record/7960972/files/LibriWASN_800_OV40.zip'
    ]
    md5_checksums = [
        '2ae30f25ea88d463d8b6f3c79286f160',
        'ec5ffca2ebe184ac1bbc416c61fdab18',
        'eba80ebd3cd868567fbfb3f46e222350',
        'a45f7d73d1dfa9c0c5a724788d1cd993',
        '5d681c70dd919af1080a129237d2ef32',
        '10efa8b713a6dc29a3e3ead4a744f050'
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
    file = (
        'https://drive.google.com/u/0/uc?id=1Piioxd5G_85K9Bhcr8ebdhXx0CnaHy7l'
        '&export=download&confirm=t&uuid=645065b5-bb2e-4418-971a-6d00aa76b1b1'
        '&at=AB6BwCDaN-TvrESmuB75j3L1cQm6:1693926341475'
    )
    download_file(file, database_path / 'libricss.zip')
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
