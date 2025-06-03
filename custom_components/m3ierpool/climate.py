"""Platform for light integration."""

from __future__ import annotations

import logging
import time

import voluptuous as vol

# Import the device class from the component that you want to support
from .api import Api
from homeassistant.components.climate import (
    PLATFORM_SCHEMA as CLIMATE_PLATFORM_SCHEMA,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = CLIMATE_PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        # vol.Optional(CONF_USERNAME, default="admin"): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    host = config[CONF_HOST]
    password = config.get(CONF_PASSWORD)

    # Setup connection with devices/cloud
    api = Api(host=host, password=password)

    # Verify that passed in configuration works
    if not api.authenticate():
        _LOGGER.error("Could not connect to AwesomeLight hub")
        return

    # Add devices
    add_entities([PoolClimate(api)], update_before_add=True)


class PoolClimate(ClimateEntity):
    """Representation of an Awesome Light."""

    def __init__(self, api: Api) -> None:
        """Initialize an AwesomeLight."""
        self._api = api
        self._attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
        self._attr_temperature_unit = "°C"
        self._attr_hvac_modes = [HVACMode.HEAT]
        self._attr_hvac_mode = HVACMode.HEAT
        self._attr_name = "Pool Heizung"

    def update(self) -> None:
        """Fetch new state data.

        This is the only method that should fetch new data for Home Assistant.
        """
        data = self._api.getData()
        self._attr_current_temperature = data["current_temperature"]
        self._attr_target_temperature = data["target_temperature"]
        self._attr_hvac_action = (
            HVACAction.HEATING if data["status"] else HVACAction.IDLE
        )

    @property
    def current_temperature(self) -> str:
        """Return the display name of this light."""
        return self._attr_current_temperature

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        target_temp = kwargs.get("temperature")
        if target_temp is not None:
            # Assuming the API has a method to set the target temperature
            self._api.setTargetTemperature(target_temp)
            time.sleep(1)
            self.update()

    # @property
    # def is_on(self) -> bool | None:
    #     """Return true if light is on."""
    #     return self._state

    # def update(self) -> None:
    #     """Fetch new state data for this light.

    #     This is the only method that should fetch new data for Home Assistant.
    #     """
    #     self._light.update()
    #     self._state = self._light.is_on()
    #     self._brightness = self._light.brightness
