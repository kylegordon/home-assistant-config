#include "esphome.h"
#include "opt3001.h"

// Gets pulled in from the associated lambda in lux_meter.yaml
// Compile with docker run --rm -v "${PWD}":/config -it esphome/esphome lux_meter.yaml compile

using namespace esphome;

class MyCustomSensor : public PollingComponent, public Sensor {
 public:
  // constructor
  MyCustomSensor() : PollingComponent(15000) {}

  void setup() override {
    // This will be called by App.setup()
  }
  void loop() override {
    // This will be called by App.loop()
  }
};

ClosedCube_OPT3001::ClosedCube_OPT3001()
{
}

OPT3001_ErrorCode ClosedCube_OPT3001::begin(uint8_t address) {
	OPT3001_ErrorCode error = NO_ERROR;
	_address = address;
	Wire.begin();

	return NO_ERROR;
}

uint16_t ClosedCube_OPT3001::readManufacturerID() {
	uint16_t result = 0;
	OPT3001_ErrorCode error = writeData(MANUFACTURER_ID);
	if (error == NO_ERROR)
		error = readData(&result);
	return result;
}

uint16_t ClosedCube_OPT3001::readDeviceID() {
	uint16_t result = 0;
	OPT3001_ErrorCode error = writeData(DEVICE_ID);
	if (error == NO_ERROR)
		error = readData(&result);
	return result;
}

OPT3001_Config ClosedCube_OPT3001::readConfig() {
	OPT3001_Config config;
	OPT3001_ErrorCode error = writeData(CONFIG);
	if (error == NO_ERROR)
		error = readData(&config.rawData);
	return config;
}

OPT3001_ErrorCode ClosedCube_OPT3001::writeConfig(OPT3001_Config config) {
	Wire.beginTransmission(_address);
	Wire.write(CONFIG);
	Wire.write(config.rawData >> 8);
	Wire.write(config.rawData & 0x00FF);
	return (OPT3001_ErrorCode)(-10 * Wire.endTransmission());
}

OPT3001 ClosedCube_OPT3001::readResult() {
	return readRegister(RESULT);
}

OPT3001 ClosedCube_OPT3001::readHighLimit() {
	return readRegister(HIGH_LIMIT);
}

OPT3001 ClosedCube_OPT3001::readLowLimit() {
	return readRegister(LOW_LIMIT);
}

OPT3001 ClosedCube_OPT3001::readRegister(OPT3001_Commands command) {
	OPT3001_ErrorCode error = writeData(command);
	if (error == NO_ERROR) {
		OPT3001 result;
		result.lux = 0;
		result.error = NO_ERROR;

		OPT3001_ER er;
		error = readData(&er.rawData);
		if (error == NO_ERROR) {
			result.raw = er;
			result.lux = 0.01*pow(2, er.Exponent)*er.Result;
		}
		else {
			result.error = error;
		}

		return result;
	}
	else {
		return returnError(error);
	}
}

OPT3001_ErrorCode ClosedCube_OPT3001::writeData(OPT3001_Commands command)
{
	Wire.beginTransmission(_address);
	Wire.write(command);
	return (OPT3001_ErrorCode)(-10 * Wire.endTransmission(true));
}

OPT3001_ErrorCode ClosedCube_OPT3001::readData(uint16_t* data)
{
	uint8_t	buf[2];

	Wire.requestFrom(_address, (uint8_t)2);

	int counter = 0;
	while (Wire.available() < 2)
	{
		counter++;
		delay(10);
		if (counter > 250)
			return TIMEOUT_ERROR;
	}

	Wire.readBytes(buf, 2);
	*data = (buf[0] << 8) | buf[1];

	return NO_ERROR;
}


OPT3001 ClosedCube_OPT3001::returnError(OPT3001_ErrorCode error) {
	OPT3001 result;
	result.lux = 0;
	result.error = error;
	return result;
}
