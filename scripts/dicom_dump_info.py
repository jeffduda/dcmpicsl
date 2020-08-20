import os
import pydicom
import itk
import numpy as np
import getopt, sys
import os.path

from os import path
from time import strftime
from datetime import date
from datetime import datetime
from os import listdir
from os.path import isfile, join, isdir
from pydicom.uid import generate_uid
from pydicom.sequence import Sequence
from pydicom.dataset import Dataset
from optparse import OptionParser
from optparse import OptionGroup
from pydicom.errors import InvalidDicomError


parser = OptionParser()

required = OptionGroup(parser, "Required parameters", "These parameters are required")

required.add_option( "-i", "--input-directory", action="store", type="string", dest="inDir", help="Directory containinig dicom files")
required.add_option( "-o", "--output-directory", action="store", type="string", dest="outDir", help="Output directory")

parser.add_option_group(required)

(options, args) = parser.parse_args()

if ( not options.outDir==None ):
    if ( options.outDir==options.inDir):
        print("Output diretory must be different than input directory")
        exit(1)

# Check required inputs
if ( options.inDir==None or not path.exists(options.inDir) ):
    print("Input image directory does not exist: "+options.input)
    exit(1)

if ( options.outDir!=None and not path.exists(options.outDir) ):
    print("Output directory should already exist, but does not")
    exit(1)

subdirs = [f for f in listdir(options.inDir) if isdir(join(options.inDir, f))]

studyConsistent=True

globalStudyUID=None
globalStudyConsistent=True
hasStudyUID=True
hasSeriesUID=True

for s in subdirs:
    #if (not isdir(join(options.outDir,s))):
    #    os.mkdir( join(options.outDir,s) )

    onlyfiles = [f for f in listdir(join(options.inDir,s)) if isfile(join(options.inDir,s,f))]

    fname = join(options.outDir,s+"_pyDicom.txt")
    ofile = open(fname, 'w')

    count = 0
    done=False
    for f in onlyfiles:
        if ( not done ):
            dcf=None
            try:
                dcf = pydicom.dcmread(join(options.inDir,s,f))
                print(dcf, file=ofile)
                done=True
            except InvalidDicomError:
                count += 1

    ofile.close
print("Exit")

# cat /data/jux/grosspeople/pcook/tmp/unreadableData.txt | while read x y ; do echo $x $y; mkdir -p /data/jux/jtduda/data/DicomHeaders/$x/$y; python dicom_dump_info.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y -o /data/jux/jtduda/data/DicomHeaders/$x/$y; done
