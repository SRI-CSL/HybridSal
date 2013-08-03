import sys
import os
import xml.dom.minidom
import ModelicaXML	# modelica -> dae
import ddae		# dae -> daexml
import daeXML		# daexml -> simplified daexml
import daexmlPP
import daexml2hsal	# daexml -> hsal

libraryStr = '''
Modelica.Fluid.Utilities.regStep(x,y1,y2,e) = if (x >= e) then y1 else (if (x <= -e) then y2 else (y1+y2)/2 )
Modelica.Fluid.Utilities.regRoot(x,y) = if (x >= 0) then sqrt(x) else -(sqrt(-x))
tester(a, b) = der(a)
'''

def printUsage():
    print '''
modelica2hsal -- a converter from Modelica to HybridSal

Usage: python modelica2hsal.py <modelica_file.xml> [<context_property.xml>] [--addTime]

Description: This will create a file called modelica_fileModel.hsal
    '''

def moveIfExists(filename):
    import shutil
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def argCheck(args, printUsage):
    "args = sys.argv list"
    if not len(args) >= 2:
        printUsage()
        sys.exit(-1)
    if args[1].startswith('-'):
        printUsage()
        sys.exit(-1)
    filename = args[1]
    basename,ext = os.path.splitext(filename)
    if len(args) > 2 and not args[2].startswith('-'):
        pfilename = args[2]
        pbasename,pext = os.path.splitext(pfilename)
    else:
        pfilename = None
        pbasename,pext = None,'.xml'
    if not(ext == '.xml') or (not(pext == '.xml') and not(pext == '.json')):
        print 'ERROR: Unknown extension {0}; expecting .xml/.json'.format(ext)
        printUsage()
        sys.exit(-1)
    if not(os.path.isfile(filename)):
        print 'ERROR: File {0} does not exist'.format(filename)
        printUsage()
        sys.exit(-1)
    if (pfilename != None) and not(os.path.isfile(pfilename)):
        print 'ERROR: File {0} does not exist'.format(pfilename)
        printUsage()
        sys.exit(-1)
    return (filename, pfilename)

def main():
    global dom
    (filename, pfilename) = argCheck(sys.argv, printUsage)
    modelica2hsal(filename, pfilename, sys.argv[1:])

def addTime(dom2):
    'add time as a new continuousState variable in the model'
    node = dom2.createElement('variable')
    node.setAttribute('name', 'time')
    node.setAttribute('variability', 'continuousState')
    node.setAttribute('direction', 'none')
    node.setAttribute('type', 'Real')
    node.setAttribute('index', '-1')
    node.setAttribute('fixed', 'false')
    node.setAttribute('flow', 'NonConnector')
    node.setAttribute('stream', 'NonStreamConnector')
    orderedVars_varlists = daexml2hsal.getElementsByTagTagName(dom2, 'orderedVariables', 'variablesList')
    assert orderedVars_varlists != None and len(orderedVars_varlists) > 0
    orderedVars_varlist = orderedVars_varlists[0]
    orderedVars_varlist.appendChild(node)
    equations = dom2.getElementsByTagName('equations')
    newequation = dom2.createElement('equation')
    newequation.appendChild( dom2.createTextNode('der(time) = 1') )
    assert equations != None and len(equations) > 0
    equations[0].appendChild(newequation)
    return dom2

def removeTime(dom1):
    'remove all equations that mention time in them'
    def hasTime(e):
        ids = e.getElementsByTagName('identifier')
        for identifier in ids:
            name = daexml2hsal.valueOf(identifier).strip()
	    if name.strip() == 'time':
                return True
        return False
    Eqn = dom1.getElementsByTagName('equations')[0]
    eqns = Eqn.getElementsByTagName('equation')
    for e in eqns:
        if hasTime(e):
            Eqn.removeChild(e)
    Eqn = dom1.getElementsByTagName('knownVariables')[0]
    eqns = Eqn.getElementsByTagName('variablevalue')
    for e in eqns:
        if hasTime(e):
            Eqn.removeChild(e)
    return dom1

