from math import log
import matplotlib.mlab as mlab
import numpy
from tangible import ast, scales
from tangible.backends.openscad import OpenScadBackend
from tangible.shapes.bars import BarsND
import wave


wav_file = 'meantime.wav'
loggishness = 0.00000000000004
nfft = 2**18
padto = nfft/(2**13)

print "Reading and analyzing file..."
spectrum, freqs = ReadAndAnalyze(filename)

print len(spectrum[0])
print len(freqs)

print "Scaling logarithmically (kinda)..."
for i, s in enumerate(spectrum):
  spectrum[i] = map(loggish, s)

print "Generating linear scale..."
scale = scales.linear(domain=[spectrum.min(), spectrum.max()],
                      codomain=[1, 10])

print "Normalizing spectrum data..."
datapoints = map(lambda x: map(scale, x), spectrum)

print "Trimming spectrum data post-normalization..."
for i, x in enumerate(datapoints):
  for j, v in enumerate(x):
      if v > 9:
        datapoints[i][j] = 9

print "Generating bars..."
bars = BarsND(datapoints,
              bar_width=1,
              bar_depth=1)

print "Rendering..."
code = bars.render(backend=OpenScadBackend)

print "Saving to file..."
with open("bars.scad", "w") as f:
    f.write(code)

def loggish(v):
  v = float(v)
  L = loggishness
  return L * (log(v) - v) + v

def ReadAndAnalyze(filename):
    wav = wave.open(wav_file, 'r')
    frames = wav.readframes(-1)
    sound_info = numpy.fromstring(frames, 'Int16')
    frame_rate = wav.getframerate()
    wav.close()
    specdata = mlab.specgram(sound_info,
                             NFFT=nfft,
                             pad_to=padto,
                             Fs=frame_rate)
    spectrum = specdata[0]
    freqs = specdata[1]
    return spectrum, freqs