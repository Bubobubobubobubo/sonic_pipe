live_loop :b do
  play 60, amp: 0.25
  play 64, amp: 0.25
  play 67, amp: 0.25
  sleep 0.25
end

play 60, amp: 0.25

stop

exit

debug
