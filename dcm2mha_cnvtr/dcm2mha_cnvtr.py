#
# dcm2mha_cnvtr ds ChRIS plugin app
#
# (c) 2022 Fetal-Neonatal Neuroimaging & Developmental Science Center
#                   Boston Children's Hospital
#
#              http://childrenshospital.org/FNNDSC/
#                        dev@babyMRI.org
#

from chrisapp.base import ChrisApp
import os
import sys
import time
import SimpleITK as sitk
import pydicom as dicom
import glob
import numpy as np
from PIL import Image
Gstr_title = r"""
     _                 _____           _                            _        
    | |               / __  \         | |                          | |       
  __| | ___ _ __ ___  `' / /'_ __ ___ | |__   __ _   ___ _ ____   _| |_ _ __ 
 / _` |/ __| '_ ` _ \   / / | '_ ` _ \| '_ \ / _` | / __| '_ \ \ / / __| '__|
| (_| | (__| | | | | |./ /__| | | | | | | | | (_| || (__| | | \ V /| |_| |   
 \__,_|\___|_| |_| |_|\_____/_| |_| |_|_| |_|\__,_| \___|_| |_|\_/  \__|_|   
                                                ______                       
                                               |______|                      
"""

Gstr_synopsis = """

(Edit this in-line help for app specifics. At a minimum, the 
flags below are supported -- in the case of DS apps, both
positional arguments <inputDir> and <outputDir>; for FS and TS apps
only <outputDir> -- and similarly for <in> <out> directories
where necessary.)

    NAME

       dcm2mha_cnvtr

    SYNOPSIS

        docker run --rm fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr                     \\
            [-h] [--help]                                               \\
            [--json]                                                    \\
            [--man]                                                     \\
            [--meta]                                                    \\
            [--savejson <DIR>]                                          \\
            [-v <level>] [--verbosity <level>]                          \\
            [--version]                                                 \\
            <inputDir>                                                  \\
            <outputDir> 

    BRIEF EXAMPLE

        * Bare bones execution

            docker run --rm -u $(id -u)                             \
                -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
                fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr                        \
                /incoming /outgoing

    DESCRIPTION

        `dcm2mha_cnvtr` ...

    ARGS

        [-h] [--help]
        If specified, show help message and exit.
        
        [--json]
        If specified, show json representation of app and exit.
        
        [--man]
        If specified, print (this) man page and exit.

        [--meta]
        If specified, print plugin meta data and exit.
        
        [--savejson <DIR>] 
        If specified, save json representation file to DIR and exit. 
        
        [-v <level>] [--verbosity <level>]
        Verbosity level for app. Not used currently.
        
        [--version]
        If specified, print version number and exit. 
"""


