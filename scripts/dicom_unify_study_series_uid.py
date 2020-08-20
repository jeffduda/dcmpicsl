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
optional = OptionGroup(parser, "Optional parameters", "These parameters are optional")

required.add_option( "-i", "--input-directory", action="store", type="string", dest="inDir", help="Directory containinig dicom files")
optional.add_option( "-o", "--output-directory", action="store", type="string", dest="outDir", help="Output directory")
optional.add_option( "-v", "--verbose", action="store_true", default=False, help="Verbose output [default=%default]")

parser.add_option_group(required)
parser.add_option_group(optional)

(options, args) = parser.parse_args()
if ( options.verbose):
    print(options)

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

studyUID=pydicom.uid.generate_uid()

for s in subdirs:
    seriesUID=pydicom.uid.generate_uid()
    onlyfiles = [f for f in listdir(join(options.inDir,s)) if isfile(join(options.inDir,s,f))]
    print(s+" ("+str(len(onlyfiles))+" files)")
    print( "  " + str(studyUID) + "  ->  " + str(seriesUID) )

    if (options.outDir != None):
        os.mkdir( join(options.outDir,s) )

    for f in onlyfiles:
        dcf=None
        try:
            dcf = pydicom.dcmread(join(options.inDir,s,f))
        except InvalidDicomError:
            ignored = ignored + 1
            if ( options.verbose ):
                print("  WARNING: Non-Dicom found & ignored: " + join(options.inDir,s,f) )

        if ( dcf != None ):

            if ( not options.outDir == None ):

                if "StudyInstanceUID" in dcf:
                    dcf.StudyInstanceUID = studyUID
                else:
                    dcf.add_new(0x0020000d, 'UI', studyUID)

                if "SeriesInstanceUID" in dcf:
                    dcf.SeriesInstanceUID = seriesUID
                else:
                    dcf.add_new(0x0020000e, 'UI', seriesUID)

                instanceUID = pydicom.uid.generate_uid()
                if "SOPInstanceUID" in dcf:
                    dcf.SOPInstanceUID = instanceUID
                else:
                    dcf.add_new(0x00080018, 'UI', instanceUID)

                mrUID = '1.2.840.10008.5.1.4.1.1.4'
                if "SOPClassUID" in dcf:
                    dcf.SOPClassUID = mrUID
                else:
                    dcf.add_new(0x00080016, 'UI', mrUID)

                dcf.save_as(join(options.outDir,s,f))






#IFS=','
#tail -n +2 ../sessionsToFixWithReadErrors.csv | while read x y ; do echo $x $y; mkdir -p /data/jux/jtduda/data/DicomHeaders/$x/$y; python dicom_dump_info.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y -o /data/jux/jtduda/data/DicomHeaders/$x/$y; done
#tail -n +2 ../sessionsToFixWithReadErrors.csv | while read x y ; do echo $x $y; python ~/data/badUID/dicom_unify_study_series_uid.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y; done
#tail -n +2 sessionsToFix.csv | while read x y ; do echo $x $y; mkdir -p /data/jux/grosspeople/pcook/fixBadUIDs/data/$x/$y; python dicom_unify_study_series_uid.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y -o /data/jux/grosspeople/pcook/fixBadUIDs/data/$x/$y  ; done
