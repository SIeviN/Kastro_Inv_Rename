# Author:      Michael Koch
# Date:        2022/04/04
# Description: Reads file names passed at the command-line, searches
#              the file for a customer name, then prepends the customer
#              name to the beginning of the filename
# Usage:       python3 cust_invoice_rename.py file_name(s)
#              or
#              cust_invoice_rename.exe file_name(s)


#Tested and Working Scenarios:
#python3 cust_invoice_rename.py CustomerInv-Schmeiding-Customer-13599435607.xml CustomerInv-Schmieding-Customer-13606328543.xml CustomerInv-Schmeiding-Customer-13573664773.xml CustomerInv-Schmeiding-Customer-13598960261.xml
#python3 cust_invoice_rename.py CustomerInv-Schmeiding-Customer-13599435607.xml
#python3 cust_invoice_rename.py New_folder\invoices\cust\*.xml
#python3 cust_invoice_rename.py New_folder/invoices/cust/*.xml
#python3 ../cust_invoice_rename.py ..\New_folder\invoices\cust\*.xml
#python3 ..\cust_invoice_rename.py ../New_folder/invoices/cust/*.xml
#python3 cust_invoice_rename.py New_folder\invoices\cust\Cust*.xml
#python3 cust_invoice_rename.py New_folder/invoices/cust/*


import argparse, os, ntpath, fnmatch
from pathlib import Path, PureWindowsPath

CUST_ACCT_SEARCH_STR = "Customer Acct Number"
END_SEEK_MARKER      = "</ReferenceNumbers>"

def resolve_windows_path(args, path):
    '''
    Parameters: args (Namespace) - arguments to use
                path (str) - the path passed from commandline
    '''
    # get infor from path lib to search for later
    file_info = Path(path)
    
    # build what we will look for using fnmatch, so I don't have to do regex
    match_search_info = f"{file_info.stem}{file_info.suffix}"

    # take the path provided and strip the extension
    corrected_path = path.replace(match_search_info, "")

    # if a wild card is used on the current directory, then make the path the current directory
    if corrected_path == "":
        corrected_path = "."
    
    if args.verbose:
        print(f"Seaching {corrected_path}")
    
    files = list()
    # create a list of the file names
    for f in os.listdir(corrected_path):
        if (fnmatch.fnmatch(f, match_search_info)):
            if args.verbose:
                print(f"Appending {f} to list to process")
            files.append(f"{corrected_path}{f}")
    
    return files

def read_cli():
    '''
    Parameters: None
    Actions: Parses commandline arguments
    Returns: parsed arguments (Namespace)
    '''
    parser = argparse.ArgumentParser(description='Process and rename Invoice files')
    parser.add_argument('files', metavar='N', type=str, nargs='*', help='XML files to parse and rename')
    parser.add_argument('--verbose', "-v", action='store_true', help='verbose output')
    args = parser.parse_args()
    if (len(args.files) <= 0):
        print("No files passed at command-line\nExiting -1")
        exit(-1)
    # if a wild-card is used, we need to process
    if ((len(args.files) == 1) and ( '*' in args.files[0])):
        args.files = resolve_windows_path(args, args.files[0])
    return args

def file_load_and_search(args, fn):
    '''
    Parameters: args (Namespace) - arguments to use
                fn (str) - the file name to open and read
    Actions: opens and reads the contents of 
    Returns: the customer name (str)
    '''
    cust_name = ""
    try:
        with open(fn, 'r') as infile:
            data = infile.readline()
            while data:
                # restrict searching as to not waste time
                if END_SEEK_MARKER in data:
                    if (args.verbose):
                        print(f"reached {END_SEEK_MARKER} without finding customer name")
                        break
                # if we find the line with the customer name in it, break
                if CUST_ACCT_SEARCH_STR in data:
                    # easy parsing since its XML, the text needed is between tags
                    cust_name = data.split(">")[1].split("<")[0]
                    break
                data = infile.readline()
    except:
        if (args.verbose):
            print(f"bad filename {fn}, skipping")
    if (args.verbose):
        print(f"Customer Name Found: {cust_name}")
    return cust_name

def file_rename(args, fn, name):
    '''
    Parameters: args (Namespace) - arguments to use
                fn (str) - the filename to change
                name (str) - the name to prepend to the filename
    Actions: renames the file
    Returns: None
    '''
    # do not rename and return early if the customer name already is in the filename
    if (name in fn):
        if (args.verbose):
            print(f"Customer name already in filename, skipping {fn}")
        return
    
    # rename the file
    f_info = Path(fn)
    f_info.rename(Path(f_info.parent, f"{name}_{f_info.stem}{f_info.suffix}"))
    
    if (args.verbose):
        print(f"new file name = {name}_{f_info.stem}{f_info.suffix}")
    return

# =========== MAIN ===========
if __name__ == "__main__":
    args = read_cli()
    
    # print out files to be renamed
    if (args.verbose):
        print("\nFiles to be parsed:")
        for i in range(0,len(args.files)):
            print(f"\t{args.files[i]}")
    
    # loop through the file names
    for fn in args.files:
        cust_name = file_load_and_search(args, fn)
        if (cust_name == ""):
            if (args.verbose):
                print(f"No customer information read from file {fn}")
            continue
        # rename the file with the found customer name
        file_rename(args, fn, cust_name)
    
    if (args.verbose):
        print("Completed, Exiting")
    exit(0)
