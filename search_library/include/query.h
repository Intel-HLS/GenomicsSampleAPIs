#ifndef _QUERY_H_
#define _QUERY_H_

#include <cstdint>
#include <string>
#include <vector>

/**
 * Templated return data class that stores the 
 * - name of the attribute
 * - num of elements in the data vector
 * - data is a vector of the elements of type T
 */
template<class T> struct return_data_t {
    char *attribute;
    uint64_t count;
    T *data;
};

/**
 * Templated helper function that creates an object of the return_data_t
 * with the appropriate type, assigns the pointers and returns the object
 */
template<class T>
return_data_t<T> *create_return_data(const std::string &attribute,
        const int &count, T *value) {
    return_data_t<T> *p_return_data = new return_data_t<T>();

    p_return_data->attribute = const_cast<char *>(attribute.c_str());
    p_return_data->count = count;
    p_return_data->data = value;

    return p_return_data;
}

/*
 * Data that is stored per cell in TileDB
 * e.g. Think of this structure as the GACall under GA4GH
 */
struct cell_t {
    uint64_t id;
    uint64_t int_count;
    uint64_t int64_t_count;
    uint64_t unsigned_count;
    uint64_t uint64_t_count;
    uint64_t float_count;
    uint64_t double_count;
    uint64_t string_count;
    return_data_t<int> **int_data;
    return_data_t<int64_t> **int64_t_data;
    return_data_t<unsigned> **unsigned_data;
    return_data_t<uint64_t> **uint64_t_data;
    return_data_t<float> **float_data;
    return_data_t<double> **double_data;
    return_data_t<char *> **string_data;
};

/**
 * Generic array of cells that is 1-dimentional
 * Keeping this structure agnostic of column or row 
 * for future scalability
 * e.g. Think of this structure as the GAVariant under GA4GH
 */
struct cell_array_t {
    uint64_t count;
    uint64_t start;
    uint64_t end;
    cell_t **cells;
};

/**
 * Result is an array of cell_array_t
 * This can be array of rows or columns
 */
struct result_array_t {
    uint64_t count;
    // token is required by the GA4GH API
    char *token;
    cell_array_t **results;
};

extern "C" uint64_t getToken();

extern "C" void clear_token(uint64_t token);

/** 
 * Setup the attributes of interest for the query before calling query_column
 * attributes_list is a comma separated list of attribute names
 */
extern "C" bool setup_attributes(char *attributes_list, uint64_t token);

/**
 * API that provides the option of filtering only the rows by row id.
 * Remember that the row id here is a tile DB row id.
 */
extern "C" void filter_rows(char *data, uint64_t token);

/**
 * query_column is the externally visible library API that
 * takes the workspace and the array name for the tileDB
 * takes a range of positions of interest and returns a result_array_t
 */
extern "C" result_array_t *query_column(char *workspace, char * array_name,
        uint64_t start, uint64_t end, uint64_t token, int64_t page_size = -1,
        char *page_token = NULL);

/*
 * Use this function to free the memory after the data from query function 
 * has been processed
 */
extern "C" void cleanup(uint64_t token);

/**
 * Helper Functions to print the data structure
 * Results Array Print
 */
extern "C" void print_result_array(result_array_t *in_result_array);

void print_cell_array(cell_array_t *in_cell_array);

void print_cell(cell_t *in_cell);

void print_log(std::ostream& output, const char *str);

#endif
