# SamWord 🇫🇷

SamWord est un **jeu de lettres en français**, inspiré du principe du scrabble, mais avec son identité propre (nom, implémentation, ressources et dictionnaire autonomes).

## Objectif
Former des mots croisés sur un plateau de 15x15 pour marquer un maximum de points.

## Fonctionnalités incluses
- Plateau 15x15 avec cases bonus (lettre x2/x3, mot x2/x3).
- 2 à 4 joueurs.
- Chevalet de 7 lettres par joueur.
- Sac de lettres avec distribution et points adaptés au français.
- Joker (`?`) pris en charge.
- Validation des mots via un dictionnaire français local (`words_fr.txt`).
- Calcul complet du score:
  - bonus lettres et mots;
  - mots croisés secondaires;
  - bonus de 50 points si les 7 lettres sont jouées.
- Commandes de jeu: jouer, passer, échanger, afficher scores/plateau/chevalet.
- Fin de partie et ajustement des scores finaux.

## Démarrage rapide (local)
1. Ouvrir un terminal dans le dossier du projet.
2. Vérifier Python 3:
   ```bash
   python3 --version
   ```
3. Lancer le jeu:
   ```bash
   python3 samword.py
   ```

## Démarrage depuis GitHub
```bash
git clone <URL_DE_TON_REPO_GITHUB>
cd <NOM_DU_REPO>
python3 samword.py
```

> Important: `samword.py` et `words_fr.txt` doivent rester dans le même dossier.

## Commandes principales
- `JOUER <mot> <ligne> <colonne> <H|V>`
- `ECHANGER <lettres>`
- `PASSER`
- `PLATEAU`
- `CHEVALET`
- `SCORES`
- `AIDE`
- `QUITTER`

Exemple:
```text
JOUER MAISON 7 4 H
```

## Dépannage
- Si le jeu ne démarre pas:
  ```bash
  python3 -m py_compile samword.py
  ```
- Si tu vois `Dictionnaire introuvable`, vérifie la présence de `words_fr.txt` à côté de `samword.py`.

## Remarque juridique
SamWord fournit une expérience de jeu de lettres complète en français sans réutiliser de marque, de logo ou de contenus propriétaires tiers.
