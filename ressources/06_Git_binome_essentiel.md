# Git en binôme — Mini-cours

> Brief associé : M2-B2 (phase sync mercredi)
> Durée de lecture + pratique : ~15 min
> Pré-requis : git de base maîtrisé (clone, commit, push, branches).

## Pourquoi cette techno ?

C'est ton **premier vrai brief binôme** du parcours. CT6 (travailler en
équipe) est **observée** mercredi, **non évaluée** encore. L'enjeu : que
le binôme **produise** sans se bloquer mutuellement.

Trois pratiques à acquérir :

1. **Driver / Navigator** : un seul code à la fois, l'autre relit, conteste,
   documente
2. **Co-authored-by** : conventions Git pour signaler que 2 personnes ont
   produit ensemble
3. **Branches courtes** : éviter le bordel des merges sur main

**Pourquoi ces pratiques** : en M3, M6, M7, M8 vous serez à nouveau en
binôme. Si vous installez les bons réflexes maintenant, ça paye 4 fois.

## Concepts clés

- **Driver** : la personne au clavier. **Une seule** à la fois.
- **Navigator** : la personne qui regarde, conteste, documente, ouvre la
  doc, vérifie. **Pas** la personne qui « ne fait rien » — souvent, c'est
  elle qui voit les erreurs.
- **Switch** : tous les **30 min**, on échange. Sinon le navigator décroche.
- **`Co-authored-by:`** : ligne dans le message de commit qui signale que
  X et Y ont produit ensemble. GitHub l'affiche dans le profil des deux.
- **Branche perso** (en async) : `anonymisation/<prénom>` — pour ne pas
  écraser le travail du binôme.

## Conventions binôme

> 💡 **Le workflow ci-dessous est une _convention_, pas une contrainte
> technique.** L'objectif réel, c'est la **coordination** (ne pas s'écraser, se
> relire, tracer qui a produit quoi) — pas le respect d'un protocole exact. Si
> ton binôme trouve une organisation qui coordonne mieux, garde l'esprit
> (driver/navigator, switch régulier, commits signés à deux) et adapte la
> lettre. Ce qui compte : que personne ne soit bloqué et que le duo produise.

### En sync mercredi

1. **Un seul écran partagé** sur Discord (le driver share). Pas 2 écrans.
2. **Switch driver/navigator** toutes les 30 min (timer).
3. **Tous les commits significatifs** incluent :
   ```
   feat(audit): calcul DI sur sex et race

   Co-authored-by: Prénom1 <prenom1@email.com>
   ```
4. **Repo commun** : créé sur le compte de l'un des deux, l'autre invité
   comme collaborateur (Settings → Collaborators).

### En async jeudi/vendredi

1. **Fork** le repo binôme sous `M2-B2-athena-<prénom>` sur ton compte
   perso. **Pas** une branche du repo commun (ça polluerait celui du
   binôme).
2. **Branche dédiée** : `anonymisation/<prénom>` (sur ton fork).
3. **Commits perso** : signature simple `Author: <prénom> <email>`, pas
   de `Co-authored-by:`.
4. Tu **ne pousses pas** sur le repo binôme en async (sauf accord
   explicite).

## Exemple minimal qui tourne

### Setup binôme à 9h15

```bash
# Le binôme A crée le repo commun depuis le template
# (sur github.com, "Use this template" → "Create a new repository")
# Nom : M2-B2-athena-alice-bob
# Owner : alice
# Privé : oui

# Alice ajoute Bob comme collaborateur :
# Settings → Collaborators → Add Bob

# Les deux clonent
git clone git@github.com:alice/M2-B2-athena-alice-bob.git
cd M2-B2-athena-alice-bob

# Configuration locale (à faire la première fois sur chaque machine)
git config user.name "Alice Dupont"     # ou Bob
git config user.email "alice@..."        # ou Bob
```

### Premier commit avec Co-authored-by

