# Datasheet — Adult Income enrichi (Athéna RH v1.0.0)

> Document accompagnant le dataset livré à Athéna RH.
> **Modèle Gebru et al. (2018), 7 sections, 2 pages max.**
> Signée binôme.

**Auteurs** : <Joelle>, <Julien D>
**Date** : <17/06/2026>
**Version** : v1.0.0

## 1. Motivation

Ce dataset a été créé par Ron Kohavi pour étudier les relations entre le revenu (2 tranches : "> 50K" et "< 50K") et les données issues du recensement de la population.
Il est complété par un enrichissement d'Athéna RH ajoutant des commentaires manager dans le but d'analyser et de modéliser le positionnement des collaborateurs en foinction de leurs caractéristiques.

## 2. Composition

> Combien d'observations, quelles colonnes, types, distribution cible,
> **variables sensibles signalées explicitement**, + le résumé du
> verdict éthique (DI les plus problématiques).

Ce dataset présente 14 variables explicatives décrivant les caractéristiques socio-démographiques des individus, une variable commentaire et la variable "revenu" (<=50K ou >50K). Elle comporte 32261 observations.

variables numériques :
- age, fnlwgt, education_num, capital_gain, capital_loss, hours_per_week

variables catégorielles nominale :
- workclass, education, marital_status, occupation, relationship, race, sex, native_country

variable cible :
- income

Pas de variable catégorielle ordinales

---------

| Aspect | Valeur |
|---|---|
| Nombre de lignes | 32261 |
| Nombre de colonnes | 16 (14 features UCI + cible `income` + `manager_comments` synthétique) |
| Cible | `income` : `<=50K` / `>50K` |
| Distribution cible | déséquilibrée (75.9% `<=50K` / 24.1% `>50K`) |
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
- L'analyse du disparate impact de la variable "sex" pour l'accès à un revenu > à 50K, montre un ratio de 0.35 pour le groupe des femmes, qui est très inférieur au seuil d'alerte
- L'analyse du disparate impact de la variable "race" pour l'accès à un revenu > à 50K, montre un ratio de 0.48 pour le groupe des "femmes", également très inférieur au seuil d'alerte
- L’analyse intersectionnelle croisant race et sex met en évidence une disparité beaucoup plus marquée que les analyses réalisées séparément sur chaque variable. Le sous-groupe le plus défavorisé présente un disparate impact de 0.16 pour l’accès à l’issue favorable income >50K.

## 3. Processus de collecte

> Origine UCI Adult Census 1994 + enrichissement Athéna RH 2026.

- **Origine des données :** Le jeu de données est une création hybride. Le socle tabulaire provient du dataset public de référence *UCI Adult Census (1994)*. Ce socle a été croisé, augmenté et mis en contexte pour les besoins d'Athéna RH par l'injection d'une couche de données textuelles non structurées `manager_comments`.

## 4. Preprocessing appliqué

Nous proposons le prétraitement suivant
- exclusion des features sensibles "marital_status", "relationship", "race", "sex" et "native_country"
- exclusion des variables "fnlwgt", "capital_gain" et "capital_loss" qui ne présentent pas d'intérêt métier pour le modèle recherché  
- exclusion de la variable "education" dont les caractéristiques sont communes avec la variable "education_num"
- compléter les manquants par la valeur la plus fréquente pour les features "occupation" et "workclass"
- les variables numériques seront reportées et normalisées
- les variables catégorielles seront encodées via one hot encoding
- Anonymisation de la variable comment_manager

## 5. Usages prévus / à éviter

**Usages prévus** :
- Le dataset peut être utilisé pour entraîner et comparer des modèles de classification, ainsi que pour analyser les biais et évaluer l’équité des algorithmes sur des données socio-démographiques

**Usages à éviter** :
- Le dataset ne doit pas être utilisé pour des prises de décisions individuelles automatisées sans suppression des features présentant des biais pouvant conduire un modèle à reproduire ces biais
- Exploitation de la colonne textuelle en texte brut : il est formellement interdit d'intégrer la colonne `manager_comments` dans un outil d'analyse ou de reporting accessible à des tiers sans avoir exécuté au préalable le pipeline d'anonymisation. Le fichier contient des PII non masquées (e-mails, numéros de comptes) qui violent directement le secret professionnel et le RGPD.

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