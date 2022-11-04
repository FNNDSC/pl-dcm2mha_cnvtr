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
from skimage.transform import resize
import csv
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

    NAME

       dcm2mha_cnvtr

    SYNOPSIS

        docker run --rm fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr           \\
            [-f|--inputFileFilter <inputFileFilter>]                    \\
            [-s|--saveAsPng]                                            \\
            [-n|--imageName <pngFileName>]                              \\
            [-p|--filterPerc <filterPercentage>]                        \\
            [-r| --rotate <rotateAngle>]                                \\
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
                fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr               \
                /incoming /outgoing

    DESCRIPTION

        `dcm2mha_cnvtr` ...

    ARGS
        [-f|--inputFileFilter <inputFileFilter>]
        A glob pattern string, default is "**/*.mha",
        representing the input file that we want to
        convert. You can choose either .mha or .dcm
        files
        
        [-s|--saveAsPng]  
        If specified, generate a resultant PNG image along with dicoms
                                                 
        [-n|--imageName <pngFileName>]
        The name of the resultant PNG file. Default is "composite.png"
                                               
        [-p|--filterPerc <filterPercentage>]
        An integer value that represents the lowest percentage of the
        maximum intensity of the PNG image that should be set to 0. 
        This field is particularly important if there is too much noise 
        in an image and we want to get a sharper resultant PNG. Default
        is 30 
        
        [-r| --rotate <rotateAngle>]  
        An integer value in multiples of 90 that represents a rotation
        angle. The input image will be rotated anticlockwise for the 
        provide angle                                 

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
    An app to convert dicom images to .mha and vice versa
    """
    PACKAGE                 = __package__
    TITLE                   = 'A ChRIS plugin app to convert dcm files to mha and vice-versa'
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
                            
        self.add_argument(  '--saveAsPng','-s',
                            dest         = 'saveAsPng',
                            type         = bool,
                            optional     = True,
                            help         = 'Save .mha file as png',
                            default      = False)
                            
        self.add_argument(  '--rotate','-r',
                            dest         = 'rotate',
                            type         = int,
                            optional     = True,
                            help         = 'Rotate input image in a anti-clockwise direction',
                            default      = 0)
                            
        self.add_argument(  '--imageName','-n',
                            dest         = 'imageName',
                            type         = str,
                            optional     = True,
                            help         = 'Name of the png file',
                            default      = 'composite.png')
                            
        self.add_argument(  '--filterPerc','-p',
                            dest         = 'filterPerc',
                            type         = int,
                            optional     = True,
                            help         = 'Specify the lowest percentage of pixel values to be set to zero',
                            default      = 30)
                            
        self.add_argument(  '--dimensionFile','-d',
                            dest         = 'dimensionFile',
                            type         = str,
                            optional     = True,
                            help         = 'Specify the lowest percentage of pixel values to be set to zero',
                            default      = "dimension.csv")
                            
        self.add_argument(  '--resizePng','-z',
                            dest         = 'resizePng',
                            type         = bool,
                            optional     = True,
                            help         = 'Specify this flag if you want to resize the output PNGs',
                            default      = False)
                            
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
        
        data = {}
        
        if(options.resizePng):
        
            csv_path = os.path.join(options.inputdir,options.dimensionFile)
        
            with open(csv_path, encoding='utf-8') as csvf:
                csvReader = csv.reader(csvf)
            
                for rows in csvReader:
                    key = rows[0]
                    data[key] = (int(rows[1]),int(rows[2]))
                    
                    
        
        str_glob = '%s/%s' % (options.inputdir,options.inputFileFilter)
        
        l_datapath = glob.glob(str_glob, recursive=True)
        
        for datapath in l_datapath:
            if(datapath.endswith('.mha')):
                save_path = datapath.split('/')[-1]
                save_path = save_path.replace('.mha','')
                save_path = os.path.join(options.outputdir,save_path)
                self.convert_to_dcm(datapath,save_path,options.saveAsPng, options.imageName, options.filterPerc,data)
            else:
                save_path = datapath.split('/')[-1]
                save_path = save_path.replace('.dcm','.mha')
                save_dir = os.path.join(options.outputdir,'mha')
                save_path = os.path.join(options.outputdir,'mha',save_path)
                self.convert_to_mha(datapath,save_path, save_dir,options.rotate)
        
    def show_man_page(self):
        """
        Print the app's man page.
        """
        print(Gstr_synopsis)
    
    def convert_to_mha(self, dicom_path,mha_path,save_dir,rotate,compress=True):
        ds = dicom.dcmread(dicom_path)
        im = ds.pixel_array.astype(float)

        rescaled_image = (np.maximum(im,0)/im.max())*255 # float pixels
        final_image = np.uint8(rescaled_image) # integers pixels
        num_rotations = int(rotate/90)
        for i in range(0,num_rotations):
            final_image = np.rot90(final_image)
        final_image = np.expand_dims(final_image, axis=0)

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
             
    def convert_to_dcm(self, mha_path,dicom_path,saveAsPng,imageName, filterPerc,data):
        # parse input arguments
        # 1. img_filename: name of image file (incl. extension)
        img_filename = mha_path
        # 2. output_path: path of directory containing the output DICOM series
        output_path = dicom_path

        img = sitk.ReadImage(img_filename)


        list(map(lambda i: self.writeSlices( img, i, output_path), range(img.GetDepth())))
        
        if saveAsPng:
            
            files = glob.glob(output_path+"/*.dcm")
            sample = dicom.dcmread(files[0])
            sample = sample.pixel_array
            dim = sample.shape
            if(data!={}):
                for key in data.keys():
                    if key in output_path:
                        dim = data[key]

            if len(files) == 1:
                new_image =sample.astype(float)
                scaled_image = (np.maximum(new_image, 0) / new_image.max()) * 255.0
                result = np.uint8(scaled_image)
            else:
                result = np.zeros(dim,dtype='uint8')
                for file in files:
                    ds = dicom.dcmread(file)
                    new_image = ds.pixel_array.astype(float)
                    
                    # resize image
                    resized_image = resize(new_image, dim)
                    
                    
                    # scale the image in the range of 1:255
                    scaled_image = (np.maximum(resized_image, 0) / resized_image.max()) * 255.0
                    
                    # Maximum pixel value in the dicom image
                    max_value = scaled_image.max()
                    
                    # lowest pixel value to filter out
                    max_filter_value = (filterPerc/100.0)*max_value
                    scaled_image[scaled_image<=max_filter_value] = 0
                    
                    scaled_image = np.uint8(scaled_image)
                    result = result + scaled_image
            final_image = Image.fromarray(result)
            final_image.save(os.path.join(output_path,imageName))
            
            print(f"Shape of the {os.path.join(output_path,imageName)} is {result.shape}")

    def writeSlices(self, img, i, output_path):
        castFilter = sitk.CastImageFilter()
        castFilter.SetOutputPixelType(sitk.sitkInt16)
    
        # Convert floating type image (imgSmooth) to int type (imgFiltered)
        image_slice = castFilter.Execute(img[:,:,i])

        
        writer = sitk.ImageFileWriter()
        # Use the study/series/frame of reference information given in the meta-data
        # dictionary and not the automatically generated information from the file IO
        writer.KeepOriginalImageUIDOn()
 
        # Write to the output directory and add the extension dcm, to force writing in DICOM format.
        writer.SetFileName(os.path.join(output_path,str(i).zfill(4)+'.dcm'))

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        writer.Execute(image_slice)
