#include <array>

#include <fmt/core.h>

#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/string.h>

#include <rubberband/RubberBandStretcher.h>

#include "general.hpp"

namespace rb = RubberBand;
namespace nb = nanobind;
using namespace nb::literals;

namespace {

constexpr size_t MAX_CHANNELS_NUM = 32;  // TODO: Use small vector instead
constexpr size_t RB_MIN_SAMPLE_RATE = 8000;
constexpr size_t RB_MAX_SAMPLE_RATE = 192000;

constexpr int RB_IS_DONE__AVAILABLE_VALUE = -1;
constexpr float RB_AUTO_FORMANT_SCALE = 0.f;

using AudioShape_t = nb::shape<nb::any, nb::any>;
constexpr size_t RB_CHANNELS_AXIS = 0;
constexpr size_t RB_SAMPLES_AXIS = 1;

using DType_t = float;
constexpr char const* DTYPE_NAME = get_numpy_format_name<DType_t>().data();

using NbAudioArrayArg_t = nb::ndarray<DType_t const, AudioShape_t, nb::c_contig, nb::device::cpu>;
using NbAudioArrayRet_t = nb::ndarray<nb::numpy, DType_t, AudioShape_t, nb::c_contig, nb::device::cpu>;

using Option = rb::RubberBandStretcher::Option;
using OptionsPreset = rb::RubberBandStretcher::PresetOption;

/* helpers ****************************************************************************************/

template <typename DType>
std::array<DType*, MAX_CHANNELS_NUM> get_audio_ptr_per_channel(DType* const audio_data, size_t channels_num, size_t const samples_num)
{
  static_assert(std::is_same_v<std::remove_const_t<DType>, DType_t>);

  std::array<DType*, MAX_CHANNELS_NUM> audio_rows_per_channel;
  channels_num = std::min(MAX_CHANNELS_NUM, channels_num);
  for (size_t channel_idx = 0; channel_idx < channels_num; ++channel_idx)
  {
    audio_rows_per_channel[channel_idx] = audio_data + channel_idx * samples_num;
  }
  return audio_rows_per_channel;
}

constexpr std::array<size_t, AudioShape_t::size> create_audio_shape(size_t const channels_num, size_t const samples_num)
{
  if constexpr (RB_CHANNELS_AXIS == 0)
    return {channels_num, samples_num};
  else
    return {samples_num, channels_num};
}

std::unique_ptr<DType_t[]> create_uninitialized_audio_data(size_t const channels_num, size_t const samples_num)
{
  return std::unique_ptr<DType_t[]>(new DType_t[channels_num * samples_num]);
}

NbAudioArrayRet_t ndarray_from_audio_data(std::unique_ptr<DType_t[]> data, size_t const channels_num, size_t const samples_num)
{
  nb::capsule deleter(data.get(), [](void* p) noexcept { delete[] static_cast<DType_t*>(p); });
  auto const& audio_shape = create_audio_shape(channels_num, samples_num);
  return NbAudioArrayRet_t(data.release(), AudioShape_t::size, audio_shape.data(), deleter);
}

std::pair<std::unique_ptr<DType_t[]>, size_t> retrieve_audio_data(rb::RubberBandStretcher& stretcher, size_t samples_num)
{
  size_t const channels_num = stretcher.getChannelCount();
  samples_num = std::min(samples_num, (size_t)(std::max(0, stretcher.available())));  // available == -1 when done

  auto audio_data = create_uninitialized_audio_data(channels_num, samples_num);
  auto const& audio_per_channel = get_audio_ptr_per_channel(audio_data.get(), channels_num, samples_num);

  stretcher.retrieve(audio_per_channel.data(), samples_num);
  return {std::move(audio_data), samples_num};
};

std::pair<std::unique_ptr<DType_t[]>, size_t> retrieve_available_audio_data(rb::RubberBandStretcher& stretcher)
{
  return retrieve_audio_data(stretcher, size_t(-1));
};

NbAudioArrayRet_t create_audio_array(size_t const channels_num, size_t const samples_num, DType_t const init_value)
{
  auto audio_data = create_uninitialized_audio_data(channels_num, samples_num);
  std::fill_n(audio_data.get(), channels_num * samples_num, init_value);
  return ndarray_from_audio_data(std::move(audio_data), channels_num, samples_num);
}

/* function wrappers ******************************************************************************/

void set_stretcher_time_ratio(rb::RubberBandStretcher& stretcher, double const time_ratio)
{
  if (time_ratio <= 0)
  {
    throw nb::value_error(fmt::format("`time_ratio={}` is not supported. Time ratio must be greater than zero.", time_ratio).c_str());
  }
  stretcher.setTimeRatio(time_ratio);
}

void set_stretcher_pitch_scale(rb::RubberBandStretcher& stretcher, double const pitch_scale)
{
  if (pitch_scale <= 0)
  {
    throw nb::value_error(fmt::format("`pitch_scale={}` is not supported. Time ratio must be greater than zero.", pitch_scale).c_str());
  }
  stretcher.setPitchScale(pitch_scale);
}

/* Bindings ***************************************************************************************/

void define_constants(nb::module_& m)
{
  m.attr("MIN_SAMPLE_RATE") = RB_MIN_SAMPLE_RATE;
  m.attr("MAX_SAMPLE_RATE") = RB_MAX_SAMPLE_RATE;
  m.attr("MAX_CHANNELS_NUM") = MAX_CHANNELS_NUM;
  m.attr("CHANNELS_AXIS") = RB_CHANNELS_AXIS;
  m.attr("SAMPLES_AXIS") = RB_SAMPLES_AXIS;
  m.attr("DTYPE_NAME") = DTYPE_NAME;
  m.attr("AUTO_FORMANT_SCALE") = RB_AUTO_FORMANT_SCALE;
}

void define_module_functions(nb::module_& m)
{
  m.def("set_default_logging_level", &rb::RubberBandStretcher::setDefaultDebugLevel, "level"_a);
  m.def("create_audio_array", &create_audio_array, "channels_num"_a, "samples_num"_a, "init_value"_a = 0);
}

void define_option_enum(nb::module_& m)
{
  nb::enum_<Option>(m, "Option", nb::is_arithmetic())
      .value("PROCESS_OFFLINE", Option::OptionProcessOffline)
      .value("PROCESS_REALTIME", Option::OptionProcessRealTime)
      .value("TRANSIENTS_CRISP", Option::OptionTransientsCrisp)
      .value("TRANSIENTS_MIXED", Option::OptionTransientsMixed)
      .value("TRANSIENTS_SMOOTH", Option::OptionTransientsSmooth)
      .value("DETECTOR_COMPOUND", Option::OptionDetectorCompound)
      .value("DETECTOR_PERCUSSIVE", Option::OptionDetectorPercussive)
      .value("DETECTOR_SOFT", Option::OptionDetectorSoft)
      .value("PHASE_LAMINAR", Option::OptionPhaseLaminar)
      .value("PHASE_INDEPENDENT", Option::OptionPhaseIndependent)
      .value("THREADING_AUTO", Option::OptionThreadingAuto)
      .value("THREADING_NEVER", Option::OptionThreadingNever)
      .value("THREADING_ALWAYS", Option::OptionThreadingAlways)
      .value("WINDOW_STANDARD", Option::OptionWindowStandard)
      .value("WINDOW_SHORT", Option::OptionWindowShort)
      .value("WINDOW_LONG", Option::OptionWindowLong)
      .value("SMOOTHING_OFF", Option::OptionSmoothingOff)
      .value("SMOOTHING_ON", Option::OptionSmoothingOn)
      .value("FORMANT_SHIFTED", Option::OptionFormantShifted)
      .value("FORMANT_PRESERVED", Option::OptionFormantPreserved)
      .value("PitchHighSpeed", Option::OptionPitchHighSpeed)
      .value("PitchHighQuality", Option::OptionPitchHighQuality)
      .value("PitchHighConsistency", Option::OptionPitchHighConsistency)
      .value("CHANNELS_APART", Option::OptionChannelsApart)
      .value("CHANNELS_TOGETHER", Option::OptionChannelsTogether)
      .value("ENGINE_FASTER", Option::OptionEngineFaster)
      .value("ENGINE_FINER", Option::OptionEngineFiner)
      // presets
      .value("PRESET_DEFAULT", Option(OptionsPreset::DefaultOptions))
      .value("PRESET_PERCUSSIVE", Option(OptionsPreset::PercussiveOptions));
}

// TODO: add init version with a logger
void define_stretcher__init__(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "__init__",
      [](rb::RubberBandStretcher* const ptr,
         size_t const sample_rate,
         size_t const channels,
         size_t const options,
         double const initial_time_ratio,
         double const initial_pitch_scale)
      {
        if (sample_rate < RB_MIN_SAMPLE_RATE || sample_rate > RB_MAX_SAMPLE_RATE)
        {
          throw nb::value_error(fmt::format("`sample_rate={}` is out of range. RubberBand supports sample rates in the range: ({}, {}).",
                                            sample_rate,
                                            RB_MIN_SAMPLE_RATE,
                                            RB_MAX_SAMPLE_RATE)
                                    .c_str());
        }
        if (channels == 0 || channels > MAX_CHANNELS_NUM)
        {
          throw nb::value_error(
              fmt::format("`channels={}` is not supported. Audio may have at least 1 and at most {} channels.", channels, MAX_CHANNELS_NUM).c_str());
        }

        new (ptr) rb::RubberBandStretcher(sample_rate, channels, options, initial_time_ratio, initial_pitch_scale);
        set_stretcher_time_ratio(*ptr, initial_time_ratio);
        set_stretcher_pitch_scale(*ptr, initial_pitch_scale);
      },
      "sample_rate"_a,
      "channels"_a,
      "options"_a = Option(OptionsPreset::DefaultOptions),
      "initial_time_ratio"_a = 1.0,
      "initial_pitch_scale"_a = 1.0);
}

