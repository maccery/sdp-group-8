#include "SDPMotors.h"
#include <Wire.h>
// determines the direction of "outwards" movement
#define KICK_POWER 1
// determines durations at max power
#define KICK_DURATION 100

#define DEBUG
#define ACK_COMMS
#define DO_PARITY
// intermediate state
#define HAPPENING 1
// finished state
#define COMPLETE 2
// negative intermediate state
#define CLOSING 3

#define BinaryCheckerI2CAddress 69

#define MOVE_POWER_LEVEL_LEFT 0.6
#define MOVE_POWER_LEVEL_RIGHT 0.8


#define BUFF_SIZE 32
uint8_t buffer[BUFF_SIZE] = "";
uint8_t buff_head = 0;
uint8_t READY = 1;
uint8_t MATCHED_CMD = 0;
long LAST_MATCH_ID = -1;
MotorBoard motors;

enum MOTORS {
  RIGHT_GRABBER = 1,
  LEFT_GRABBER = 2,
  KICKER = 3,
  LEFT_MOTOR = 4,
  RIGHT_MOTOR = 5,
  MAX_ENGINES = 6
};

uint8_t movement_motors[] = {LEFT_MOTOR, RIGHT_MOTOR};

// 0 -> not kicking, 1 -> kicking, 2 -> getting back to position
byte IS_KICKING = 0;

byte MATCHED=0;
byte KICK_AFTERWARDS = 0;

void setup_pins() {
  pinMode(2,INPUT);
  pinMode(3,OUTPUT);
  pinMode(4,INPUT);
  pinMode(5,OUTPUT);
  pinMode(6,OUTPUT);
  pinMode(7,INPUT);
  pinMode(8,OUTPUT);
  pinMode(9,OUTPUT);
  pinMode(10,INPUT);
  pinMode(11,INPUT);
  pinMode(12,INPUT);
  pinMode(13,OUTPUT); // LED
  pinMode(A0,INPUT);
  pinMode(A1,INPUT);
  pinMode(A2,INPUT);
  pinMode(A3,INPUT);
  digitalWrite(8,HIGH); //Pin 8 must be high to turn the radio on!
}
void parse_packet();
void read_serial() {
  MATCHED_CMD = 0;
  while(Serial.available() > 0) {
    char a = Serial.read();
    if (a != '\t') {
      switch (buff_head) {
      case 0: break;
      case 1:
        if (a <= 'Z' && a >= 'A')
          buffer[buff_head++] = a;
        else buff_head = 0;
        break;  // reject impossible things
      default: buffer[buff_head++] = a;
      }
    }
    else {
      switch(buff_head) {
      case 0: buffer[buff_head++] = a; break;  // init hit
      case 1:
      case 2:
      case 5:
      case 6:
      case 10: buffer[buff_head++] = a; parse_packet(); break; // finishing byte
      // longest packet is 11B long, if we somehow reach this, just reset it all
      default: if (buff_head >= 11) buff_head = 0; buffer[buff_head++] = a; break;
      }
    }
    buffer[buff_head] = 0;
    if (buff_head >= BUFF_SIZE) buff_head = 0;
    if (MATCHED_CMD != 0)
      for(int i = 0; Serial.available() > 0 && i < 1024; i++)
        Serial.read();
    MATCHED_CMD = 0;
  }
}

/*
Packet format:
0x00(K|F|L|T|O|C|S|B)BBP0x00  [6B]
where B is a byte, P is parity byte (xor'd Bs + 0)
0x00VBBBBBBBB0x00 [11B]
0x00RBBBB0x00 [7B]
0x000x00  -> heartbeat
When packet is identified it will be sent to a function to do things
and then acknowledged.
*/

