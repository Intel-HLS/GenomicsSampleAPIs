#include "query.h"

#include <iostream>
#include <vector>
#include <chrono>
#include <ctime>

// Helper Functions to print the data structure
// Results Array Print
extern "C" void print_result_array(result_array_t *in_result_array) {
    std::cout << "Results: Count: " << in_result_array->count << "\t";
    if( in_result_array->token ) { 
        std::cout << "Token: " << in_result_array->token;
    }
    std::cout << std::endl;
    for( uint64_t i = 0; i < in_result_array->count; ++i ) {
        print_cell_array(in_result_array->results[i]);
        std::cout << std::endl;
    }
}

void print_cell_array(cell_array_t *in_cell_array) {
    std::cout << "Variant: [" << in_cell_array->start;
    std::cout << " : " << in_cell_array->end << " ]" << std::endl;
    for(uint64_t i = 0; i < in_cell_array->count; ++i ) {
        print_cell(in_cell_array->cells[i]);
        std::cout << std::endl;
    }
}

template<class T>
void print_vector(T **data, uint64_t &count) {
    for(auto idx = 0; idx < count; ++idx ) {
        auto *array = data[idx];
        std::cout << array->attribute << " [ ";
        for( auto i = 0; i < array->count; ++i ) {
            std::cout << array->data[i] << ",";
        }
        std::cout << " ]; ";
    }
}

void print_cell(cell_t *in_cell) {
    std::cout << "Call: ID " << in_cell->id << "; ";
    print_vector<return_data_t<int>>(in_cell->int_data, in_cell->int_count);
    print_vector<return_data_t<int64_t>>(in_cell->int64_t_data, in_cell->int64_t_count);
    print_vector<return_data_t<unsigned>>(in_cell->unsigned_data, in_cell->unsigned_count);
    print_vector<return_data_t<uint64_t>>(in_cell->uint64_t_data, in_cell->uint64_t_count);
    print_vector<return_data_t<float>>(in_cell->float_data, in_cell->float_count);
    print_vector<return_data_t<double>>(in_cell->double_data, in_cell->double_count);
    print_vector<return_data_t<char *>>(in_cell->string_data, in_cell->string_count);
}

void print_log(std::ostream& output, const char *str) {
    // std::chrono::milliseconds time_now = std::chrono::duration_cast<std::chrono::milliseconds>std::chrono::system_clock::now();
    auto now = std::chrono::high_resolution_clock::now();
    auto tt = std::chrono::high_resolution_clock::to_time_t(now);
    auto now_str = std::string(ctime(&tt));
    now_str[now_str.size() - 1] = '\0';
    std::chrono::time_point<std::chrono::high_resolution_clock, std::chrono::milliseconds> t = std::chrono::time_point_cast<std::chrono::milliseconds>(now);
    // auto time_now = std::chrono::duration_cast<std::chrono::milliseconds>();
    output << "[" << now_str << "][" << t.time_since_epoch().count() << " mS] " << str << std::endl;
}
