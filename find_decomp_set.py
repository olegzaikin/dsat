# Created on: 1 Oct 2024
# Author: Oleg Zaikin
# E-mail: zaikin.icc@gmail.com
#
# For a given CNF and an initial decomposition set, find the best decomposition
# set in D-SAT style, like it was published in Oleg Zaikin's PhD thesis.
#==============================================================================

import sys
import random
import os
import copy
import time

script = "find_decomp_set.py"
version = "0.0.1"

timelimit_sec = 5000

def write_clauses_cnf(cnf_name : str, var_num : int, \
					  main_cnf_clauses : list, one_lit_clauses : list):
	with open(cnf_name, 'w') as f:
		f.write('p cnf ' + str(var_num) + ' ' + str(len(main_cnf_clauses) + len(one_lit_clauses)) + '\n')
		for c in main_cnf_clauses:
			f.write(c + '\n')
		for c in one_lit_clauses:
			f.write(c + '\n')

def parse_solver_log(log):
	res = 'INDET'
	lines = log.split('\n')
	for line in lines:
		if len(line) < 12:
			continue
		if 's SATISFIABLE' in line:
			res = 'SAT'
		elif 's UNSATISFIABLE' in line:
			res = 'UNSAT'
	return res

def process_decomp_set(base_cnf_name : str, decomposition_set : list, \
					   solver : str, iter_num : int):
	assert(iter_num >= 0 and iter_num <= 32)
	s = base_cnf_name.split('bitM.cnf')[0]
	ind = s.rfind('_')
	assert(ind > 0)
	# Cut the bitM value in the base CNF name:
	cnf_name_part1 = s[:ind+1]
	assert(cnf_name_part1[-1] == '_')
	# Add a current bitM value to the base CNF name
	cur_cnf_name = cnf_name_part1 + str(iter_num) + 'bitM.cnf'
	print('CNF : ' + cur_cnf_name)
	# Read a CNF:
	main_cnf_clauses = []
	var_num = -1
	unit_clauses_decomp_set_num = 0
	with open(cur_cnf_name, 'r') as f:
		lines = f.read().splitlines()
		assert(len(lines) > 2)
		for line in lines:
			if line[0] == 'c':
				continue
			if line[0] == 'p':
				var_num = int(line.split()[2])
				continue
			words = line.split()
			assert(words[-1] == '0')
			# Unit clause:
			if len(words) == 2:
				# Don't collect dec-set-unit-clauses - they will be replaced:
				if abs(int(words[0])) in decomposition_set:
					unit_clauses_decomp_set_num += 1
					continue
			main_cnf_clauses.append(line)
		assert(unit_clauses_decomp_set_num == len(decomposition_set))
	assert(var_num > 0)
	print('var_num : ' + str(var_num))
	print(str(len(main_cnf_clauses)) + ' main clauses')
	# Generate random sample of binary sequences of d_set size:
	sample = []
	for i in range(sample_size):
		bin_seq = ''
		for j in range(len(decomposition_set)):
			rval = random.randint(0, 1)
			bin_seq += str(rval)
		sample.append(bin_seq)
	assert(len(sample) > 0)
	print('Random sample of size ' + str(len(sample)) + ' was generated')
	print('The first 3 elements are :')
	for i in range(3):
		print(sample[i])
	# For each element from the sample, make and solver a CNF:
	sum_runtime = 0
	for bin_seq in sample:
		assert(len(decomposition_set) >= len(bin_seq))
		one_lit_clauses = []
		for i in range(len(decomposition_set)):
			s = '' if bin_seq[i] == '1' else '-'
			s += str(decomposition_set[i]) + ' 0'
			one_lit_clauses.append(s)
		#print(one_lit_clauses)
		assert(len(one_lit_clauses) == len(decomposition_set))
		new_cnf_name = 'tmp.cnf'
		write_clauses_cnf(new_cnf_name, var_num, main_cnf_clauses, one_lit_clauses)
		sys_str = 'timeout ' + str(timelimit_sec) + ' ' + solver + ' ' + new_cnf_name
		t = time.time()
		cdcl_log = os.popen(sys_str).read()
		t = time.time() - t
		runtime = float(t)
		res = parse_solver_log(cdcl_log)
		if res == 'INDET':
			print('Too hard instance, res=INDET, runtime=' + str(runtime))
			break
		#print(res + ' ' + str(runtime) + ' sec')
		sum_runtime += runtime
	avg_runtime = sum_runtime / len(sample)
	return avg_runtime

print(script + ' of version ' + version + ' is running')
if len(sys.argv) == 2 and sys.argv[1] == '-v':
	exit(1)

if len(sys.argv) < 4:
	print('Usage : ' + script + ' cnf decomposition-set solver [sample-size]')
	print('  cnf               : a file in DIMACS format.')
	print('  decomposition-set : a file with an initial decomposition set')
	print('  solver            : a complete SAT solver')
	print('  sample-size       : size of a random sample')
	exit(1)

cnf_name = sys.argv[1]
assert('0bitM' in cnf_name)
decomposition_set_fname = sys.argv[2]
solver = sys.argv[3]
sample_size = 1000
if len(sys.argv) > 4:
	sample_size = int(sys.argv[4])
assert(sample_size >= 3)
print('cnf_name                : ' + cnf_name)
print('decomposition_set_fname : ' + decomposition_set_fname)
print('solver                  : ' + solver)
print('sample_size             : ' + str(sample_size))

decomposition_set = []
with open(decomposition_set_fname, 'r') as f:
	lines = f.read().splitlines()
	assert(len(lines) == 1)
	line = lines[0]
	if '-' in line:
		from_str = line.split('-')[0]
		to_str = line.split('-')[1]
		if from_str != '' and to_str != '':
			from_val = int(line.split('-')[0])
			to_val = int(line.split('-')[1])
			for i in range(from_val, to_val+1):
				assert(i > 0)
				decomposition_set.append(i)
	else:
		words = line.split()
		for w in words:
			assert(int(w) > 0)
			decomposition_set.append(int(w))
assert(len(decomposition_set) == 32)

print('decomposition_set :')
print(decomposition_set)

random.seed(0)

best_estim = -1
best_dec_set = -1
dec_set = copy.deepcopy(decomposition_set)
for i in range(32):
	print(dec_set)
	dec_set_size = len(dec_set)
	avg_runtime = process_decomp_set(cnf_name, dec_set, solver, i)
	print('avg_runtime  : ' + str(avg_runtime))
	assert(avg_runtime > 0)
	estim = avg_runtime * pow(2, dec_set_size)
	print('dec_set size : ' + str(dec_set_size))
	print('estim        : ' + str(estim) + ' sec')
	if best_estim < 0 or estim < best_estim:
		best_estim = estim
		best_dec_set = dec_set
	else:
		print('Break because the last estimation is worse than the best one.')
		break
	dec_set = dec_set[:-1]

print('***')
print('best_estim        : ' + str(best_estim))
print('best_dec_set_size : ' + str(len(best_dec_set)))
print('best_dec_set      :')
print(best_dec_set)
