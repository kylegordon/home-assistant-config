#include "OPT3001.h"
#include "ClosedCube_OPT3001.h"
#include "esphome/core/log.h"

namespace esphome {
namespace opt3001 {

static const char *const TAG = "opt3001";

  ClosedCube_OPT3001 myself;
  
  void OPT3001Component::setup () {
    myself.begin(0x44);
    delay(100);
    configureSensor_();
    delay(100);
    myself.readManufacturerID();
    myself.readDeviceID();
  }

  // Most of this copied from https://github.com/closedcube/ClosedCube_OPT3001_Arduino/blob/master/examples/opt3001demo/opt3001demo.ino
  // I have no real idea what I'm doing.
  void OPT3001Component::configureSensor_() {
    OPT3001_Config newConfig;

    newConfig.RangeNumber = B1100;
    newConfig.ConvertionTime = B0;
    newConfig.Latch = B1;
    newConfig.ModeOfConversionOperation = B11;

    OPT3001_ErrorCode errorConfig = myself.writeConfig(newConfig);
    if (errorConfig != NO_ERROR)
      ESP_LOGD("error","OPT3001 configuration %i", errorConfig);
    else {
      OPT3001_Config sensorConfig = myself.readConfig();
      ESP_LOGD("config","OPT3001 Current Config:");
      ESP_LOGD("config","------------------------------");
      ESP_LOGD("config","Conversion ready (R): %i", sensorConfig.ConversionReady);
      ESP_LOGD("config","Conversion time (R/W): %i", sensorConfig.ConvertionTime);
      ESP_LOGD("config","Fault count field (R/W): %i", sensorConfig.FaultCount);
      ESP_LOGD("config","Flag high field (R-only): %i", sensorConfig.FlagHigh);
      ESP_LOGD("config","Flag low field (R-only): %i", sensorConfig.FlagLow);
      ESP_LOGD("config","Latch field (R/W): %i", sensorConfig.Latch);
      ESP_LOGD("config","Mask exponent field (R/W): %i", sensorConfig.MaskExponent);
      ESP_LOGD("config","Mode of conversion operation (R/W): %i", sensorConfig.ModeOfConversionOperation);
      ESP_LOGD("config","Polarity field (R/W): %i", sensorConfig.Polarity);
      ESP_LOGD("config","Overflow flag (R-only): %i", sensorConfig.OverflowFlag);
      ESP_LOGD("config","Range number (R/W): %i", sensorConfig.RangeNumber);
      ESP_LOGD("config","------------------------------");
    }

    u_short manufacturer_id = myself.readManufacturerID();
    this->ambient_light_sensor_->publish_state(manufacturer_id);

    u_short device_id = myself.readDeviceID();
    this->ambient_light_sensor_->publish_state(device_id);

    u_short high_limit = myself.readHighLimit().lux;
    this->ambient_light_sensor_->publish_state(high_limit);

    u_short low_limit = myself.readLowLimit().lux;
    this->ambient_light_sensor_->publish_state(low_limit);

    u_short error_code = myself.readResult().error;
  }
  void OPT3001Component::dump_config() {
  ESP_LOGCONFIG(TAG, "OPT3001:");
  LOG_I2C_DEVICE(this);
  if (this->is_failed()) {
    ESP_LOGE(TAG, "Communication with OPT3001 failed!");
  }
  LOG_UPDATE_INTERVAL(this);

  LOG_SENSOR("  ", "Ambient: ", this->ambient_light_sensor_);
}
  
  float OPT3001Component::get_setup_priority() const { return setup_priority::DATA; }
  void OPT3001Component::update() {
    ESP_LOGD("update", "Sending update");
    int lux_level = myself.readResult().lux;
    this->ambient_light_sensor_->publish_state(lux_level);
  }

}// Namespace ESP
}// Namespace OPT3001
