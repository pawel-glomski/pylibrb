import pytest

import pylibrb
from pylibrb import RubberBandStretcher, Option


@pytest.fixture
def realtime_stretcher():
  yield RubberBandStretcher(sample_rate=16000,
                            channels=1,
                            options=Option.PROCESS_REALTIME | Option.ENGINE_FINER)


class TestStretcherInit:

  @pytest.mark.parametrize('sample_rate, expected_exc', [
      (-1, TypeError),
      (pylibrb.MIN_SAMPLE_RATE - 1, ValueError),
      (pylibrb.MAX_SAMPLE_RATE + 1, ValueError),
  ])
  def test_init_should_raise_proper_error_when_invalid_sample_rate(self, sample_rate: int,
                                                                   expected_exc: Exception):
    with pytest.raises(expected_exc):
      RubberBandStretcher(sample_rate=sample_rate, channels=1)

  @pytest.mark.parametrize('channels, expected_exc', [
      (-1, TypeError),
      (0, ValueError),
      (pylibrb.MAX_CHANNELS_NUM + 1, ValueError),
  ])
  def test_init_should_raise_proper_error_when_invalid_channels(self, channels: int,
                                                                expected_exc: Exception):
    with pytest.raises(expected_exc):
      RubberBandStretcher(16000, channels=channels)

  @pytest.mark.parametrize('options, expected_exc', [
      ('Option.PRESET_DEFAULT', TypeError),
      (-1, TypeError),
  ])
  def test_init_should_raise_proper_error_when_invalid_options(self, options: Option,
                                                               expected_exc: Exception):
    with pytest.raises(expected_exc):
      RubberBandStretcher(sample_rate=16000, channels=1, options=options)

  @pytest.mark.parametrize('time_ratio, expected_exc', [
      (-1.0, ValueError),
      (0.0, ValueError),
      ('0', TypeError),
  ])
  def test_init_should_raise_proper_error_when_invalid_time_ratio(self, time_ratio: float,
                                                                  expected_exc: Exception):
    with pytest.raises(expected_exc):
      RubberBandStretcher(sample_rate=16000, channels=1, initial_time_ratio=time_ratio)

  @pytest.mark.parametrize('pitch_scale, expected_exc', [
      (-1.0, ValueError),
      (0.0, ValueError),
      ('0', TypeError),
  ])
  def test_init_should_raise_proper_error_when_invalid_pitch_scale(self, pitch_scale: float,
                                                                   expected_exc: Exception):
    with pytest.raises(expected_exc):
      RubberBandStretcher(sample_rate=16000, channels=1, initial_pitch_scale=pitch_scale)

  def test_init_should_create_stretcher_with_correct_state_when_valid_args(self):
    stretcher = RubberBandStretcher(sample_rate=16000,
                                    channels=pylibrb.MAX_CHANNELS_NUM,
                                    options=Option.ENGINE_FINER,
                                    initial_time_ratio=0.5,
                                    initial_pitch_scale=0.5)

    assert stretcher.channels == pylibrb.MAX_CHANNELS_NUM
    assert stretcher.engine_version == 3
    assert stretcher.time_ratio == 0.5
    assert stretcher.pitch_scale == 0.5
    assert stretcher.available() == 0
    assert stretcher.is_done() == False


class TestRealtimeStretcher:

  def test_process_should_raise_value_error_when_incorrect_audio_layout(
      self, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher

    bad_audio_data = pylibrb.create_audio_array(stretcher.channels, 512).T  # transposed

    with pytest.raises(ValueError):
      stretcher.process(bad_audio_data)

  def test_process_should_succeed_when_valid_audio(self, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher
    required_samples_before = stretcher.get_samples_required()
    audio_samples = required_samples_before // 2
    audio_data = pylibrb.create_audio_array(stretcher.channels, audio_samples)

    stretcher.process(audio_data)

    assert stretcher.get_samples_required() == required_samples_before - audio_samples

  def test_available_should_return_zero_when_not_enough_samples_provided(
      self, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher
    audio_data = pylibrb.create_audio_array(stretcher.channels,
                                            stretcher.get_samples_required() - 1)

    stretcher.process(audio_data)

    assert stretcher.available() == 0

  def test_available_should_return_number_of_available_samples_when_enough_samples_provided(
      self, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher
    audio_data = pylibrb.create_audio_array(stretcher.channels, stretcher.get_samples_required())

    stretcher.process(audio_data)

    assert stretcher.available() > 0

  def test_retrieve_should_return_empty_array_when_result_is_not_available(
      self, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher
    audio_data = pylibrb.create_audio_array(stretcher.channels,
                                            stretcher.get_samples_required() - 1)

    stretcher.process(audio_data)

    assert stretcher.retrieve(512).size == 0

  def test_retrieve_should_return_correct_number_of_samples_when_result_is_available(
      self, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher
    audio_data = pylibrb.create_audio_array(stretcher.channels, stretcher.get_samples_required())

    stretcher.process(audio_data)
    available_samples = stretcher.available()

    assert available_samples > 0
    result = stretcher.retrieve(available_samples)

    assert result.shape[pylibrb.SAMPLES_AXIS] == available_samples
    assert result.shape[pylibrb.CHANNELS_AXIS] == stretcher.channels

    # since we just took all the available audio, there shouldn't be any left
    assert stretcher.retrieve(available_samples).size == 0

  @pytest.mark.parametrize('time_ratio', [1.0, 0.5])
  def test_retrieve_should_return_expected_number_of_samples_for_given_time_ratio(
      self, time_ratio: float, realtime_stretcher: RubberBandStretcher):
    stretcher = realtime_stretcher

    audio_data = pylibrb.create_audio_array(stretcher.channels,
                                            stretcher.get_samples_required(),
                                            init_value=1)
    audio_samples = audio_data.shape[pylibrb.SAMPLES_AXIS]

    expected_samples = 0.0
    observed_samples = 0
    iters = 10

    stretcher.time_ratio = 1.0
    for _ in range(iters):
      stretcher.process(audio_data)
      expected_samples += audio_samples * stretcher.time_ratio
      observed_samples += stretcher.retrieve(stretcher.available()).shape[pylibrb.SAMPLES_AXIS]

    stretcher.time_ratio = time_ratio
    for i in range(iters):
      stretcher.process(audio_data, final=(i + 1) == iters)
      expected_samples += audio_samples * stretcher.time_ratio
      observed_samples += stretcher.retrieve(stretcher.available()).shape[pylibrb.SAMPLES_AXIS]

    relative_error = abs(expected_samples - observed_samples) / expected_samples
    assert relative_error <= 0.05
