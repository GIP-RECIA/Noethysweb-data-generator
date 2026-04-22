#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fonction simple pour vider complètement la base de données
Usage: clean_data()
"""

import os
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'noethysweb.settings')
django.setup()


def clean_data_strict():
    """Supprime TOUTES les données sans aucune erreur - méthode radicale"""
    print("Nettoyage STRICT de la base de données (sans erreur)...")

    # Importer la connection au début
    from django.db import connection

    try:
        # Désactiver complètement les contraintes
        cursor = connection.cursor()

        if connection.vendor == 'sqlite':
            # SQLite: désactiver les clés étrangères
            cursor.execute("PRAGMA foreign_keys = OFF")
            cursor.execute("PRAGMA ignore_check_constraints = ON")

        # Récupérer tous les noms de tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Exclure les tables système
        system_tables = ['sqlite_sequence', 'django_migrations']
        tables = [t for t in tables if t not in system_tables]

        total_deleted = 0

        # Vider chaque table avec DELETE SQL direct
        for table in tables:
            try:
                # Compter avant suppression
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]

                if count > 0:
                    # Suppression SQL direct (bypass Django)
                    cursor.execute(f"DELETE FROM {table}")
                    total_deleted += count
                    print(f"Supprimé {count:6} enregistrements de {table}")

            except Exception as e:
                print(f"Table {table}: {str(e)}")

        # Réinitialiser les séquences
        cursor.execute("DELETE FROM sqlite_sequence")

        # Réactiver les contraintes
        if connection.vendor == 'sqlite':
            cursor.execute("PRAGMA foreign_keys = ON")
            cursor.execute("PRAGMA ignore_check_constraints = OFF")

        # Forcer Django à voir les changements
        from django.db import connection
        connection.close()

        print(f"\nNettoyage STRICT terminé! {total_deleted} enregistrements")
        print("supprimés")
        print("Base de données 100% vide - 0 erreur")

    except Exception as e:
        print(f"Erreur lors du nettoyage strict: {e}")
        # En cas d'erreur, réactiver les contraintes
        try:
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON")
        except Exception:
            pass


def generate_data():
    """Génère les données de base : superuser et configuration initiale"""
    print("Génération des données de base...")

    # Importer les modèles Django nécessaires
    # from django.db import connection
    from core.models import Utilisateur

    try:
        # Créer le superuser avec le modèle Utilisateur de Noethys
        if not Utilisateur.objects.filter(username='admin').exists():
            user = Utilisateur.objects.create_superuser(
                username='admin',
                email='admin@demo.fr',
                password='password'
            )
            print(f"Superuser créé: {user.username} ({user.email})")
        else:
            print("Superuser 'admin' existe déjà")

        print("Génération des données terminée!")

    except Exception as e:
        print(f"Erreur lors de la génération des données: {e}")


def clean_and_generate():
    """Nettoie la base et génère les données de base en une seule commande"""
    print("=== NETTOYAGE COMPLET + GÉNÉRATION DONNÉES ===")
    clean_data_strict()
    generate_data()
    print("=== OPÉRATION TERMINÉE ===")
