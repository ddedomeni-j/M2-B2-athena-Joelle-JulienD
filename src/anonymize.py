"""M2-B2 — Fonction d'anonymisation à compléter (phase async individuelle).

Tu choisis ta stratégie et tu la défends dans `reflexion.md` :
- Suppression : remplacer l'entité par `[REDACTED]` ou `[NAME]`
- Substitution : Faker côté apprenant, ré-injection
- Généralisation : remplacer par un rôle (`[MANAGER]`, `[EMPLOYEE]`)
- Hash : empreinte irréversible

Le squelette pose la signature minimale. À toi de remplir.
"""
from __future__ import annotations

import re

# TODO — charger le modèle spaCy une seule fois (au module load, pas dans la fonction)
# import spacy
# NLP = spacy.load("en_core_web_md")  # ou "fr_core_news_md" selon ton dataset

# Regex de complément (spaCy ne couvre pas tout — email, IBAN partiel, téléphone US)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE_RE = re.compile(r"\b\d{3}[.-]?\d{3}[.-]?\d{4}\b")
IBAN_PARTIAL_RE = re.compile(r"\*{2,}\d{4}")


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

    # TODO 2 — Compléter avec regex (spaCy ne détecte ni email ni IBAN partiel ni tel)
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = IBAN_PARTIAL_RE.sub("[IBAN]", text)

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