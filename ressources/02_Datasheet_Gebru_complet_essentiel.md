# Datasheet Gebru — version étoffée — Mini-cours

> Brief associé : M2-B2
> Durée de lecture + pratique : ~20 min
> Pré-requis : avoir vu le mini-cours datasheet M2-B1 (`05_Datasheet_Gebru_essentiel.md`).

## Pourquoi cette techno ?

En M2-B1 tu as fait une **datasheet d'audit interne** (German Credit), 1 page,
focus sur les choix techniques.

En M2-B2 tu la fais **en binôme** pour un dataset RH **plus sensible** :
le `manager_comments` contient des **PII non maîtrisées**, le DPO Athéna RH
en attend une lecture **stratégique** pour décider du go/no-go production.

Donc même structure (7 sections Gebru), mais :
- **2 pages max** au lieu d'1 (cas plus complexe)
- **Section 2 — Composition** : signaler **explicitement** le risque PII de
  `manager_comments` + résumé du verdict éthique (DI principaux)
- **Section 5 — Usages à éviter** : plus détaillée — quels usages déclencheraient
  une violation RGPD ?
- **Signature duo** : « Auteurs : <prénom1>, <prénom2> » en haut

**Différence clé vs M2-B1** :

| Aspect | M2-B1 (Eckmühl) | M2-B2 (Athéna) |
|---|---|---|
| Format | 1 page | 2 pages max |
| Auteur | Solo | Binôme signé |
| Sensibilité principale | Variables sensibles tabulaires | **PII textuelles** + variables sensibles tabulaires |
| Verdict éthique | Inclus dans audit.md séparé | Résumé dans Composition |
| Public | DPO Eckmühl (1 interlocuteur) | DPO Athéna + équipe légale RH |

## Concepts clés

- **Signature binôme** : tous les commits significatifs en
  `Co-authored-by: <prénom> <email>`. Mention « Auteurs : <prénom1>,
  <prénom2> » en première ligne de la datasheet.
- **Section 2 enrichie** : tableau de schéma + signalement explicite des
  PII textuelles dans `manager_comments` + résumé chiffré du verdict
  éthique (DI principaux).
- **Section 5 enrichie** : 3-5 usages à éviter spécifiques au contexte RH
  (ex. décisions de licenciement automatisées, scoring de performance
  individuel sans HITL).
- **Versioning** : v1.0.0-duo en sortie de M2-B2. Si tu refais en M7
  (audit complet), tu passes en v2.0.0.

## Structure complète (les 7 sections)

### 1. Motivation
Dataset Adult Income (UCI 1994) + enrichissement Athéna RH 2026 avec
`manager_comments`. Pourquoi ce dataset existe dans le contexte Athéna ?
À quel besoin métier répond-il ?

### 2. Composition (la plus dense en M2-B2)
- Nombre de lignes, colonnes, types
- Distribution cible
- **Schéma des colonnes** (tableau condensé)
- **Variables sensibles signalées** : `sex`, `race`, `native_country`,
  `marital_status`
- **Risque PII textuel** : `manager_comments` contient noms, emails,
  téléphones, IBAN partiels
- **Résumé verdict éthique** : 2-3 DI les plus problématiques avec chiffres

### 3. Processus de collecte
Adult UCI Census Bureau 1994. Enrichissement Athéna : commentaires manager
synthétiques (Faker, 10 templates). **Pas de personnes réelles** dans les
PII (Faker), mais l'apprenant **ne sait pas ça** au démarrage du brief —
l'audit doit traiter le dataset comme si les PII étaient réelles.

### 4. Preprocessing appliqué
Choix de **votre binôme**. Concis.

### 5. Usages prévus / à éviter
- **Prévus** : audit éthique, base de test pour pipeline d'anonymisation
- **À éviter** :
  - Décisions individuelles automatisées (licenciement, promotion, salaire)
  - Profilage individuel sans HITL (RGPD art. 22)
  - Réutilisation des PII même après anonymisation pour d'autres finalités
  - Partage hors équipe RH Athéna

### 6. Distribution
Format, destinataire, conditions, contraintes RGPD.

