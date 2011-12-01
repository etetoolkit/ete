GENERAL_OPTIONS  = -Wall -W -pedantic
DEBUG_OPTIONS    = -g3
OPTIMIZE_OPTIONS = -O4

COMPILE_OPTS = $(GENERAL_OPTIONS) $(OPTIMIZE_OPTIONS)

OBJS = Seq.o Mseq.o MIter.o etree.o emodel.o

.PHONY: clean

default: gerpcol gerpelem

gerpcol.o:	gerpcol.cc etree.o emodel.o MIter.o Mseq.o Seq.o
	g++ $(COMPILE_OPTS) -c gerpcol.cc

gerpcol:	gerpcol.o $(GERPCOL_LIBFILE)
	g++ $(COMPILE_OPTS) -o gerpcol MIter.o Mseq.o Seq.o gerpcol.o etree.o emodel.o $(GERPCOL_LIBFILE)

gerpelem.o:	gerpelem.cc
	g++ $(COMPILE_OPTS) -c gerpelem.cc

gerpelem:	gerpelem.o
	g++ $(COMPILE_OPTS) -o gerpelem gerpelem.o

analyze:	analyze.o
	g++ $(COMPILE_OPTS) -o analyze analyze.o

filter:	filter.o
	g++ $(COMPILE_OPTS) -o filter filter.o

$(GERPCOL_LIBFILE):	$(OBJS)
	ar -rc $(GERPCOL_LIBFILE) $(OBJS)
	ranlib $(GERPCOL_LIBFILE)

Seq.o:	Seq.cc Seq.h Vec.h
	g++ $(COMPILE_OPTS) -c Seq.cc

Mseq.o:	Mseq.cc $(MSEQ_H)
	g++ $(COMPILE_OPTS) -c Mseq.cc

MIter.o:	MIter.cc MIter.h Seq.h Vec.h
	g++ $(COMPILE_OPTS) -c MIter.cc

etree.o:	etree.cc etree.h MIter.o Mseq.o Seq.o
	g++ $(COMPILE_OPTS) -c etree.cc

emodel.o:	emodel.cc emodel.h MIter.o Mseq.o Seq.o
	g++ $(COMPILE_OPTS) -c emodel.cc

clean:
	rm -f *.o $(GERPCOL_LIBFILE) gerpcol gerpelem analyze filter *~ core.*
