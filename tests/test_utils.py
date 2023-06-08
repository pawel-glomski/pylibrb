import pytest

import numpy as np

import pylibrb
from pylibrb import create_audio_array, reorder_to_rb, reorder_from_rb


def test_create_audio_array_should_create_array_with_correct_shape():
  audio = create_audio_array(2, 128)

  assert audio.shape[pylibrb.CHANNELS_AXIS] == 2
  assert audio.shape[pylibrb.SAMPLES_AXIS] == 128


def test_create_audio_array_should_create_array_with_correct_value():
  audio = create_audio_array(2, 128, 321)

  assert np.all(audio == 321)


def test_reorder_to_rb_should_raise_index_error_when_bad_samples_axis():
  audio = create_audio_array(2, 128)

  with pytest.raises(IndexError):
    reorder_to_rb(audio, samples_axis=2)


def test_reorder_to_rb_should_do_nothing_when_audio_with_correct_layout():
  audio = create_audio_array(2, 128)

  audio_reordered = reorder_to_rb(audio, samples_axis=pylibrb.SAMPLES_AXIS)

  assert audio_reordered.shape == audio.shape


def test_reorder_to_rb_should_reorder_audio_array_when_audio_with_wrong_layout():
  audio = create_audio_array(2, 128)

  # pass transposed audio array and thus also transposed samples axis (i.e. channels axis)
  audio_reordered = reorder_to_rb(audio.T, samples_axis=pylibrb.CHANNELS_AXIS)

  assert audio_reordered.shape == audio.shape


def test_reorder_to_rb_should_reorder_audio_array_when_audio_with_wrong_complex_layout():
  audio = create_audio_array(1, 2 * 4 * 8 * 4).reshape(2, 4, 8, 4)

  audio_reordered = reorder_to_rb(audio, samples_axis=2)  # select 3rd axis of shape 8

  expected_shape = [8, 8]
  expected_shape[pylibrb.CHANNELS_AXIS] = 2 * 4 * 1 * 4
  assert audio_reordered.shape == tuple(expected_shape)


def test_reorder_from_rb_should_raise_value_error_when_missing_None_in_wanted_shape():
  audio = create_audio_array(2, 128)

  with pytest.raises(ValueError):
    reorder_from_rb(audio, wanted_shape=(2, 128))


def test_reorder_from_rb_should_do_nothing_when_audio_with_correct_layout():
  rb_audio = create_audio_array(2, 128)

  wanted_shape = [-1, -1]
  wanted_shape[pylibrb.SAMPLES_AXIS] = None
  audio_reordered = reorder_from_rb(rb_audio, wanted_shape=wanted_shape)

  assert audio_reordered.shape == rb_audio.shape


def test_reorder_from_rb_should_reorder_audio_array_when_audio_with_wrong_layout():
  rb_audio = create_audio_array(2, 128)

  # pass samples axis as channels axis
  wanted_shape = [2, 2]
  wanted_shape[pylibrb.CHANNELS_AXIS] = None
  audio_reordered = reorder_from_rb(rb_audio, wanted_shape=wanted_shape)

  assert audio_reordered.shape == rb_audio.T.shape


def test_reorder_from_rb_should_reorder_audio_array_when_audio_with_wrong_complex_layout():
  audio = create_audio_array(24, 128).reshape(1, 2, 128, 3, 4)
  audio[0, 0, :, 0, 0] = np.arange(128)
  audio[-1, -1, :, -1, -1] = np.arange(128, 2 * 128)

  rb_audio = reorder_to_rb(audio, samples_axis=2)
  audio_reordered = reorder_from_rb(rb_audio, wanted_shape=[1, 2, None, 3, 4])

  assert audio_reordered.shape == audio.shape
  assert np.array_equal(audio[0, 0, :, 0, 0], np.arange(128))
  assert np.array_equal(audio[-1, -1, :, -1, -1], np.arange(128, 2 * 128))
