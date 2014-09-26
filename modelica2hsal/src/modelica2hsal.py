import sys
import os
import xml.dom.minidom
import ddae		# dae -> daexml
import daeXML		# daexml -> simplified daexml
import daexml2hsal	# daexml -> hsal
import modelica2daexml
import modelica_slicer

# ----------------------------------------------------------------------
# USAGE:
# ----------------------------------------------------------------------
# modelica2hsal(filename, prop_filename, options)
#  where options = ['--slicewrt', varlist, ...]
#  Returns: (hsal_filename, track_map)
#  where track_map = dict: Str->Str maps varlist to output vars in hsal
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# The library string. Update it if you see in a new function in modelica.
# ----------------------------------------------------------------------
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
min(x,y) = if (x < y) then x else y
transpose(x) = x
vector(x) = x
real(x) = x
integer(x,y) = x
sign(x) = x
selector(x,y) = x[y]
selector(x,y,z) = x[y][z]
'''
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Properties can be given in json file. Following is an example
# Assumes modelica file has an embedded property.
# ----------------------------------------------------------------------
propStr = '''
{"context" : "TRUE",
 "property" : 
 {"f"    : "G", 
  "nargs": 1, 
  "args" : 
    [{"f"    : "/=", 
     "nargs": 2, 
     "args" : ["__RequirementVar__", "violated"] }] } } '''
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Usage from command-line 
# ----------------------------------------------------------------------
def printUsage():
    print '''
modelica2hsal -- a converter from Modelica to HybridSal

Usage: python modelica2hsal.py <modelica_file.xml> [<context_property.xml>] [--addTime]

Description: This will create a file called modelica_fileModel.hsal
    '''
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Check args when called from command-line
# ----------------------------------------------------------------------
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
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# main function of entry when called from command-line
# ----------------------------------------------------------------------
def main():
    global dom
    (filename, pfilename) = argCheck(sys.argv, printUsage)
    modelica2hsal(filename, pfilename, sys.argv[1:])
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Main external interface function -- it is a wrapper to others
# ----------------------------------------------------------------------
def modelica2hsal(filename, pfilename = None, options = []):
    # if --slicewrt is in options, apply the slicer
    if '--slicewrt' in options:
      index = options.index('--slicewrt')
      varlist = options[index+1]
      if type(varlist) != list:
        varlist = varlist.split(',')
      if len(varlist) == 0:
        print 'ERROR: Cannot slice with respect to empty list of variables!'
        sys.exit(1)
      (filename, mdom, track_map) = modelica_slicer.modelica_slice_file(filename, varlist)
      del mdom
    else:
      track_map = {}
    # slicer can change filename by replacing '-' by '_'

    # convert (sliced) modelica to daexml
    (dom2, dom1, daexmlfilename) = modelica2daexml.modelica2daexml(filename,options)
    basename,ext = os.path.splitext(filename)

    # Parse library string and then simplify the daexml in stages
    print >> sys.stderr, 'Trying to simplify the Modelica model...'
    try:
      (libdom,libdaexml) = ddae.daestring2daexml(libraryStr,'library')
    except:
      print 'Library in wrong syntax. Unable to handle.'
      sys.exit(-1)

    # Simplify the daexml in stages
    dom1 = daeXML.simplifydaexml(dom1,daexmlfilename,library=libdaexml)
    # os.remove( daexmlfilename )
    print >> sys.stderr, 'Finished simplification steps.'
    dom3 = None		# No property file given by default
    if pfilename != None and pfilename.rstrip().endswith('.xml'):
      print >> sys.stderr, 'Reading XML file containing context and property'
      try:
        dom3 = xml.dom.minidom.parse(pfilename)
      except xml.parsers.expat.ExpatError, e:
        print 'Syntax Error: Input XML ', e 
        print 'Error: Property XML file is not well-formed...Quitting.'
        sys.exit(-1)
      except:
        print 'Error: Property XML file is not well-formed'
        print 'Quitting', sys.exc_info()[0]
        sys.exit(-1)
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
        sys.exit(-1)
      except:
        print 'Error: Unable to read property JSON file...Quitting.'
        sys.exit(-1)
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
          vlist = oVars[0].getElementsByTagName('variable')
          for v in vlist: 		# v = <variable ...>
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
            print >> sys.stderr, 'WARNING: NO REQUIREMENT FOUND in plant.'
        except SyntaxError, e:
          print 'Syntax Error: Input JSON ', e 
          print 'Error: Property JSONStr is not well-formed...Quitting.'
          sys.exit(-1)
        except:
          print 'Error: Unable to read property JSONstr...Quitting.'
          sys.exit(-1)
    else:
      print >> sys.stderr, 'WARNING: NO REQUIREMENT FOUND in plant model.'
    print >> sys.stderr, 'Creating HybridSal model....'
    outfile = daexml2hsal.daexml2hsal(dom1, dom2, daexmlfilename, dom3)
    print >> sys.stderr, 'Created HybridSal model.'
    return (outfile, track_map)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------

