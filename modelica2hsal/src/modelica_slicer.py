import sys
import os
import xml.dom.minidom 

# Notes: 
# 05 Aug, 2014: Using only orderedVariables for creating slices...
# 17 Aug, 2014: initialEquations absent in slice -- fixed
# 17 Aug, 2014: aliasVariables  absent in slice -- fixed
# 22 Aug, 2014: knownVars defined using other vars -- include them too!

# Algorithm for SLICER:
# Maintain equivalence class of variables
#  if x+y=10 is an equation, then x,y are in the same class (UF data-struct)
#  if dx/dt = x+y+z, then x points_to y,z (reliesOn data-struct)
# slice = compute influence variables modulo equivalence

# Usage:
# Inside python call:
#  modelica_slicer.modelica_slice_file(filename, varlist)
#    where varlist = list of variable names (str)
# Command line:
#  python src/modelica_slicer.py examples/no_controls_dae.xml --slicewrt "driveLine.pTM_with_TC.torque_Converter_Lockup.clutch_lockup.phi_rel" > tmp.txt
#
#  python src/modelica_slicer.py  examples/SystemDesignTest-r663.xml  --slicewrt "driver_gear_select, shift_request_state, output_speed_torque_converter, input_speed_torque_converter, prndl" > tmp.txt

# ----------------------------------------------------------------------
# Union Find data structure
# ----------------------------------------------------------------------
class UnionFind:
  def __init__(self):
    self.parent = {}
  def find(self, v):
    ans = v
    while self.parent.has_key(ans):
      ans = self.parent[ans]
    u = v
    while u != ans and self.parent[u] != ans:
      tmp = self.parent[u]
      self.parent[u] = ans
      u = tmp
    return ans
  def union(self, varlist): 
    if varlist == []:
      return self
    vroot = self.find( varlist[0] )
    for v in varlist[1:]:
      vroot1 = self.find(v)
      if vroot1 != vroot:
        self.parent[vroot1] = vroot
    return self
  def get_eq_class(self, v):
    '''return list of all v's that are eq to given v'''
    v3 = self.find(v)
    ans = [ v3 ]
    print 'eq class representative: {0}'.format(v3)
    for (v1,v2) in self.parent.items():
      if v2==v3:
        ans.append(v1)
    return ans
  def __str__(self):
    classes = {}
    ans = '{\n'
    for k in self.parent.keys():
      v = self.find(k)
      if classes.has_key(v):
        classes[v] += 1
      else:
        classes[v] = 1
      ans += ' {0}:{1},\n '.format( k,v)
    ans += '}'
    ans += str(classes)
    return ans
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Binary Relation -- dependency relation for slicing
# ----------------------------------------------------------------------
class LabeledBinaryRelation:
  def __init__(self):
    self.r = {}
  def update(self, src, dst, label):
    if self.r.has_key(src):
      if self.r[src].has_key(dst):
        return self
      else:
        self.r[src][dst] = label
    else:
      self.r[src] = {dst:label}
    return self
  def normalize(self, uf):
    def normalize1(vlabel, uf):
      return { uf.find(k):v for k,v in vlabel.items() }
    for k,v in self.r.items():
      knf = uf.find(k)
      if self.r.has_key(knf):
        self.r[knf].update( normalize1(v,uf) )
      else:
        self.r[knf] = normalize1(v,uf)
  def image(self, v):
    if self.r.has_key(v):
      return self.r[v]
    return {}
  def __str__(self):
    return str(self.r)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Usage 
# ----------------------------------------------------------------------
def printUsage():
    print '''
modelica_slicer -- a slicer from Modelica DAEs; creates sliced DAE XML dump

Usage: python src/modelica_slicer.py <modelica_file.xml> --slicewrt "v1,v2,v3"

Description: This will create a file called modelica_file_slice.xml
    '''
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
# Helpers for reading DOM nodes
def valueOf(node):
    """return text value of node"""
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(i.data)

def getChildByTagName(node,tag):
    for i in node.childNodes:
        if i.nodeType == i.ELEMENT_NODE and i.tagName == tag:
            return i
    return None

def getElementsByTagTagName(root, tag1, tag2):
    node = root.getElementsByTagName(tag1)
    if node == None or len(node) == 0:
        return []
    nodes = node[0].getElementsByTagName(tag2)
    ans = nodes if nodes != None else []
    return ans    

def helper_create_tag_val(tag, val, position = None):
    global dom
    node = dom.createElement(tag)
    if position != None:
        node.setAttribute('col', str(position.col))
        node.setAttribute('line', str(position.line))
    node.appendChild( dom.createTextNode( val ) )
    return node 
