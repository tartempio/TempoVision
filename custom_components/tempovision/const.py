"""Constants for the TempoVision integration."""

DOMAIN = "tempovision"
# supported platforms – sensor already, add button for manual refresh
PLATFORMS = ["sensor", "button"]

# scraping
KELWATT_TARGET_URL = "https://www.kelwatt.fr/fournisseurs/edf/tempo"
OPEN_DPE_TARGET_URL = "https://open-dpe.fr/assets/tempo_days.json"

# the three tempo colours
TEMPO_COLOURS = ("Rouge", "Blanc", "Bleu")

WEEKDAYS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

# Configuration
CONF_SOURCE = "source"
CONF_SEPARATE_PROB_ENTITIES = "separate_probabilities"

SOURCE_KELWATT = "kelwatt"
SOURCE_OPEN_DPE = "open_dpe"

DEFAULT_SOURCE = SOURCE_OPEN_DPE
DEFAULT_SEPARATE_PROB_ENTITIES = False