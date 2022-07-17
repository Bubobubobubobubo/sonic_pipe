load "/Users/bubo/ziffers/ziffers.rb"

z1 "q 0", port: "hermod", channel: 1, scale: :chromatic,
  key: :d, rhythm: "qee qee"

z2 "0.25 0 3 7 T", port: "hermod", channel: 2, scale: :chromatic, key: :d,
  rhythm: "qee qeee"

z3 "0.25 _ 0 3 7 T", port: "hermod", channel: 3, scale: :chromatic, key: :d,
  rhythm: "wqee qee"

z4 "0.25 _ 0 3 7 T", port: "hermod", channel: [4, 5], scale: :chromatic, key: :d,
  rhythm: "ee qq ee qee"

z1 "0 0 [0 50] 0", port: "hermod", rhythm: "qee qq ee ", channel: [6, 7]

z2 "0 ^ 0 ^ 0^0 ", port: "hermod", rhythm: "qee qq ee ", channel: [6, 7]
