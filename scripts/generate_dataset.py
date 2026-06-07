"""Génère le dataset Athéna RH (M2-B2) de façon reproductible.

Le volet tabulaire est l'Adult Income (UCI, 32 561 lignes) — données réelles,
donc les disparate impacts sont stables d'une génération à l'autre.

Le volet textuel `manager_comments` est **synthétique** : des commentaires
managers en texte libre, majoritairement en anglais (~88 %) avec une part en
français (~12 %), truffés de PII (noms, emails, téléphones, IBAN partiels,
dates, références de ticket). Tout est produit avec Faker et une graine fixe
(``random_state=42``) → deux exécutions donnent exactement le même fichier.

Usage::

    python scripts/generate_dataset.py

Produit :
    data/adult_income_with_comments.csv   (~32 561 lignes, 16 colonnes)
    data/audit_sample.csv                  (200 lignes, stratifié 50/50 income)

Les deux fichiers sont volontairement git-ignorés (cf. .gitignore) : on ne
commite pas la donnée, on la régénère.
"""
from __future__ import annotations

import io
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd
from faker import Faker

SEED = 42
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Schéma canonique Adult Income (ordre des colonnes UCI).
COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "sex",
    "capital_gain", "capital_loss", "hours_per_week", "native_country", "income",
]

UCI_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/adult/adult.data"

# Part de commentaires en français (le reste en anglais). ~12 % → piège NER
# réaliste : un modèle spaCy anglais ratera les noms français.
FRENCH_RATIO = 0.12

# Gabarits de commentaires anglais. {p}=nom, {p2}=2e nom, {email}, {phone},
# {iban}, {date}, {ticket}. Chaque gabarit porte un sous-ensemble de PII.
EN_TEMPLATES = [
    "{p} is a strong promotion candidate this year. Discussed with HR ({p2}, {phone}). Budget pre-approved on account {iban}.",
    "Behavioral concern raised by colleague {p}. Manager {p2} ({email}) to follow up by {date}. Reference ticket {ticket}.",
    "Annual review for {p}: solid contributor, no concern. Manager: {p2}, contact {email}.",
    "PIP opened {date}. Coaching assigned to {p} ({email}). Review in 90 days. Confidential — HR contact: {p2}.",
    "{p} requested a transfer. Approved by {p2}. Reach them at {phone} for handover. Ticket {ticket}.",
    "Strong year for {p}. Bonus wired to account {iban}. Validated by {p2} on {date}.",
    "{p} flagged a conflict with {p2}. Mediation scheduled. HR follow-up: {email}.",
    "Onboarding complete for {p}. Buddy assigned: {p2} ({email}). No issues.",
    "{p} on extended leave since {date}. Backfill discussed with {p2}, {phone}.",
    "Performance below target for {p}. Action plan owned by {p2}. Ticket {ticket}.",
]

# Gabarits français (noms générés en locale fr_FR).
FR_TEMPLATES = [
    "RAS pour {p} cette année. Manager : {p2}.",
    "Entretien annuel de {p} : bon élément. Référent : {p2}, joignable au {phone}.",
    "Alerte comportementale signalée par {p2} au sujet de {p}. Suivi RH : {email}.",
    "Mobilité demandée par {p}. Validée par {p2} le {date}. Ticket {ticket}.",
    "Prime versée à {p} sur le compte {iban}. Contrôle : {p2}.",
    "Plan d'accompagnement ouvert pour {p}. Coaching confié à {p2} ({email}).",
]


def load_adult_tabular() -> pd.DataFrame:
    """Charge le volet tabulaire Adult Income (UCI, fallback OpenML).

    Returns:
        DataFrame de 32 561 lignes aux 15 colonnes canoniques, valeurs
        nettoyées (espaces supprimés), cible ``income`` en ``<=50K`` / ``>50K``.

    Raises:
        RuntimeError: si aucune source n'est joignable.
    """
    try:
        raw = urllib.request.urlopen(UCI_URL, timeout=20).read().decode()
        df = pd.read_csv(
            io.StringIO(raw), header=None, names=COLUMNS,
            skipinitialspace=True, na_values="?",
        )
        df = df.dropna(how="all")
        df["income"] = df["income"].str.replace(".", "", regex=False).str.strip()
        return df.reset_index(drop=True)
    except (urllib.error.URLError, TimeoutError, OSError):
        pass

    try:
        from sklearn.datasets import fetch_openml

        bunch = fetch_openml("adult", version=2, as_frame=True)
        df = bunch.frame.rename(
            columns={
                "education-num": "education_num",
                "marital-status": "marital_status",
                "capital-gain": "capital_gain",
                "capital-loss": "capital_loss",
                "hours-per-week": "hours_per_week",
                "native-country": "native_country",
                "class": "income",
            }
        )
        df["income"] = df["income"].astype(str).str.replace(".", "", regex=False).str.strip()
        return df[COLUMNS].reset_index(drop=True)
    except Exception as exc:  # noqa: BLE001 — on remonte une erreur claire
        raise RuntimeError(
            "Impossible de charger Adult Income (UCI et OpenML injoignables). "
            "Vérifie ta connexion réseau."
        ) from exc


def _fake_pii(fake_en: Faker, fake_fr: Faker, french: bool) -> dict[str, str]:
    """Construit un jeu de PII cohérent pour remplir un gabarit."""
    fake = fake_fr if french else fake_en
    return {
        "p": fake.name(),
        "p2": fake.name(),
        "email": fake_en.email(),  # emails toujours en format ASCII standard
        "phone": fake_en.numerify("###.###.####"),
        "iban": "****" + fake_en.numerify("####"),
        "date": fake_en.date_between(start_date="-1y", end_date="today").isoformat(),
        "ticket": "HR-" + fake_en.numerify("#####"),
    }


def build_comments(n: int) -> list[str]:
    """Génère ``n`` commentaires managers synthétiques (déterministe, seed 42)."""
    Faker.seed(SEED)
    fake_en = Faker("en_US")
    fake_fr = Faker("fr_FR")
    fake_en.seed_instance(SEED)
    fake_fr.seed_instance(SEED)

    comments: list[str] = []
    for i in range(n):
        french = (i % 100) < int(FRENCH_RATIO * 100)
        templates = FR_TEMPLATES if french else EN_TEMPLATES
        template = templates[i % len(templates)]
        comments.append(template.format(**_fake_pii(fake_en, fake_fr, french)))
    return comments


def main() -> None:
    """Produit les deux CSV dans ``data/``."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("Chargement Adult Income (UCI)…")
    df = load_adult_tabular()
    print(f"  → {len(df)} lignes, {df.shape[1]} colonnes")

    print("Injection des commentaires managers synthétiques (Faker, seed 42)…")
    df["manager_comments"] = build_comments(len(df))

    full_path = DATA_DIR / "adult_income_with_comments.csv"
    df.to_csv(full_path, index=False)
    print(f"  → {full_path} ({full_path.stat().st_size // 1024} Ko)")

    # Échantillon d'audit : 100 lignes par classe income (50/50), seed 42.
    sample = (
        df.groupby("income", group_keys=False)
        .sample(n=100, random_state=SEED)
        .sample(frac=1, random_state=SEED)
        .reset_index(drop=True)
    )
    sample_path = DATA_DIR / "audit_sample.csv"
    sample.to_csv(sample_path, index=False)
    print(f"  → {sample_path} ({len(sample)} lignes, stratifié 50/50)")


if __name__ == "__main__":
    main()