#include <stdio.h>
#include <unistd.h>

int main() {
	
	char buf[64] = { 0 };
	read(stdin, buf, 64);

	printf(buf);
	return 0;
}
