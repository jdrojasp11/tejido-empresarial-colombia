import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import analytics
import download_data
import etl


def main() -> None:
    print("### 1/3 Descarga de datos")
    download_data.main()
    print("\n### 2/3 ETL y modelo estrella")
    etl.main()
    print("\n### 3/3 Analitica y tablero de KPIs")
    analytics.main()
    print("\nPipeline completo.")


if __name__ == "__main__":
    sys.exit(main())
