find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(torch_subdirectory STATIC)

    target_include_directories(torch_subdirectory PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}")
    target_sources(torch_subdirectory PRIVATE two_times_cpu.cpp)
endif()
