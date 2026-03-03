[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

[releases-shield]: https://img.shields.io/github/release/tartempio/TempoVision.svg?style=for-the-badge
[releases]: https://github.com/tartempio/TempoVision/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/tartempio/TempoVision.svg?style=for-the-badge
[commits]: https://github.com/tartempio/TempoVision/commits/main
[license-shield]: https://img.shields.io/github/license/tartempio/TempoVision.svg?style=for-the-badge
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[hacs]: https://github.com/custom-components/hacs

# TempoVision

*Nouvelles fonctionnalités (mars 2026) : planification dynamique des mises à jour, identifiants de probabilités normalisés, et bouton d'actualisation.*

TempoVision est une intégration personnalisée pour Home Assistant permettant de suivre et de prédire les couleurs du contrat **EDF Tempo** (Bleu, Blanc, Rouge) pour la semaine à venir.

L'audience de cette intégration étant principalement française, cette documentation est rédigée en français.

## Caractéristiques

- **Données en temps réel** : Récupère les informations directement depuis [Kelwatt](https://www.kelwatt.fr/fournisseurs/edf/tempo).
- **Prévisions sur 7 jours** : Affiche la couleur pour aujourd'hui (J), demain (J+1) et des prévisions jusqu'à J+8.
- **Probabilités détaillées** : Pour les jours de prévision (à partir de J+2), l'intégration expose les probabilités de chaque couleur (Bleu, Blanc, Rouge).
- **Mise à jour automatique** : Les données sont rafraîchies selon un horaire adaptatif (voir ci‑dessous) : toutes les heures en journée, et toutes les 5 minutes entre 06 h et 08 h.
- **Organisation simplifiée** : Toutes les entités sont regroupées sous un seul appareil de type "Service" nommé **TempoVision**.
- **Configurable** : Option permettant de choisir d'exposer les probabilités sous forme d'attributs (par défaut) ou de capteurs individuels.

## Installation

### Via HACS (Recommandé)

[![Open your Home Assistant instance and open a repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=tartempio&repository=TempoVision&category=integration)

Ou manuellement:

1. Ouvrez **HACS** dans votre instance Home Assistant.
2. Allez dans **Intégrations**.
3. Cliquez sur les trois points en haut à droite et choisissez **Dépôts personnalisés**.
4. Ajoutez l'URL de ce dépôt et sélectionnez la catégorie **Intégration**.
5. Recherchez **TempoVision** et cliquez sur **Télécharger**.
6. Redémarrez Home Assistant.

## Configuration

1. Allez dans **Paramètres** > **Appareils et services**.
2. Cliquez sur **Ajouter une intégration** en bas à droite.
3. Recherchez **TempoVision** et suivez les instructions.
4. Lors de la configuration, vous pouvez choisir d'activer l'option **"Exposer chaque pourcentage de couleur dans des entités séparées"**.

## Entités créées

L'intégration ajoute désormais un **bouton d'actualisation** :
- `button.tempo_refresh` : force le téléversement immédiat des données depuis le site Tempo.


L'intégration crée un capteur pour chaque jour :
- `sensor.tempo_j` : Couleur d'aujourd'hui.
- `sensor.tempo_j_1` : Couleur de demain.
- `sensor.tempo_j_2` à `sensor.tempo_j_8` : Prévisions pour les jours suivants.

Chaque entité contient des attributs tels que la date précise et les probabilités de couleurs. Les probabilités sont exposées sous le format `probabilite_<couleur>` (par exemple `probabilite_rouge`). Si l'option est activée, des capteurs individuels seront également créés : `sensor.tempo_j_x_probabilite_rouge`, `sensor.tempo_j_x_probabilite_blanc`, etc.

## Avertissement

Les données affichées pour les jours J+2 et suivants sont des prévisions basées sur des probabilités calculées par Kelwatt. Seule la couleur officielle communiquée par RTE/EDF fait foi.
