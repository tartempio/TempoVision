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

TempoVision est une intégration personnalisée pour Home Assistant permettant de suivre et de prédire les couleurs du contrat **EDF Tempo** (Bleu, Blanc, Rouge) pour la semaine à venir.

L'audience de cette intégration étant principalement française, cette documentation est rédigée en français.

## Caractéristiques

- **Deux sources de données au choix** :
  - **Kelwatt** : Récupère depuis [Kelwatt](https://www.kelwatt.fr/fournisseurs/edf/tempo), avec prévisions détaillées et probabilités par couleur.
  - **Open-DPE** : Récupère depuis [open-dpe.fr](https://open-dpe.fr), avec un format J+n et probabilités par couleur.
- **Prévisions sur 8 jours** :
  - Avec **Kelwatt** : Affiche la couleur pour aujourd'hui (J), demain (J+1) et prévisions jusqu'à J+8.
  - Avec **Open-DPE** : Crée des entités J+1 à J+8 (pas de J).
- **Probabilités par couleur** : Pour les deux sources, expose les probabilités pour chaque couleur (Bleu, Blanc, Rouge).
- **Probabilité de l'état** : Un attribut "Probabilité" expose le pourcentage pour la couleur de l'état (couleur la plus probable).
- **Mise à jour automatique** : Les données sont rafraîchies selon un horaire adaptatif : toutes les heures en journée, et toutes les 5 minutes entre 06 h et 08 h.
- **Organisation simplifiée** : Toutes les entités sont regroupées sous un seul appareil de type "Service" nommé **TempoVision**.
- **Configurable** : Option permettant (pour les deux sources) d'exposer les probabilités sous forme d'attributs (par défaut) ou de capteurs individuels.

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

Une seule étape vous demande de configurer :

1. **Source de simulation** : Choisissez entre **Kelwatt** ou **Open-DPE** (**Open-DPE** est proposé par défaut).
2. **Probabilités séparées** (optionnel) : Activez l'option **"Exposer chaque pourcentage de couleur dans des entités séparées"** pour créer des capteurs dédiés pour les probabilités de chaque couleur, ou rester avec les attributs par défaut.

## Entités créées

### Bouton d'actualisation

L'intégration crée un **bouton de rafraîchissement** :
- `button.tempovision_refresh` : force le téléversement immédiat des données.

### Capteurs Tempo

L'intégration crée un capteur pour chaque jour prévu :

**Avec Kelwatt** :
- `sensor.tempovision_j` : Couleur d'aujourd'hui.
- `sensor.tempovision_j_1` à `sensor.tempovision_j_8` : Prévisions pour les 8 jours suivants.

**Avec Open-DPE** :
- `sensor.tempovision_j_1` à `sensor.tempovision_j_8` : Prévisions J+1 à J+8 (pas de "J").

Chaque entité contient :
- **État** : La couleur prévue (Bleu, Blanc ou Rouge).
- **Attributs** :
  - `date` : La date ISO du jour.
  - `probabilite` : Probabilité de la couleur de l'état (0–100 %).
  - `probabilite_rouge` : Probabilité de la couleur Rouge.
  - `probabilite_blanc` : Probabilité de la couleur Blanc.
  - `probabilite_bleu` : Probabilité de la couleur Bleu.
- **Entités séparées** (si option activée) : Des capteurs individuels pour les probabilités de chaque couleur : `sensor.tempovision_j_x_probabilite_rouge`, etc.

## Avertissement

- **Sources Kelwatt** : Les données affichées pour les jours J+2 et suivants sont des prévisions basées sur des probabilités calculées par Kelwatt. Seule la couleur officielle communiquée par RTE/EDF fait foi.
- **Source Open-DPE** : Les prévisions sont basées sur les données publiques de [open-dpe.fr](https://open-dpe.fr). Consultez le site officiel pour la validité et l'actualité des données.

## Support et contribution

Pour toute question, bug ou suggestion, veuillez consulter l'[issue tracker](https://github.com/tartempio/TempoVision/issues).
