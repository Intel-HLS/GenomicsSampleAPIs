/**
 * The MIT License (MIT)
 * Copyright (c) 2016 Intel Corporation
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of 
 * this software and associated documentation files (the "Software"), to deal in 
 * the Software without restriction, including without limitation the rights to 
 * use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of 
 * the Software, and to permit persons to whom the Software is furnished to do so, 
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all 
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
 * FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
 * COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
 * IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/

#include <iostream>
#include <iomanip>
#include <string.h>
#include <getopt.h>

#include "query.h"
void usage(char *program) {
    char workspace[] = "/mnt/app_hdd/scratch/jagan/TileDB/DB/";
    char array_name[] = "ICGC";
    std::cout << "Usage: " << std::endl;
    std::cout << program << std::endl;
    std::cout << "\t-w <workspace> " << std::endl;
    std::cout << "\t-A <array name> " << std::endl;
    std::cout << "\t-s <start> " << std::endl;
    std::cout << "\t-e <end> " << std::endl;
    std::cout << "\t-p <page_size> " << std::endl;
    std::cout << "\t-a <csv of attributes> " << std::endl;
    std::cout << "\t[-f <csv of row ids>] " << std::endl;
    std::cout << "\t[-x <# of ways to split the query>] " << std::endl;
    std::cout << "Example: " << std::endl << "\t" << program << " -w "
            << workspace << " -A " << array_name
            << " -s 16943809 -e 16944810 -a REF,ALT,QUAL" << std::endl;
}

int main(int argc, char *argv[]) {
    char *workspace;
    char *array_name;
    uint64_t start;
    uint64_t end;
    char *attributes;
    char *token;
    int split_ways = 1;
    char *filter = NULL;
    int64_t page_size = -1;
    std::string str_token;
    char *page_token = NULL;

    int req_cout = 0;
    int c = 0;
    while ((c = getopt(argc, argv, "A:s:e:w:f:a:x:p:h")) >= 0) {
        switch (c) {
        case 'w':
            workspace = optarg;
            ++req_cout;
            break;
        case 'A':
            array_name = optarg;
            ++req_cout;
            break;
        case 's':
            start = std::stoull(optarg);
            ++req_cout;
            break;
        case 'e':
            end = std::stoull(optarg);
            ++req_cout;
            break;
        case 'x':
            split_ways = std::stoi(optarg);
            break;
        case 'f':
            filter = optarg;
            break;
        case 'a':
            attributes = optarg;
            ++req_cout;
            break;
        case 'p':
            page_size = std::stoull(optarg);
            break;
        case 'h':
        default:
            usage(argv[0]);
            return 0;
        }
    }

    if (req_cout < 5) {
        usage(argv[0]);
        return 0;
    }

    uint64_t split_width = (end - start) / split_ways;
    for (int i = 0; i < split_ways; ++i) {
        unsigned count = 0;
        do {
            uint64_t tile_token = getToken();

            setup_attributes(attributes, tile_token);

            if (filter != NULL) {
                filter_rows(filter, tile_token);
            }

            uint64_t new_start = start + split_width * i;
            uint64_t new_end = new_start + split_width - 1;
            if (i == split_ways - 1) {
                new_end = end;
            }
            std::cout << "Querying: " << new_start << " " << new_end
                    << std::endl;
            result_array_t *r_arr = query_column(workspace, array_name,
                    new_start, new_end, tile_token, page_size, page_token);
            print_result_array(r_arr);
            if (r_arr->token) {
                str_token = std::string(r_arr->token);
                page_token = const_cast<char *>(str_token.c_str());
                std::cout << "Received Page Token : " << str_token;
                std::cout << " @ iteration " << ++count << std::endl;
            } else {
                page_token = NULL;
            }
            cleanup(tile_token);
        } while (page_token != NULL);
    }
}
