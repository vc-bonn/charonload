cmake_minimum_required(VERSION 3.27)

project(cpp_only_project)


# Include charonload
if(NOT CHARONLOAD_JIT_COMPILE)
    add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/../.." "${CMAKE_CURRENT_BINARY_DIR}/charonload")
endif()


charonload_add_torch_library(cpp_only_lib STATIC)
target_sources(cpp_only_lib PRIVATE two_times_cpu.cpp)

add_executable(main)
target_sources(main PRIVATE main.cpp)
target_link_libraries(main PRIVATE cpp_only_lib)
