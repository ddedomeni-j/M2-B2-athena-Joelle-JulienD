# Audit éthique complet (DI + intersectionnalité) — Mini-cours

> Brief associé : M2-B2
> Durée de lecture + pratique : ~25 min
> Pré-requis : avoir compris le disparate impact en M2-B1 (mini-cours 02).

## Pourquoi cette techno ?

En M2-B1 tu as appris à calculer le **disparate impact (DI)** sur une seule
variable sensible. En M2-B2, on **étend** :

1. **Plusieurs variables sensibles en parallèle** : sex, race,
   native_country — un tableau de DI plutôt qu'une valeur isolée
2. **Intersectionnalité** : DI sur le croisement de 2 variables sensibles
   (`sex × race`, `sex × native_country`). C'est là que les biais
   structurels les plus graves apparaissent — souvent invisibles quand on
   regarde une seule variable à la fois.

C'est la **base** d'un audit éthique sérieux. En M7-M8 on ira plus loin
(autres métriques : Equalized Odds, Statistical Parity Difference, etc.).
En M2-B2 on s'arrête au DI agrégé + intersectionnalité simple.

**Pourquoi l'intersectionnalité compte** : sur Adult Income, le DI est déjà
alarmant variable par variable (`sex` ≈ 0.36, `race` ≈ 0.35), mais il
**chute encore** sur le croisement `sex × race` (≈ 0.16) — un sous-groupe
(femmes *Other* ou *Black*) bien plus pénalisé, invisible quand on regarde
`sex` et `race` séparément. Dans d'autres jeux de données, le DI peut être OK
sur chaque variable isolée (0.85, 0.88) et catastrophique au croisement :
c'est tout l'intérêt de croiser.

**Alternatives à connaître :**

| Approche | Quand l'utiliser ? |
|---|---|
| **Calcul pandas direct** | Audit M2 — clair, transparent, sans dépendance. **Notre cas.** |
| **Fairlearn `MetricFrame`** | Plusieurs métriques en parallèle (DI, SPD, Equal Odds) — bonus M2, central M7 |
| **AIF360 (IBM)** | Framework complet, lourd — overkill pour M2 |

## Concepts clés

- **Tableau de DI** : un DataFrame avec une ligne par variable sensible,
  colonnes `(SR_min, SR_max, DI, verdict_4/5)`.
- **Variable composite intersectionnelle** : `df["sex_race"] = df["sex"] + "_" + df["race"]`.
  Tu obtiens N modalités (ici 2 × 5 = 10).
- **Modalités à faible support** : si une intersection a moins de **30 observations**,
  le DI est **statistiquement fragile** — signaler.
- **Outcome positif clair** : pour Adult Income, `income == ">50K"` est
  l'outcome favorable (avoir un haut revenu).
- **Direction du biais** :
  - DI < 0.8 → le groupe minoritaire est **désavantagé** (signal habituel)
  - DI > 1.25 → le groupe minoritaire est **avantagé** (rare, à investiguer aussi)

> ⚠️ **Ce que le DI _n'est pas_.** Le DI utilisé ici est un **ratio simple de
> parité statistique** (`SR_min / SR_max`), choisi comme métrique **pédagogique
> M2** — il est **non exhaustif** : il dépend de la distribution globale et ne
> capture pas la variance intra-groupes. En industrie on le complète par la
> **Statistical Parity Difference (SPD)** et la **différence absolue**
> (`SR_max − SR_min`) — cf. M7. Surtout : **le DI est un indicateur de
> _disparité_, pas une preuve de _discrimination_.** Une disparité peut avoir
> des causes légitimes ; établir une discrimination (légale, éthique) demande
> le **contexte métier**, pas un seul ratio.

## Exemple minimal qui tourne

```python
# pandas==2.2.2
import pandas as pd

df = pd.read_csv("data/adult_income_with_comments.csv")

# Fonction réutilisable
def disparate_impact(df, sensible, target="income", positive=">50K"):
    sr = df.groupby(sensible)[target].apply(lambda x: (x == positive).mean())
    di = sr.min() / sr.max()
    return di, sr

# DI sur 3 variables sensibles
results = []
for col in ["sex", "race", "marital_status"]:
    di, sr = disparate_impact(df, col)
    results.append({
        "variable": col,
        "DI": round(di, 3),
        "signal_4/5": "⚠️" if di < 0.8 else "✅",
        "SR_min": round(sr.min(), 3),
        "SR_max": round(sr.max(), 3),
    })
print(pd.DataFrame(results))
```

Sortie typique :

```
        variable     DI signal_4/5  SR_min  SR_max
0            sex  0.358         ⚠️   0.109   0.306
1           race  0.347         ⚠️   0.092   0.266
2 marital_status  0.103         ⚠️   0.046   0.447
```

**Tous** les DI sont largement en dessous de 0.8 sur Adult Income — un dataset
**fortement déséquilibré, corrélé à des inégalités socio-économiques
structurelles** (et c'est pour ça qu'il sert de cas d'école). Attention à la
formulation : ce déséquilibre **n'est pas** une discrimination intentionnelle
ni un « système injuste » démontré — c'est un **recensement brut** (US Census
1994) qui **reflète** des inégalités réelles de l'époque. Les chiffres
ci-dessus sont **exactement** ceux que produit le code sur le dataset généré
(seed 42) — tu dois retrouver les mêmes.

