# Microsoft Presidio (bonus) — Mini-cours

> Brief associé : M2-B2 (bonus optionnel async)
> Durée de lecture + pratique : ~20 min
> Pré-requis : avoir terminé le tronc (spaCy + regex + stratégie + reflexion).
>
> ⚠️ **Ce mini-cours est BONUS.** Ne le lis que si tu as fini le tronc.
> Pas requis pour valider M2-B2.

## Pourquoi cette techno ?

**Microsoft Presidio** est un **framework open-source** d'anonymisation de
PII, qui **emballe** ce que tu as construit à la main :

- **Détection** combinée spaCy + regex + transformers (Analyzer)
- **Anonymisation** avec stratégies pré-câblées (Anonymizer)
- **Plus de 40 types de PII** détectées out-of-the-box (passeport US, IBAN,
  carte bancaire, IP, MAC, etc.)
- **Production-ready** : utilisé par Microsoft Azure, AWS, plusieurs banques

Si tu veux pousser au-delà du tronc M2-B2, Presidio est une bonne porte
d'entrée vers un outil pro. **Et ça fera une bonne discussion en
restitution** sur les trade-offs *build vs buy*.

**Alternatives à connaître :**

| Approche | Niveau de maturité |
|---|---|
| **spaCy + regex (tu)** | Tronc M2 — transparent, compréhensible |
| **Presidio** | Bonus M2, central M7 — production-ready |
| **AWS Comprehend** | SaaS payant, anonymisation cloud |
| **Azure Cognitive Services** | SaaS Microsoft, similaire à AWS |
| **Cloud DLP (Google)** | SaaS payant, complet |

Comparaison synthétique :

| Critère | spaCy + regex | Presidio | Cloud (AWS/Azure/GCP) |
|---|---|---|---|
| Coût | Gratuit | Gratuit | $$ |
| Maintenance | Toi | Microsoft | Cloud provider |
| Customisation | Totale | Forte | Limitée |
| Production-ready | ⚠️ DIY | ✅ | ✅ |
| Souveraineté | ✅ local | ✅ local | ❌ |
| Démarrage | 30 min | 1 h | 30 min |

## Concepts clés

- **`AnalyzerEngine`** : détecte les PII (équivalent ton spaCy + regex).
  Retourne une liste de `RecognizerResult` avec type, start, end, score.
- **`AnonymizerEngine`** : applique une stratégie d'anonymisation aux
  détections de l'Analyzer.
- **Recognizers** : 50+ pré-câblés (PERSON, EMAIL_ADDRESS, PHONE_NUMBER,
  IBAN_CODE, US_SSN, CREDIT_CARD, IP_ADDRESS, etc.). Tu peux ajouter les
  tiens (regex ou modèle).
- **Operators** : `replace` (suppression), `mask` (substitution char par
  char), `hash`, `encrypt` (réversible avec clé), `redact` (suppression).

## Exemple minimal qui tourne

```python
# pip install presidio-analyzer presidio-anonymizer
# python -m spacy download en_core_web_md  (déjà fait)
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = (
    "Allison Hill is a strong candidate. "
    "Contact: rhonda@hr.example, 651-216-1559. "
    "Account ****3503."
)

# 1. Détection
results = analyzer.analyze(text=text, language="en")
for r in results:
    print(r.entity_type, text[r.start:r.end], f"(score={r.score:.2f})")
# PERSON Allison Hill (score=0.85)
# EMAIL_ADDRESS rhonda@hr.example (score=1.0)
# PHONE_NUMBER 651-216-1559 (score=0.75)
# ...

# 2. Anonymisation (stratégie : suppression simple)
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
print(anonymized.text)
# → "<PERSON> is a strong candidate. Contact: <EMAIL_ADDRESS>, <PHONE_NUMBER>. Account ****3503."
```

Pour une **stratégie hash** :

```python
operators = {
    "PERSON": OperatorConfig("hash", {"hash_type": "sha256"}),
    "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
}
anonymized = anonymizer.anonymize(
    text=text, analyzer_results=results, operators=operators
)
print(anonymized.text)
```

## Exercice guidé (bonus)

1. Installe Presidio
2. Lance sur 10 exemples de `audit_sample.csv`
3. **Compare** ses détections vs ton implémentation spaCy + regex :
   - Y a-t-il des PII que Presidio attrape **et que tu rates** ?
   - Y a-t-il des PII que tu attrapes **et que Presidio rate** ?
4. Dans `reflexion.md`, ajoute un paragraphe **« Comparatif Presidio »** :
   - Force de Presidio
   - Faiblesse observée
   - Garderais-tu Presidio en prod ? Pourquoi ?

## Pièges fréquents

| Piège | Conséquence |
|---|---|
| `pip install presidio` (sans suffixe) | Ne marche pas — il faut `presidio-analyzer` ET `presidio-anonymizer` séparément |
| Lancer Presidio sans installer un modèle spaCy | Presidio plante au démarrage |
| Utiliser Presidio sur du français | Le support FR est **limité** — préfère spaCy `fr_core_news_md` à la main |
| Cargo cult : adopter Presidio sans comprendre | Tu perds la transparence — comprends d'abord, adopte ensuite |

**Symptôme → cause probable** :

| Symptôme | Cause probable |
|---|---|
| `ImportError: presidio_analyzer` | `pip install presidio-analyzer presidio-anonymizer` manquant |
| Presidio détecte beaucoup de faux positifs | Tu peux régler `score_threshold=0.7` au `.analyze(...)` |
| Pas de détection sur du FR | Charger explicitement un modèle FR : `nlp_engine = NlpEngineProvider(nlp_configuration={'lang_code': 'fr', ...})` |
| Plus lent que ton implémentation | Normal — Presidio fait plus de checks. Acceptable en prod, pas idéal en batch massif |

## Pour aller plus loin

- **Doc officielle Presidio** : <https://microsoft.github.io/presidio/>
- **GitHub Presidio** : <https://github.com/microsoft/presidio>
- **Article ENISA — PETs (Privacy-Enhancing Technologies)** : pour le
  contexte réglementaire

## Vérification (checklist apprenant)

- [ ] Presidio installé et lancé sur au moins 10 exemples
- [ ] Comparatif spaCy+regex vs Presidio rédigé dans `reflexion.md`
- [ ] J'ai compris que **Presidio n'est pas magique** — il combine les
      mêmes briques que ce que j'ai fait à la main
- [ ] Je sais dire si Presidio est adapté à mon contexte (français,
      souveraineté, transparence)