# -------------------------------------------------------------------

# -------------------------------------------------------------------
def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Note: there is also "aliasVariables"
def varsxml2dict(ovars):
  '''return a dict from var-name to var-id'''
  ans = {}
  for i in ovars:
    ans[i.getAttribute('name')] = i.getAttribute('id')
  return ans

def kvars2dict(kvars, uf, reliesOn, ovarl, prefix='k'):
  ans = {}
  for var in kvars:
    eid = var.getAttribute('id')
    vname = var.getAttribute('name')
    bindvalexpr = getChildByTagName(var, 'bindValueExpression')
    if bindvalexpr == None:
      continue
    bindexpr = getChildByTagName(bindvalexpr, 'bindExpression')
    if bindexpr == None:
      continue
    elist = [ vname ]
    mml = getChildByTagName(bindexpr, 'MathML')
    assert mml != None, 'No MathML'
    lhs = helper_create_tag_val('ci', vname)
    analyze_mml( lhs, mml, uf, reliesOn, ovarl, name=prefix+eid )
  return (uf, reliesOn)

def mml_eqn_get_lhs_rhs( mml ):
  '''MathML equation: <MathML><math>
     <apply><equiv><lhs><rhs></apply><math></MathML>'''
  math_e = getChildByTagName(mml, 'math')
  assert math_e != None, 'No math in MathML'
  apply_e = getChildByTagName(math_e, 'apply')
  assert apply_e != None, 'No apply in MathML.math'
  equiv = getArg( apply_e, 1)
  #print apply_e.toxml(), equiv.toxml()
  assert equiv.tagName == 'equivalent', 'Err: Expected equivalent tag {0}\n{1}'.format(equiv.toxml(), apply_e.toxml())
  lhs = getArg( apply_e, 2)
  rhs = getArg( apply_e, 3)
  return (lhs,rhs)

def eqnsxml2dict(eqns, uf, reliesOn, ovarl, prefix=''):
  '''get its MathML child, find <ci> in it'''
  for e in eqns:
    eid = e.getAttribute('id')
    mml = getChildByTagName(e, 'MathML')
    assert mml != None, 'No MathML'
    lhs, rhs = mml_eqn_get_lhs_rhs(mml)
    analyze_mml( lhs, rhs, uf, reliesOn, ovarl, name=prefix+eid )
    '''cis = mml.getElementsByTagName('ci')
    for i in cis:
      varname = valueOf(i).strip()
      if varname not in elist:
        elist.append(varname)
    ans[ prefix+eid ] = elist
    '''
  return (uf, reliesOn)

def analyze_mml( lhs, rhs, uf, reliesOn, ovarl, name='e'):
  '''update uf and reliesOn based on lhs=eqn, use name as label'''
  nxt, curr, pre = [], [], []
  (nxt, curr, pre) = classify_vars_as_curr_pre( lhs, nxt, curr, pre, ovarl)
  (nxt, curr, pre) = classify_vars_as_curr_pre( rhs, nxt, curr, pre, ovarl)
  '''
  if nxt != []:
    print 'name={0}, nxt={1}, curr={2}, pre={3}'.format(name, nxt, curr, pre)
  '''
  if nxt == [] and pre == []:
    uf.union( curr )
  elif pre == []:
    for i in nxt:
      for j in curr:
        reliesOn.update(i, j, name)
  elif nxt == []:
    for i in curr:
      for j in pre:
        reliesOn.update(i, j, name)
  else:
    assert False, 'Err: One equation has all next, curr and pre vars!'
  return (uf, reliesOn)

def classify_vars_as_curr_pre( mml, nxt, curr, pre, ovarl ):
  '''recurse and clasify each var in mml expr as nxt, curr or pre'''
  if mml.tagName == 'ci':
    allvars = [ mml ]
  else:
    allvars = mml.getElementsByTagName('ci')
  for i in allvars:
    varname = valueOf(i).strip()
    if varname not in ovarl:
      continue
    parent = i.parentNode
    if parent != None and parent.tagName == 'apply':
      op = getArg(parent, 1)
      if op.tagName == 'diff':
        if varname not in nxt:
          nxt.append(varname)
      elif op.tagName == 'pre':
        if varname not in pre:
          pre.append(varname)
      else:
        if varname not in curr:
          curr.append(varname)
    else:
      if varname not in curr:
        curr.append(varname)
  '''print 'Expr and its classification of variables'
  print mml.toxml()
  print 'nxt ', nxt
  print 'curr ', curr
  print 'pre ', pre '''
  return (nxt, curr, pre)

