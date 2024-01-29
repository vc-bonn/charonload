cmake_minimum_required(VERSION 3.27)

project(charonload_version LANGUAGES CXX)

find_package(charonload REQUIRED)

# Dummy bindings
charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)
target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)

file(WRITE "${CMAKE_BINARY_DIR}/charonload_version.txt" "${charonload_VERSION}")