class Dcm2mha_cnvtr(ChrisApp):
    """
    An app to ...
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin app'
    CATEGORY                = ''
    TYPE                    = 'ds'
    ICON                    = ''   # url of an icon image
    MIN_NUMBER_OF_WORKERS   = 1    # Override with the minimum number of workers as int
    MAX_NUMBER_OF_WORKERS   = 1    # Override with the maximum number of workers as int
    MIN_CPU_LIMIT           = 2000 # Override with millicore value as int (1000 millicores == 1 CPU core)
    MIN_MEMORY_LIMIT        = 8000  # Override with memory MegaByte (MB) limit as int
    MIN_GPU_LIMIT           = 0    # Override with the minimum number of GPUs as int
    MAX_GPU_LIMIT           = 0    # Override with the maximum number of GPUs as int

    # Use this dictionary structure to provide key-value output descriptive information
    # that may be useful for the next downstream plugin. For example:
    #
    # {
    #   "finalOutputFile":  "final/file.out",
    #   "viewer":           "genericTextViewer",
    # }
    #
    # The above dictionary is saved when plugin is called with a ``--saveoutputmeta``
    # flag. Note also that all file paths are relative to the system specified
    # output directory.
    OUTPUT_META_DICT = {}

    def define_parameters(self):
        """
        Define the CLI arguments accepted by this plugin app.
        Use self.add_argument to specify a new app argument.
        """
        self.add_argument(  '--inputFileFilter','-f',
                            dest         = 'inputFileFilter',
                            type         = str,
                            optional     = True,
                            help         = 'Input file filter',
                            default      = '**/*.mha')
                            
    def run(self, options):
        """
        Define the code to be run by this plugin app.
        """
        print(Gstr_title)
        print('Version: %s' % self.get_version())

        # Output the space of CLI
        d_options = vars(options)
        for k,v in d_options.items():
            print("%20s: %-40s" % (k, v))
        print("")
        
        str_glob = '%s/%s' % (options.inputdir,options.inputFileFilter)
        
        l_datapath = glob.glob(str_glob, recursive=True)
        
        for datapath in l_datapath:
            if(datapath.endswith('.mha')):
                save_path = datapath.split('/')[-1]
                save_path = save_path.replace('.mha','')
                save_path = os.path.join(options.outputdir,save_path)
                self.convert_to_dcm(datapath,save_path)
            else:
                save_path = datapath.split('/')[-1]
                save_path = save_path.replace('.dcm','.mha')
                save_dir = os.path.join(options.outputdir,'mha')
                save_path = os.path.join(options.outputdir,'mha',save_path)
                self.convert_to_mha(datapath,save_path, save_dir)
        
    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
    
    def convert_to_mha(self, dicom_path,mha_path,save_dir,compress=True):
        ds = dicom.dcmread(dicom_path)
        im = ds.pixel_array.astype(float)
        rescaled_image = (np.maximum(im,0)/im.max())*255 # float pixels
        final_image = np.uint8(rescaled_image) # integers pixels
        final_image = np.expand_dims(final_image, axis=0)
        print(final_image.shape)


        #final_image = Image.fromarray(final_image)

        self.write(sitk.GetImageFromArray(final_image), mha_path, save_dir, compress)
        
    def write(self,img, path, save_dir, compress=True):
        """
        Write a volume to a file path.
        :param img: the volume
        :param path: the target path
        :return:
        """
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        writer = sitk.ImageFileWriter()
        writer.KeepOriginalImageUIDOn()
        writer.SetFileName(path)
        writer.Execute(img)
             
    def convert_to_dcm(self, mha_path,dicom_path):
        # parse input arguments
        # 1. img_filename: name of image file (incl. extension)
        img_filename = mha_path
        # 2. output_path: path of directory containing the output DICOM series
        output_path = dicom_path

        img = sitk.ReadImage(img_filename)

        modification_time = time.strftime("%H%M%S")
        modification_date = time.strftime("%Y%m%d")

        # Copy some of the tags and add the relevant tags indicating the change.
        # For the series instance UID (0020|000e), each of the components is a number, cannot start
        # with zero, and separated by a '.' We create a unique series ID using the date and time.
        # tags of interest:
        direction = img.GetDirection()
        series_tag_values = [("0008|0031",modification_time), # Series Time
                  ("0008|0021",modification_date), # Series Date
                  ("0008|0008","DERIVED\\SECONDARY"), # Image Type
                  ("0020|000e", "1.2.826.0.1.3680043.2.1125."+modification_date+".1"+modification_time), # Series Instance UID
                  ("0020|0037", '\\'.join(map(str, (direction[0], direction[3], direction[6],# Image Orientation (Patient)
                                                    direction[1],direction[4],direction[7])))),
                  ("0008|103e", "Created-SimpleITK")] # Series Description


        list(map(lambda i: self.writeSlices(series_tag_values, img, i, output_path), range(img.GetDepth())))
        
    def writeSlices(self, series_tag_values, img, i, output_path):
        castFilter = sitk.CastImageFilter()
        castFilter.SetOutputPixelType(sitk.sitkInt16)
    
        # Convert floating type image (imgSmooth) to int type (imgFiltered)
        image_slice = castFilter.Execute(img[:,:,i])

        # Tags shared by the series.
        list(map(lambda tag_value: image_slice.SetMetaData(tag_value[0], tag_value[1]), series_tag_values))

        # Slice specific tags.
        image_slice.SetMetaData("0008|0012", time.strftime("%Y%m%d")) # Instance Creation Date
        image_slice.SetMetaData("0008|0013", time.strftime("%H%M%S")) # Instance Creation Time

        # Setting the type to CT preserves the slice location.
        image_slice.SetMetaData("0008|0060", "CT")  # set the type to CT so the thickness is carried over

        # (0020, 0032) image position patient determines the 3D spacing between slices.
        image_slice.SetMetaData("0020|0032", '\\'.join(map(str,img.TransformIndexToPhysicalPoint((0,0,i))))) # Image Position (Patient)
        image_slice.SetMetaData("0020,0013", str(i)) # Instance Number
        
        writer = sitk.ImageFileWriter()
        # Use the study/series/frame of reference information given in the meta-data
        # dictionary and not the automatically generated information from the file IO
        writer.KeepOriginalImageUIDOn()
        
        # Write to the output directory and add the extension dcm, to force writing in DICOM format.
        writer.SetFileName(os.path.join(output_path,str(i).zfill(4)+'.dcm'))

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        writer.Execute(image_slice)
