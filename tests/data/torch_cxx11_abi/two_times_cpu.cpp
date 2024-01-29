#include "two_times_cpu.h"

#include <ATen/Dispatch.h>
#include <ATen/ops/zeros_like.h>

#include <aliased_external_string_lib.h>
#include <external_string_lib.h>

#ifndef EXTERNAL_INTERFACE
    #error Linking against external_interface library failed!
#endif

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

std::string
numel_to_string(const at::Tensor& input)
{
    return int_to_string(input.numel());
}

std::string
numel_to_string_aliased(const at::Tensor& input)
{
    return aliased_int_to_string(input.numel());
}
