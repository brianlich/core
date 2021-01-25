""" Support for SleepIQ sensors """
from homeassistant import config_entries
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.entity import Entity

from . import SleepIQDataUpdateCoordinator, SleepIQDevice
from .const import ATTRIBUTION_TEXT, DOMAIN, ICON, LEFT, RIGHT


async def async_setup_entry(
    hass, config_entry: config_entries.ConfigEntry, async_add_entities
):

    coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    """Set up sensors from a config entry."""
    sensors = []
    sensors.append(SleepNumberSensor(LEFT, coordinator))
    sensors.append(SleepNumberSensor(RIGHT, coordinator))
    async_add_entities(sensors)


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
