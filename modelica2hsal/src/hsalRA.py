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

def printUsage():
    print '''
modelica2sal -- a converter from Modelica to Sal

Usage: python modelica2sal.py <modelica_file.xml> [<context_property.xml>] [--addTime]

Description: This will create a file called modelica_fileModel.sal
    '''

def main():
    def checkexe(filename):
        exepaths = os.environ['PATH'].split(os.path.pathsep)
        for i in exepaths:
            exefile = os.path.join(i, filename)
            if os.path.exists(exefile):
                return True
        print 'ERROR: File {0} not found in PATH.'.format(filename)
        return False
    def getexe():
        folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
        relabsfolder = os.path.join(folder, '..', '..', 'bin')
        relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
        return relabsfolder
    global dom
    (filename, pfilename) = modelica2hsal.argCheck(sys.argv, printUsage)
    try:
        outfile = modelica2hsal.modelica2hsal(filename, pfilename, options = sys.argv[1:])
    except Exception, e:
        print e
        print 'Error: Unable to create HybridSal file from Modelica XML'
        return -1
    # this will create outfile == 'filenameModel.hsal'
    # now I need to run hsal2hasal
    try:
        xmlfilename = HSalRelAbsCons.hsal2hxml(outfile)
    except Exception, e:
        print e
        print 'Syntax error in generated HybridSal file. Quitting.'
        return -1
    try:
        ans, prop_exists = HSalRelAbsCons.hxml2sal(xmlfilename, optarg=0, timearg=None)
    except Exception, e:
        print e
        print 'Relational abstracter can not abstract this model. Quitting.'
        return -1
    iswin = sys.platform.startswith('win')
    # if pfilename != None:
    if prop_exists:
        salinfbmc = 'sal-inf-bmc.bat' if iswin else 'sal-inf-bmc'
        if not checkexe(salinfbmc):
            salinfbmc = os.path.join(getexe(), 'sal-inf-bmc.bat')
            assert os.path.exists(salinfbmc), 'ERROR: {0} not found'.format(salinfbmc)
        # change directory to where the sal file was created...
        #if os.environ.has_key('SALCONTEXTPATH'):
            #oldpath = os.environ['SALCONTEXTPATH']
        #else:
            #oldpath = '.'
        hsal_file_path = os.path.abspath(ans) 
        hsal_file_path = hsal_file_path.replace('\\', '/')
        hsal_file_path = hsal_file_path.replace('C:', '/cygdrive/c')
        #hsal_file_path = hsal_file_path.replace('C:', '/c/')
        #os.environ['SALCONTEXTPATH'] = hsal_file_path + ':' + oldpath 
        #print 'SALCONTEXTPATH = ', os.environ['SALCONTEXTPATH']
        retCode = subprocess.call([salinfbmc, "-d", "4", hsal_file_path, "p1"], env=os.environ)
        if retCode != 0:
            print "sal-inf-bmc failed."
            return 1
        #print 'You can now run sal-inf-bmc on the generated SAL file'
        #print 'Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> p1'
        #print 'NOTE: The requirement is called p1 in the generated SAL file'
        #print 'NOTE: Use sal-inf-bmc --help for more information'
        #print 'NOTE: Download and install SAL from sal.csl.sri.com'
    else:
        print 'No property-context file was provided'
        print 'For verifying the model, add a property in the generated SAL file'
        print 'Then, Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> <propertyName added in generated SAL file>'
    return 0

if __name__ == "__main__":
    main()

