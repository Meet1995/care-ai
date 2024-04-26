#include <WiFi.h>
#include <ESP32Firebase.h>
#include <time.h>

#include "DFRobot_BloodOxygen_S.h"

#define WIFI_SSID "<YOUR SSID>"
#define WIFI_PASSWORD "<YOUR PASSWORD>"

#define FIREBASE_HOST "<YOUR FIREBASE DB URL>"
#define FIREBASE_AUTH "<YOUR DB SECRET>"

Firebase firebase(FIREBASE_HOST);

#define I2C_COMMUNICATION  //use I2C for communication, but use the serial port for communication if the line of codes were masked

#ifdef  I2C_COMMUNICATION
#define I2C_ADDRESS    0x57
DFRobot_BloodOxygen_S_I2C MAX30102(&Wire ,I2C_ADDRESS);
#else
/* ---------------------------------------------------------------------------------------------------------------
 *    board   |             MCU                | Leonardo/Mega2560/M0 |    UNO    | ESP8266 | ESP32 |  microbit  |
 *     VCC    |            3.3V/5V             |        VCC           |    VCC    |   VCC   |  VCC  |     X      |
 *     GND    |              GND               |        GND           |    GND    |   GND   |  GND  |     X      |
 *     RX     |              TX                |     Serial1 TX1      |     5     |   5/D6  |  D2   |     X      |
 *     TX     |              RX                |     Serial1 RX1      |     4     |   4/D7  |  D3   |     X      |
 * ---------------------------------------------------------------------------------------------------------------*/
#if defined(ARDUINO_AVR_UNO) || defined(ESP8266)
SoftwareSerial mySerial(4, 5);
DFRobot_BloodOxygen_S_SoftWareUart MAX30102(&mySerial, 9600);
#else
DFRobot_BloodOxygen_S_HardWareUart MAX30102(&Serial1, 9600); 
#endif
#endif

void setup()
{
  Serial.begin(115200);
  // For WiFi and Firebase
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");


  // For Sensor
  while (false == MAX30102.begin())
  {
    Serial.println("init fail!");
    delay(1000);
  }
  Serial.println("init success!");
  Serial.println("start measuring...");
  MAX30102.sensorStartCollect();

  // Initialize NTP client after WiFi is connected
  configTime(-5 * 3600, 0, "pool.ntp.org");  // Configure NTP client
  delay(1000);  // Wait for time to be set
}

void loop() {
  for(int i=0; i<10; i++){
    float spO2, pulseRate, temp;
    MAX30102.getHeartbeatSPO2();

    spO2 = MAX30102._sHeartbeatSPO2.SPO2;
    Serial.print("SPO2 is : ");
    Serial.print(spO2);
    Serial.println("%");

    pulseRate = MAX30102._sHeartbeatSPO2.Heartbeat;
    Serial.print("heart rate is : ");
    Serial.print(pulseRate);
    Serial.println(" Times/min");

    temp = MAX30102.getTemperature_C();
    Serial.print("Temperature value of the board is : ");
    Serial.print(temp);
    Serial.println(" ℃");

    // Get the current UNIX timestamp
    time_t now = time(nullptr);
    
    // Replace all data under 'pulse', 'spo2', and 'temp' with the new data
    String pulseString = String(now) + ":" + String(pulseRate);
    firebase.setString("101/pulse/" + String(i), pulseString);
    firebase.setString("101/spo2/" + String(i), String(now) + ":" + String(spO2));
    firebase.setString("101/temperature/" + String(i), String(now) + ":" + String(temp));
    sleep(1);
  } 


}