## Intersectionnalité

```python
# Création de la variable composite sex × race
df["sex_race"] = df["sex"].str.cat(df["race"], sep="_")

# Vérification de support (au moins 30 obs par modalité)
print(df["sex_race"].value_counts())
# Male_White                   19174
# Female_White                  8642
# Male_Black                    1569
# Female_Black                  1555
# Male_Asian-Pac-Islander        693
# Female_Asian-Pac-Islander      346
# Male_Amer-Indian-Eskimo        192
# Male_Other                     162
# Female_Amer-Indian-Eskimo      119
# Female_Other                   109   ← petit support, DI fragile à signaler

# DI intersectionnel
di_intersect, sr_intersect = disparate_impact(df, "sex_race")
print(f"DI sex × race = {di_intersect:.3f}")
print(f"\nSelection rate par groupe :")
print(sr_intersect.sort_values())
```

Tu observeras que les femmes noires ont un SR bien plus faible que les
hommes blancs — biais structurel majeur invisible en regardant `sex` et
`race` séparément.

> ⚠️ **Variance extrême à faible support.** Quand un sous-groupe compte peu
> d'observations (ex. `Female_Other`, n ≈ 109), le DI devient **instable** : il
> peut varier fortement selon le seed, le split ou un simple ré-échantillonnage.
> Les DI intersectionnels sont donc à interpréter comme **exploratoires** (« où
> creuser ? »), **pas décisionnels** (« voici le verdict »). On les utilise pour
> orienter l'investigation, jamais pour conclure seuls.

## Exercice guidé

En binôme, calcule :

1. DI sur **3 variables sensibles** : `sex`, `race`, `native_country`
   (agrégé en `USA`/`non-USA` pour simplifier)
2. **1 intersectionnalité** : `sex × race` ou `sex × native_country`
3. Identifie le **DI le plus problématique** et écris 1 phrase
   d'interprétation pour le DPO

**Solution attendue** (verdicts approximatifs sur Adult Income) :

- `sex` : DI ≈ 0.36 → signal majeur (femmes désavantagées)
- `race` : DI ≈ 0.35 → signal majeur (groupes non-blancs désavantagés)
- `native_country` (USA vs non) : DI ≈ 0.80 → **juste au-dessus du seuil 4/5**
  (cas limite — à signaler comme « borderline », pas comme « clean »)
- `sex × race` : DI ≈ 0.16 → **biais intersectionnel critique** (femmes
  *Other* / *Black* SR ≈ 0.05-0.06 vs hommes *White*/*Asian* SR ≈ 0.33)

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Intersectionnalité sans vérifier le support (< 30 obs) | DI fragile, conclusion non fiable |
| Choisir le mauvais "positif" | DI inversé, recommandations à l'envers |
| Comparer DI sur des variables avec sample sizes très différents | Comparaison non significative — toujours signaler le support |
| Réduire `race` en binaire (`White` / `non-White`) sans justifier | Masque des disparités importantes — préfère le multi-modalités |
| Calculer DI sur le **modèle** au lieu du **dataset** | En M2 on audite **les données**, pas un modèle (qui n'existe pas encore) |
| Vouloir mitiger | C'est M7 — en M2 on **alerte** seulement |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| DI = 0 exact sur intersectionnalité | Un groupe a 0 % d'outcome positif (souvent groupe minuscule) — signaler comme "non interprétable" |
| `KeyError` sur la cible | Tu utilises `"<=50K"` vs `">50K"` (Adult ajoute parfois un `.` final) — vérifie `.value_counts()` |
| Tous les DI > 0.8 | Bizarre sur Adult Income — vérifie que tu n'as pas pris `<=50K` comme positif |
| `native_country` brut donne DI ≈ 0 mais USA/non-USA donne DI ≈ 0.80 | Le DI brut est tiré par un micro-pays à 0 % >50K (support minuscule, non fiable) ; la binarisation **agrège** et lisse l'effet. Toujours regarder le support avant de conclure |

## Pour aller plus loin

- **Fairlearn — Disparity metrics** : <https://fairlearn.org/main/user_guide/assessment/common_fairness_metrics.html>
- **Barocas, Hardt, Narayanan — *Fairness and ML*** chapitre 2 : <https://fairmlbook.org/>
  (livre gratuit en ligne, le passage sur l'intersectionnalité est éclairant)
- **CNIL — IA et données personnelles** : <https://www.cnil.fr/fr/intelligence-artificielle/ia-comment-etre-en-conformite-avec-le-rgpd>
- **Crenshaw 1989 — *Demarginalizing the Intersection of Race and Sex*** :
  l'article fondateur du concept d'intersectionnalité (en sociologie, pas en ML)

## Vérification (checklist binôme)

- [ ] DI calculé sur 3 variables sensibles, présentées dans un tableau
- [ ] DI intersectionnel calculé sur au moins 1 croisement
- [ ] Support (n obs) vérifié sur chaque modalité d'intersection
- [ ] Verdict 4/5 explicite pour chaque DI
- [ ] Paragraphe markdown : « Le biais le plus problématique est... » +
      interprétation pour le DPO
- [ ] Pas de tentative de mitigation (c'est M7)