void parse_packet() {
  // uses static buffer ^^^^
  if (buff_head <= 1) return;
  if ((char)buffer[0] != '\t' || buff_head >= BUFF_SIZE){ buff_head = 0; return;}
  if ((char)buffer[buff_head - 1] != '\t') return;
  uint8_t b = buff_head;
  buff_head = 0;
  switch(b) {
  case 2:
    // empty message, retransmit READY if needed
    if (READY != 0) {
      Serial.println("READY");
      Serial.flush();
    }
    return;
  case 6: {
    // command message, extract relevant parts and stuff to handler
    char cmd = buffer[1];
    if (cmd == 'V' || cmd == 'R') {
      buff_head = b;
      return;
    }
    uint8_t b1 = buffer[2], b2 = buffer[3];
    if ((long)(byte)buffer[4] == LAST_MATCH_ID) {
      Serial.println("ACK, repeat");
      Serial.flush();
      return;
    }
    LAST_MATCH_ID = (byte) buffer[4];
    /*
    uint8_t p = b1 ^ b2 ^ 0;
    if (p = (byte)buffer[4]) {
      Serial.print("FAIL: Parity fail, got ");
      Serial.print(p);
      Serial.print(", but expected: ");
      Serial.println((byte)buffer[4]);
      Serial.flush();
      return;
    }*/
    // parity passed, handle it now
    command(cmd, b1, b2);
    Serial.print("ACK");
    Serial.println(LAST_MATCH_ID);
    Serial.flush();
    return;
  }
  case 7: {
    // run engine message, no parity
    char cmd = buffer[1];
    uint8_t id = buffer[2];
    int8_t pwr = buffer[3];
    // reinterpret_cast<int16_t>(buffer[4]) -> 4;5
    int16_t duration = *(int16_t*)(&buffer[4]);
    if (cmd != 'R') {
      if (cmd == 'V') {
        buff_head = b;
        return;
      }
      Serial.println("FAIL: Got run engine-like packet, but cmd isn't R, wat");
      return;
    }
    run_engine(id, pwr, duration);
    Serial.println("ACK");
    Serial.flush();
    return;
  }
  case 11: {
    // full move message, no parity
    char cmd = buffer[1];
    int16_t lm = *(int16_t*)(&buffer[2]);
    int16_t rm = *(int16_t*)(&buffer[4]);
    int16_t sm = *(int16_t*)(&buffer[6]);
    if (cmd != 'M') {
      Serial.println("FAIL: Got move-like packet, but cmd isn't M, wat");
      return;
    }
    move_bot(lm, rm, sm, MOVE_POWER_LEVEL_LEFT, MOVE_POWER_LEVEL_RIGHT);
    Serial.println("ACK");
    Serial.flush();
    return;
  }
  default:
    Serial.print("FAIL: Got msg:");
    Serial.println((char*)buffer + 1);
    Serial.flush();
    return;
  }
}

void setup() {
  Serial.begin(115200);  // 115kb
  setup_pins();
  Wire.begin();  // need this s.t. arduino is mastah
  Serial.println("Team8-D READY");
  Serial.flush();
  motors.stop_all();
}

void kick_f(float power, uint16_t duration) {
  IS_KICKING = HAPPENING;

  // Runs the motor at the given motor, the for KICK_DURATION lenght of time
  motors.run_motor(KICKER, power, duration, 0);
}

void loop() {
  // check whether something needs to be stopped
  motors.scan_motors();

  // if kicking -> check whether we need to start retracting the kicker, etc
  switch(IS_KICKING) {
  case HAPPENING:
    // While we're in the happening state, check when the kicker stops
    if (!motors.is_running(KICKER)) {
      // IT should have stopped already but just verify this
      motors.stop_motor(KICKER);  
      
      // Wait 30ms then bring the kicker back to its original position
      delay(30);
      kick_f(-0.5 * KICK_POWER, uint16_t(float(KICK_DURATION)));
      
      IS_KICKING = COMPLETE;
    }
    break;
  case COMPLETE:
    if (!motors.is_running(KICKER)) {
      IS_KICKING = 0;
    }
    break;
  default:
    break; // do nothing
  }

  if (READY == 0 && motors.all_stopped())
    READY = 1;
  read_serial();
  delay(5);
}