```bash
# Alice est driver, Bob est navigator
# Ils ajoutent une cellule au notebook
git add notebooks/M2-B2_audit_alice_bob.ipynb
git commit -m "feat(audit): scaffold du notebook + setup imports

Co-authored-by: Bob Martin <bob@email.com>"

git push
```

### Switch driver après 30 min

```bash
# Bob prend le clavier (share son écran)
# Alice devient navigator
# (rien à changer dans Git, juste qui code)
# Le prochain commit inclura :
# Co-authored-by: Alice Dupont <alice@...>
```

### Fork en async

```bash
# Sur github.com : page du repo commun → "Fork" → ton compte perso
# Nom du fork : M2-B2-athena-<prénom>

git clone git@github.com:<prénom>/M2-B2-athena-<prénom>.git
cd M2-B2-athena-<prénom>
git checkout -b anonymisation/<prénom>

# Travaille
git add src/anonymize.py
git commit -m "feat(anonymize): stratégie hash + suppression"
git push -u origin anonymisation/<prénom>

# À la fin, merge sur main de ton fork
git checkout main
git merge anonymisation/<prénom>
git push
```

## Exercice guidé (à 9h15 mercredi avec ton binôme)

1. Choisissez **qui possède le repo** (= owner sur GitHub)
2. L'owner crée le repo depuis le template
3. L'owner invite l'autre comme collaborateur
4. **Les deux clonent**
5. Faites **votre premier commit duo** :
   - Driver écrit la première cellule markdown du notebook
   - Commit : `git commit -m "init: header notebook + auteurs

Co-authored-by: <autre>"`

Si ce premier commit duo passe, le reste suit. **Si vous galérez plus de
10 min ici, demandez à Marianne** — c'est plus simple que de bloquer.

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| Deux drivers en parallèle (2 écrans, 2 codes) | Merges en pagaille, conflit après 30 min |
| Pas de switch — Alice code tout, Bob regarde | CT6 ratée, Bob décroche, un seul commit valide |
| `Co-authored-by:` mal formaté | GitHub ne l'affiche pas — `Co-authored-by: <nom> <email>` exact |
| Email perso vs email no-reply GitHub | Le `Co-authored-by:` ne lie pas au profil GitHub → utilise l'email du profil GitHub (Settings → Emails) |
| Push direct sur le main du commun en async | Bob écrase le travail d'Alice sans s'en rendre compte |
| Fork mal fait | Tu travailles sur le repo commun au lieu de ton fork — push refusé ou écrasement |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| GitHub n'affiche pas Bob comme co-author | Ligne vide manquante avant `Co-authored-by:` dans le message de commit |
| Conflit de merge en sync | Les 2 ont commit en parallèle sans pull — synchronisez-vous au début et fin de switch |
| Bob ne peut pas push | Il n'a pas été invité comme collaborateur — Alice doit l'inviter en Settings |
| Le fork apparaît vide | Tu as cloné le repo commun et essayé de push sur ton compte — refais un fork via GitHub UI |
| Branche `anonymisation/<prénom>` invisible sur GitHub | Tu as oublié de pousser : `git push -u origin anonymisation/<prénom>` |

## Pour aller plus loin

- **GitHub Docs — Co-authored commits** : <https://docs.github.com/fr/pull-requests/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors>
- **Atlassian — Driver/Navigator pair programming** : <https://www.atlassian.com/agile/software-development/pair-programming>
- **GitHub Docs — Forking** : <https://docs.github.com/fr/get-started/quickstart/fork-a-repo>

## Vérification (checklist binôme)

- [ ] Repo commun créé avec le bon nom (`M2-B2-athena-<prénom1>-<prénom2>`)
- [ ] L'un est owner, l'autre est invité comme collaborateur
- [ ] Au moins **3 commits significatifs** incluent `Co-authored-by:` correct
- [ ] Vous avez **switché** driver/navigator au moins **2 fois**
- [ ] En async, chacun a forké et créé sa branche `anonymisation/<prénom>`
- [ ] Personne n'a pushé sur le repo commun en async (sauf accord
      explicite)