import sys
import os
import xml.dom.minidom
import ModelicaXML	# modelica -> dae
import ddae		# dae -> daexml
import daeXML		# daexml -> simplified daexml
import daexmlPP
import daexml2hsal	# daexml -> hsal
import modelica2daexml
import modelica_slicer

# USAGE:
# modelica2hsal(filename, prop_filename, options)
# where options = ['--slicewrt', varlist, ...]

libraryStr = '''
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Reverse = 1
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Park = 2
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Swim_Mode = 3
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Neutral = 4
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Neutral_Pivot = 5
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Low = 6
C2M2L_Decl.Interfaces.Context_Interfaces.Driver.PRNDL_Setting.Drive = 7
Modelica.Fluid.Utilities.regStep(x,y1,y2,e) = if (x > e) then y1 else y2
abs(x) = if (x >= 0) then x else -x 
power(x,2) = x * x
Modelica.Fluid.Utilities.regRoot(x,y) = if (x >= 0) then sqrt(x) else -(sqrt(-x))
semiLinear(0.0,x,y) = 0.0
semiLinear(x,y,z) = if (x >= 0) then x*y else x*z
noEvent(x) = x
smooth(x,y) = y
Modelica.Math.tempInterpol2(0.0,{{x,y,z,u,v}},{2,3,4,5})={{y,z,u,v}}
Modelica.Math.Matrices.isEqual({{x,y,z,u,v}},{{a,b,c,d,e}},w)= (x==a and y==b and z==c and u==d and v==e)
Modelica.Blocks.Types.ExternalCombiTable1D.constructor(x,y,z,u,v) = z
Modelica.Blocks.Types.ExternalCombiTable2D.constructor(x,y,z,u) = z
Modelica.Blocks.Tables.CombiTable1D.getTableValue(table,1,u,d) = mytable(u,table,2)
Modelica.Blocks.Tables.CombiTable1D.getTableValue(table,icol,u,d) = mytable(u,table,icol+1)
Modelica.Blocks.Tables.CombiTable2D.getTableValue(table,u1,u2,d) = mytable2(u1,u2,table)
Modelica.Blocks.Tables.CombiTable1D.tableIpo(table,icol,u)=mytable(u,table,icol)
Modelica.Math.tempInterpol1(u,table,icol)=mytable(u,table,icol)
Modelica.Blocks.Sources.CombiTimeTable.getNextTimeEvent(x,y,z) = y
Modelica.Blocks.Sources.CombiTimeTable.getTableValue(x,y,z,u,v,w) = 12
Modelica.Blocks.Sources.CombiTimeTable.getTableTimeTmin(x, y) = 0
Modelica.Blocks.Sources.CombiTimeTable.getTableTimeTmax(x, y) = 1900
max({{x, 1.0001}}) = 1.0001
transpose(x) = x
vector(x) = x
real(x) = x
sign(x) = x
selector(x,y) = x[y]
selector(x,y,z) = x[y][z]
'''

propStr = '''
{"context" : "TRUE",
 "property" : 
 {"f"    : "G", 
  "nargs": 1, 
  "args" : 
    [{"f"    : "/=", 
     "nargs": 2, 
     "args" : ["__RequirementVar__", "violated"] }] } } '''

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

def modelica2hsal(filename, pfilename = None, options = []):
    if '--slicewrt' in options:
      index = options.index('--slicewrt')
      varlist = options[index+1]
      if type(varlist) != list:
        varlist = varlist.split(',')
      (filename,mdom) = modelica_slicer.modelica_slice_file(filename, varlist)
    (dom2, dom1, daexmlfilename) = modelica2daexml.modelica2daexml(filename,options)
    basename,ext = os.path.splitext(filename)
    print >> sys.stderr, 'Trying to simplify the Modelica model...'
    try:
        # print 'Trying to parse the libraryString...'
        (libdom,libdaexml) = ddae.daestring2daexml(libraryStr,'library')
        # print 'Successfully parsed the libraryString...'
        # print libdaexml.toxml()
    except:
        print 'Library in wrong syntax. Unable to handle.'
        sys.exit(-1)
    dom1 = daeXML.simplifydaexml(dom1,daexmlfilename,library=libdaexml)
    #os.remove(daexmlfilename)	# this is .daexml file
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
    elif pfilename == None:
        print >> sys.stderr, 'Assuming requirement contained in XML file.'
        try:
            import json
            jsondata = propStr
            for i in ['\n','\r','\\']:
                jsondata = jsondata.replace(i,'')
            oVars = daexml2hsal.getElementsByTagTagName(dom2, 'orderedVariables', 'variablesList')
            assert oVars != None and len(oVars) > 0
            found = False
            for v in oVars[0].getElementsByTagName('variable'):  # v = <variable ...>
                v_typ = v.getAttribute('type')
                if v_typ.startswith('enumeration') and v_typ.find('violated') != -1:
                    varname = v.getAttribute('name')
                    print >> sys.stderr, 'Requirement Variable', varname
                    jsondata = jsondata.replace('__RequirementVar__',varname)
                    found = True
                    break
            if found:
                dom3 = json.loads(jsondata)
            else:
                print 'WARNING: NO REQUIREMENT FOUND.'
        except SyntaxError, e:
            print 'Syntax Error: Input JSON ', e 
            print 'Error: Property JSONStr is not well-formed...Quitting.'
            return -1
        except:
            print 'Error: Unable to read property JSONstr...Quitting.'
            return -1
    else:
        print 'WARNING: NO REQUIREMENT FOUND.'
        print '***Verification model generated, but no result reported.***'
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
