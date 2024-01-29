find_package(charonload)

if(charonload_FOUND)
    charonload_add_torch_library(${TORCH_EXTENSION_NAME} MODULE)

    target_sources(${TORCH_EXTENSION_NAME} PRIVATE bindings.cpp)
    target_link_libraries(${TORCH_EXTENSION_NAME} PRIVATE torch_subdirectory)
endif()
