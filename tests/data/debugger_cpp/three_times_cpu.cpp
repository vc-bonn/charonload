#include "three_times_cpu.h"

#include <ATen/Dispatch.h>
#include <ATen/ops/zeros_like.h>

at::Tensor
three_times(const at::Tensor& input)
{
    // For testing the debugger, set a breakpoint at the statement below.
    //
    // Note that since AT_DISPATCH_ALL_TYPES is the next statement and resolves to a larger code chunk, the debugger
    // must be continued several times to successfully jump to the end of the program.
    auto output = at::zeros_like(input);

    AT_DISPATCH_ALL_TYPES(input.scalar_type(),
                          "two_times_cpu",
                          [&]()
                          {
                              for (std::size_t i = 0; i < input.numel(); ++i)
                              {
                                  output.data_ptr<scalar_t>()[i] = scalar_t(3) * input.data_ptr<scalar_t>()[i];
                              }
                          });

    return output;
}
