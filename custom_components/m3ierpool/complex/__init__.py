"""The M3ier Pool integration."""

from __future__ import annotations

from Api import Api

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant

# List the platforms that you want to support.
_PLATFORMS: list[Platform] = [Platform.CLIMATE]

# Create ConfigEntry type alias with API object
type M3ierpoolConfigEntry = ConfigEntry[Api]


# Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: M3ierpoolConfigEntry) -> bool:
    """Set up M3ier Pool from a config entry."""

    # 1. Create API instance
    api = Api(host=entry.data[CONF_HOST], password=entry.data[CONF_PASSWORD])
    # 2. Validate the API connection (and authentication)
    api.authenticate()
    # 3. Store an API object for your platforms to access
    entry.runtime_data = api

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


# Update entry annotation
async def async_unload_entry(hass: HomeAssistant, entry: M3ierpoolConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
