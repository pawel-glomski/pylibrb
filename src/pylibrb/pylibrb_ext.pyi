from enum import Flag

import numpy as np

MIN_SAMPLE_RATE: int
'''Minimum sample rate an audio can have.'''

MAX_SAMPLE_RATE: int
'''Maximum sample rate an audio can have.'''

MAX_CHANNELS_NUM: int
'''Maximum number of channels an audio can have.'''

CHANNELS_AXIS: int
'''Axis of channels in an audio array.'''

SAMPLES_AXIS: int
'''Axis of samples in an audio array.'''

DTYPE_NAME: str
'''Name of the audio type in NumPy's format.'''

AUTO_FORMANT_SCALE: float
'''Default value of `formant_scale`, which causes the scale to be calculated automatically.

See the documentation of `RubberBandStretcher.formant_scale` for more details.
'''


class Option(Flag):
  '''Processing options for the timestretcher. The preferred options should normally be set in the
  constructor, as a bitwise OR of the option flags. The default value (Option.PRESET_DEFAULT) is 
  intended to give good results in most situations.
     - Flags prefixed `Option.PROCESS` determine how the timestretcher will be invoked. These
       options may not be changed after construction. The Process setting is likely to depend on
       your architecture: non-real-time operation on seekable files: Offline; real-time or streaming
       operation: RealTime.
     - Flags prefixed `Option.ENGINE` select the core Rubber Band processing engine to be used.
       These options may not be changed after construction.
     - Flags prefixed `Option.TRANSIENTS` control the component frequency phase-reset mechanism in
       the R2 engine, that may be used at transient points to provide clarity and realism to
       percussion and other significant transient sounds. These options have no effect when using
       the R3 engine. These options may be changed after construction when running in real-time
       mode, but not when running in offline mode.
     - Flags prefixed `Option.DETECTOR` control the type of transient detector used in the R2
       engine. These options have no effect when using the R3 engine. These options may be changed
       after construction when running in real-time mode, but not when running in offline mode.
     - Flags prefixed `Option.PHASE` control the adjustment of component frequency phases in the R2
       engine from one analysis window to the next during non-transient segments. These options have
       no effect when using the R3 engine. These options may be changed at any time.
     - Flags prefixed `Option.THREADING` control the threading model of the stretcher. These options
       may not be changed after construction.
     - Flags prefixed `Option.WINDOW` influence the window size for FFT processing. In the R2 engine
       these affect the resulting sound quality but have relatively little effect on processing
       speed. With the R3 engine they can dramatically affect processing speed as well as output
       quality. These options may not be changed after construction.
     - Flags prefixed `Option.SMOOTHING` control the use of window-presum FFT and time-domain
       smoothing in the R2 engine. These options have no effect when using the R3 engine.These
       options may not be changed after construction.
     - Flags prefixed `Option.FORMANT` control the handling of formant shape (spectral envelope)
       when pitch-shifting. These options affect both the R2 and R3 engines. These options may be
       changed at any time.
     - Flags prefixed `Option.PITCH` control the method used for pitch shifting. These options
       affect only realtime mode. In offline mode the method is not adjustable. In the R2 engine
       these options may be changed at any time; in the R3 engine they may be set only on
       construction.
     - Flags prefixed `Option.CHANNELS` control the method used for processing two-channel stereo
       audio. These options may not be changed after construction.
    '''

  CHANNELS_APART = ...
  '''Channels are handled for maximum individual fidelity, at the expense of synchronisation.
  In the R3 engine, this means frequency-bin synchronisation is maintained more closely for
  lower-frequency content than higher. In R2, it means the stereo channels are processed
  individually and only synchronised at transients. In both engines this gives the highest
  quality for the individual channels but a more diffuse stereo image, an unnatural increase
  in `width`, and generally a loss of mono compatibility (i.e. mono mixes from stereo can sound
  phasy). This option is the default.
  '''

  CHANNELS_TOGETHER = ...
  '''Channels are handled for higher synchronisation at some expense of individual fidelity. In
  particular, a stretcher processing two channels will treat its input as a stereo pair and aim to
  maximise clarity at the centre and preserve mono compatibility. This gives relatively less stereo
  space and width than the default, as well as slightly lower fidelity for individual channel
  content, but the results may be more appropriate for many situations making use of stereo mixes.
  '''

  DETECTOR_COMPOUND = ...
  '''Use a general-purpose transient detector which is likely to be good for most situations.
  This is the default.
  '''

  DETECTOR_PERCUSSIVE = ...
  '''Detect percussive transients.'''

  DETECTOR_SOFT = ...
  '''Use an onset detector with less of a bias toward percussive transients.
  This may give better results with certain material (e.g. relatively monophonic piano music).
  '''

  ENGINE_FASTER = ...
  '''Use the Rubber Band Library R2 (Faster) engine. This is the engine implemented in Rubber Band
  Library v1.x and v2.x, and it remains the default in newer versions. It uses substantially less
  CPU than the R3 engine and there are still many situations in which it is likely to be the more
  appropriate choice.
  '''

  ENGINE_FINER = ...
  '''Use the Rubber Band Library R3 (Finer) engine. This engine was introduced in Rubber Band
  Library v3.0. It produces higher-quality results than the R2 engine for most material, especially
  complex mixes, vocals and other sounds that have soft onsets and smooth pitch changes, and music
  with substantial bass content. However, it uses much more CPU power than the R2 engine.
  '''

  FORMANT_PRESERVED = ...
  '''Preserve the spectral envelope of the unshifted signal. This permits shifting the note
  frequency without so substantially affecting the perceived pitch profile of the voice or
  instrument.
  '''

  FORMANT_SHIFTED = ...
  '''Apply no special formant processing. The spectral envelope will be pitch shifted as normal.
  This is the default.
  '''

  PHASE_INDEPENDENT = ...
  '''Adjust the phase in each frequency bin independently from its neighbours. This usually results
  in a slightly softer, phasier sound.
  '''

  PHASE_LAMINAR = ...
  '''Adjust phases when stretching in such a way as to try to retain the continuity of phase
  relationships between adjacent frequency bins whose phases are behaving in similar ways. This, the
  default setting, should give good results in most situations.
  '''

  PITCH_HIGH_CONSISTENCY = ...
  '''Use a method that supports dynamic pitch changes without discontinuities, including when
  crossing the 1.0 pitch scale. This may cost more in CPU than the default, especially when the
  pitch scale is exactly 1.0. You should use this option whenever you wish to support dynamically
  changing pitch shift during processing.
  '''

  PITCH_HIGH_QUALITY = ...
  '''Favour sound quality over CPU cost. Use this for fixed pitch shifts where sound quality is of
  most concern. Do not use this for arbitrarily time-varying pitch shifts
  (see `Option.PITCH_HIGH_CONSISTENCY` below).'''

  PITCH_HIGH_SPEED = ...
  '''Favour CPU cost over sound quality. This is the default. Use this when time-stretching only, or
  for fixed pitch shifts where CPU usage is of concern. Do not use this for arbitrarily time-varying
  pitch shifts (see `Option.PITCH_HIGH_CONSISTENCY` below).
  '''

  PROCESS_OFFLINE = ...
  '''Run the stretcher in offline mode. In this mode the input data needs to be provided twice, once
  to `study()`, which calculates a stretch profile for the audio, and once to `process()`,
  which stretches it.
  '''

  PROCESS_REALTIME = ...
  '''Run the stretcher in real-time mode. In this mode only `process()` should be called, and the
  stretcher adjusts dynamically in response to the input audio.
  '''

  SMOOTHING_OFF = ...
  '''Do not use time-domain smoothing.'''

  SMOOTHING_ON = ...
  '''Use time-domain smoothing. This will result in a softer sound with some audible artifacts
  around sharp transients, but it may be appropriate for longer stretches of some instruments and
  can mix well with `Option.WINDOW_SHORT`.
  '''

  THREADING_ALWAYS = ...
  '''Use multiple threads in any situation where `Option.THREADING_AUTO` would do so, except omit
  the check for multiple CPUs and instead assume it to be true.
  '''

  THREADING_AUTO = ...
  '''Permit the stretcher to determine its own threading model. In the R2 engine this means using
  one processing thread per audio channel in offline mode if the stretcher is able to determine that
  more than one CPU is available, and one thread only in realtime mode. The R3 engine does not
  currently have a multi-threaded mode, but if one is introduced in future, this option may use it.
  This is the default.
  '''

  THREADING_NEVER = ...
  '''Never use more than one thread.'''

  TRANSIENTS_CRISP = ...
  '''Reset component phases at the peak of each transient (the start of a significant note or
  percussive event). This, the default setting, usually results in a clear-sounding output; but it
  is not always consistent, and may cause interruptions in stable sounds present at the same time as
  transient events. The `Option.DETECTOR` flags (below) can be used to tune this to some extent.
  '''

  TRANSIENTS_MIXED = ...
  '''Reset component phases at the peak of each transient, outside a frequency range typical of
  musical fundamental frequencies. The results may be more regular for mixed stable and percussive
  notes than `Option.TRANSIENTS_CRISP`, but with a "phasier" sound. The balance may sound very good
  for certain types of music and fairly bad for others.
  '''

  TRANSIENTS_SMOOTH = ...
  '''Do not reset component phases at any point. The results will be smoother and more regular but
  may be less clear than with either of the other transients flags.
  '''

  WINDOW_LONG = ...
  '''Use a longer window. With the R2 engine this is likely to result in a smoother sound at the
  expense of clarity and timing. The R3 engine currently ignores this option, treating it like
  `Option.WINDOW_STANDARD`.
  '''

  WINDOW_SHORT = ...
  '''Use a shorter window. This has different effects with R2 and R3 engines. With the R2 engine it
  may result in crisper sound for audio that depends strongly on its timing qualities, but is likely
  to sound worse in other ways and will have similar efficiency. With the R3 engine, it causes the
  engine to be restricted to a single window size, resulting in both dramatically faster processing
  and lower delay than `Option.WINDOW_STANDARD`, but at the expense of some sound quality. It may
  still sound better for non-percussive material than the R2 engine. With both engines it reduces
  the start delay somewhat (see `get_start_delay)` which may be useful for real-time
  handling.
  '''

  WINDOW_STANDARD = ...
  '''Use the default window size. The actual size will vary depending on other parameters. This
  option is expected to produce better results than the other window options in most situations.
  In the R3 engine this causes the engine's full multi-resolution processing scheme to be used.
  '''

  PRESET_DEFAULT = ...
  '''Default preset (Offline)'''

  PRESET_PERCUSSIVE = ...
  '''Percussive preset'''


