#include "external_cudart_lib.h"

#include <cuda_runtime_api.h>

int
get_multi_processor_count()
{
    int device = 0;

    int multi_processor_count = 0;
    cudaDeviceGetAttribute(&multi_processor_count, cudaDevAttrMultiProcessorCount, device);

    return multi_processor_count;
}
