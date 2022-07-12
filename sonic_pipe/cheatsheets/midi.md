# MIDI

* midi 
    * **sustain:** Duration of note event in beats 
    * **vel:** Velocity of note as a MIDI number 
    * **on:** If specified and false/nil/0 will stop the midi on/off messages from being sent out. (Ensures all opts are evaluated in this call to midi regardless of value). 

* midi_all_notes_off 
    * **channel:** Channel to send the all notes off message to 
    * **port:** MIDI port to send to 
    * **on:** If specified and false/nil/0 will stop the midi all notes off message from being sent out. (Ensures all opts are evaluated in this call to midi_all_notes_off regardless of value). 

* midi_cc 
    * **channel:** Channel(s) to send to 
    * **port:** MIDI port(s) to send to 
    * **value:** Control value as a MIDI number. 
    * **val_f:** Control value as a value between 0 and 1 (will be converted to a MIDI value) 
    * **on:** If specified and false/nil/0 will stop the midi cc message from being sent out. (Ensures all opts are evaluated in this call to midi_cc regardless of value). 

* midi_channel_pressure  

    * **channel:** Channel(s) to send to 
    * **port:** MIDI port(s) to send to 
    * **value:** Pressure value as a MIDI number. 
    * **val_f:** Pressure value as a value between 0 and 1 (will be converted to a MIDI value) 
    * **on:** If specified and false/nil/0 will stop the midi channel pressure message from being sent out. (Ensures all opts are evaluated in this call to midi_channel_pressure regardless of value). 

* midi_clock_beat
    * Sends enough MIDI clock ticks for one beat to all connected MIDI devices. Use the port: opt to restrict which MIDI ports are used. 

* midi_clock_tick
    * Sends a MIDI clock tick message to all connected devices on all channels. Use the port: and channel: opts to restrict which MIDI ports and channels are used. 

* midi_continue
    * Sends the MIDI continue system message to all connected MIDI devices on all ports. Use the port: opt to restrict which MIDI ports are used. 
* midi_local_control_off
* midi_local_control_on
* midi_mode  mode
* midi_note_off
* midi_note_on
* midi_notes
* midi_pc
    * Sends a MIDI program change message to all connected devices on all channels. Use the port: and channel: opts to restrict which MIDI ports and channels are used. 
* midi_pitch_bend 
* midi_poly_pressure
* midi_raw
* midi_reset
* midi_sound_off
* midi_start
* midi_stop