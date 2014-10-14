import sys
import os
import os.path
import inspect
import subprocess

# adds the current folder (where this file resides) into the path
folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
relabsfolder = os.path.join(folder, '..', '..', 'src')
relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
folder = os.path.realpath(os.path.abspath(folder))
for i in [folder, relabsfolder]:
    if i not in sys.path:
        sys.path.insert(0, i)

import modelica2hsal
import HSalRelAbsCons

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

def printUsage():
    print '''
modelica2sal -- a converter from Modelica to Sal

Usage: python modelica2sal.py <modelica_file.xml> [<context_property.xml>] [--addTime]

Description: This will create a file called modelica_fileModel.sal
    '''

def main():
    def getexe():
        folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
        relabsfolder = os.path.join(folder, '..', '..', 'bin')
        relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
        return relabsfolder
    global dom
    (filename, pfilename) = modelica2hsal.argCheck(sys.argv, printUsage)
    try:
        (outfile,trk_map) = modelica2hsal.modelica2hsal(filename, pfilename, options = sys.argv[1:])
    except Exception, e:
        print e
        print 'Error: Unable to create HybridSal file from Modelica XML'
        return -1
    if not(type(outfile) == str and os.path.isfile(outfile) and os.path.getsize(outfile) > 100):
        print 'Error: Translation from Modelica to HybridSal failed. Quitting.'
        return -1
    # this will create outfile == 'filenameModel.hsal'
    # now I need to run hsal2hasal
    try:
        xmlfilename = HSalRelAbsCons.hsal2hxml(outfile)
    except Exception, e:
        print e
        print 'Syntax error in generated HybridSal file. Quitting.'
        return -1
    if not(type(xmlfilename) == str and os.path.isfile(xmlfilename) and os.path.getsize(xmlfilename) > 100):
        print 'Error: Failed to parse HybridSal file. Quitting.'
        return -1
    try:
        ans, prop_exists = HSalRelAbsCons.hxml2sal(xmlfilename, optarg=0, timearg=None)
    except Exception, e:
        print e
        print 'Relational abstracter can not abstract this model. Quitting.'
        return -1
    if not(type(ans) == str and os.path.isfile(ans) and os.path.getsize(ans) > 100):
        print 'Error: Failed to abstract HybridSal model into a SAL model. Quitting.'
        return -1
    iswin = sys.platform.startswith('win')
    # if pfilename != None:
    if prop_exists:
        salinfbmcexe = find_sal_exe()
        if salinfbmcexe == None:
            print 'ERROR: Failed to find sal-inf-bmc'
            return -1
        # change directory to where the sal file was created...
        #if os.environ.has_key('SALCONTEXTPATH'):
            #oldpath = os.environ['SALCONTEXTPATH']
        #else:
            #oldpath = '.'
        hsal_file_path = os.path.abspath(ans) 
        (basename,ext) = os.path.splitext(hsal_file_path)
        result_filename = basename + 'Result.txt'
        hsal_file_path = hsal_file_path.replace('\\', '/')
        hsal_file_path = hsal_file_path.replace('C:', '/cygdrive/c')
        try:
          f = open(result_filename, 'w')
        except Exception, e:
          print 'Failed to open file {0} for writing results'.format(result_filename)
          print 'Results will be displaced on stdout'
          f = sys.stdout
        #hsal_file_path = hsal_file_path.replace('C:', '/c/')
        #os.environ['SALCONTEXTPATH'] = hsal_file_path + ':' + oldpath 
        #print 'SALCONTEXTPATH = ', os.environ['SALCONTEXTPATH']
        salinfbmcexe.extend(["-d", "4", hsal_file_path, "p1"])
        retCode = subprocess.call(salinfbmcexe, env=os.environ, stdout=f)
        if retCode != 0:
            print "sal-inf-bmc failed."
            return -1
        #print 'You can now run sal-inf-bmc on the generated SAL file'
        #print 'Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> p1'
        #print 'NOTE: The requirement is called p1 in the generated SAL file'
        #print 'NOTE: Use sal-inf-bmc --help for more information'
        #print 'NOTE: Download and install SAL from sal.csl.sri.com'
    else:
        print 'No property-context file was provided'
        print 'For verifying the model, add a property in the generated SAL file'
        print 'Then, Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> <propertyName added in generated SAL file>'
        return -1
    return 0

if __name__ == "__main__":
    ret_code = main()
    sys.exit( ret_code )

