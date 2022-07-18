* :dull_bell

A simple dull discordant bell sound. 

```
note amp pan attack decay sustain release
attack_level decay_level sustain_level
env_curve
```

* :chipbass

A 16 step triangle wave modelled after the 2A03 chip found in voice 3 of the NES games console. This can be used for retro sounding basslines. For complete authenticity with the 2A03 bear in mind that the triangle channel on that chip didn’t have a volume control. 

```
note note_resolution amp pan attack decay sustain
release attack_level decay_level sustain_level env_curve
```

* :chiplead 

A slightly clipped square (pulse) wave with phases of 12.5%, 25% or 50% modelled after the 2A03 chip found in voices 1 and 2 of the NES games console. This can be used for retro sounding leads and harmonised lines. This also adds an opt ‘note_resolution’ which locks the note slide to certain pitches which are multiples of the step size. This allows for emulation of the sweep setting on the 2A03. 

```
note note_resolution amp pan attack decay sustain release
attack_level decay_level sustain_level env_curve width
```

* :chipnoise

Generates noise whose values are either -1 or 1 (like a pulse or square wave) with one of 16 particular frequencies. This is similar to the noise channel on the 2A03 chip used in the NES games console, although it lacks the same Pseudo-Random Number Generator (PRNG) and doesn’t implement the 2A03’s lesser used noise mode. The amplitude envelope defaults to moving by step to keep that 16 bit feel and this synth also has a slight soft clipping to better imitate the original sound of the device. Use for retro effects, hand claps, snare drums and hi-hats. 

```
amp pan attack decay sustain release attack_level decay_level sustain_level env_curve freq_band
```

* :pretty_bell

A pretty bell sound. Works well with short attacks and long decays. 

```
note amp pan attack decay sustain release 
attack_level decay_level sustain_level env_curve
```

* :beep

A simple pure sine wave. The sine wave is the simplest, purest sound there is and is the fundamental building block of all noise. The mathematician Fourier demonstrated that any sound could be built out of a number of sine waves (the more complex the sound, the more sine waves needed). Have a play combining a number of sine waves to design your own sounds! 

```
note amp pan attack decay sustain release 
attack_level decay_level sustain_level env_curve
```

* :sine

A simple pure sine wave. The sine wave is the simplest, purest sound there is and is the fundamental building block of all noise. The mathematician Fourier demonstrated that any sound could be built out of a number of sine waves (the more complex the sound, the more sine waves needed). Have a play combining a number of sine waves to design your own sounds! 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve
```

* :saw

A saw wave with a low pass filter. Great for using with FX such as the built in low pass filter (available via the cutoff arg) due to the complexity and thickness of the sound. 

```
note amp pan attack decay sustain release 
attack_level decay_level sustain_level env_curve
cutoff
```

* :pulse

A simple pulse wave with a low pass filter. This defaults to a square wave, but the timbre can be changed dramatically by adjusting the pulse_width arg between 0 and 1. The pulse wave is thick and heavy with lower notes and is a great ingredient for bass sounds. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff pulse_width
```

* :rodeo

Classic 70’s electric piano sound, with built-in compressor and chorus. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level use_chords use_compressor
cutoff
```

* :subpulse

A pulse wave with a sub sine wave passed through a low pass filter. The pulse wave is thick and heavy with lower notes and is a great ingredient for bass sounds - especially with the sub wave. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff pulse_width
sub_amp sub_detune
```

* :square

A simple square wave with a low pass filter. The square wave is thick and heavy with lower notes and is a great ingredient for bass sounds. If you wish to modulate the width of the square wave see the synth pulse. 

```
note amp pan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff
```

* :tri

A simple triangle wave with a low pass filter. 


```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff pulse_width
```


* :dsaw

A pair of detuned saw waves passed through a low pass filter. Two saw waves with slightly different frequencies generates a nice thick sound which is the basis for a lot of famous synth sounds. Thicken the sound by increasing the detune value, or create an octave-playing synth by choosing a detune of 12 (12 MIDI notes is an octave). 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level cutoff detune
```

* :dpulse

A pair of detuned pulse waves passed through a low pass filter. Two pulse waves with slightly different frequencies generates a nice thick sound which can be used as a basis for some nice bass sounds. Thicken the sound by increasing the detune value, or create an octave-playing synth by choosing a detune of 12 (12 MIDI notes is an octave). Each pulse wave can also have individual widths (although the default is for the detuned pulse to mirror the width of the main pulse). 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff detune pulse_width dpulse_width 
```

