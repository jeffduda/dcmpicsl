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
from pydicom.uid import ExplicitVRLittleEndian
from pydicom.uid import ExplicitVRBigEndian

def illegaltag_callback(dataset, data_element):
    if data_element.tag.group == 0x0001:
        del dataset[data_element.tag]
    if data_element.tag.group == 0x0003:
        del dataset[data_element.tag]
    if data_element.tag.group == 0x0005:
        del dataset[data_element.tag]
    if data_element.tag.group == 0x0007:
        del dataset[data_element.tag]

parser = OptionParser()

required = OptionGroup(parser, "Required parameters", "These parameters are required")
optional = OptionGroup(parser, "Optional parameters", "These parameters are optional")

required.add_option( "-i", "--input-directory", action="store", type="string", dest="inDir", help="Directory containinig subdirectories of dicom files, organized by series")
optional.add_option( "-o", "--output-directory", action="store", type="string", dest="outDir", help="Output directory")
optional.add_option( "-r", "--rename", action="store_true", default=False, help="Rename files by SOPInstanceUID [default=%default]")
optional.add_option( "-v", "--verbose", action="store_true", default=False, help="Verbose output [default=%default]")

parser.add_option_group(required)
parser.add_option_group(optional)

(options, args) = parser.parse_args()
if ( options.verbose ):
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
    #print(s+" ("+str(len(onlyfiles))+" files)")
    #print( "  " + str(studyUID) + "  ->  " + str(seriesUID) )

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
                if "MediaStorageSOPInstanceUID" in dcf.file_meta:
                    dcf.file_meta.MediaStorageSOPInstanceUID = instanceUID
                else:
                    dcf.file_meta.add_new(0x00020003, 'UI', instanceUID)

                mrUID = '1.2.840.10008.5.1.4.1.1.4'
                if "SOPClassUID" in dcf:
                    dcf.SOPClassUID = mrUID
                else:
                    dcf.add_new(0x00080016, 'UI', mrUID)

                if "MediaStorageSOPClassUID" in dcf.file_meta:
                    dcf.file_meta.MediaStorageSOPClassUID = mrUID
                else:
                    dcf.file_meta.add_new(0x00020002, 'UI', mrUID)

                endianUID = pydicom.uid.ExplicitVRLittleEndian

                if ( dcf.is_little_endian ):
                    if ( dcf.is_implicit_VR ):
                        endianUID = pydicom.uid.ImplicitVRLittleEndian
                else:
                    endianUID = pydicom.uid.ExplicitVRBigEndian
                    if ( dcf.is_implicit_VR ):
                        endianUID = pydicom.uid.ImplicitVRBigEndian
                if "TransferSyntaxUID" in dcf.file_meta:
                    dcf.file_meta.TransferSyntaxUID = endianUID
                else:
                    dcf.file_meta.add_new(0x00020010, 'UI', endianUID)

                implementUID = '1.2.826.0.1.3680043.8.498.1'
                if "ImplementationClassUID" in dcf.file_meta:
                    dcf.file_meta.ImplementationClassUID = implementUID
                else:
                    dcf.file_meta.add_new(0x00020012, 'UI', implementUID)

                #dcf.remove_private_tags()
                dcf.walk(illegaltag_callback)

                if ( options.rename ):
                    dcf.save_as(join(options.outDir,s,instanceUID))
                else:
                    dcf.save_as(join(options.outDir,s,f))






#IFS=','
#tail -n +2 ../sessionsToFixWithReadErrors.csv | while read x y ; do echo $x $y; mkdir -p /data/jux/jtduda/data/DicomHeaders/$x/$y; python dicom_dump_info.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y -o /data/jux/jtduda/data/DicomHeaders/$x/$y; done
#tail -n +2 ../sessionsToFixWithReadErrors.csv | while read x y ; do echo $x $y; python ~/data/badUID/dicom_unify_study_series_uid.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y; done
#tail -n +2 sessionsToFix.csv | while read x y ; do echo $x $y; mkdir -p /data/jux/grosspeople/pcook/fixBadUIDs/data/$x/$y; python dicom_unify_study_series_uid.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y -o /data/jux/grosspeople/pcook/fixBadUIDs/data/$x/$y  ; done
