cmake_minimum_required(VERSION 3.27)

project(torch_cxx_standard LANGUAGES CXX)

set(CMAKE_CXX_STANDARD ${CHARONLOAD_TORCH_STANDARD})

find_package(Torch REQUIRED)

add_executable(torch_cxx_standard)
target_sources(torch_cxx_standard PRIVATE torch_cxx_standard.cpp)
target_link_libraries(torch_cxx_standard PRIVATE ${TORCH_LIBRARIES})
