# --- Compiler --- #
CXX = $(MPIPATH)mpicxx
CPPFLAGS=-std=c++11 -fPIC -fopenmp
SOFLAGS=-shared -fPIC -Wl,-soname,
LDFLAGS=-lz -lrt -lcrypto

# --- Debug/Release/Verbose mode handler --- #
BUILD ?= debug
DEBUG ?= 1
COVFLAGS=

ifeq ($(BUILD),debug)
  CPPFLAGS+= -g -gdwarf-2 -g3 -DDEBUG=$(DEBUG)
  LINKFLAGS+=-g -gdwarf-2 -g3
  TILEDB_BUILD:=debug
endif

ifeq ($(BUILD),debug-coverage)
  CPPFLAGS+= -g -gdwarf-2 -g3 -DDEBUG=$(DEBUG) --coverage
  LINKFLAGS+=-g -gdwarf-2 -g3 --coverage
  COVFLAGS=-g -gdwarf-2 -g3 --coverage
  TILEDB_BUILD:=debug
endif

ifeq ($(BUILD),release)
  CPPFLAGS += -DNDEBUG -O3
  LINKFLAGS+=-O3
  TILEDB_BUILD:=release
endif

ifndef GENOMICSDB_DIR
	GENOMICSDB_DIR=./dependencies/GenomicsDB
endif

