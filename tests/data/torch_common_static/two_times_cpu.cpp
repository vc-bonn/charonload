#include "two_times_cpu.h"

#include <ATen/Dispatch.h>
#include <ATen/ops/zeros_like.h>

at::Tensor
two_times(const at::Tensor& input)
{
    auto output = at::zeros_like(input);

    AT_DISPATCH_ALL_TYPES(input.scalar_type(),
                          "two_times_cpu",
                          [&]()
                          {
                              for (std::size_t i = 0; i < input.numel(); ++i)
                              {
                                  output.data_ptr<scalar_t>()[i] = scalar_t(2) * input.data_ptr<scalar_t>()[i];
                              }
                          });

    return output;
}
