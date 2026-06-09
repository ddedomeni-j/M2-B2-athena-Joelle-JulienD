# Note de réflexion — Stratégie d'anonymisation (perso)

> Template à remplir en phase async individuelle (jeudi/vendredi matin).
> **Max 1 page.** Personnel — chaque apprenant rédige la sienne.
> Public : Marianne (évaluation) + futur toi qui relit ce repo.

---

## Ma stratégie d'anonymisation

> Quelle stratégie ai-je choisie ? Suppression / substitution /
> généralisation / hash / mix ?

...

## Ce que j'ai gardé lisible et pourquoi

> Quelles informations laisse-t-on dans le texte (et pourquoi c'est OK) ?

- ...
- ...

## Ce que j'ai masqué et pourquoi

> Quelles informations ai-je remplacées et avec quelle logique ?

- ...
- ...

## Trade-offs assumés

> Lisibilité du texte vs protection vie privée. Où ai-je placé le curseur,
> et pour quelles raisons (RGPD, métier, robustesse) ?

...

## Cadre réglementaire — RGPD + AI Act

> Deux textes, deux angles : positionne tes choix face aux **deux**.

- **RGPD** (données personnelles) : minimisation, finalité, droit à l'effacement.
  Mon anonymisation y répond par : ...
- **AI Act** (règlement UE 2024, risque classé par usage) : un système qui exploite
  des **commentaires RH** pour évaluer des personnes relève potentiellement du
  **« haut risque »** (emploi / gestion des travailleurs = Annexe III) → exigences
  renforcées de **qualité des données, traçabilité et supervision humaine**. En quoi
  mon audit + mon anonymisation y contribuent : ...

## Limites de ma stratégie

> Qu'est-ce que ma fonction `anonymize_comments` rate ? Quels faux positifs
> ou faux négatifs ai-je observés sur l'échantillon ?

- Faux négatifs (PII non détectées) : ...
- Faux positifs (texte normal anonymisé à tort) : ...

## Si je devais industrialiser

> Que faudrait-il ajouter pour une vraie mise en production (M5+) ?

- ...

---

*Note rédigée par <prénom>, <date>, dans le cadre du brief M2-B2 ATOS.*