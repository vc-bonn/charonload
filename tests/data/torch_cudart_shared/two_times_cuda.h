#pragma once

#include <ATen/core/Tensor.h>

at::Tensor
two_times(const at::Tensor& input);

int
numel_times_multi_processor_count(const at::Tensor& input);

int
numel_times_multi_processor_count_aliased(const at::Tensor& input);
