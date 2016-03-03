from math import log
import matplotlib.mlab as mlab
import numpy
from tangible import ast, scales
from tangible.backends.openscad import OpenScadBackend
from tangible.shapes.bars import BarsND
import wave

# Relative path to the WAV file
inPath = ""
# Relative path to the SCAD output file
outPath = "bars.scad"
# Play with this to move between linear and logarithmic scaling of amplitudes
loggishness = 0.00000000000004
# These parameters determine the "resolution" of the spectrogram
nfft = 2**18
padto = nfft/(2**13)

def main():

  print "Reading and analyzing file..."
  spectrum, freqs = ReadAndAnalyze(inPath)

  print len(freqs)
  print len(spectrum[0])


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
  with open(outPath, "w") as f:
      f.write(code)

def loggish(v):
  v = float(v)
  L = loggishness
  return L * (log(v) - v) + v

def ReadAndAnalyze(f):
    wav = wave.open(f, 'r')
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

if __name__ == "__main__":
  main()