void define_stretcher_read_only_properties(nb::class_<rb::RubberBandStretcher>& cls)
{
  // these are not getters, as their values do not depend on the current state of the stretcher
  cls.def_prop_ro("channels", &rb::RubberBandStretcher::getChannelCount);
  cls.def_prop_ro("engine_version", &rb::RubberBandStretcher::getEngineVersion);
}

void define_stretcher_read_write_properties(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def_prop_rw("time_ratio", &rb::RubberBandStretcher::getTimeRatio, &set_stretcher_time_ratio);
  cls.def_prop_rw("pitch_scale", &rb::RubberBandStretcher::getPitchScale, &set_stretcher_pitch_scale);
  cls.def_prop_rw("formant_scale",
                  &rb::RubberBandStretcher::getFormantScale,
                  [](rb::RubberBandStretcher& stretcher, double const formant_scale)
                  {
                    if (formant_scale <= 0 && formant_scale != RB_AUTO_FORMANT_SCALE)
                    {
                      throw nb::value_error(
                          fmt::format("`formant_scale={}` is not supported. Time ratio must be greater than zero.", formant_scale).c_str());
                    }
                    stretcher.setFormantScale(formant_scale);
                  });
}

void define_stretcher_setters_with_getters(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def("set_frequency_cutoff", &rb::RubberBandStretcher::setFrequencyCutoff, "n"_a, "f"_a);
  cls.def("get_frequency_cutoff", &rb::RubberBandStretcher::getFrequencyCutoff, "n"_a);
}

