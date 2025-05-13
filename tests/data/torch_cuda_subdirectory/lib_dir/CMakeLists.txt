# Use GLOBAL import to force short-cicuiting
find_package(charonload GLOBAL)

if(charonload_FOUND)
    charonload_add_torch_library(torch_cuda_subdirectory STATIC)

    target_include_directories(torch_cuda_subdirectory PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
    target_sources(torch_cuda_subdirectory PRIVATE two_times_cuda.cu)
endif()
