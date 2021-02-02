""" Support for SleepIQ sensors """
from homeassistant import config_entries
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import entity_platform
import voluptuous as vol

from . import SleepIQDataUpdateCoordinator, SleepIQDevice
from .const import ATTRIBUTION_TEXT, DOMAIN, ICON, LEFT, RIGHT


async def async_setup_entry(
    hass, config_entry: config_entries.ConfigEntry, async_add_entities
):

    coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    """Set up sensors from a config entry."""
    sensors = []
    sensors.append(SleeperSensor(LEFT, coordinator))
    sensors.append(SleeperSensor(RIGHT, coordinator))
    async_add_entities(sensors)


class SleeperSensor(SleepIQDevice, Entity):
    """Implementation of a SleepIQ sensor."""

    def __init__(self, side: str, coordinator: SleepIQDataUpdateCoordinator):
        super().__init__(coordinator)
        self._state = None
        self._side = side
        self._coordinator = coordinator
        self._unique_id = (
            DOMAIN
            + "_"
            + self.coordinator.data.bedId
            + "_"
            + side
            + "_sleep_number_sensor"
        )

    @property
    def name(self):
        """ The name of the device """
        if self._side is LEFT:
            return self._coordinator.data.left_side.sleeper.firstName + " Sleep Number"
        else:
            return self._coordinator.data.right_side.sleeper.firstName + " Sleep Number"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._side is LEFT:
            return self._coordinator.data.left_side.sleepNumber
        else:
            return self._coordinator.data.right_side.sleepNumber

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        if self._side is LEFT:
            return {
                "sleeper": self._coordinator.data.left_side.sleeper.firstName,
                "isInBed": self._coordinator.data.left_side.isInBed,
                "favorite": self._coordinator.data.left_side.sleeper.favorite,
                "responsive_air": "on"
                if self._coordinator.data.responsive_air.leftSideEnabled
                else "off",
                "foot_warming": "off"
                if self._coordinator.data.foot_warming.footWarmingStatusLeft == 0
                else "on",
                "side": "left"
                if self._coordinator.data.left_side.sleeper.side == 0
                else "right",
                "sleepGoal": self._coordinator.data.left_side.sleeper.sleepGoal,
                "birthMonth": self._coordinator.data.left_side.sleeper.birthMonth,
                "birthYear": self._coordinator.data.left_side.sleeper.birthYear,
                "height": self._coordinator.data.left_side.sleeper.height,
                "weight": self._coordinator.data.left_side.sleeper.weight,
                "firstSessionRecorded": self._coordinator.data.left_side.sleeper.firstSessionRecorded,
                "lastLogin": self._coordinator.data.left_side.sleeper.lastLogin,
                "sleeperID": self._coordinator.data.sleeperLeftId,
                ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
            }
        else:
            return {
                "sleeper": self._coordinator.data.right_side.sleeper.firstName,
                "isInBed": self._coordinator.data.right_side.isInBed,
                "favorite": self._coordinator.data.right_side.sleeper.favorite,
                "responsive_air": "on"
                if self._coordinator.data.responsive_air.rightSideEnabled
                else "off",
                "foot_warming": "off"
                if self._coordinator.data.foot_warming.footWarmingStatusRight == 0
                else "on",
                "side": "left"
                if self._coordinator.data.left_side.sleeper.side == 0
                else "right",
                "sleepGoal": self._coordinator.data.right_side.sleeper.sleepGoal,
                "birthMonth": self._coordinator.data.right_side.sleeper.birthMonth,
                "birthYear": self._coordinator.data.right_side.sleeper.birthYear,
                "height": self._coordinator.data.right_side.sleeper.height,
                "weight": self._coordinator.data.right_side.sleeper.weight,
                "firstSessionRecorded": self._coordinator.data.right_side.sleeper.firstSessionRecorded,
                "lastLogin": self._coordinator.data.right_side.sleeper.lastLogin,
                "sleeperID": self._coordinator.data.sleeperRightId,
                ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
            }


class SleepNumberSensor(SleepIQDevice, Entity):
    """Implementation of a SleepIQ sensor."""

    def __init__(self, side: str, coordinator: SleepIQDataUpdateCoordinator):
        super().__init__(coordinator)
        self._state = None
        self._side = side
        self._coordinator = coordinator
        self._unique_id = (
            DOMAIN
            + "_"
            + self.coordinator.data.bedId
            + "_"
            + side
            + "_sleep_number_sensor"
        )

    @property
    def name(self):
        """ The name of the device """
        if self._side is LEFT:
            return self._coordinator.data.left_side.sleeper.firstName + " Sleep Number"
        else:
            return self._coordinator.data.right_side.sleeper.firstName + " Sleep Number"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._side is LEFT:
            return self._coordinator.data.left_side.sleepNumber
        else:
            return self._coordinator.data.right_side.sleepNumber

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        if self._side is LEFT:
            return {
                "sleeperID": self._coordinator.data.sleeperLeftId,
                ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
            }
        else:
            return {
                "sleeperID": self._coordinator.data.sleeperRightId,
                ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
            }
