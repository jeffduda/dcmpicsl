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
from pydicom.tag import Tag


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

    sp = options.inDir.split('/')
    last = len(sp)-1
    if sp[last] == "":
        last = len(sp)-2

    date = str(sp[last])
    subject = str(sp[last-1])
    seriesDir = str(s)

    prefix = subject + "," + date + "," + seriesDir

    onlyfiles = [f for f in listdir(join(options.inDir,s)) if isfile(join(options.inDir,s,f))]

    fname = join(options.outDir,s+"_pyDicom.txt")
    ofile = open(fname, 'w')

    count = 0

    done=False

    for f in onlyfiles:
        if ( not done ):
            dcf=None
            try:
                name="NA"
                id="NA"
                study="NA"
                voxbo=0

                dcf = pydicom.dcmread(join(options.inDir,s,f))
                #print(dcf, file=ofile)
                pNameTag = Tag((0x10,0x10))
                pIDTag = Tag((0x10,0x20))
                studyUIDTag = Tag((0x0020,0x000d))
                voxboTag=Tag((0x1119,0x0001))

                if pNameTag in dcf.keys():
                    pName = str( dcf[pNameTag].value )
                    if ( pName != "" ):
                        name = pName

                if pIDTag in dcf.keys():
                    pID = str( dcf[pIDTag].value )
                    if ( pID != "" ):
                        id = pID

                if studyUIDTag in dcf.keys():
                    studyUID = str( dcf[studyUIDTag].value )
                    if ( studyUID != "" ):
                        study=studyUID

                if voxboTag in dcf.keys():
                    voxbo=1

                print(prefix + "," + str(voxbo) + "," + name + "," + id + "," + study)

                done=True
            except InvalidDicomError:
                count += 1

    ofile.close

# cat /data/jux/grosspeople/pcook/tmp/unreadableData.txt | while read x y ; do echo $x $y; mkdir -p /data/jux/jtduda/data/DicomHeaders/$x/$y; python dicom_dump_info.py -i /data/jux/grosspeople/Volumetric/SIEMENS/Subjects/$x/$y -o /data/jux/jtduda/data/DicomHeaders/$x/$y; done
