CFLAGS = -D_REENTRANT -g
LDLIBS = -lpthread

PROGS = thrd thread thread-messagepassing thread-cancellation thread-synchronization-sem

all: $(PROGS)

thrd: parallel-executing-threads.c
	gcc $(CFLAGS) $< -o $@ $(LDLIBS)

%: %.c
	gcc $(CFLAGS) $< -o $@ $(LDLIBS)

clean:
	rm -f $(PROGS)

.PHONY: all clean
