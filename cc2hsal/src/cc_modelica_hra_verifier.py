# Main file for creating cc_hra_verifier. Copied from hsalRA.py
import sys
import os
import os.path
import inspect
import subprocess

# When merging controller and plant, we now use || rather than []
# Because: we need to prove some F properties; 
# Ideally, add a scheduler that gives turn to controller and plant.

# adds the current folder (where this file resides) into the path
thisfile = os.path.abspath(inspect.getfile( inspect.currentframe() ))
folder = os.path.split( thisfile )[0]
relabsrootfolder = os.path.join(folder, '..', '..')
relabsrootfolder = os.path.realpath(os.path.abspath(relabsrootfolder))
relabsfolder = os.path.join(relabsrootfolder, 'src')
relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
ccfolder = os.path.realpath(os.path.abspath(folder))
modelicafolder = os.path.join(relabsrootfolder, 'modelica2hsal', 'src')
#print folder, relabsfolder

hsalxmlpp = os.path.join(modelicafolder,'HSalXMLPP.pyc')
if os.path.isfile( hsalxmlpp ):
  os.remove( hsalxmlpp )
hsalxmlpp = os.path.join(modelicafolder,'HSalXMLPP.py')
if os.path.isfile( hsalxmlpp ):
  os.remove( hsalxmlpp )
for i in [ccfolder, relabsfolder, modelicafolder]:
    if i not in sys.path:
        sys.path.insert(0, i)
os.environ['PATH'] += '{1}{0}{1}'.format(relabsrootfolder,os.path.pathsep)    # insert for jar file
# insert modelicafolder too later and then import modelica2hsal if needed later

import HSalRelAbsCons
import cybercomposition2hsal
import modelica2hsal
from daexml2hsal import modelica2hsal_rename

#copying from install.py... will find sal here.
def findFile(basedir, filename, blacklist):
    """See if you can find filename in any directory in basedir"""
    for root, dirs, files in os.walk( basedir ):
        if filename in files:
            return os.path.join(root, filename)
        for i in blacklist:
            if i in dirs:
                dirs.remove(i)
    return None

def checkexe(filename, env_names, flags = None):
  for env_name in env_names:
    exepaths = os.environ[ env_name ].split(os.path.pathsep)
    for i in exepaths:
        exefile = os.path.join(i, filename)
        if os.path.exists(exefile):
            if flags == None:
                return exefile
            try:
                call_list = [ exefile ]
                call_list.extend( flags )
                ret_code = subprocess.call( call_list )
                return exefile
            except Exception, e:
                print 'Warning: File {0} found in PATH, but not executable.'.format(exefile)
                continue
  print 'WARNING: File {0} not found in PATH.'.format(filename)
  return None

def find_sal_exe():
    salinfbmc = 'sal-inf-bmc'
    salinfbmc_nexe = checkexe(salinfbmc, ['PATH'], flags = None)
    salinfbmc_exe = checkexe(salinfbmc, ['PATH'], flags = ['-V'])
    if salinfbmc_exe != None:
        print "Using {0}".format(salinfbmc_exe)
        return [ salinfbmc_exe ]
    iswin = sys.platform.startswith('win')	# is windows
    if not(iswin):	# not windows
        print "***SAL not found.  Download and install SAL.***"
        print "***Update PATH with location of sal-inf-bmc.***"
        return None
    cygwin = os.path.join('C:',os.path.sep,'cygwin')
    print 'Checking for cygwin at {0}'.format(cygwin)
    if os.path.isdir(cygwin):
        pass
    elif os.environ.has_key('CYGWIN_HOME'):
        cygwin = os.environ['CYGWIN_HOME']
        assert os.path.isdir(cygwin), 'CYGWIN_HOME is not a directory!!!'
    else:    
        print '***Unable to find cygwin; install cygwin and sal***'
        print '***If cygwin is not installed in the standard location c:/cygwin/, then set environment variable CYGWIN_HOME.***'
        return None
    print 'cygwin found at {0}'.format(cygwin)
    print 'searching for sal-inf-bmc...'
    if salinfbmc_nexe != None:
      salinfbmc = salinfbmc_nexe
    else:
      blacklist = ['zoneinfo','cache','locale','font','doc','include','examples','terminfo','man','lib']
      salinfbmc = findFile(cygwin, 'sal-inf-bmc', blacklist)
    if salinfbmc != None:
        print 'sal-inf-bmc found at {0}'.format(salinfbmc)
    elif os.environ.has_key('SAL_HOME'):
        salhome = os.environ['SAL_HOME']
        assert os.path.isdir(salhome), 'Env var SAL_HOME is not a directory!!!!'
        salinfbmc = os.path.join(salhome, 'bin', 'sal-inf-bmc')
        assert os.path.isfile(salinfbmc), 'SAL_HOME/bin/sal-inf-bmc NOT found!!!!'
    else:
        print '***Unable to find SAL; download and install from sal.csl.sri.com'
        print '***If installed in non-standard location, set ENV variable SAL_HOME'
        return None
    # now we have salinfbmc and cygwin both set...
    cygwinbash = os.path.join(cygwin, 'bin', 'bash.exe')
    assert os.path.isfile(cygwinbash), "ERROR: {0} not found".format(cygwinbash)
    return [cygwinbash, '-li', salinfbmc]

