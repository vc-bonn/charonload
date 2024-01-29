cmake_minimum_required(VERSION 3.27)

project(torch_cmake_options LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    if(NOT TEST_OPTION STREQUAL "some_value")
        message(FATAL_ERROR "TEST_OPTION not correctly set.")
    endif()

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp two_times_cpu.cpp)
endif()
