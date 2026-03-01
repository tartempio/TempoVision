"""Constants for the TempoVision integration."""

DOMAIN = "tempovision"
PLATFORMS = ["sensor"]

# scraping
TARGET_URL = "https://www.kelwatt.fr/fournisseurs/edf/tempo"

# the three tempo colours
TEMPO_COLOURS = ("Rouge", "Blanc", "Bleu")

WEEKDAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# Configuration
CONF_SEPARATE_PROB_ENTITIES = "separate_probabilities"
DEFAULT_SEPARATE_PROB_ENTITIES = False