def getEqnsContainingV(v, edict):
  ans = []
  for (e,vlist) in edict.items():
    for va in vlist:
      if va.endswith(v):
        ans.append(e)
        break
  return ans

def getAllVarsInE(e, edict):
  return edict[e]

def varbackwards( varlist, uf, reliesOn ):
  '''monotonically increase varlist, list =list of names '''
  todo = varlist
  relevantv, relevante = [], []
  while todo != []:
    v = todo.pop()
    if v not in relevantv:
      relevantv.append(v)
    else:
      continue
    vnf = uf.find( v )
    vdict = reliesOn.image( vnf )
    for v in vdict.keys():
      if v not in todo and v not in relevantv:
          todo.append( v )
          relevante.append( vdict[v] )
    print '#v, #e', len(relevantv), len(relevante)
    print '#todo', len(todo)
  return (relevantv, relevante)

def find_matching_vars( varlist, ovarl ):
  '''replace v in varlist by v' s.t. v' in ovarl and v'.endswith(v)'''
  ans = []
  for i in varlist:
    istrip = i.strip()
    print 'searching for {0}...'.format(istrip)
    for j in ovarl:
      if j.endswith(istrip):
        print '{0} matched to {1}'.format(i, j)
        ans.append(j)
        break
  return ans

def extend_ovarl( ovarl, aliases ):
  '''add alias names into ovarl'''
  ans = []
  for i in aliases:
    bind = i.getElementsByTagName('bindExpression')[0]
    ci = bind.getElementsByTagName('ci')[0]
    varname = valueOf(ci).strip()
    if varname in ovarl:
      ans.append(i.getAttribute('name'))
  ovarl.extend( ans )
  return ovarl

# ----------------------------------------------------------------------
# Slice of equations, given relevant variables and state variables list
# ----------------------------------------------------------------------
def set_union(a, b):
  for i in b:
    if i not in a:
      a.append(i)
  return a

def isRelevantE( e, relevantv, ovarl):
  '''return True if
  for every var v in e, if v is in ovarl, then v is in relevantv
  '''
  ciL = e.getElementsByTagName('ci')
  varsL = [ valueOf(i).strip() for i in ciL ]
  restv = []
  for v in varsL:
    if v in ovarl:
      if v not in relevantv:
        return (False, restv)
    else:
      restv.append(v)
  return (True, restv)

def getRelevantE(equationL, total, ovarl):
  '''return subset of equationL containing e s.t.
  for every var v in e, if v is in ovarl, then v is in total
  '''
  ans, other_vars = [], []
  for e in equationL:
    (in_slice, restv) = isRelevantE( e, total, ovarl)
    if in_slice:
      ans.append(e)
      other_vars = set_union(other_vars, restv)
  return (ans, other_vars)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
def map_name_to_xml( var_name_l, ovars):
  '''var_name_l = list of strings, ovars =list of XMLs'''
  def find_var_in_list(var_name, ovars):
    for i in ovars:
      vname = i.getAttribute('name')
      if vname == var_name:
        return i
    return None
  sliced_v, rest = [], []
  for i in var_name_l:
    var_xml = find_var_in_list(i, ovars)
    if var_xml != None:
      sliced_v.append(var_xml)
    else:
      rest.append(i)
  return (sliced_v, rest)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# knownVar may be defined using other vars! Include them too!
# ----------------------------------------------------------------------
def saturate_kvars( sliced_kv, sliced_kv_names, kvars ):
  '''look at definition of kvar, find all vars in it, put them in'''
  stack, rest = sliced_kv, []
  while len(stack) != 0:
    new_kvs = []
    for v in stack:
      new_kvs = saturate_one_kvar( v, sliced_kv_names, new_kvs )
    (new_kv_xmls, rest3) = map_name_to_xml( new_kvs, kvars )
    rest.extend( rest3 )
    sliced_kv.extend( new_kv_xmls )
    sliced_kv_names.extend( new_kvs )
    stack = new_kv_xmls
  return (sliced_kv, sliced_kv_names, rest)

