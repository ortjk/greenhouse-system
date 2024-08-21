#include "DHT.h"
#include "./encoding_f.h"

#define ERROR_PIN 13
#define MOTOR_PIN 2

#define DHT_INTERVAL 3000 // read temp every 3s

unsigned long previousDHT = 0;

float humidity = 50;
float temperature = 25;

Setpoints setpoints; // window configuration defined in encoding_f.h

bool statusERROR = false;

DHT dht(3, DHT22); // digital pin 3
// dht requires 10k resistor accross the Vin and data pins

// read the dht sensor and push data to serial bus
void publishTemperature()
{
  humidity = dht.readHumidity();
  temperature = dht.readTemperature();

  unsigned short encoded = encodeOutput(&statusERROR, &temperature, &humidity);

  // data must be couched by beginning and ending bytes
  byte output [4];
  output[0] = 0xFE;
  output[1] = (encoded >> 8) & 0xFF;
  output[2] = encoded & 0xFF;
  output[3] = 0xFF;
  
  Serial.write(output, 4);
}

// helper function to read the configuration sent by the pi;
// just Serial.readBytes() does not always capture all data
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
      // if the byte read is NOT the end of message byte, save the byte and prepare to read the next
      if (rc != 0xFF)
      {
        input[ndx] = rc;
        ndx++;
        if (ndx >= 2)
        {
          ndx = 1;
        }
      }
      // else the byte read IS the end of message byte, and the reading process can stop
      else
      {
        inProgress = false;
        ndx = 0;
        finished = true;
      }
    }
    // if a byte has been read without the reading process starting yet
    // and the byte is the message beginning, start reading
    else if (rc == 0xFE)
    {
      inProgress = true;
    }
  }
}

// read the serial bus and saves the configuration sent
void refreshSetpoints()
{
  if (Serial.available() > 0)
  {
    byte input [2];
    receiveData(input);
    decodeInput(&input[0], &input[1], &setpoints);
  }
}

// do control output based on current configuration
void controlWindows()
{
  if (setpoints.manualEnable) // manual controls take priority
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
  else // change state based on temperature setpoints
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
    // note: reading sensor takes an additional ~250ms
    publishTemperature();

    refreshSetpoints();

    previousDHT = currentTime;
  }

  // control windows based on state
  controlWindows();

  delay(10); // delay 10ms for stability
}