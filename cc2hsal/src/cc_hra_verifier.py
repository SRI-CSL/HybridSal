# Main file for creating cc_hra_verifier. Copied from hsalRA.py
import sys
import os
import os.path
import inspect
import subprocess

# adds the current folder (where this file resides) into the path
folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
relabsrootfolder = os.path.join(folder, '..', '..')
relabsrootfolder = os.path.realpath(os.path.abspath(relabsrootfolder))
relabsfolder = os.path.join(relabsrootfolder, 'src')
relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
folder = os.path.realpath(os.path.abspath(folder))
#print folder, relabsfolder
for i in [folder, relabsfolder]:
    if i not in sys.path:
        sys.path.insert(0, i)
os.environ['PATH'] += '{1}{0}{1}'.format(relabsrootfolder,os.path.pathsep)    # insert for jar file
# insert modelicafolder too later and then import modelica2hsal if needed later

import HSalRelAbsCons
import cybercomposition2hsal

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

def printUsage():
    print '''
cc_hra_verifier: A Verifier for CyberComposition models 
                 Uses HybridSal Relational Abstracter

Usage: python cc_hra_verifier.py <CC.xml> 
       cc_hra_verifier.exe <CC.xml>

Description: This will analyze all LTL properties in the CC.xml model, and
 create a file called CCResults.txt containing the analysis results.'''

def main():
    def getexe():
        folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
        relabsfolder = os.path.join(folder, '..', '..', 'bin')
        relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
        return relabsfolder
    global dom
    filename = cybercomposition2hsal.argCheck(sys.argv, printUsage)
    try:
        (basefilename, propNameList) = cybercomposition2hsal.cybercomposition2hsal(filename, options = sys.argv[1:])
    except Exception, e:
        print e
        print 'ERROR: Unable to translate CyberComposition XML to HybridSal'
        return -1
    assert type(basefilename) == str, 'ERROR: cc2hsal return value type: string expected'
    hsalfile = basefilename + '.hsal'
    if not(os.path.isfile(hsalfile) and os.path.getsize(hsalfile) > 100):
        print 'ERROR: Unable to translate CyberComposition XML to HybridSal. Quitting.'
        return -1
    # now I need to run hsal2hasal
    try:
        xmlfilename = HSalRelAbsCons.hsal2hxml(hsalfile)
    except Exception, e:
        print e
        print 'ERROR: Failed to parse generated HybridSal file. Syntax error in generated HybridSal file. Quitting.'
        return -1
    if not(type(xmlfilename) == str and os.path.isfile(xmlfilename) and os.path.getsize(xmlfilename) > 100):
        print 'ERROR: Failed to parse HybridSal file. Quitting.'
        return -1
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
    # iswin = sys.platform.startswith('win')
    # if pfilename != None:
    if prop_exists:
        salinfbmcexe = find_sal_exe()
        if salinfbmcexe == None:
            print 'ERROR: Failed to find sal-inf-bmc. Ensure SAL is installed.'
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
          return -1
          #print 'Results will be displaced on stdout'
          #f = sys.stdout
        #hsal_file_path = hsal_file_path.replace('C:', '/c/')
        #os.environ['SALCONTEXTPATH'] = hsal_file_path + ':' + oldpath 
        #print 'SALCONTEXTPATH = ', os.environ['SALCONTEXTPATH']
        for p1 in propNameList:
          print >> f, 'PropertyName: {0}'.format(p1)
          f.flush()
          cmd = list(salinfbmcexe)
          cmd.extend(["-d", "10", hsal_file_path, p1])
          retCode = subprocess.call( cmd, env=os.environ, stdout=f)
          f.flush()
          if retCode != 0:
              print "sal-inf-bmc failed."
              return -1
          print >> f, '~~~~~~~~~~'
          f.flush()
        f.close()
        #print 'NOTE: Download and install SAL from sal.csl.sri.com'
    else:
        print 'No LTL properties were provided'
        print 'For verifying the model, add a property either in the Matlab model or in the translated SAL file directly'
        print 'Then, Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> <propertyName added in generated SAL file>'
        return -1
    return 0

if __name__ == "__main__":
    ret_code = main()
    sys.exit(ret_code)

