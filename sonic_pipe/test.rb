load "/Users/bubo/ziffers/ziffers.rb"

live_loop :b do
  use_synth :saw
  zplay "0.25 0 1 2 4 5 9", amp: 0.25
  zplay "0.25 2 4 4 8 9 12", amp: 0.25
  zplay "0.25 0 1 2 4 5 0^248", amp: 0.25
  zplay "0.25 2 4 4 8 9 02^59", amp: 0.25
end

live_loop :d, sync: :b do
  sample :drum_bass_hard
  sleep 0.5
end

live_loop :e, sync: :b do
  sample :drum_cymbal_closed
  sleep 0.125
  sample :drum_cymbal_closed
  sleep 0.125
  sample :drum_cymbal_closed
  sleep 0.25
  sample :drum_cymbal_closed
  sleep 0.25
end

exit
