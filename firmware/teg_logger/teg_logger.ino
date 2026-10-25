/*
  TEG characterisation logger
  Peltier module (TEC1-12706) run as a thermoelectric generator.

  Hardware
    Arduino Uno R3
    ADS1115 16-bit ADC, I2C address 0x48 (ADDR pin to GND)
    20x4 LCD with I2C backpack, address 0x27 (some boards use 0x3F)
    2x DS18B20 on D2 with a 4.7 kohm pull-up to 5 V
      (a 3rd DS18B20 in the hot bath is optional, used for calorimetry)

  Wiring
    SDA -> A4, SCL -> A5 (ADS1115 and LCD share the bus)
    ADS1115 A0 -> top of load resistor (TEG +)
    ADS1115 A1 -> bottom of load resistor (TEG -), also joined to GND
    Check the TEG polarity with a multimeter first: A0 must not go below -0.3 V.

  Libraries (Arduino IDE > Library Manager)
    OneWire, DallasTemperature, Adafruit ADS1X15, LiquidCrystal I2C (Frank de Brabander)

  Serial: 115200 baud, one CSV line per sample, comment lines start with '#'.
    t_s,T_hot_C,T_cold_C,dT_C,T_bath_C,V_V,R_ohm,I_A,P_W

  Commands (type in Serial Monitor or teg_logger.py, end with Enter)
    R <ohms>   set the load resistance you just connected (0 = open circuit)
    C          calibrate: put both sensors in the same water first
    Z          clear the calibration offset
    X          swap which sensor is hot and which is cold
    P <sec>    logging period in seconds (minimum 1)
    N <text>   write a note into the log
    ?          show status
*/

#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <Adafruit_ADS1X15.h>
#include <LiquidCrystal_I2C.h>
#include <EEPROM.h>

const uint8_t ONE_WIRE_PIN = 2;
const uint8_t LCD_ADDR = 0x27;
const uint8_t ADS_ADDR = 0x48;
const uint8_t ADC_SAMPLES = 16;     // averaged per reading, about 130 ms at 128 SPS
const uint8_t CAL_SAMPLES = 10;

OneWire oneWire(ONE_WIRE_PIN);
DallasTemperature sensors(&oneWire);
Adafruit_ADS1115 ads;
LiquidCrystal_I2C lcd(LCD_ADDR, 20, 4);

DeviceAddress addr[3];
uint8_t nSensors = 0;

// Saved in EEPROM so calibration survives a reset
struct Config {
  uint16_t magic;
  float coldOffset;   // added to the cold sensor reading
  uint8_t swapped;    // 1 = sensor 0 is cold, sensor 1 is hot
};
const uint16_t MAGIC = 0x7E61;
Config cfg;

float rLoad = 0;                 // ohms, 0 = open circuit
unsigned long periodMs = 1000;
unsigned long lastSample = 0;
bool lowGain = false;            // true = +/-6.144 V range, false = +/-4.096 V
uint8_t calLeft = 0;
float calSum = 0;

char line[48];
uint8_t lineLen = 0;

void saveConfig() { EEPROM.put(0, cfg); }

void lcdLine(uint8_t row, const char *s) {
  lcd.setCursor(0, row);
  uint8_t n = 0;
  while (s[n] && n < 20) lcd.print(s[n++]);
  while (n++ < 20) lcd.print(' ');
}

float readTemp(uint8_t i) {
  float t = sensors.getTempC(addr[i]);
  return (t == DEVICE_DISCONNECTED_C) ? NAN : t;
}

// Averaged differential reading A0-A1 with simple auto-ranging
float readVolts() {
  float sum = 0;
  for (uint8_t i = 0; i < ADC_SAMPLES; i++) {
    sum += ads.computeVolts(ads.readADC_Differential_0_1());
  }
  float v = sum / ADC_SAMPLES;
  if (!lowGain && fabs(v) > 4.0) {
    lowGain = true;
    ads.setGain(GAIN_TWOTHIRDS);
  } else if (lowGain && fabs(v) < 3.5) {
    lowGain = false;
    ads.setGain(GAIN_ONE);
  }
  return v;
}

void printAddress(DeviceAddress a) {
  for (uint8_t i = 0; i < 8; i++) {
    if (a[i] < 16) Serial.print('0');
    Serial.print(a[i], HEX);
  }
}

void printStatus() {
  Serial.print(F("# sensors=")); Serial.print(nSensors);
  Serial.print(F(" hot=")); printAddress(addr[cfg.swapped ? 1 : 0]);
  Serial.print(F(" cold=")); printAddress(addr[cfg.swapped ? 0 : 1]);
  Serial.print(F(" cold_offset=")); Serial.print(cfg.coldOffset, 3);
  Serial.print(F(" R_load=")); Serial.print(rLoad, 3);
  Serial.print(F(" period_s=")); Serial.println(periodMs / 1000.0, 1);
}

void printHeader() {
  Serial.println(F("t_s,T_hot_C,T_cold_C,dT_C,T_bath_C,V_V,R_ohm,I_A,P_W"));
}

