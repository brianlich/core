""" Support for SleepIQ sensors """
import logging

from homeassistant import config_entries
from homeassistant.components.light import LightEntity, SUPPORT_BRIGHTNESS
from homeassistant.const import ATTR_ATTRIBUTION

from . import SleepIQDataUpdateCoordinator, SleepIQDevice
from .const import ATTRIBUTION_TEXT, DOMAIN

RIGHT_NIGHT_STAND = 1
LEFT_NIGHT_STAND = 2
RIGHT_NIGHT_LIGHT = 3
LEFT_NIGHT_LIGHT = 4

BED_LIGHTS = [RIGHT_NIGHT_STAND, LEFT_NIGHT_STAND, RIGHT_NIGHT_LIGHT, LEFT_NIGHT_LIGHT]

__LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, config_entry: config_entries.ConfigEntry, async_add_entities
):
    """Set up a bed from a config entry."""
    coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    lights = []
    if coordinator.data.light1 is not None:
        lights.append(SleepIQNightLight(coordinator, 1))

    if coordinator.data.light2 is not None:
        lights.append(SleepIQNightLight(coordinator, 2))

    if coordinator.data.light3 is not None:
        lights.append(SleepIQNightLight(coordinator, 3))

    if coordinator.data.light4 is not None:
        lights.append(SleepIQNightLight(coordinator, 4))

    async_add_entities(lights)


class SleepIQNightLight(LightEntity, SleepIQDevice):
    """ Representation of a light """

    def __init__(
        self,
        coordinator: SleepIQDataUpdateCoordinator,
        outletID: int,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._outletid = outletID
        self._name = None
        self._brightness = self._coordinator.data.foundation.fsLeftUnderbedLightPWM
        self._unique_id = (
            DOMAIN + "_" + self._coordinator.data.bedId + "_light_" + str(outletID)
        )

        if self._outletid == 1:
            self._is_on = bool(self._coordinator.data.light1.setting)
            self._name = self._coordinator.data.light1.name
            # __LOGGER.debug("Found a light: " + str(outletID))
        elif self._outletid == 2:
            self._is_on = bool(self._coordinator.data.light2.setting)
            self._name = self._coordinator.data.light2.name
            # __LOGGER.debug("Found a light: " + str(outletID))
        elif self._outletid == 3:
            self._is_on = bool(self._coordinator.data.light3.setting)
            self._name = self._coordinator.data.light3.name
            # __LOGGER.debug("Found a light: " + str(outletID))
        elif self._outletid == 4:
            self._is_on = bool(self._coordinator.data.light4.setting)
            self._name = self._coordinator.data.light4.name
            # __LOGGER.debug("Found a light: " + str(outletID))
        else:
            self._name = ""

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    # @property
    # def state(self):
    #     """Return the name of the sensor."""
    #     return self._state

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return True

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            "bedId": self._coordinator.data.bedId,
            ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
        }

    @property
    def is_on(self):
        """Return True if device is on."""
        return self._is_on

    @property
    def brightness(self):
        """Return True if device is on."""
        return self._brightness

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        flags = SUPPORT_BRIGHTNESS
        return flags

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        await self._coordinator.sleepiq.turn_on_light(self._outletid)
        # self._coordinator.data.light3.setting = 1
        await self._coordinator.async_request_refresh()
        self._is_on = True
        # self._state = True

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        await self._coordinator.sleepiq.turn_off_light(self._outletid)
        # self._coordinator.data.light3.setting = 0
        await self._coordinator.async_request_refresh()
        # self._state = False
        self._is_on = False

    # async def async_update(self):
    #     """Call when forcing a refresh of the device."""
    #     self._is_on = self._coordinator.sleepiq.get_light_status(self._outletid)
