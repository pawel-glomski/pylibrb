from typing import List, Union

import numpy as np

from .pylibrb_ext import *

import importlib.metadata

__version__ = importlib.metadata.version("pylibrb")

del importlib

DType = np.dtype(DTYPE_NAME)
"""The data type used internally for audio."""


def reorder_to_rb(audio: np.ndarray, samples_axis: int) -> np.ndarray:
    """If needed, changes the (logical) layout of audio to make it `pylibrb-compatible`.

    This only returns a view of the provided array (only the logical layout may be changed), thus
    the actual memory order won't be affected. `pylibrb` will make a copy if the input of
    `process()` or `study()` is not C-contiguous.

    Args:
        rb_audio:
          Audio to be reordered.
        samples_axis:
          Which axis is used for samples. All other axes will be treated as separate channels.

    Returns:
        np.ndarray:
          View of the provided audio with the `pylibrb-compatible` layout.
    """
    output_shape = [-1, -1]
    output_shape[SAMPLES_AXIS] = audio.shape[samples_axis]
    # squeezes all axes into a single "channel" axis, except for the `samples_axis` axis
    return np.moveaxis(audio, [samples_axis], [-SAMPLES_AXIS]).reshape(output_shape)


def reorder_from_rb(
    rb_audio: np.ndarray, wanted_shape: List[Union[int, None]]
) -> np.ndarray:
    """If needed, changes the (logical) layout of pylibrb-compatible audio to match the specified
    layout.

    This only returns a view of the provided audio (only the logical layout may be changed) thus the
    actual memory order will be unchanged.

    Args:
        rb_audio:
          pylibrb-compatible audio to be reordered.
        wanted_shape:
          What should be the shape of the output. This list should contain at least one `None`,
          which will specify the axis for samples. The shape can contain a single `-1` value.

    Returns:
        np.ndarray:
          View of the provided audio with the specified layout.
    """
    wanted_samples_axis = wanted_shape.index(None)
    wanted_shape = (
        wanted_shape[:wanted_samples_axis] + wanted_shape[wanted_samples_axis + 1 :]
    )
    current_shape = [rb_audio.shape[SAMPLES_AXIS]]
    current_shape[CHANNELS_AXIS:CHANNELS_AXIS] = wanted_shape
    return np.moveaxis(
        rb_audio.reshape(current_shape), [-SAMPLES_AXIS], [wanted_samples_axis]
    )
