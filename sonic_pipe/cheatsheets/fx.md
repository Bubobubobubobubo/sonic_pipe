* :Autotuner 

Autotune/phase vocoder effect. Used without any arguments, it tries to detect the pitch and shift it to the nearest exact note. This can help with out of tune singing, but it’s also an interesting effect in its own right. When used with the note: arg, it tries to shift the input to match that note instead. This gives that classic “robot singing” sound that people associate with vocoders. This can then be changed using the control method to create new melodies. 

```
amp: 1 mix: 1 pre_mix: note: 0 formant_ratio: 1.0
```

* :Band Eq

Attenuate or Boost a frequency band.

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 freq: 100 res: 0.6 db: 0.6
```

* :Bitcrusher

Creates lo-fi output by decimating and deconstructing the incoming audio by lowering both the sample rate and bit depth. The default sample rate for CD audio is 44100, so use values less than that for that crunchy chip-tune sound full of artefacts and bitty distortion. Similarly, the default bit depth for CD audio is 16, so use values less than that for lo-fi sound. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 sample_rate: 10000 bits: 8 cutoff: 0
```

* :BPF

Combines low pass and high pass filters to only allow a ‘band’ of frequencies through. If the band is very narrow (a low res value like 0.0001) then the BPF will reduce the original sound, almost down to a single frequency (controlled by the centre opt). With higher values for res we can simulate other filters e.g. telephone lines, by cutting off low and high frequencies. Use FX `:band_eq` with a negative db for the opposite effect - to attenuate a given band of frequencies. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 centre: 100 res: 0.6
```

* :Compressor

Compresses the dynamic range of the incoming signal. Equivalent to automatically turning the amp down when the signal gets too loud and then back up again when it’s quiet. Useful for ensuring the containing signal doesn’t overwhelm other aspects of the sound. Also a general purpose hard-knee dynamic range processor which can be tuned via the opts to both expand and compress the signal. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 threshold: 0.2 clamp_time: 0.01 
slope_above: 0.5 slope_below: 1 relax_time: 0.01
```

* :Distortion

Distorts the signal reducing clarity in favour of raw crunchy noise. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 distort: 0.5
```

* :Echo

Standard echo with variable phase duration (time between echoes) and decay (length of echo fade out). If you wish to have a phase duration longer than 2s, you need to specify the longest phase duration you’d like with the arg max_phase. Be warned, echo FX with very long phases can consume a lot of memory and take longer to initialise. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 0.25 decay: 2 max_phase: 2
```


* :Eq

Basic parametric EQ.

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 low_shelf: 0 low_shelf_note: 43.349957 low_shelf_slope: 1 low: 0 low_note: 59.2130948 low_q: 0.6 mid: 0 mid_note: 83.2130948 mid_q: 0.6 high: 0 high_note: 104.9013539 high_q: 0.6 high_shelf: 0 high_shelf_note: 114.2326448 high_shelf_slope: 1
```

* :Flanger

Mix the incoming signal with a copy of itself which has a rate modulating faster and slower than the original. Creates a swirling/whooshing effect. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 4 phase_offset: 0 wave: 4 invert_wave: 0 stereo_invert_wave: 0 delay: 5 max_delay: 20 depth: 5 decay: 2 feedback: 0 invert_flange: 0
```

* :Gverb

Make the incoming signal sound more spacious or distant as if it were played in a large room or cave. Similar to reverb but with a more spacious feel. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 spread: 0.5 damp: 0.5 pre_damp: 0.5 dry: 1 room: 10 release: 3 ref_level: 0.7 tail_level: 0.5
```

* :HPF

Dampens the parts of the signal that are lower than the cutoff point (typically the bass of the sound) and keeps the higher parts (typically the crunchy fizzy harmonic overtones). Choose a lower cutoff to keep more of the bass/mid and a higher cutoff to make the sound more light and crispy. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100
```

* :Ixi Techno

Moving resonant low pass filter between min and max cutoffs. Great for sweeping effects across long synths or samples. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 4 phase_offset: 0 cutoff_min: 60 cutoff_max: 120 res: 0.8
```

* :Krush

Krush that sound! 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: gain: 5 cutoff: 100 res: 0
```

* :Level

Amplitude modifier. All FX have their own amp built in, so it may be the case that you don’t specifically need an isolated amp FX. However, it is useful to be able to control the overall amplitude of a number of running synths. All sounds created in the FX block will have their amplitudes multipled by the amp level of this FX. For example, use an amp of 0 to silence all internal synths. 

```ruby
amp: 1
```

* :LPF

Dampens the parts of the signal that are higher than the cutoff point (typically the crunchy fizzy harmonic overtones) and keeps the lower parts (typically the bass/mid of the sound). Choose a higher cutoff to keep more of the high frequencies/treble of the sound and a lower cutoff to make the sound more dull and only keep the bass. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100
```

* :Mono

Sum left and right channels. Useful with stereo samples that you need as a mono sound, or for use with panslicer. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 pan: 0
```

* :NBPF

