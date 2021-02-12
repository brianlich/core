import logging
from typing import Optional
from sleepi.models import Light

import voluptuous as vol
from voluptuous.validators import Boolean
from homeassistant import config_entries
from homeassistant.const import ATTR_ATTRIBUTION, STATE_ON, STATE_OFF
from homeassistant.components.switch import SwitchEntity, DEVICE_CLASS_SWITCH

from . import SleepIQDataUpdateCoordinator, SleepIQDevice
from .const import ATTRIBUTION_TEXT, DOMAIN


_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, config_entry: config_entries.ConfigEntry, async_add_entities
):
    """Set up a bed from a config entry."""
    coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    switches = []

    switches.append(ResponsiveAirSwitch(coordinator, "left"))
    switches.append(ResponsiveAirSwitch(coordinator, "right"))
    switches.append(PrivacyModeSwitch(coordinator))

    for light in coordinator.data.lights:
        if light is not None:
            switches.append(SleepIQNightLight(coordinator, light))

    async_add_entities(switches)


class PrivacyModeSwitch(SleepIQDevice, SwitchEntity):
    """Representation of a SleepIQ responsive air switch."""

    def __init__(self, coordinator: SleepIQDataUpdateCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._unique_id = DOMAIN + "_" + self._coordinator.data.bedId + "_privacy_mode"
        self._name = "Sleep Number privacy mode"
        self._is_on = (
            True if self._coordinator.data.privacy_mode.pauseMode == "on" else False
        )

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._is_on

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_SWITCH

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            "accountId": self._coordinator.data.privacy_mode.accountId,
            "bedId": self._coordinator.data.privacy_mode.bedId,
            "pauseMode": self._coordinator.data.privacy_mode.pauseMode,
            ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
        }

    async def async_turn_on(self):
        """Send the on command."""
        _LOGGER.debug("Turning on privacy mode")
        await self._coordinator.sleepiq.turn_on_privacy_mode()
        self._is_on = True
        self.async_write_ha_state()
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self):
        """Send the off command."""
        _LOGGER.debug("Turning off privacy mode")
        await self._coordinator.sleepiq.turn_off_privacy_mode()
        self._is_on = False
        self.async_write_ha_state()
        await self._coordinator.async_request_refresh()


class ResponsiveAirSwitch(SleepIQDevice, SwitchEntity):
    """Representation of a SleepIQ responsive air switch."""

    def __init__(self, coordinator: SleepIQDataUpdateCoordinator, side):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._side = side
        self._is_on = True
        self._unique_id = (
            DOMAIN
            + "_"
            + self._coordinator.data.bedId
            + "_"
            + self._side
            + "responsive_air"
        )

        if self._side.lower() == "left":
            self._name = (
                self._coordinator.data.left_side.sleeper.firstName + " responsive air"
            )
            self._is_on = self._coordinator.data.responsive_air.leftSideEnabled
        elif self._side.lower() == "right":
            self._name = (
                self._coordinator.data.right_side.sleeper.firstName + " responsive air"
            )
            self._is_on = self._coordinator.data.responsive_air.rightSideEnabled

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self):
        """Get whether the switch is in on state."""
        return self._is_on

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            "adjustmentThreshold": self._coordinator.data.responsive_air.adjustmentThreshold,
            "inBedTimeout": self._coordinator.data.responsive_air.inBedTimeout,
            "leftSideEnabled": self._coordinator.data.responsive_air.leftSideEnabled,
            "rightSideEnabled": self._coordinator.data.responsive_air.rightSideEnabled,
            "outOfBedTimeout": self._coordinator.data.responsive_air.outOfBedTimeout,
            "pollFrequency": self._coordinator.data.responsive_air.pollFrequency,
            "prefSyncState": self._coordinator.data.responsive_air.prefSyncState,
            ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
        }

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_SWITCH

    async def async_turn_on(self, **kwargs):
        """Send the on command."""
        _LOGGER.debug(f"Turning on {self._name}")
        await self._coordinator.sleepiq.turn_on_responsive_air(self._side)
        self._is_on = True
        self.async_write_ha_state()
        await self._coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Send the off command."""
        _LOGGER.debug(f"Turning off {self._name}")
        await self._coordinator.sleepiq.turn_off_responsive_air(self._side)
        self._is_on = False
        self.async_write_ha_state()
        await self._coordinator.async_request_refresh()


class SleepIQNightLight(SwitchEntity, SleepIQDevice):
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
        self._is_on = bool(
            self._coordinator.data.lights[self._light.outlet - 1].setting
        )
        self._unique_id = (
            f"{DOMAIN}_{self._coordinator.data.bedId}_light_{str(self._light.outlet)}"
        )

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
            "setting": self._coordinator.data.lights[self._light.outlet - 1].setting,
            "outletID": self._coordinator.data.lights[self._light.outlet - 1].outlet,
            ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
        }

    @property
    def is_on(self):
        """Return True if device is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        self._coordinator.data.lights[self._light.outlet - 1].setting = 1
        await self._coordinator.sleepiq.turn_on_light(self._light.outlet)
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        self._coordinator.data.lights[self._light.outlet - 1].setting = 0
        await self._coordinator.sleepiq.turn_off_light(self._light.outlet)
        self.async_write_ha_state()
