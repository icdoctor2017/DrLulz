# -*- coding: utf-8 -*-

import re
import os
import csv
import glob
import string
from Tkinter import Tk
from cStringIO import StringIO
from tkFileDialog import askdirectory
from pyth.plugins.rtf15.reader import Rtf15Reader



def decode_cell(cell):
    '''The cell matched so lets handle it'''
    
    # variable that will hold the converted text
    temp_cell = []
    
    # pyth checks for the rtf syntax before processing, so 'unicode_escape' escapes the '\' so pyth doesn't complain
    cell_encode = re.sub(r'\\u|\\\\u|\\N|\\\\N', ' ', cell)
    cell_encode = cell_encode.decode('unicode_escape')
    cell_encode = filter(lambda x: x in string.printable, cell_encode)
    cell_rtf = Rtf15Reader.read(StringIO(cell_encode))

    # turn the pyth object into readable text
    cell_txt = [x.content for x in cell_rtf.content]
    
    # iterate and extract the pyth object text into temp_cell
    for line in cell_txt:
        for l in line:
            temp_cell.append(l.content)
                
    
    # combine and join the extracted text into one string (for one cell)
    combined = [i for sub in temp_cell for i in sub]
    new_cell =  ' '.join(combined)
    
    # the non-ascii characters in your file were followed by _ so i removed them for cleanliness
    # uncomment to keep the _
    new_cell = re.sub('_', '', new_cell)
    
    # remove extra whitespace and return the converted cell
    # remove L at end of string
    return ' '.join(new_cell[:-1].split())



def find_rtf(row):
    '''Start looking for rtf syntax'''
    
    # variable that will return the row to writer
    temp_row = []
    
    # loop and index each cell in row
    for n, cell in enumerate(row):
        
        # your csv is shitty
        if type(cell) == str:
            cell = unicode(cell, "utf-8", errors="ignore")
        else:
            cell = unicode(cell)

        # if the cell text starts with {\\rtf we need to know
        if re.match(r'^{\\\\rtf', cell):
            
            # holder
            combined = []
            
            # collect all cells following matched cell
            for item in row[n:]:
                combined.append(item)
            
            # combine the rest of the row
            cell = ' '.join(combined)
            
            # send off to convert rtf
            cell_matched = decode_cell(cell)
            
            # add the cell, with converted rtf, back to the row
            temp_row.append(cell_matched.encode('ascii', 'ignore'))
            
            # we dont want to process further cells because they're now combined
            # break the loop to start at next row
            break

        else:
            # if the cell didn't have rtf just add it back to the row
            temp_row.append(cell.encode('ascii', 'ignore'))
            
    return temp_row



def open_csv(f_ori, f_new):
    '''Open original file, process, and save to new file'''

    # 'rU' = read 'r' and open with 'U' so the newlines inside the cell are respected
    # 'wb' = write 'w' in binary 'b' mode
    # 'with open' automatically closes the file
    with open(f_ori, 'rU') as file1, open(f_new, 'wb') as file2:
    
        reader = csv.reader(file1)
        writer = csv.writer(file2)
        
        # loop through rows in the opened csv
        for row in reader:
            
            # send to fx to look for rtf syntax
            new_row = find_rtf(row)
            
            # write the row to new file
            writer.writerow(new_row)



def add_suffix(f_ori):
    '''Append suffix to original file name'''
    
    suffix = '-processed'
    
    # explode full path into path, name, ext
    path, name = os.path.split(f_ori)
    name, ext = os.path.splitext(name)
    
    # function to append suffix
    mk_suffix = lambda i: os.path.join(path, '%s%s%s' % (name, i, ext))
    
    # process and return
    return mk_suffix(suffix)



def iterate_dir(path):
    '''Iterate files in selected dir and filter out .csv'''

    extension = '/*.csv'
    select = path + extension
    
    for i in glob.iglob(select):
        # create unique name for new file
        # send to opener
        open_csv(i, add_suffix(i))
            
            

def main():
    '''Initiate script and select directory to process'''
    
    ini_path = os.path.expanduser('~/Desktop')
    
    OPEN_OPTIONS = dict(
                        # specify root folder for ui
                        # uncomment initialdir entirely to remember last dir
                        #initialdir='/Users',
                        initialdir=ini_path,
                        title='Select Directory'
                        )

    Tk().withdraw()
    ask_path = askdirectory(**OPEN_OPTIONS)

    # move to fx
    iterate_dir(ask_path)



if __name__ == "__main__":
    main()
