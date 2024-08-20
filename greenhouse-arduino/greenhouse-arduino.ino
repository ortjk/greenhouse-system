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

  byte output [4];
  output[0] = 0xFE;
  output[1] = (encoded >> 8) & 0xFF;
  output[2] = encoded & 0xFF;
  output[3] = 0xFF;
  
  Serial.write(output, 4);
}

void receiveData(byte* input)
{
  bool finished = false;
  bool inProgress = false;
  byte ndx = 0;
  byte rc;

  while (Serial.available() > 0 && !finished)
  {
    rc = Serial.read();

    if (inProgress)
    {
      if (rc != 0xFF)
      {
        input[ndx] = rc;
        ndx++;
        if (ndx >= 2)
        {
          ndx = 1;
        }
      }
      else
      {
        inProgress = false;
        ndx = 0;
        finished = true;
      }
    }
    else if (rc == 0xFE)
    {
      inProgress = true;
    }
  }
}

void refreshSetpoints()
{
  if (Serial.available() > 0)
  {
    byte input [2];
    receiveData(input);
    decodeInput(&input[0], &input[1], &setpoints);
  }
}

void controlWindows()
{
  if (setpoints.manualEnable)
  {
    if (setpoints.manualOpen)
    {
      digitalWrite(MOTOR_PIN, HIGH);
    }
    else
    {
      digitalWrite(MOTOR_PIN, LOW);
    }
  }
  else
  {
    if (temperature > setpoints.maxTemperature)
    {
      digitalWrite(MOTOR_PIN, HIGH);
    }
    else if (temperature < setpoints.minTemperature)
    {
      digitalWrite(MOTOR_PIN, LOW);
    }
  }
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

  // control windows based on state
  controlWindows();

  delay(10); // delay 10ms for stability
}