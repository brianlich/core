"""Support for SleepIQ custom binary sensors."""

from homeassistant import config_entries
from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_OCCUPANCY,
    BinarySensorEntity,
)
from homeassistant.const import ATTR_ATTRIBUTION

from . import SleepIQDataUpdateCoordinator, SleepIQDevice
from .const import ATTRIBUTION_TEXT, DOMAIN, ICON, IS_IN_BED, LEFT, RIGHT


async def async_setup_entry(
    hass, config_entry: config_entries.ConfigEntry, async_add_entities
):
    coordinator: SleepIQDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    """Set up the binary sensors"""
    binary_sensors = []
    binary_sensors.append(IsInBedBinarySensor(LEFT, coordinator))
    binary_sensors.append(IsInBedBinarySensor(RIGHT, coordinator))
    binary_sensors.append(SleepNumberConnectivityBinarySensor(coordinator))
    async_add_entities(binary_sensors)


class IsInBedBinarySensor(SleepIQDevice, BinarySensorEntity):
    """Implementation of a SleepIQ presence sensor."""

    def __init__(self, side, coordinator: SleepIQDataUpdateCoordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._side = side
        self._unique_id = (
            DOMAIN + "_" + self._coordinator.data.bedId + "_" + self._side + "is_in_bed"
        )
        self._is_on = (
            self._coordinator.data.left_side.isInBed
            if self._side.lower() == "left"
            else self._coordinator.data.right_side.isInBed
        )

    @property
    def name(self):
        """ Return the name of the sensor """
        if self._side is LEFT:
            if self._coordinator.data.left_side.sleeper.firstName is None:
                return self._side + " side " + IS_IN_BED
            return self._coordinator.data.left_side.sleeper.firstName + " " + IS_IN_BED
        else:
            if self._coordinator.data.right_side.sleeper.firstName is None:
                return self._side + " side " + IS_IN_BED
            return self._coordinator.data.right_side.sleeper.firstName + " " + IS_IN_BED

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self):
        """Return the status of the sensor."""
        return self._is_on

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_OCCUPANCY

    @property
    def icon(self):
        """Return the class of this sensor."""
        return ICON

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        if self._side is LEFT:
            thisdict = {
                "bedId": self._coordinator.data.left_side.sleeper.bedId,
                "firstName": self._coordinator.data.left_side.sleeper.firstName,
                "sleeperId": self._coordinator.data.left_side.sleeper.sleeperId,
                ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
            }
        else:
            thisdict = {
                "bedId": self._coordinator.data.right_side.sleeper.bedId,
                "firstName": self._coordinator.data.right_side.sleeper.firstName,
                "sleeperId": self._coordinator.data.right_side.sleeper.sleeperId,
                ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
            }

        return thisdict


class SleepNumberConnectivityBinarySensor(SleepIQDevice, BinarySensorEntity):
    """Implementation of a SleepIQ presence sensor."""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._coordinator = coordinator
        self._name = "Sleep Number online sensor"
        self._is_on = self._coordinator.data.status
        self._unique_id = (
            DOMAIN + "_" + self._coordinator.data.bedId + "_connectivity_binary_sensor"
        )

    @property
    def name(self):
        """ Name """
        return self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def is_on(self):
        """Return the status of the sensor."""
        return self._is_on

    @property
    def device_class(self):
        """Return the class of this sensor."""
        return DEVICE_CLASS_CONNECTIVITY

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        return {
            "name": self._coordinator.data.name,
            "registrationDate": self._coordinator.data.registrationDate,
            "bedId": self._coordinator.data.bedId,
            "macAddress": self._coordinator.data.macAddress,
            "serial": self._coordinator.data.serial,
            "status": self._coordinator.data.status,
            "sku": self._coordinator.data.sku,
            "version": self._coordinator.data.version,
            ATTR_ATTRIBUTION: ATTRIBUTION_TEXT,
        }
