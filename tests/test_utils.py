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


def test_reorder_to_rb_should_do_nothing_when_audio_with_correct_layout():
  audio = create_audio_array(2, 128)

  audio_reordered = reorder_to_rb(audio, channels_axis=pylibrb.CHANNELS_AXIS)

  assert audio_reordered.shape == audio.shape


def test_reorder_to_rb_should_reorder_audio_array_when_audio_with_wrong_layout():
  audio = create_audio_array(2, 128)

  # pass transposed audio array and thus also transposed channels axis (i.e. samples axis)
  audio_reordered = reorder_to_rb(audio.T, channels_axis=pylibrb.SAMPLES_AXIS)

  assert audio_reordered.shape == audio.shape


def test_reorder_from_rb_should_do_nothing_when_audio_with_correct_layout():
  rb_audio = create_audio_array(2, 128)

  audio_reordered = reorder_from_rb(rb_audio, wanted_channels_axis=pylibrb.CHANNELS_AXIS)

  assert audio_reordered.shape == rb_audio.shape


def test_reorder_from_rb_should_reorder_audio_array_when_audio_with_wrong_layout():
  rb_audio = create_audio_array(2, 128)

  # pass samples axis as channels axis
  audio_reordered = reorder_from_rb(rb_audio, wanted_channels_axis=pylibrb.SAMPLES_AXIS)

  assert audio_reordered.shape == rb_audio.T.shape
