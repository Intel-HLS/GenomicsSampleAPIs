#include <iostream>
#include <sstream>
#include <iomanip>
#include <exception>
#include <mutex>          // std::mutex

#include "libquery.h"

std::mutex data_mutex;           // mutex for critical section

#define DATA_CHUNK 16
std::vector<LibBookKeeping> bookkeeping(DATA_CHUNK);

extern "C" uint64_t getToken() {
    data_mutex.lock();

    uint64_t i = 0;
    for (; i < bookkeeping.size(); ++i)
    {
        if (bookkeeping[i].isValid == false)
        {
            bookkeeping[i].isValid = true;
            data_mutex.unlock();
            
            #ifdef DEBUG
            std::cout << "Assigning Token : " << i << std::endl;
            #endif
            return i;
        }
    }

    // Will reach here if all entries are used
    bookkeeping.resize(bookkeeping.size() + DATA_CHUNK);
    bookkeeping[i].isValid = true;
    data_mutex.unlock();

    #ifdef DEBUG
    std::cout << "Assigning Token : " << i << std::endl;
    #endif

    return i;
}

extern "C" void clear_token(uint64_t token) {
    data_mutex.lock();
    #ifdef DEBUG
    std::cout << "Clearing Token : " << token << std::endl;
    #endif
    bookkeeping[token].clear();
    data_mutex.unlock();
}

/*
 * Populate the cell_t structure, and return the pointer
 */
cell_t *create_cell(const VariantCall &call, Globals *g_globals) {
    cell_t *p_cell = new cell_t();

    p_cell->id = call.get_row_idx();
#if DEBUG>1
    std::cout << " Reading Call at row " << p_cell->id;
    std::cout << " - has " << call.get_num_fields() << " fields " ;
#endif

    // Create vector objects that can hold each of the data types
    // If they are not used then they get deleted before we exit the function
    // Otherwise, they are cleaned up when the destructor is called.
    auto *m_int_data = new std::vector<return_data_t<int> *>();
    auto *m_int64_t_data = new std::vector<return_data_t<int64_t> *>();
    auto *m_unsigned_data = new std::vector<return_data_t<unsigned> *>();
    auto *m_uint64_t_data = new std::vector<return_data_t<uint64_t> *>();
    auto *m_float_data = new std::vector<return_data_t<float> *>();
    auto *m_double_data = new std::vector<return_data_t<double> *>();
    auto *m_string_data = new std::vector<return_data_t<char *> *>();

#if DEBUG>1
    std::cout << "[Attr,Type,Size] : [ "; 
#endif
    for( auto i = 0u; i < call.get_num_fields(); ++i ) {
        auto& field_ptr = call.get_field(i);   //returns unique_ptr<VariantFieldBase>&
        if(field_ptr.get())
        {
            unsigned size = 0;
            char* ptr = 0;
            bool allocated = false;
            //The function may allocate memory which must be freed by the client code
            //For example, when querying the ALT field, the function will allocate array of N char*
            auto type_index = field_ptr->get_C_pointers(size, reinterpret_cast<void**>(&ptr), allocated);
            if( type_to_int.find(type_index) == type_to_int.end())
            {
              std::cerr << "Unknown type for field idx " << i << ", skipping\n";
              continue;
            }
            // If the field is not part of the query_idx of interest then skip it
            if( g_globals->query_idx_to_attribute_idx.count(i) == 0 ) {
                continue;
            }
            unsigned attribute_idx = g_globals->query_idx_to_attribute_idx[i];
            g_globals->allocated_map[g_globals->attributes->at(attribute_idx)] = allocated;
#if DEBUG>1
            std::cout << "[ " << g_globals->attributes->at(attribute_idx);
            std::cout << "," << get_type_string(type_index);
            std::cout << "," << size << " ] ; ";
#endif
            switch(type_to_int[type_index])
            {
                case POINTER_INT:
                  m_int_data->push_back(
                        create_return_data<int>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<int *>(ptr)));
                  break;
                case POINTER_INT64_T:
                  m_int64_t_data->push_back(
                        create_return_data<int64_t>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<int64_t *>(ptr)));
                  break;  
                case POINTER_UNSIGNED:
                  m_unsigned_data->push_back(
                        create_return_data<unsigned>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<unsigned *>(ptr)));
                  break;
                case POINTER_UINT64_T:
                  m_uint64_t_data->push_back(
                        create_return_data<uint64_t>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<uint64_t *>(ptr)));
                  break;
                case POINTER_FLOAT:
                  m_float_data->push_back(
                        create_return_data<float>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<float *>(ptr)));
                  break;
                case POINTER_DOUBLE:
                  m_double_data->push_back(
                        create_return_data<double>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<double *>(ptr)));
                  break;
                case POINTER_CHAR_PTR:
                  m_string_data->push_back(
                        create_return_data<char *>(g_globals->attributes->at(attribute_idx),
                                                   size,
                                                   reinterpret_cast<char **>(ptr)));
                  break;
            }
        }
    }
