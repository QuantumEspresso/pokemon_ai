{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
    python3
    python3Packages.requests
    python3Packages.beautifulsoup4
    python3Packages.lxml
    python3Packages.tqdm
    # Pokémon AI API
    python3Packages.fastapi
    python3Packages.uvicorn
    python3Packages.pydantic
    python3Packages.httpx
    python3Packages.orjson
  ];
  shellHook = ''
    echo "Pokémon Champions scraper — Python + requests + BeautifulSoup"
    echo "Uruchom: python scrape_champions.py"
  '';
}
