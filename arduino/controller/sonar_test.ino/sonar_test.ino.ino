/* YourDuino SKETCH UltraSonic Serial 2.0
 Runs HC-04 and SRF-06 and other Ultrasonic Modules
 Open Serial Monitor to see results
 Reference: http://playground.arduino.cc/Code/NewPing
 Questions?  terry@yourduino.com */

/*-----( Import needed libraries )-----*/
#include <NewPing.h>
/*-----( Declare Constants and Pin Numbers )-----*/
#define  TRIGGER_PIN  3
#define  ECHO_PIN     A3
#define MAX_DISTANCE 200 // Maximum distance we want to ping for (in centimeters).
                         //Maximum sensor distance is rated at 400-500cm.
/*-----( Declare objects )-----*/
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE); // NewPing setup of pins and maximum distance.
/*-----( Declare Variables )-----*/
int DistanceMM;
int DistanceCm;

void setup()   /****** SETUP: RUNS ONCE ******/
{
  Serial.begin(9600);
  Serial.println("UltraSonic Distance Measurement");
  Serial.println("YourDuino.com  terry@yourduino.com");
}//--(end setup )---


void loop()   /****** LOOP: RUNS CONSTANTLY ******/
{
  //delay(100);// Wait 100ms between pings (about 10 pings/sec). 29ms should be the shortest delay between pings.
  DistanceMM = sonar.ping_in();
  Serial.print("Ping: ");
  Serial.print(DistanceMM); // Convert ping time to distance and print result 
                            // (0 = outside set distance range, no ping echo)
  Serial.print(" in     ");
  
  //delay(100);// Wait 100ms between pings (about 10 pings/sec). 29ms should be the shortest delay between pings.
  DistanceCm = sonar.ping_cm();
  Serial.print("Ping: ");
  Serial.print(DistanceCm); 
  Serial.println(" cm");  

}//--(end main loop )---

/*-----( Declare User-written Functions )-----*/

// None
//*********( THE END )***********
