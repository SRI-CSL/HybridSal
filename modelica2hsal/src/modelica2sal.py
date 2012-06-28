import sys
import os.path
import inspect

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

def main():
    global dom
    (filename, pfilename) = modelica2hsal.argCheck(sys.argv, printUsage)
    try:
        outfile = modelica2hsal.modelica2hsal(filename, pfilename)
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
        ans = HSalRelAbsCons.hxml2sal(xmlfilename, optarg=0, timearg=None)
    except Exception, e:
        print e
        print 'Relational abstracter can not abstract this model. Quitting.'
        return -1
    if pfilename != None:
        print 'You can now run sal-inf-bmc on the generated SAL file'
        print 'Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> p1'
        print 'NOTE: The requirement is called p1 in the generated SAL file'
        print 'NOTE: Use sal-inf-bmc --help for more information'
        print 'NOTE: Download and install SAL from sal.csl.sri.com'
    else:
        print 'No property-context file was provided'
        print 'For verifying the model, add a property in the generated SAL file'
        print 'Then, Use the command: sal-inf-bmc -d 4 <GeneratedSALFile> <propertyName added in generated SAL file>'
    return ans

if __name__ == "__main__":
    main()

