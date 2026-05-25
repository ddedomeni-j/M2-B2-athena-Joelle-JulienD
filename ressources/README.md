# Ressources M2-B2 — Audit éthique + anonymisation Athéna RH

> Brief associé : **M2-B2**.
> Mode : binôme sync mercredi (2h15) + individuel async jeudi/vendredi (6h).
> Le brief lui-même est diffusé sur **Simplonline**.

---

## 📚 Ordre de mobilisation

### Phase sync (mercredi binôme)

| Tâche | Durée | Mini-cours associé |
|---|---|---|
| 0. Setup binôme | 15 min | [`06_Git_binome_essentiel.md`](./06_Git_binome_essentiel.md) |
| 1. Audit éthique complet | 1 h 30 | [`01_Audit_ethique_complet_essentiel.md`](./01_Audit_ethique_complet_essentiel.md) |
| 2. Datasheet binôme | 30 min | [`02_Datasheet_Gebru_complet_essentiel.md`](./02_Datasheet_Gebru_complet_essentiel.md) |

### Phase async (jeudi/vendredi individuel)

| Tâche | Durée | Mini-cours associé |
|---|---|---|
| 3. Exploration PII | 1 h | (manuel — lire des exemples) |
| 4. Mise en place spaCy NER | 1 h | [`03_spaCy_NER_PII_essentiel.md`](./03_spaCy_NER_PII_essentiel.md) |
| 5. Stratégie d'anonymisation | 2 h | [`04_Strategies_anonymisation_essentiel.md`](./04_Strategies_anonymisation_essentiel.md) |
| 6. **Bonus** Presidio | en plus | [`05_Presidio_alternative_essentiel.md`](./05_Presidio_alternative_essentiel.md) |

> 💡 **Tu n'es pas obligé·e de lire les mini-cours en amont.** Chacun est conçu
> pour être consulté **au moment où tu en as besoin**, pendant la tâche
> correspondante. Lecture + exercice guidé en ~15-20 min.

---

## 🎯 Ce qu'on cherche à atteindre

### Phase sync (binôme)

- Un **notebook d'audit éthique** propre, avec DI sur 3+ variables sensibles
  + 1 intersection
- Une **datasheet Gebru** complète, signée duo, 7 sections, 2 pages max
- Un repo binôme avec commits `Co-authored-by:` systématiques

### Phase async (perso)

- Une **fonction `anonymize_comments`** dans `src/anonymize.py`
- Un **notebook d'anonymisation** avec démarche + 5 exemples avant/après
- Un **sample anonymisé** `data/audit_sample_anonymized_<prénom>.csv`
- Une **note de réflexion** `reflexion.md` 1 page max

→ Compétences visées : **C2 — imiter** (renforcement de M2-B1) + **C3 —
adapter** (renforcement de M2-B1).

---

## 🔗 Liens externes

Toutes les URLs externes des mini-cours sont consolidées dans
[`liens_officiels.md`](./liens_officiels.md), vérifiées avant chaque envoi
de brief.

---

## 🆘 Bloqué·e ?

1. Relis le mini-cours correspondant à ta tâche actuelle.
2. **spaCy** : modèle bien téléchargé (`python -m spacy download en_core_web_md`) ?
3. En binôme : si vous êtes 2 à bloquer, **switchez** driver/navigator.
4. Demande sur Discord (`fil-M2-B2`).

**Garde-fou** : pas besoin de coder hors mercredi sync + 6h async.
Si tu finis avant, viens en MP.