#if DEBUG>1
    std::cout << std::endl;
#endif

    // int data
    p_cell->int_count = m_int_data->size();
    if( p_cell->int_count == 0 ) {
        p_cell->int_data = NULL;
        delete m_int_data;
    }
    else {
        p_cell->int_data = &((*m_int_data)[0]);
        g_globals->int_data.push_back(m_int_data);
    }
    // int64_t data
    p_cell->int64_t_count = m_int64_t_data->size();
    if( p_cell->int64_t_count == 0 ) {
        p_cell->int64_t_data = NULL;
        delete m_int64_t_data;
    }
    else {
        p_cell->int64_t_data = &((*m_int64_t_data)[0]);
        g_globals->int64_t_data.push_back(m_int64_t_data);
    }
    // unsigned data
    p_cell->unsigned_count = m_unsigned_data->size();
    if( p_cell->unsigned_count == 0 ) {
        p_cell->unsigned_data = NULL;
        delete m_unsigned_data;
    }
    else {
        p_cell->unsigned_data = &((*m_unsigned_data)[0]);
        g_globals->unsigned_data.push_back(m_unsigned_data);
    }
    // uint64_t data
    p_cell->uint64_t_count = m_uint64_t_data->size();
    if( p_cell->uint64_t_count == 0 ) {
        p_cell->uint64_t_data = NULL;
        delete m_uint64_t_data;
    }
    else {
        p_cell->uint64_t_data = &((*m_uint64_t_data)[0]);
        g_globals->uint64_t_data.push_back(m_uint64_t_data);
    }
    // float data
    p_cell->float_count = m_float_data->size();
    if( p_cell->float_count == 0 ) {
        p_cell->float_data = NULL;
        delete m_float_data;
    }
    else {
        p_cell->float_data = &((*m_float_data)[0]);
        g_globals->float_data.push_back(m_float_data);
    }
    // double data
    p_cell->double_count = m_double_data->size();
    if( p_cell->double_count == 0 ) {
        p_cell->double_data = NULL;
        delete m_double_data;
    }
    else {
        p_cell->double_data = &((*m_double_data)[0]);
        g_globals->double_data.push_back(m_double_data);
    }
    // string data
    p_cell->string_count = m_string_data->size();
    if( p_cell->string_count == 0 ) {
        p_cell->string_data = NULL;
        delete m_string_data;
    }
    else {
        p_cell->string_data = &((*m_string_data)[0]);
        g_globals->string_data.push_back(m_string_data);
    }

    return p_cell;
}