def modelica2hsal(filename, pfilename = None, options = []):
    def existsAndNew(filename1, filename2):
        if os.path.isfile(filename1) and os.path.getctime(filename1) >= os.path.getctime(filename2):
            print "File {0} exists and is new".format(filename1)
            return True
        return False
    basename,ext = os.path.splitext(filename)
    try:
        dom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        print 'Syntax Error: Input XML ', e 
        print 'Error: Input XML file is not well-formed...Quitting.'
        return -1
    except:
        print 'Error: Input XML file is not well-formed'
        print 'Quitting', sys.exc_info()[0]
        return -1
    dom2 = dom	# will be used later by daexml2hsal for variable information
    if '--addTime' in options:
        dom2 = addTime(dom2)
    daefilename = basename + '.dae'
    print >> sys.stderr, 'Parsing Modelica XML file......'
    if not existsAndNew(daefilename, filename):
        with open(daefilename,'w') as fp:
            ModelicaXML.HSalPPContext(dom, fp)   # create a .dae file
        print >> sys.stderr, 'Parsing complete. Created file {0}'.format(daefilename)
    else:
        print >> sys.stderr, 'Using existing {0} file'.format(daefilename)
    # now parse the dae into daexml
    daexmlfilename = basename + '.daexml'
    if not existsAndNew(daexmlfilename, daefilename):
        (dom,daexml) = ddae.dae2daexml(daefilename)
        # neither dom nor daexml are used below; used for side-effect to create file!!
        print >> sys.stderr, 'Created file {0}'.format(daexmlfilename)
    else:
        print >> sys.stderr, 'Using existing {0} file'.format(daexmlfilename)
    # os.remove(daefilename)	# this is .dae file
    print >> sys.stderr, 'Trying to simplify the Modelica model...'
    try:
        dom1 = xml.dom.minidom.parse(daexmlfilename)
    except:
        print 'Model not supported: Unable to handle some expressions currently'
        sys.exit(-1)
    if '--removeTime' in options:
        dom1 = removeTime(dom1)
    # Now try to parse the library file
    try:
        print 'Trying to parse the libraryString...'
        (libdom,libdaexml) = ddae.daestring2daexml(libraryStr,'library')
        print 'Successfully parsed the libraryString...'
        # print libdaexml.toxml()
    except:
        print 'Library in wrong syntax. Unable to handle.'
        sys.exit(-1)
    dom1 = daeXML.simplifydaexml(dom1,daexmlfilename,library=libdaexml)
    os.remove(daexmlfilename)	# this is .daexml file
    print >> sys.stderr, 'Finished simplification steps.'
    # with open('tmp','w') as fp:
        # daexmlPP.source_textPP(dom1, filepointer=fp)
    dom3 = None		# No property file given by default
    if pfilename != None and pfilename.rstrip().endswith('.xml'):
        print >> sys.stderr, 'Reading XML file containing context and property'
        try:
            dom3 = xml.dom.minidom.parse(pfilename)
        except xml.parsers.expat.ExpatError, e:
            print 'Syntax Error: Input XML ', e 
            print 'Error: Property XML file is not well-formed...Quitting.'
            return -1
        except:
            print 'Error: Property XML file is not well-formed'
            print 'Quitting', sys.exc_info()[0]
            return -1
        print >> sys.stderr, 'Finished reading context and property'
    elif pfilename != None and pfilename.rstrip().endswith('.json'):
        print >> sys.stderr, 'Reading JSON file containing context and property'
        try:
            import json
            with open(pfilename,'r') as fp:
                jsondata = fp.read()
                for i in ['\n','\r','\\']:
                    jsondata = jsondata.replace(i,'')
                dom3 = json.loads(jsondata)
                assert isinstance(dom3,dict),'ERROR: Expected dict in JSON file'
        except SyntaxError, e:
            print 'Syntax Error: Input JSON ', e 
            print 'Error: Property JSON file is not well-formed...Quitting.'
            return -1
        except:
            print 'Error: Unable to read property JSON file...Quitting.'
            return -1
    print >> sys.stderr, 'Creating HybridSal model....'
    outfile = daexml2hsal.daexml2hsal(dom1, dom2, daexmlfilename, dom3)
    print >> sys.stderr, 'Created HybridSal model.'
    return outfile

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
