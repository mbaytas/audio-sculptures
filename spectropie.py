# wave is taking too long, move to pydub

import wave
from math import log
import matplotlib.mlab as mlab
import numpy
from tangible import ast, scales
from tangible.backends.openscad import OpenScadBackend
from tangible.shapes.base import BaseShape

# Relative path to the WAV file
inPath = 'basket.wav'
# Relative path to the SCAD output file
outPath = "pie.scad"
# Play with this to move between linear and logarithmic scaling of amplitudes
loggishness = 0.000000000000000001
# These parameters determine the "resolution" of the spectrogram
nfft = 2**18
padto = 2**3

def main():
    print "Reading and analyzing file..."
    spectrum, freqs = ReadAndAnalyze(inPath)

    print "Scaling logarithmically (kinda)..."
    for i, s in enumerate(spectrum):
      spectrum[i] = map(loggish, s)

    print "Generating linear scale..."
    scale = scales.linear(domain=[spectrum.min(), spectrum.max()],
                          codomain=[0, 20000])

    print "Generating ring-shaped pieces..."
    rIndexes = range(len(freqs)-1)
    unitAngle = 360.0/len(spectrum[0]) # depends on total time & sample rate
    angles = numpy.arange(0, 360, unitAngle)

    print len(spectrum[0])
    print len(angles)
    print len(freqs)

    rings = []

    for rIndex in rIndexes:
        rInner = freqs[rIndex] + 8000
        rOuter = freqs[rIndex+1] + 8000

        print "Generating ring for region: %s Hz - %s Hz" % (rInner, rOuter)

        print "-- Normalizing spectrum data with linear scale..."
        data = map(scale, spectrum[:][rIndex])

        ringSectors = []
        for angleIndex, angle in enumerate(angles):
            sector = ast.CircleSector(rOuter, unitAngle)
            if rInner:
                killer = ast.CircleSector(rInner, unitAngle)
                sector = ast.Difference([sector, killer])
            sector = ast.Rotate(unitAngle*angleIndex, (0,0,1), sector)
            sector = ast.LinearExtrusion(data[angleIndex], sector)
            ringSectors.append(sector)

        ring = ast.Union(ringSectors)

        rings.append(ring)

    print "Generating unified geometry..."
    union = ast.Union(rings)

    print "Rendering..."
    with open(outPath, "w") as f:
        code = OpenScadBackend(union).generate()
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
                             Fs=frame_rate,
                             noverlap=512)
    spectrum = specdata[0]
    freqs = specdata[1]
    return spectrum, freqs

if __name__ == '__main__':
    main()
