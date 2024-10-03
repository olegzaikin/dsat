CPP = g++
CPPFLAGS = -O3 -std=c++20

solve_decomp_set: solve_decomp_set.o
	${CPP} ${CPPFLAGS} solve_decomp_set.o -o solve_decomp_set

solve_decomp_set.o: solve_decomp_set.cpp
	${CPP} ${CPPFLAGS} solve_decomp_set.cpp -c

clean:
	rm -rf *.o
	rm solve_decomp_set
	clear
