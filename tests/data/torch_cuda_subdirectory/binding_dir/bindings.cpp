#include <torch/python.h>

#include "three_times_cuda.h"
#include "two_times_cuda.h"

using namespace pybind11::literals;

#define STRINGIFY_IMPL(x) #x
#define STRINGIFY(a) STRINGIFY_IMPL(a)

PYBIND11_MODULE(TORCH_EXTENSION_NAME, m)
{
    m.doc() = "A C++/CUDA extension module named \"" STRINGIFY(TORCH_EXTENSION_NAME) "\" that is built just-in-time.";

    m.def("two_times", &two_times, "input"_a, R"(
        Multiply the given input tensor by a factor of 2 on the GPU using CUDA.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        A new tensor with the same shape and dtype as ``input`` and where each value is multiplied by 2.
    )");

    m.def("three_times", &three_times, "input"_a, R"(
        Multiply the given input tensor by a factor of 3 on the GPU using CUDA.

        Parameters
        ----------
        input
            A tensor with arbitrary shape and dtype.

        Returns
        -------
        A new tensor with the same shape and dtype as ``input`` and where each value is multiplied by 3.
    )");
}
