# This file is part of the util module of the MDTF code package (see mdtf/MDTF_v2.0/LICENSE.txt)

import os
import sys


def get_available_programs(verbose=0):
   return {'py': 'python', 'ncl': 'ncl'}
   #return {'py': sys.executable, 'ncl': 'ncl'}  

def makefilepath(varname,timefreq,casename,datadir):
    """ 
    USAGE (varname, timefreq, casename, datadir )
       str varname  (as set by var_code/util/set_variables_*.py)
       str timefreq "mon","day","6hr","3hr","1hr"
       str datadir directory where model data lives

    """
    return datadir+"/"+timefreq+"/"+casename+"."+varname+"."+timefreq+".nc"

def setenv(varname,varvalue,env_dict,verbose=0,overwrite=True):
   # env_dict: a dictionary to be dumped once file is created
   # This is a wrapper to os.environ so any new env vars 
   # automatically get written to the file
   
   if (not overwrite) and (varname in env_dict): 
      if (verbose > 0): print "Not overwriting ENV ",varname," = ",env_dict[varname]
   else:
      if ('varname' in env_dict) and (env_dict[varname] != varvalue) and (verbose > 0): 
         print "WARNING: setenv ",varname," = ",varvalue," overriding previous setting ",env_dict[varname]
      env_dict[varname] = varvalue

      # environment variables must be strings
      if type(varvalue) is bool:
         if varvalue == True:
            varvalue = '1'
         else:
            varvalue = '0'
      elif type(varvalue) is not str:
         varvalue = str(varvalue)
      os.environ[varname] = varvalue

      if (verbose > 0): print "ENV ",varname," = ",env_dict[varname]
   if ( verbose > 2) : print "Check ",varname," ",env_dict[varname]


def translate_varname(varname_in,verbose=0):
   func_name = " translate_varname "
   if ( verbose > 2): print func_name+" read in varname: ",varname_in
   if ( varname_in in os.environ ):
      varname = os.environ[varname_in]  #gets variable name as imported by set_variables_$modeltype.py
      if ( verbose > 1): print func_name+" found varname: ",varname
   else: 
      varname = varname_in
      if ( verbose > 1): print func_name+"WARNING: didn't find ",varname, " in environment vars, not substituting"
      #      print "To do: Modify read_files.main to accept argument of model type and import"
   if ( verbose > 2): print func_name + "returning ",varname
   return varname



