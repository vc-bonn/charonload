#include <ATen/Dispatch.h>
#include <ATen/cuda/Exceptions.h>
#include <ATen/ops/zeros_like.h>

#ifndef __CUDACC_EXTENDED_LAMBDA__
    #error "Modified CUDA_NVCC_FLAGS (extended lambda) from torch not correctly propagated"
#endif

template <class T>
__global__ void
three_times_kernel(const T* const input, T* const output, const std::size_t N)
{
    for (int i = blockDim.x * blockIdx.x + threadIdx.x; i < N; i += blockDim.x * gridDim.x)
    {
        output[i] = T(3) * input[i];
    }
}

at::Tensor
three_times(const at::Tensor& input)
{
    auto output = at::zeros_like(input);

    AT_DISPATCH_ALL_TYPES(input.scalar_type(),
                          "three_times_kernel",
                          [&]()
                          {
                              const std::uint32_t block_size = 128;
                              const std::uint32_t num_blocks = (input.numel() + block_size - 1) / block_size;
                              three_times_kernel<<<num_blocks, block_size>>>(input.data_ptr<scalar_t>(),
                                                                             output.data_ptr<scalar_t>(),
                                                                             input.numel());
                              AT_CUDA_CHECK(cudaGetLastError());
                              AT_CUDA_CHECK(cudaDeviceSynchronize());
                          });

    return output;
}