GENOMICSDB_STATIC_LIBRARY = $(GENOMICSDB_DIR)/bin/libgenomicsdb.a
GENOMICSDB_BIN_DIR = $(GENOMICSDB_DIR)/bin
LINKFLAGS += -L$(GENOMICSDB_BIN_DIR)
GENOMICSDB_INCLUDE_DIRS = $(wildcard $(GENOMICSDB_DIR)/include/*)

BUILD_NUM_THREADS ?= 8
ifndef TILEDB_DIR
	TILEDB_DIR=$(GENOMICSDB_DIR)/dependencies/TileDB
endif
INCLUDE_PATHS = -I$(TILEDB_DIR)/core/include/c_api

LDFLAGS:= -Wl,-Bstatic -L$(TILEDB_DIR)/core/lib/$(TILEDB_BUILD) -ltiledb -Wl,-Bdynamic $(LDFLAGS)

INCLUDE_PATHS+=$(GENOMICSDB_INCLUDE_DIRS:%=-I%)

ifndef HTSDIR
  HTSDIR=$(GENOMICSDB_DIR)/dependencies/htslib
endif

ifdef HTSDIR
    INCLUDE_PATHS+=-I$(HTSDIR)
    CPPFLAGS += -DHTSDIR
    LDFLAGS+=-Wl,-rpath,'$(HTSDIR)' -Wl,-Bdynamic -L$(HTSDIR) -lhts -Wl,-Bdynamic
endif

CSV_FLAGS= 
#libcsv - optional, but required if csvs need to be imported
ifdef LIBCSV_DIR
  CSV_FLAGS=LIBCSV_DIR=$(LIBCSV_DIR)
else
  CSV_FLAGS=USE_LIBCSV=1
endif

# --- Directories --- #
LIB_INCLUDE_DIR = include
LIB_SRC_DIR = src
LIB_LIB_DIR = lib
LIB_BIN_DIR = bin
LIB_OBJ_DIR = obj

# EXAMPLE_INCLUDE_DIR = example/include
EXAMPLE_SRC_DIR = example/src
EXAMPLE_BIN_DIR = example/bin
EXAMPLE_OBJ_DIR = example/obj

# --- Files --- #
LIB_INCLUDE := $(wildcard $(LIB_INCLUDE_DIR)/*.h)
LIB_SRC := $(wildcard $(LIB_SRC_DIR)/*.cc)
LIB_OBJ := $(patsubst $(LIB_SRC_DIR)/%.cc, $(LIB_OBJ_DIR)/%.o, $(LIB_SRC))

EXAMPLE_SRC := $(wildcard $(EXAMPLE_SRC_DIR)/*.cc)
EXAMPLE_OBJ := $(patsubst $(EXAMPLE_SRC_DIR)/%.cc, $(EXAMPLE_OBJ_DIR)/%.o, $(EXAMPLE_SRC))
EXAMPLE_BIN := $(patsubst $(EXAMPLE_SRC_DIR)/%.cc, $(EXAMPLE_BIN_DIR)/%, $(EXAMPLE_SRC))

.PHONY: example libquery all clean clean_example clean_lib

all: $(GENOMICSDB_STATIC_LIBRARY) libquery example

example: $(EXAMPLE_BIN_DIR)/example_libquery

libquery: $(LIB_LIB_DIR)/libquery.so

clean: clean_lib clean_example clean_so clean_genomicsdb

clean_so:
	rm -rf $(LIB_LIB_DIR)/*

$(GENOMICSDB_STATIC_LIBRARY):
	make -C $(GENOMICSDB_DIR) BUILD=$(BUILD) $(CSV_FLAGS) OPENMP=1 -j $(BUILD_NUM_THREADS)

clean_genomicsdb:
	make -C $(GENOMICSDB_DIR) clean

# --- Compilation and dependency genration --- #

# Compile Global Structures

-include $(LIB_OBJ:.o=.d)

$(LIB_OBJ_DIR)/%.o: $(LIB_SRC_DIR)/%.cc
	@test -d $(LIB_OBJ_DIR) || mkdir -p $(LIB_OBJ_DIR)
	@echo "Compiling $<"
	@$(CXX) $(CPPFLAGS) $(INCLUDE_PATHS) -I $(LIB_INCLUDE_DIR) -c $< -o $@
	@$(CXX) -MM $(CPPFLAGS) $(INCLUDE_PATHS) -I $(LIB_INCLUDE_DIR) $< > $(@:.o=.d)
	@mv -f $(@:.o=.d) $(@:.o=.d.tmp)
	@sed 's|.*:|$@:|' < $(@:.o=.d.tmp) > $(@:.o=.d)
	@rm -f $(@:.o=.d.tmp)

clean_lib:
	rm -f $(LIB_BIN_DIR)/* $(LIB_OBJ_DIR)/*

# Compile Example

-include $(EXAMPLE_OBJ:.o=.d)

$(EXAMPLE_OBJ_DIR)/%.o: $(EXAMPLE_SRC_DIR)/%.cc
	@test -d $(EXAMPLE_OBJ_DIR) || mkdir -p $(EXAMPLE_OBJ_DIR)
	@echo "Compiling $<"
	@$(CXX) $(CPPFLAGS) -I$(LIB_INCLUDE_DIR) -c $< -o $@
	@$(CXX) -MM $(CPPFLAGS) -I$(LIB_INCLUDE_DIR) $< > $(@:.o=.d)
	@mv -f $(@:.o=.d) $(@:.o=.d.tmp)
	@sed 's|.*:|$@:|' < $(@:.o=.d.tmp) > $(@:.o=.d)
	@rm -f $(@:.o=.d.tmp)

clean_example:
	rm -f $(EXAMPLE_BIN_DIR)/* $(EXAMPLE_OBJ_DIR)/*

clean_tiledb:
	rm -f $(LIB_BIN_DIR)/* $(LIB_OBJ_DIR)/*

# --- Linking --- #

###################
# Example Linking #
###################

$(EXAMPLE_BIN_DIR)/example_libquery: $(LIB_LIB_DIR)/libquery.so $(EXAMPLE_OBJ_DIR)/example_libquery.o
	@test -d $(EXAMPLE_BIN_DIR) || mkdir -p $(EXAMPLE_BIN_DIR)
	@echo "Linking example $@"
	@$(CXX) $(COVFLAGS) -Wl,-rpath,'$(LIB_LIB_DIR)' -o $@ $^ -Wl,-Bdynamic -L$(LIB_LIB_DIR) -lquery -Wl,-Bdynamic

##################
# TileDB Linking #
##################

$(LIB_LIB_DIR)/libquery.so: $(GENOMICSDB_STATIC_LIBRARY) $(LIB_OBJ_DIR)/libquery.o $(LIB_OBJ_DIR)/query.o 
	@test -d $(LIB_LIB_DIR) || mkdir -p $(LIB_LIB_DIR)
	@echo "Linking dynamic library $@"
	@$(CXX) $(CPPFLAGS) -Wl,-rpath,'$(GENOMICSDB_BIN_DIR)' $(SOFLAGS)libquery.so -o $@ $^ -Wl,-Bstatic $(LINKFLAGS) -lgenomicsdb -Wl,-Bdynamic $(LDFLAGS)

