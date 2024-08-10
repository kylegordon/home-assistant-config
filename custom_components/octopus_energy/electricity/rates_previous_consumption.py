import logging

from homeassistant.core import HomeAssistant, callback

from homeassistant.components.event import (
    EventEntity,
    EventExtraStoredData,
)
from homeassistant.helpers.restore_state import RestoreEntity

from .base import (OctopusEnergyElectricitySensor)
from ..utils.attributes import dict_to_typed_dict
from ..const import EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES

_LOGGER = logging.getLogger(__name__)

class OctopusEnergyElectricityPreviousConsumptionRates(OctopusEnergyElectricitySensor, EventEntity, RestoreEntity):
  """Sensor for displaying the previous consumption's rates."""

  def __init__(self, hass: HomeAssistant, meter, point):
    """Init sensor."""
    # Pass coordinator to base class
    OctopusEnergyElectricitySensor.__init__(self, hass, meter, point, "event")

    self._hass = hass
    self._state = None
    self._last_updated = None

    self._attr_event_types = [EVENT_ELECTRICITY_PREVIOUS_CONSUMPTION_RATES]

  @property
  def unique_id(self):
    """The id of the sensor."""
    return f"octopus_energy_electricity_{self._serial_number}_{self._mpan}{self._export_id_addition}_previous_consumption_rates"
    
  @property
  def name(self):
    """Name of the sensor."""
    return f"Previous Consumption Rates {self._export_name_addition}Electricity ({self._serial_number}/{self._mpan})"
  
  @property
  def entity_registry_enabled_default(self) -> bool:
    """Return if the entity should be enabled when first added.

    This only applies when fist added to the entity registry.
    """
    return False

  async def async_added_to_hass(self):
    """Call when entity about to be added to hass."""
    # If not None, we got an initial value.
    await super().async_added_to_hass()
    
    self._hass.bus.async_listen(self._attr_event_types[0], self._async_handle_event)

  async def async_get_last_event_data(self):
    data = await super().async_get_last_event_data()
    return EventExtraStoredData.from_dict({
      "last_event_type": data.last_event_type,
      "last_event_attributes": dict_to_typed_dict(data.last_event_attributes),
    })

  @callback
  def _async_handle_event(self, event) -> None:
    if (event.data is not None and "mpan" in event.data and event.data["mpan"] == self._mpan and "serial_number" in event.data and event.data["serial_number"] == self._serial_number):
      self._trigger_event(event.event_type, event.data)
      self.async_write_ha_state()