"""Config flow for SleepIQ Custom integration."""
import logging

from aiohttp.client import ClientSession
from sleepi.sleepiq import SleepIQ
import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.components import sleepiq

from .const import DOMAIN  # pylint:disable=unused-import

__LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({"username": str, "password": str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    username = data["username"]
    password = data["password"]

    async with ClientSession() as websession:
        api = SleepIQ(username, password, websession)
        login = await api.login()

    if login:
        return {"title": username}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SleepIQ Custom."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect as err:
            errors["base"] = "cannot_connect"
            err_msg = str(err)
        except InvalidAuth as err:
            errors["base"] = "invalid_auth"
            err_msg = str(err)
        except ValueError as err:
            errors["base"] = "invalid_auth"
            err_msg = str(err)
        except Exception as err:  # pylint: disable=broad-except
            __LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
            err_msg = str(err)
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        __LOGGER.error(err_msg)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
