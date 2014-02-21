CC = gcc

levenshtein.sqlext: src/levenshtein.c
	$(CC) -Wall -shared -fPIC -Isqlite3 -o levenshtein.sqlext src/levenshtein.c

clean:
	rm levenshtein.sqlext
