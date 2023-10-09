"""Sensor to collect the tariff rates of Bulb Energy Ltd in the UK."""
from __future__ import annotations

import json
import requests
import statistics
import voluptuous as vol
from datetime import timedelta

import logging
from random import randint
from typing import Any

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

CONF_POSTCODE = 'postcode'
CONF_PAYPLAN = 'payplan'
CONF_ECO7 = 'eco7'

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_POSTCODE): cv.string,
    vol.Optional(CONF_PAYPLAN, default="monthly"): cv.string,
    vol.Optional(CONF_ECO7, default=False): cv.boolean
})

# Check every 12 hours
SCAN_INTERVAL = timedelta(hours=12)

mutation = """ 
query Tariffs($postcode: String!, $monthly: Boolean!, $legacyPrepay: Boolean!, $smartPayg: Boolean!, $eco7: Boolean!) {
  tariffs(postcode: $postcode) {
    residential {
      electricity {
        credit @include(if: $monthly) {
          standard @skip(if: $eco7) {
            ...StandardElectricityTariff
            __typename
          }
          economy7 @include(if: $eco7) {
            ...Eco7ElectricityTariff
            __typename
          }
          __typename
        }
        prepay @include(if: $legacyPrepay) {
          standard @skip(if: $eco7) {
            ...StandardElectricityTariff
            __typename
          }
          economy7 @include(if: $eco7) {
            ...Eco7ElectricityTariff
            __typename
          }
          __typename
        }
        smartPayg @include(if: $smartPayg) {
          standard @skip(if: $eco7) {
            ...StandardElectricityTariff
            __typename
          }
          economy7 @include(if: $eco7) {
            ...Eco7ElectricityTariff
            __typename
          }
          __typename
        }
        __typename
      }
      __typename
    }
    __typename
  }
}

fragment StandardElectricityTariff on ResidentialElectricityStandardTariff {
  fuel
  postcode
  paymentMethod
  standingCharge
  unitRates {
    standard
    __typename
  }
  __typename
}

fragment Eco7ElectricityTariff on ResidentialElectricityEconomy7Tariff {
  fuel
  postcode
  paymentMethod
  standingCharge
  unitRates {
    day
    night
    __typename
  }
  __typename
}
""".strip()

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    postcode = config['postcode']
    eco7 = config['eco7']
    payplan = config['payplan']
    add_entities([BulbEnergySensor(postcode, eco7, payplan)])

def get_live_kWhs_from_Bulb(postcode: str, eco7: bool, payplan = str):
    """
    scrapes the current GBP per kWH from the Bulb webpages tarrif, with selected options
    """
    resp = makequery(postcode, eco7, payplan)

    pence_per_kWH = float(parserates(resp))
    GBP_per_kWH = pence_per_kWH/100

    return GBP_per_kWH

def makequery(postcode: str, eco7: bool, payplan: str) -> dict:
    """Makes a query against the Bulb GraphQL database

    :param payplan: One of `legacyPrepay`, `smartPayg`, `monthly`.

    :returns: Decoded JSON response of GraphQL
    """
    url = "https://join-gateway.bulb.co.uk/graphql"
    opname = "Tariffs"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
        "x-bulb-session": "15630c9a-577d-45da-a8ed",
        "content-type": "application/json",
        "Origin": "https://bulb.co.uk",
        "TE": "Trailers",
    }

    variables = {
        "postcode": postcode,
        "eco7": eco7,
        "legacyPrepay": False,
        "smartPayg": False,
        "monthly": True,
    }

    assert payplan in variables
    variables[payplan] = True

    query = dict(variables=variables, query=mutation, operationName=opname)

    resp = requests.post(url, json=query, headers=headers)

    if 200 <= resp.status_code < 300:
        return resp.json()
    else:
        raise Exception("Bad Request.")

def parserates(jsonresp: dict) -> float:
    """
    Extracts kWatt hour rates from json dictionary
    """

    rates = jsonresp["data"]["tariffs"]["residential"]["electricity"]["credit"]
    if "standard" in rates:
        # no day night average
        return rates["standard"][0]["unitRates"]["standard"]
    else:
        # average day and night
        unitRates = rates["economy7"][0]["unitRates"]
        return statistics.mean([unitRates["day"], unitRates["night"]])

class BulbEnergySensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, postcode, eco7, payplan):
        """Initialize the sensor."""
        self._postcode = postcode
        self._eco7 = eco7
        self._payplan = payplan
        self._state = None

        # Gather data on startup. SCAN_INTERVAL is 12 hours
        self.update()

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'kWh Rate'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return '£/kWh'

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """
        _LOGGER.info("in update")
        print("in update. Querying: " + self._postcode, self._eco7, self._payplan)
        self._state = get_live_kWhs_from_Bulb(self._postcode, self._eco7, self._payplan)
