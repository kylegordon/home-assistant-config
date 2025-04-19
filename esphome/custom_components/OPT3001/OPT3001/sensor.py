import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import i2c, sensor
from esphome.const import (
    CONF_ID,
    CONF_ILLUMINANCE,
    CONF_TEMPERATURE,
    DEVICE_CLASS_ILLUMINANCE,
    ICON_EMPTY,
    STATE_CLASS_MEASUREMENT,
    UNIT_LUX,

)

DEPENDENCIES = ["i2c"]

opt3001_ns = cg.esphome_ns.namespace("opt3001")
OPT3001Component = opt3001_ns.class_(
    "OPT3001Component", cg.PollingComponent, i2c.I2CDevice
)

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(OPT3001Component),
            cv.Required(CONF_ILLUMINANCE): sensor.sensor_schema(
                unit_of_measurement=UNIT_LUX,
                icon=ICON_EMPTY,
                accuracy_decimals=1,
                device_class=DEVICE_CLASS_ILLUMINANCE,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
           
        }
    )
    .extend(cv.polling_component_schema("5s"))
    .extend(i2c.i2c_device_schema(0x45))
)
async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await i2c.register_i2c_device(var, config)

    if CONF_ILLUMINANCE in config:
        sens = await sensor.new_sensor(config[CONF_ILLUMINANCE])
        cg.add(var.set_ambient_light_sensor(sens))
