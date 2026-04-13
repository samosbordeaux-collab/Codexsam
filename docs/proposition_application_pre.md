# Proposition d'application interne PRE (pilotage des 95 mesures)

## 1) Contexte synthétique

Le besoin vise à sécuriser et industrialiser la production du rapport mensuel PRE, aujourd'hui produite à partir de sources hétérogènes (PDF, Excel, Word, mails, notes) et consolidée via un outil IA externe.

Contraintes fortes :
- sensibilité des instances destinataires (COSUI, consolidation préfectorale trimestrielle),
- exigence de traçabilité et d'auditabilité,
- traitement en moins d'une demi-journée,
- absence d'équipe dédiée (1 personne en charge).

## 2) Objectifs de l'application

L'application doit couvrir 3 objectifs opérationnels :
1. **Centraliser** les données des 95 mesures PRE dans une base interne unique.
2. **Contrôler automatiquement** la qualité des données (vides, doublons, incohérences inter-sources, valeurs aberrantes).
3. **Produire rapidement** un rapport mensuel consolidé, versionnable et diffusable aux instances.

## 3) Périmètre fonctionnel cible

### 3.1 Ingestion multi-format
- Dépôt de fichiers : PDF, XLSX, CSV, DOCX, ODT, TXT.
- Connecteurs mail (boîte fonctionnelle dédiée) pour ingestion automatisée.
- Modèle de métadonnées obligatoire à l'import :
  - période de référence,
  - organisme émetteur,
  - mesure PRE concernée,
  - version/source.

### 3.2 Normalisation et référentiel commun
- Schéma de données unique par mesure PRE :
  - identifiant mesure,
  - budget prévu / réalisé,
  - avancement (%),
  - statut (OK / vigilance / alerte),
  - commentaires et justificatifs.
- Mapping semi-assisté des colonnes sources vers ce schéma.
- Historisation complète (qui a importé quoi, quand, et quelle version).

### 3.3 Contrôles qualité automatiques (équivalent usages ChatGPT Pro)
- Détection des champs manquants.
- Détection des doublons (exacts et proches).
- Règles d'incohérence métier :
  - avancement > 100%,
  - budget réalisé sans budget prévu,
  - variations anormales par rapport au mois précédent.
- Score de confiance des données par mesure.
- File d'anomalies à traiter avec workflow : Nouveau / En cours / Résolu / Rejeté.

### 3.4 Consolidation temporelle et mémoire interne
- Vue mensuelle consolidée.
- Vue comparative N / N-1 / N-12.
- Journal des corrections et justification des arbitrages.
- Recherche plein texte sur l'historique des échanges et décisions.

### 3.5 Génération de rapports
- Génération automatique du rapport mensuel (DOCX + PDF).
- Synthèse exécutive + annexes détaillées par mesure.
- Indicateurs clés : taux de complétude, nombre d'anomalies, mesures à risque.
- Export trimestriel dédié au préfet (format standardisé).

### 3.6 Gouvernance, sécurité, conformité
- Hébergement interne (réseau et stockage maîtrisés DSIN).
- SSO + RBAC (rôles : contributrice, valideur, lecture COSUI, admin).
- Chiffrement au repos et en transit.
- Journal d'audit immuable (lecture/écriture/export).
- Rétention paramétrable et purge conforme politique SI.

## 4) Architecture recommandée (MVP pragmatique)

- **Front-office** : application web interne (formulaires d'import, tableaux de bord, traitement anomalies).
- **Back-end** : API métier (validation, consolidation, génération rapports).
- **Base de données** : PostgreSQL (données structurées) + stockage objet interne (pièces sources).
- **Moteur de règles** : bibliothèque de règles versionnées (YAML/SQL) pour contrôles qualité.
- **IA interne optionnelle** (encadrée) :
  - extraction assistée de textes/tabulaires,
  - proposition d'explication d'écarts,
  - jamais de sortie de données hors SI interne.

## 5) Plan de mise en oeuvre proposé

### Phase 0 — Cadrage (2 semaines)
- Ateliers métier avec Mohana + DSIN.
- Définition du dictionnaire de données PRE (95 mesures).
- Catalogue des règles de contrôle prioritaires.
- Maquette du rapport cible (mensuel + trimestriel).

### Phase 1 — MVP sécurisé (6 à 8 semaines)
- Import Excel/CSV + formulaire manuel.
- Référentiel mesures PRE + historisation.
- Règles de qualité de base (vides, doublons, incohérences simples).
- Rapport mensuel auto + export PDF.

### Phase 2 — Industrialisation (6 semaines)
- Ingestion DOCX/PDF/mails.
- Workflow complet de traitement d'anomalies.
- Tableaux de bord décideurs.
- Exports trimestriels préfet + audit avancé.

### Phase 3 — Optimisation IA interne (option, 4 semaines)
- Assistance à l'analyse d'écarts.
- Suggestions de plans d'action basées sur l'historique interne.
- Évaluation continue qualité/risque de l'IA interne.

## 6) Indicateurs de succès

- Temps de production du rapport mensuel : **< 2 heures**.
- Taux d'anomalies détectées automatiquement : **> 90%** des cas connus.
- Taux de complétude des 95 mesures : **> 98%** avant comité.
- Traçabilité : **100%** des modifications historisées.
- Zéro transfert de données sensibles vers des services IA externes.

## 7) Alternatives à instruire (comme évoqué en séance)

1. **Spécialisation d'un LLM interne dédié PRE**
   - Avantage : qualité d'analyse narrative et détection avancée.
   - Risque : délai de mise au point, gouvernance MLOps.

2. **Pilote Copilot Pro en environnement cloisonné**
   - Avantage : accélération productive.
   - Risque : vérifier précisément clauses contractuelles, résidence des données, journalisation.

3. **Approche sans LLM (règles + BI)**
   - Avantage : robustesse, auditabilité maximale, time-to-value rapide.
   - Limite : moins performant sur documents non structurés.

## 8) Recommandation immédiate

Au vu de la charge et de la criticité, lancer **d'abord un MVP sans dépendance forte à un LLM externe**, centré sur :
- centralisation,
- contrôles qualité automatisés,
- génération de rapport standardisé,
- sécurité et audit.

Puis ajouter progressivement une brique IA interne assistive une fois le socle de données fiabilisé.
