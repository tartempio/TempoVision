"""Config flow for TempoVision integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    DOMAIN,
    CONF_SEPARATE_PROB_ENTITIES,
    CONF_SOURCE,
    DEFAULT_SEPARATE_PROB_ENTITIES,
    DEFAULT_SOURCE,
    SOURCE_KELWATT,
    SOURCE_OPEN_DPE,
)

class TempoVisionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for TempoVision."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="TempoVision",
                data={},
                options={
                    CONF_SOURCE: user_input.get(CONF_SOURCE, DEFAULT_SOURCE),
                    CONF_SEPARATE_PROB_ENTITIES: user_input.get(
                        CONF_SEPARATE_PROB_ENTITIES, DEFAULT_SEPARATE_PROB_ENTITIES
                    ),
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SOURCE,
                        default=DEFAULT_SOURCE,
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[SOURCE_OPEN_DPE, SOURCE_KELWATT],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            translation_key=CONF_SOURCE,
                        )
                    ),
                    vol.Optional(
                        CONF_SEPARATE_PROB_ENTITIES,
                        default=DEFAULT_SEPARATE_PROB_ENTITIES,
                    ): selector.BooleanSelector(),
                }
            ),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        _config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return TempoVisionOptionsFlowHandler()


class TempoVisionOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for TempoVision."""

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(
                title="",
                data={
                    CONF_SOURCE: user_input.get(
                        CONF_SOURCE,
                        self.config_entry.options.get(
                            CONF_SOURCE,
                            self.config_entry.data.get(CONF_SOURCE, DEFAULT_SOURCE),
                        ),
                    ),
                    CONF_SEPARATE_PROB_ENTITIES: user_input.get(
                        CONF_SEPARATE_PROB_ENTITIES,
                        self.config_entry.options.get(
                            CONF_SEPARATE_PROB_ENTITIES,
                            DEFAULT_SEPARATE_PROB_ENTITIES,
                        ),
                    ),
                },
            )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SOURCE,
                        default=self.config_entry.options.get(
                            CONF_SOURCE,
                            self.config_entry.data.get(CONF_SOURCE, DEFAULT_SOURCE),
                        ),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[SOURCE_OPEN_DPE, SOURCE_KELWATT],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                            translation_key=CONF_SOURCE,
                        )
                    ),
                    vol.Optional(
                        CONF_SEPARATE_PROB_ENTITIES,
                        default=self.config_entry.options.get(
                            CONF_SEPARATE_PROB_ENTITIES,
                            DEFAULT_SEPARATE_PROB_ENTITIES,
                        ),
                    ): selector.BooleanSelector(),
                }
            ),
        )
