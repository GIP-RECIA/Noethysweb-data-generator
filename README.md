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
- `clean_data()` : Vide toutes les données de test
- `generate_data()` : Génère les données de test
- `clean_and_generate()` : Nettoie et génère les données de test

Que ce soit pour `generate_data()` ou `clean_and_generate()`, vous pouvez spécifier le mode de création des comptes :
- `generate_data(mode_compte="famille")` : Crée un compte Django par famille
- `generate_data(mode_compte="individu")` : Crée un compte Django par parent

Par défaut, le mode `famille` est utilisé.

Identifiants de connexion de l'administrateur :
- Email : admin
- Mot de passe : password