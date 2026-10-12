# Compilação da versão em C do Compartilha+
CC      = gcc
CFLAGS  = -std=c99 -Wall -Wextra -pedantic
FONTES  = main.c util.c estoque.c

compartilha: $(FONTES) util.h estoque.h
	$(CC) $(CFLAGS) $(FONTES) -o compartilha

limpar:
	rm -f compartilha compartilha.exe *.dat