void command(char cmd, uint8_t b1, uint8_t b2) {
  MATCHED_CMD = 1;
  uint8_t cd[] = {cmd, b1, b2, 0};
  switch (cmd) {
  case 'K': kick(b1); READY = 0; return;
  case 'F': move_front(b1, b2);  READY = 0;return;
  case 'T': turn(b1, b2);  READY = 0;return;
  case 'S': stop_engines(); READY = 0; return;
  case 'B': receive_binary(b1); READY = 0; return;
  case 'G': grab(); READY = 0; return;
  case 'U': ungrab(); READY = 0; return;
  default: READY = 1; MATCHED_CMD = 0;
  }
}
int16_t reint(uint8_t a, uint8_t b) {
  // I am aware that I could try to mess with &a and &b, but no. Just no.
  uint8_t tmp[] = {a, b};
  return *(int16_t*)(&tmp);
}

// Given the binary sent, print it
void receive_binary(uint8_t b1) {
  // prints the received byte
  Serial.print("binary received ");
  Serial.print(b1);
  Serial.println();

  // Outputs the byte through I2C to a checker
  Wire.beginTransmission(BinaryCheckerI2CAddress);
  Wire.write(&b1, 1);
  Wire.endTransmission();
}

void move_front(uint8_t a, uint8_t b) {
  // We will only move forward if the robot is in the 'ready' state
  if (READY == 0) return;

  int16_t d = reint(a, b);
  
  return move_bot(d, d, 0, MOVE_POWER_LEVEL_LEFT, MOVE_POWER_LEVEL_RIGHT);
}

void turn(uint8_t a, uint8_t b) {
  // We will only turn if the robot is in the 'ready' state
  if (READY == 0) return;

  int16_t d = reint(a, b);
  return move_bot(-d, d, 0, MOVE_POWER_LEVEL_LEFT, MOVE_POWER_LEVEL_RIGHT);
}

void stop_engines() {
  // only stops movement engines!
  motors.stop_motor(LEFT_MOTOR);
  motors.stop_motor(RIGHT_MOTOR);
  motors.stop_motor(LEFT_GRABBER);
  motors.stop_motor(RIGHT_GRABBER);
}

void grab() {
  motors.run_motor(LEFT_GRABBER, 1, uint16_t(float(300)), -1);
  motors.run_motor(RIGHT_GRABBER, -1, uint16_t(float(300)), -1);
}

void ungrab() {
  motors.run_motor(LEFT_GRABBER, -0.2, uint16_t(float(500)), -1);
  motors.run_motor(RIGHT_GRABBER, 0.3, uint16_t(float(500)), -1);
}

/*
The power provided by the python interface is multiplied by the KICK_POWER function
*/
void kick(uint8_t pwr) {
    MATCHED=1;
    
    // Firstly bring the kicker back
    motors.run_motor(KICKER, 0.2, uint16_t(float(800)), -1);
    //delay(310);
    
    IS_KICKING = HAPPENING;

    // Runs the motor at the given motor, the for KICK_DURATION lenght of time
    motors.run_motor(KICKER, -1.0*float(pwr), uint16_t(float(300)/float(pwr)), 850);
}

void move_bot(int16_t lm, int16_t rm, int16_t sm, float left_power, float right_power) {
  if (READY == 0) return;
  uint16_t lag = motors.get_max_lag(movement_motors, 4);

  motors.run_motor(LEFT_MOTOR, lm > 0? left_power : -left_power, abs(lm), motors.get_adj_lag(LEFT_MOTOR, lag));
  motors.run_motor(RIGHT_MOTOR, rm > 0? right_power : -right_power, abs(rm), motors.get_adj_lag(RIGHT_MOTOR, lag));
}

void run_engine(uint8_t id, int8_t pwr, uint16_t time) {
  float power = float(pwr) / 127.0;
  motors.run_motor(id, power, time, -1);
}
