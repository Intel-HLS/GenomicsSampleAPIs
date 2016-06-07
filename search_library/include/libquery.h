#ifndef _LIBQUERY_H_
#define _LIBQUERY_H_

#include <vector>
#include <unordered_map>
#include <typeindex>

#include "query.h"
#include "libtiledb_variant.h"

class Globals {
  public:
    std::vector<Variant> variants;
    VariantQueryConfig query_config;
    GA4GHPagingInfo paging_info;

    std::vector<std::string> *attributes;
    std::unordered_map<unsigned, unsigned> query_idx_to_attribute_idx;
    std::unordered_map<std::string, bool> allocated_map;

    result_array_t *p_result_array;
    std::vector<std::vector<cell_t *> *>Calls;

    std::vector<std::vector<return_data_t<int> *> *> int_data;
    std::vector<std::vector<return_data_t<int64_t> *> *> int64_t_data;
    std::vector<std::vector<return_data_t<unsigned> *> *> unsigned_data;
    std::vector<std::vector<return_data_t<uint64_t> *> *> uint64_t_data;
    std::vector<std::vector<return_data_t<float> *> *> float_data;
    std::vector<std::vector<return_data_t<double> *> *> double_data;
    std::vector<std::vector<return_data_t<char *> *> *> string_data;

    bool query_idx_is_set;

    std::string JSON_string;
 
    Globals() {
        attributes = NULL;
        query_idx_is_set = false;
        p_result_array = NULL;
    } 

    /**
     * cleans the book keeping structures except query config
     */
    void cleanup() {
#ifdef DEBUG
        std::cout << "Cleaning up ..." << std::endl;
#endif
        for( auto &v : variants) {
            v.clear();
        }
        variants.clear();

        delete_2d_vector<std::vector<std::vector<return_data_t<int> *>*>>(int_data);
        delete_2d_vector<std::vector<std::vector<return_data_t<int64_t> *>*>>(int64_t_data);
        delete_2d_vector<std::vector<std::vector<return_data_t<unsigned> *>*>>(unsigned_data);
        delete_2d_vector<std::vector<std::vector<return_data_t<uint64_t> *>*>>(uint64_t_data);
        delete_2d_vector<std::vector<std::vector<return_data_t<float> *>*>>(float_data);
        delete_2d_vector<std::vector<std::vector<return_data_t<double> *>*>>(double_data);
        delete_2d_vector<std::vector<std::vector<return_data_t<char *> *>*>>(string_data);

        if (p_result_array) {
            for (int i = 0; i < p_result_array->count; ++i)
            {
                cell_array_t *p_cell_array = p_result_array->results[i];
                for (int j = 0; j < p_cell_array->count; ++j)
                {
                    delete p_cell_array->cells[j];
                }
                delete Calls[i];
                delete p_result_array->results[i];
            }
            delete [] p_result_array->results;
            delete p_result_array;
        }
        p_result_array = NULL;
    }

    void clear() {
        query_config.clear();
        if( attributes ) {
            delete attributes;
        }

        query_idx_to_attribute_idx.clear();
        attributes = NULL;
        query_idx_is_set = false;
    }

    /**
     * templated helper that deletes the allocated memory 
     */
    template<class T>
    void delete_2d_vector(T &in_vector) {
        for( auto *data : in_vector ) {
          for( auto *element : *data ) {
                auto itr = allocated_map.find(std::string(element->attribute));
                if (itr != allocated_map.end())
                {
                    if (itr->second)
                    {
                        delete [] element->data;
                    }
                }
                delete element;
          }
          data->clear();
          delete data;
        }
        in_vector.clear();
    }

    ~Globals() {
        cleanup();
        clear();
    }
};

class LibBookKeeping
{
public:
    Globals *data;
    bool isValid; 

    LibBookKeeping() {
        isValid = false;
        data = new Globals();
    }
    ~LibBookKeeping() {
        delete data;
    }

    void clear() {
        isValid = false;
        delete data;
        data = new Globals();
    }
};

enum CPointersEnum
{
  POINTER_INT=0u,
  POINTER_INT64_T,
  POINTER_UNSIGNED,
  POINTER_UINT64_T,
  POINTER_FLOAT,
  POINTER_DOUBLE,
  POINTER_CHAR_PTR,
};

auto type_to_int = std::unordered_map<std::type_index, unsigned> {
    { std::type_index(typeid(int)), POINTER_INT },
    { std::type_index(typeid(int64_t)), POINTER_INT64_T },
    { std::type_index(typeid(unsigned)), POINTER_UNSIGNED },
    { std::type_index(typeid(uint64_t)), POINTER_UINT64_T },
    { std::type_index(typeid(float)), POINTER_FLOAT },
    { std::type_index(typeid(double)), POINTER_DOUBLE },
    { std::type_index(typeid(char)), POINTER_CHAR_PTR }
};

std::string get_type_string(std::type_index type) {
    switch(type_to_int[type]) {
        case POINTER_INT:
          return std::string("INT");
        case POINTER_UINT64_T:
          return std::string("UINT64_T");
        case POINTER_INT64_T:
          return std::string("INT64_T");
        case POINTER_UNSIGNED:
          return std::string("UNSIGNED");
        case POINTER_FLOAT:
          return std::string("FLOAT");
        case POINTER_DOUBLE:
          return std::string("DOUBLE");
        case POINTER_CHAR_PTR:
          return std::string("STRING");
    }
}
#endif
