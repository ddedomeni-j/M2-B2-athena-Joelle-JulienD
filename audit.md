# Audit du dataset fourni par Athéna RH

## 1. Verdict qualité

1. 3 features ont des données manquantes : occupation, workclass et native_country
Le nombre de valeurs manquantes étant faible on suggère d'utiliser une stratégie de remplacement par la valeur la plus fréquente

2. Les données sont globalement déséquilibrées : à part pour la feature "occupation" il y a un fort déséquilibre entre les différentes catégories des features. Ce déséquilibre est fort pour les catégories "sexe" et "relationship" et supérieur ou égal à 1000 en ration pour les autres features

3. Il y a des valeurs qui semblent étranges pour la feature "education_num" : est-ce que les valeurs inférieures à 7 ont un sens?

4. La feature "income" présente un déséquilibre : seuls 24.1% des salariés ont un revenu supérieur à 50K

5. La feature "fnlwgt" est une donnée statistique qui ne sera pas utile au modèle. On propose de la retirer.

6. La feature "marital_status" est une donnée sensible qui croisée avec d'autres feautures comme "sexe" et "relationship" peut permettre de remonter à l'individu. On propose d'écrater cette feature

7. les features "capital_loss" et "capital_gain" n'a pas d'utilité pour créer le modèle, elles peuvent être supprimées du modèle de données

8. La feature "hours_per_week" présente une forte disparité : y a-t-il une erreur dans les données lorsqu'on trouve un revenu > à 50K associé à une ou deux heures par semaine. Il faudra valider avec le client qu'il ne s'agit pas d'une erreur

9. L'âge est une donnée qui peut être considérée comme sensible mais elle est forcément liée à l'évolution de carrière. On propose donc de la conserver dans les sonnées du modèle

10. "manager_comments" est une feature disparate contenant des informations personnelles qui devra être traitée à part

11. Les features "education" et "education_num" sont liées. On conservera "education_num" qui est ordinale et n'a donc pas à être transformée pour créer le modèle de données

## 2. Verdict éthique

1. L'analyse du DI du genre sur le revenu donne un ratio de 0.35 qui constitue une alerte. De plus la feature "genre" est une donnée sensible que l'on propose d'abandonner

2. L'analyse du DI de la race sur le revenu donne un ratio de 0.484 qui constitue une alerte. Le DI entre race et genre est de 0.164 qui est très faible. De plus la feature "race" est une donnée sensible que l'on propose d'abandonner

3. L'analyse du DI de la native_country sur le revenu donne un ratio de 0.804 qui est à la limite du seuil d'alerte. La feature est une donnée sensible, on propose également de la retirer

## 3. Recommandations

- On conserve les features "age", "workclass", "education_num", "occupation income"
- La feature "manager_comments" doit être retraitée pour anonymiser et extraire les informations pertinentes
- La feature "hours_per_week" doit être revue et validée avec le client
- Les features "fnlwgt", "marital_status", "relationship", "race", "sex", "capital_gain capital_loss", "native_country "education" ne seront pas incluses dans le modèle de données


---

*Audit produit par <Joelle> et <Julien>, <17/06/2026>, dans le cadre du brief M2-B2 ATOS.*