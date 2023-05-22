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
      wanted_channels_axis: 
        Which axis is used for channels.

  Returns:
      np.ndarray:
        View of the provided audio with the pylibrb-compatible layout.
  """
  assert channels_axis in [0, 1]
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
