# Noethysweb-data-generator
Scripts permettant de générer des données reproductibles pour noethysweb

## Installation

Copier le fichier `data-generator.py` dans le répertoire `/noethysweb` de votre
projet.

Installer faker :
```bash
pip install faker
```

## Utilisation

Se placer dans le dossier `/noethysweb` de votre projet et exécuter :
```bash
python manage.py shell
>>> exec(open('data-generator.py').read())
```

Ensuite voici les commandes disponibles :
- `generate_data()` : Génère les données de test
- `clean_data()` : Nettoie les données de test