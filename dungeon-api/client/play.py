"""BONUS — Client terminal du jeu (argparse + requests).

Objectif : jouer à votre propre API depuis le terminal, par exemple :
    python client/play.py login --username alice --password secret
    python client/play.py create --name Aragorn --classe guerrier --force 6 --agilite 2 --intelligence 2
    python client/play.py look --hero 1
    python client/play.py move --hero 1 --direction nord
    python client/play.py attack --hero 1
    python client/play.py rest --hero 1

Conseil : enregistrez le token JWT reçu au login dans un fichier (ex. .token)
pour le réutiliser dans les commandes suivantes.
"""

import argparse

API_URL = "http://127.0.0.1:8000"


def main() -> None:
    parser = argparse.ArgumentParser(description="Dungeon as a Service — client terminal")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # TODO : déclarez une sous-commande par action (login, create, look, move, attack, rest)
    subparsers.add_parser("health", help="Vérifie que l'API répond")

    args = parser.parse_args()

    if args.command == "health":
        # TODO : remplacez ce print par un appel requests.get(f"{API_URL}/health")
        print("À vous de jouer !")


if __name__ == "__main__":
    main()
