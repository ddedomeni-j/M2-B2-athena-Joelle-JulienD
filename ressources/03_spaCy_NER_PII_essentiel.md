# spaCy NER pour détection de PII — Mini-cours

> Brief associé : M2-B2 (phase async perso)
> Durée de lecture + pratique : ~25 min
> Pré-requis : `pip install spacy` + `python -m spacy download en_core_web_md`
> (~50 Mo, à faire une fois).

## Pourquoi cette techno ?

**NER** = *Named Entity Recognition*. Le modèle prend un texte et **identifie
des entités nommées** : personnes (PERSON), lieux (GPE), organisations
(ORG), dates, monnaies, etc.

Pour de **l'anonymisation**, c'est le **point de départ** : on détecte les
entités, puis on les remplace (suppression / substitution / généralisation /
hash — cf. mini-cours 04).

**Pourquoi spaCy** :
- **Pré-entraîné** : pas besoin d'annoter, ça marche out-of-the-box
- **Multi-langue** : `en_core_web_md` (anglais), `fr_core_news_md` (français)
- **Rapide** : 10 000 commentaires en < 1 min
- **Standard industriel** : utilisé en prod par de nombreuses entreprises

**Limites** (à connaître pour la note de réflexion) :
- **Recall imparfait** : spaCy rate des noms peu courants, des typos, des
  noms étrangers
- **Pas de détection d'email, téléphone, IBAN** par défaut → complèter par
  **regex**
- **Sensibilité au domaine** : entraîné sur Wikipedia/news, moins bon sur
  langage RH/business

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **spaCy NER + regex** | Standard M2-B2 — combinaison robuste pour PII tabulaires/textuelles |
| **Microsoft Presidio** | Wrapper plus complet (spaCy + regex + transformers) — bonus M2-B2, central en M7 |
| **Hugging Face NER (transformers)** | Modèles BERT/DistilBERT plus précis — plus lourd, justifié en M4+ |
| **LLM via prompt** | Tentant mais coûteux + non déterministe + risque RGPD (envoi de PII à un fournisseur tiers). **Anti-pattern M2.** |
| **Regex pur** | OK pour formats stricts (email, téléphone). **Insuffisant pour les noms** (variabilité énorme) |

## Concepts clés

- **Modèle spaCy** : objet `nlp = spacy.load("en_core_web_md")`. Charge une
  fois (~50 Mo), réutilise partout.
- **Document spaCy** : `doc = nlp(text)`. Itérable sur ses tokens et ses
  entités (`doc.ents`).
- **Entité** : objet avec `.text` (chaîne brute), `.label_` (PERSON / GPE /
  ORG / DATE / …), `.start_char` / `.end_char` (positions).
- **Labels standards** :
  - `PERSON` : noms de personnes
  - `ORG` : organisations (entreprises, agences)
  - `GPE` : entités géopolitiques (pays, villes)
  - `LOC` : lieux non-géopolitiques (montagnes, océans)
  - `DATE`, `TIME`, `MONEY`, `PERCENT`, `CARDINAL` : valeurs typées
- **Complément regex** : pour `EMAIL`, `PHONE`, `IBAN`, `IBAN_PARTIAL` — spaCy
  ne les détecte pas, à compléter manuellement.

## Exemple minimal qui tourne

```python
# spacy==3.7.5, modèle en_core_web_md préinstallé
import re

import spacy

NLP = spacy.load("en_core_web_md")  # à faire UNE fois au module load

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE_RE = re.compile(r"\b\d{3}[.-]?\d{3}[.-]?\d{4}\b")
IBAN_RE = re.compile(r"\*{2,}\d{4}")  # IBAN partiel `****XXXX`


def detect_pii(text: str) -> dict[str, list[str]]:
    """Détecte les PII dans un texte. Retourne un dict {type: [valeurs]}."""
    doc = NLP(text)

    # spaCy : PERSON, GPE, ORG
    result = {"PERSON": [], "GPE": [], "ORG": []}
    for ent in doc.ents:
        if ent.label_ in result:
            result[ent.label_].append(ent.text)

    # Regex : EMAIL, PHONE, IBAN
    result["EMAIL"] = EMAIL_RE.findall(text)
    result["PHONE"] = PHONE_RE.findall(text)
    result["IBAN"] = IBAN_RE.findall(text)

    return {k: v for k, v in result.items() if v}  # filtre vides


# Test
sample = (
    "Allison Hill is a strong promotion candidate this year. "
    "Discussed with HR (Rhonda Smith, 651.216.1559). "
    "Budget pre-approved on account ****3503."
)
print(detect_pii(sample))
# {'PERSON': ['Allison Hill', 'Rhonda Smith'], 'PHONE': ['651.216.1559'], 'IBAN': ['****3503']}
```

