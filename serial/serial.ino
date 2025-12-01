#include	<AFMotor.h>

// motor speed
#define MAX_VEL 200
#define MID_VEL 150

#define BACK_VEL 200  // 후진 속도

#define SMALL_DELAY_TIME 120  // 회전 시간
#define TINY_DELAY_TIME 100   // 직진 시간
#define BACK_DELAY_TIME 80    // 후진 시간


/*
motor pin number
a: right motor
b: left motor
*/

AF_DCMotor	a(3);
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
	// 시리얼 데이터가 없으면 리턴
	if (Serial.available() == 0) {
		return;
	}

	// 버퍼에 있는 가장 최신 명령만 읽기 (오래된 명령 무시)
	// 최대 50개까지만 읽어서 성능 보장
	char direction = '\0';
	int readCount = 0;
	while(Serial.available() > 0 && readCount < 50) {
		char c = Serial.read();
		if (c != '\n' && c != '\r') {
			direction = c;
		}
		readCount++;
	}

	// 남은 버퍼 데이터는 모두 클리어
	while(Serial.available() > 0) {
		Serial.read();
	}

	// 유효한 명령이 없으면 리턴
	if (direction == '\0') {
		return;
	}

	switch(direction){
		case 'S':
			a.run(RELEASE);
			b.run(RELEASE);
			a.setSpeed(0);
			b.setSpeed(0);
			break;
		case 'G':
			a.run(BACKWARD);
			b.run(BACKWARD);
			a.setSpeed(MAX_VEL);
			b.setSpeed(MAX_VEL);
			break;
		case 'B':
			a.run(FORWARD);
			b.run(FORWARD);
			a.setSpeed(BACK_VEL);
			b.setSpeed(BACK_VEL);
			delay(BACK_DELAY_TIME);
			break;
		case 'R':
			a.run(BACKWARD);
			b.run(BACKWARD);
			a.setSpeed(MAX_VEL);
			b.setSpeed(0);
			break;
		case 'L':
			a.run(BACKWARD);
			b.run(BACKWARD);
			a.setSpeed(0);
			b.setSpeed(MAX_VEL);
			break;
		case 'r':
			a.run(BACKWARD);
			b.run(BACKWARD);
			a.setSpeed(MAX_VEL);
			b.setSpeed(0);
			break;
		case 'l':
			a.run(BACKWARD);
			b.run(BACKWARD);
			a.setSpeed(0);
			b.setSpeed(MAX_VEL);
			break;
		default:
			a.run(RELEASE);
			b.run(RELEASE);
			return;
	}
	Serial.println(direction);
}

void loop()
{
	// test();
	mainFunction();
	delay(10);  // CPU 과부하 방지 및 안정적인 시리얼 통신
}
