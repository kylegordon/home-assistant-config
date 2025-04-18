#pragma once

#include "esphome/core/component.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/i2c/i2c.h"

namespace esphome {
namespace opt3001 {

class OPT3001Component : public PollingComponent, public i2c::I2CDevice{
 public:
  void set_ambient_light_sensor(sensor::Sensor *ambient_light_sensor) { ambient_light_sensor_ = ambient_light_sensor; }

  void setup() override;
  void dump_config() override;
  float get_setup_priority() const override;
  void update() override;

  protected:
    void configureSensor_();
    sensor::Sensor *ambient_light_sensor_;
    
};
}// Namespace ESP
}// Namespace OPT3001
