"""Button platform for TempoVision integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType
from homeassistant.components.button import ButtonEntity

from .const import DOMAIN

from .sensor import TempoDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the refresh button entity for a config entry."""
    data = hass.data.setdefault(DOMAIN, {}).setdefault(entry.entry_id, {})
    coordinator: TempoDataUpdateCoordinator | None = data.get("coordinator")
    if coordinator is None:
        raise RuntimeError(
            "TempoVision coordinator is missing during button setup. "
            "This may indicate an integration initialization issue. "
            "Try reloading the TempoVision integration from the Home Assistant UI."
        )

    async_add_entities([TempoRefreshButton(coordinator)], True)


class TempoRefreshButton(ButtonEntity):
    """Button entity that triggers an immediate data refresh."""

    def __init__(self, coordinator: TempoDataUpdateCoordinator) -> None:
        self.coordinator = coordinator
        self._attr_name = "TempoVision Actualiser"
        self._attr_unique_id = f"{DOMAIN}_refresh"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "tempovision_service")},
            name="TempoVision",
            manufacturer="Kelwatt Scraper",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    async def async_press(self) -> None:
        # update internal last pressed timestamp so UI shows it
        from homeassistant.util import dt as dt_util

        self._attr_last_pressed = dt_util.utcnow()
        self.async_write_ha_state()

        # request a coordinator update
        await self.coordinator.async_request_refresh()
