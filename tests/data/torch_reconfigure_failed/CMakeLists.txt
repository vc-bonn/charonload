cmake_minimum_required(VERSION 3.27)

project(torch_reconfigure_failed LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp two_times_cpu.cpp)
endif()

if(EXISTS "${CMAKE_BINARY_DIR}/dirty.txt")
    message(FATAL_ERROR "Intentional configure failure")
endif()
