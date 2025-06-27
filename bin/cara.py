#!/bin/python3
##############################################################
## C.A.R.A
## Changelog Automation & Release Assistant
## Created by: Antonius Torode
##############################################################
## The purpose of this application/script is to provide some
## automation for updating a changelog by using the git log
## and git commit history. This app provides configuration
## in order to setup the changelog formatting and logging
## features to match various functionalities.
##############################################################


# Used for adding application parameters.
import argparse

parser = argparse.ArgumentParser(description='Changelog Automation & Release Assistant (CARA).')
parser.add_argument('-v', '--verbose',
                    required=False,
                    action='store_true',
                    help="Enables verbose mode. This will output various program data for detailed output.")
parser.add_argument('-d', '--debug',
                    required=False,
                    action='store_true',
                    help="Enables debug mode. This will output various program data for debugging.")
parser.add_argument('-c', '--config', 
                    action='store', 
                    help='The configuration file to use.')
parser.add_argument('-i', '--output', 
                    action='store', 
                    help='The input changelog to use. Use this option to overwrite/update an existing changelog.')
parser.add_argument('-o', '--output', 
                    action='store', 
                    help='The output file to use. Used this option to create a new changelog.')
args = parser.parse_args()