def get_prop_str( sal_file, prop_name ):
  '''sal_file = relevant file content as string, prop_name = string'''
  i = sal_file.find( prop_name )
  if i == -1:
    return 'Failed to get property string'
  i = sal_file.find( '|-', i )
  j = sal_file.find( ';', i )
  return sal_file[ i+2: j]

# ---------------------------------------------------------------------
# Operations on HybridSAL file -- operates on strings
# ---------------------------------------------------------------------
# from hsal filename to hsal-str
def hsal_file_to_str( hsalfilename ):
  f = open( hsalfilename, 'r' )
  hsal_model = f.read()
  f.close()
  return hsal_model

# get name of first module -- to be used as default controller
def get_first_module_name( hsal_model ):
  '''find first instance of MODULE and return its name'''
  index = hsal_model.find('MODULE')
  if index != -1:
    endindex = hsal_model.rfind( ':', 0, index )
    startindex1 = hsal_model.rfind( ';', 0, endindex ) + 1
    startindex2 = hsal_model.rfind( ' ', 0, endindex ) + 1
    startindex3 = hsal_model.rfind( 'BEGIN', 0, endindex ) + 5
    startindex = max([startindex1, startindex2, startindex3])
    modName = hsal_model[startindex:endindex].strip()
    return modName
  else:
    print 'ERROR: No MODULE in controller HybridSAL file'
    sys.exit(-1)
 
# get all properties (THEOREM) in a hsal-str
def get_props_from_hsal_str(hsal_model):
  '''get all (propertyName, moduleName) from the HybridSal file. Recall
     propertyName: THEOREM moduleName |- LTL_prop'''
  propList = []
  index = hsal_model.find("THEOREM")
  while index != -1:
    endindex = hsal_model.rfind( ':', 0, index )
    startindex = hsal_model.rfind( ';', 0, endindex )
    propName = hsal_model[startindex+1:endindex].strip()
    # Now get the moduleName
    vdashIndex = hsal_model.find( '|-', index )
    moduleName = hsal_model[index+7:vdashIndex].strip()
    # Now get the property string
    pEndIndex = hsal_model.find( ';', vdashIndex )
    propStr = hsal_model[ vdashIndex+2: pEndIndex]
    propList.append( [propName, moduleName, propStr] )
    index = hsal_model.find("THEOREM", pEndIndex)
  return propList

# get all PARAMETERS in a hsal-str
def get_params_from_hsal_str(hsal_str):
  '''get all x: REAL=val; params from the HybridSal str.'''
  paramList = []
  # parameters are between first BEGIN and first MODULE
  index = hsal_str.find("BEGIN")
  if index == -1:
    return paramList
  end_index = hsal_str.find("MODULE", index)
  if end_index == -1:
    return paramList
  index = index + 5   # End of BEGIN
  end_index -= 3      # Before : MODULE
  while index != -1 and index < end_index - 3:
    pname_end_index = hsal_str.find(":", index)
    pname = hsal_str[index+1: pname_end_index].strip()
    paramList.append( pname )
    index = hsal_str.find(";", pname_end_index)
  return paramList

