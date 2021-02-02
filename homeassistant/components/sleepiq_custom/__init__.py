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
SERVICE_SET_FAVORITE_ATTR_NUMBER = "number"
SERVICE_SET_FOOT_WARMING = "set_foot_warming"

from .const import (
    DEVICE_MANUFACTURER,
    DEVICE_NAME,
    DEVICE_SW_VERSION,
    DOMAIN,
    SCAN_INTERVAL,
)

SERVICE_SET_NUMBER_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_SET_FAVORITE_ATTR_SIDE): str,
        vol.Required(SERVICE_SET_FAVORITE_ATTR_NUMBER): int,
    }
)

SERVICE_SET_FOOT_WARMING_SCHEMA = vol.Schema(
    {
        vol.Required(SERVICE_SET_FAVORITE_ATTR_SIDE): cv.string,
        vol.Required("temperature"): cv.string,
    }
)


_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["light", "sensor", "binary_sensor", "switch"]


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

    async def handle_foot_warming(call):
        """ Handle the foot warmer """
        side = call.data.get("side")
        temperature = call.data.get("temperature")
        await coordinator.sleepiq.turn_on_footwarming(side, temperature)

    async def handle_set_sleep_number(call):
        """ Handle the service call to set the Sleep Number for specific side """
        side = call.data.get("side", "")
        number_to_set = call.data.get("sleep_number", "")

        set_sleep_number(side, number_to_set)

    async def handle_set_favorite_sleep_number(call):
        """ Handle the service call to set the Sleep Number favorite for a specific side """
        side = call.data.get("side", "")
        number_to_set = call.data.get("number", "")

        await set_favorite_sleep_number(side, number_to_set)

    async def set_favorite_sleep_number(side, number_to_set):
        """ Set the favorite sleep number for a specific side"""
        if side is None:
            _LOGGER.error("You must specify a side when setting the sleep number")
        else:
            _LOGGER.error("This is were we set the favorite sleep number")
            await coordinator.sleepiq.set_favorite_sleepnumber(side, number_to_set)

    async def set_sleep_number(side, number_to_set):
        """ Set the sleep number for a specific side"""
        if side is None:
            _LOGGER.error("You must specify a side when setting the sleep number")

        if 0 < int(number_to_set) <= 100 and int(number_to_set) % 5 == 0:
            _LOGGER.error("This is were we set the sleep number")
            # await coordinator.sleepiq.set_sleepnumber(side, number_to_set)
        else:
            message = f"Invalid sleep number: {number_to_set}. The new sleep number must be a multiple of 5 between 5 and 100"
            _LOGGER.error(message)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_FOOT_WARMING,
        handle_foot_warming,
        schema=SERVICE_SET_FOOT_WARMING_SCHEMA,
    )

    # hass.services.register(DOMAIN, SERVICE_SET_SLEEP_NUMBER, handle_set_sleep_number)

    # hass.services.register(
    #     DOMAIN,
    #     SERVICE_SET_FAVORITE,
    #     handle_set_favorite_sleep_number,
    #     schema=SERVICE_SET_NUMBER_SCHEMA,
    # )

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

    # def update_listeners(self) -> None:
    #     """Call update on all listeners."""
    #     for update_callback in self._listeners:
    #         update_callback()

    async def _async_update_data(self) -> Bed:
        """Fetch data from API endpoint."""
        try:
            _LOGGER.debug("Fetching data")
            if self.sleepiq._key is None:
                await self.sleepiq.login()
            return await self.sleepiq.fetch_homeassistant_data()
        except Exception as e:
            message = "SleepIQ failed to login, double check your username and password"
            _LOGGER.error(message)
            _LOGGER.error(e)


class SleepIQDevice(CoordinatorEntity):
    def __init__(
        self,
        coordinator: SleepIQDataUpdateCoordinator,
    ):
        """Initialize the SleepIQ entity."""
        self._coordinator = coordinator
        super().__init__(coordinator)

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information about this Sleep IQ device."""
        return {
            "identifiers": {(DOMAIN, "sleepiq-device")},
            "name": DEVICE_NAME,
            "manufacturer": DEVICE_MANUFACTURER,
            "model": self._coordinator.data.model,
            "sw_version": DEVICE_SW_VERSION,
        }
