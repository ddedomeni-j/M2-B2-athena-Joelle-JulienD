# Stratégies d'anonymisation — Mini-cours

> Brief associé : M2-B2 (phase async perso)
> Durée de lecture + pratique : ~25 min
> Pré-requis : détection PII en place (mini-cours 03).

## Pourquoi cette techno ?

Une fois les PII détectées (via spaCy + regex), il faut **décider quoi en
faire**. **4 stratégies principales**, chacune avec ses trade-offs.

Ton choix dépend :
- du **risque légal** (RGPD, AI Act, secteur)
- de la **finalité métier** (faut-il garder de la lisibilité ?)
- de la **réversibilité** (peut-on retrouver l'original ? veut-on
  pouvoir ?)

**Important** : il n'y a pas de "bonne" stratégie universelle — il y a
**ta** stratégie défendue dans `reflexion.md`.

## Concepts clés — les 4 stratégies

### 1. **Suppression / masking**
Remplace l'entité par un placeholder fixe.

```python
"Allison Hill is a candidate" → "[NAME] is a candidate"
```

- ✅ **Simple**, **irréversible**, **sûr** au sens RGPD
- ❌ Perd toute info utile (impossible de tracker la même personne dans 2 commentaires)

### 2. **Substitution**
Remplace par une valeur **cohérente mais fake** (Faker).

```python
"Allison Hill is a candidate" → "Sarah Johnson is a candidate"
```

