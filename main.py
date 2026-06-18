"""Simulador Bancario de Sistema Operacional - ponto de entrada."""

import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.menu import MainMenu


def main() -> None:
    os.system("cls")
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()