Like the Band Pass Filter but normalised. The normaliser is useful here as some volume is lost when filtering the original signal. 


```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 centre: 100 res: 0.6
```

* :NHPF

A high pass filter chained to a normaliser. Ensures that the signal is both filtered by a standard high pass filter and then normalised to ensure the amplitude of the final output is constant. A high pass filter will reduce the amplitude of the resulting signal (as some of the sound has been filtered out) the normaliser can compensate for this loss (although will also have the side effect of flattening all dynamics). See doc for hpf. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100
```

* :NLPF

A low pass filter chained to a normaliser. Ensures that the signal is both filtered by a standard low pass filter and then normalised to ensure the amplitude of the final output is constant. A low pass filter will reduce the amplitude of the resulting signal (as some of the sound has been filtered out) the normaliser can compensate for this loss (although will also have the side effect of flattening all dynamics). See doc for lpf. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100
```

* :Normaliser

Raise or lower amplitude of sound to a specified level. Evens out the amplitude of incoming sound across the frequency spectrum by flattening all dynamics. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 level: 1
```

* :NRBPF

Like the Band Pass Filter but normalised, with a resonance (slight volume boost) around the target frequency. This can produce an interesting whistling effect, especially when used with larger values for the res opt.  The normaliser is useful here as some volume is lost when filtering the original signal. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 centre: 100 res: 0.5
```

* :NRHPF

Dampens the parts of the signal that are lower than the cutoff point (typically the bass of the sound) and keeps the higher parts (typically the crunchy fizzy harmonic overtones). The resonant part of the resonant high pass filter emphasises/resonates the frequencies around the cutoff point. The amount of emphasis is controlled by the res opt with a higher res resulting in greater resonance. High amounts of resonance (rq ~1) can create a whistling sound around the cutoff frequency.  Choose a lower cutoff to keep more of the bass/mid and a higher cutoff to make the sound more light and crispy. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100 res: 0.5
```

* :NRLPF


Dampens the parts of the signal that are higher than the cutoff point (typically the crunchy fizzy harmonic overtones) and keeps the lower parts (typically the bass/mid of the sound). The resonant part of the resonant low pass filter emphasises/resonates the frequencies around the cutoff point. The amount of emphasis is controlled by the res opt with a higher res resulting in greater resonance. High amounts of resonance (rq ~1) can create a whistling sound around the cutoff frequency. 
Choose a higher cutoff to keep more of the high frequencies/treble of the sound and a lower cutoff to make the sound more dull and only keep the bass. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100 res: 0.5
```

* :Octaver

