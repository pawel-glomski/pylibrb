#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>

#include <rubberband/RubberBandStretcher.h>

#include "general.hpp"

namespace rb = RubberBand;
namespace nb = nanobind;
using namespace nb::literals;

using AudioShape_t = nb::shape<nb::any, nb::any>;
constexpr size_t RB_CHANNEL_IDX = 0;
constexpr size_t RB_SAMPLE_IDX = 1;
constexpr size_t MAX_CHANNELS_NUM = 8;

using DType_t = float;
constexpr char const* DTYPE_NAME = get_numpy_format_name<DType_t>().data();

using NbAudioArrayArg_t = nb::ndarray<DType_t, AudioShape_t, nb::c_contig, nb::device::cpu>;
using NbAudioArrayRet_t = nb::ndarray<nb::numpy, DType_t, AudioShape_t, nb::c_contig, nb::device::cpu>;

constexpr std::array<size_t, AudioShape_t::size> create_audio_shape(size_t const channels_num, size_t const samples_num)
{
  if constexpr (RB_CHANNEL_IDX == 0)
    return {channels_num, samples_num};
  else
    return {samples_num, channels_num};
}

NbAudioArrayRet_t create_audio_array(size_t const channels_num, size_t const samples_num)
{
  auto data = new DType_t[channels_num * samples_num];
  nb::capsule deleter(data, [](void* p) noexcept { delete[] static_cast<DType_t*>(p); });

  return NbAudioArrayRet_t(data, AudioShape_t::size, create_audio_shape(channels_num, samples_num).data(), deleter);
}

std::array<DType_t*, MAX_CHANNELS_NUM> get_audio_ptr_per_channel(DType_t* audio_data,
                                                                 size_t const channels_num,
                                                                 size_t const samples_num)
{
  std::array<DType_t*, MAX_CHANNELS_NUM> audio_rows_per_channel;
  for (size_t channel_idx = 0; channel_idx < channels_num; ++channel_idx)
  {
    audio_rows_per_channel[channel_idx] = audio_data + channel_idx * samples_num;
  }
  return audio_rows_per_channel;
}
