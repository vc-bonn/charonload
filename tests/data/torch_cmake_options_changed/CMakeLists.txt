cmake_minimum_required(VERSION 3.27)

project(torch_cpu LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    if(NOT DEFINED TEST_OPTION)
        message(FATAL_ERROR "TEST_OPTION should be defined but is not.")
    endif()

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp two_times_cpu.cpp)
    target_compile_definitions(${TORCH_EXTENSION_NAME} PRIVATE "TEST_OPTION=${TEST_OPTION}")
endif()
