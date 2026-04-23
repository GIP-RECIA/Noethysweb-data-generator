#!/usr/bin/env python3
"""
Script pour nettoyer les espaces en fin de lignes du fichier data-generator.py
"""

import os
import sys


def clean_trailing_spaces(file_path):
    """
    Nettoie les espaces en fin de lignes d'un fichier

    Args:
        file_path (str): Chemin du fichier à nettoyer
    """
    try:
        # Lire le contenu du fichier
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        # Nettoyer chaque ligne
        cleaned_lines = []
        changes_made = False

        for i, line in enumerate(lines, 1):
            original_line = line
            if line.endswith('\n'):
                cleaned_line = line.rstrip() + '\n'
            else:
                cleaned_line = line.rstrip()

            if original_line != cleaned_line:
                changes_made = True
                print(f"Ligne {i}: Espaces en fin de ligne supprimés")

            cleaned_lines.append(cleaned_line)

        # Écrire le fichier nettoyé si des modifications ont été faites
        if changes_made:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(cleaned_lines)
            print(f"Le fichier {file_path} a été nettoyé avec succès.")
        else:
            print(f"Aucun espace en fin de ligne trouvé dans {file_path}.")

    except FileNotFoundError:
        print(f"Erreur: Le fichier {file_path} n'existe pas.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du nettoyage du fichier: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Fichier à nettoyer
    target_file = "data-generator.py"

    # Vérifier si le fichier existe
    if not os.path.exists(target_file):
        print(f"Erreur: Le fichier {target_file} n'existe pas "
              f"dans le répertoire courant.")
        sys.exit(1)

    print(f"Nettoyage des espaces en fin de lignes dans {target_file}...")
    clean_trailing_spaces(target_file)
