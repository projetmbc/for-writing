from typing import Callable

from pathlib import Path

import io
import requests
import zipfile

from shutil import rmtree


def download_and_unzip(
    log_raise_error: Callable,
    url            : str,
    extract_to     : Path,
    chunk_size     : int = 8192,
) -> None:
    extract_to = Path(extract_to)
    extract_to.mkdir(
        parents  = True,
        exist_ok = True
    )

    response = requests.get(
        url,
        stream  = True,
        timeout = 30
    )

    response.raise_for_status()

    zip_content = io.BytesIO()

    for chunk in response.iter_content(
        chunk_size = chunk_size
    ):
        zip_content.write(chunk)

# We must go back to the start of the ZIP file.
    zip_content.seek(0)

    try:
        with zipfile.ZipFile(
            zip_content,
            mode = 'r'
        ) as zip_ref:
            zip_ref.extractall(extract_to)

            names = zip_ref.namelist()

            for file_name in names:
                if file_name.endswith('.zip'):
                    inner_zip_path = extract_to / file_name

                    with zipfile.ZipFile(inner_zip_path, 'r') as inner_zip:
                        inner_zip.extractall(extract_to)

                    inner_zip_path.unlink()

    except zipfile.BadZipFile:
        log_raise_error(
            context   = "Donwload ZIP file",
            desc      = "Invalid ZIP file",
            exception = zipfile.BadZipFile,
            xtra = f"URL used = {url}"
        )


def clean_src_files(
    local_src_dir: Path,
    globs_kept   : [str],
) -> None:
    for g in globs_kept:
        for p in local_src_dir.glob(g):
            p.rename(local_src_dir.parent / p.name)

    rmtree(local_src_dir)


def clean_src_dirs(
    local_src_dir: Path,
    globs_kept   : [str],
) -> None:
    for g in globs_kept:
        for p in local_src_dir.glob(g):
            subdir = local_src_dir.parent / p.parent.name

            if not subdir.is_dir():
                subdir.mkdir()

            p.rename(subdir / p.name)

    rmtree(local_src_dir)