class RubberBandStretcher:
  '''The Rubber Band stretcher supports two processing modes, offline and real-time, and two
  processing "engines", known as the R2 or Faster engine and the R3 or Finer engine.The choices of
  processing mode and engine are fixed on construction. The two engines work identically in API
  terms, and both of them support both offline and real-time modes as described below.

  Offline mode:
    In offline mode, you must provide the audio block-by-block in two passes. In the first pass,
    call `study()` on each block; in the second pass, call `process()` on each block and
    receive the output via `retrieve()`.

    In offline mode, the time and pitch ratios are fixed as soon as the study pass has begun and
    cannot be changed afterwards. (But see `set_keyframe_map()` for a way to do pre-planned
    variable time stretching in offline mode.) Offline mode also performs padding and delay
    compensation so that the stretched result has an exact start and duration.
  
  Real-time mode:
    In real-time mode, there is no study pass, just a single streaming pass in which the audio is
    passed to `process()` and output received via `retrieve()`.
  
    In real-time mode you can change the time and pitch ratios at any time. You may need to perform
    signal padding and delay compensation in real-time mode; see
    `get_preferred_start_pad()` and `get_start_delay()` for details.
  
  Rubber Band Library is RT-safe when used in real-time mode with "normal" processing parameters.
  That is, it performs no allocation, locking, or blocking operations after initialisation during
  normal use, even when the time and pitch ratios change. There are certain exceptions that include
  error states and extremely rapid changes between extreme ratios, as well as the case in which more
  frames are passed to `process()` than the values returned by `get_samples_required()` or set using
  `set_max_process_size()`, when buffer reallocation may occur. Note that offline mode is never
  RT-safe.
  
  Thread safety:
    Multiple instances of `RubberBandStretcher` may be created and used in separate threads
    concurrently However, for any single instance of `RubberBandStretcher`, you may not call
    `process()` more than once concurrently, and you may not change the time or pitch ratio while a
    `process()` call is being executed (if the stretcher was created in real-time mode; in offline
    mode you can't change the ratios during use anyway). So you can run `process()` in its own
    thread if you like, but if you want to change ratios dynamically from a different thread, you
    will need some form of mutex in your code. Changing the time or pitch ratio is real-time safe
    except in extreme circumstances, so for most applications that may change these dynamically it
    probably makes most sense to do so from the same thread as calls `process()`, even if that is a
    real-time thread.
  '''

  def __init__(self,
               sample_rate: int,
               channels: int,
               options: Option = Option.PRESET_DEFAULT,
               initial_time_ratio: float = 1.0,
               initial_pitch_scale: float = 1.0) -> None:
    '''Constructs a time and pitch stretcher object to run at the given sample rate, with the given
    number of channels.

    Both of the stretcher engines provide their best balance of quality with efficiency at sample
    rates of 44100 or 48000 Hz. Other rates may be used, and the stretcher should produce sensible
    output with any rate from 8000 to 192000 Hz, but you are advised to use 44100 or 48000 where
    practical. Do not use rates below 8000 or above 192000 Hz.

    Initial time and pitch scaling ratios and other processing options may be provided. In
    particular, the behaviour of the stretcher depends strongly on whether offline or real-time mode
    is selected on construction (via `Option.PROCESS_OFFLINE` or `Option.PROCESS_REALTIME` option.
    Offline is the default).

    Args:
      sample_rate:
        Sample rate of the audio.
      channels:
        Number of channels of the audio.
      options (optional):
        Processing options. The behaviour of the stretcher depends strongly on whether offline or
        real-time mode is selected. See `Option` for possible options. Defaults to
        `Option.PRESET_DEFAULT`.
      initial_time_ratio (optional):
        Initial time ratio. Defaults to 1.0.
      initial_pitch_scale (optional):
        Initial pitch scale. Defaults to 1.0.
    '''

  @property
  def channels(self) -> int:
    '''The number of channels this stretcher was constructed with.'''

  @property
  def engine_version(self) -> int:
    '''The active internal engine version, according to the `Option.ENGINE`  flag supplied on
    construction. This will return 2 for the R2 (Faster) engine or 3 for the R3 (Finer) engine.'''

  @property
  def formant_scale(self) -> float:
    '''Get or set a pitch scale for the vocal formant envelope, separate from the overall pitch
    scale. 

    This is a ratio of target frequency to source frequency. For example, a ratio of 2.0 would shift
    the formant envelope up by one octave; 0.5 down by one octave; or 1.0 leave the formant
    unaffected.

    By default this is set to the special value of `AUTO_FORMANT_SCALE`, which causes the scale to
    be calculated automatically. It will be treated as 1.0 / the pitch scale if
    `Option.FORMANT_PRESERVED` is specified, or 1.0 for `Option.FORMANT_SHIFTED`.

    Conversely, if this is set to a value other than the default 0.0, formant shifting will happen
    regardless of the state of the `Option.FORMANT_PRESERVED`/`Option.FORMANT_SHIFTED` option.

    This property is provided for special effects only. You do not need to call it for ordinary
    pitch shifting, with or without formant preservation - just specify or omit the
    `Option.FORMANT_PRESERVED` option as appropriate. Use this property only if you want to shift
    formants by a distance other than that of the overall pitch shift.

    This property is supported only in the R3 (`Option.ENGINE_FINER`) engine. It has no effect in R2
    (`Option.ENGINE_FASTER`).
    '''

  @formant_scale.setter
  def formant_scale(self) -> float:
    ...

  @property
  def pitch_scale(self) -> float:
    '''Get or set the pitch scaling ratio for the stretcher.
    
    This is the ratio of target frequency to source frequency. For example, a ratio of 2.0 would
    shift up by one octave; 0.5 down by one octave; or 1.0 leave the pitch unaffected.

    To put this in musical terms, a pitch scaling ratio corresponding to a shift of S equal-tempered
    semitones (where S is positive for an upwards shift and negative for downwards) is
    `pow(2.0, S / 12.0)`.

    If the stretcher was constructed in Offline mode, the pitch scaling ratio is fixed throughout
    operation; this property may be changed any number of times between construction (or a call to
    `reset()`) and the first call to `study()` or `process()`, but may not be changed after
    `study()` or `process()` has been called.
  
    If the stretcher was constructed in RealTime mode, the pitch scaling ratio may be varied during
    operation; this property may be changed at any time, so long as it is not changed concurrently
    with `process()`. You should either change this property from the same thread as `process()`,
    or provide your own mutex or similar mechanism to ensure that changing the `pitch_scale` and
    running `process()` cannot be done at once (there is no internal mutex for this purpose).
    '''

  @pitch_scale.setter
  def pitch_scale(self) -> float:
    ...

  @property
  def time_ratio(self) -> float:
    '''Get or set the time ratio for the stretcher.

    This is the ratio of stretched to unstretched duration -- not tempo. For example, a ratio of 2.0
    would make the audio twice as long (i.e. halve the tempo); 0.5 would make it half as long
    (i.e. double the tempo); 1.0 would leave the duration unaffected.

    If the stretcher was constructed in Offline mode, the time ratio is fixed throughout operation;
    this property may be changed any number of times between construction (or a call to `reset()`)
    and the first call to `study()` or `process()`, but may not be changed after
    `study()` or `process()` has been called.

    If the stretcher was constructed in RealTime mode, the time ratio may be varied during
    operation; this property may be changed at any time, so long as it is not changed concurrently
    with `process()`. You should either change this property from the same thread as `process()`,
    or provide your own mutex or similar mechanism to ensure that changing the `time_ratio` and
    running `process()` cannot be done at once (there is no internal mutex for this purpose).
    '''

  @time_ratio.setter
  def time_ratio(self, ratio: float) -> float:
    ...

  def calculate_stretch(self) -> None:
    '''Force the stretcher to calculate a stretch profile Normally this happens automatically for
    the first `process()` call in offline mode.

    This function is provided for diagnostic purposes only and is supported only with the R2 engine.
    '''

  def available(self) -> int:
    '''Ask the stretcher how many audio samples of output data are available for reading via
    `retrieve()`.

    Returns:
      The number of available samples or 0 if no samples are available - this usually means more
      input data needs to be provided, but if the stretcher is running in threaded mode it may just
      mean that not enough data has yet been processed Call `get_samples_required()` to discover
      whether more input is needed.
    '''

  def get_exact_time_points(self) -> list[float]:
    '''This function is provided for diagnostic purposes only and is supported only with the R2
    engine.


    Returns:
      In offline mode: the sequence of internal frames for which exact timing has been sought, for
      the entire audio data, provided the stretch profile has been calculated.
      
      In realtime mode: An empty list.
    '''

  def get_frequency_cutoff(self, n: int) -> float:
    '''This function is not for general use and is supported only with the R2 engine.

    Args:
      n: Which frequency cutoff to get.

    Returns:
      The value of internal frequency cutoff value n.
    '''

  def get_input_increment(self) -> int:
    '''This function is provided for diagnostic purposes only and is supported only with the R2
    engine.

    Returns:
      The value of the internal input block increment value.
    '''

  def get_output_increment(self) -> list[int]:
    '''This function is provided for diagnostic purposes only and is supported only with the R2
    engine.
    
    Returns:
      In offline mode: The sequence of internal block increments for output, for the entire audio
      data, provided the stretch profile has been calculated.
      
      In realtime mode: Any output increments that have accumulated since the last call to
      `get_output_increment()`, to a limit of 16.
    '''

  def get_phase_reset_curve(self) -> list[float]:
    '''This function is provided for diagnostic purposes only and is supported only with the R2
    engine.
    
    Returns:
      In offline mode: The sequence of internal phase reset detection function values, for the
      entire audio data, provided the stretch profile has been calculated.
      
      In realtime mode: Any phase reset points that have accumulated since the last call to
      `get_phase_reset_curve()`, to a limit of 16.
    '''

  def get_preferred_start_pad(self) -> int:
    '''Gets the number of padding samples for the initial `process()` call when in RealTime mode.
 
    In RealTime mode (unlike in Offline mode) the stretcher performs no automatic padding or
    delay/latency compensation at the start of the signal. This permits applications to have their
    own custom requirements, but it also means that by default some samples will be lost or
    attenuated at the start of the output and the correct linear relationship between input and
    output sample counts may be lost.

    Most applications using RealTime mode should solve this by calling
    `get_preferred_start_pad()` and supplying the returned number of (silent) samples at
    the start of their input, before their first "true" `process()` call; and then also calling
    `get_start_delay()` and trimming the returned number of samples from the start of their
    stretcher's output.

    Ensure you have set the time and pitch scale factors to their proper starting values before
    calling `get_preferred_start_pad()` or `get_start_delay()`.

    Returns:
      In RealTime mode:
        The number of padding samples for the initial `process()` call.

      In Offline mode:
        Zero.
    '''

  def get_samples_required(self) -> int:
    '''Ask the stretcher how many audio samples should be provided as input in order to ensure that
    some more output becomes available.

    If your application has no particular constraint on processing block size and you are able to
    provide any block size as input for each cycle, then your normal mode of operation would be to
    loop querying this function; providing that number of samples to `process()`; and reading the
    output using `available()` and `retrieve()`.
    
    See `set_max_process_size()` for a more suitable operating mode for applications that do have
    external block size constraints.
  
    Note that this value is only relevant to `process()`, not to `study()` (to which you may
    pass any number of samples at a time, and from which there is no output).

    Returns:
      The number of audio samples required by the stretcher.
    '''

  def get_start_delay(self) -> int:
    '''Get the output delay of the stretcher.

    This is the number of audio samples that one should discard at the start of the output, after
    padding the start of the input with `get_preferred_start_pad()`, in order to ensure
    that the resulting audio has the expected time alignment with the input.

    Ensure you have set the time and pitch scale factors to their proper starting values before
    calling `get_start_delay()`.

    Returns:
      In RunTime mode:
        The number of audio samples that one should discard at the start of the output
      
      In Offline mode: zero, since padding and delay compensation are handled internally.
    '''

  def is_done(self) -> bool:
    '''Checks whether the stretcher has already processed all the provided data and the resulting
    audio has been retrieved.
    
    Returns:
      `True` if the "final" block has been processed and already retrieved, `False` otherwise.
    '''

  def process(self, audio: np.ndarray, final: bool) -> None:
    '''Provide a block of samples for processing.
    
    See also `get_samples_required()` and `set_max_process_size()`.
    
    Args:
      audio:
        De-interleaved audio data with one float array per channel. Sample values are conventionally
        expected to be in the range -1.0f to +1.0f
      final:
        Is this the last block of input data.
    '''

  def reset(self) -> None:
    '''Reset the stretcher's internal buffers.

    The stretcher should subsequently behave as if it had just been constructed (although retaining
    the current time and pitch ratio).
    '''

  def retrieve(self, samples_num: int) -> np.ndarray:
    '''Obtain some processed output data from the stretcher.
    
    Up to `samples_num` samples will be stored in each of the output arrays (one per channel for
    de-interleaved audio data) pointed to by `output`.
    
    The number of samples available to be retrieved can be queried beforehand with a call to
    `available()`.
    
    Returns:
      An array with the requested number of samples, or less if the requested amount was greater
      than the number of samples currently available (can return an empty array).
    '''

  def set_detector_options(self, options: int) -> None:
    '''Change an `Option.DETECTOR` configuration setting.
    
    This may be called at any time in RealTime mode.
    
    It may not be called in Offline mode (for which the detector option is fixed on construction).
    
    This has no effect when using the R3 engine.

    Args:
      options:
        New `Option.DETECTOR` settings.

    '''

  def set_expected_input_duration(self, samples: int) -> None:
    '''Tell the stretcher exactly how many input samples it will receive.
    
    This is only useful in Offline mode, when it allows the stretcher to ensure that the number of
    output samples is exactly correct
    
    In RealTime mode no such guarantee is possible and this value is ignored.

    Args:
      samples:
        The number of input samples the stretcher will expect to receive.
    '''

  def set_formant_options(self, options: int) -> None:
    '''Change an `Option.FORMANT` configuration setting.

    This may be called at any time in any mode.

    Note that if running multi-threaded in Offline mode, the change may not take effect immediately
    if processing is already under way when this function is called.

    Args:
      options:
        New `Option.FORMANT` settings.
    '''

  def set_frequency_cutoff(self, n: int, f: float) -> None:
    '''Set the value of internal frequency cutoff n to f Hz.

    This function is not for general use and is supported only with the R2 engine.

    Args:
      n: Which frequency cutoff to set.
      f: The frequency cutoff value to set.
    '''

  def set_keyframe_map(self, mapping: dict[int, int]) -> None:
    '''Provide a set of mappings from `before` to `after` sample numbers so as to enforce a
    particular stretch profile.
    
    This function cannot be used in RealTime mode.

    This function may not be called after the first call to `process()`. It should be called after
    the time and pitch ratios have been set; the results of changing the time and pitch ratios after
    calling this function are undefined.
    
    Calling `reset()` will clear this mapping.
    
    The key frame map only affects points within the material; it does not determine the overall
    stretch ratio (that is, the ratio between the output material's duration and the source
    material's duration). You need to provide this ratio separately to `time_ratio`, otherwise the
    results may be truncated or extended in unexpected ways regardless of the extent of the frame
    numbers found in the key frame map.

    Args:
      mapping: Mapping the indices of the audio samples in the source material to the corresponding
      indices in the stretched output file, with a "reasonable" gap between the mapped samples.
    '''

  def set_logging_level(self, level: int) -> None:
    '''Set the level of debug output.
    
    The default is whatever has been set using `set_default_logging_level()`, or 0 if that function
    has not been called.
    
    All output goes to `cerr` unless a custom `Logger` has been provided on construction.
    Because writing to `cerr` is not RT-safe, only debug level 0 is RT-safe in normal use by
    default. Debug levels 0 and 1 use only C-string constants as debug messages, so they are
    RT-safe if your custom logger is RT-safe. Levels 2 and 3 are not guaranteed to be RT-safe in any
    conditions as they may construct messages by allocation.

    Args:
      level:
        The logging level to set. Can be one of the following:

          0: Report errors only.

          1: Report some information on construction and ratio change. Nothing is reported during  
          normal processing unless something changes.

          2: Report a significant amount of information about ongoing stretch calculations during   
          normal processing.

          3: Report a large amount of information and also (in the R2 engine) add audible ticks to  
          the output at phase reset points. This is seldom useful.
    '''

  def set_max_process_size(self, samples: int) -> None:
    '''Tell the stretcher the maximum number of samples that you will ever be passing in to a single
    `process()` call.

    If you don't call this, the stretcher will assume that you are calling `get_samples_required()`
    at each cycle and are never passing more samples than are suggested by that function.

    If your application has some external constraint that means you prefer a fixed block size, then
    your normal mode of operation would be to provide that block size to this function; to loop
    calling `process()` with that size of block; after each call to `process()`, test whether output
    has been generated by calling `available()`; and, if so, call `retrieve()` to obtain it See
    `get_samples_required()` for a more suitable operating mode for applications without such
    external constraints.

    This function may not be called after the first call to `study()` or `process()`.

    Note that this value is only relevant to `process()`, not to `study()`.

    Args:
      samples: The maximum number of samples that will be ever passed in a single `process()` call.
    '''

  def set_phase_options(self, options: int) -> None:
    '''Change an `Option.PHASE` configuration setting This may be called at any time in any mode.
    
    This has no effect when using the R3 engine.

    Note that if running multi-threaded in Offline mode, the change may not take effect immediately
    if processing is already under way when this function is called.

    Args:
      options:
        New `Option.PHASE` settings.
    '''

  def set_pitch_options(self, options: int) -> None:
    '''Change an `Option.PITCH` configuration setting.
    
    This may be called at any time in RealTime mode.

    It may not be called in Offline mode (for which the pitch option is fixed on construction).
    
    This has no effect when using the R3 engine.

    Args:
      options:
        New `Option.PITCH` settings.
    '''

  def set_transients_options(self, options: int) -> None:
    '''Change an `Option.TRANSIENTS` configuration setting.
    
    This may be called at any time in RealTime mode.
    
    It may not be called in Offline mode (for which the transients option is fixed on construction).
    
    This has no effect when using the R3 engine.

    Args:
      options:
        New `Option.TRANSIENTS` settings.
    '''

  def study(self, audio: np.ndarray, final: bool) -> None:
    '''Provide a block of `samples` samples for the stretcher to study and calculate a stretch
    profile from.

    This is only meaningful in Offline mode, and is required if running in that mode.

    You should pass the entire input through `study()` before any `process()` calls are
    made, as a sequence of blocks in individual `study()` calls, or as a single large block.

    Args:
      audio:
        De-interleaved audio data with one float array per channel. Sample values are conventionally
        expected to be in the range -1.0f to +1.0f
      final:
        Is this the last block of input data.
    '''


def create_audio_array(channels_num: int, samples_num: int, init_value: float = 0.0) -> np.ndarray:
  '''Creates an array for audio with `channels_num` channels and `samples_num` samples.

  Args:
    channels_num:
      Number of channels that the audio will have.
    samples_num:
      Number of samples that the audio will have.
    init_value:
      Value that assigned to every element of the array. 

  Returns:
    Numpy ndarray with pylibrb-compatible shape and dtype.
  '''


def set_default_logging_level(level: int) -> None:
  '''Set the default level of debug output for subsequently constructed stretchers.
    
  Args:
    level:
      The logging level to set. Can be one of the following:

        0: Report errors only.

        1: Report some information on construction and ratio change. Nothing is reported during  
        normal processing unless something changes.

        2: Report a significant amount of information about ongoing stretch calculations during   
        normal processing.

        3: Report a large amount of information and also (in the R2 engine) add audible ticks to  
        the output at phase reset points. This is seldom useful.
  '''