- ✅ Texte reste **lisible**, **réaliste**
- ✅ **Cohérence** possible si on map la même PII → même fake (avec un cache)
- ❌ **Risque de ré-identification** si la substitution leak des infos
  (ex. on garde le genre, l'origine ethnique du nom)
- ❌ Peut induire en erreur (le lecteur pense lire un vrai nom)

### 3. **Généralisation**
Remplace par une **catégorie** ou un **rôle**.

```python
"Allison Hill is a candidate" → "[MANAGER] is a candidate"
"contact 651.216.1559" → "contact [US_PHONE]"
```

- ✅ Conserve l'info **structurelle** (« il y a un nom de manager ici »)
- ✅ Lisible, contextuel
- ❌ Demande une typologie a priori (qui est manager ? qui est employé ?)
- ❌ Peut être moins lisible qu'une vraie substitution

### 4. **Hash**
Empreinte cryptographique à **sens unique** (on n'inverse pas SHA-256
directement), **mais ré-identifiable** sur un espace fini → c'est de la
**pseudonymisation**, pas une anonymisation.

```python
"Allison Hill" → "a8f3..." (SHA-256 tronqué)
```

- ✅ **Cohérence parfaite** : même PII → même hash partout
- ✅ **Sens unique** cryptographiquement (avec sel)
- ❌ **Ré-identifiable** sur un espace fini : qui possède le sel peut re-hasher
  la liste des noms → **pseudonymisation**, pas anonymisation
- ❌ **Illisible** pour un humain
- ❌ Le hash sans sel permet la ré-identification par dictionnaire (rainbow
  table) — toujours saler

## ⚠️ Vocabulaire légal : PII ≠ pseudonymisation ≠ anonymisation

Trois notions que le RGPD distingue nettement, et qu'on confond souvent :

- **PII détectée ≠ donnée anonymisée.** Repérer une PII (spaCy, regex) ne la
  protège pas — c'est l'étape *avant* le traitement, pas le traitement.
- **Pseudonymisation** (RGPD, **art. 4-5**) : la donnée ne peut plus être
  attribuée à une personne **sans information supplémentaire** (un sel, une
  table de correspondance, une clé) conservée à part. La donnée reste
  **personnelle** → le RGPD **s'applique toujours**.
- **Anonymisation** (RGPD, **considérant 26**) : ré-identification
  **irréversible et raisonnablement impossible**, même en croisant d'autres
  sources. La donnée sort alors du périmètre RGPD.

> 🔑 **Le hash est une _pseudonymisation_, pas une anonymisation légale.** Même
> salé, l'espace des noms est fini : qui possède le sel peut re-hasher la liste
> des noms et ré-identifier. Donc la colonne « RGPD-friendly » ci-dessous
> signifie « **réduit le risque** », **pas** « sort la donnée du RGPD ». Seule
> la **suppression** (sans table) s'en approche réellement.

## Comparaison synthétique

| Stratégie | Lisibilité | Réversibilité | Cohérence | Réduit le risque RGPD |
|---|---|---|---|---|
| Suppression | ❌ | ❌ | ❌ | ✅✅ |
| Substitution (avec map) | ✅ | ❌ (si pas de cache) | ✅ avec map persistée | ✅ |
| Substitution (sans map) | ✅ | ❌ | ❌ | ✅ |
| Généralisation | 🟡 | ❌ | 🟡 (catégorie) | ✅ |
| Hash | ❌ | 🟡 (re-hash possible si on a le sel) | ✅✅ | ✅ |

## Exemple minimal — stratégie hybride

```python
import re
from hashlib import sha256

import spacy

NLP = spacy.load("en_core_web_md")
HASH_SALT = "atos_m2_b2_salt"  # secret en vrai, env var

EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")
PHONE_RE = re.compile(r"\b\d{3}[.-]?\d{3}[.-]?\d{4}\b")
IBAN_RE = re.compile(r"\*{2,}\d{4}")


def _hash(value: str) -> str:
    """Hash court avec sel (8 hex chars suffisent en interne)."""
    return sha256((HASH_SALT + value).encode()).hexdigest()[:8]


def anonymize_comments(text: str) -> str:
    """Stratégie hybride :
       - PERSON → généralisation `[PERSON_<hash>]` (cohérence, pas de table de correspondance)
       - EMAIL → suppression `[EMAIL]`
       - PHONE → suppression `[PHONE]`
       - IBAN → suppression `[IBAN]`
       - GPE / ORG → conservés (info contextuelle utile)
    """
    doc = NLP(text)

    # spaCy : collecter PERSON (on traite plus tard pour ne pas casser les positions)
    persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

    # Remplacement PERSON par hash court
    for name in persons:
        text = text.replace(name, f"[PERSON_{_hash(name)}]")

    # Regex : suppression simple
    text = EMAIL_RE.sub("[EMAIL]", text)
    text = PHONE_RE.sub("[PHONE]", text)
    text = IBAN_RE.sub("[IBAN]", text)

    return text


# Test
sample = (
    "Allison Hill is a strong promotion candidate this year. "
    "Discussed with HR (Rhonda Smith, 651.216.1559, rhonda@hr.example). "
    "Budget pre-approved on account ****3503."
)
print(anonymize_comments(sample))
# → "[PERSON_a8f31c4d] is a strong promotion candidate this year.
#    Discussed with HR ([PERSON_b2e91f88], [PHONE], [EMAIL]).
#    Budget pre-approved on account [IBAN]."
```

Avec cette stratégie :
- Tu **conserves la cohérence** (même Allison Hill → même hash partout)
- Tu évites une **table de correspondance** (rien à stocker ni à protéger en
  plus ; ça reste de la pseudonymisation, pas une anonymisation)
- Tu **gardes le contexte** lisible (« il y a 2 personnes différentes »)
- Tu **supprimes** les PII fortement identifiantes (email, téléphone, IBAN)

## Exercice guidé

Choisis **ta stratégie** parmi les 4 (ou un mix) et **défends-la** dans
`reflexion.md` :

1. Quelle stratégie ?
2. Pourquoi (RGPD, lisibilité, finalité métier) ?
3. Quel **trade-off** as-tu accepté ?
4. Quelles **limites** observes-tu sur tes 5 exemples avant/après ?

**Pas de "bonne" réponse** — il faut juste que **ta** réponse soit
**argumentée**.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Hash sans sel | Ré-identifiable par dictionnaire (rainbow table) |
| Substitution Faker sans seed | Pas reproductible — fais `Faker.seed(42)` |
| Substitution qui leak des features (genre, ethnie via nom) | RGPD-suspect — préfère hash ou généralisation |
| Suppression sans cohérence | Tu remplaces "Allison Hill" différemment selon où il apparaît |
| Anonymiser GPE/ORG inutilement | Tu perds le contexte sans gain RGPD réel |
| Mélanger stratégies sans expliquer | La `reflexion.md` devient illisible |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| 2 hash différents pour le même nom | Tu hashes après modification du texte — hash AVANT le replace |
| `replace()` casse une autre entité par effet de bord | Tu remplaces une sous-chaîne courte qui matche ailleurs — utilise des positions ou regex avec délimiteurs |
| Texte anonymisé devient illisible | Tu as tout supprimé sans rien laisser de contextuel — re-équilibre avec de la généralisation |
| `[PERSON_<hash>]` partout, plus rien de lisible | Tu peux raccourcir le placeholder en `[P1]`, `[P2]` avec un compteur cohérent |
| Anonymisation reste réversible (le DPO retrouve les vrais noms) | Tu as substitué avec Faker mais leak le genre + l'origine — utilise hash ou généralisation à la place |

## Pour aller plus loin

- **CNIL — Anonymisation** : <https://www.cnil.fr/fr/technologies/lanonymisation-de-donnees-personnelles>
  (le guide officiel français — règles d'or, exemples)
- **RGPD — Considérant 26** : définit ce qu'est « anonyme » vs « pseudonymisé »
- **Wikipédia — Data anonymization** : <https://en.wikipedia.org/wiki/Data_anonymization>
  (panorama des techniques)
- **Microsoft Presidio — Anonymizer** : <https://microsoft.github.io/presidio/anonymizer/>
  (bonus, voir mini-cours 05)

## Vérification (checklist apprenant)

- [ ] J'ai choisi **ma stratégie** parmi les 4 (ou un mix)
- [ ] J'ai implémenté `anonymize_comments(text: str) -> str` dans
      `src/anonymize.py`
- [ ] J'ai testé sur ~10 exemples de `audit_sample.csv`
- [ ] J'ai noté **avant/après** sur au moins **5 exemples** dans mon notebook
- [ ] J'ai défendu ma stratégie dans `reflexion.md` (4 questions imposées)
- [ ] J'ai identifié au moins **1 limite** de ma stratégie