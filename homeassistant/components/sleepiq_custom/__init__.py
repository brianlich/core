"""The SleepIQ Custom integration."""
import asyncio
import logging
import voluptuous as vol
from typing import Any, Dict

from sleepi.models import Bed
from sleepi.sleepiq import SleepIQ

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

SERVICE_SET_SLEEP_NUMBER = "set_sleep_number"
SERVICE_SET_FAVORITE = "set_favorite_sleep_number"
SERVICE_SET_FAVORITE_ATTR_SIDE = "side"
SERVICE_SET_FAVORITE_ATTR_NUMBER = "sleep_number"
SERVICE_SET_FOOT_WARMING = "set_foot_warming"
SERVICE_SET_FOOT_WARMING_ATTR_TEMP = "temperature"
SERVICE_SET_LIGHT_BRIGHTNESS = "set_light_brightness"
SERVICE_SET_LIGHT_BRIGHTNESS_ATTR_BRIGHTNESS = "brightness"

from .const import (
    DEVICE_MANUFACTURER,
    DEVICE_NAME,
    DEVICE_SW_VERSION,
    DOMAIN,
    SCAN_INTERVAL,
)

SERVICE_SET_NUMBER_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_SET_FAVORITE_ATTR_SIDE): cv.string,
        vol.Required(SERVICE_SET_FAVORITE_ATTR_NUMBER): cv.positive_int,
    }
)

SERVICE_SET_FOOT_WARMING_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_SET_FAVORITE_ATTR_SIDE): cv.string,
        vol.Required(SERVICE_SET_FOOT_WARMING_ATTR_TEMP): cv.string,
    }
)

SERVICE_SET_NUMBER_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_SET_FAVORITE_ATTR_SIDE): cv.string,
        vol.Required(SERVICE_SET_FAVORITE_ATTR_NUMBER): cv.positive_int,
    }
)

SERVICE_SET_BRIGHTNESS_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_SET_LIGHT_BRIGHTNESS_ATTR_BRIGHTNESS): cv.string,
    }
)


_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor", "binary_sensor", "switch"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the SleepIQ Custom component."""
    return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up SleepIQ Custom from a config entry."""

    coordinator = SleepIQDataUpdateCoordinator(hass, config_entry=config_entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    async def handle_set_light_brightness(call):
        """ Handle the foot warmer service call """
        brightness: str = call.data.get("brightness")
        _LOGGER.debug(f"Setting the brightness of the underbed light to {brightness}")
        return await coordinator.sleepiq.set_light_brightness(brightness)

    async def handle_foot_warming(call):
        """ Handle the foot warmer service call """
        side = call.data.get("side")
        temperature = call.data.get("temperature")

        if temperature.lower() == "off":
            _LOGGER.debug(f"Turning off the {side} foot warmer")
            return await coordinator.sleepiq.turn_off_foot_warming(side)
        else:
            _LOGGER.debug(
                f"Turning on the {side} foot warmer and setting it to {temperature}"
            )
            return await coordinator.sleepiq.turn_on_foot_warming(side, temperature)

    async def handle_set_sleep_number(call):
        """ Handle the service call to set the Sleep Number for specific side """
        side = call.data.get("side", "")
        number_to_set = call.data.get("sleep_number", "")

        if 0 < int(number_to_set) <= 100 and int(number_to_set) % 5 == 0:
            _LOGGER.error(f"Setting the {side} side Sleep Number to {number_to_set}.")
            await coordinator.sleepiq.set_sleepnumber(side, number_to_set)
        else:
            _LOGGER.error(
                f"Invalid sleep number: {number_to_set}. The new sleep number must be a multiple of 5 between 5 and 100"
            )

    async def handle_set_favorite_sleep_number(call):
        """ Handle the service call to set the Sleep Number favorite for a specific side """
        side = call.data.get("side", "")
        number_to_set = call.data.get("sleep_number", "")

        if side is None:
            _LOGGER.error("You must specify a side when setting the sleep number")

        if 0 < int(number_to_set) <= 100 and int(number_to_set) % 5 == 0:
            _LOGGER.error(
                f"This is were we set the favorite sleep number to {number_to_set}"
            )
            await coordinator.sleepiq.set_favorite_sleepnumber(side, number_to_set)
        else:
            _LOGGER.error(
                f"Invalid sleep number: {number_to_set}. The new sleep number must be a multiple of 5 between 5 and 100"
            )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FOOT_WARMING,
        handle_foot_warming,
        schema=SERVICE_SET_FOOT_WARMING_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_SLEEP_NUMBER,
        handle_set_sleep_number,
        schema=SERVICE_SET_NUMBER_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FAVORITE,
        handle_set_favorite_sleep_number,
        schema=SERVICE_SET_NUMBER_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_LIGHT_BRIGHTNESS,
        handle_set_light_brightness,
        schema=SERVICE_SET_NUMBER_SCHEMA,
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    username = entry.title
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        _LOGGER.debug("Unloaded entry for %s", username)

    if not hass.data[DOMAIN]:
        del hass.data[DOMAIN]

    return unload_ok


class SleepIQDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching SleepIQ data."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry):
        """Initialize global SleepIQ data updater."""

        config = config_entry.data
        username = config["username"]
        password = config["password"]
        websession = async_get_clientsession(hass)
        self.sleepiq = SleepIQ(username, password, websession)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> Bed:
        """Fetch data from API endpoint."""
        data = None
        try:
            _LOGGER.debug("Fetching data")
            if self.sleepiq._key is None:
                await self.sleepiq.login()
            data = await self.sleepiq.fetch_homeassistant_data()
            if data is not None:
                return data
        except Exception as e:
            message = (
                f"SleepIQ failed to login, double check your username and password. {e}"
            )
            _LOGGER.error(message)


class SleepIQDevice(CoordinatorEntity):
    """ Represents a base SleepIQ device """

    def __init__(
        self,
        coordinator: SleepIQDataUpdateCoordinator,
    ):
        """Initialize the SleepIQ entity."""
        self._coordinator = coordinator
        super().__init__(coordinator)

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information about the Sleep IQ device"""
        return {
            "identifiers": {(DOMAIN, self._coordinator.data.bedId)},
            "name": self._coordinator.data.name,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": self._coordinator.data.model,
            "sw_version": DEVICE_SW_VERSION,
        }
