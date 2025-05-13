# This short-circuits from GLOBAL find_package
find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp three_times_cuda.cu)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_cuda_subdirectory)
endif()
