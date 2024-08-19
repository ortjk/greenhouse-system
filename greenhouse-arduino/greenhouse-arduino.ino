#include "DHT.h"
#include "./encoding_f.h"

#define ERROR_PIN 13
#define MOTOR_PIN 2

#define DHT_INTERVAL 3000 // read temp every 3s

unsigned long previousDHT = 0;

float humidity = 50;
float temperature = 25;

Setpoints setpoints;

bool statusERROR = false;

DHT dht(3, DHT22); // digital pin 3
// dht requires 10k resistor accross the Vin and data pins

void publishTemperature()
{
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();

  unsigned short encoded = encodeOutput(&statusERROR, &temperature, &humidity);

  byte output [3];
  output[0] = (encoded >> 8) & 0xFF;
  output[1] = encoded & 0xFF;
  output[2] = '\n';
  
  Serial.write(output, 3);
}

void setup() 
{
  Serial.begin(9600);
  
  pinMode(ERROR_PIN, OUTPUT);
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(3, INPUT);

  dht.begin();
}

void loop() 
{
  // check temperature
  // note: reading temperature takes an additional ~250ms
  unsigned long currentTime = millis();
  if (currentTime - previousDHT >= DHT_INTERVAL)
  {
    publishTemperature();

    /*
    if (temperature >= ACTUATOR_THRESHOLD)
    {
      digitalWrite(ACTUATOR_PIN, HIGH); // open the windows
    }
    else
    {
      digitalWrite(ACTUATOR_PIN, HIGH); // close the windows
    }
    */

    previousDHT = currentTime;
  }

  // TODO add serial communication with raspberry pi

  delay(10); // delay for stability
}