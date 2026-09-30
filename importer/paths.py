"""Shared locations so the importer works from any working directory."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"
GL860_DIR = str(DATA_DIR / "GL860")
COAI_DIR = str(DATA_DIR / "COAI")
CONFIG_FILE = str(HERE / "config.ini")