## Exercice guidé

Sur 10 lignes de `audit_sample.csv`, applique `detect_pii` et compte :

1. Le total de PII détectées par type (`PERSON`, `EMAIL`, `PHONE`, etc.)
2. Les **faux positifs** observés (texte normal qui aurait été détecté à tort)
3. Les **faux négatifs** observés (PII réelles que spaCy a ratées)

**Pas besoin de calcul de métrique formelle** (précision/rappel/F1) — la
**vérification qualitative sur ~10 exemples** suffit pour le brief
(cf. brief, tâche 7).

**Solution attendue** :

```python
import pandas as pd

df = pd.read_csv("data/audit_sample.csv")
sample = df["manager_comments"].head(10)

for i, text in enumerate(sample):
    print(f"--- Exemple {i+1} ---")
    print(text)
    print("Détections :", detect_pii(text))
    print()
```

Tu observeras :
- spaCy attrape **bien** les noms anglais courants (~95 % recall sur
  10 exemples Faker)
- spaCy attrape **moins bien** les noms français (utilise `fr_core_news_md`)
- spaCy attrape **mal** les noms exotiques ou tronqués
- Les regex font le travail pour `EMAIL`, `PHONE`, `IBAN`

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Charger `nlp = spacy.load(...)` dans la fonction (au lieu du module) | Lent — 1 seconde par appel. Charge au module load. |
| Oublier `python -m spacy download en_core_web_md` | `OSError: [E050] Can't find model 'en_core_web_md'` |
| Utiliser `en_core_web_sm` (small) plutôt que `md` (medium) | Précision moindre, mais OK pour M2. `md` reste le meilleur compromis. |
| Regex email trop laxiste | Match des trucs comme `a@b.c` qui ne sont pas des emails valides — utilise la regex robuste fournie |
| Détecter sans dédupliquer | Tu remplaces deux fois la même entité, parfois avec des résultats incohérents |
| Modifier `text` pendant `for ent in doc.ents` | Décale les positions — fais une liste d'entités d'abord, puis remplace |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| `Can't find model 'en_core_web_md'` | Modèle pas téléchargé : `python -m spacy download en_core_web_md` |
| spaCy détecte des dates partout | `DATE` est dans le label set — tu peux filtrer si tu n'en veux pas |
| spaCy ne détecte pas un nom évident | Nom court ou peu courant — utilise `fr_core_news_md` si français, ou ajoute des règles regex de complément |
| Performance lente (> 1 s par commentaire) | Tu recharges le modèle à chaque appel — passe-le en variable globale du module |
| Regex `\d{10}` ne marche pas | Les numéros US ont des séparateurs : `\d{3}[.-]?\d{3}[.-]?\d{4}` |

## Pour aller plus loin

- **Doc officielle spaCy NER** : <https://spacy.io/usage/linguistic-features#named-entities>
- **Liste des modèles spaCy FR/EN** : <https://spacy.io/models>
- **Microsoft Presidio** (bonus M2-B2) : <https://microsoft.github.io/presidio/>
  — wrapper qui combine spaCy + regex + transformers, prêt à l'emploi
- **Wikipédia — Data anonymization** : <https://en.wikipedia.org/wiki/Data_anonymization>
  (panorama des techniques)
  — bonnes pratiques générales

## Vérification (checklist apprenant)

- [ ] `pip install spacy` + `python -m spacy download <modèle>` faits
- [ ] J'ai chargé le modèle **une seule fois** au module load
- [ ] J'ai testé `detect_pii` sur ~10 exemples de `audit_sample.csv`
- [ ] J'ai noté les **faux positifs** et **faux négatifs** observés (matière
      pour ma `reflexion.md`)
- [ ] J'ai complété spaCy avec **regex** pour EMAIL, PHONE, IBAN
- [ ] J'ai compris que l'évaluation est **qualitative** (~10 exemples),
      pas une benchmark formelle