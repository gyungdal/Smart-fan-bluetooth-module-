#include <stdio.h>

void main(){
  char* test = "power=20";
  int t;
  sscanf(strstr(test, "=") + 1, "%d", &t);
  printf("%d", t);
}
