cmake_minimum_required (VERSION 2.6)
project (bitstream)
add_executable (bitstream
	"src/main.cpp"
)
target_link_libraries (bitstream wiringPi)
