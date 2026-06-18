# Note de réflexion — Stratégie d'anonymisation (perso)

> Template à remplir en phase async individuelle (jeudi/vendredi matin).
> **Max 1 page.** Personnel — chaque apprenant rédige la sienne.
> Public : Marianne (évaluation) + futur toi qui relit ce repo.

---

## Ma stratégie d'anonymisation

- Traitement de "PERSON": généralisation pour essayer de garder le rôle de la personne (Manager, Employé, RH)
- Traitement des "EMAIL": substitution par un placeholder : on ne souhaite pas garder de traçabilité de cette information
- Traitement de "GPE " ou "LOC": substitution par un placeholder : on ne souhaite pas garder de traçabilité de cette information
- Traitement de "ORG": on ne touche pas aux organisations pour l'instant
- Traitement des "DATE" et "TIME": généralisation pour essayer de garder l'année (YEAR XXXX)
- Traitement des numéros de compte et IBAN : substitution par un placeholder : on ne souhaite pas garder de traçabilité de cette information
- Traitement des numéros de téléphone : substitution par un placeholder : on ne souhaite pas garder de traçabilité de cette information
- J'ai appliqué l'expression régulière avant spaCy pour enlever les risques de fausses détection sur des expressions connues

...

## Ce que j'ai gardé lisible et pourquoi

- ORG : c'est un fichier RH interne l'organisation a un faible risque de réidentification

## Ce que j'ai masqué et pourquoi

Les entités susceptibles d’identifier directement ou indirectement une personne ont été systématiquement substituées ou généralisées.

Cela inclut les noms de personnes (`PERSON`), les adresses email (`EMAIL`), les numéros de téléphone (`PHONE`), ainsi que les identifiants financiers comme les comptes bancaires ou IBAN (`ACCOUNT`, `IBAN`). Ces informations sont fortement identifiantes et leur présence expose à un risque élevé de réidentification.

Les entités géographiques (`GPE`, `LOC`) ont également été masquées, car un lieu précis peut contribuer à identifier une personne lorsqu’il est combiné avec d’autres informations. 

Les informations temporelles (`DATE`, `TIME`) ont été supprimées ou généralisées, car des dates précises peuvent permettre de retracer des événements.

## Trade-offs assumés

Le compromis a été orienté en priorité vers la protection de la vie privée, tout en conservant un minimum de lisibilité permettant de comprendre le contexte métier.

D’un point de vue RGPD, j’ai appliqué un principe de minimisation des données en supprimant ou en généralisant toutes les informations directement ou indirectement identifiantes.

Du point de vue métier, j’ai cherché à préserver une certaine intelligibilité du texte en conservant la structure des phrases ainsi que des informations contextuelles non sensibles, comme les rôles (ex. `[MANAGER]`, `[EMPLOYEE]`) ou les organisations (`ORG`).

...

## Cadre réglementaire — RGPD + AI Act

> Deux textes, deux angles : positionne tes choix face aux **deux**.

- **RGPD** (données personnelles) : minimisation, finalité, droit à l'effacement.
Mon anonymisation y répond par la suppression ou la généralisation systématique des données directement identifiantes (noms, emails, téléphones, identifiants bancaires), conformément au principe de minimisation des données.  

- **AI Act** (règlement UE 2024, risque classé par usage) : un système qui exploite
  des **commentaires RH** pour évaluer des personnes relève potentiellement du
  **« haut risque »** (emploi / gestion des travailleurs = Annexe III) → exigences
  renforcées de **qualité des données, traçabilité et supervision humaine**. 
  
  L’utilisation de commentaires RH pour évaluer des personnes relève potentiellement des systèmes à haut risque (gestion des travailleurs), ce qui implique des exigences renforcées en matière de qualité des données, de traçabilité et de supervision humaine.

  - **Qualité des données** :
    L’identification et la quantification des PII (noms, emails, identifiants, etc.) permettent de mieux comprendre la nature des données utilisées et d’identifier les sources potentielles de biais ou de fuite d’information. L’anonymisation réduit le bruit lié aux données personnelles non pertinentes pour l’évaluation

  - **Réduction des biais et risques** :
    En supprimant les informations directement identifiantes, le système est moins susceptible d’introduire des biais liés à l’identité des individus (nom, origine géographique, etc.), ce qui contribue à une utilisation plus équitable et conforme aux exigences du cadre "haut risque".

  - **Traçabilité** :
    L’approche par règles explicites (spaCy + regex + transformation en tags) permet de documenter précisément les transformations appliquées aux données. Chaque type de PII est traité de manière transparente et reproductible, ce qui facilite l’audit du système.

  - **Supervision humaine** :
    La comparaison avec une anonymisation manuelle (jeu de référence) permet d’évaluer la performance du système (recall, précision) et d’identifier ses limites. Cela s’inscrit dans une logique de contrôle humain et d’amélioration continue, conformément aux exigences de supervision humaine du AI Act.

