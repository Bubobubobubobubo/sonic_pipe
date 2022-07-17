# Ziffers: numbered musical notation

## Pitches

Ziffers is a numbered musical notation and live code golfing language. Melodies are written using numbers 0-9 or characters 'T' 'E' which can be used in chromatic scale (T=10, E=11).

```ruby
# numbers
-2 -1 0 1 2 T E

# Play the chromatic scale:
zplay "0 1 2 3 4 5 6 7 8 9 T E", scale: :chromatic

# Play in D Minor:
zplay "0 023 3 468", key: :d, scale: :minor

```

## Scales

Ziffers supports all the scales defined in Sonic Pi.Custom scales are also supported (via nasty monkeypatch). Scale is generated from the array of integers or floats represeting the steps in the scale.

```ruby
zplay "q 0 1 2 3"
zplay "q 0 1 2 3", scale: :minor # Scale from the Sonic pi
zplay "q 0 1 2 3", scale: :jiao # Another one
zplay "q 0 1 2 3", scale: [1,2,1.234,2] # Custom scale via monkeypatch
```


## Note lengths

Default note length is a whole note w, meaning 1 beat of sleep after the note is played. Note lengths can be changed with characters, list notation or Z notation.

Most common note length are:

* w = Whole (Semibreve)
* h = Half (Minim)
* q = Quarter (Crotchet)
* e = Eight (Quaver)
* s = Sixteenth (Semiquaver)

Note lengths can be defined for all following notes or for single notes by grouping the note lenght characters. For example note lengths in Blue bird song can be defined using characters q (Quarter notes) for most of the notes and w (Whole notes) by grouping the character with the specific note integer:

```ruby
zplay "|q 4 2 4 2 |q 4 5 4 2 |q 3 1 3 1 |q 3 4 3 1 |q 4 2 4 2 |q 4 5 4 2 | w4 |q 4 3 2 1 | w0 |"
```

* **m** = Max = 15360 ticks = 8 beat
* **k** = Max triplet = 10240 ticks = 5,333 beat
* **l** = Long = 7680 ticks = 4 beats
* **p** = Long triplet = 5120 ticks = 2,666 beat
* **d** = Double whole = 3840 ticks = 2 beat
* **c** = Double whole triplet = 2560 ticks = 1,333 beat
* **w** = Whole = 1920 ticks = 1 beat
* **y** = Whole triplet = 1280 = 0,666 beat
* **h** = Half = 960 ticks = 0.5 beat
* **n** = Half triplet = 640 ticks = 0.333 beats
* **q** = Quarter = 480 ticks = 0.25 beat
* **a** = Quarter triplet = 320 ticks = 0,1666 beat
* **e** = Eighth = 240 ticks = 0.125 beat
* **f** = Eight triplet = 160 ticks = 0,08333 beat
* **s** = Sixteenth = 120 ticks = 0.0625 beat
* **x** = Sixteenth triplet = 80 ticks = 0,041666 beat
* **t** = Thirty-second = 60 ticks = 0.03125 beat
* **g** = Thirty-second triplet = 40 ticks = 0,0208333 beat
* **u** = Sixty-fourth = 30 ticks = 0.015625 beat
* **j** = Sixty-fourth triplet = 20 ticks = 0,01041666 beat
* **o** = Hundred twenty-eighth = 10 ticks = 0.005 beat
* **z** = Zero = 0 ticks = 0 beat

Ties can be created using multiple note length characters. Tied note lengths are summed up for the next degree, for example:

```ruby
# q+e=0.375
zplay "q 0 qe 2 3 4 qe 3 4"
```

. for dotted notes. First dot increases the duration of the basic note by half of its original value. Second dot half of the half, third dot half of the half of the half ... and so on. For example dots added to Whole note "w." will change the duration to 1.5, second dot "w.." to 1.75, third dot to 1.875.

## Bars and Measures

Bars can be used to separate melody to array of measures. Measures also start in the default octave and note length, unless explictly stated otherwise.

```ruby
a = zparse "| q _ 0 1 | 2 3 | 5 6 | 7 8 |"
print a.measures # List of measures (List of lists)
print a.measures[2].pcs # Pitch classes from given measure
print a.hash_measures # Measures in hash format
print a.group_measures(2) # Creates matrix of arrays [[[..],[..]],[[..],[..]]]
```

## Subdivisions

Subdivision notation divides the previous note length to equal proportions and can be used to create complex patterns:

```ruby
zplay "[4 2 4 2] [4 5 4 2] [3 1 3 1] [3 4 3 1] [4 2 4 2] [4 5 4 2] 4 [4 3 2 1] 0"
zplay "w [1 2 3 4] h [1 2 3 4] q [1 2 3 4] w [1 2[3 4]] h [ 1 [ 2 [ 3 [ 4 ]]]]"
```

## Rest / Silence


Use r to create musical rest in the melodies. r can be combined with note length, meaning it will sleep the length of the r, for example:

```ruby
# Play quarter note 1 (D) and then sleep half note and then play half note 2 (E)
zplay "q 1 h r 2", key: :d
```

## Sharp and flat

* `b` is flat
* `#` is sharp

Sharps and flats are not sticky so you have to use it every time before the note number. For example in key of C: `#0` = C#


## Chords

Chords can be played using roman numerals: `i ii iii iv v vi vii`.

