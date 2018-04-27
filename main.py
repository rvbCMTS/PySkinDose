import argparse
from dose import skin_dose
import os
import sys

parser = argparse.ArgumentParser()

parser.add_argument('--file-path', help='Path to RDSR DICOM file to parse')
parser.add_argument('--verbose', help='Print logs to terminal')
parser.add_argument('--print-dose', help='Print the result to the terminal')
parser.add_argument('--save2db', help='Save the result to database (NOT YET IMPLEMENTED)')

args = parser.parse_args()

if not args.file_path:
    sys.exit('File path parameter missing')
elif not os.path.isfile(args.file_path):
    sys.exit('The give path does not lead to a file')

result = skin_dose(args.file_path, print_result=args.print_dose, verbose=args.verbose, save2db=args.save2db)
