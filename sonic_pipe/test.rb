load "/Users/bubo/ziffers/ziffers.rb"
link
set_link_bpm! 120
use_midi_defaults port: "cable-loop-midi_5"

set_volume! 0.5

live_loop :a do
  use_synth :bass_foundation
  play (ring 60,64,67,[60,72]).tick(:babp)
  sleep (ring 0.25, 0.25).tick(:a)
end


live_loop :b, sync: :a do
  use_synth :bass_foundation
  play (ring :f5, :e5, :a5).tick(:bipa)
  sleep (ring 0.25, 0.25).tick(:a)
end

stop

help_midi
