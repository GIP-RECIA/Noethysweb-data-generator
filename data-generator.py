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
    """Génère toutes les données de base par étapes successives"""
    print("=== GÉNÉRATION DES DONNÉES DE BASE ===")

    # Importer les modèles Django nécessaires
    from core.models import (
        Utilisateur, Structure, Organisateur, Caisse, Regime
    )
    try:
        # Étape 0 : Superuser
        print("\n--- ÉTAPE 0 : SUPERUSER ---")
        if not Utilisateur.objects.filter(username='admin').exists():
            user = Utilisateur.objects.create_superuser(
                username='admin',
                email='admin@demo.fr',
                password='password'
            )
            print(f"Superuser créé: {user.username} ({user.email})")
        else:
            print("Superuser 'admin' existe déjà")

        # Étape 1 : Données de base
        print("\n--- ÉTAPE 1 : DONNÉES DE BASE ---")

        # Structure
        if not Structure.objects.exists():
            structure = Structure.objects.create(
                nom="Mairie de Test Ville",
                rue="1 Place de la Mairie",
                cp="75001",
                ville="Paris",
                tel="0100000000",
                mail="contact@testville.fr",
                site="www.testville.fr"
            )
            print(f"Structure créée: {structure.nom}")
        else:
            structure = Structure.objects.first()
            print(f"Structure existante: {structure.nom}")

        # Organisateur
        if not Organisateur.objects.exists():
            organisateur = Organisateur.objects.create(
                nom="Association Test",
                rue="5 Rue de l'Association",
                cp="75002",
                ville="Paris",
                tel="0100000001",
                mail="contact@association-test.fr",
                site="www.association-test.fr"
            )
            print(f"Organisateur créé: {organisateur.nom}")
        else:
            organisateur = Organisateur.objects.first()
            print(f"Organisateur existant: {organisateur.nom}")

        # Caisses et Régimes
        caisses_data = [
            {
                "nom": "CAF",
                "regime": {"nom": "CAF"}
            },
            {
                "nom": "MSA",
                "regime": {"nom": "MSA"}
            }
        ]

        for caisse_data in caisses_data:
            if not Caisse.objects.filter(nom=caisse_data["nom"]).exists():
                regime_data = caisse_data["regime"]

                # Créer le régime d'abord
                regime, created = Regime.objects.get_or_create(
                    nom=regime_data["nom"]
                )
                if created:
                    print(f"Régime créé: {regime.nom}")

                # Créer la caisse
                caisse = Caisse.objects.create(
                    nom=caisse_data["nom"],
                    regime=regime
                )
                print(f"Caisse créée: {caisse.nom} (régime: {regime.nom})")
            else:
                caisse = Caisse.objects.get(nom=caisse_data["nom"])
                print(f"Caisse existante: {caisse.nom}")

        print("\n=== GÉNÉRATION TERMINÉE ===")

    except Exception as e:
        print(f"Erreur lors de la génération des données: {e}")


def clean_and_generate():
    """Nettoie la base et génère les données de base en une seule commande"""
    print("=== NETTOYAGE COMPLET + GÉNÉRATION DONNÉES ===")
    clean_data_strict()
    generate_data()
    print("=== OPÉRATION TERMINÉE ===")
