#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""MCP Detector Correction.

Usage:
    mcp_detector_correction [--skipimg] [--verbose] <input_dir> <output_dir>
    mcp_detector_correction (-h | --help)
    mcp_detector_correction --version

Options:
    --skipimg    skip first and last image
    -h --help    print this message
    --version    print version info
    --verbose    verbose output
"""

import glob
from docopt import docopt
from pathlib import Path
from neutronimaging.detector_correction import correct_images, load_images, read_shutter_count
from neutronimaging.detector_correction import read_shutter_time
from neutronimaging.detector_correction import read_spectra
from neutronimaging.detector_correction import merge_meta_data

if __name__ == "__main__":
    args = docopt(__doc__, help=True, version='MCP Detector Correction 1.0')

    # parsing input
    print("Parsing input")
    input_dir = args["<input_dir>"]
    output_dir = args["<output_dir>"]
    skip_first_last_img = args["--skipimg"]
    verbose = args["--verbose"]
    shutter_count_file = glob.glob(input_dir + '/*_ShutterCount.txt')[0]
    shutter_time_file = glob.glob(input_dir + '/*_ShutterTimes.txt')[0]
    spectra_file = glob.glob(input_dir + '/*_Spectra.txt')[0]

    # validation
    print("Validating input arguments")
    assert Path(input_dir).exists()
    assert Path(output_dir).exists()
    assert Path(shutter_count_file).exists()
    assert Path(shutter_time_file).exists()
    assert Path(spectra_file).exists()

    # process metadata
    print("Processing metadata")
    df_meta = merge_meta_data(
        read_shutter_count(shutter_count_file), 
        read_shutter_time(shutter_time_file), 
        read_spectra(spectra_file),
        )
    if verbose:
        print(df_meta)
    
    # load images
    print("Loading images into memory")
    o_norm = load_images(input_dir)

    # perform image correction
    print("Perform correction")
    img_corrected = correct_images(
        o_norm, 
        df_meta, 
        skip_first_and_last=skip_first_last_img,
        )
    print("corrected image summary")
    print(f"\tdimension:\t{img_corrected.shape}")
    print(f"\ttype:\t{img_corrected.dtype}")
    
    # export results
    print(f"Writing data to {output_dir}")
    o_norm.data['sample']['data'] = img_corrected
    o_norm.export(folder=output_dir, data_type='sample')
