#include <fmt/core.h>

#include "bindings.hpp"

namespace {

using Option = rb::RubberBandStretcher::Option;
using OptionsPreset = rb::RubberBandStretcher::PresetOption;

/* function wrappers ******************************************************************************/

void set_stretcher_time_ratio(rb::RubberBandStretcher& stretcher, double const time_ratio)
{
  if (time_ratio <= 0)
  {
    throw nb::value_error(fmt::format("`time_ratio={}` is not supported. Time ratio must be greater than zero.", time_ratio));
  }
  stretcher.setTimeRatio(time_ratio);
}

void set_stretcher_pitch_scale(rb::RubberBandStretcher& stretcher, double const pitch_scale)
{
  if (pitch_scale <= 0)
  {
    throw nb::value_error(fmt::format("`pitch_scale={}` is not supported. Time ratio must be greater than zero.", pitch_scale));
  }
  stretcher.setPitchScale(pitch_scale);
}

/* Bindings ***************************************************************************************/

void define_constants(nb::module_& m)
{
  m.attr("MIN_SAMPLE_RATE") = RB_MIN_SAMPLE_RATE;
  m.attr("MAX_SAMPLE_RATE") = RB_MAX_SAMPLE_RATE;
  m.attr("MAX_CHANNELS_NUM") = MAX_CHANNELS_NUM;
  m.attr("CHANNEL_IDX") = RB_CHANNEL_IDX;
  m.attr("SAMPLE_IDX") = RB_SAMPLE_IDX;
  m.attr("DTYPE_NAME") = DTYPE_NAME;
}

void define_module_functions(nb::module_& m)
{
  m.def("set_default_logging_level", &rb::RubberBandStretcher::setDefaultDebugLevel, "level"_a);
  m.def("create_audio_array", &create_audio_array, "channels_num"_a, "samples_num"_a);
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
         std::underlying_type_t<Option> const options,
         double const initial_time_ratio,
         double const initial_pitch_scale)
      {
        if (sample_rate < RB_MIN_SAMPLE_RATE || sample_rate > RB_MAX_SAMPLE_RATE)
        {
          throw nb::value_error(fmt::format("`sample_rate={}` is out of range. RubberBand supports sample rates in the range: ({}, {}).",
                                            sample_rate,
                                            RB_MIN_SAMPLE_RATE,
                                            RB_MAX_SAMPLE_RATE));
        }
        if (channels == 0 || channels > MAX_CHANNELS_NUM)
        {
          throw nb::value_error(fmt::format("`channels={}` is not supported. Audio may have at least 1 and at most {} channels.",
                                            channels,
                                            MAX_CHANNELS_NUM));
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
                    if (formant_scale <= 0)
                    {
                      throw nb::value_error(fmt::format("`formant_scale={}` is not supported. Time ratio must be greater than zero.", formant_scale));
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
  cls.def("set_max_process_size", &rb::RubberBandStretcher::setMaxProcessSize, "samples"_a);
  cls.def("set_keyframe_map", &rb::RubberBandStretcher::setKeyFrameMap, "mapping"_a);
  cls.def("set_logging_level", &rb::RubberBandStretcher::setDebugLevel, "level"_a);
}

void define_stretcher_getters_only(nb::class_<rb::RubberBandStretcher>& cls)
{
  // these are not properties, as their values do depend on the current state of the stretcher
  cls.def("get_available", &rb::RubberBandStretcher::available);
  cls.def("get_preferred_start_pad", &rb::RubberBandStretcher::getPreferredStartPad);
  cls.def("get_start_delay", &rb::RubberBandStretcher::getStartDelay);
  cls.def("get_samples_required", &rb::RubberBandStretcher::getSamplesRequired);
  cls.def("get_input_increment", &rb::RubberBandStretcher::getInputIncrement);
  cls.def("get_output_increment", &rb::RubberBandStretcher::getOutputIncrements);
  cls.def("get_phase_reset_curve", &rb::RubberBandStretcher::getPhaseResetCurve);
  cls.def("get_exact_time_points", &rb::RubberBandStretcher::getExactTimePoints);
}

void define_stretcher_method_study(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "study",
      [](rb::RubberBandStretcher& stretcher, NbAudioArrayArg_t audio, bool const final)
      {
        size_t const channels_num = stretcher.getChannelCount();
        size_t const samples_num = audio.shape(RB_SAMPLE_IDX);
        if (audio.shape(RB_CHANNEL_IDX) != channels_num)
        {
          throw std::runtime_error("Wrong number of audio channels");
        }

        auto const& audio_per_channel = get_audio_ptr_per_channel(audio.data(), channels_num, samples_num);
        stretcher.study(audio_per_channel.data(), samples_num, final);
      },
      "audio_data"_a,
      "final"_a = false,
      nb::call_guard<nb::gil_scoped_release>());
}

void define_stretcher_method_process(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "process",
      [](rb::RubberBandStretcher& stretcher, NbAudioArrayArg_t audio, bool const final)
      {
        size_t const channels_num = stretcher.getChannelCount();
        size_t const samples_num = audio.shape(RB_SAMPLE_IDX);
        if (audio.shape(RB_CHANNEL_IDX) != channels_num)
        {
          throw std::runtime_error("Wrong number of audio channels");
        }

        auto const& audio_per_channel = get_audio_ptr_per_channel(audio.data(), channels_num, samples_num);
        stretcher.process(audio_per_channel.data(), samples_num, final);
      },
      "audio_data"_a,
      "final"_a = false,
      nb::call_guard<nb::gil_scoped_release>());
}

void define_stretcher_method_retrieve(nb::class_<rb::RubberBandStretcher>& cls)
{
  cls.def(
      "retrieve",
      [](rb::RubberBandStretcher& stretcher, size_t samples_num)
      {
        size_t const channels_num = stretcher.getChannelCount();
        samples_num = std::min(samples_num, (size_t)(std::max(0, stretcher.available())));  // available == -1 when done

        NbAudioArrayRet_t audio = create_audio_array(channels_num, samples_num);
        auto const& audio_per_channel = get_audio_ptr_per_channel(audio.data(), channels_num, samples_num);

        stretcher.retrieve(audio_per_channel.data(), samples_num);

        return audio;
      },
      "samples_num"_a,
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
