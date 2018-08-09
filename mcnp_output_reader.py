"""
Reads MCNP output file
"""

import matplotlib
import matplotlib.pyplot as plt
import datetime
import sys
import argparse
import logging
import numpy as np


class MCNPOutput():
    """ MCNP output data"""
    def __init__(self):
        """ define data"""
        self.file_name = ""
        self.version = ""
        self.date = ""
        self.start_time = ""
        self.cell_mass_volume = []
        self.surface_area = []
        self.num_tallies = 1
        self.num_rendevous = 1
        self.tally_data = []
        self.summary_data = []
        self.tfc_data = []
        

class MCNP_tally_data():
    """ data for an individual tally """
    def __init__(self):
        self.number = 1
        self.type = 1
        self.particle = "neutron"
        self.nps = 1 
        # for type 1 or 2
        self.surfaces = None
        self.areas = None
        # for type 4
        self.cells = None
        self.vols = None
        # for type 5 tallies
        self.x = None
        self.y = None
        self.z = None
        self.cell_scores = None
        self.uncoll_flux = None
        self.uncoll_err = None
        # for type 6
        # for type 8
        # general
        self.result = []
        self.err = []
        self.eng = []
        self.stat_tests = None




class MCNP_summary_data():
    """ data for an individual tally """
    def __init__(self):
        self.number = 1
        self.type = 1


def write_lines(path, lines):
    f = open(path, 'w')
    for l in lines:
        f.write(l)
        f.write("\n")
    f.close()


def get_lines(path):
    """ reads file at path and returns a list with 1 entry per line """
    with open(path) as f:
        lines = f.read().splitlines()
    f.close()
    return lines


def find_line(text, lines, num):
    """finds a index of the line in lines where the text is present in
       the first num characters
    """
    i = 0
    for l in lines:
        i = i + 1
        if l[0:num] == text:
            return i - 1
    # TODO: add a catch if it doesnt find any match

def get_version(data):
    """ """
    return 1


def get_cell_mass(data):
    """ """
    return 1


def get_surface_area(data):
    """ """
    return 1


def get_num_tallies(data):
    """ """
    return 1


def get_num_rendevous(data):
    """ """
    return 1


def get_summary(data, ptype, rnum):
    """ """
    return 1