void define_stretcher_setters_only(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def("set_transients_options", &rb::RubberBandStretcher::setTransientsOption, "options"_a);
  cls.def("set_detector_options", &rb::RubberBandStretcher::setDetectorOption, "options"_a);
  cls.def("set_phase_options", &rb::RubberBandStretcher::setPhaseOption, "options"_a);
  cls.def("set_formant_options", &rb::RubberBandStretcher::setFormantOption, "options"_a);
  cls.def("set_pitch_options", &rb::RubberBandStretcher::setPitchOption, "options"_a);
  cls.def("set_expected_input_duration", &rb::RubberBandStretcher::setExpectedInputDuration, "samples"_a);
  cls.def(
      "set_max_process_size",
      [](rb::RubberBandStretcher& stretcher, size_t const samples)
      {
        if (samples > stretcher.getProcessSizeLimit())
        {
          throw nb::value_error(
              fmt::format("The specified number of samples ({}) exceeds the limit ({}), see `get_process_size_limit()` for more details",
                          samples,
                          stretcher.getProcessSizeLimit())
                  .c_str());
        }
        stretcher.setMaxProcessSize(samples);
      },
      "samples"_a);
  cls.def("set_keyframe_map", &rb::RubberBandStretcher::setKeyFrameMap, "mapping"_a);
  cls.def("set_logging_level", &rb::RubberBandStretcher::setDebugLevel, "level"_a);
}

