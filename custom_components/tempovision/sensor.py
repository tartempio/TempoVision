"""Sensor platform for the TempoVision integration."""
from __future__ import annotations

from datetime import datetime, timedelta
import logging
import re
from typing import Any, Optional

from homeassistant.util import dt as dt_util

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.const import PERCENTAGE
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN, 
    TARGET_URL, 
    WEEKDAYS, 
    TEMPO_COLOURS,
    CONF_SEPARATE_PROB_ENTITIES,
    DEFAULT_SEPARATE_PROB_ENTITIES,
)

# mapping of french month names to month numbers for date parsing
MONTHS: dict[str, int] = {
    "janvier": 1,
    "février": 2,
    "fevrier": 2,
    "mars": 3,
    "avril": 4,
    "mai": 5,
    "juin": 6,
    "juillet": 7,
    "août": 8,
    "aout": 8,
    "septembre": 9,
    "octobre": 10,
    "novembre": 11,
    "décembre": 12,
    "decembre": 12,
}


def _date_str_to_timestamp(date_str: str) -> Optional[int]:
    """Convert a french date string (e.g. "lundi 2 mars") to a Unix timestamp.

    If no year is provided the current year is assumed.  Returns ``None`` if the
    string cannot be parsed.  The resulting datetime is converted to UTC using
    Home Assistant utilities so that the timestamp is consistent with HA's
    timezone handling.
    """
    parts = date_str.lower().split()
    # first word is weekday, drop it if present
    if parts and parts[0] in WEEKDAYS:
        parts = parts[1:]
    if len(parts) < 2:
        return None
    try:
        day = int(parts[0])
    except ValueError:  # not a number
        return None
    month_name = parts[1]
    year = datetime.now().year
    if len(parts) >= 3:
        try:
            year = int(parts[2])
        except ValueError:
            pass
    month = MONTHS.get(month_name)
    if not month:
        return None
    try:
        # assume 06:00 in Paris local time as per new requirement
        from zoneinfo import ZoneInfo
        paris = ZoneInfo("Europe/Paris")
        dt = datetime(year, month, day, 6, tzinfo=paris)
    except Exception:
        return None
    # convert to UTC timestamp
    dt_utc = dt.astimezone(dt_util.UTC)
    return int(dt_utc.timestamp())

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(hours=2)