def get_tally(lines, tnum, rnum=-1):
     """reads the lines and extracts the  tally results"""
     
     tally_data = MCNP_tally_data()
     tally_data.number = tnum

     # todo add ability to do all rendevous
     # reduce to only the final result set
     term_line = find_line("      run terminated when", lines, 25)
     lines = lines[term_line:]

     # reduce to only the tally results section
     fline = "1tally" + ((9-len(str(tnum)))*" ")
     res_start_line = find_line(fline + str(tnum), lines, 15)
     # add an error catch

     tally_data.particle = lines[res_start_line+2][24:33]
     tally_data.nps = lines[res_start_line][28:40]
     tally_data.type = lines[res_start_line + 1][22]
     
     lines = lines[res_start_line + 1:]
     tal_end_line = find_line("1tally", lines, 6)
     lines = lines[:tal_end_line-1]

     if logging.getLogger().getEffectiveLevel() == 10:
         logging.debug("writing tally_test.txt")
         write_lines("tally_test.txt", lines) 

     # debug 
     logging.info('Reading tally %s', str(tnum))
     logging.debug('Run term line number: %s', str(term_line))
     logging.debug('Result start line number: %s', str(res_start_line))
     logging.debug('tally end line number: %s', str(tal_end_line))
     logging.debug(tally_data.particle)
     logging.debug('tally nps: %s', str(tally_data.nps))
     logging.debug('tally type: %s', str(tally_data.type))
    

     # depending on tally type choose what to do now
     if tally_data.type == "4" or tally_data.type == "6":
         logging.debug("volume")
         tally_data.vols = []
         tally_data.cells = []
         # find cells
         # find volumes
         # TODO: if more than a single line of vols or cells
         vol_line_id = find_line("           volumes ", lines, 19)
         vol_val_line = lines[vol_line_id + 2]
         vol_val_line = " ".join(vol_val_line.split())
         tally_data.vols = vol_val_line.split(" ")
         cell_val_line = lines[vol_line_id + 1]
         cell_val_line = " ".join(cell_val_line.split())
         cell_val_line = cell_val_line.split(":")[1]
         tally_data.cells = cell_val_line.split(" ")[1:]

         # loop for each cell
         for cell in tally_data.cells:
             cline = " cell  " 
             cell_res_start = find_line(cline + cell, lines, len(cell)+len(cline))
             if lines[cell_res_start + 1] == "      energy   ":
                 logging.debug("noticed energy")
                 loc_line_id2=find_line("      total    ", lines[cell_res_start + 1:], 15)
                 erg_lines = lines[cell_res_start + 2:cell_res_start + 1 + loc_line_id2]
                 for l in erg_lines:
                     l=l.strip()
                     l=l.split(" ")
                     tally_data.eng.append(float(l[0]))
                     tally_data.result.append(float(l[3]))
                     tally_data.err.append(float(l[4]))
             else:
                 data_line = lines[cell_res_start + 1]
                 data_line = " ".join(data_line.split())
                 data_line = data_line.split(" ")
                 tally_data.result.append(data_line[0])
                 tally_data.err.append(data_line[1])


       
     elif tally_data.type == "5":
         logging.debug("type 5")

         # read detector position
         loc_line_id=find_line(" detector located", lines, 17)
         loc_line = lines[loc_line_id]
         loc_line = loc_line.split("=")[1]
         loc_line = loc_line.split(" ")
         tally_data.x = loc_line[1]
         tally_data.y = loc_line[2]
         tally_data.z = loc_line[3]
         res_line = lines[loc_line_id + 1]

         # check if energy dependant
         if res_line == "      energy   ":
             logging.debug("energy dependant")
             loc_line_id2=find_line(" detector located", lines[loc_line_id+1:], 17)
             erg_lines = lines[loc_line_id + 2:loc_line_id + loc_line_id2-1]
             for l in erg_lines:
                 l=l.strip()
                 l=l.split(" ")
                 tally_data.eng.append(float(l[0]))
                 tally_data.result.append(float(l[3]))
                 tally_data.err.append(float(l[4]))
             
         else:
             res_line = res_line.split(" ")[-2:]
             tally_data.result.append(res_line[0])
             tally_data.err.append(res_line[1])

     elif tally_data.type == "1" or tally_data.type == "2":
         logging.debug("surface")
         tally_data.areas = []
         tally_data.surfaces = []

         # TODO: if more than a single line of surfaces or areas
         # find areas
         area_line_id = find_line("           areas", lines, 16)
         area_val_line = lines[area_line_id + 2]
         area_val_line = " ".join(area_val_line.split())
         tally_data.areas = np.asarray(area_val_line.split(" "))
         # find surfaces
         suf_val_line = lines[area_line_id + 1]
         suf_val_line = " ".join(suf_val_line.split())
         suf_val_line = suf_val_line.split(":")[1]
         tally_data.surfaces = suf_val_line.split(" ")[1:]
         logging.debug(tally_data.areas)
         logging.debug(tally_data.surfaces)

         first_surface_line_id = find_line(" surface ", lines, 9)
         if lines[first_surface_line_id +1] == "      energy   ":
             logging.debug("energy bins")
             first_tot_line_id = find_line("      total  ", lines[first_surface_line_id:], 13)
             erg_lines = lines[first_surface_line_id+2:first_surface_line_id+first_tot_line_id]
             for l in erg_lines:
                 l = l.strip()
                 l = l.split(" ")
                 tally_data.eng.append(float(l[0]))
                 tally_data.result.append(float(l[3]))
                 tally_data.err.append(float(l[4]))
             logging.debug(tally_data.eng)
             logging.debug(tally_data.result)
             logging.debug(tally_data.err)
         else:
             logging.debug("no energy bins")

     elif tally_data.type == "8":
         logging.debug("pulse height tally")

     # get statistical test outcomes
     stat_res_line_id = find_line(" passed", lines, 7)
     stat_line = lines[stat_res_line_id]
     stat_line = stat_line.strip()
     stat_line = " ".join(stat_line.split())
     stat_line = stat_line.split(" ")[1:]
     tally_data.stat_tests = stat_line
    

     return tally_data


def read_output_file(path, tnum):
    """ """
    logging.info('Reading MCNP output file: %s', path)
    ofile_data = get_lines(path)
    mc_data = MCNPOutput()

    td1 = get_tally(ofile_data, tnum) # temporary remove later
    return td1


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Read MCNP output file")
    parser.add_argument("input", help="path to the output file")
    args = parser.parse_args()

    read_output_file(args.input)
