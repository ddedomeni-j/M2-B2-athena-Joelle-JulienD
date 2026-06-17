# Datasheet — Adult Income enrichi (Athéna RH v1.0.0)

> Document accompagnant le dataset livré à Athéna RH.
> **Modèle Gebru et al. (2018), 7 sections, 2 pages max.**
> Signée binôme.

**Auteurs** : Joelle, Julien D
**Date** : <date>
**Version** : v1.0.0

## 1. Motivation

> Pourquoi ce dataset existe ? Qui l'a créé ?

- Ce dataset a été créé par Ron Kohavi pour étudier les relations entre le revenu (2 tranches : "> 50K" et "< 50K") et les données issues du recensement de la population.

## 2. Composition

> Combien d'observations, quelles colonnes, types, distribution cible,
> **variables sensibles signalées explicitement**, + le résumé du
> verdict éthique (DI les plus problématiques).

| Aspect | Valeur |
|---|---|
| Nombre de lignes | 200 observations |
| Nombre de colonnes | 16 (14 features UCI + cible `income` + `manager_comments` synthétique) |
| Cible | `income` : `<=50K` / `>50K` |
| Distribution cible | (75.9% `<=50K` / 24.1% `>50K`) |
| Variables sensibles | `sex`, `race`, `native_country`, `marital_status` |

**Schéma des colonnes** :

| Colonne | Type | Note |
|---|---|---|
| `age` | int | 17 — 90 |
| `workclass` | str | Statut de travail (9 modalités) |
| `education` | str | Diplôme (16 modalités) |
| `marital_status` | str | ⚠️ Sensible |
| `occupation` | str | Profession (15 modalités) |
| `relationship` | str | Position familiale (6 modalités) |
| `race` | str | ⚠️ Sensible (5 modalités) |
| `sex` | str | ⚠️ Sensible binaire |
| `capital_gain` / `capital_loss` | int | Très asymétriques (médiane 0) |
| `hours_per_week` | int | 1 — 99 |
| `native_country` | str | ⚠️ Sensible (40+ modalités) |
| `income` (cible) | str | `<=50K`, `>50K` |
| `manager_comments` | str | Texte libre **avec PII** — à anonymiser en async |

**Résumé verdict éthique** :
- DI le plus problématique : Le Disparate Impact (DI) s'effondre à un score critique de 0,1823 sur la variable intersectionnelle composite sex_race
- Intersectionnalités notables : L'analyse croisée révèle un effet "double peine" majeur pour le groupe des femmes noires (Female_Black). Ce sous-groupe affiche le taux de sélection positive le plus faible du dataset avec seulement 5,79%, tandis que le groupe le plus favorisé — les hommes blancs (Male_White) — culmine à $31,76%


## 3. Processus de collecte

> Origine UCI Adult Census 1994 + enrichissement Athéna RH 2026.

- **Origine des données :** Le jeu de données est une création hybride. Le socle tabulaire provient du dataset public de référence *UCI Adult Census (1994)*. Ce socle a été croisé, augmenté et mis en contexte pour les besoins d'Athéna RH par l'injection d'une couche de données textuelles non structurées `manager_comments`.

## 4. Preprocessing appliqué

> Ce que **votre binôme** a fait dans la phase sync.

- * **Création d'une Feature Intersectionnelle (`sex_race`) :** Afin de rendre visibles les discriminations cumulatives, nous avons fusionné les variables catégorielles `sex` et `race` en une feature unique appelée `sex_race`(pour mettre en évidence l'effondrement éthique du sous-groupe des femmes noires (`Female_Black`)).
  
- * **Généralisation et Regroupement Géographique (`native_country`) :** regroupement stratégique binaire en reformatant cette colonne sous la modalité `USA / Non-USA`. Ce preprocessing a permis de remonter artificiellement le ratio de Disparate Impact (DI) à **0,804** , au prix d'une perte volontaire de granularité sur les pays d'origine non-américains.



## 5. Usages prévus / à éviter

**Usages prévus** :
- * **Entraînement de pipelines d'anonymisation :** Utilisation comme jeu de test pour mesurer le taux de rappel d'algorithmes de dé-identification automatisés face à des fuites de données personnelles complexes (PII textuelles).

**Usages à éviter** :
- * **Exploitation de la colonne textuelle en texte brut :** Il est formellement interdit d'intégrer la colonne `manager_comments` dans un outil d'analyse ou de reporting accessible à des tiers sans avoir exécuté au préalable le pipeline d'anonymisation. Le fichier contient des PII non masquées (e-mails, numéros de comptes) qui violent directement le secret professionnel et le RGPD.

## 6. Distribution

- Destinataire : Athéna RH (Laurence Béthencourt, DPO)
- Format : Parquet snappy (chiffrement par colonne pour isoler les données personnelles PII)
- Conditions : Le fichier doit être déposé sur les serveurs sécurisés d'Athéna RH et rattaché exclusivement au groupe d'utilisateurs habilités.

## 7. Maintenance

- Mainteneur·euses : Joelle, Julien D
- Version : v1.0.0 — 17/06/2026
- Signaler un problème : Ouverture d'un ticket Jira interne avec le tag `[ETHICS-ALERT]`

---

*Datasheet produite en binôme dans le cadre du brief M2-B2 ATOS.*