```ruby
# Play chords as a sequence using default chord length of 1
zplay "[: i vi v :]" 
zplay "q [: iv 1 2 3 iii 2 3 4 ii 4 3 2 i 1 2 3 :]", chord_sleep: 0 # Play chord simultaniously with the melody using **chord_sleep**
Chord key is assigned with key parameter (defaults to major). Alternatively chord_key can be used to change the key for the chords.
```

Chords can be customized by taking more notes from the scale or by using chord names.

Examples using the scale:

```ruby
zplay "i"   # Plays trichord
zplay "i+1" # Plays root
zplay "i+4" # Plays 7th chord
zplay "i+5" # Plays 9th chord
zplay "i+24" # Plays chord in multiple octaves
```

For using chord names see Sonic Pi:s chord and chord_names in help. Notice that current key is ignored if the chord_name is used. Define chord name using using ^ with the name.

Examples using the chord names:

```ruby
zplay "i vi", chord_name: :dim
zplay "i vi^dim"
zplay "i^7*2" # Plays chord in 2 octaves
zplay "i vi", chord_name: "m11+"
zplay "i vi^m11+"
zplay "i^maj*2" # Plays chord in two octaves
Chords can also be inverted using % char, for example %1 to invert all following chords up by one:

zplay "vii%-2 iii%-1 vi%-1 ii v i%1 iv%2", chord_sleep: 0.25, key: :d, scale: :minor
```

## Arpeggios


You can also create melodies by playing chord arpeggios using G character and chords. You can use subset of ziffers notation to denote chord notes and note lengths (other than that might not work as expected). Arpeggio subset can be escaped using ' right after the G character. Escaping is useful especially if combined with the note grouping. Alternatively groups parameter can be set to false.

Examples:

```ruby
zplay "@(q 1 2 3 1) i ii iii iv v vi vii"

zplay "@(q 0 1 e 2 1 0 1) [: i^7 :3][: iv^dim7%-1 :3]", key: :d4, scale: :mixolydian

zplay "@(q 0 123) [: i^7 :4][: iv%-1 :4]"
```

## Escape/eval

You can escape a degree using the following syntax: 

```ruby
{10 11} {1.2 2.43} {3+1*2}
```

## Octaves

Octave can be adjusted up by one using ^ or down by one using _ for all the following notes. Alternatively octave can be changed directly to given value using (number) for example (1) to change the octave to 1.

Single octave changes can be grouped to single notes or chords, for example (2) _3 3 will first change octave to 2 and then next note's octave is set down by one.

Octave is reseted automatically to default when measures are denoted with |.


```ruby
^ 0 ^ 1 _ 2 _ 3
zplay "q 0 1 2 ^ 0 ^^ 1 2 _ 0 1 2 __ 0 1 2" # Octaves changed for following notes
zplay "q 0 _4 0 ^1 _1^3__2" # Change octave for single notes only
zplay "q 0 <-1> 0 2 <0> 0 1" # Change octave explicitly to certain value for all following notes
zplay "_A A ^A", A: :ambi_choir # Change pitch of the sample
zplay "q 1 2 ^ 3 4 ^ 0 ^ 4 3 ___ 2 1", octave: -1 # Staff octave is set to -1
zplay "1 1__3^3 1<3>3<1>3" # Both syntaxes can be used with chords
zplay "|q _ 0 1 | 0 1 |" # Octaves (and durations) are reseted in each measure
```

## Escaped octave

```ruby
<2> 1 <1>1<-2>3
```

## Randoms

```ruby
% ? % ? % ?
```

## Random between

```ruby
(-3,6)
```

## Random selections

```ruby
[q 1 2, q 3 e 4 6]
```

## Repeat

Use [: 1 2 :] as a basic repeat. Repeats can also be recursive for example in Frere Jacques:


```ruby
[: 1 (2,6) 3 :4]
```

Use < part ; part > in repeats for alternative sections, like:

```ruby
"[: 1 2 3 < 4 3 2 ; 5 4 3 > :]".
```

Alternative endings in ievan polkka:

```ruby
zplay "[: q 0 e0 e0 0 1 | q 2 0 0 2 | < q 1 -1 -1 1 | q 2 0 h0  | ; | q.4 e3 q 2 1  | q 2 0 h0 > :] "\
  "[: q 4 e4 e4 3 2 | q 1 -1 -1 1 | < q 3 e3 e3 2 1 | q 2 0 0 2 | ; | q 3 e3 e3 2 1 | q 2 0 h0 > :]", key: :g, scale: :minor
```

## Staccato

' is a shorthand for halving the release or schrinking the sample.

```ruby
zplay "h 0 '0 ''0 '''0"
zplay "A 'A ''A '''A", A: :ambi_choir
```


## Cycles

```ruby
[: <q,e> 1  <2 3,3 5> :]
```

## Lists

```ruby
h 1 q(0 1 2 3) 2
```

## List operations

```ruby
(1 2 (3 4)+2)*2 ((1 2 3)+(0 9 13))-2 ((3 4 {10})*(2 9 3))%7
```

## List assignation

```ruby
A=(0 (1,6) 3) B=(3 ? 2) B A B B A
```

## Random repeat

```ruby
(: 1 (2,6) 3 :4)
```

## Conditionals

```ruby
1 {%<0.5?3} 3 4 (: 1 2 {%<0.2?3:2} :3)
```

## Functions

```ruby
(0 1 2 3){x%3==0?x-2:x+2}
```

## Polynomials

```ruby
(-10..10){(x**3)*(x+1)%12}
```
