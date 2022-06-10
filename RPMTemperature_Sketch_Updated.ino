  const int NumPortsToRead = 6;
  int AnalogResult[NumPortsToRead];
  volatile unsigned long TimeStamp = 0;
  volatile unsigned long time1 = 0;
  volatile unsigned long time2 = 0;
  volatile unsigned long Oldtime1 = 0;
  volatile unsigned long Oldtime2 = 0;
  volatile unsigned long TempTime1 = 0;
  volatile unsigned long TempTime2 = 0;
  String AllResult = "";
  int tempPin = A1;
  int Vo;
  float R2;
  float R1 = 991;

void setup() {
  // Initialize serial communication
  // Ensure that Baud rate specified here matches that selected in SimpleDyno
  // Availailable Baud rates are:
  // 9600, 14400, 19200, 28800, 38400, 57600, 115200
  Serial.begin(9600);
  // Initialize interupts (Pin2 is interrupt 0 = RPM1, Pin3 in interrupt 1 = RPM2)
  attachInterrupt(0,channel1,FALLING);
  attachInterrupt(1,channel2,FALLING);
}

void loop() {
  AllResult = "";
  AllResult += micros();
  AllResult += ",";
  //added so that there is no issue with interrupts
  noInterrupts();
  AllResult += TempTime1;
  AllResult += ",";
  AllResult += time1;
  AllResult += ",";
  AllResult += TempTime2;
  AllResult += ",";
  AllResult += time2;
  interrupts();
 /*
  for (int Looper = 0; Looper < NumPortsToRead;Looper++){
    AnalogResult[Looper] = analogRead(Looper);
    AllResult += ",";
    AllResult += AnalogResult[Looper];
  }
 */
 //Clayton Norris Added Dec 20, 2021 This is adding the temperature
  Vo = analogRead(tempPin);
  R2 = R1 * (1023.0 / (float)Vo - 1.0);
  AllResult += ",";
  AllResult += R2;
  //
  Serial.println (AllResult);
  Serial.flush();
  delay(1);
}

//Interrupt routine for RPM1
void channel1(){
  TempTime1 = micros();
  time1 = TempTime1-Oldtime1;
  Oldtime1 = TempTime1;
}

//Interrupt routine for RPM2
void channel2(){
    TempTime2 = micros();
  time2 = TempTime2-Oldtime2;
  Oldtime2 = TempTime2;
}
