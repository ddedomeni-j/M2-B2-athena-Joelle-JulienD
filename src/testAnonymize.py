import pandas as pd
from anonymize import anonymize_comments
from collections import Counter, defaultdict
import re

AUDIT_FILE = "./data/audit_sample.csv"

TEXT_COLUMN = "manager_comments"
MANUAL_COLUMN = "manual_transcription"

EXPECTED_LABELS = [
    "PERSON",
    "EMAIL",
    "PHONE",
    "ACCOUNT",
    "IBAN",
    "YEAR",
    "LOCATION",
    "ORG",
]

TAG_RE = re.compile(r"\[([A-Z_]+)(?:[ _-]\d{4})?\]")

def normalize_label(label: str) -> str:
    """
    Normalise certains labels pour faciliter la comparaison.
    Exemple :
    [YEAR_2024] -> YEAR
    [MASKED_ACCOUNT] -> ACCOUNT
    [BANK_ID] -> ACCOUNT
    """

    if label.startswith("YEAR"):
        return "YEAR"

    if label in {"MASKED_ACCOUNT", "BANK_ID", "IBAN_PARTIEL"}:
        return "ACCOUNT"

    if label in {"TELEPHONE", "PHONE_US", "PHONE_FR"}:
        return "PHONE"

    if label in {"NOM_PERSONNE", "PER"}:
        return "PERSON"

    if label in {"LOC", "GPE", "LIEU"}:
        return "LOCATION"

    return label

def extract_tags(text: str) -> Counter:
    """
    Extrait les tags du type [PERSON], [EMAIL], [ACCOUNT], [YEAR_2024], etc.
    Retourne un Counter par label.
    """

    if not isinstance(text, str):
        return Counter()

    labels = []

    for match in TAG_RE.finditer(text):
        raw_label = match.group(1)
        label = normalize_label(raw_label)
        labels.append(label)

    return Counter(labels)


# ============================================================
# Comparaison ligne par ligne
# ============================================================

def compare_tag_counts(auto_text: str, manual_text: str) -> dict:
    """
    Compare les tags détectés automatiquement avec les tags attendus manuellement.
    Retourne les TP, FP, FN par label.
    """

    auto_counts = extract_tags(auto_text)
    manual_counts = extract_tags(manual_text)

    labels = set(auto_counts.keys()) | set(manual_counts.keys()) | set(EXPECTED_LABELS)

    result = {}

    for label in labels:
        auto_n = auto_counts[label]
        manual_n = manual_counts[label]

        tp = min(auto_n, manual_n)
        fp = max(auto_n - manual_n, 0)
        fn = max(manual_n - auto_n, 0)

        result[label] = {
            "auto": auto_n,
            "manual": manual_n,
            "tp": tp,
            "fp": fp,
            "fn": fn,
        }

    return result

# ============================================================
# Chargement des fichiers
# ============================================================

df = pd.read_csv(AUDIT_FILE, encoding="utf-8", sep=";")

# ============================================================
# Gestion d'erreur
# ============================================================

if TEXT_COLUMN not in df.columns:
    raise ValueError(
        f"La colonne '{TEXT_COLUMN}' est absente de {AUDIT_FILE}. "
        f"Colonnes disponibles : {list(df.columns)}"
    )


if MANUAL_COLUMN not in df.columns:
    raise ValueError(
        f"Colonne manuelle absente : {MANUAL_COLUMN}. "
        f"Colonnes disponibles : {list(df.columns)}"
    )

# ============================================================
# Sélection des 20 premières lignes
# ============================================================

df_20 = df.head(min(20,len(df))).copy()

df_20["auto_anonymized"] = df_20[TEXT_COLUMN].apply(anonymize_comments)

# ============================================================
# Calcul des métriques globales
# ============================================================

global_scores = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0, "auto": 0, "manual": 0})
line_errors = []

for idx, row in df_20.iterrows():
    auto_text = row["auto_anonymized"]
    manual_text = row[MANUAL_COLUMN]

    comparison = compare_tag_counts(auto_text, manual_text)

    row_has_error = False
    row_errors = []

    for label, values in comparison.items():
        global_scores[label]["tp"] += values["tp"]
        global_scores[label]["fp"] += values["fp"]
        global_scores[label]["fn"] += values["fn"]
        global_scores[label]["auto"] += values["auto"]
        global_scores[label]["manual"] += values["manual"]

        if values["fp"] > 0 or values["fn"] > 0:
            row_has_error = True

            if values["fn"] > 0:
                row_errors.append(
                    f"{label}: {values['fn']} non détecté(s)"
                )

            if values["fp"] > 0:
                row_errors.append(
                    f"{label}: {values['fp']} détecté(s) en trop"
                )

    if row_has_error:
        line_errors.append({
            "index": idx,
            "original": row[TEXT_COLUMN],
            "auto_anonymized": auto_text,
            "manual_anonymized": manual_text,
            "errors": row_errors,
        })

# ============================================================
# Tableau de résumé par type de PII
# ============================================================

summary_rows = []

for label, scores in global_scores.items():
    tp = scores["tp"]
    fp = scores["fp"]
    fn = scores["fn"]

    recall = tp / (tp + fn) if (tp + fn) > 0 else None
    precision = tp / (tp + fp) if (tp + fp) > 0 else None
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision is not None and recall is not None and (precision + recall) > 0
        else None
    )

    summary_rows.append({
        "label": label,
        "manual_expected": scores["manual"],
        "auto_detected": scores["auto"],
        "true_positive": tp,
        "false_positive": fp,
        "false_negative": fn,
        "recall_detection_ratio": recall,
        "precision": precision,
        "f1_score": f1,
    })

summary_df = pd.DataFrame(summary_rows)

summary_df = summary_df.sort_values(
    by=["manual_expected", "auto_detected"],
    ascending=False
)

# ============================================================
# Affichage du résumé
# ============================================================

print("\n========== RATIO DE DÉTECTION PAR TYPE ==========\n")

print(summary_df)

print("\nRésumé :\n")

for _, row in summary_df.iterrows():
    label = row["label"]

    recall = row["recall_detection_ratio"]
    precision = row["precision"]

    recall_str = "N/A" if pd.isna(recall) else f"{recall:.1%}"
    precision_str = "N/A" if pd.isna(precision) else f"{precision:.1%}"

    print(
        f"- {label} : "
        f"attendu={row['manual_expected']}, "
        f"détecté={row['auto_detected']}, "
        f"TP={row['true_positive']}, "
        f"FP={row['false_positive']}, "
        f"FN={row['false_negative']}, "
        f"recall={recall_str}, "
        f"precision={precision_str}"
    )


# ============================================================
# Affichage des erreurs en dessous
# ============================================================
DEBUG = False
if DEBUG:
    print("\n========== ERREURS DÉTAILLÉES ==========\n")

    if not line_errors:
        print("Aucune erreur détectée sur les tags comparés.")
    else:
        for error in line_errors:
            print("\n----------------------------------------")
            print(f"Ligne index : {error['index']}")

            print("\nErreurs :")
            for e in error["errors"]:
                print(f"- {e}")

            print("\nTexte original :")
            print(error["original"])

            print("\nAnonymisation automatique :")
            print(error["auto_anonymized"])

            print("\nAnonymisation manuelle :")
            print(error["manual_anonymized"])