def saturate_one_kvar( var, sliced_kv_names, new_kvs ):
  n = var.getAttribute('name')
  bindvalexpr = getChildByTagName(var, 'bindValueExpression')
  if bindvalexpr == None:
    return new_kvs
  bindexpr = getChildByTagName(bindvalexpr, 'bindExpression')
  assert bindexpr != None, 'Err: No bindExpression in kvar {0}'.format(n)
  mml = getChildByTagName(bindexpr, 'MathML')
  assert mml != None, 'Err: No MathML in kvar {0}'.format(n)
  ciL = mml.getElementsByTagName('ci')
  varsL = [ valueOf(i).strip() for i in ciL ]
  for vname in varsL:
    if vname not in sliced_kv_names and vname not in new_kvs:
      if not vname.startswith('Modelica.Blocks.Types'):
        new_kvs.append( vname )
  return new_kvs
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
def modelicadom_slicer(modelicadom, varlist):
    '''dom = modelicaXML dom; varlist = variables wrt which slice
       output a tuple with sliced_e, sliced_v, etc.'''
    global dom
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, "daexml", None)
    ctxt = modelicadom.getElementsByTagName('dae')[0]
    variables = getChildByTagName(ctxt, 'variables')
    equations = getChildByTagName(ctxt, 'equations')
    #zeroCrossing = getChildByTagName(ctxt, 'zeroCrossingList')
    #arrayOfEqns = getChildByTagName(ctxt, 'arrayOfEquations')
    #algorithms = getChildByTagName(ctxt, 'algorithms')
    #functions = getChildByTagName(ctxt, 'functions')
    assert variables != None, 'Variables not found in input XML file!'

    # get list of names of ordered_variables
    tmp = getChildByTagName(variables, 'orderedVariables')
    ovars = tmp.getElementsByTagName('variable') if tmp != None else []
    ovarl = [i.getAttribute('name') for i in ovars]

    # set kvars = all externalVariables + aliasVariables
    kvars = []
    tmp = getChildByTagName(variables, 'externalVariables')
    extVars = tmp.getElementsByTagName('variable') if tmp != None else []
    kvars.extend( extVars )
    tmp = getChildByTagName(variables, 'aliasVariables')
    aliases = tmp.getElementsByTagName('variable') if tmp != None else []
    kvars.extend( aliases )

    ## set ovarl = ordered_variable_list + their aliases
    ovarl = extend_ovarl( ovarl, aliases )

    # Map given varlist to the ones we know in ovarl
    varlist = find_matching_vars( varlist, ovarl )

    # Initialize the data structures 
    equationL = equations.getElementsByTagName('equation')
    union_find,  relies_on = UnionFind(), LabeledBinaryRelation()
    (uf, reliesOn) = eqnsxml2dict(equationL, union_find, relies_on, ovarl)
    (uf, reliesOn) = kvars2dict( kvars, uf, reliesOn, ovarl )
    reliesOn.normalize( uf )

    # print 'Done creating data structures UF and reliesOn'
    # print uf, reliesOn

    # given varlist, find ALL-relevant vars using the data-structures
    (relevantv, relevante) = varbackwards( varlist, union_find, relies_on )
    '''print 'No. of relevant nodes = {0}:'.format(len(relevantv))
    print relevantv 
    print 'No. of relevant equations = {0}:'.format(len(relevante))
    print relevante'''

    # extend relevantv by including equivalent members 
    sliced_v, roots = [], []
    for i in relevantv:
      # print 'Equivalence class of {0}'.format(i)
      rooti = union_find.find( i )
      if rooti in roots:
        continue
      roots.append( rooti )
      eq_class = union_find.get_eq_class( i )
      sliced_v.extend(eq_class)
      # print eq_class
    # print 'Num of different eq classes = {0}'.format(len(roots))
    # print 'Sum of all eq classes = {0}'.format(len(sliced_v))

    # sliced_v = Union [relevantv]

    # get all equations containing only vars in sliced_v
    # other_v = other (known)-variables in the relevant equations
    (slice_e, other_v) = getRelevantE(equationL, sliced_v, ovarl)
    # print 'Number of relevant equations = {0}'.format(len(slice_e))

    # get all relevant initial Equations the same way...
    init_equations = getChildByTagName(ctxt, 'initialEquations')
    if init_equations != None:
      iequationL = init_equations.getElementsByTagName('equation')
      (slice_ie, other_v1) = getRelevantE(iequationL, sliced_v, ovarl)
      other_v = set_union(other_v, other_v1)
    else:
      slice_ie = []

    # sliced_v -> name -> XML map using ovars
    (sliced_v, rest) = map_name_to_xml( sliced_v, ovars)
    (sliced_av, rest) = map_name_to_xml( rest, aliases)
    sliced_v.extend( sliced_av )

    # find other_v in knownVariables and get knownVar_slice
    tmp = getChildByTagName(variables, 'knownVariables')
    kvars = tmp.getElementsByTagName('variable') if tmp != None else []
    (sliced_kv, rest2) = map_name_to_xml(other_v, kvars)
    (sliced_ev, rest2) = map_name_to_xml(rest2, extVars)
    sliced_kv.extend( sliced_ev )

    # knownVar may be defined using other vars! Include them too!
    (sliced_kv, other_v, rest3) = saturate_kvars(sliced_kv, other_v, kvars)

    # addTime if needed
    if 'time' in rest2:
      rest2.remove('time')
      (sliced_v, slice_e) = addTime( modelicadom, sliced_v, slice_e )

    # check nothing is left out
    assert len(rest) == 0, 'Err: Rest has {0} elements: {1}'.format(len(rest), rest)
    assert len(rest2) == 0, 'Err:Rest2 has {0} elements: {1}'.format(len(rest2), rest2)
    assert len(rest3) == 0, 'Err:Rest3 has {0} elements: {1}'.format(len(rest3), rest3)

    return ( slice_e, sliced_v, sliced_kv, slice_ie )

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
    if not(ext == '.xml'):
        print 'ERROR: Unknown extension {0}; expecting .xml'.format(ext)
        printUsage()
        sys.exit(-1)
    if not(os.path.isfile(filename)):
        print 'ERROR: File {0} does not exist'.format(filename)
        printUsage()
        sys.exit(-1)
    return filename