void handleCommand() {
  line[lineLen] = '\0';
  char cmd = toupper(line[0]);
  char *arg = line + 1;
  while (*arg == ' ') arg++;

  switch (cmd) {
    case 'R':
      rLoad = max(0.0, atof(arg));
      Serial.print(F("# R_load set to ")); Serial.print(rLoad, 3); Serial.println(F(" ohm"));
      break;
    case 'C':
      calLeft = CAL_SAMPLES;
      calSum = 0;
      Serial.println(F("# calibrating, keep both sensors in the same water"));
      break;
    case 'Z':
      cfg.coldOffset = 0;
      saveConfig();
      Serial.println(F("# offset cleared"));
      break;
    case 'X':
      cfg.swapped = !cfg.swapped;
      saveConfig();
      Serial.println(F("# hot/cold sensors swapped"));
      break;
    case 'P':
      periodMs = (unsigned long)(max(1.0, atof(arg)) * 1000);
      Serial.print(F("# period set to ")); Serial.print(periodMs / 1000.0, 1); Serial.println(F(" s"));
      break;
    case 'N':
      Serial.print(F("# note: ")); Serial.println(arg);
      break;
    case '?':
      printStatus();
      break;
    default:
      if (lineLen) Serial.println(F("# unknown command, type ? for status"));
  }
}

void handleSerial() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (lineLen) handleCommand();
      lineLen = 0;
    } else if (lineLen < sizeof(line) - 1) {
      line[lineLen++] = c;
    }
  }
}

void updateLcd(float tH, float tC, float dT, float v, float i, float p) {
  char buf[21], a[10], b[10];

  dtostrf(tH, 5, 1, a);
  dtostrf(tC, 5, 1, b);
  snprintf(buf, sizeof(buf), "Th%sC  Tc%sC", a, b);
  lcdLine(0, buf);

  dtostrf(dT, 6, 2, a);
  if (rLoad > 0) {
    dtostrf(rLoad, 5, 2, b);
    snprintf(buf, sizeof(buf), "dT%sC  R=%s", a, b);
  } else {
    snprintf(buf, sizeof(buf), "dT%sC  OPEN", a);
  }
  lcdLine(1, buf);

  dtostrf(v, 6, 4, a);
  if (rLoad > 0) {
    dtostrf(i, 5, 3, b);
    snprintf(buf, sizeof(buf), "V %sV I %sA", a, b);
  } else {
    snprintf(buf, sizeof(buf), "Voc %sV", a);
  }
  lcdLine(2, buf);

  if (calLeft > 0) {
    snprintf(buf, sizeof(buf), "CALIBRATING %d", calLeft);
  } else if (rLoad > 0) {
    dtostrf(p * 1000, 7, 1, a);
    snprintf(buf, sizeof(buf), "P %s mW", a);
  } else if (dT > 3) {
    dtostrf(v / dT * 1000, 5, 1, a);      // live Seebeck estimate
    snprintf(buf, sizeof(buf), "S~%s mV/C", a);
  } else {
    snprintf(buf, sizeof(buf), "S~ (need dT>3C)");
  }
  lcdLine(3, buf);
}

void setup() {
  Serial.begin(115200);
  Wire.begin();
  lcd.init();
  lcd.backlight();
  lcdLine(0, "TEG logger");

  if (!ads.begin(ADS_ADDR)) {
    Serial.println(F("# ERROR: ADS1115 not found at 0x48"));
    lcdLine(1, "ADS1115 not found");
    while (true) {}
  }
  ads.setGain(GAIN_ONE);                 // +/-4.096 V, 125 uV per bit
  ads.setDataRate(RATE_ADS1115_128SPS);

  sensors.begin();
  nSensors = min(sensors.getDeviceCount(), (uint8_t)3);
  if (nSensors < 2) {
    Serial.print(F("# ERROR: need 2 DS18B20, found ")); Serial.println(nSensors);
    lcdLine(1, "Need 2 DS18B20");
    while (true) {}
  }
  for (uint8_t i = 0; i < nSensors; i++) {
    sensors.getAddress(addr[i], i);
    sensors.setResolution(addr[i], 12);  // 0.0625 C steps, 750 ms conversion
  }
  sensors.setWaitForConversion(false);

  EEPROM.get(0, cfg);
  if (cfg.magic != MAGIC || isnan(cfg.coldOffset)) {
    cfg.magic = MAGIC;
    cfg.coldOffset = 0;
    cfg.swapped = 0;
    saveConfig();
  }

  printStatus();
  Serial.println(F("# hold one sensor in your fingers to check which is hot; X swaps them"));
  printHeader();

  sensors.requestTemperatures();         // first conversion, ready by the first sample
  lastSample = millis();
}

void loop() {
  handleSerial();
  if (millis() - lastSample < periodMs) return;
  lastSample = millis();

  float tH = readTemp(cfg.swapped ? 1 : 0);
  float tCraw = readTemp(cfg.swapped ? 0 : 1);
  float tB = (nSensors >= 3) ? readTemp(2) : NAN;
  sensors.requestTemperatures();         // non-blocking, read on the next sample

  if (calLeft > 0 && !isnan(tH) && !isnan(tCraw)) {
    calSum += tH - tCraw;
    if (--calLeft == 0) {
      cfg.coldOffset = calSum / CAL_SAMPLES;
      saveConfig();
      Serial.print(F("# calibration done, cold_offset = ")); Serial.println(cfg.coldOffset, 3);
    }
  }

  float tC = tCraw + cfg.coldOffset;
  float dT = tH - tC;
  float v = readVolts();
  float i = (rLoad > 0) ? v / rLoad : 0;
  float p = (rLoad > 0) ? v * v / rLoad : 0;

  Serial.print(millis() / 1000.0, 1); Serial.print(',');
  Serial.print(tH, 3); Serial.print(',');
  Serial.print(tC, 3); Serial.print(',');
  Serial.print(dT, 3); Serial.print(',');
  Serial.print(tB, 3); Serial.print(',');
  Serial.print(v, 5); Serial.print(',');
  Serial.print(rLoad, 3); Serial.print(',');
  Serial.print(i, 5); Serial.print(',');
  Serial.println(p, 6);

  updateLcd(tH, tC, dT, v, i, p);
}
