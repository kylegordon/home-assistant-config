#include "esphome.h"
#include "ClosedCube_OPT3001.h"

using namespace esphome;

class MyOPT3001 : public PollingComponent {
 public:

  ClosedCube_OPT3001 myself;
  Sensor *manufacturer_id_sensor = new Sensor();
  Sensor *device_id_sensor = new Sensor();
  Sensor *lux_sensor = new Sensor();
  Sensor *high_limit_sensor = new Sensor();
  Sensor *low_limit_sensor = new Sensor();

  // Update every 5s (value in ms)
  MyOPT3001() : PollingComponent(5000) { }

  void setup() override {
    // myself.initSHT20();    // Init SHT20 Sensor
    myself.begin(0x44);
    delay(100);
    configureSensor();
    delay(100);
    // myself.checkSHT20();   // Check SHT20 Sensor
    myself.readManufacturerID();
    myself.readDeviceID();
  }

  // Most of this copied from https://github.com/closedcube/ClosedCube_OPT3001_Arduino/blob/master/examples/opt3001demo/opt3001demo.ino
  // I have no real idea what I'm doing.
  void configureSensor() {
    OPT3001_Config newConfig;
    
    newConfig.RangeNumber = B1100;	
    newConfig.ConvertionTime = B0;
    newConfig.Latch = B1;
    newConfig.ModeOfConversionOperation = B11;

    OPT3001_ErrorCode errorConfig = myself.writeConfig(newConfig);
    if (errorConfig != NO_ERROR)
      ESP_LOGD("update","OPT3001 configuration %i", errorConfig);
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
    
  }

  void update() override {

    ESP_LOGD("update", "In start of update");

    u_short manufacturer_id = myself.readManufacturerID();
    manufacturer_id_sensor->publish_state(manufacturer_id);

    u_short device_id = myself.readDeviceID();
    device_id_sensor->publish_state(device_id);

    int lux_level = myself.readResult().lux;
    lux_sensor->publish_state(lux_level);

    u_short high_limit = myself.readHighLimit().lux;
    high_limit_sensor->publish_state(high_limit);

    u_short low_limit = myself.readLowLimit().lux;
    low_limit_sensor->publish_state(low_limit);

    u_short error_code = myself.readResult().error;

    // %i for int ?
    // %f for float ?
    ESP_LOGD("update", "The value of manufacturer_id is: %i", manufacturer_id);
    ESP_LOGD("update", "The value of device_id is: %i", device_id);
    ESP_LOGD("update", "The value of lux_level is: %i", lux_level);

    ESP_LOGD("update", "The value of error_code is: %i", error_code);


  }
};