// Update cell_array_t will all the cells from a given column
cell_array_t *create_cell_array(Variant &variant, Globals *g_globals) {
    cell_array_t *p_cell_array = new cell_array_t();

    p_cell_array->start = variant.get_column_begin();
    p_cell_array->end = variant.get_column_end();

    // Since we know the number of calls there are, size the data vectors
    auto size = p_cell_array->end - p_cell_array->start + 1;

    std::vector<cell_t *> *m_Calls = new std::vector<cell_t *>();

    for(Variant::valid_calls_iterator iterator = variant.begin(); 
        iterator != variant.end(); ++iterator ) {
        m_Calls->push_back(create_cell(*iterator, g_globals));
    }

    p_cell_array->count = m_Calls->size();
    p_cell_array->cells = &((*m_Calls)[0]); 

    g_globals->Calls.push_back(m_Calls);

    return p_cell_array;
}

/**
 * Reads the variants info and populates the result_array_t 
 */
result_array_t *create_result_array(uint64_t token) {
    Globals *g_globals = bookkeeping[token].data;
    result_array_t *p_result_array = new result_array_t();
    g_globals->p_result_array = p_result_array;

    // Populate the count and create the results array **
    p_result_array->count = g_globals->variants.size();
    p_result_array->results = new cell_array_t*[p_result_array->count];

    if (g_globals->paging_info.is_query_completed())
    {
        p_result_array->token = NULL;
    }
    else {
        const std::string &str_token = g_globals->paging_info.get_page_end_token();
        p_result_array->token = const_cast<char *>(str_token.c_str());
    }
#ifdef DEBUG
    std::cout << "# Variants: " << g_globals->variants.size() << std::endl;
#endif
    uint64_t idx = 0;
    for( Variant &v : g_globals->variants ) {
#if DEBUG>2
        std::cout << "@ variant: " << idx << std::endl;
        v.print(std::cout, &g_globals->query_config);
#endif

        p_result_array->results[idx] = create_cell_array(v, g_globals); 
        ++idx;
    }
#if DEBUG>3
    print_result_array(p_result_array);
#endif
    return p_result_array;
}

/**
 * Use this function to free the memory after the data from query function has been processed
 */
extern "C" void cleanup(uint64_t token) {
    clear_token(token); 
}

void parseCSV(char *csv, std::vector<std::string> &output) {
    std::string str(csv);
    char *input = new char[str.size() + 1];
    strcpy(input, str.c_str());

    char *token = strtok(input, ",");
    while( token != NULL ) {
        output.push_back(std::string(token));
        token = strtok(NULL, ",");
    }
    delete [] input;
}

/** 
 * Setup the attributes of interest for the query before calling query_column
 * attributes_list is a comma separated list of attribute names
 */ 
extern "C" bool setup_attributes(char *attributes_list, uint64_t token) {
    Globals *g_globals = bookkeeping[token].data;
    std::vector<std::string> *attributes = new std::vector<std::string>();

    parseCSV(attributes_list, *attributes);
#ifdef DEBUG
    std::cout << "\tAttributes : ";
    for( auto s : *attributes ) {
        std::cout << s << ", ";
    }
    std::cout << std::endl;
#endif

    if( g_globals->attributes != NULL ) { 
        if( *attributes == *(g_globals->attributes) ) {
            return true;
        }
        else {
            delete g_globals->attributes;
        }
    }

    g_globals->query_config.clear();
    g_globals->query_config.set_attributes_to_query(*attributes);

    g_globals->attributes = attributes;
    g_globals->query_idx_is_set = false;
    g_globals->query_idx_to_attribute_idx.clear();

    return true;
}

/**
 * API that provides the option of filtering only the rows by row id.
 * Remember that the row id here is a tile DB row id.
 */
extern "C" void filter_rows(char *data, uint64_t token) {
    Globals *g_globals = bookkeeping[token].data;

    std::vector<std::string> input_list;
    parseCSV(data, input_list);

    std::vector<int64_t> rows(input_list.size());
    for( uint64_t i = 0; i < input_list.size(); ++i ) {
        rows[i] = std::stoll(input_list[i]);
    }

#ifdef DEBUG
    std::cout << "Filtering " << rows.size() << " Rows " << std::endl;
#endif
#if DEBUG>1
    for( auto& r : rows ) {
        std::cout << r << ", ";
    }
    std::cout << std::endl;
#endif

    if( g_globals->query_config.is_bookkeeping_done() ) {
        g_globals->query_config.update_rows_to_query(rows);
    }
    else {
            g_globals->query_config.set_rows_to_query(rows);
    }
}

