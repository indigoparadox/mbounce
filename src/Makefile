
# vim: ft=make noexpandtab

OBJECTS := mbounce.o
OBJECTS_TESTS := check.o check_mbounce.o check_mext2.o

BINDIR_LINUX = ../bin/linux
BINDIR_MSP430G2553 = ../bin/msp430g2553

MD=mkdir -v -p

$(BINDIR_LINUX)/libmbounce.a: OBJDIR := ../obj/linux
$(BINDIR_LINUX)/libmbounce.a: CFLAGS += \
	-DCHECK \
	-DDEBUG

$(BINDIR_MSP430G2553)/libmbounce.a: OBJDIR := ../obj/msp430g2553
$(BINDIR_MSP430G2553)/libmbounce.a: AR := msp430-ar
$(BINDIR_MSP430G2553)/libmbounce.a: CC := msp430-gcc
$(BINDIR_MSP430G2553)/libmbounce.a: CFLAGS += \
	-mmcu=msp430g2553 \
	-g \
	-pg \
	-Os \
	-fno-builtin \
	-ffreestanding \
	-nostdlib

test_mbounce: LDFLAGS += $(shell pkg-config --libs check) -L. -lmbounce
test_mbounce: CFLAGS += -DCHECK -g -Wall -Werror
test_mbounce: OBJDIR := ../obj/test_mbounce

all: $(BINDIR_LINUX)/libmbounce.a $(BINDIR_MSP430G2553)/libmbounce.a

test_mbounce: disk.o $(BINDIR_LINUX)/libmbounce.a $(addprefix ../obj/linux/,$(OBJECTS_TESTS))
	$(CC) -o $@ $^ -L$(BINDIR_LINUX) $(LDFLAGS)

$(BINDIR_LINUX)/libmbounce.a: $(addprefix ../obj/linux/,$(OBJECTS))
	$(MD) $(BINDIR_LINUX)
	$(AR) rcs $@ $^

$(BINDIR_MSP430G2553)/libmbounce.a: $(addprefix ../obj/msp430g2553/,$(OBJECTS))
	$(MD) $(BINDIR_MSP430G2553)
	$(AR) rcs $@ $^

../obj/linux/check.o: ../tests/check.c
	$(MD) $(OBJDIR)
	$(CC) -c -o $@ $< $(CFLAGS)

../obj/linux/%.o: $(notdir %.c)
	$(MD) $(OBJDIR)
	$(CC) -c -o $@ $< $(CFLAGS)

../obj/msp430g2553/%.o: $(notdir %.c)
	$(MD) $(OBJDIR)
	$(CC) -c -o $@ $< $(CFLAGS)

.PHONY: clean docs

docs:
	doxygen doxyfile

clean:
	rm -rf ../obj; \
	rm -f test_mbounce; \
	rm -rf ../bin; \
	rm -rf ../doc

