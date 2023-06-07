import numpy as np

from .pylibrb_ext import *

DType = np.dtype(DTYPE_NAME)
'''The data type used internally for audio.'''


def reorder_to_rb(audio: np.ndarray, channels_axis: int) -> np.ndarray:
  """If needed, changes the (logical) layout of audio to make it pylibrb-compatible.
  
  Generally this only returns a view of the provided audio (only the logical layout may be changed)
  thus the actual memory order is unchanged. When an array is provided to `pylibrb`, it makes a copy
  if the memory order is not C-contiguous.

  Args:
      rb_audio:
        Audio to be reordered.
      channels_axis: 
        Which axis is used for channels.

  Returns:
      np.ndarray:
        View of the provided audio with the pylibrb-compatible layout.
  """
  if channels_axis not in [0, 1]:
    # TODO: when adding support for batched audio:
    # - add `samples_axis` argument
    # audio = np.moveaxis(audio, [channel_axis, samples_axis], [-1-CHANNELS_AXIS, -1-SAMPLES_AXIS])
    # audio = audio.reshape((-1, *audio.shape[-2:]))
    #
    # then `reorder_from_rb` would have to revert this operation:
    # - add `wanted_shape` argument, remove `wanted_channels_axis`
    # wanted_channels_axis = wanted_shape.index('c')
    # wanted_samples_axis = wanted_shape.index('s')
    # current_shape = list(wanted_shape + rb_audio.shape[-2:])
    # del current_shape[wanted_channels_axis]
    # del current_shape[wanted_samples_axis]
    # rb_audio.reshape(current_shape)
    # rb_audio = np.moveaxis(rb_audio, [-1-CHANNELS_AXIS, -1-SAMPLES_AXIS],
    #                                  [wanted_channels_axis, wanted_samples_axis])
    raise ValueError(f'{channels_axis=} is not supported, audio must always have 2 dimensions: '
                     '{channels, samples}')
  if channels_axis == CHANNELS_AXIS:
    return audio
  return audio.T


def reorder_from_rb(rb_audio: np.ndarray, wanted_channels_axis: int) -> np.ndarray:
  """If needed, changes the (logical) layout of Rubber-Band-compatible audio to match the specified
  layout.
  
  For an array with `x` channels and `y` samples, the returned array will have the shape:
   - `(x, y)` for `wanted_channels_axis=0`
   - `(y, x)` for `wanted_channels_axis=1`

  Generally this only returns a view of the provided audio (only the logical layout may be changed)
  thus the actual memory order is unchanged.

  Args:
      rb_audio:
        pylibrb-compatible audio to be reordered.
      wanted_channels_axis: 
        Which axis should be used for channels.

  Returns:
      np.ndarray:
        View of the provided audio with the specified layout.
  """
  return reorder_to_rb(rb_audio, wanted_channels_axis)


del np
