import sys
import time
from pathlib import Path

import requests

from config import RAW_DIR, SOURCES


def download(url: str, dest: Path, params: dict | None = None, retries: int = 3) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  Ya existe: {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
        return dest
    headers = {"User-Agent": "Mozilla/5.0 (tejido-empresarial-colombia ETL)"}
    for attempt in range(1, retries + 1):
        try:
            print(f"  Descargando {dest.name} (intento {attempt})...")
            with requests.get(url, params=params, stream=True, timeout=600, headers=headers) as r:
                r.raise_for_status()
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                tmp.replace(dest)
            print(f"  OK {dest.name} ({dest.stat().st_size / 1e6:.1f} MB)")
            return dest
        except Exception as exc:
            print(f"  Error: {exc}")
            if attempt == retries:
                raise
            time.sleep(3 * attempt)
    return dest


def main() -> None:
    print("Descarga de datos abiertos (Superintendencia de Sociedades)")
    for key, meta in SOURCES.items():
        print(f"[{key}] {meta['dataset']}")
        download(meta["url"], RAW_DIR / meta["file"], meta.get("params"))
    print("Descarga finalizada.")


if __name__ == "__main__":
    sys.exit(main())
