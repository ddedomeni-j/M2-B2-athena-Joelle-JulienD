# Note de réflexion — Stratégie d'anonymisation (perso)

> Template à remplir en phase async individuelle (jeudi/vendredi matin).
> **Max 1 page.** Personnel — chaque apprenant rédige la sienne.
> Public : Marianne (évaluation) + futur toi qui relit ce repo.

---

## Ma stratégie d'anonymisation

> Quelle stratégie ai-je choisie ? Suppression / substitution /
> généralisation / hash / mix ?

J’ai opté pour une stratégie hybride combinant la substitution contextuelle séquentielle, orchestrée par le moteur industriel Microsoft Presidio. 

Contrairement à une simple suppression qui détruit la structure grammaticale et rend le texte inutilisable pour des modèles NLP en aval, la substitution remplace les entités critiques détectées (noms, e-mails, téléphones, IBAN) par des balises typées anonymes. 
Pour les noms propres, la logique applique un index chronologique incrémental (`[INDIVIDU_1]`, `[INDIVIDU_2]`) de gauche à droite au sein de chaque commentaire, garantissant la traçabilité des interactions (qui parle de qui) sans compromettre l'anonymat.

## Ce que j'ai gardé lisible et pourquoi

> Quelles informations laisse-t-on dans le texte (et pourquoi c'est OK) ?

- **Le contexte métier et managérial :** Les verbes d'action, les qualificatifs de performance, les termes liés aux processus RH (ex: "Primes", "Manager") et le jargon de l'entreprise (ex: "RAS").
- **La syntaxe et la langue d'origine :** Les structures de phrases en français et en anglais sont préservées.

Conserver ce contexte est indispensable pour la finalité du traitement (l'audit de la qualité des commentaires de performance). Sans cela, il serait impossible d'identifier des biais d'évaluation, des discriminations ou des violations des postures managériales. Ces données textuelles ne permettent pas, à elles seules, de réidentifier une personne physique de manière directe.


## Ce que j'ai masqué et pourquoi

> Quelles informations ai-je remplacées et avec quelle logique ?

J'ai ciblé et masqué systématiquement les données à fort pouvoir identifiant (Direct & Indirect) :
- **PERSON (`[INDIVIDU_X]`) :** Noms et prénoms des collaborateurs, managers et tiers.
- **EMAIL_ADDRESS (`[EMAIL]`) & PHONE_NUMBER (`[PHONE]`) :** Coordonnées de contact direct souvent insérées dans les notes de suivi.
- **IBAN / Données financières (`[IBAN]`) :** Masquage des structures bancaires et des masques textuels techniques de type `****1234` via une surcouche Regex, car ces données n'ont aucune valeur ajoutée pour un audit RH et présentent un risque critique en cas de fuite.

- (optionnel) **Numéro ticket RH**: non critique mais pourrai etre aussi masqué pour des raisons de sécurité

## Trade-offs assumés

> Lisibilité du texte vs protection vie privée. Où ai-je placé le curseur,
> et pour quelles raisons (RGPD, métier, robustesse) ?

Le curseur a été délibérément placé en faveur d'une **haute protection de la vie privée (Sécurité)** sans pour autant sacrifier l'utilité analytique du texte :
- **Métier vs RGPD :** En indexant séquentiellement les individus (`[INDIVIDU_1]` a signalé `[INDIVIDU_2]`), le modèle conserve la sémantique de la relation hiérarchique ou conflictuelle, ce qui répond à l'exigence métier, tout en éliminant la donnée nominative exigée par le RGPD.

## Cadre réglementaire — RGPD + AI Act

> Deux textes, deux angles : positionne tes choix face aux **deux**.

- **RGPD** (données personnelles) : minimisation, finalité, droit à l'effacement.
  Mon anonymisation y répond par : ...
- **AI Act** (règlement UE 2024, risque classé par usage) : un système qui exploite
  des **commentaires RH** pour évaluer des personnes relève potentiellement du
  **« haut risque »** (emploi / gestion des travailleurs = Annexe III) → exigences
  renforcées de **qualité des données, traçabilité et supervision humaine**. En quoi
  mon audit + mon anonymisation y contribuent : ...


- RGPD (Données Personnelles)
Mon pipeline répond strictement aux trois principes fondamentaux :
1.  **Minimisation :** Seul le texte nécessaire à l'analyse managériale est conservé ; toutes les variables techniques d'identification directe sont purgées.
2.  **Finalité :** Le traitement restrictif garantit que l'évaluation RH ne puisse plus être détournée pour flouter ou cibler un individu précis.
3.  **Sécurité par défaut (Privacy by Design) :** L'export final est converti en format **Parquet via PyArrow**, figeant les types, optimisant le stockage (réduction de 43 Ko à 20 Ko par dictionnaire binaire) et empêchant toute fuite de texte brut liée à de mauvais échappements de caractères (sauts de ligne).

- AI Act (Règlement UE 2024)
Les systèmes d’IA exploitant des commentaires RH à des fins d'évaluation ou de gestion des travailleurs entrent dans la catégorie **« Haut Risque » (Annexe III)**. Mon approche d'audit et d'anonymisation y contribue directement :
* **Qualité des données et réduction des biais :** En nettoyant les PII, on force les futurs modèles d'IA à s'entraîner sur des faits professionnels et non sur des caractéristiques nominatives ou de genre sous-jacentes.
* **Supervision humaine et Traçabilité :** Le rapport d'audit documente précisément ce que l'algorithme voit et masque, fournissant la documentation technique obligatoire exigée par l'AI Act pour la conformité des systèmes à haut risque.


## Limites de ma stratégie

> Qu'est-ce que ma fonction `anonymize_comments` rate ? Quels faux positifs
> ou faux négatifs ai-je observés sur l'échantillon ?

L'analyse technique des résultats sur notre échantillon de test met en évidence les limites inhérentes aux modèles de reconnaissance d'entités nommées (NER) de spaCy face aux spécificités de la langue française :

### Faux positifs (Texte normal masqué à tort)
* **Mutilation du vocabulaire français (Modèle linguistique) :** Lors des phases de confusion linguistique (où le moteur applique des patterns anglais sur du texte français), des participes passés et des adjectifs français indispensables au sens métier ont été catégorisés à tort comme des personnes (`PERSON`). C'est le cas pour les mots **"comportementale"**, **"signalée"** (Commentaire #9) et **"versée"** (Commentaire #10), qui ont été transformés en `[INDIVIDU]`.
* **Acronymes et contextes techniques :** Le sigle métier **"RAS"** (*Rien À Signaler*) a été faussement interprété comme une entité juridique et converti en `[ORGANISATION]` (Commentaire #13). De même, une structure d'adresse e-mail brute (`william00@example.org`) a été interceptée par spaCy comme une `[ORGANISATION]` avant même l'application des règles de nettoyage (Commentaire #14).

### Faux négatifs (PII non détectées)
* **Échec sur les noms de famille composés et à particule :** Le modèle NER de base peine à cartographier la structure des noms de famille complexes en français. Les particules et structures nobles ont été fragmentées ou ignorées :
    * **"Noël Joubert de Lagarde"** (Commentaire #9) a été découpé en un patchwork de plusieurs individus au lieu d'un seul bloc.
    * **"Sabine Rey du Grondin"** (Commentaire #12) a été tronquée et partiellement oubliée.
    * **"Philippine de la Duval"** (Commentaire #13) a totalement échappé à la vigilance du modèle NER, le nom étant resté visible en texte brut dans l'export.

## Si je devais industrialiser

> Que faudrait-il ajouter pour une vraie mise en production (M5+) ?

- Pour passer du prototype du notebook à une véritable mise en production industrielle à l'échelle de l'entreprise, l'utilisation de **Microsoft Presidio** doit être conteneurisée et architecturée ainsi :

1. **Micro-services et API REST :** Sortir du script séquentiel Pandas/Notebook. Il faut déployer Presidio sous forme de conteneurs Docker (un conteneur pour le `presidio-analyzer` et un pour le `presidio-anonymizer`) 
2. **Supervision Humaine (AI Act - Haut Risque) :** Mettre en place un seuil de confiance (Confidence Score). Si Presidio a un doute sur une entité (score < 85%), le commentaire est envoyé dans une file de quarantaine pour validation manuelle par un officier de conformité avant d'intégrer le Data Lake.
3. **Pipeline de données optimisé :** Automatiser le flux pour que les fichiers nettoyés soient directement stockés dans un Data Lake au format **Parquet via PyArrow**, partitionnés par année/filiale, réduisant les coûts de stockage de 50% comme démontré lors de notre phase de test.

---

*Note rédigée par Joelle, 18/06/2026, dans le cadre du brief M2-B2 ATOS.*