* :dtri

A pair of detuned triangle waves passed through a low pass filter. Two pulse waves with slightly different frequencies generates a nice thick sound which can be used as a basis for some nice bass sounds. Thicken the sound by increasing the detune value, or create an octave-playing synth by choosing a detune of 12 (12 MIDI notes is an octave). 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff detune
```

* :fm

A sine wave with a fundamental frequency which is modulated at audio rate by another sine wave with a specific modulation, division and depth. Useful for generating a wide range of sounds by playing with the divisor and depth params. Great for deep powerful bass and fun 70s sci-fi sounds. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff divisor depth
```

* :mod_fm

The FM synth modulating between two notes - the duration of the modulation can be modified using the mod_phase arg, the range (number of notes jumped between) by the mod_range arg and the width of the jumps by the mod_width param. The FM synth is a sine wave with a fundamental frequency which is modulated at audio rate by another sine wave with a specific modulation, division and depth. Useful for generating a wide range of sounds by playing with the :divisor and :depth params. Great for deep powerful bass and fun 70s sci-fi sounds. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff divisor depth mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave
```



* :mod_saw

A saw wave passed through a low pass filter which modulates between two separate notes via a variety of control waves. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave
```

* :mod_dsaw

A pair of detuned saw waves (see the dsaw synth) which are modulated between two fixed notes at a given rate. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave detune
```

* :mod_sine

A sine wave passed through a low pass filter which modulates between two separate notes via a variety of control waves. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave 
```

* :mod_beep

A sine wave passed through a low pass filter which modulates between two separate notes via a variety of control waves. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave 
```

* :mod_tri

A triangle wave passed through a low pass filter which modulates between two separate notes via a variety of control waves. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave 
```

* :mod_pulse

A pulse wave with a low pass filter modulating between two notes via a variety of control waves (see mod_wave: arg). The pulse wave defaults to a square wave, but the timbre can be changed dramatically by adjusting the pulse_width arg between 0 and 1. 

```
note amp ppan attack decay sustain release
attack_level decay_level sustain_level env_curve
cutoff mod_phase mod_range 
mod_pulse_width mod_phase_offset mod_invert_wave
mod_wave pulse_width
```

* :tb303 

Emulation of the classic Roland TB-303 Bass Line synthesiser. Overdrive the res (i.e. use very large values) for that classic late 80s acid sound. 

```
note amp pan decay sustain release decay_level
sustain_level env_curve cutoff_min cutoff_attack
cutoff_decay cutoff_release cutoff_attack_level
cutoff_decay_level res wave pulse_width
```

* :tech_saws

Slightly modified supersaw implementation based on http://sccode.org/1-4YS 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff
```

* :supersaw

Thick swirly saw waves sparkling and moving about to create a rich trancy sound. 


```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res
```

* :hoover 

Classic early 90’s rave synth - ‘a sort of slurry chorussy synth line like the classic Dominator by Human Resource’. Based on Dan Stowell’s implementation in SuperCollider and Daniel Turczanski’s port to Overtone. Works really well with portamento (see docs for the ‘control’ method). 


```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res
```

* kalimba

A synthesised kalimba (a type of African thumb piano). Note that due to the plucked nature of this synth the envelope opts such as attack:, sustain: and release: do not work as expected. They can only shorten the natural length of the note, not prolong it. Note the default envelope is longer than usual - sustain: 4 and release: 1 

```
note amp pan attack decay sustain release attack_level decay_level sustain_level clickiness
```


* :prophet

Dark and swirly, this synth uses Pulse Width Modulation (PWM) to create a timbre which continually moves around. This effect is created using the pulse ugen which produces a variable width square wave. We then control the width of the pulses using a variety of LFOs - sin-osc and lf-tri in this case. We use a number of these LFO modulated pulse ugens with varying LFO type and rate (and phase in some cases) to provide the LFO with a different starting point. We then mix all these pulses together to create a thick sound and then feed it through a resonant low pass filter (rlpf). For extra bass, one of the pulses is an octave lower (half the frequency) and its LFO has a little bit of randomisation thrown into its frequency component for that extra bit of variety. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res
```

* :zawa