# given hsal-file as str, return str of the named MODULE in it.
def get_module_str_from_hsal_file(hsal_model, modulename):
  beginIndex = hsal_model.find( modulename + ': MODULE')
  endIndex = hsal_model.find( 'END;', beginIndex)
  module_str = hsal_model[ beginIndex:endIndex ]
  return module_str

# used to get INPUT and OUTPUT from the module-string
def get_module_X_from_module_str(module_str, keyword):
  '''keyword = INPUT or OUTPUT,
     RECALL HSAL syntax -- keyword varname: typename
     return inputs-list or outputs-list, where each input/output
     is a (name, type) tuple'''
  ans = []
  index = module_str.find( keyword )
  while index != -1:
    endIndex = module_str.find( ':', index)
    varname = module_str[index+5:endIndex].strip()
    vartype = module_str[endIndex+1:endIndex+10].strip()
    ans.append( (varname, vartype) )
    index = module_str.find( keyword, endIndex )
  return ans

# given a module name, return all inputs & outputs in that module
def get_module_io_from_hsal_str(hsal_str, modulename):
  module_str = get_module_str_from_hsal_file(hsal_str, modulename)
  inputs = get_module_X_from_module_str( module_str, 'INPUT')
  outputs = get_module_X_from_module_str( module_str, 'OUTPUT')
  return (inputs, outputs)
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# usage for command-line invocation
# ---------------------------------------------------------------------
def printUsage():
    print '''
cc_modelica_hra_verifier: A Verifier for CyberComposition + 
   Modelica models; Uses HybridSal Relational Abstracter

Usage: python cc_modelica_hra_verifier.py <CC.xml> [<Modelica.xml>]  OR
       cc_modelica_hra_verifier.exe <CC.xml> [<Modelica.xml>] OR
       cc_modelica_hra_verifier.exe <Modelica.xml> [property.json]
       [--mapping file.json]


Description: This tool analyzes all LTL properties in the CC.xml model, 
 after composing the controller CC.xml with the plan Modelica.xml. 
 Specifying the plant model, Modelica.xml, is optional.
 If both controller and plant are specified, and LTL properties are
 included in the controller model, then the output is a file called 
 <CC>Modelica_sliceModelResults.txt containing the analysis results.
 If only the controller model is given, and it includes LTL properties,
 then the output is a file called <CC>Results.txt.
 If only the modelica file is given, then the output file is called
 <Modelica>ModelResults.txt
 Optional argument mapping can be used to specify the name of the
 modelicaURI2CyPhyMap file; default is modelicaURI2CyPhyMap.json.'''
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# argument checker for command line invocation
# ---------------------------------------------------------------------
def argCheck(args, printUsage):
    "args = sys.argv list"
    if '--test' in args:
        run_all_tests()
        sys.exit(0)
    if '--clean' in args:
        run_all_tests(True)
        sys.exit(0)
    if not len(args) >= 2:
        printUsage()
        sys.exit(-1)
    if args[1].startswith('-'):
        printUsage()
        sys.exit(-1)
    files = []
    for i in range(1,min(3, len(args))):
      filename = args[i]
      basename,ext = os.path.splitext(filename)
      if not(ext == '.xml') and not(ext == '.json'):
        # print 'ERROR: Unknown extension {0}; expecting .xml'.format(ext)
        # printUsage()
        # sys.exit(-1)
        continue
      if not(os.path.isfile(filename)):
        print 'ERROR: File {0} does not exist'.format(filename)
        printUsage()
        sys.exit(-1)
      files.append(filename)
    assert files[0].endswith('.xml'), 'Error: First argument should be an xml file'
    return (files[0], files[1] if len(files)>=2 else None)
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Replace values of parameters in string by values from p_map
# ---------------------------------------------------------------------
def update_param_values(hsal_model, p_map):
  '''return new hsal_model by replacing param values by new ones'''
  ans = hsal_model
  for i in p_map.keys():
    index = ans.find( i )
    if index != -1:
      index_begin = ans.find('=', index)
      index_end = ans.find( ';', index)
      # Case 1: param: TYPE = value;
      if index_begin != -1 and index_begin < index_end:
        print 'Replaced {2}: {0} by {1}'.format(ans[index_begin+1:index_end], p_map[i], i)
        ans = ans[0:index_begin+1] + ' ' + str(p_map[i]) + ans[index_end:]
      # Case 2: param: TYPE ;
      elif index_end != -1:
        ans = ans[0:index_end] + ' = ' + str(p_map[i]) + ans[index_end:]
        print 'Replaced {2}: No value by {1}'.format(ans[index_end], p_map[i], i)
      else:
        print 'Warning: Parameter declaration found but unable to replace'
    else:
      print 'Warning: Parameter {0} NOT found in SAL file'.format(i)
  return ans
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Merge two HSal files; Return value: hsalfilename, propNameList
# ---------------------------------------------------------------------
def merge_files(hsalp_str,hsalc_str,trackmap,primaryModule,pNameModLTLL,f):
  '''merge the two strings, create a new HSal file, write to f'''
  def get_content(hsal_str):
    index1 = hsal_str.find('BEGIN')
    index2 = hsal_str.rfind('END')
    return hsal_str[index1+5:index2]

  (track_map, p_map) = trackmap

  # add plant model
  hsalp_ctxt = get_content(hsalp_str)
  print >> f, hsalp_ctxt
  # Now we have plant modeled as: system = control || plant

  # add controller model
  hsalc_ctxt = get_content(hsalc_str)
  hsalc_ctxt = update_param_values(hsalc_ctxt, p_map)
  print >> f, hsalc_ctxt
  # Now we have controller+properties 
  
  # in primaryModule, rename variables as per track_map
  # finalsys: MODULE = system || (RENAME i TO track_map[i], ... IN primaryM);
  final = 'finalsys'
  system = ' '
  pre, post = '(RENAME ', 'system'
  for (k,v) in track_map.items():
    newv = modelica2hsal_rename(v)
    if hsalp_ctxt.find(newv) != -1:
      system += '{2}{0} TO {1}'.format(newv, k, pre)
      pre = ', '
      post = ' IN system)'
  system += post
  print >> f, '{2}: MODULE = {0} || {1};\n\n'.format(primaryModule, system, final)

  # Now add the properties for finalsys
  ans = []
  for i in range(len(pNameModLTLL)):
    pName = pNameModLTLL[i][0]
    pMod = pNameModLTLL[i][1]
    pLTL = pNameModLTLL[i][2]
    print >> f, ' {0}f: THEOREM\n  finalsys |- {1};\n\n'.format(pName, pLTL)
    ans.append( (pName+'f', final, pLTL) )

  return ans
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
def existsAndNew(filename1, filename2):
    if os.path.isfile(filename1) and os.path.getmtime(filename1) >= os.path.getmtime(filename2):
      print "File {0} exists and is new".format(filename1)
      return True
    return False
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Check if given filename is a SignalFlow file (controller)
# ---------------------------------------------------------------------
def check_if_controller_file( ccfilename ):
    f = open(ccfilename, 'r')
    ans, i = False, 0
    while (ans == False and i < 4):
      line = f.readline()
      if line.find('SignalFlow') != -1:
        ans = True
      i += 1
    f.close()
    return ans
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Main function called on command-line invocation
# ---------------------------------------------------------------------
def controllerplant2hsal(ccfilename, modfilename, opts):
    # convert controller to SAL
    print 'Generating controller in HybridSAL...'
    try:
      (basefilename, propNameList) = cybercomposition2hsal.cybercomposition2hsal(ccfilename, options = opts)
    except Exception, e:
      print e
      print 'ERROR: Unable to translate CyberComposition XML to HybridSal'
      return -1
    if type(basefilename) != str:
      'ERROR: cc2hsal return value type: string expected'
      return -1

    # check if cc2hsal worked properly
    hsalCfile = basefilename + '.hsal'
    if not(os.path.isfile(hsalCfile) and os.path.getsize(hsalCfile) > 100):
      print 'ERROR: Unable to translate CyberComposition XML to HybridSal. Quitting.'
      return -1
    print 'Created file {0}'.format(hsalCfile)

    # hsalCfile = name of controller file, propNameList = property Names
    # extract property name, modName, str from the hsal file
    hsalc_str = hsal_file_to_str( hsalCfile )
    pNameModLTLL = get_props_from_hsal_str(hsalc_str)

    # get the main controller module of interest
    if len(pNameModLTLL) > 0:
      primaryModule = pNameModLTLL[0][1]
    else:
      primaryModule = get_first_module_name( hsalc_str )

    # find input and output variables in that module
    (ins, outs) = get_module_io_from_hsal_str(hsalc_str, primaryModule)

    # throw away other properties
    pNameModLTLL[:] = [i for i in pNameModLTLL if i[1]==primaryModule]
    print 'Updated property list: ', pNameModLTLL

    # Now get input variable names used in the controller to be verified
    variableList = [i[0] for i in ins]	# ins = (var,type)-list
    print 'Input variables list: ', variableList

    # Now we need to get parameter names...
    paramList = get_params_from_hsal_str(hsalc_str)
    print 'Parameter list: ', paramList

    # Now run the modelica2hsal that includes the modelica_slicer...
    if modfilename != None:
      print 'Slicing the plant and creating plant in HybridSAL...'
      aa = sys.argv[3:]
      aa.extend(['--slicewrt', variableList])
      # Comment the following line for using param values from Matlab XML
      # Uncomment it for using param values from Modelica XML
      aa.extend(['--slicewrtp', paramList])
      aa.extend(['--primaryControlModule', primaryModule])
      try:
        (hsalPfile, track_map) = modelica2hsal.modelica2hsal(modfilename, pfilename=None, options=aa)
      except Exception, e:
        print e
        print 'Error: Unable to create HybridSal file from Modelica XML'
        return -1
      if not(type(hsalPfile) == str and os.path.isfile(hsalPfile) and os.path.getsize(hsalPfile) > 100):
        print 'Warning: Slice is empty.'
      # this will create outfile == 'filenameModel.hsal'

    if modfilename != None and hsalPfile != None:
      print 'Generated file {0} containing the sliced plant model'.format(hsalPfile)

      # Variables:
      # hsalPfile = plant model generated from modelica+slicer
      # hsalCfile = controller model generated from CyberCompositionXML
      # hsalc_str = hsalCfile read in as a string
      # primaryModule = name of main MODULE in controller
      # pNameModLTLL = (name, mod_name, ltl-str) for all properties
      # track_map = dict var_name_str -> var_name_str

      print 'Merging plant and controller models into single model...'

      # merge the controller and plant models
      hsalfile = basefilename + os.path.basename(hsalPfile)
      if not(existsAndNew(hsalfile, hsalPfile) and existsAndNew(hsalfile, hsalCfile)):
        hsalp_str = hsal_file_to_str( hsalPfile )
        try:
          f = open(hsalfile, 'w')
        except Exception, e:
          print 'Failed to open {0} for writing merged file'.format(hsalfile)
          return -1
        print >> f, "{0}: CONTEXT =\nBEGIN\n".format(os.path.basename(hsalfile)[:-5])
        pNameModLTLL = merge_files(hsalp_str, hsalc_str, track_map, primaryModule, pNameModLTLL, f)
        print >> f, "END"
        f.close()
        print 'Generated file {0} containing the merged model.'.format(hsalfile)
      else:
        print 'Reusing existing file {0} containing the merged model.'.format(hsalfile)
        for i in range(len(pNameModLTLL)):
          pNameModLTLL[i][0] += 'f'

      print 'Abstracting the merged model...'
    else: # modfilename == None or hsalPfile == None
      print 'No plant model to use. Assuming nondeterministic plant...'
      hsalfile = hsalCfile
      # pNameModLTLL remains unchanged

    return hsalfile, pNameModLTLL
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Given HybridSal file and properties in it, analyze and create Result.txt file
# ---------------------------------------------------------------------
def hsal2end(hsalfile, pNameModLTLL):
    # now I need to run hsal2hasal; first parse the HSal file
    try:
      xmlfilename = HSalRelAbsCons.hsal2hxml(hsalfile)
    except Exception, e:
      print e
      print 'ERROR: Failed to parse generated HybridSal file. Syntax error in generated HybridSal file. Quitting.'
      return -1
    if not(type(xmlfilename) == str and os.path.isfile(xmlfilename) and os.path.getsize(xmlfilename) > 100):
      print 'ERROR: Failed to parse HybridSal file. Quitting.'
      return -1

    # Now relationally abstract hsal to sal
    try:
      ans_prop_exists = HSalRelAbsCons.hxml2sal(xmlfilename, optarg=0, timearg=None, ptf=False)
    except Exception, e:
      print e
      print 'ERROR: Relational abstracter can not abstract this model. Quitting.'
      return -1
    if not isinstance(ans_prop_exists, tuple):
      print 'ERROR: Relational abstracter failed to abstract this model. Quitting.'
      return -1
    (ans, prop_exists) = ans_prop_exists
    if not(type(ans) == str and os.path.isfile(ans) and os.path.getsize(ans) > 100):
      print 'ERROR: Failed to abstract HybridSal model into a SAL model. Quitting.'
      return -1

    print 'Relational abstraction successfully created {0}'.format(ans)

    # Now ready to run sal-inf-bmc 
    if prop_exists:
      print 'Model checking the properties...'
      salinfbmcexe = find_sal_exe()
      if salinfbmcexe == None:
        print 'ERROR: Failed to find sal-inf-bmc. Ensure SAL is installed.'
        return -1
      hsal_file_path = os.path.abspath(ans) 
      (basename,ext) = os.path.splitext(hsal_file_path)
      result_filename = basename + 'Result.txt'
      hsal_file_path = hsal_file_path.replace('\\', '/')
      hsal_file_path = hsal_file_path.replace('C:', '/cygdrive/c')
      try:
        f = open(result_filename, 'w')
      except Exception, e:
        print 'Failed to open file {0} for writing results'.format(result_filename)
        return -1
      #os.environ['SALCONTEXTPATH'] = hsal_file_path + ':' + oldpath 
      #print 'SALCONTEXTPATH = ', os.environ['SALCONTEXTPATH']

      # just get to the place in file where there are properties
      '''hsal_str = ''
      with open(hsalfile, 'r') as hsal_fp:
        old_pos = hsal_fp.tell()
        line_str = hsal_fp.readline()
        while line_str != '' and line_str.find('THEOREM') == -1:
          old_pos = hsal_fp.tell()
          line_str = hsal_fp.readline()
        # and get the file contents from that point on--optimization
        if line_str != '':  # if there are properties
          hsal_fp.seek( old_pos )
          hsal_str = hsal_fp.read()
      # hsal_str = contains all the properties...

      # for each property, run sal-inf-bmc and collect result in file f
      for p1 in propNameList:
        print >> f, 'PropertyName: {0}'.format(p1)
        print >> f, 'PropertyStr: {0}'.format(get_prop_str(hsal_str,p1))
        f.flush()
        cmd = list(salinfbmcexe)
        cmd.extend(["-d", "10", hsal_file_path, pName])
        retCode = subprocess.call( cmd, env=os.environ, stdout=f)
        f.flush()
        if retCode != 0:
          print "sal-inf-bmc failed."
          return -1
        print >> f, '~~~~~~~~~~'
        f.flush()
      f.close()
      #print 'NOTE: Download and install SAL from sal.csl.sri.com'
      '''

      # Now we have the properties and its LTL text 
      for i in range(len(pNameModLTLL)):
        pName = pNameModLTLL[i][0]
        pMod = pNameModLTLL[i][1]
        LTL = pNameModLTLL[i][2]
        print >> f, 'PropertyName: {0}'.format(pName)
        print >> f, 'PropertyStr: {0}'.format(LTL)
        f.flush()
        cmd = list(salinfbmcexe)
        cmd.extend(["-d", "10", hsal_file_path, pName])
        retCode = subprocess.call( cmd, env=os.environ, stdout=f)
        f.flush()
        if retCode != 0:
          print "sal-inf-bmc failed."
          return -1
        print >> f, '~~~~~~~~~~'
        f.flush()

      f.close()
      print 'Generated file {0} containing the verification results'.format(result_filename)

    else: 	# if prop_exists is false
      print 'No LTL properties were provided'
      print 'For verifying the model, add a property either in the Matlab model or in the translated SAL file directly'
      print 'Then, Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> <propertyName added in generated SAL file>'
      return -1
    return 0
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
def plant2hsal(modfilename, propfilename, opts):
    print 'No controller found. Converting plant model to HybridSAL...'
    try:
      (hsalPfile, track_map) = modelica2hsal.modelica2hsal(modfilename, pfilename=propfilename, options=opts)
    except Exception, e:
      print e
      print 'Error: Unable to create HybridSal file from Modelica XML'
      return -1
    if not(type(hsalPfile) == str and os.path.isfile(hsalPfile) and os.path.getsize(hsalPfile) > 100):
        print 'Warning: Generated HybridSal file is empty.'
      # this will create outfile == 'filenameModel.hsal'

    if modfilename != None and hsalPfile != None:
      print 'Generated file {0} containing the plant model'.format(hsalPfile)
  
    hsalp_str = hsal_file_to_str( hsalPfile )
    pNameModLTLL = get_props_from_hsal_str(hsalp_str)

    return hsalPfile, pNameModLTLL
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
# Main function called on command-line invocation
# ---------------------------------------------------------------------
def main():
    def getexe():
      folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
      relabsfolder = os.path.join(folder, '..', '..', 'bin')
      relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
      return relabsfolder

    # get controller-filename and modelica-filename from argv
    (ccfilename, modfilename) = argCheck(sys.argv, printUsage)

    ccfile_exists = check_if_controller_file(ccfilename)

    if ccfile_exists:
      hsalfile, pNameModLTLL = controllerplant2hsal(ccfilename, modfilename, sys.argv[2:])
    else:
      propfilename = modfilename
      hsalfile, pNameModLTLL = plant2hsal(ccfilename, propfilename, sys.argv[2:])

    # convert controller to SAL
    return hsal2end(hsalfile, pNameModLTLL)
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
def run_all_tests(cleanonly=False):
    def clean(i,j):
      del_if_exists( i+'.hsal' )
      del_if_exists( j+'_slice.xml' )
      del_if_exists( j+'_slice.daexml' )
      del_if_exists( j+'_slice.daexml1' )
      del_if_exists( j+'_slice.daexml2' )
      del_if_exists( j+'_slice.daexml3' )
      del_if_exists( j+'_slice.daexml4' )
      del_if_exists( j+'_sliceModel.hsal' )
      del_if_exists( i+j+'_sliceModel.hsal' )
      del_if_exists( i+j+'_sliceModel.hxml' )
      del_if_exists( i+j+'_sliceModel.sal' )
    def del_if_exists(f):
      dirs = ['cc2hsal/examples/', 'modelica2hsal/examples/']
      for d in dirs:
        if os.path.isfile( d+f ):
          os.remove( d+f )
    print 'Running all tests...'
    test_files = [('SimplifiedShiftControllerDecl','SDT_OM_Cyber_dss','modelicaURI2CyPhyMap.json')]
    test_files.append( ('TorqueConverterDecl', 'SDT_OM_Cyber_dss','modelicaURI2CyPhyMap.json') )
    test_files.append( ('TorqueReductionSignalDecl', 'SDT_OM_Cyber_dss','modelicaURI2CyPhyMap.json') )
    test_files.append(('SimplifiedShiftControllerDeclold','sdt_om_cyber_dss_old','sdt_om_cyber_dss_old.json'))
    test_files.append(('SimplifiedControllersCyber_before','SystemDesignTest_r663','modelicaURI2CyPhyMap_r663.json'))
    for (i,j,k) in test_files:   
      clean(i,j)
      cmd = [ "python", "cc2hsal/src/cc_modelica_hra_verifier.py" ]
      cmd.append( 'cc2hsal/examples/' + i+'.xml')
      cmd.append( 'modelica2hsal/examples/' + j+'.xml')
      cmd.extend( ['--mapping', k] )
      if cleanonly==False:
        print '------------------------------------------------'
        print cmd
        subprocess.call( cmd )
        clean(i,j)
        print '------------------------------------------------'
# ---------------------------------------------------------------------

# ---------------------------------------------------------------------
if __name__ == "__main__":
    ret_code = main()
    os._exit(ret_code)
    #sys.exit(ret_code)
# ---------------------------------------------------------------------

