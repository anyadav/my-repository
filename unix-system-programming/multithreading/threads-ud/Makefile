CFLAGS = -D_REENTRANT -g
LDLIBS = -lpthread

PROGS = thrd thread1

all: $(PROGS)

thrd: thr.c
	gcc $(CFLAGS) $< -o $@ $(LDLIBS)

thread1: thread1.c
	gcc $(CFLAGS) $< -o $@ $(LDLIBS)

clean:
	rm -f $(PROGS)

.PHONY: all clean