Saw wave with oscillating timbre. Produces moving saw waves with a unique character controllable with the control oscillator (usage similar to mod synths). 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level cutoff res phase phase_offset
wave invert_wave range disable_wave pulse_width
```

* :dark_ambience

A slow rolling bass with a sparkle of light trying to escape the darkness. Great for an ambient sound. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res detune1
detune2 noise ring room reverb_time
```

* :growl

A deep rumbling growl with a bright sine shining through at higher notes. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res
```

* :hollow

A hollow breathy sound constructed from random noise 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res noise 
norm
```

* :blade

Straight from the 70s, evoking the mists of Blade Runner, this simple electro-style string synth is based on filtered saw waves and a variable vibrato. 

```
note amp pan attack decay sustain release 
attack_level decay_level sustain_level env_curve
vibrato_rate vibrato_depth vibrato_delay
```

* :piano

A basic piano synthesiser. Note that due to the plucked nature of this synth the envelope opts such as attack:, sustain: and release: do not work as expected. They can only shorten the natural length of the note, not prolong it. 

```
note amp pan vel attack decay sustain release
attack_level decay_level sustain_level hard
stereo_width
```

* :pluck

A basic plucked string synthesiser that uses Karplus-Strong synthesis. Note that due to the plucked nature of this synth the envelope opts such as attack:, sustain: and release: do not work as expected. They can only shorten the natural length of the note, not prolong it. Also, the note: opt will only honour whole tones. 


```
note ampp an attack sustain release attack_level decay
decay_level sustain_level noise_amp max_delay_time 
pluck_decay coef
```

* :sound_in / :sound_in_stereo

Treat sound card input as a synth. If your audio card has inputs, you may use this synth to feed the incoming audio into Sonic Pi. This synth will read in a single mono audio stream - for example from a standard microphone or guitar. See :sound_in_stereo for a similar synth capable of reading in a stereo signal. 

```
amp pan attack decay sustain release attack_level 
sustain_level env_curve input
```

* :noise

Noise that contains equal amounts of energy at every frequency - comparable to radio static. Useful for generating percussive sounds such as snares and hand claps. Also useful for simulating wind or sea effects. 

```
amp pan attack decay sustain release attack_level 
decay_level sustain_level env_curve cutoff res
```

* :pnoise

Noise whose spectrum falls off in power by 3 dB per octave. Useful for generating percussive sounds such as snares and hand claps. Also useful for simulating wind or sea effects. 

```
amp pan attack decay sustain release attack_level
decay_level sustain_level env_curve cutoff res
```

* :bnoise

Noise whose spectrum falls off in power by 6 dB per octave. Useful for generating percussive sounds such as snares and hand claps. Also useful for simulating wind or sea effects. 

```
amp pan attack decay sustain release attack_level 
decay_level sustain_level env_curve cutoff res
```

* :gnoise

Generates noise which results from flipping random bits in a word. The spectrum is emphasised towards lower frequencies. Useful for generating percussive sounds such as snares and hand claps. Also useful for simulating wind or sea effects. 

```
amp pan attack decay sustain release attack_level decay_level susatin_level env_curve cutoff res
```

* :cnoise

Generates noise whose values are either -1 or 1. This produces the maximum energy for the least peak to peak amplitude. Useful for generating percussive sounds such as snares and hand claps. Also useful for simulating wind or sea effects. 

```
amp pan attack decay sustain release attack_level decay_level sustain_level env_curve cutoff res
```

* :winwood_lead 

A lead synth inspired by the Winwood songs from the early 80s. Adapted for Sonic Pi from Steal This Sound. 

```
note amp pan attack decay sustain release attack_level
decay_level sustain_level cutoff res lfo_width, lfo_rate
ramp_ratio ramp_length seed
```

* :bass_foundation 

A soft bass synth inspired by the sounds of the 80s. Use together with :bass_highend if you want to give it a gargling component. Adapted for Sonic Pi from Steal This Sound. 

```
note amp pan attack decay sustain release
attack_level decay_level sustain_level cutoff
res
```

* :bass_highend

An addition to the :bass_foundation synth inspired by the sounds of the 80s. Use them together if you want to give it a rough, slurping, or gargling component. Adapted for Sonic Pi from Steal This Sound. 

```
note amp pan attack decay sustain release
attack_level decay_level sustain_level cutoff
res drive
```
