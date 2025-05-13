cmake_minimum_required(VERSION 3.27)

project(torch_cuda_subdirectory LANGUAGES CXX CUDA)

add_subdirectory(lib_dir)

# Must come AFTER lib_dir
add_subdirectory(binding_dir)
