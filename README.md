# M2-B2 — Squelette repo (Athéna RH — audit éthique + anonymisation)

> **Repo template GitHub.** Clique sur **« Use this template »** en haut à
> droite de cette page → **Create a new repository**.
>
> **2 modalités selon la phase** :
> - **Sync mercredi (binôme)** : nomme ton repo `M2-B2-athena-<prénom1>-<prénom2>`
>   sur le compte de l'un de vous deux. L'autre est invité comme collaborateur.
> - **Async jeudi/vendredi (perso)** : **fork** le repo binôme sous
>   `M2-B2-athena-<prénom>` sur ton compte perso. Tu travailles sur la branche
>   `anonymisation/<prénom>`.

---

## 🚀 Démarrage

```bash
# 0. Clone ton repo perso (ou binôme)
git clone git@github.com:<owner>/<repo-name>.git
cd <repo-name>

# 1. Environnement virtuel
python -m venv .venv && source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate                              # Windows

# 2. Dépendances
pip install -r requirements.txt

# 3. Dépose les 2 CSV reçus via Discord (fil-M2-B2) dans data/ :
#    data/adult_income_with_comments.csv  +  data/audit_sample.csv

# 4. Modèle spaCy (~50 Mo — à télécharger une fois)
python -m spacy download en_core_web_md

# 5. Vérification
jupyter notebook notebooks/M2-B2_audit_template.ipynb
```

Si ça démarre sans erreur, ton poste est prêt.

> 📦 Les datasets `adult_income_with_comments.csv` (~32 561 lignes) et
> `audit_sample.csv` (200 lignes) sont **fournis par la formatrice via
> Discord** (`fil-M2-B2`) mercredi 9h — tout le monde reçoit le **même** jeu
> (graine fixe), indispensable pour comparer les disparate impacts en
> restitution. Ils sont git-ignorés : on ne commite pas la donnée.
>
> ⚠️ **Corpus bilingue volontaire** : ~88 % des commentaires sont en anglais,
> ~12 % en français. Le modèle `en_core_web_md` attrapera bien les noms
> anglais et **ratera une partie des noms français** : c'est un piège réaliste.
> Tu le **documentes** comme une limite de ta détection (à compléter par regex
> ou à signaler) — tu ne changes pas de modèle à chaque commentaire.

---

## 📁 Structure du repo

### Phase sync (binôme)

```
M2-B2-athena-<prénom1>-<prénom2>/
├── data/                                         # gitignored
│   ├── adult_income_with_comments.csv            # fourni via Discord
│   └── audit_sample.csv                          # fourni via Discord
├── notebooks/
│   └── M2-B2_audit_template.ipynb                # → audit_<prénom1>_<prénom2>.ipynb
├── datasheet.md                                  # à compléter en binôme (signature duo)
├── README.md                                     # à compléter
├── ressources/                                   # 📚 mini-cours d'appui
│   ├── README.md
│   ├── 01_Audit_ethique_complet_essentiel.md
│   ├── 02_Datasheet_Gebru_complet_essentiel.md
│   ├── 03_spaCy_NER_PII_essentiel.md
│   ├── 04_Strategies_anonymisation_essentiel.md
│   ├── 05_Presidio_alternative_essentiel.md
│   ├── 06_Git_binome_essentiel.md
│   └── liens_officiels.md
├── requirements.txt
└── .gitignore
```

### Phase async (perso, fork du repo binôme)

```
M2-B2-athena-<prénom>/
├── (tout ce qui précède, héritage du binôme)
├── src/
│   └── anonymize.py                              # à compléter — fonction perso
├── data/
│   └── audit_sample_anonymized_<prénom>.csv      # produit perso
├── notebooks/
│   └── M2-B2_anonymisation_<prénom>.ipynb        # livrable perso
└── reflexion.md                                  # max 1 page perso
```

---

## 📚 Mini-cours d'appui

Les **6 mini-cours pédagogiques** sont fournis dans
[`./ressources/`](./ressources/). Lecture juste-à-temps :

| Tâche | Mini-cours |
|---|---|
| Audit éthique complet (DI + intersectionnalité) | [`01_Audit_ethique_complet_essentiel.md`](./ressources/01_Audit_ethique_complet_essentiel.md) |
| Datasheet Gebru — version étoffée | [`02_Datasheet_Gebru_complet_essentiel.md`](./ressources/02_Datasheet_Gebru_complet_essentiel.md) |
| spaCy NER pour la détection PII | [`03_spaCy_NER_PII_essentiel.md`](./ressources/03_spaCy_NER_PII_essentiel.md) |
| Stratégies d'anonymisation (4 options) | [`04_Strategies_anonymisation_essentiel.md`](./ressources/04_Strategies_anonymisation_essentiel.md) |
| Microsoft Presidio (bonus) | [`05_Presidio_alternative_essentiel.md`](./ressources/05_Presidio_alternative_essentiel.md) |
| Git en binôme (branches + Co-authored-by) | [`06_Git_binome_essentiel.md`](./ressources/06_Git_binome_essentiel.md) |

Cf. [`./ressources/README.md`](./ressources/README.md) pour l'ordre de mobilisation.

---

## 🧭 Démarche attendue

### Mercredi sync (2h15) — binôme

1. **Setup binôme** (15 min) — choix du binôme, repo commun, conventions
   `Co-authored-by:`, switch driver/navigator
2. **Audit éthique complet** (1h30) — DI sur ≥ 3 variables sensibles + intersection
3. **Datasheet binôme** (30 min) — 7 sections Gebru, signée duo
4. **Tour de table 11h30** — restitution duo 5 min × 4 paires

### Async jeudi/vendredi matin (6h) — individuel

5. **Fork du repo binôme** (15 min)
6. **Exploration PII** (1h)
7. **Mise en place spaCy NER** (1h) — vérification qualitative sur ~10 exemples
8. **Stratégie d'anonymisation** (2h) — tu défends ton choix dans `reflexion.md`
9. **Production livrables perso** (1h45)

→ Compétences visées : **C2 — imiter (renforcement)** + **C3 — adapter (renforcement)**.

---

## ✅ Conventions de code

- Python 3.11+
- Type hints sur toutes les signatures publiques
- Pas de `print` (utiliser `display()`)
- `pathlib.Path` pour les chemins
- En **binôme** : commits avec `Co-authored-by: <prénom> <email>` pour le
  partenaire qui n'est pas au clavier

---

## 🆘 Bloqué·e ?

1. Relis le mini-cours concerné (cf. [`./ressources/README.md`](./ressources/README.md)).
2. Si **spaCy** plante au chargement du modèle : as-tu fait
   `python -m spacy download en_core_web_md` ? (~50 Mo)
3. La **détection NER rate des noms français** (~12 % du corpus) : c'est
   attendu avec `en_core_web_md`. Complète par regex, ou charge en plus
   `fr_core_news_md` sur les commentaires détectés comme français — mais
   surtout **documente cette limite** dans ta `reflexion.md`.
4. En binôme : si vous bloquez à 2, **switchez** driver/navigator —
   souvent ça débloque.
5. Demande en direct mercredi sur Discord — `fil-M2-B2`.