async def async_setup_entry(
    hass: HomeAssistant, 
    entry: ConfigEntry, 
    async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensors for a config entry."""
    data = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    coordinator: TempoDataUpdateCoordinator | None = data.get("coordinator")
    if coordinator is None:
        coordinator = TempoDataUpdateCoordinator(hass)
        data["coordinator"] = coordinator
        await coordinator.async_config_entry_first_refresh()

    # create one entity per weekday provided by coordinator data
    sensors: list[Entity] = []
    
    separate_probs = entry.options.get(
        CONF_SEPARATE_PROB_ENTITIES, DEFAULT_SEPARATE_PROB_ENTITIES
    )
    
    for day in coordinator.data.keys():
        sensors.append(TempoSensor(coordinator, day))
        if separate_probs and day not in ("J", "J+1"):
            for color in TEMPO_COLOURS:
                sensors.append(TempoProbabilitySensor(coordinator, day, color))

    async_add_entities(sensors, True)


class TempoDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate updates for tempo data."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="tempo",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from the remote tempo site."""
        session = aiohttp_client.async_get_clientsession(self.hass)
        try:
            response = await session.get(TARGET_URL, timeout=30)
            response.raise_for_status()
            text = await response.text()
        except Exception as err:  # pylint: disable=broad-except
            raise UpdateFailed(f"Error fetching tempo page: {err}")

        data = parse_tempo_page(text)
        if not data:
            raise UpdateFailed("No tempo information could be parsed")
        return data


def parse_tempo_page(html: str) -> dict:
    """Extract colour information, probabilities and dates from HTML.

    The site layout uses flex boxes and cards. We parse "Aujourd'hui"
    and "Demain" from header cards, and the predictions from the
    "Prévisions" cards using beautifulsoup.
    """
    try:
        from bs4 import BeautifulSoup
    except ImportError:  # pragma: no cover - defensive
        BeautifulSoup = None  # type: ignore

    results = {}
    if BeautifulSoup is None:
        return results

    soup = BeautifulSoup(html, "html.parser")
    days_in_order = []

    # 1. Parse Today and Tomorrow
    for text in ["Aujourd'hui", "Demain"]:
        el = soup.find(string=re.compile(text))
        if el:
            header = el.find_parent("div", class_=re.compile("card-header"))
            if header:
                day_p = header.find("p", class_=re.compile("text--xs"))
                if day_p:
                    date_str = day_p.get_text(strip=True).lower()
                    day_str = date_str.split(" ")[0]
                    if day_str in WEEKDAYS:
                        card = header.find_parent("div")
                        if card:
                            card_text = card.get_text(separator=" ", strip=True)
                            match = re.search(r"Tempo\s+(Bleu|Blanc|Rouge)", card_text, re.IGNORECASE)
                            if match:
                                color = match.group(1).capitalize()
                                ts = _date_str_to_timestamp(date_str)
                                results[date_str] = {"color": color, "probs": {}, "date": date_str, "timestamp": ts}
                                days_in_order.append(date_str)

    # 2. Parse Predictions (Prévisions) for the next 5 days
    for card in soup.find_all("div", class_=lambda x: x and "card" in x):
        header = card.find("div", class_="card-score__header")
        if header:
            title_p = header.find("p", class_="card-score__header--title")
            if title_p:
                date_str = title_p.get_text(strip=True).lower()
                day_str = date_str.split(" ")[0]
                if day_str in WEEKDAYS and date_str not in results:
                    color = None
                    for strong in card.find_all("strong"):
                        color_text = strong.get_text(strip=True).capitalize()
                        if color_text in TEMPO_COLOURS:
                            color = color_text
                            break
                    
                    if color:
                        probs = {"Bleu": 0.0, "Blanc": 0.0, "Rouge": 0.0}
                        prob_bar = card.find("div", class_="probability-bar")
                        if prob_bar:
                            for div in prob_bar.find_all("div", title=True):
                                title = div.get("title", "")
                                match = re.search(r"(Bleu|Blanc|Rouge)\s*:\s*([\d,.]+)\s*%", title)
                                if match:
                                    p_color = match.group(1).capitalize()
                                    prob_val = float(match.group(2).replace(",", "."))
                                    probs[p_color] = prob_val
                        
                        ts = _date_str_to_timestamp(date_str)
                        results[date_str] = {"color": color, "probs": probs, "date": date_str, "timestamp": ts}
                        days_in_order.append(date_str)

    # Convert to J+X structure
    final_dict = {}
    for i, date_str in enumerate(days_in_order):
        offset_name = "J" if i == 0 else f"J+{i}"
        final_dict[offset_name] = results[date_str]

    return final_dict


class TempoSensor(Entity):
    """Representation of a single day sensor (J+X)."""

    def __init__(self, coordinator: TempoDataUpdateCoordinator, day_key: str) -> None:
        self.coordinator = coordinator
        self.day_key = day_key
        self._attr_name = f"Tempo {day_key}"
        self._attr_unique_id = f"{DOMAIN}_{self.day_key.replace('+', '_')}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "tempovision_service")},
            name="TempoVision",
            manufacturer="Kelwatt Scraper",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self) -> Any | None:
        data = self.coordinator.data.get(self.day_key)
        if data:
            return data.get("color")
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data.get(self.day_key, {})
        attrs: dict[str, Any] = {"jour": self.day_key}
        if "date" in data:
            # change the date string to a datetime at 06:00 Paris
            date_str = data["date"]
            dt_obj = None
            try:
                # reuse timestamp helper for basic parsing
                ts = _date_str_to_timestamp(date_str)
                if ts is not None:
                    # build Paris timezone aware datetime at 6h
                    from zoneinfo import ZoneInfo
                    paris = ZoneInfo("Europe/Paris")
                    naive = datetime.fromtimestamp(ts, tz=dt_util.UTC)
                    # naive currently UTC midnight; convert to Paris date
                    dt_obj = naive.astimezone(paris).replace(hour=6, minute=0, second=0, microsecond=0)
            except Exception:
                dt_obj = None
            if dt_obj:
                attrs["date"] = dt_obj.isoformat()
            else:
                attrs["date"] = date_str
        if "probs" in data and data["probs"]:
            for color, prob in data["probs"].items():
                # rename prob attributes to full word
                attrs[f"Probabilité {color}"] = prob
        return attrs

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

class TempoProbabilitySensor(Entity):
    """Representation of a single day probability sensor (J+X)."""

    def __init__(self, coordinator: TempoDataUpdateCoordinator, day_key: str, color: str) -> None:
        self.coordinator = coordinator
        self.day_key = day_key
        self.color = color
        self._attr_name = f"Tempo {day_key} Probabilité {color}"
        self._attr_unique_id = f"{DOMAIN}_{self.day_key.replace('+', '_')}_prob_{color.lower()}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "tempovision_service")},
            name="TempoVision",
            manufacturer="Kelwatt Scraper",
            entry_type=DeviceEntryType.SERVICE,
        )
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_icon = "mdi:percent"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def state(self) -> Any | None:
        data = self.coordinator.data.get(self.day_key, {})
        probs = data.get("probs", {})
        if self.color in probs:
            return probs[self.color]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data.get(self.day_key, {})
        attrs: dict[str, Any] = {"jour": self.day_key}
        if "date" in data:
            # convert as above for probability sensor as well
            date_str = data["date"]
            dt_obj = None
            try:
                ts = _date_str_to_timestamp(date_str)
                if ts is not None:
                    from zoneinfo import ZoneInfo
                    paris = ZoneInfo("Europe/Paris")
                    naive = datetime.fromtimestamp(ts, tz=dt_util.UTC)
                    dt_obj = naive.astimezone(paris).replace(hour=6, minute=0, second=0, microsecond=0)
            except Exception:
                dt_obj = None
            if dt_obj:
                attrs["date"] = dt_obj.isoformat()
            else:
                attrs["date"] = date_str
        if "timestamp" in data and data["timestamp"] is not None:
            attrs["timestamp"] = data["timestamp"]
        return attrs

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()
