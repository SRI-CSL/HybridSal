import sys
import os
import xml.dom.minidom 

# ----------------------------------------------------------------------
# Usage:
# ----------------------------------------------------------------------
# Inside python call:
#  modelica_slicer.modelica_slice_file(filename, varlist)
#    where varlist = list of variable names (str)
# Command line:
#  python src/modelica_slicer.py examples/no_controls_dae.xml --slicewrt "driveLine.pTM_with_TC.torque_Converter_Lockup.clutch_lockup.phi_rel" > tmp.txt
#
#  python src/modelica_slicer.py  examples/SystemDesignTest-r663.xml  --slicewrt "driver_gear_select, shift_request_state, output_speed_torque_converter, input_speed_torque_converter, prndl" > tmp.txt
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Notes: 
# ----------------------------------------------------------------------
# 05 Aug, 2014: Using only orderedVariables for creating slices...
# 17 Aug, 2014: initialEquations absent in slice -- fixed
# 17 Aug, 2014: aliasVariables  absent in slice -- fixed
# 22 Aug, 2014: knownVars defined using other vars -- include them too!
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Algorithm for SLICER:
# ----------------------------------------------------------------------
# New algorithm for slicer:
# 1. for each eqn: compute (pre, curr, next) ORDERED variables+their aliases
# 2. for each ovar: point to eqns where it occurs as next, curr, pre
# 3. varlist, eqn -> varlist, eqn
#  if v occurs as NEXT, then add that eqn and add all curr in that eqn
#  if v occurs as CURR as sole LHS var, then add that eqn and vars
#  if v occurs as CURR in RHS and LHS is 0, then add that eqn and vars
#  else: mark v as INPUT
# output: create DAG : v -> eqn -> new v (CASE 2,3 only)
# output: path from each root to leaf -- INTERFACE
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Usage 
# ----------------------------------------------------------------------
def printUsage():
    print '''
modelica_slicer -- a slicer from Modelica DAEs; creates sliced DAE XML dump

Usage: python src/modelica_slicer.py <modelica_file.xml> --slicewrt "v1,v2,v3"

Description: This will create a file called modelica_file_slice.xml

NOTE: If it exists, the program uses file modelicaURI2CyPhyMap.json for 
   classifying variables as plant/controller/context variables.
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

def jsonfile2dict(filename):
  '''Return the dict obtained by reading given JSON file'''
  def remove_bad_chars(c):
    return c if c not in bad_chars else ''
  if not os.path.isfile(filename):
    return {}
  try:
    import json
    with open(filename, 'r') as fp:
      jsondata = fp.read()
      bad_chars = ['\n', '\r', '\\']
      jsondata = ''.join(map(remove_bad_chars, jsondata))
      d = json.loads(jsondata)
      return d
  except SyntaxError, e:
    print 'Syntax error in JSON file ', e
    sys.exit(-1)

def set_union(a, b):
  for i in b:
    if i not in a:
      a.append(i)
  return a

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
# Get LHS and RHS of a MathML equation
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Details about an equation: its nxt, curr, pre vars for LHS, RHS
# -------------------------------------------------------------------
class EDetails:
  def __init__(self, e, lhs, rhs, ovarl, cond=None):
    self.e = e
    if type(lhs) in [str, unicode]:
      self.lhs = ([], [lhs], [], [])
    else:
      nxt, curr, pre, r = [], [], [], []
      self.lhs = classify_vars_as_curr_pre( lhs, nxt, curr, pre, ovarl, r)
    nxt, curr, pre, r = [], [], [], []
    self.rhs = classify_vars_as_curr_pre( rhs, nxt, curr, pre, ovarl, r)
    if cond != None:
      self.rhs = classify_vars_as_curr_pre( cond, nxt, curr, pre, ovarl, r)
    self.allnxt = list(self.lhs[0])
    self.allnxt.extend( self.rhs[0] )
    self.allcurr = list(self.lhs[1])
    self.allcurr.extend( self.rhs[1] )
    self.allpre = list(self.lhs[2])
    self.allpre.extend(self.rhs[2])
    self.allrest = list( self.lhs[3] )
    self.allrest.extend( self.rhs[3] )
  def get_nxt(self):
    return self.allnxt
  def get_curr(self):
    return self.allcurr
  def get_pre(self):
    return self.allpre
  def get_rest(self):
    return self.allrest
  def get_lhs_var(self):
    if self.lhs[0] == [] and self.lhs[2] == [] and len(self.lhs[1])==1:
      return self.lhs[1][0] 
    return None
  def is_lhs(self, vname):
    return self.lhs == ([], [vname], [])
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Information about each variable. Dict: Var_Name -> (nxtL,currL,preL)
# ----------------------------------------------------------------------
class VInfo:
  def __init__(self):
    self.d = {}
  def update(self, v, index, value):
    if not self.d.has_key(v):
      self.d[v] = ([], [], [])
    self.d[v][index].append( value )
  def get(self, v):
    if not self.d.has_key(v):
      return ([],[],[])
    return self.d[v]
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Information about each Equation. Used for creating slice.
# Dict: Equation XML to EDetails object
# ----------------------------------------------------------------------
class EInfo:
  def __init__(self):
    self.d = {}
  def update(self, e, ovarl, vInfo):
    if e.tagName == 'equation':
      mml = getChildByTagName(e, 'MathML')
      assert mml != None, 'No MathML'
      lhs, rhs = mml_eqn_get_lhs_rhs(mml)
      e_info = EDetails( e, lhs, rhs, ovarl)
    elif e.tagName == 'whenEquation':
      mml = getChildByTagName(e, 'MathML')
      assert mml != None, 'No MathML'
      lhs, rhs = mml_eqn_get_lhs_rhs(mml)
      wcond = getChildByTagName(e, 'whenEquationCondition')
      e_info = EDetails( e, lhs, rhs, ovarl, cond=wcond)
    elif e.tagName == 'variable':
      var = e
      vname = var.getAttribute('name')
      bindvalexpr = getChildByTagName(var, 'bindValueExpression')
      if bindvalexpr == None:
        return
      bindexpr = getChildByTagName(bindvalexpr, 'bindExpression')
      if bindexpr == None:
        return
      mml = getChildByTagName(bindexpr, 'MathML')
      assert mml != None, 'No MathML'
      e_info = EDetails( e, vname, mml, ovarl)
    else:
      assert False, 'Err: Unknown tagName {0}'.format(e.tagName)
    self.d[e] = e_info
    for i in e_info.get_nxt():
      vInfo.update(i, 0, e_info)
    for i in e_info.get_curr():
      vInfo.update(i, 1, e_info)
    for i in e_info.get_pre():
      vInfo.update(i, 2, e_info)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Tree data-structure... Final slice is computed as a TREE/DAG
# ----------------------------------------------------------------------
class TreeNode:
  '''DAG. Hopefully no cycles in DAEs...'''
  def __init__(self, v):
    self.vname = v
    self.children = []
    self.label = None
  def get_name(self):
    return self.vname
  def add_child_label( self, chosen_e ):
    self.label = chosen_e
  def add_child( self, new_node ):
    self.children.append( new_node )
  def get_all_nodes_eqns(self, nodes, eqns, rest):
    if self.vname in nodes:
      return
    nodes.append( self.vname )
    if self.label != None:
      if self.label.e.tagName == 'equation':
        eqns.append( self.label.e )
      # else it is a aliasVariable, gets added to sliced_v later.
      for i in self.label.get_rest():
        if i not in rest:
          rest.append(i)
    for i in self.children:
      i.get_all_nodes_eqns( nodes, eqns, rest )
    return 
  def __str__(self):
    def my_str(node, done):
      if node in done:
        return node.vname+'#'
      else:
        done.append(node)
        ans = self.vname + '('
        for i in self.children:
          ans += my_str(i, done)
          ans += ', '
        ans += ')'
      return ans
    done = []
    return my_str(self, done)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Helpers for creating data-structure from eqns and known-variables.
# ----------------------------------------------------------------------
def kvarsxml2dictDS(kvars, ovarl, eInfo, vInfo):
  return eqnsxml2dictDS(kvars, ovarl, eInfo, vInfo)

def eqnsxml2dictDS(eqns, ovarl, eInfo, vInfo):
  for e in eqns:
    eInfo.update( e, ovarl, vInfo)
  return (eInfo, vInfo)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Routine for picking the defining equation for a variable
# ----------------------------------------------------------------------
def black_list( e_info ):
  '''some equations will be blacklisted. RULES are:
     if table and driver occur in any variable name occurring in eqn'''
  def goodr1( vname ):
    return vname != 'time' and (vname.find('table') == -1 or vname.find('driver') == -1)
  good = all([goodr1(i) for i in e_info.get_curr()])
  good = good and all([goodr1(i) for i in e_info.get_rest()])
  return not good

def pick_defining_equation( var_name, nxtL, currL, preL ):
  '''if v occurs as NEXT, then add that eqn and add all curr in that eqn
     if v occurs as CURR as sole LHS var, then add that eqn and vars
     if v occurs as CURR in RHS and LHS is 0, then add that eqn and vars
     else: mark v as INPUT'''
  print >> sys.stderr, 'For {0}: {1}, {2}, {3}'.format( var_name, len(nxtL), len(currL), len(preL))
  if len(nxtL) == 1:
    print 'For variable {0}, found dx/dt equation'.format(var_name)
    return nxtL[0]
  if len(nxtL) > 1:
    print >> sys.stderr, 'Warning: {1} equations contain d{0}/dt'.format(var_name, len(nxtL))
    print >> sys.stderr, 'Warning: Need more analysis. Picking arbitrarily.'
    return nxtL[0]
  new_currL = []
  for e_info in currL:
    lhs_var = e_info.get_lhs_var()
    if lhs_var == var_name and len(e_info.get_nxt()) == 0:
      print >> sys.stderr, 'found x = sth equation, checking...'
      del new_currL
      if black_list( e_info ):
        return None
      print >> sys.stderr, 'Using {0} = sth equation'.format(var_name)
      return e_info
    elif lhs_var == None:
      new_currL.append( e_info )
    # else: equation defines some variable, so ignore it...
  print >> sys.stderr, '{0} choices remaining'.format(len(new_currL))
  for e_info in new_currL:
    if len(e_info.get_nxt()) == 0:
      print >> sys.stderr, 'Picking ', valueOf(e_info.e)
      return e_info
  return None
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Construct TREEs by going tracing what var depends on what others
# ----------------------------------------------------------------------
def varbackwardsREC( todo_nodes, eInfo, vInfo, processed ):
  while len(todo_nodes) != 0:
    node = todo_nodes.pop()
    node_name = node.get_name()
    if node_name in processed.keys():
      continue
    processed[node_name] = node
    (nxtL, currL, preL) = vInfo.get( node_name )
    chosen_e = pick_defining_equation( node_name, nxtL, currL, preL )
    if chosen_e != None:
      node.add_child_label( chosen_e )
      e_nxtL = list( chosen_e.get_nxt() )
      e_nxtL.extend( chosen_e.get_curr() )
      e_nxtL.extend( chosen_e.get_pre() )
      for vname in e_nxtL:
        if vname not in processed.keys():
          new_node = TreeNode(vname)
          todo_nodes.append( new_node )
          node.add_child( new_node )
        else:
          new_node = processed[vname]
          node.add_child( new_node )	# It is a DAG now
    else:
      print >> sys.stderr, '{0}: No defining equation found'.format(node_name )
      print >> sys.stderr, 'Assuming it is an INPUT'
  return

def varbackwardsDS( varlist, eInfo, vInfo): 
  nodes = []
  for v in varlist:
    nodes.append( TreeNode( v ) )
  todo_nodes, processed_nodes = list( nodes ), {}
  varbackwardsREC( todo_nodes, eInfo, vInfo, processed_nodes)
  print >> sys.stderr 'varbackwardsDS terminated!!!!!'
  return nodes
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Compute data-structures and the slice TREE
# ----------------------------------------------------------------------
def new_wrapper(varlist, eqns, kvars, ovarl):
  '''use info in eqns and kvars to construct data-structs eInfo,vInfo
  Then use these DS to go backwards from varlist and compute slice'''
  # populate data-structures
  eInfo, vInfo = EInfo(), VInfo()
  (eInfo, vInfo) = eqnsxml2dictDS(eqns, ovarl, eInfo, vInfo)
  (eInfo, vInfo) = kvarsxml2dictDS(kvars, ovarl, eInfo, vInfo)

  # compute the tree; returns the roots of the trees
  roots = varbackwardsDS( varlist, eInfo, vInfo)

  # From the trees, extract sliced_v, sliced_kv, sliced_e, sliced_ie.....
  sliced_v, sliced_e, sliced_kv = [], [], []
  for root in roots:
    root.get_all_nodes_eqns( sliced_v, sliced_e, sliced_kv )
  return (sliced_v, sliced_e, sliced_kv)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Given MathML expression, return its dx/dt, x, pre(x) variables.
# ----------------------------------------------------------------------
def classify_vars_as_curr_pre( mml, nxt, curr, pre, ovarl, rest ):
  '''recurse and clasify each var in mml expr as nxt, curr or pre'''
  if mml.tagName == 'ci':
    allvars = [ mml ]
  else:
    allvars = mml.getElementsByTagName('ci')
  for i in allvars:
    varname = valueOf(i).strip()
    if varname not in ovarl:
      if varname not in rest:
        rest.append( varname )
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
  return (nxt, curr, pre, rest)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Matlab names and Modelica names are NOT identical. Do suffix MATCH.
# ----------------------------------------------------------------------
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
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# Extend orderedVariables by their aliases before MATCHING.
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Slice of equations, given relevant variables and state variables list
# ----------------------------------------------------------------------
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
# Map variable name to their corresponding XML node in XMLDAEdump.xml
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
# Add time variable explicitly to the Modelica model
# ----------------------------------------------------------------------
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
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# The two main functions... slice and then output to file.
# ----------------------------------------------------------------------
def modelicadom_slicer(modelicadom, varlist, meta={}):
    '''dom = modelicaXML dom; varlist = variables wrt which slice
       output a tuple with sliced_e, sliced_v, etc.'''
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
    wequationL = equations.getElementsByTagName('whenEquation')
    equationL.extend( wequationL )

    (sliced_v, sliced_e, sliced_kv) = new_wrapper( varlist, equationL, kvars, ovarl )

    # compatible with names in old code
    other_v = sliced_kv
    slice_e = sliced_e

    print >> sys.stderr, 'sliced_v is '
    print >> sys.stderr, sliced_v
    print >> sys.stderr, 'other_v obtained from vars(sliced_e) - sliced_v '
    print >> sys.stderr, other_v

    # get all relevant initial Equations the same way...
    init_equations = getChildByTagName(ctxt, 'initialEquations')
    if init_equations != None:
      iequationL = init_equations.getElementsByTagName('equation')
      (slice_ie, other_v1) = getRelevantE(iequationL, sliced_v, ovarl)
      other_v = set_union(other_v, other_v1)
    else:
      slice_ie = []
    print >> sys.stderr, 'other_v after processing init equations'
    print >> sys.stderr, other_v

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
    assert len(rest3) == 0, 'Err:Rest3 has {0} elements: {1}'.format(len(rest3), rest3)
    if len(rest2) != 0:
      print 'WARNING: Rest2 has {0} elements: {1}'.format(len(rest2), rest2)

    return ( slice_e, sliced_v, sliced_kv, slice_ie )

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
# ----------------------------------------------------------------------
 
# ----------------------------------------------------------------------
# if calling slicer through python, this is the function to call.
# ----------------------------------------------------------------------
def modelica_slice_file(filename, varlist):
    '''create a file base(filename)_slice.xml.
       Wrapper over modelicadom_slicer and output_sliced_dom
    '''
    assert os.path.isfile(filename), 'ERROR: File does not exist'
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
    dirname = os.path.dirname(filename)
    jsonfile = os.path.join(dirname, 'modelicaURI2CyPhyMap.json')
    d = jsonfile2dict( jsonfile )
    (sliced_e, sliced_v, other_v, slice_ie) = modelicadom_slicer(modelicadom, varlist, meta=d)
    slice_filename = basename + '_slice.xml'
    print >> sys.stderr, 'Creating file {0}...'.format(slice_filename)
    output_sliced_dom(slice_filename, sliced_e, slice_ie, sliced_v, other_v, modelicadom)
    return (slice_filename, modelicadom)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# if calling slicer through command-line then ...
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
    if not(ext == '.xml'):
        print 'ERROR: Unknown extension {0}; expecting .xml'.format(ext)
        printUsage()
        sys.exit(-1)
    if not(os.path.isfile(filename)):
        print 'ERROR: File {0} does not exist'.format(filename)
        printUsage()
        sys.exit(-1)
    return filename

def main():
    global dom
    filename = argCheck(sys.argv, printUsage)
    options = sys.argv[2:]
    assert '--slicewrt' in options, 'Error: Specify slice variables. {0}'.format(printUsage())
    index = options.index('--slicewrt')
    varlist = options[index+1].split(',')
    modelica_slice_file(filename, varlist)
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
if __name__ == "__main__":
    main()
# ----------------------------------------------------------------------

