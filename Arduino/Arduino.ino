//oled 128 * 32 Ic2
#include <SPI.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
//RTC
#include <RtcDS1302.h>
#include <Wire.h>
#include <EEPROM.h>
//JSON
#include <ArduinoJson.h>
#include <ArduinoJson.hpp>
//DHT22
#include <DHT.h>
#include <DHT_U.h>
//servo
#include <Servo.h>

#define DHTPIN 2       // Pin digital conectado al sensor DHT
#define DHTTYPE DHT22  // Tipo de sensor DHT

#define SCREEN_WIDTH 128     // OLED display width, in pixels
#define SCREEN_HEIGHT 32     // OLED display height, in pixels
#define OLED_RESET -1        // Reset pin # (or -1 if sharing Arduino reset pin)
#define SCREEN_ADDRESS 0x3C  ///< See datasheet for Address; 0x3D for 128x64, 0x3C for 128x32

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

//DHT 22 inicializacion
DHT_Unified dht(DHTPIN, DHTTYPE);
uint32_t delayMS;

//Objeto JSON
DynamicJsonDocument doc(256);  

//RTC object
ThreeWire myWire(7, 6, 8);  // IO/DAT, SCLK/CLK, CE/RST
RtcDS1302<ThreeWire> Rtc(myWire);

//ultrasonico
const int Trigger = 4;
const int Echo = 3;

//Servo de comida
Servo servo;

// Verificar uso de pantalla correcta
#if (SSD1306_LCDHEIGHT != 32)
#error("Altura incorrecta, cambie en la libreria de Adafruit_SSD1306.h!");
#endif

void setup() {
  Serial.begin(9600);
  Wire.begin();
  dht.begin();
  Rtc.Begin();

  while (!Serial);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;)
      ;  // Don't proceed, loop forever
  }


  RtcDateTime compiled = RtcDateTime(__DATE__, __TIME__);

  if (!Rtc.IsDateTimeValid()) {
    //RTC lost confidence in the DateTime!;
    Rtc.SetDateTime(compiled);
  }

  if (Rtc.GetIsWriteProtected()) {
    //RTC was write protected, enabling writing now;
    Rtc.SetIsWriteProtected(false);
  }

  if (!Rtc.GetIsRunning()) {
    //RTC was not actively running, starting now;
    Rtc.SetIsRunning(true);
  }

  RtcDateTime now = Rtc.GetDateTime();
  if (now < compiled) {
    //RTC is older than compile time!  (Updating DateTime);
    Rtc.SetDateTime(compiled);
  } else if (now > compiled) {
    //"RTC is newer than compile time. (this is expected);
  } else if (now == compiled) {
    //RTC is the same as compile time! (not expected but all is fine);
  }

  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  delayMS = sensor.min_delay / 1000;

  display.clearDisplay();
  display.display();

  testscrolltext("HappyTail");

  pinMode(Trigger, OUTPUT);
  pinMode(Echo, INPUT);
  digitalWrite(Trigger, LOW);

  servo.attach(9);
  servo.write(90);
}

void loop() {

  if (Serial.available() > 0) {
    String read = Serial.readStringUntil('\n');

    if (read == "food") {
      food();
    }
     
  }

  doc["status"] = "ok";
  get_temp_humidity();

  RtcDateTime now_loop = Rtc.GetDateTime();
  printDateTime(now_loop);

  // Utiliza la función serializeJson para convertir el documento JSON en una cadena y enviarlo por el puerto serie
  serializeJson(doc, Serial);
  Serial.println();

  delay(2000);
  doc.clear();
}

void get_temp_humidity() {
  delay(delayMS);
  sensors_event_t event;

  dht.temperature().getEvent(&event);
  if (isnan(event.temperature)) {
    doc["temperature"] = F("Error reading temperature!");
  } else {
    doc["temperature"] = event.temperature;
  }

  dht.humidity().getEvent(&event);
  if (isnan(event.relative_humidity)) {
    doc["humidity"] = F("Error reading humidity!");
  } else {
    doc["humidity"] = event.relative_humidity;
  }
}

#define countof(a) (sizeof(a) / sizeof(a[0]))

void printDateTime(const RtcDateTime& dt) {
  char datestring[14];
  char hourstring[14];

  snprintf_P(hourstring,
             countof(hourstring),
             PSTR("%02u:%02u:%02u"),
             dt.Hour(),
             dt.Minute(),
             dt.Second());

  doc["time"] = hourstring;
  //serializeJson(doc, Serial);
  Serial.println();

  snprintf_P(datestring,
             countof(datestring),
             PSTR("%02u/%02u/%04u"),
             dt.Month(),
             dt.Day(),
             dt.Year());
  doc["date"] = datestring;
}

void testscrolltext(String m) {
  display.clearDisplay();
  display.display();

  display.setTextSize(2);  // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(16, 0);
  display.println(m);
  display.display();  // Show initial text
  delay(100);

  // Scroll in various directions, pausing in-between:
  display.startscrollleft(0x00, 0x0F);
  delay(1000);
}
void textError(void) {
  display.stopscroll();
  delay(100);
  display.clearDisplay();
  display.display();

  display.setTextSize(2);  // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 0);
  display.println("Error");
  display.display();  // Show initial text
  delay(1500);
  testscrolltext("HappyTail");
}

void food(void) {
  testscrolltext("dispensing");
  long t, d;
  servo.write(0);
  delay(3000);

  for (int i = 0; i < 10; i++) {
    digitalWrite(Trigger, HIGH);
    delayMicroseconds(10);
    digitalWrite(Trigger, LOW);

    t = pulseIn(Echo, HIGH);
    d = t / 59;

    if (d < 5) {
      doc["food"] = true;
    } else {
      doc["food"] = false;
    }
  }
  delay(2000);
  servo.write(90);

  if (doc["food"] == false) {
    textError();
  }
}
