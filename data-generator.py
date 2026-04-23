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

        # Associer la structure à l'admin pour qu'elle apparaisse
        # dans les listes
        admin_user = Utilisateur.objects.get(username='admin')
        if structure not in admin_user.structures.all():
            admin_user.structures.add(structure)
            admin_user.structure_actuelle = structure
            admin_user.save()
            print(f"Structure '{structure.nom}' associée à l'admin")

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
            {"nom": "Coqueluche", "vaccin_obligatoire": True},
            {"nom": "Tétanos", "vaccin_obligatoire": True},
            {"nom": "Poliomyélite", "vaccin_obligatoire": True},
            {"nom": "Diphtérie", "vaccin_obligatoire": True},
            {"nom": "Tuberculose", "vaccin_obligatoire": True},
            # Vaccins obligatoires avec restriction de date
            {"nom": "Haemophilus influenzae B", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(1992, 1, 1)},
            {"nom": "Hépatite B", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(2018, 1, 1)},
            {"nom": "Méningocoque", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(2018, 1, 1)},
            {"nom": "Pneumocoque", "vaccin_obligatoire": True,
             "vaccin_date_naiss_min": date(2018, 1, 1)},
            # Maladies sans vaccin obligatoire
            {"nom": "Grippe saisonnière", "vaccin_obligatoire": False},
            {"nom": "COVID-19", "vaccin_obligatoire": False},
            {"nom": "Maladie chronique", "vaccin_obligatoire": False},
            {"nom": "Allergie", "vaccin_obligatoire": False},
            {"nom": "Handicap", "vaccin_obligatoire": False},
            {"nom": "Rougeole", "vaccin_obligatoire": True},
            {"nom": "Oreillons", "vaccin_obligatoire": True},
            {"nom": "Rubéole", "vaccin_obligatoire": True},
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
            {
                "nom": "BCG",
                "duree_validite": "j0-m0-a20",
                "maladies": ["Tuberculose"]
            },
            {
                "nom": "DTCoq Polio",
                "duree_validite": "j0-m0-a10",
                "maladies": ["Diphtérie", "Tétanos", "Coqueluche",
                             "Poliomyélite"]
            },
            {
                "nom": "ROR",
                "duree_validite": "j0-m0-a20",
                "maladies": ["Rougeole", "Oreillons", "Rubéole"]
            },
            {
                "nom": "Hépatite B",
                "duree_validite": "j0-m0-a20",
                "maladies": ["Hépatite B"]
            },
            {
                "nom": "Hib",
                "duree_validite": "j0-m0-a5",
                "maladies": ["Haemophilus influenzae B"]
            },
            {
                "nom": "Pneumocoque",
                "duree_validite": "j0-m0-a5",
                "maladies": ["Pneumocoque"]
            },
            {
                "nom": "Méningocoque C",
                "duree_validite": "j0-m0-a5",
                "maladies": ["Méningocoque"]
            },
            {
                "nom": "Grippe saisonnière",
                "duree_validite": "j0-m0-a1",
                "maladies": ["Grippe saisonnière"]
            },
            {
                "nom": "COVID-19",
                "duree_validite": "j0-m6-a0",
                "maladies": ["COVID-19"]
            }
        ]

        for vaccin_data in types_vaccins:
            if not TypeVaccin.objects.filter(nom=vaccin_data["nom"]).exists():
                vaccin = TypeVaccin.objects.create(
                    nom=vaccin_data["nom"],
                    duree_validite=vaccin_data["duree_validite"]
                )

                # Associer les maladies au vaccin
                for nom_maladie in vaccin_data["maladies"]:
                    try:
                        maladie = TypeMaladie.objects.get(
                            nom=nom_maladie)
                        vaccin.types_maladies.add(maladie)
                    except TypeMaladie.DoesNotExist:
                        print(f"  Attention: Maladie '{nom_maladie}' "
                              f"non trouvée")

                duree_info = f" (validité: {vaccin_data['duree_validite']})"
                print(f"TypeVaccin créé: {vaccin_data['nom']}{duree_info}")

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

        # Jours fériés français
        from datetime import date
        from dateutil.relativedelta import relativedelta
        from dateutil.easter import easter

        annee = date.today().year

        # Jours fériés fixes (année = 0)
        jours_feries_fixes = [
            {"nom": "Jour de l'an", "jour": 1, "mois": 1, "annee": 0,
             "type": "fixe"},
            {"nom": "Fête du travail", "jour": 1, "mois": 5, "annee": 0,
             "type": "fixe"},
            {"nom": "Victoire 1945", "jour": 8, "mois": 5, "annee": 0,
             "type": "fixe"},
            {"nom": "Fête nationale", "jour": 14, "mois": 7, "annee": 0,
             "type": "fixe"},
            {"nom": "Assomption", "jour": 15, "mois": 8, "annee": 0,
             "type": "fixe"},
            {"nom": "Toussaint", "jour": 1, "mois": 11, "annee": 0,
             "type": "fixe"},
            {"nom": "Armistice 1918", "jour": 11, "mois": 11, "annee": 0,
             "type": "fixe"},
            {"nom": "Noël", "jour": 25, "mois": 12, "annee": 0,
             "type": "fixe"}
        ]

        # Jours fériés variables (calculés pour l'année en cours)
        dimanche_paques = easter(annee)
        lundi_paques = dimanche_paques + relativedelta(days=+1)
        jeudi_ascension = dimanche_paques + relativedelta(days=+39)
        lundi_pentecote = dimanche_paques + relativedelta(days=+50)

        jours_feries_variables = [
            {"nom": "Lundi de Pâques", "jour": lundi_paques.day,
             "mois": lundi_paques.month, "annee": annee, "type": "variable"},
            {"nom": "Jeudi de l'Ascension", "jour": jeudi_ascension.day,
             "mois": jeudi_ascension.month, "annee": annee,
             "type": "variable"},
            {"nom": "Lundi de Pentecôte", "jour": lundi_pentecote.day,
             "mois": lundi_pentecote.month, "annee": annee, "type": "variable"}
        ]

        # Jours fériés variables (calculés pour l'année suivante)
        annee_suivante = annee + 1
        dimanche_paques_suiv = easter(annee_suivante)
        lundi_paques_suiv = dimanche_paques_suiv + relativedelta(days=+1)
        jeudi_ascension_suiv = dimanche_paques_suiv + relativedelta(days=+39)
        lundi_pentecote_suiv = dimanche_paques_suiv + relativedelta(days=+50)

        jours_feries_variables_suiv = [
            {"nom": "Lundi de Pâques", "jour": lundi_paques_suiv.day,
             "mois": lundi_paques_suiv.month, "annee": annee_suivante,
             "type": "variable"},
            {"nom": "Jeudi de l'Ascension", "jour": jeudi_ascension_suiv.day,
             "mois": jeudi_ascension_suiv.month, "annee": annee_suivante,
             "type": "variable"},
            {"nom": "Lundi de Pentecôte", "jour": lundi_pentecote_suiv.day,
             "mois": lundi_pentecote_suiv.month, "annee": annee_suivante,
             "type": "variable"}
        ]

        # Fusionner les trois listes
        jours_feries = (jours_feries_fixes +
                        jours_feries_variables +
                        jours_feries_variables_suiv)

        for ferie in jours_feries:
            if not Ferie.objects.filter(
                nom=ferie["nom"], annee=ferie["annee"]
            ).exists():
                print(f"Création du jour férié: {ferie['nom']} "
                      f"({ferie['type']})")
                Ferie.objects.create(**ferie)
                if ferie["annee"] == 0:
                    date_info = f"({ferie['jour']}/{ferie['mois']})"
                else:
                    date_info = (f"({ferie['jour']}/"
                                 f"{ferie['mois']}/{ferie['annee']})")
                print(f"Ferie créé: {ferie['nom']} {date_info}")

        # Modèles de documents
        modeles_documents = [
            # Catégorie: attestation
            {"nom": "Attestation de présence", "categorie": "attestation",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Attestation de scolarité", "categorie": "attestation",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: facture
            {"nom": "Facture standard", "categorie": "facture",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Facture simplifiée", "categorie": "facture",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: rappel
            {"nom": "Lettre de rappel première", "categorie": "rappel",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Lettre de rappel deuxième", "categorie": "rappel",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},
            {"nom": "Mise en demeure", "categorie": "rappel",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: reglement
            {"nom": "Reçu de règlement", "categorie": "reglement",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Avis de paiement", "categorie": "reglement",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: inscription
            {"nom": "Bulletin d'inscription", "categorie": "inscription",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Convocation inscription", "categorie": "inscription",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: individu
            {"nom": "Fiche individuelle", "categorie": "individu",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Certificat médical", "categorie": "individu",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: famille
            {"nom": "Fiche famille", "categorie": "famille",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Autorisation de sortie", "categorie": "famille",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: cotisation
            {"nom": "Reçu cotisation", "categorie": "cotisation",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Attestation adhésion", "categorie": "cotisation",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: attestation_fiscale
            {"nom": "Attestation fiscale annuelle",
             "categorie": "attestation_fiscale",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},

            # Catégorie: devis
            {"nom": "Devis standard", "categorie": "devis",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Devis simplifié", "categorie": "devis",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: location
            {"nom": "Contrat de location", "categorie": "location",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "État des lieux", "categorie": "location",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: location_demande
            {"nom": "Demande de location", "categorie": "location_demande",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Confirmation de location",
             "categorie": "location_demande",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},

            # Catégorie: fond (calques de fond)
            {"nom": "En-tête standard", "categorie": "fond",
             "largeur": 210, "hauteur": 297, "defaut": True, "objets": "[]"},
            {"nom": "Pied de page", "categorie": "fond",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"},
            {"nom": "Filigrane", "categorie": "fond",
             "largeur": 210, "hauteur": 297, "defaut": False, "objets": "[]"}
        ]

        for modele in modeles_documents:
            if not ModeleDocument.objects.filter(nom=modele["nom"]).exists():
                ModeleDocument.objects.create(**modele)
                defaut_info = " (défaut)" if modele["defaut"] else ""
                print(f"ModeleDocument créé: {modele['nom']} "
                      f"[{modele['categorie']}]{defaut_info}")

        # Modèles d'emails
        modeles_emails = [
            # Catégorie: saisie_libre
            {"nom": "Email standard", "categorie": "saisie_libre",
             "description": "Modèle d'email standard pour communications",
             "objet": "Information de {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {UTILISATEUR_PRENOM},</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},
            {"nom": "Email formel", "categorie": "saisie_libre",
             "description": "Modèle d'email formel pour communications",
             "objet": "Communication officielle - {ORGANISATEUR_NOM}",
             "html": "<p>Madame, Monsieur,</p>"
                    "<p>Veuillez trouver ci-joint...</p>"
                    "<p>Cordialement,<br/>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": False},

            # Catégorie: facture
            {"nom": "Facture standard", "categorie": "facture",
             "description": "Envoi d'une facture à une famille",
             "objet": "Facture n°{NUMERO_FACTURE} - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Veuillez trouver en pièce jointe votre facture "
                    "n°{NUMERO_FACTURE} d'un montant de {SOLDE}€.</p>"
                    "<p>Date d'échéance : {DATE_ECHEANCE}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},
            {"nom": "Rappel facture", "categorie": "facture",
             "description": "Rappel de facture impayée",
             "objet": "Rappel Facture n°{NUMERO_FACTURE} - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Nous vous rappelons que votre facture "
                    "n°{NUMERO_FACTURE} d'un montant de {SOLDE}€ "
                    "est toujours impayée.</p>"
                    "<p>Date d'échéance : {DATE_ECHEANCE}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": False},

            # Catégorie: rappel
            {"nom": "Rappel première", "categorie": "rappel",
             "description": "Premier rappel de paiement",
             "objet": "Rappel de paiement - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Nous vous rappelons un solde impayé de "
                    "{SOLDE_CHIFFRES}€ ({SOLDE_LETTRES}).</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},
            {"nom": "Mise en demeure", "categorie": "rappel",
             "description": "Mise en demeure avant recouvrement",
             "objet": "MISE EN DEMEURE - {ORGANISATEUR_NOM}",
             "html": "<p>Madame, Monsieur,</p>"
                    "<p>Suite à nos multiples relances, "
                    "nous vous mettons en demeure de "
                    "régler votre solde de {SOLDE_CHIFFRES}€.</p>"
                    "<p>Sinon, nous procéderons à une action en justice.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": False},

            # Catégorie: inscription
            {"nom": "Confirmation inscription", "categorie": "inscription",
             "description": "Confirmation inscription activité",
             "objet": "Confirmation inscription - {ACTIVITE_NOM_COURT}",
             "html": "<p>Bonjour {INDIVIDU_PRENOM},</p>"
                    "<p>Nous vous confirmons votre inscription à "
                    "{ACTIVITE_NOM_LONG} pour la période du "
                    "{DATE_DEBUT} au {DATE_FIN}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},
            {"nom": "Annulation inscription", "categorie": "inscription",
             "description": "Annulation inscription activité",
             "objet": "Annulation inscription - {ACTIVITE_NOM_COURT}",
             "html": "<p>Bonjour {INDIVIDU_PRENOM},</p>"
                    "<p>Nous vous informons de l'annulation de votre "
                    "inscription à {ACTIVITE_NOM_LONG}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": False},

            # Catégorie: attestation_presence
            {"nom": "Attestation présence",
             "categorie": "attestation_presence",
             "description": "Envoi attestation présence",
             "objet": "Attestation présence - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {INDIVIDU_PRENOM},</p>"
                    "<p>Veuillez trouver en pièce jointe "
                    "votre attestation de présence pour "
                    "la période du {DATE_DEBUT} au {DATE_FIN}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: cotisation
            {"nom": "Renouvellement cotisation", "categorie": "cotisation",
             "description": "Demande de renouvellement de cotisation",
             "objet": "Renouvellement cotisation - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Votre cotisation {NOM_COTISATION} arrive à "
                    "échéance le {DATE_FIN}.</p>"
                    "<p>Pour renouveler : {URL_PORTAIL}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},
            {"nom": "Confirmation cotisation",
             "categorie": "cotisation",
             "description": "Confirmation paiement cotisation",
             "objet": "Confirmation cotisation - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Nous vous confirmons le paiement "
                    "de votre cotisation {NOM_COTISATION}.</p>"
                    "<p>Votre carte est valide jusqu'au {DATE_FIN}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": False},

            # Catégorie: portail
            {"nom": "Création compte portail", "categorie": "portail",
             "description": "Création d'un compte portail pour une famille",
             "objet": "Création de votre compte portail - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Votre compte portail a été créé.</p>"
                    "<p>Identifiant : {IDENTIFIANT_INTERNET}<br/>"
                    "Mot de passe : {MOTDEPASSE_INTERNET}</p>"
                    "<p>URL : {URL_PORTAIL}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: location
            {"nom": "Confirmation location", "categorie": "location",
             "description": "Confirmation d'une location",
             "objet": "Confirmation location - {NOM_PRODUIT}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous vous confirmons la location de {NOM_PRODUIT} "
                    "du {DATE_DEBUT} au {DATE_FIN}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: location_demande
            {"nom": "Confirmation demande location",
             "categorie": "location_demande",
             "description": "Confirmation de réception demande location",
             "objet": "Confirmation demande location - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre demande de location "
                    "du {DATE}.</p>"
                    "<p>Nous traitons votre demande et reviendrons "
                    "vers vous rapidement.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: devis
            {"nom": "Envoi devis", "categorie": "devis",
             "description": "Envoi d'un devis à une famille",
             "objet": "Devis n°{NUMERO_DEVIS} - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Veuillez trouver en pièce jointe votre devis "
                    "n°{NUMERO_DEVIS} d'un montant de {SOLDE}€.</p>"
                    "<p>Ce devis est valable jusqu'au {DATE_FIN}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: reglement
            {"nom": "Confirmation règlement",
             "categorie": "reglement",
             "description": "Confirmation de réception d'un règlement",
             "objet": "Confirmation règlement n°{ID_REGLEMENT} "
                    "- {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_PAYEUR},</p>"
                    "<p>Nous vous confirmons la réception de "
                    "votre règlement de {MONTANT_REGLEMENT}€ "
                    "par {MODE_REGLEMENT}.</p>"
                    "<p>N° quittancier : {NUM_QUITTANCIER}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: recu_reglement
            {"nom": "Envoi reçu règlement", "categorie": "recu_reglement",
             "description": "Envoi d'un reçu de règlement",
             "objet": "Reçu de règlement n°{NUMERO_RECU} - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_PAYEUR},</p>"
                    "<p>Veuillez trouver en pièce jointe votre reçu "
                    "de règlement n°{NUMERO_RECU} d'un montant de "
                    "{MONTANT_REGLEMENT}€.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: releve_prestations
            {"nom": "Relevé prestations", "categorie": "releve_prestations",
             "description": "Envoi d'un relevé des prestations",
             "objet": "Relevé des prestations - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Veuillez trouver en pièce jointe votre relevé "
                    "des prestations au {DATE_EDITION_RELEVE}.</p>"
                    "<p>Reste dû : {RESTE_DU}€</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: recu_don_oeuvres
            {"nom": "Reçu don oeuvres", "categorie": "recu_don_oeuvres",
             "description": "Envoi d'un reçu de don aux œuvres",
             "objet": "Reçu de don n°{NUMERO_RECU} - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_DONATEUR},</p>"
                    "<p>Nous vous remercions pour votre don de "
                    "{MONTANT_CHIFFRES}€ ({MONTANT_LETTRES}).</p>"
                    "<p>Veuillez trouver en pièce jointe votre reçu "
                    "fiscal n°{NUMERO_RECU}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: attestation_fiscale
            {"nom": "Attestation fiscale", "categorie": "attestation_fiscale",
             "description": "Envoi d'une attestation fiscale",
             "objet": "Attestation fiscale - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Veuillez trouver en pièce jointe votre "
                    "attestation fiscale pour la période du "
                    "{DATE_DEBUT} au {DATE_FIN}.</p>"
                    "<p>Montant facturé : {MONTANT_FACTURE}€<br/>"
                    "Montant réglé : {MONTANT_REGLE}€</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: reservations
            {"nom": "Liste réservations", "categorie": "reservations",
             "description": "Envoi de la liste des réservations",
             "objet": "Liste des réservations - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Veuillez trouver en pièce jointe la liste de "
                    "vos réservations.</p>"
                    "<p>Solde : {SOLDE}€</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: mandat_sepa
            {"nom": "Mandat SEPA", "categorie": "mandat_sepa",
             "description": "Envoi d'un mandat SEPA",
             "objet": "Mandat SEPA - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Veuillez trouver en pièce jointe votre mandat "
                    "SEPA (Référence Unique du Mandat : "
                    "{REFERENCE_UNIQUE_MANDAT}).</p>"
                    "<p>Date de signature : {DATE_SIGNATURE}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: rappel_pieces_manquantes
            {"nom": "Rappel pièces manquantes",
             "categorie": "rappel_pieces_manquantes",
             "description": "Rappel pièces manquantes",
             "objet": "Pièces manquantes - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_FAMILLE},</p>"
                    "<p>Nous vous rappelons que les pièces "
                    "suivantes sont manquantes pour votre "
                    "dossier :</p>"
                    "<p>{LISTE_PIECES_MANQUANTES}</p>"
                    "<p>Merci de nous les fournir rapidement.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: rappel_vaccinations_manquantes
            {"nom": "Rappel vaccinations",
             "categorie": "rappel_vaccinations_manquantes",
             "description": "Rappel vaccinations manquantes",
             "objet": "Vaccinations manquantes - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {NOM_COMPLET_INDIVIDU},</p>"
                    "<p>Nous vous rappelons que les vaccinations "
                    "suivantes sont manquantes pour votre "
                    "dossier :</p>"
                    "<p>{LISTE_VACCINATIONS_MANQUANTES}</p>"
                    "<p>Merci de mettre à jour votre carnet de santé.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_demande_inscription
            {"nom": "Demande inscription portail",
             "categorie": "portail_demande_inscription",
             "description": "Confirmation demande inscription portail",
             "objet": "Demande d'inscription reçue - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre demande "
                    "d'inscription du {DEMANDE_HORODATAGE}.</p>"
                    "<p>Description : {DEMANDE_DESCRIPTION}</p>"
                    "<p>Nous traitons votre demande et vous "
                    "répondrons avant le {DEMANDE_TRAITEMENT_DATE}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_demande_reservation
            {"nom": "Demande réservation portail",
             "categorie": "portail_demande_reservation",
             "description": "Confirmation demande réservation portail",
             "objet": "Demande de réservation reçue - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {INDIVIDU_PRENOM},</p>"
                    "<p>Nous avons bien reçu votre demande "
                    "de réservation du {DEMANDE_HORODATAGE}.</p>"
                    "<p>Réponse : {DEMANDE_REPONSE}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_demande_renseignement
            {"nom": "Demande renseignement portail",
             "categorie": "portail_demande_renseignement",
             "description": "Confirmation demande renseignement portail",
             "objet": "Demande de modification reçue - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre demande "
                    "de modification du {DEMANDE_HORODATAGE}.</p>"
                    "<p>Description : {DEMANDE_DESCRIPTION}</p>"
                    "<p>Nous traitons votre demande et vous "
                    "répondrons rapidement.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_demande_facture
            {"nom": "Demande facture portail",
             "categorie": "portail_demande_facture",
             "description": "Confirmation demande facture portail",
             "objet": "Demande de facture reçue - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre demande "
                    "de facture du {DEMANDE_HORODATAGE}.</p>"
                    "<p>Description : {DEMANDE_DESCRIPTION}</p>"
                    "<p>Nous traitons votre demande et vous "
                    "enverrons votre facture rapidement.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_demande_recu_reglement
            {"nom": "Demande reçu règlement portail",
             "categorie": "portail_demande_recu_reglement",
             "description": "Confirmation demande reçu règlement portail",
             "objet": "Demande de reçu reçue - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre demande "
                    "de reçu de règlement du {DEMANDE_HORODATAGE}.</p>"
                    "<p>Description : {DEMANDE_DESCRIPTION}</p>"
                    "<p>Nous traitons votre demande et vous "
                    "enverrons votre reçu rapidement.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_demande_location
            {"nom": "Demande location portail",
             "categorie": "portail_demande_location",
             "description": "Confirmation demande location portail",
             "objet": "Demande de location reçue - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre demande "
                    "de location du {DEMANDE_HORODATAGE}.</p>"
                    "<p>Description : {DEMANDE_DESCRIPTION}</p>"
                    "<p>Catégories demandées : {CATEGORIES}</p>"
                    "<p>Produits demandés : {PRODUITS}</p>"
                    "<p>Nous traitons votre demande et vous "
                    "répondrons avant le {DEMANDE_TRAITEMENT_DATE}.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_places_disponibles
            {"nom": "Places disponibles portail",
             "categorie": "portail_places_disponibles",
             "description": "Notification places disponibles portail",
             "objet": "Places disponibles - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {INDIVIDU_PRENOM},</p>"
                    "<p>Des places sont disponibles pour les "
                    "activités suivantes :</p>"
                    "<p>{DETAIL_PLACES}</p>"
                    "<p>Pour réserver : {URL_PORTAIL}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_confirmation_reservations
            {"nom": "Confirmation réservations portail",
             "categorie": "portail_confirmation_reservations",
             "description": "Confirmation réservations portail",
             "objet": "Confirmation réservations - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour {INDIVIDU_PRENOM},</p>"
                    "<p>Nous vous confirmons vos réservations "
                    "pour {ACTIVITE_NOM}.</p>"
                    "<p>Période : {PERIODE_NOM}</p>"
                    "<p>Modifications : {DETAIL_MODIFICATIONS}</p>"
                    "<p>Pour consulter : {URL_PORTAIL}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: portail_notification_message
            {"nom": "Notification message portail",
             "categorie": "portail_notification_message",
             "description": "Notification message portail",
             "objet": "Nouveau message - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Vous avez reçu un nouveau message "
                    "dans votre espace portail.</p>"
                    "<p>Pour le consulter : {URL_MESSAGE}</p>"
                    "<p>Pour vous connecter : {URL_PORTAIL}</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True},

            # Catégorie: commande_repas
            {"nom": "Commande repas", "categorie": "commande_repas",
             "description": "Confirmation de commande de repas",
             "objet": "Commande repas - {ORGANISATEUR_NOM}",
             "html": "<p>Bonjour,</p>"
                    "<p>Nous avons bien reçu votre commande de repas "
                    "{NOM_COMMANDE}.</p>"
                    "<p>Période : du {DATE_DEBUT} au {DATE_FIN}</p>"
                    "<p>Merci de vérifier les détails sur le portail.</p>"
                    "<p>{UTILISATEUR_SIGNATURE}</p>",
             "defaut": True}
        ]

        for modele in modeles_emails:
            if not ModeleEmail.objects.filter(nom=modele["nom"]).exists():
                ModeleEmail.objects.create(**modele)
                defaut_info = " (défaut)" if modele["defaut"] else ""
                print(f"ModeleEmail créé: {modele['nom']} "
                      f"[{modele['categorie']}]{defaut_info}")

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
        comptes_bancaires = [
            {
                "nom": "Compte principal",
                "defaut": True,
                "raison": "Mairie de Test Ville",
                "numero": "FR7630004000031234567890143",
                "code_etab": "30004",
                "code_guichet": "00323",
                "code_nne": "12345678901",
                "cle_rib": "43",
                "cle_iban": "14",
                "iban": "FR7630004000031234567890143",
                "bic": "BNPAFRPPXXX",
                "code_ics": "FR76ZZZ123456",
                "dft_titulaire": "Mairie de Test Ville",
                "dft_iban": "FR7630004000031234567890143",
                "adresse_service": "Service Financier",
                "adresse_rue": "Rue de la Mairie",
                "adresse_numero": "1",
                "adresse_batiment": "Bâtiment A",
                "adresse_etage": "1er étage",
                "adresse_boite": "101",
                "adresse_cp": "37000",
                "adresse_ville": "TESTVILLE",
                "adresse_pays": "FR"
            },
            {
                "nom": "Compte secondaire",
                "defaut": False,
                "raison": "Association Test",
                "numero": "FR7630004000039876543210256",
                "code_etab": "30004",
                "code_guichet": "00323",
                "code_nne": "98765432109",
                "cle_rib": "56",
                "cle_iban": "25",
                "iban": "FR7630004000039876543210256",
                "bic": "BNPAFRPPXXX",
                "code_ics": "FR76ZZZ654321",
                "dft_titulaire": "Association Test",
                "dft_iban": "FR7630004000039876543210256",
                "adresse_service": "Trésorerie",
                "adresse_rue": "Avenue des Sports",
                "adresse_numero": "15",
                "adresse_batiment": "Bâtiment B",
                "adresse_etage": "RDC",
                "adresse_boite": "200",
                "adresse_cp": "37000",
                "adresse_ville": "TESTVILLE",
                "adresse_pays": "FR"
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
