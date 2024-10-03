// Created on: 2 Oct 2024
// Author: Oleg Zaikin
// E-mail: zaikin.icc@gmail.com
//
// For a given CNF and a set of its variables, vary all their values. 
//==============================================================================

#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <vector>
#include <assert.h>
#include <math.h>
#include <bitset>
#include <algorithm>

std::string version = "0.0.1";

unsigned TASK_VAR_NUM = 14;

std::vector<unsigned> read_decomp_set(const std::string decomp_set_name);
void solve(const std::string cnf_name, std::vector<unsigned> decomp_set);
std::vector<std::string> read_cnf(std::string cnf_name);

void print_version() {
	std::cout << "version: " << version << std::endl;
}

void print_usage() {
	std::cout << "Usage : solve_decomp_set CNF decomp-set" << std::endl;
}

int main(int argc, char **argv) 
{
	std::vector<std::string> str_argv;
	for (int i=0; i < argc; ++i) str_argv.push_back(argv[i]);
	assert(str_argv.size() == argc);
	if ((argc == 2 and str_argv[1] == "-h") or (argc < 3)) {
		print_usage();
		std::exit(EXIT_SUCCESS);
	}
	if (argc == 2 and str_argv[1] == "-v") {
		print_version();
		std::exit(EXIT_SUCCESS);
	}

    std::string cnf_name = str_argv[1];
    std::string decomp_set_name = str_argv[2];

    std::cout << "cnf_name        : " << cnf_name        << std::endl;
    std::cout << "decomp_set_name : " << decomp_set_name << std::endl;

    std::vector<unsigned> decomp_set = read_decomp_set(decomp_set_name);
    std::cout << "decomp_set : ";
    for (auto &x : decomp_set) std::cout << x << " ";
    std::cout << std::endl;

	solve(cnf_name, decomp_set);

    return 0;
}

void solve(const std::string cnf_name, std::vector<unsigned> decomp_set)
{
	// Read clauses from a CNF:
	std::vector<std::string> clauses = read_cnf(cnf_name);
	std::cout << "clauses size : " << clauses.size() << std::endl;

	unsigned increm_var_num = decomp_set.size() - TASK_VAR_NUM;
	std::cout << "increm_var_num : " << increm_var_num << std::endl;

	// Create cubes for varying the last increm_var_num variables:
	std::vector<std::string> cubes;
	for (unsigned i = 0; i < unsigned(pow(2, increm_var_num)); i++) {
		std::string str = std::bitset<32>( i ).to_string();
		str = str.substr(32 -  increm_var_num, increm_var_num);
		//std::cout << str << std::endl;
		std::stringstream sstream;
		sstream << "a ";
		for (unsigned j = 0; j < str.size(); j++) {
			sstream << (str[j] == '1' ? "" : "-") << decomp_set[TASK_VAR_NUM + j] << " ";
		}
		sstream << "0";
		cubes.push_back(sstream.str());
	}
	std::cout << "cubes size : " << cubes.size() << std::endl;

	//for (auto &x : cubes) std::cout << x << std::endl;

	for (unsigned i = 0; i < unsigned(pow(2, TASK_VAR_NUM)); i++) {
	//for (unsigned i = 0; i < 5; i++) {
		std::string str = std::bitset<32>( i ).to_string();
		str = str.substr(32 - TASK_VAR_NUM, TASK_VAR_NUM);
		//std::cout << str << std::endl;
		std::vector<std::string> decomp_unit_clauses;
		for (unsigned j = 0; j < str.size(); j++) {
			std::stringstream sstream;
			sstream << (str[j] == '1' ? "" : "-") << decomp_set[j] << " ";
			sstream << "0";
			decomp_unit_clauses.push_back(sstream.str());
		}
		//for (auto &x : decomp_unit_clauses) std::cout << x << std::endl;
		//std::cout << std::endl;
		std::stringstream sstream;
		std::string cleaned_cnf_name = cnf_name;
		unsigned start = cleaned_cnf_name.find("./");
		cleaned_cnf_name.erase(start, 2);
		start = cleaned_cnf_name.find(".cnf");
		cleaned_cnf_name.erase(start, 4);
		sstream << "task_" << i << "_" << cleaned_cnf_name << ".icnf";
		std::ofstream ofile(sstream.str());
		ofile << "p inccnf\n";
		for (auto &x : clauses) ofile << x << "\n";
		for (auto &x : decomp_unit_clauses) ofile << x << "\n";
		for (auto &x : cubes) ofile << x << "\n";
		ofile.close();
	}
}

// Read CNF's main clauses:
std::vector<std::string> read_cnf(std::string cnf_name) {;
	std::ifstream cnf_file(cnf_name);
	if (!cnf_file.is_open()) {
		std::cerr << "cnf_file " << cnf_name << " wasn't opened\n";
		std::exit(EXIT_FAILURE);
	}
	std::vector<std::string> clauses;
	std::string str;
	while (getline(cnf_file, str)) {
		if (str.empty() or str[0] == 'p' or str[0] == 'c') continue;
		clauses.push_back(str);
	}
	assert(not clauses.empty());
	return clauses;
}

// Read a decomposition set from a given file:
std::vector<unsigned> read_decomp_set(const std::string decomp_set_name) {
	std::vector<unsigned> decomp_set;
	std::ifstream decomp_set_file(decomp_set_name);
	if (!decomp_set_file.is_open()) {
		std::cerr << "decomp_set_file " << decomp_set_name << " wasn't opened\n";
		std::exit(EXIT_FAILURE);
	}
	std::string str;
	std::stringstream sstream;
	getline(decomp_set_file, str);
	sstream << str;
	std::string word;
	while (sstream >> word) {
        assert(word != "0");
        decomp_set.push_back(std::stoi(word));
    }
	decomp_set_file.close();
	assert(decomp_set.size() > 0);
	return decomp_set;
}
