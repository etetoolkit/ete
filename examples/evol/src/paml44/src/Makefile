PRGS =  baseml codeml basemlg mcmctree pamp evolver yn00 chi2 
CC = cc # cc, gcc, cl

CFLAGS = -O4 -funroll-loops -fomit-frame-pointer -finline-functions

#MAC OSX G5:
#CFLAGS = -mcpu=G5 -O4 -funroll-loops -fomit-frame-pointer -finline-functions

#MAC OSX intel:
#CFLAGS = -march=pentium-m -O4 -funroll-loops -fomit-frame-pointer -finline-functions

#CFLAGS = -O4
#CFLAGS = -fast
#CFLAGS = -m64 -march=opteron -mtune=opteron -ansi -O3 -funroll-loops -fomit-frame-pointer -finline-functions 
#CFLAGS = -march=athlon -mcpu=athlon -O4 -funroll-loops -fomit-frame-pointer -finline-functions
#CFLAGS = -march=pentiumpro -mcpu=pentiumpro -O4 -funroll-loops -fomit-frame-pointer -finline-functions 

LIBS = -lm # -lM

all : $(PRGS)

baseml : baseml.c tools.c
	$(CC) $(CFLAGS) -o $@ baseml.c tools.c $(LIBS)
basemlg : basemlg.c tools.c
	$(CC) $(CFLAGS) -o $@ basemlg.c tools.c $(LIBS)
codeml : codeml.c tools.c
	$(CC) $(CFLAGS) -o $@ codeml.c tools.c $(LIBS)
evolver : evolver.c tools.c 
	$(CC) $(CFLAGS) -o $@ evolver.c tools.c $(LIBS)
pamp : pamp.c tools.c 
	$(CC) $(CFLAGS) -o $@ pamp.c tools.c $(LIBS)
mcmctree : mcmctree.c tools.c
	$(CC) $(CFLAGS) -o $@ mcmctree.c tools.c $(LIBS)
yn00: yn00.c tools.c
	$(CC) $(CFLAGS) -o $@ yn00.c tools.c $(LIBS)
chi2 : chi2.c
	$(CC) $(CFLAGS) -o $@ chi2.c $(LIBS)