/**
 * set_page_size is used to request tile db to give only the
 * number of variants asked by the page size or lesser and not
 * any more
 */
void set_page_size(unsigned page_size, uint64_t token) {
#ifdef DEBUG
    std::cout << "[libquery] Set Page Size : " << page_size << std::endl;
#endif
    Globals *g_globals = bookkeeping[token].data;
    g_globals->paging_info.set_page_size(page_size);
}

/**
 * set_page_token is used when a token was returned from the previous query
 * and the user wishes to query again from where tile DB left off
 */
void set_page_token(char *tile_token, uint64_t token) {
    if (tile_token)
    {
    #ifdef DEBUG
        std::cout << "[libquery] Set Page Token : " << tile_token << std::endl;
    #endif
        Globals *g_globals = bookkeeping[token].data;
        const std::string str_token(tile_token);
        g_globals->paging_info.set_page_end_token(str_token);
    }
}

/**
 * Helper function that fetches the data from tile DB and populates the Variant Structure
 * This can be processed further based on the requirement from the calling function
 */
bool fetch_data(char *workspace, char *array_name,
                uint64_t start, uint64_t end,
                uint64_t token, int64_t page_size = -1,
                char *page_token = NULL) {
    if( start > end ) {
        std::cerr << "ERROR: start (" << start << ") > end (" << end << ")" << std::endl;
        return false;
    }

    Globals *g_globals = bookkeeping[token].data;

    // Cleanout any variants that was there in the previous call 
    g_globals->cleanup();

#ifdef DEBUG
    std::cout << "[" << token << "] ";
    std::cout << "Workspace : " << workspace << " Array : " << array_name << std::endl;
    std::cout << "[" << token << "] ";
    std::cout << "Adding range [" << start << ", " << end << "] to query_config" << std::endl;
#endif
    try {
        // Setup query config with the new range query
        g_globals->query_config.set_column_interval_to_query(start, end);

        if (page_size >= 0)
        {
            set_page_size((unsigned)page_size, token);
        }
        if (page_token)
        {
            set_page_token(page_token, token);
        }

#ifdef DEBUG
        std::cout << "[" << token << "] ";
        std::cout << "Running Query ... " << std::endl;
#endif
        db_query_column_range(workspace, array_name, 0, g_globals->variants, g_globals->query_config, &(g_globals->paging_info));

        // query_idx will not be updated until the first query is sent
        if( !g_globals->query_idx_is_set ) {
            unsigned query_idx;
            unsigned index = 0;
#ifdef DEBUG
            std::cout << "[" << token << "] ";
            std::cout << "Input Attributes : ";
#endif
            for( std::string attribute : *g_globals->attributes ) { 
                if( g_globals->query_config.get_query_idx_for_name(attribute, query_idx) ) { 
                    g_globals->query_idx_to_attribute_idx[query_idx] = index;
#ifdef DEBUG
                    std::cout << attribute; 
                    std::cout << " [" << query_idx << ":" << index << "] ";
#endif
                    ++index;
                }
            }
#ifdef DEBUG
            std::cout << std::endl;
#endif
            g_globals->query_idx_is_set = true;
        }
    }
    catch( std::exception& e ) {
        std::cerr << e.what() << std::endl;
        return false;
    }
    return true;
}

/**
 * query_column is the externally visible library API that
 * takes the workspace and the array name for the tileDB
 * takes a range of positions of interest and returns a result_array_t
 */
extern "C" result_array_t *query_column(char *workspace, char *array_name,
                                        uint64_t start, uint64_t end,
                                        uint64_t token, int64_t page_size,
                                        char *page_token) {
    if (fetch_data(workspace, array_name, start, end, token, page_size, page_token)) {
        return create_result_array(token);
    }
    else {
        return NULL;
    }
}
