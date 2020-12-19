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
    // myself.checkSHT20();   // Check SHT20 Sensor
    myself.readManufacturerID();
    myself.readDeviceID();
  }

  void update() override {
    u_short manufacturer_id = myself.readManufacturerID();
    manufacturer_id_sensor->publish_state(manufacturer_id);

    u_short device_id = myself.readDeviceID();
    device_id_sensor->publish_state(device_id);

    u_short lux_level = myself.readResult().lux;
    lux_sensor->publish_state(lux_level);

    u_short high_limit = myself.readHighLimit().lux;
    high_limit_sensor->publish_state(high_limit);

    u_short low_limit = myself.readLowLimit().lux;
    low_limit_sensor->publish_state(low_limit);
  }
};