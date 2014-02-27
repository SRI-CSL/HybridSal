# OBSOLETE FILE -- use modelica2sal instead....
import sys
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

Usage: python modelica2sal.py <modelica_file.xml> [<context_property.xml>]

Description: This will create a file called modelica_fileModel.sal
    '''

# def generateHSalfilename(filename):
    # basename,ext = os.path.splitext(filename)
    # basename = basename.replace('.','_')
    # basename += "Model"
    # return basename + ".hsal"

def hsal2hxml(filename):
    basename,ext = os.path.splitext(filename)
    if ext == '.hxml':
        xmlfilename = filename
    elif ext == '.hsal':
        xmlfilename = basename + ".hxml"
        hybridsal2xml = 'hybridsal2xml.jar'
        retCode = subprocess.call(["java", "-jar", hybridsal2xml, "-o", xmlfilename, filename])
        if retCode != 0 or not(os.path.isfile(xmlfilename)):
            print "hybridsal2xml failed to create XML file. Quitting."
            return 1
    else:
        print "Unknown file extension; Expecting .hsal or .hxml; Quitting"
        return 1
    return xmlfilename

def main():
    global dom
    (filename, pfilename) = modelica2hsal.argCheck(sys.argv, printUsage)
    try:
        outfile = modelica2hsal.modelica2hsal(filename, pfilename, options = sys.argv[1:])
        # maybe copy file to a local place?
        #retCode = subprocess.call(['modelica2hsal', filename, pfilename])
        #outfile = generateHSalfilename(filename)
    except Exception, e:
        print e
        print 'Error: Unable to create HybridSal file from Modelica XML'
        return -1
    # this will create outfile == 'filenameModel.hsal'
    # now I need to run hsal2hasal
    try:
        xmlfilename = hsal2hxml(outfile)
    except Exception, e:
        print e
        print 'Syntax error in generated HybridSal file. Quitting.'
        return -1
    try:
        ans = HSalRelAbsCons.hxml2sal(xmlfilename, optarg=0, timearg=None)
    except Exception, e:
        print e
        print 'Relational abstracter can not abstract this model. Quitting.'
        return -1
    iswin = sys.platform.startswith('win')
    if pfilename != None:
        salinfbmc = 'sal-inf-bmc'
        if iswin:
            salinfbmc += '.bat'
        # change directory to where the sal file was created...
        # os.chdir( os.path.dirname(ans) )
        ans = os.path.realpath(os.path.abspath(ans))
        ans = repr(ans)
        ans = ans.replace('\\','/')
        ans = ans.replace('c:/','/cygdrive/c/')
        ans = ans[1:-1]
        retCode = subprocess.call([salinfbmc, "-d", "4", ans, "p1"])
        if retCode != 0:
            print "sal-inf-bmc failed."
            return 1
        else:
            print "sal-inf-bmc terminated successfully."
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

