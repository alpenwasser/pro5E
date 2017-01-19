#include <iostream>
#include <wiringPi.h>
#include <sys/time.h>
#include <fstream>

enum BufferDataSlots
{
	BUF_DATA,
	BUF_TIME,

	BUF_NUM_SLOTS
};

#define NUM_MEASUREMENTS 25000
#define PIN_CLOCK        17
#define PIN_DATA         18

void initialise_gpio()
{
	wiringPiSetupGpio();

	pinMode(PIN_CLOCK, INPUT);
	pinMode(PIN_DATA, INPUT);	
}

void acquire_data(int bitstream_buf[BUF_NUM_SLOTS][NUM_MEASUREMENTS])
{
	timeval end, start;

	gettimeofday(&start, 0);
	for(int i = 0; i != NUM_MEASUREMENTS; ++i)
	{
		// wait for clock to go positive
		while(digitalRead(PIN_CLOCK) == 0) {}

		gettimeofday(&end, 0);
		bitstream_buf[BUF_DATA][i] = digitalRead(PIN_DATA);
		bitstream_buf[BUF_TIME][i] = ((end.tv_sec * 1000000) + end.tv_usec) - ((start.tv_sec * 1000000) + start.tv_usec);

		// wait for clock to go negative
		while(digitalRead(PIN_CLOCK) == 1) {}
	}
}

void save_data(const int bitstream_buf[BUF_NUM_SLOTS][NUM_MEASUREMENTS])
{
	std::ofstream data_file("bit_stream.txt");
	std::ofstream clock_file("vin_clk.txt");
	for(int i = 0; i != NUM_MEASUREMENTS; ++i)
	{
		long double time_usec = bitstream_buf[BUF_TIME][i] / 1000000.0;
		clock_file << time_usec << "     " << "1.2" << "     " << std::endl;
		if(bitstream_buf[BUF_DATA][i] == 1)
			data_file << time_usec << "     " << "3.0000" << std::endl;
		else
			data_file << time_usec << "     " << "1.0e-9" << std::endl;
	}
}

int main()
{
	initialise_gpio();

	/*
	 * The IO operations may be too slow, so we store the measurements
         * to a temporary buffer and save the buffer later.
	 */
	int bitstream_buf[BUF_NUM_SLOTS][NUM_MEASUREMENTS];
	acquire_data(bitstream_buf);
	save_data(bitstream_buf);

	std::cout << "done" << std::endl;
	return 0;
}

