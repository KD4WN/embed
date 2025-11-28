#include	<AFMotor.h>

// motor speed
#define MAX_VEL 255
#define MID_VEL 200

#define BACK_VEL 180

#define SMALL_DELAY_TIME 80  // 줄어든 회전 시간 (원래 170)
#define TINY_DELAY_TIME 50   // 줄어든 직진 시간 (원래 120)


/*
motor pin number
a: right motor
b: left motor
*/

AF_DCMotor	a(1);
AF_DCMotor	b(4);

/*
constant delay time
delay time is wheel operation time
if the delay time is longer, the wheel operation time is longer.
*/

void setup()
{
	Serial.begin(9600);

	a.setSpeed(200);
	b.setSpeed(200);

	a.run(RELEASE);
	b.run(RELEASE);
}

void test()
{
	Serial.println("test code");
	delay(2000);

	uint8_t i;

	// a.run(FORWARD);
	// b.run(FORWARD);
	// for (i=0; i<255; i++) {
	// 	a.setSpeed(i);
	// 	b.setSpeed(i);
	// 	delay(10);
	// }
	// a.run(BACKWARD);
	// b.run(BACKWARD);
	// for (i=0; i<255; i++) {
	// 	a.setSpeed(i);
	// 	b.setSpeed(i);
	// 	delay(10);
	// }
	a.run(RELEASE);
	b.run(RELEASE);

	Serial.println("motors stopped");
	delay(1000);
}

void FrontFucntion() {
		a.run(FORWARD);
  	b.run(FORWARD);
}

void mainFunction()
{
	char DataToRead[2];
	DataToRead[1] = '\n';
	
	Serial.readBytesUntil('\n',DataToRead, 2);
	char direction = DataToRead[0];
	
	int i = 1;
	while(DataToRead[i] != '\n' && i < 2) 
		i++;
	
	switch(direction){
		case 'S':
			a.setSpeed(0);
			b.setSpeed(0);
			delay(SMALL_DELAY_TIME);
			break;
		case 'G':
      		a.run(FORWARD);
      		b.run(FORWARD);
			a.setSpeed(MAX_VEL);
			b.setSpeed(MAX_VEL);
			delay(TINY_DELAY_TIME);
			break;
		case 'B':
			a.run(BACKWARD);
      		b.run(BACKWARD);
			a.setSpeed(BACK_VEL);
			b.setSpeed(BACK_VEL);
			delay(SMALL_DELAY_TIME);
			break;
		case 'R':
     	 	a.run(FORWARD);
      		b.run(FORWARD);
			a.setSpeed(MAX_VEL);
			b.setSpeed(0);
			delay(SMALL_DELAY_TIME);
			break;
		case 'L':
			a.run(FORWARD);
      		b.run(FORWARD);
			a.setSpeed(0);
			b.setSpeed(MAX_VEL);
			delay(SMALL_DELAY_TIME);
			break;
		case 'r':
			a.run(FORWARD);
     		b.run(FORWARD);
			a.setSpeed(MID_VEL);
			b.setSpeed(0);
			delay(SMALL_DELAY_TIME);
			break;
		case 'l':
			a.run(FORWARD);
      		b.run(FORWARD);
			a.setSpeed(0);
			b.setSpeed(MID_VEL);
			delay(SMALL_DELAY_TIME);
			break;
		default:
			a.setSpeed(0);
      		b.setSpeed(0);
			return;
    }
	if (direction == 'R' || direction == 'L')
	{
		delay(20);
    }
    else if(direction =='B')
	{
		delay(100);
    }
  	a.setSpeed(0);
  	b.setSpeed(0);
	delay(300); // 원래 300
	Serial.println(direction);
}

void loop()
{
	// test();
	mainFunction();
}