void define_stretcher_getters_only(nb::class_<rb::RubberBandStretcher>& cls)
{
  // these are not properties, as their values do depend on the current state of the stretcher
  cls.def("is_done", [](rb::RubberBandStretcher const& stretcher) { return stretcher.available() == RB_IS_DONE__AVAILABLE_VALUE; });
  cls.def("available",
          [](rb::RubberBandStretcher const& stretcher)
          {
            auto const available = stretcher.available();
            return available == RB_IS_DONE__AVAILABLE_VALUE ? 0 : available;
          });
  cls.def("get_preferred_start_pad", &rb::RubberBandStretcher::getPreferredStartPad);
  cls.def("get_start_delay", &rb::RubberBandStretcher::getStartDelay);
  cls.def("get_samples_required", &rb::RubberBandStretcher::getSamplesRequired);
  cls.def("get_input_increment", &rb::RubberBandStretcher::getInputIncrement);
  cls.def("get_output_increment", &rb::RubberBandStretcher::getOutputIncrements);
  cls.def("get_phase_reset_curve", &rb::RubberBandStretcher::getPhaseResetCurve);
  cls.def("get_exact_time_points", &rb::RubberBandStretcher::getExactTimePoints);
  cls.def("get_process_size_limit", &rb::RubberBandStretcher::getProcessSizeLimit);
}

void define_stretcher_method_study(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "study",
      [](rb::RubberBandStretcher& stretcher, NbAudioArrayArg_t const audio, bool const final = false)
      {
        size_t const channels_num = stretcher.getChannelCount();
        size_t const samples_num = audio.shape(RB_SAMPLES_AXIS);
        if (audio.shape(RB_CHANNELS_AXIS) != channels_num)
        {
          throw nb::value_error("Wrong number of audio channels");
        }

        auto const& audio_per_channel = get_audio_ptr_per_channel(audio.data(), channels_num, samples_num);
        stretcher.study(audio_per_channel.data(), samples_num, final);
      },
      "audio"_a,
      "final"_a = false,
      nb::call_guard<nb::gil_scoped_release>());
}

void define_stretcher_method_process(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "process",
      [](rb::RubberBandStretcher& stretcher, NbAudioArrayArg_t const audio, bool const final = false)
      {
        size_t const channels_num = stretcher.getChannelCount();
        size_t const samples_num = audio.shape(RB_SAMPLES_AXIS);
        if (audio.shape(RB_CHANNELS_AXIS) != channels_num)
        {
          throw nb::value_error("Wrong number of audio channels");
        }

        auto const& audio_per_channel = get_audio_ptr_per_channel(audio.data(), channels_num, samples_num);
        stretcher.process(audio_per_channel.data(), samples_num, final);
      },
      "audio"_a,
      "final"_a = false,
      nb::call_guard<nb::gil_scoped_release>());
}

void define_stretcher_method_retrieve(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "retrieve",
      [](rb::RubberBandStretcher& stretcher, size_t const wanted_samples_num)
      {
        auto [audio_data, samples_num] = retrieve_audio_data(stretcher, wanted_samples_num);

        nb::gil_scoped_acquire gil_acquired;
        return ndarray_from_audio_data(std::move(audio_data), stretcher.getChannelCount(), samples_num);
      },
      "samples_num"_a,
      nb::call_guard<nb::gil_scoped_release>());
  cls.def(
      "retrieve_available",
      [](rb::RubberBandStretcher& stretcher)
      {
        auto [audio_data, samples_num] = retrieve_available_audio_data(stretcher);

        nb::gil_scoped_acquire gil_acquired;
        return ndarray_from_audio_data(std::move(audio_data), stretcher.getChannelCount(), samples_num);
      },
      nb::call_guard<nb::gil_scoped_release>());
}

void define_stretcher_simple_methods(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def("reset", &rb::RubberBandStretcher::reset);
  cls.def("calculate_stretch", &rb::RubberBandStretcher::calculateStretch);
}

void define_stretcher_class(nb::module_& m)
{
  auto stretcher_class = nb::class_<rb::RubberBandStretcher>(m, "RubberBandStretcher");
  define_stretcher__init__(stretcher_class);
  define_stretcher_read_write_properties(stretcher_class);
  define_stretcher_read_only_properties(stretcher_class);
  define_stretcher_setters_with_getters(stretcher_class);
  define_stretcher_setters_only(stretcher_class);
  define_stretcher_getters_only(stretcher_class);
  define_stretcher_method_study(stretcher_class);
  define_stretcher_method_process(stretcher_class);
  define_stretcher_method_retrieve(stretcher_class);
  define_stretcher_simple_methods(stretcher_class);
}

}  // namespace

NB_MODULE(pylibrb_ext, m)
{
  define_constants(m);
  define_module_functions(m);
  define_option_enum(m);
  define_stretcher_class(m);
}
