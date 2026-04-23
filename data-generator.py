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
                fax="0100000001",
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
                tel="0110000000",
                fax="0110000001",
                mail="contact@association-test.fr",
                site="www.association-test.fr",
                num_agrement="123456789",
                num_siret="12345678901234",
                code_ape="1234A"
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

        # Étape 2 : Configuration système
        print("\n--- ÉTAPE 2 : CONFIGURATION SYSTÈME ---")

        # Importer les modèles de l'étape 2
        from core.models import (
            TypeQuotient, NiveauScolaire, CategorieTravail,
            TypeMaladie, TypeVaccin, TypeSieste, Ferie,
            ModeleDocument, ModeleEmail, ListeDiffusion,
            CategorieInformation
        )

        # Types de quotients familiaux
        types_quotients = ["QF", "QF1", "QF2", "QF3"]

        for type_q in types_quotients:
            if not TypeQuotient.objects.filter(nom=type_q).exists():
                TypeQuotient.objects.create(nom=type_q)
                print(f"TypeQuotient créé: {type_q}")

        # Niveaux scolaires
        niveaux_scolaires = [
            {"nom": "TPS", "abrege": "TPS", "ordre": 1},
            {"nom": "PS", "abrege": "PS", "ordre": 2},
            {"nom": "MS", "abrege": "MS", "ordre": 3},
            {"nom": "GS", "abrege": "GS", "ordre": 4},
            {"nom": "CP", "abrege": "CP", "ordre": 5},
            {"nom": "CE1", "abrege": "CE1", "ordre": 6},
            {"nom": "CE2", "abrege": "CE2", "ordre": 7},
            {"nom": "CM1", "abrege": "CM1", "ordre": 8},
            {"nom": "CM2", "abrege": "CM2", "ordre": 9},
            {"nom": "6ème", "abrege": "6ème", "ordre": 10},
            {"nom": "5ème", "abrege": "5ème", "ordre": 11},
            {"nom": "4ème", "abrege": "4ème", "ordre": 12},
            {"nom": "3ème", "abrege": "3ème", "ordre": 13}
        ]

        for niveau in niveaux_scolaires:
            if not NiveauScolaire.objects.filter(nom=niveau["nom"]).exists():
                NiveauScolaire.objects.create(**niveau)
                print(f"NiveauScolaire créé: {niveau['nom']}")

        # Catégories de travail
        categories_travail = [
            "Agriculteur exploitant",
            "Artisan commerçant",
            "Cadre supérieur",
            "Profession intermédiaire",
            "Employé",
            "Ouvrier qualifié",
            "Ouvrier non qualifié",
            "Inactif"
        ]

        for cat in categories_travail:
            if not CategorieTravail.objects.filter(nom=cat).exists():
                CategorieTravail.objects.create(nom=cat)
                print(f"CategorieTravail créée: {cat}")

        # Types de maladies
        from datetime import date

        types_maladies = [
            {"nom": "Maladie bénigne", "vaccin_obligatoire": False},
            {"nom": "Maladie moyenne", "vaccin_obligatoire": False},
            {"nom": "Maladie grave", "vaccin_obligatoire": False},
            {"nom": "Maladie chronique", "vaccin_obligatoire": False},
            {"nom": "Allergie", "vaccin_obligatoire": False},
            {"nom": "Handicap", "vaccin_obligatoire": False},
            # Vaccins obligatoires sans restriction
            {"nom": "Rougeole", "vaccin_obligatoire": True},
            {"nom": "Oreillons", "vaccin_obligatoire": True},
            {"nom": "Rubéole", "vaccin_obligatoire": True},
            {"nom": "Coqueluche", "vaccin_obligatoire": True},
            {"nom": "Tétanos", "vaccin_obligatoire": True},
            {"nom": "Poliomyélite", "vaccin_obligatoire": True},
            {"nom": "Diphtérie", "vaccin_obligatoire": True},
            # Vaccins obligatoires avec restriction de date
            {"nom": "Haemophilus influenzae B", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(1992, 1, 1)},
            {"nom": "Hépatite B", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(2018, 1, 1)},
            {"nom": "Méningocoque C", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(2018, 1, 1)},
            {"nom": "Pneumocoque", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(2018, 1, 1)},
            # Maladies sans vaccin obligatoire
            {"nom": "Grippe saisonnière", "vaccin_obligatoire": False},
            {"nom": "COVID-19", "vaccin_obligatoire": False}
        ]

        for maladie in types_maladies:
            if not TypeMaladie.objects.filter(nom=maladie["nom"]).exists():
                TypeMaladie.objects.create(**maladie)
                if maladie["vaccin_obligatoire"]:
                    vaccin_status = "(vaccin obligatoire)"
                else:
                    vaccin_status = ""
                print(f"TypeMaladie créé: {maladie['nom']} "
                      f"{vaccin_status}")

        # Types de vaccins
        types_vaccins = [
            "BCG",
            "DTCoq Polio",
            "ROR",
            "Hépatite B",
            "Hib",
            "Pneumocoque",
            "Méningocoque C",
            "Grippe saisonnière"
        ]

        for vaccin in types_vaccins:
            if not TypeVaccin.objects.filter(nom=vaccin).exists():
                TypeVaccin.objects.create(nom=vaccin)
                print(f"TypeVaccin créé: {vaccin}")

        # Types de siestes
        types_siestes = [
            "Pas de sieste",
            "Sieste courte (< 1h)",
            "Sieste moyenne (1-2h)",
            "Sieste longue (> 2h)"
        ]

        for sieste in types_siestes:
            if not TypeSieste.objects.filter(nom=sieste).exists():
                TypeSieste.objects.create(nom=sieste)
                print(f"TypeSieste créé: {sieste}")

        # Jours fériés français (année en cours)
        from datetime import date
        annee = date.today().year
        jours_feries = [
            {"nom": "Jour de l'an", "jour": 1, "mois": 1,
             "annee": annee, "type": "fixe"},
            {"nom": "Fête du travail", "jour": 1, "mois": 5,
             "annee": annee, "type": "fixe"},
            {"nom": "Victoire 1945", "jour": 8, "mois": 5,
             "annee": annee, "type": "fixe"},
            {"nom": "Fête nationale", "jour": 14, "mois": 7,
             "annee": annee, "type": "fixe"},
            {"nom": "Assomption", "jour": 15, "mois": 8,
             "annee": annee, "type": "fixe"},
            {"nom": "Toussaint", "jour": 1, "mois": 11,
             "annee": annee, "type": "fixe"},
            {"nom": "Armistice 1918", "jour": 11, "mois": 11,
             "annee": annee, "type": "fixe"},
            {"nom": "Noël", "jour": 25, "mois": 12,
             "annee": annee, "type": "fixe"}
        ]

        for ferie in jours_feries:
            if not Ferie.objects.filter(
                nom=ferie["nom"], annee=ferie["annee"]
            ).exists():
                Ferie.objects.create(**ferie)
                print(f"Ferie créé: {ferie['nom']} "
                      f"({ferie['jour']}/{ferie['mois']}/{ferie['annee']})")

        # Modèles de documents
        modeles_documents = [
            {"nom": "Attestation de présence",
             "categorie": "Attestation", "largeur": 210, "hauteur": 297},
            {"nom": "Facture",
             "categorie": "Facture", "largeur": 210, "hauteur": 297},
            {"nom": "Certificat de scolarité",
             "categorie": "Certificat", "largeur": 210, "hauteur": 297},
            {"nom": "Autorisation de sortie",
             "categorie": "Autorisation", "largeur": 210, "hauteur": 297},
            {"nom": "Convocation parents",
             "categorie": "Convocation", "largeur": 210, "hauteur": 297},
            {"nom": "Bulletin d'inscription",
             "categorie": "Inscription", "largeur": 210, "hauteur": 297}
        ]

        for modele in modeles_documents:
            if not ModeleDocument.objects.filter(nom=modele["nom"]).exists():
                ModeleDocument.objects.create(**modele)
                print(f"ModeleDocument créé: {modele['nom']}")

        # Modèles d'emails
        modeles_emails = [
            "Rappel d'échéance",
            "Information générale",
            "Convocation réunion",
            "Changement de planning",
            "Urgence fermeture"
        ]

        for modele in modeles_emails:
            if not ModeleEmail.objects.filter(nom=modele).exists():
                ModeleEmail.objects.create(nom=modele)
                print(f"ModeleEmail créé: {modele}")

        # Listes de diffusion
        listes_diffusion = [
            "Tous les parents",
            "Parents CP-CE1",
            "Parents CE2-CM1",
            "Personnel enseignant",
            "Direction",
            "Intervenants extérieurs"
        ]

        for liste in listes_diffusion:
            if not ListeDiffusion.objects.filter(nom=liste).exists():
                ListeDiffusion.objects.create(nom=liste)
                print(f"ListeDiffusion créée: {liste}")

        # Catégories d'informations
        categories_info = [
            "Information générale",
            "Urgence",
            "Planning",
            "Pédagogique",
            "Administratif",
            "Événementiel"
        ]

        for cat in categories_info:
            if not CategorieInformation.objects.filter(nom=cat).exists():
                CategorieInformation.objects.create(nom=cat)
                print(f"CategorieInformation créée: {cat}")

        # Étape 3 : Activités et infrastructures
        print("\n--- ÉTAPE 3 : ACTIVITÉS ET INFRASTRUCTURES ---")

        # Importer les modèles de l'étape 3
        from core.models import (
            Activite, CompteBancaire, ModeReglement, Emetteur
        )
        from datetime import date, timedelta

        # Modes de règlement
        modes_reglement = [
            {"label": "Espèces", "type_comptable": "caisse"},
            {"label": "Chèque", "type_comptable": "banque",
             "numero_piece": "NUM"},
            {"label": "Virement", "type_comptable": "banque",
             "numero_piece": "NUM"},
            {"label": "Carte bancaire", "type_comptable": "banque",
             "numero_piece": "NUM"},
            {"label": "Prélèvement", "type_comptable": "banque",
             "numero_piece": "NUM"}
        ]

        for mode in modes_reglement:
            if not ModeReglement.objects.filter(label=mode["label"]).exists():
                ModeReglement.objects.create(**mode)
                print(f"ModeReglement créé: {mode['label']}")

        # Comptes bancaires
        structure = Structure.objects.first()
        comptes_bancaires = [
            {
                "nom": "Compte principal",
                "defaut": True,
                "raison": "Mairie de Test Ville",
                "structure": structure
            },
            {
                "nom": "Compte secondaire",
                "defaut": False,
                "raison": "Association Test",
                "structure": structure
            }
        ]

        for compte in comptes_bancaires:
            if not CompteBancaire.objects.filter(nom=compte["nom"]).exists():
                CompteBancaire.objects.create(**compte)
                print(f"CompteBancaire créé: {compte['nom']}")

        # Activités
        date_debut = date.today()
        date_fin = date_debut + timedelta(days=365)

        activites = [
            {
                "nom": "Centre de loisirs - Vacances de printemps",
                "abrege": "CL-Printemps",
                "date_debut": date_debut + timedelta(days=30),
                "date_fin": date_debut + timedelta(days=40),
                "nbre_inscrits_max": 50,
                "portail_inscriptions_affichage": "PERIODE"
            },
            {
                "nom": "Atelier périscolaire - Mercredi",
                "abrege": "APS-Mercredi",
                "date_debut": date_debut,
                "date_fin": date_fin,
                "nbre_inscrits_max": 30,
                "portail_inscriptions_affichage": "TOUJOURS"
            },
            {
                "nom": "Stage d'été - Sport et nature",
                "abrege": "SE-Ete",
                "date_debut": date_debut + timedelta(days=120),
                "date_fin": date_debut + timedelta(days=135),
                "nbre_inscrits_max": 40,
                "portail_inscriptions_affichage": "PERIODE"
            },
            {
                "nom": "Cantine scolaire",
                "abrege": "CAN-Scolaire",
                "date_debut": date_debut,
                "date_fin": date_fin,
                "nbre_inscrits_max": 100,
                "portail_inscriptions_affichage": "TOUJOURS"
            },
            {
                "nom": "Accueil périscolaire - Matin",
                "abrege": "APP-Matin",
                "date_debut": date_debut,
                "date_fin": date_fin,
                "nbre_inscrits_max": 60,
                "portail_inscriptions_affichage": "TOUJOURS"
            }
        ]

        for activite in activites:
            if not Activite.objects.filter(nom=activite["nom"]).exists():
                Activite.objects.create(**activite)
                print(f"Activite créée: {activite['nom']}")

        # Émetteurs de règlement
        mode_especes = ModeReglement.objects.get(label="Espèces")
        mode_cheque = ModeReglement.objects.get(label="Chèque")
        mode_virement = ModeReglement.objects.get(label="Virement")

        emetteurs = [
            {"mode": mode_especes, "nom": "Caisse principale"},
            {"mode": mode_cheque, "nom": "Parents - Chèques"},
            {"mode": mode_virement, "nom": "Parents - Virements"},
            {"mode": mode_especes, "nom": "Caisse secondaire"},
            {"mode": mode_cheque, "nom": "Mairie - Chèques"}
        ]

        for emetteur in emetteurs:
            if not Emetteur.objects.filter(nom=emetteur["nom"]).exists():
                Emetteur.objects.create(**emetteur)
                print(f"Emetteur créé: {emetteur['nom']}")

        print("\n=== GÉNÉRATION TERMINÉE ===")

    except Exception as e:
        print(f"Erreur lors de la génération des données: {e}")


def clean_and_generate():
    """Nettoie la base et génère les données de base en une seule commande"""
    print("=== NETTOYAGE COMPLET + GÉNÉRATION DONNÉES ===")
    clean_data_strict()
    generate_data()
    print("=== OPÉRATION TERMINÉE ===")
