#include	<AFMotor.h>

// motor speed
#define MAX_VEL 255
#define MID_VEL 200

#define BACK_VEL 200  // 후진 속도

// 소회전 속도 (부드러운 회전을 위해)
#define SMALL_TURN_VEL 150

/*
motor pin number
a: right motor
b: left motor
*/

AF_DCMotor	a(3);
AF_DCMotor	b(4);

void setup()
{
	Serial.begin(9600);
	Serial.setTimeout(10);  // 타임아웃을 짧게 설정

	a.setSpeed(200);
	b.setSpeed(200);

	a.run(RELEASE);
	b.run(RELEASE);
}

void mainFunction()
{
	if (Serial.available() <= 0) {
		return;  // 데이터가 없으면 즉시 리턴
	}

	char direction = Serial.read();

	// 개행문자 제거
	if (direction == '\n' || direction == '\r') {
		return;
	}

	switch(direction){
		case 'S':
			a.setSpeed(0);
			b.setSpeed(0);
			a.run(RELEASE);
			b.run(RELEASE);
			break;

		case 'G':
			a.setSpeed(MAX_VEL);
			b.setSpeed(MAX_VEL);
			a.run(BACKWARD);
			b.run(BACKWARD);
			break;

		case 'B':
			a.setSpeed(BACK_VEL);
			b.setSpeed(BACK_VEL);
			a.run(FORWARD);
			b.run(FORWARD);
			break;

		case 'R':
			a.setSpeed(MAX_VEL);
			b.setSpeed(0);
			a.run(BACKWARD);
			b.run(BACKWARD);
			break;

		case 'L':
			a.setSpeed(0);
			b.setSpeed(MAX_VEL);
			a.run(BACKWARD);
			b.run(BACKWARD);
			break;

		case 'r':
			a.setSpeed(MAX_VEL);
			b.setSpeed(SMALL_TURN_VEL);
			a.run(BACKWARD);
			b.run(BACKWARD);
			break;

		case 'l':
			a.setSpeed(SMALL_TURN_VEL);
			b.setSpeed(MAX_VEL);
			a.run(BACKWARD);
			b.run(BACKWARD);
			break;

		default:
			return;
	}

	Serial.println(direction);
}

void loop()
{
	mainFunction();
}
