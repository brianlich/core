""" Support for SleepIQ sensors """
import logging

from sleepi.models import Light

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
    # coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    # lights = []

    # for light in coordinator.data.lights:
    #     if light is not None:
    #         lights.append(SleepIQNightLight(coordinator, light))

    # if coordinator.data.light2 is not None:
    #     lights.append(SleepIQNightLight(coordinator, 2))

    # if coordinator.data.light3 is not None:
    #     lights.append(SleepIQNightLight(coordinator, 3))

    # if coordinator.data.light4 is not None:
    #     lights.append(SleepIQNightLight(coordinator, 4))

    # async_add_entities(lights)


class SleepIQNightLight(LightEntity, SleepIQDevice):
    """ Representation of a light """

    def __init__(
        self,
        coordinator: SleepIQDataUpdateCoordinator,
        light: Light,
    ):
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._light = light
        self._name = self._light.name
        self._brightness = self._coordinator.data.foundation.fsLeftUnderbedLightPWM
        self._name = self._light.name
        self._is_on = self._light.setting
        # self._unique_id = (
        self._unique_id = (
            f"{DOMAIN}_{self._coordinator.data.bedId}_light_{str(self._light.outlet)}"
        )
        #     + "_"
        #     + self._coordinator.data.bedId
        #     + "_light_"
        #     + str(self._light.outlet)
        # )

        # self._name = self._light.name
        # self._is_on = self._light.setting

        # x = 0
        # for light in self._coordinator.data.lights:
        #     if light is not None:
        # self._name = self._coordinator.data.lights[self._outletid - 1].name
        # self._is_on = self._coordinator.data.lights[self._outletid - 1].setting
        # x += 1

        # if self._outletid == 1:
        #     self._is_on = bool(self._coordinator.data.light1.setting)
        #     self._name = self._coordinator.data.light1.name
        #     # __LOGGER.debug("Found a light: " + str(outletID))
        # elif self._outletid == 2:
        #     self._is_on = bool(self._coordinator.data.light2.setting)
        #     self._name = self._coordinator.data.light2.name
        #     # __LOGGER.debug("Found a light: " + str(outletID))
        # elif self._outletid == 3:
        #     self._is_on = bool(self._coordinator.data.light3.setting)
        #     self._name = self._coordinator.data.light3.name
        #     # __LOGGER.debug("Found a light: " + str(outletID))
        # elif self._outletid == 4:
        #     self._is_on = bool(self._coordinator.data.light4.setting)
        #     self._name = self._coordinator.data.light4.name
        #     # __LOGGER.debug("Found a light: " + str(outletID))
        # else:
        #     self._name = ""
        #     __LOGGER.debug(f"Found an unknown light with outletID: {outletID}")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

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
        await self._coordinator.sleepiq.turn_on_light(self._light.outlet)
        await self._coordinator.async_request_refresh()
        self._coordinator.data.lights[self._light.outlet - 1].setting = True
        # self._is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        self._coordinator.data.lights[self._light.outlet - 1].setting = False
        await self._coordinator.sleepiq.turn_off_light(self._light.outlet)
        await self._coordinator.async_request_refresh()
        # self._is_on = False
        self.async_write_ha_state()
