// For the DS18B20 1-wire temp sensors
#include <OneWire.h>
#include <DallasTemperature.h>
// For the DHT22 temp and humidity sensors
#include <DHT.h>

// pin 3 for the one wire sensors
#define ONE_WIRE_BUS 3
// pin 2 for the DHT22 sensor
#define DHTPIN 2
#define DHTTYPE DHT22

// Setup a oneWire instance to communicate with any OneWire devices
OneWire oneWire(ONE_WIRE_BUS);
// Pass our oneWire reference to Dallas Temperature. 
DallasTemperature tempSensors(&oneWire);
// Assign the addresses of your 1-Wire temp sensors.
// See the tutorial on how to obtain these addresses:
// http://www.hacktronics.com/Tutorials/arduino-1-wire-address-finder.html
DeviceAddress insideThermometer = { 0x28, 0xB6, 0xCB, 0xA8, 0x04, 0x00, 0x00, 0xD2 };
DeviceAddress outsideThermometer = { 0x28, 0xAF, 0x13, 0xAA, 0x04, 0x00, 0x00, 0x78 };

// Initialize DHT sensor for normal 16mhz Arduino
DHT dht(DHTPIN, DHTTYPE);

void setup(void)
{
  Serial.begin(9600);
  
  tempSensors.begin();
  // set the resolution to 10 bit (good enough?)
  tempSensors.setResolution(insideThermometer, 10);
  tempSensors.setResolution(outsideThermometer, 10);
  
  dht.begin();
}

void printTemperature(DeviceAddress deviceAddress)
{
  float tempC = tempSensors.getTempC(deviceAddress);
  //if (tempC == -127.00) {
  //  Serial.print("Error getting temperature");
  //} else {
  Serial.print(tempC);
  //}
}

void loop(void)
{ 
  delay(2000);
  tempSensors.requestTemperatures();
  Serial.print("[");
  printTemperature(insideThermometer);
  Serial.print(",");
  printTemperature(outsideThermometer);
  
  // Reading temperature or humidity takes about 250 milliseconds!
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  // Read temperature as Celsius
  float dhtTemp = dht.readTemperature();
  Serial.print(",");
  Serial.print(dhtTemp);
  float dhtHumidity = dht.readHumidity();
  Serial.print(",");
  Serial.print(dhtHumidity);
  
  Serial.print("]\n");
}

