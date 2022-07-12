# Ableton Link

* link

```ruby
use_bpm 120 # bpm is at 120
link # wait for the start of the next bar before continuing
     # (where each bar has 4 beats)
puts current_bpm #=> :link (not 120)
```

* link_sync

Similar to link except it also waits for the link session to be playing. If it is, then it behaves identially to link. If the session is not playing, then link_sync will first wait until the session has started before then continuing as if just link had been called. 

* set_link_bpm!  

Set the tempo for the link metronome in BPM. This is ‘global’ in that the BPM of all threads/live_loops in Link BPM mode will be affected. Note that this will also change the tempo of all link metronomes connected to the local network. Also note that the current thread does not have to be in Link BPM mode for this function to affect the Link clock’s BPM. 

```ruby
use_bpm :link                                
set_link_bpm! 30                             

8.times do
  bpm += 10
  set_link_bpm! bpm                          
  sample :loop_amen, beat_stretch: 2
  sleep 2
end
```