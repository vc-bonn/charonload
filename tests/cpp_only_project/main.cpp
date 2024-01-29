#include <cstdlib>

#include <torch/types.h>

#include "two_times_cpu.h"

int
main()
{
    const auto dtype_float = torch::TensorOptions{}.dtype(torch::kFloat32).device(torch::kCPU);
    auto t_input = torch::randint(0, 10, { 3, 3, 3 }, dtype_float);

    auto t_output = two_times(t_input);

    return torch::equal(t_output, 2.0f * t_input) ? EXIT_SUCCESS : EXIT_FAILURE;
}