### 7. Maintenance
Auteurs binôme + version + date + canal de signalement de problème.

## Exemple minimal (extrait section 2)

```markdown
## 2. Composition

**Volume** : 32 561 lignes × 16 colonnes (14 features Adult + `income` + `manager_comments`)
**Distribution cible** : 76 % `<=50K` / 24 % `>50K`

| Colonne | Type | Note |
|---|---|---|
| `age` | int | 17-90 |
| `sex` | str | ⚠️ Sensible binaire |
| `race` | str | ⚠️ Sensible (5 modalités) |
| `marital_status` | str | ⚠️ Sensible |
| `native_country` | str | ⚠️ Sensible (40+ modalités) |
| `manager_comments` | str | ⚠️ **Texte libre avec PII** : noms, emails, téléphones, IBAN partiels |
| ... | | |

**Résumé verdict éthique** (cf. notebook audit) :
- DI `sex` : 0.36 → biais majeur (femmes désavantagées)
- DI `race` : 0.35 → biais majeur (groupes non-blancs désavantagés)
- DI intersectionnel `sex × race` : 0.16 → **biais structurel critique**
- Risque PII : 100 % des `manager_comments` contiennent au moins 1 PII
```

## Exercice guidé

En binôme, complétez **la section 2 (Composition)** de la datasheet Athéna à
partir des résultats de votre notebook d'audit :

1. Listez les colonnes et leur type (numérique / catégorielle / texte libre).
2. Marquez explicitement les **variables sensibles** (`sex`, `race`,
   `marital_status`, `native_country`) et la colonne à PII (`manager_comments`).
3. Reportez le **résumé verdict éthique chiffré** (les 3 DI + l'intersection)
   calculés dans votre notebook — pas des valeurs approximatives.
4. Ajoutez une phrase « Usages à éviter » spécifique au contexte RH.

**Attendu** : une section *Composition* qu'un DPO non-technicien comprend en
2 minutes, avec les chiffres exacts de votre audit (et non recopiés du
mini-cours).

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Datasheet rédigée par 1 seul du binôme | CT6 ratée, restitution duo bancale |
| Section *Usages à éviter* trop générique | DPO décroche — sois spécifique au contexte RH |
| Oublier de signaler la PII de `manager_comments` | **Faute grave** — c'est le risque #1 du dataset |
| Datasheet de 4 pages | Trop verbeux — vise 2 pages dense, pas 4 vagues |
| Pas de version + date | Impossible de tracer |
| Sections rédigées dans le désordre par les 2 membres sans relire | Incohérences (chiffres divergents entre sections) |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| Le DPO te demande "et les emails dans les commentaires ?" | Section 2 ne signale pas la PII textuelle |
| Le DPO te demande "vous avez fait l'anonymisation ?" | Section 4 ne mentionne pas que l'anonymisation est en async perso, pas en sync binôme |
| Tu n'arrives pas à signer en binôme | Forgot `Co-authored-by:` dans les commits — ajoute un commit final qui ré-acte la co-paternité |
| Datasheet de 5 pages | Trop de détails dans Composition — déplace le tableau de schéma en annexe ou retire les lignes redondantes |

## Pour aller plus loin

- **Hugging Face — Dataset cards** : <https://huggingface.co/docs/datasets/dataset_card>
- **Microsoft — Datasheets for Datasets template** : <https://www.microsoft.com/en-us/research/uploads/prod/2019/01/1803.09010.pdf>
- **CNIL — Documentation RGPD données RH** : <https://www.cnil.fr/fr/la-gestion-des-ressources-humaines>

## Vérification (checklist binôme)

- [ ] Les 7 sections Gebru sont présentes
- [ ] La datasheet tient en 2 pages markdown rendues
- [ ] La section 2 signale **explicitement** la PII de `manager_comments`
- [ ] Le résumé du verdict éthique chiffré est dans la section 2
- [ ] La section 5 donne ≥ 3 usages à éviter spécifiques RH
- [ ] La datasheet est signée « Auteurs : <prénom1>, <prénom2> »
- [ ] Les commits sont `Co-authored-by:` quand pertinent
- [ ] Lisible par un DPO non-technicien (Laurence Béthencourt)