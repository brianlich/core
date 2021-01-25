"""Constants for the SleepIQ Custom integration."""

from datetime import timedelta


ATTRIBUTION_TEXT = "Data provided by SleepIQ"
DEVICE_MANUFACTURER = "Sleep Number"
DEVICE_NAME = "Smart Bed 360"
DEVICE_SW_VERSION = "1.0"
DOMAIN = "sleepiq_custom"
ICON = "mdi:bed"
IS_IN_BED = "is in bed"
LEFT = "left"
RIGHT = "right"
SCAN_INTERVAL = timedelta(seconds=30)
SIDES = [LEFT, RIGHT]
SLEEP_NUMBER = "Sleep Number"
SERVICE_SET_SLEEP_NUMBER = "set_sleep_number"
SERVICE_SET_FAVORITE = "set_favorite_sleep_number"