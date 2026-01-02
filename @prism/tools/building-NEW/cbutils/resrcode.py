import requests
import zipfile
import io
from pathlib import Path

def download_and_unzip(
    log_raise_error,
    url: str,
    extract_to: Path,
    chunk_size: int = 8192,
) -> None:
    extract_to = Path(extract_to)
    extract_to.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, stream=True, timeout=30)
    response.raise_for_status()

    # Utilisation d'un BytesIO pour stocker le stream
    zip_content = io.BytesIO()
    for chunk in response.iter_content(chunk_size=chunk_size):
        zip_content.write(chunk)

    # Crucial : Revenir au début du fichier avant lecture
    zip_content.seek(0)

    try:
        with zipfile.ZipFile(zip_content, 'r') as zip_ref:
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
