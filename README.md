# pylibrb
[![tests](https://github.com/pawel-glomski/pylibrb/actions/workflows/test.yml/badge.svg)](https://github.com/pawel-glomski/pylibrb/actions/workflows/test.yml)

pylibrb (py-lib-rubberband) is a simple Python extension exposing [Rubber Band Library](https://breakfastquay.com/rubberband/) using [nanobind](https://github.com/wjakob/nanobind) bindings.

Since this is not a wrapper around a command-line app (like [pyrubberband](https://github.com/bmcfee/pyrubberband)), both offline and real-time modes are available.

Currently this extenstion exposes only a single class: `RubberBandStretcher`, which implements all the functionalities of the underlying C++ class. The interface is nearly identical to the original library, with a few changes to make it a bit more Pythonic by:
 - using `snake_case`
 - not using (magic) numbers to represent the state

Throughout the library, audio is accepted and returned in the form of [NumPy](https://github.com/numpy/numpy) ndarrays.

## Example

```python
from pylibrb import RubberBandStretcher, Option, create_audio_array

# create a stretcher
stretcher = RubberBandStretcher(sample_rate=16000,
                                channels=1,
                                options=Option.PROCESS_REALTIME | Option.ENGINE_FINER,
                                initial_time_ratio=0.5)
stretcher.set_max_process_size(1024)

# provide the audio to the stretcher, until some output is available
audio_in = create_audio_array(channels_num=1, samples_num=1024)
while not stretcher.available():
  audio_in[:] = 0  # get the next batch of samples, here we just use silence
  stretcher.process(audio_in)

# retrieve the available samples
audio_out = stretcher.retrieve(stretcher.available())

```

For more instructions, read the docstings of the `RubberBandStretcher` class and the `Option` enum, or see the [documentation of Rubber Band Library](https://breakfastquay.com/rubberband/documentation.html).