"""M2-B2 — Fonction d'anonymisation à compléter (phase async individuelle).

Tu choisis ta stratégie et tu la défends dans `reflexion.md` :
- Suppression : remplacer l'entité par `[REDACTED]` ou `[NAME]`
- Substitution : Faker côté apprenant, ré-injection
- Généralisation : remplacer par un rôle (`[MANAGER]`, `[EMPLOYEE]`)
- Hash : empreinte irréversible

Le squelette pose la signature minimale. À toi de remplir.
"""
from __future__ import annotations

from email.mime import text
import re

import os
import pandas as pd
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# 1. Initialisation des moteurs industriels de Microsoft
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# TODO — charger le modèle spaCy une seule fois (au module load, pas dans la fonction)
import spacy
NLP = spacy.load("en_core_web_md")  # ou "fr_core_news_md" selon ton dataset




# Regex de complément (spaCy ne couvre pas tout — email, IBAN partiel, téléphone US)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE_RE = re.compile(r"\b\d{3}[.-]?\d{3}[.-]?\d{4}\b")
IBAN_PARTIAL_RE = re.compile(r"\*{2,}\d{4}")

def audit_with_en_model(text: str) -> dict:
    """
    EXTRACTS entities using ONLY the English model to document what it catches/misses.
    """
    if not isinstance(text, str) or not text.strip():
        return {"PERSON": [], "GPE": [], "ORG": [], "EMAILS": []}
        
    doc = NLP(text)
    return {
        "PERSON": [ent.text for ent in doc.ents if ent.label_ == "PERSON"],
        "GPE": [ent.text for ent in doc.ents if ent.label_ == "GPE"],
        "ORG": [ent.text for ent in doc.ents if ent.label_ == "ORG"],
        "EMAILS": EMAIL_RE.findall(text),
        "PHONE": PHONE_RE.findall(text),
        "IBAN": IBAN_PARTIAL_RE.findall(text)
    }

def anonymize_comments(text: str) -> str:
    """Anonymise un commentaire manager.

    Args:
        text: Texte libre potentiellement contenant des PII.

    Returns:
        Texte anonymisé selon la stratégie choisie.
    """
    # TODO 1 — Détecter les entités avec spaCy (PERSON, GPE, ORG)
    # doc = NLP(text)
    # for ent in doc.ents:
    #     if ent.label_ == "PERSON":
    #         # ⬇️ Applique TA stratégie (suppression / généralisation /
    #         #    substitution / hash) — à défendre dans reflexion.md
    #         text = text.replace(ent.text, ...)  # à compléter

    if not isinstance(text, str) or not text.strip():
        return ""

    anonymized = text

    # --- TODO 1 — Détecter les entités avec spaCy (PERSON) ---
    doc = NLP(anonymized)

    # --- COLLECTE ET TRI DES ENTITÉS NLP ---
    detected_names = []
    detected_gpe = []
    detected_org = []
    for ent in doc.ents:
        clean_text = ent.text.strip()
        if not clean_text:
            continue
        
        if ent.label_ == "PERSON":
            if clean_text not in detected_names:
                detected_names.append(clean_text)
        elif ent.label_ == "GPE":
            if clean_text not in detected_gpe:
                detected_gpe.append(clean_text)
        elif ent.label_ == "ORG":
            if clean_text not in detected_org:
                detected_org.append(clean_text)

    # Tri par longueur décroissante pour éviter les conflits de remplacement
    sorted_names = sorted(detected_names, key=len, reverse=True)
    sorted_gpe = sorted(detected_gpe, key=len, reverse=True)
    sorted_org = sorted(detected_org, key=len, reverse=True)

    # --- 2. APPLICATION DE LA STRATÉGIE DE GÉNÉRALISATION ---
    
    # Remplacement des personnes (Généralisation indexée pour la cohérence du fil)
    for idx, name in enumerate(sorted_names, start=1):
        # Utilisation des frontières de mots (\b) pour éviter d'anonymiser des morceaux de mots
        anonymized = re.sub(r'\b' + re.escape(name) + r'\b', f"[INDIVIDU_{idx}]", anonymized)

    # Remplacement des Lieux / GPE (Généralisation simple)
    for gpe in sorted_gpe:
        anonymized = re.sub(r'\b' + re.escape(gpe) + r'\b', "[LOCALITÉ]", anonymized)

    # Remplacement des Organisations / ORG (Généralisation simple)
    for org in sorted_org:
        anonymized = re.sub(r'\b' + re.escape(org) + r'\b', "[ORGANISATION]", anonymized)


    # TODO 2 — Compléter avec regex (spaCy ne détecte ni email ni IBAN partiel ni tel)
    anonymized = EMAIL_RE.sub("[EMAIL]", anonymized)
    anonymized = PHONE_RE.sub("[PHONE]", anonymized)
    anonymized = IBAN_PARTIAL_RE.sub("[IBAN]", anonymized)

    return anonymized

def anonymize_with_presidio(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""

    # --- ÉTAPE 1 : ANALYSE (Détection des PII) ---
    # Presidio prend en charge nativement le français si configuré, 
    # mais son modèle par défaut gère déjà très bien les structures mixtes.
    analysis_results = analyzer.analyze(
        text=text,
        entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "IBAN"],
        language="en"
    )

    # --- ÉTAPE 2 : CONFIGURATION DES OPÉRATEURS (Stratégies) ---
    # On définit comment transformer chaque entité détectée
    operators = {
        # Pour les personnes : Généralisation (remplacement par un titre/tag anonyme)
        "PERSON": OperatorConfig(
            "replace", 
            {"new_value": "[INDIVIDU]"}
        ),
        # Pour les données techniques : Suppression/Masquage par type
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
        "IBAN": OperatorConfig("replace", {"new_value": "[IBAN]"}),
    }

    # --- ÉTAPE 3 : ANONYMISATION ---
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=analysis_results,
        operators=operators
    )

    # --- ÉTAPE 4 : INDEXATION POST-PROCESSING (Optionnel) ---
    # Presidio remplace tout par [INDIVIDU]. Si on veut remettre les index [INDIVIDU_1],
    # on applique une petite passe de numérotation pour la cohérence textuelle.
    final_text = anonymized_result.text
    count = 1
    while "[INDIVIDU]" in final_text:
        final_text = final_text.replace("[INDIVIDU]", f"[INDIVIDU_{count}]", 1)
        count += 1

    return final_text



if __name__ == "__main__":
    # Test rapide
    sample = (
        "Allison Hill is a strong promotion candidate this year. "
        "Discussed with HR (Rhonda Smith, 651.216.1559). "
        "Budget pre-approved on account ****3503."
    )
    print("Avant :", sample)
    print("Après :", anonymize_comments(sample))