## Limites de ma stratégie

L'analyse faite sur les 20 premières lignes du fichier d'audit produit les résultats suivants :

| label     | manual_expected | auto_detected | true_positive | false_positive | false_negative | recall_detection_ratio | precision | f1_score |
|-----------|----------------|---------------|----------------|----------------|----------------|------------------------|-----------|----------|
| EMPLOYEE  | 21             | 11            | 11             | 0              | 10             | 0.52381                | 1.0       | 0.687500 |
| MANAGER   | 10             | 9             | 9              | 0              | 1              | 0.90000                | 1.0       | 0.947368 |
| EMAIL     | 9              | 9             | 9              | 0              | 0              | 1.00000                | 1.0       | 1.000000 |
| PERSON    | 8              | 20            | 8              | 12             | 0              | 1.00000                | 0.4       | 0.571429 |
| YEAR      | 6              | 6             | 6              | 0              | 0              | 1.00000                | 1.0       | 1.000000 |
| PHONE     | 5              | 5             | 5              | 0              | 0              | 1.00000                | 1.0       | 1.000000 |
| ACCOUNT   | 4              | 4             | 4              | 0              | 0              | 1.00000                | 1.0       | 1.000000 |
| DATE      | 0              | 3             | 0              | 3              | 0              | NaN                    | 0.0       | NaN      |
| HR        | 0              | 2             | 0              | 2              | 0              | NaN                    | 0.0       | NaN      |
| ORG       | 0              | 0             | 0              | 0              | 0              | NaN                    | NaN       | NaN      |
| LOCATION  | 0              | 0             | 0              | 0              | 0              | NaN                    | NaN       | NaN      |
| IBAN      | 0              | 0             | 0              | 0              | 0              | NaN                    | NaN       | NaN      |
``
1. Mon test n'est pas exhaustifs car IBAN, LOCATION, ORG, HR ne sont pas dans le jeu de test.
2. la généralisation des personnes en rôles métier ne fonctionne pas à 100 %. Le label `EMPLOYEE` présente un rappel de 52,4 % : seulement 11 occurrences sur 21 attendues sont correctement détectées. La généralisation à `[EMPLOYEE]` est moins bonne que pour `MANAGER` qui a un recall de 90 %. Beaucoup d'`[EMPLOYEE]` sont détectés en tant que `[PERSON]`
3. `DATE` est détecté 3 fois alors qu’il n’était pas attendu dans la transcription manuelle, et `HR` est détecté 2 fois alors qu’il n’était pas annoté comme entité à masquer. Certaines sorties de spaCy sont incorrectes


## Si je devais industrialiser

### 1. Amélioration de la qualité et de la couverture
- Enrichir les règles de détection (regex + spaCy) pour améliorer la précision et le recall des catégories mal reconnues.
- Envisager l'utilisation d'un LLM si on veut conserver la généralisation des personnes en rôles

### 2. Évaluation systématique et monitoring
- Mettre en place un jeu de test automatisé plus large et représentatif.
- Mesurer des métriques continues (recall, précision, F1) en production.

### 3. Traçabilité et auditabilité
- Logger les transformations appliquées (quelle règle a déclenché quel remplacement).
- Versionner le pipeline d'anonymisation.
- Fournir des rapports d’audit réguliers.

### 4. Supervision humaine
- Intégrer une validation humaine sur un échantillon régulier.

---
//
/Note rédigée par JulienD, 18/06/2026, dans le cadre du brief M2-B2 ATOS.