def addTime(dom2, varlist, eqnlist):
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
    varlist.append( node )
    newequation = dom2.createElement('equation')
    newequation.appendChild( dom2.createTextNode('der(time) = 1') )
    eqnlist.append( newequation )
    return (varlist, eqnlist)

def output_sliced_dom(slice_filename, sliced_e, slice_ie, sliced_v, other_v, dom):
  '''output XML in the given filename'''
  with open(slice_filename, 'w') as fp:
    print >> fp, '''<?xml version="1.0" encoding="UTF-8"?>
<dae xmlns:p1="http://www.w3.org/1998/Math/MathML"
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
    xsi:noNamespaceSchemaLocation="http://home.dei.polimi.it/donida/Projects/AutoEdit/Images/DAE.xsd">
    '''
    total_vars = len(sliced_v) + len(other_v)
    print >> fp, '<variables dimension="{0}">'.format(total_vars)
    print >> fp, '<orderedVariables dimension="{0}">'.format(len(sliced_v))
    print >> fp, '<variablesList>'
    for i in sliced_v:
      print >> fp, i.toxml()
    print >> fp, '</variablesList>'
    print >> fp, '</orderedVariables>'
    # Next print out knownVariables....
    print >> fp, '<knownVariables dimension="{0}">'.format(len(other_v))
    for i in other_v:
      print >> fp, i.toxml()
    # print other_v here????
    print >> fp, '</knownVariables>'
    print >> fp, '</variables>'
    print >> fp, '<equations dimension="{0}">'.format(len(sliced_e))
    for i in sliced_e:
      print >> fp, i.toxml()
    print >> fp, '</equations>'
    print >> fp, '<initialEquations dimension="{0}">'.format(len(slice_ie))
    for i in slice_ie:
      print >> fp, i.toxml()
    print >> fp, '</initialEquations>'
    print >> fp, '</dae>'
  print 'Created file {0}'.format( slice_filename )

def modelica_slice_file(filename, varlist):
    '''create a file base(filename)_slice.xml'''
    def existsAndNew(filename1, filename2):
        if os.path.isfile(filename1) and os.path.getctime(filename1) >= os.path.getctime(filename2):
            print "File {0} exists and is new".format(filename1)
            return True
        return False
    basename,ext = os.path.splitext(filename)
    try:
        modelicadom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        print 'Syntax Error: Input XML ', e 
        print 'Error: Input XML file is not well-formed...Quitting.'
        sys.exit(-1)
    except:
        print 'Error: Input XML file is not well-formed'
        print 'Quitting', sys.exc_info()[0]
        sys.exit(-1)
    (sliced_e, sliced_v, other_v, slice_ie) = modelicadom_slicer(modelicadom, varlist)
    slice_filename = basename + '_slice.xml'
    print >> sys.stderr, 'Creating file {0}...'.format(slice_filename)
    output_sliced_dom(slice_filename, sliced_e, slice_ie, sliced_v, other_v, modelicadom)
    #if not existsAndNew(slice_filename, filename):
      # Bug: slice created using different variables have same filename
      #output_sliced_dom(slice_filename, sliced_e, slice_ie, sliced_v, other_v, modelicadom)
    #else:
      #print 'Slice exists.'
    return (slice_filename, modelicadom)

def main():
    global dom
    filename = argCheck(sys.argv, printUsage)
    options = sys.argv[2:]
    assert '--slicewrt' in options, 'Error: Specify slice variables. {0}'.format(printUsage())
    index = options.index('--slicewrt')
    varlist = options[index+1].split(',')
    modelica_slice_file(filename, varlist)

if __name__ == "__main__":
    main()