This effect adds three pitches based on the input sound. The first is the original sound transposed up an octave (super_amp), the second is the original sound transposed down an octave (sub_amp) and the third is the original sound transposed down two octaves (subsub_amp). The way the transpositions are done adds some distortion/fuzz, particularly to the lower octaves, whilst the upper octave has a ‘cheap’ quality. This effect is often used in guitar effects pedals but it can work with other sounds too. There’s a great description of the science behind this on [Wikipedia](https://en.wikipedia.org/wiki/Octave_effect).

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: super_amp: 1 sub_amp: 1 subsub_amp: 1
```

* :Pan

Specify where in the stereo field the sound should be heard. A value of -1 for pan will put the sound in the left speaker, a value of 1 will put the sound in the right speaker and values in between will shift the sound accordingly. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 pan: 0
```

* :Panslicer

Slice the pan automatically from left to right. Behaves similarly to slicer and wobble FX but modifies stereo panning of sound in left and right speakers. Default slice wave form is square (hard slicing between left and right) however other wave forms can be set with the wave: opt. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 0.25 amp_min: 0 amp_max: 1 pulse_width: 0.5 phase_offset: 0 wave: 1 invert_wave: 0 probability: 0 prob_pos: 0 seed: 0 smooth: 0 smooth_up: 0 smooth_down: 0 pan_min: -1 pan_max: 1
```

* :Ping Pong

Echo FX with each delayed echo swapping between left and right channels. Has variable phase duration (time between echoes) and feedback (proportion of sound fed into each echo). If you wish to have a phase duration longer than 1s, you need to specify the longest phase duration you’d like with the arg max_phase. Be warned, :ping_pong FX with very long phases can consume a lot of memory and take longer to initialise. Also, large values for feedback will cause the echo to last for a very long time.  Note: sliding the phase: opt with phase_slide: will also cause each echo during the slide to change in pitch, in much the same way that a sample’s pitch changes when altering its rate. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 0.25 feedback: 0.5 max_phase: 1 pan_start: 1
```

* :Pitch Shift

Changes the pitch of a signal without affecting tempo. Does this mainly through the pitch parameter which takes a midi number to transpose by. You can also play with the other params to produce some interesting textures and sounds. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 window_size: 0.2 pitch: 0 pitch_dis: 0.0 time_dis: 0.0
```

* :RBPF

Like the Band Pass Filter but with a resonance (slight volume boost) around the target frequency. This can produce an interesting whistling effect, especially when used with larger values for the res opt. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 centre: 100 res: 0.5
```

* :Record

Recorder! 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 buffer:
```

* :Reverb

Make the incoming signal sound more spacious or distant as if it were played in a large room or cave. Signal may also be dampened by reducing the amplitude of the higher frequencies. 

```ruby
amp: 1 mix: 0.4 pre_mix: 1 pre_amp: 1 room: 0.6 damp: 0.5
```

* :RHPF

Dampens the parts of the signal that are lower than the cutoff point (typically the bass of the sound) and keeps the higher parts (typically the crunchy fizzy harmonic overtones). The resonant part of the resonant high pass filter emphasises/resonates the frequencies around the cutoff point. The amount of emphasis is controlled by the res opt with a higher res resulting in greater resonance. High amounts of resonance (rq ~1) can create a whistling sound around the cutoff frequency. 
Choose a lower cutoff to keep more of the bass/mid and a higher cutoff to make the sound more light and crispy. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100 res: 0.5
```

* :Ring Mod

Attack of the Daleks! Ring mod is a classic effect often used on soundtracks to evoke robots or aliens as it sounds hollow or metallic. We take a ‘carrier’ signal (a sine wave controlled by the freq opt) and modulate its amplitude using the signal given inside the fx block. This produces a wide variety of sounds - the best way to learn is to experiment! 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 freq: 30 mod_amp: 1
```

* :RLPF

Dampens the parts of the signal that are higher than the cutoff point (typically the crunchy fizzy harmonic overtones) and keeps the lower parts (typically the bass/mid of the sound). The resonant part of the resonant low pass filter emphasises/resonates the frequencies around the cutoff point. The amount of emphasis is controlled by the res opt with a higher res resulting in greater resonance. High amounts of resonance (rq ~1) can create a whistling sound around the cutoff frequency.  Choose a higher cutoff to keep more of the high frequencies/treble of the sound and a lower cutoff to make the sound more dull and only keep the bass. 

```ruby
 amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 cutoff: 100 res: 0.5 
```

* :Slicer

Modulates the amplitude of the input signal with a specific control wave and phase duration. With the default pulse wave, slices the signal in and out, with the triangle wave, fades the signal in and out and with the saw wave, phases the signal in and then dramatically out. Control wave may be inverted with the arg invert_wave for more variety. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 0.25 amp_min: 0 amp_max: 1 pulse_width: 0.5 phase_offset: 0 wave: 1 invert_wave: 0 probability: 0 prob_pos: 0 seed: 0 smooth: 0 smooth_up: 0 smooth_down: 0
```

* :Sound Out

Outputs a mono signal to a soundcard output of your choice. By default will mix the incoming stereo signal (generated within the FX block) into a single mono channel. However, with the mode: opt, it is possible to alternatively send either the incoming left or right channel out directly. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 output: 1 mode: 0
```

* :Sound Out Stereo

Outputs a two-channel stereo signal to two consecutive soundcard outputs of your choice. By default will route the left and right channels of the incoming stereo signal (generated within the FX block) into separate left and right output channels. However, with the mode: opt, it is possible to alternatively cross over the channels or mix the incoming stereo channels into a single mono output and duplicate that on both left and right output channels. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 output: 1 mode: 0
```

* :Tanh

Forces all audio through a hyperbolic tangent function which has the effect of acting like distorted limiter. It works by folding loud signals back in on itself. The louder the input signal, the more folding occurs - resulting in increased strange harmonics and distortion. This folding also has the effect of limiting the outgoing signal, therefore to increase the output amplitude use the amp: opt and to increase the folding/distortion use the pre_amp: opt. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 krunch: 5
```

* :Tremolo

Modulate the volume of the sound. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 4 phase_offset: 0 wave: 2 invert_wave: 0 depth: 0.5
```

* :Vowel

This effect filters the input to match a human voice singing a certain vowel sound. Human singing voice sounds are easily achieved with a source of a saw wave with a little vibrato. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 vowel_sound: 1 voice: 0
```

* :Whammy

A cheap sounding transposition effect, with a slightly robotic edge. Good for adding alien sounds and harmonies to everything from beeps to guitar samples. It’s similar to pitch shift although not as smooth sounding. 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 transpose: 12 max_delay_time: 1 deltime: 0.05 grainsize: 0.075
```

* :Wobble

Versatile wobble FX. Will repeatedly modulate a range of filters (rlpf, rhpf) between two cutoff values using a range of control wave forms (saw, pulse, tri, sine). You may alter the phase duration of the wobble, and the resonance of the filter. Combines well with the dsaw synth for fun dub wobbles. Cutoff value is at cutoff_min at the start of phase 

```ruby
amp: 1 mix: 1 pre_mix: 1 pre_amp: 1 phase: 0.5 cutoff_min: 60 cutoff_max: 120 res: 0.8 phase_offset: 0 wave: 0 invert_wave: 0 pulse_width: 0.5 filter: 0 probability: 0 prob_pos: 0 seed: 0 smooth: 0 smooth_up: 0 smooth_down: 0
```