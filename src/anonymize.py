"""M2-B2 — Fonction d'anonymisation à compléter (phase async individuelle).

Tu choisis ta stratégie et tu la défends dans `reflexion.md` :
- Suppression : remplacer l'entité par `[REDACTED]` ou `[NAME]`
- Substitution : Faker côté apprenant, ré-injection
- Généralisation : remplacer par un rôle (`[MANAGER]`, `[EMPLOYEE]`)
- Hash : empreinte irréversible

Le squelette pose la signature minimale. À toi de remplir.
"""
from __future__ import annotations

import spacy
import re
import unicodedata

# TODO — charger le modèle spaCy une seule fois (au module load, pas dans la fonction)
NLP = spacy.load("en_core_web_md")  # ou "fr_core_news_md" selon ton dataset

# Regex de complément (spaCy ne couvre pas tout — email, IBAN partiel, téléphone US)
# EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# PHONE_RE = re.compile(r"\b\d{3}[.-]?\d{3}[.-]?\d{4}\b")
PHONE_RE = re.compile(r"\b(?:\+?1[\s.-]?)?(?:\(?\d{3}\)?[\s.-]?)\d{3}[\s.-]?\d{4}\b")
# IBAN_PARTIAL_RE = re.compile(r"\*{2,}\d{4}")
ACCOUNT_RE = re.compile(r"\*{2,}\s?\d{2,}\b")
IBAN_PARTIAL_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:[\s-]?[A-Z0-9*]{2,}){2,}\b")

def infer_role(ent, doc):
    """
    Devine le rôle d'une personne selon le contexte proche
    """
    # window = doc[max(0, ent.start - 3): min(len(doc), ent.end + 3)]
    window = doc[max(0, ent.start - 2): min(len(doc), ent.end)]
    context = window.text.lower()

    if any(word in context for word in ["manager", "director", "head", "lead", "responsable", "supervisor", "chief", "approved", "validated", "approuvé", "validé"]) :
    #    any(word in windowPrec.text.lower() for word in []):
        return "MANAGER"

    if any(word in context for word in ["hr", "human resources", "recruiter"]):
        return "HR"

    if any(word in context for word in ["employee", "staff", "candidate", "team member", "for", "pour", "colleague"]) :
    #    any(word in windowPrec.text.lower() for word in []):
        return "EMPLOYEE"

    if any(word in context for word in ["client", "customer"]):
        return "CLIENT"

    return "PERSON"

def normalize_text(text: str) -> str:
    """
    Normalise le texte :
    - minuscules
    - suppression des accents
    """
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(char for char in text if unicodedata.category(char) != "Mn")
    return text

def generalize_date_or_time(entity_text: str, entity_label: str) -> str:
    """
    Généralise une entité DATE ou TIME en année quand c'est possible.

    Exemples :
    - "March 12, 2024" -> "[YEAR_2024]"
    - "12/03/2024" -> "[YEAR_2024]"
    - "2024-03-12" -> "[YEAR_2024]"
    - "en 2023" -> "[YEAR_2023]"
    - "last year" -> "[DATE]"
    - "10:30 AM" -> "[TIME]"
    """

    if not isinstance(entity_text, str):
        return f"[{entity_label}]"

    text = entity_text.strip()
    normalized = normalize_text(text)

    # 1. Chercher une année explicite sur 4 chiffres
    year_match = re.search(r"\b(19\d{2}|20\d{2}|21\d{2})\b", normalized)

    if year_match:
        year = year_match.group(1)
        return f"[YEAR {year}]"

    # 2. Chercher les dates numériques avec année sur 2 chiffres
    # Exemples : 12/03/24, 12-03-24, 03.12.24
    short_year_match = re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-](\d{2})\b",
        normalized
    )

    if short_year_match:
        short_year = int(short_year_match.group(1))

        # Heuristique simple :
        # 00-30 -> 2000-2030
        # 31-99 -> 1931-1999
        if short_year <= 30:
            year = 2000 + short_year
        else:
            year = 1900 + short_year

        return f"[YEAR_{year}]"

    # 3. Expressions relatives : on ne peut pas déduire l'année sans date de référence
    relative_date_keywords = [
        "today", "yesterday", "tomorrow",
        "last year", "next year", "this year",
        "aujourd hui", "hier", "demain",
        "l annee derniere", "annee derniere",
        "l an prochain", "annee prochaine",
        "cette annee"
    ]

    if any(keyword in normalized for keyword in relative_date_keywords):
        return "[DATE]"

    # 4. Si c'est une heure pure, on généralise en TIME
    time_pattern = re.compile(
        r"\b\d{1,2}:\d{2}(?::\d{2})?\s?(am|pm)?\b"
    )

    if entity_label == "TIME" or time_pattern.search(normalized):
        return "[TIME]"

    # 5. Fallback selon le label spaCy
    if entity_label == "DATE":
        return "[DATE]"

    if entity_label == "TIME":
        return "[TIME]"

    return f"[{entity_label}]"

def anonymize_comments(text: str) -> str:
    """Anonymise un commentaire manager.

    Args:
        text: Texte libre potentiellement contenant des PII.

    Returns:
        Texte anonymisé selon la stratégie choisie.
    """

    # TODO 2 — Compléter avec regex (spaCy ne détecte ni email ni IBAN partiel ni tel)
    # On inverse pour traiter les informations non reconnues par spaCy avant de traiter les entités mieux détectées par spaCy
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = ACCOUNT_RE.sub("[ACCOUNT]", text)
    text = IBAN_PARTIAL_RE.sub("[IBAN]", text)

    # TODO 1 — Détecter les entités avec spaCy (PERSON, GPE, ORG)
    doc = NLP(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Généralisation pour essayer de garder le rôle de la personne
            role = infer_role(ent, doc)
            text = text.replace(ent.text, f"[{role}]")
        elif ent.label_ == "EMAIL":
            # Substitution par un placeholder : on ne souhaite pas garder de traçabilité de cette information
            text = text.replace(ent.text, "[EMAIL]")
        elif ent.label_ == "GPE " or ent.label_ == "LOC":
            # Substitution par un placeholder : on ne souhaite pas garder de traçabilité de cette information
            text = text.replace(ent.text, "[LOCATION]")
        elif ent.label_ == "ORG":
            continue  # On ne touche pas aux organisations pour l'instant
        elif ent.label_ == "DATE" or ent.label_ == "TIME":
            # Généralisation pour essayer de garder l'année
            text = text.replace(ent.text, generalize_date_or_time(ent.text, ent.label_))

    return text

if __name__ == "__main__":
    # Test rapide
    sample = (
        "Allison Hill is a strong promotion candidate this year. "
        "Discussed with HR (Rhonda Smith, 651.216.1559). "
        "Budget pre-approved on account ****3503."
    )
    print("Avant :", sample)
    print("Après :", anonymize_comments(sample))