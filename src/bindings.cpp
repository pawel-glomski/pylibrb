#include "bindings.hpp"

namespace {

void define_constants(nb::module_& m)
{
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

void define_rubberband_option_enum(nb::module_& m)
{
  nb::enum_<rb::RubberBandStretcher::Option>(m, "Option")
      .value("ProcessOffline", rb::RubberBandStretcher::Option::OptionProcessOffline)
      .value("ProcessRealTime", rb::RubberBandStretcher::Option::OptionProcessRealTime)
      .value("TransientsCrisp", rb::RubberBandStretcher::Option::OptionTransientsCrisp)
      .value("TransientsMixed", rb::RubberBandStretcher::Option::OptionTransientsMixed)
      .value("TransientsSmooth", rb::RubberBandStretcher::Option::OptionTransientsSmooth)
      .value("DetectorCompound", rb::RubberBandStretcher::Option::OptionDetectorCompound)
      .value("DetectorPercussive", rb::RubberBandStretcher::Option::OptionDetectorPercussive)
      .value("DetectorSoft", rb::RubberBandStretcher::Option::OptionDetectorSoft)
      .value("PhaseLaminar", rb::RubberBandStretcher::Option::OptionPhaseLaminar)
      .value("PhaseIndependent", rb::RubberBandStretcher::Option::OptionPhaseIndependent)
      .value("ThreadingAuto", rb::RubberBandStretcher::Option::OptionThreadingAuto)
      .value("ThreadingNever", rb::RubberBandStretcher::Option::OptionThreadingNever)
      .value("ThreadingAlways", rb::RubberBandStretcher::Option::OptionThreadingAlways)
      .value("WindowStandard", rb::RubberBandStretcher::Option::OptionWindowStandard)
      .value("WindowShort", rb::RubberBandStretcher::Option::OptionWindowShort)
      .value("WindowLong", rb::RubberBandStretcher::Option::OptionWindowLong)
      .value("SmoothingOff", rb::RubberBandStretcher::Option::OptionSmoothingOff)
      .value("SmoothingOn", rb::RubberBandStretcher::Option::OptionSmoothingOn)
      .value("FormantShifted", rb::RubberBandStretcher::Option::OptionFormantShifted)
      .value("FormantPreserved", rb::RubberBandStretcher::Option::OptionFormantPreserved)
      .value("PitchHighSpeed", rb::RubberBandStretcher::Option::OptionPitchHighSpeed)
      .value("PitchHighQuality", rb::RubberBandStretcher::Option::OptionPitchHighQuality)
      .value("PitchHighConsistency", rb::RubberBandStretcher::Option::OptionPitchHighConsistency)
      .value("ChannelsApart", rb::RubberBandStretcher::Option::OptionChannelsApart)
      .value("ChannelsTogether", rb::RubberBandStretcher::Option::OptionChannelsTogether)
      .value("EngineFaster", rb::RubberBandStretcher::Option::OptionEngineFaster)
      .value("EngineFiner", rb::RubberBandStretcher::Option::OptionEngineFiner);

  nb::enum_<rb::RubberBandStretcher::PresetOption>(m, "OptionsPreset", nb::is_arithmetic())
      .value("Default", rb::RubberBandStretcher::PresetOption::DefaultOptions)
      .value("Percussive", rb::RubberBandStretcher::PresetOption::PercussiveOptions);
}

void define_rubberband_stretcher_class(nb::module_& m)
{
  nb::class_<rb::RubberBandStretcher>(m, "RubberBandStretcher")
      // TODO: add init version with logger
      .def(nb::init<size_t, size_t, int, double, double>(),
           "sample_rate"_a,
           "channels"_a,
           "options"_a = rb::RubberBandStretcher::PresetOption::DefaultOptions,
           "initial_time_ratio"_a = 1.0,
           "initial_pitch_scale"_a = 1.0)
      // setters with getters
      .def_prop_rw("time_ratio", &rb::RubberBandStretcher::getTimeRatio, &rb::RubberBandStretcher::setTimeRatio)
      .def_prop_rw("pitch_scale", &rb::RubberBandStretcher::getPitchScale, &rb::RubberBandStretcher::setPitchScale)
      .def_prop_rw("formant_scale_r3", &rb::RubberBandStretcher::getFormantScale, &rb::RubberBandStretcher::setFormantScale)
      .def("set_frequency_cutoff_r2", &rb::RubberBandStretcher::setFrequencyCutoff, "n"_a, "f"_a)
      .def("get_frequency_cutoff_r2", &rb::RubberBandStretcher::getFrequencyCutoff, "n"_a)
      // setters only
      .def("set_transients_options_r2_realtime", &rb::RubberBandStretcher::setTransientsOption, "options"_a)
      .def("set_detector_options_r2_realtime", &rb::RubberBandStretcher::setDetectorOption, "options"_a)
      .def("set_phase_options_r2", &rb::RubberBandStretcher::setPhaseOption, "options"_a)
      .def("set_formant_options", &rb::RubberBandStretcher::setFormantOption, "options"_a)
      .def("set_pitch_options_r2_realtime", &rb::RubberBandStretcher::setPitchOption, "options"_a)
      .def("set_expected_input_duration_offline", &rb::RubberBandStretcher::setExpectedInputDuration, "samples"_a)
      .def("set_max_process_size", &rb::RubberBandStretcher::setMaxProcessSize, "samples"_a)
      .def("set_keyframe_map_offline", &rb::RubberBandStretcher::setKeyFrameMap, "mapping"_a)
      .def("set_logging_level", &rb::RubberBandStretcher::setDebugLevel, "level"_a)
      // getters only (constant)
      .def_prop_ro("channels", &rb::RubberBandStretcher::getChannelCount)
      .def_prop_ro("engine_version", &rb::RubberBandStretcher::getEngineVersion)
      // getters only (variable)
      .def("get_available", &rb::RubberBandStretcher::available)
      .def("get_preferred_start_pad_realtime", &rb::RubberBandStretcher::getPreferredStartPad)
      .def("get_start_delay_realtime", &rb::RubberBandStretcher::getStartDelay)
      .def("get_samples_required", &rb::RubberBandStretcher::getSamplesRequired)
      .def("get_input_increment_r2", &rb::RubberBandStretcher::getInputIncrement)
      .def("get_output_increment_r2", &rb::RubberBandStretcher::getOutputIncrements)
      .def("get_phase_reset_curve_r2", &rb::RubberBandStretcher::getPhaseResetCurve)
      .def("get_exact_time_points_r2_offline", &rb::RubberBandStretcher::getExactTimePoints)
      // methods
      .def("reset", &rb::RubberBandStretcher::reset)
      .def(
          "study_offline",
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
          nb::call_guard<nb::gil_scoped_release>())
      .def(
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
          nb::call_guard<nb::gil_scoped_release>())
      .def(
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
          nb::call_guard<nb::gil_scoped_release>())
      .def("calculate_stretch_r2_offline", &rb::RubberBandStretcher::calculateStretch);
}

}  // namespace

NB_MODULE(pylibrb_ext, m)
{
  define_constants(m);
  define_module_functions(m);
  define_rubberband_option_enum(m);
  define_rubberband_stretcher_class(m);
}
