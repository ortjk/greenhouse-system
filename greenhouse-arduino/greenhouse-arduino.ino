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

void refreshSetpoints()
{
  byte input [2];
  Serial.readBytesUntil('\n', input, 2);
  decodeInput(&input[0], &input[1], &setpoints);
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
  unsigned long currentTime = millis();
  if (currentTime - previousDHT >= DHT_INTERVAL)
  {
    // check temperature
    // note: reading temperature takes an additional ~250ms
    publishTemperature();

    // retrieve setpoints
    refreshSetpoints();

    previousDHT = currentTime;
  }

  delay(10); // delay 10ms for stability
}