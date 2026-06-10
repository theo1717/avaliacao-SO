"""Simulador Bancario de Sistema Operacional - ponto de entrada."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ui.menu import MainMenu


def main() -> None:
    menu = MainMenu()
    menu.run()


if __name__ == "__main__":
    main()
