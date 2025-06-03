"""API interactions for the M3ierpool integration."""

import re

import requests

from homeassistant.exceptions import HomeAssistantError


class Api:
    """API interactions with M3ierpool."""

    def __init__(self, host, password) -> None:
        """Initialize the Api class for M3ierpool integration."""
        self.host = host
        self.password = password

    def authenticate(self) -> bool:
        """Authenticate with the M3ierpool API."""
        r = requests.get(
            f"http://192.168.178.59/modify?0003={self.password}&x=0&y=0",
            allow_redirects=True,
            timeout=10,
        )
        if r.status_code != 200:
            raise CannotConnect
        if "login.htm" in r.text:
            raise InvalidAuth

    def getStatus(self, text) -> bool:
        """Return False if the heater is off based on the provided text."""
        return "Die Heizung ist aus" not in text

    def getTemperatures(self, text) -> float:
        """Extract and return the current and target water temperatures from the provided HTML text."""
        tempregex = re.compile(
            r"""Wassertemperatur .*[\s<>A-z=\"0-9:;-]*font-size:64px\">([0-9.]*).*[\s<>A-z=\"0-9:;/-]*color:white\">([0-9.]*)""",
            re.MULTILINE,
        )
        match = tempregex.search(text)
        temperature = float(match.group(1))
        target_temperature = float(match.group(2))
        assert temperature > 0 and temperature < 40
        assert target_temperature > 0 and target_temperature < 40
        return (temperature, target_temperature)

    def getData(self):
        """Retrieve the current status and water temperatures from the M3ierpool device."""
        r = requests.get(f"http://192.168.178.59/", timeout=10)
        text = r.text
        temperatures = self.getTemperatures(text)
        return {
            "status": self.getStatus(text),
            "current_temperature": temperatures[0],
            "target_temperature": temperatures[1],
        }

    def setTargetTemperature(self, target_temperature: float):
        """Set the target water temperature on the M3ierpool device."""
        r = requests.get(
            f"http://192.168.178.59/modify?0110={target_temperature}&x=36&y=32",
            timeout=10,
            allow_redirects=False,
        )
        if "login.htm" in r.text:
            self.authenticate()
            self.setTargetTemperature(target_temperature)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
