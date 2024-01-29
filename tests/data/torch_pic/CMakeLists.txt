cmake_minimum_required(VERSION 3.27)

project(torch_pic LANGUAGES CXX)

find_package(charonload)

if(charonload_FOUND)
    add_library(torch_pic STATIC)

    target_sources(torch_pic PRIVATE two_times_cpu.cpp)
    target_compile_features(torch_pic PUBLIC cxx_std_17)
    target_link_libraries(torch_pic PUBLIC ${TORCH_LIBRARIES})

    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_pic)
endif()
