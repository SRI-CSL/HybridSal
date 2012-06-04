import sys
import os.path
import xml.dom.minidom
import ModelicaXML	# modelica -> dae
import ddae		# dae -> daexml
import daeXML		# daexml -> simplified daexml
import daexml2hsal	# daexml -> hsal

def printUsage():
    print '''
modelica2hsal -- a converter from Modelica to HybridSal

Usage: python modelica2hsal.py <modelica_file.xml>

Description: This will create a file called modelica_file.hsal
    '''

def moveIfExists(filename):
    import shutil
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def main():
    global dom
    if not len(sys.argv) == 2:
        printUsage()
        return -1
    filename = sys.argv[1]
    basename,ext = os.path.splitext(filename)
    if not(ext == '.xml'):
        print 'ERROR: Unknown file extension {0}; expecting .xml'.format(ext)
        printUsage()
        return -1
    if not(os.path.isfile(filename)):
        print 'ERROR: File {0} does not exist'.format(filename)
        printUsage()
        return -1
    modelica2hsal(filename)

def modelica2hsal(filename):
    basename,ext = os.path.splitext(filename)
    dom = xml.dom.minidom.parse(filename)
    dom2 = dom	# will be used later by daexml2hsal for variable information
    daefilename = basename + '.dae'
    moveIfExists(daefilename)
    print >> sys.stderr, 'Parsing Modelica XML file......'
    with open(daefilename,'w') as fp:
        ModelicaXML.HSalPPContext(dom, fp)   # create a .dae file
    print >> sys.stderr, 'Parsing complete. Created file {0}'.format(daefilename)
    # now parse the dae into daexml
    (dom,daexml) = ddae.dae2daexml(daefilename)
    daexmlfilename = basename + '.daexml'
    print >> sys.stderr, 'Created file {0}'.format(daexmlfilename)
    print >> sys.stderr, 'Trying to simplify the Modelica model...'
    dom1 = xml.dom.minidom.parse(daexmlfilename)
    dom1 = daeXML.simplifydaexml(dom1,daexmlfilename)
    print >> sys.stderr, 'Finished simplification steps.'
    print >> sys.stderr, 'Creating HybridSal model....'
    daexml2hsal.daexml2hsal(dom1, dom2, daexmlfilename)
    print >> sys.stderr, 'Created HybridSal model.'
    return 0

if __name__ == "__main__":
    main()

'''
	python ModelicaXML.py RCEngine.xml  > RCEngine.dae
	python ddae.py RCEngine.dae
	python daeXML.py RCEngine.daexml
	mv RCEngine.dae_flat_xml RCEngine1.daexml
	python daexmlPP.py RCEngine1.daexml > RCEngine1.dae
	python daexml2hsal.py RCEngine1.daexml RCEngine.xml
'''
