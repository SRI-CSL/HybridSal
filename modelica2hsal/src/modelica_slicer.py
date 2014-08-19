import sys
import os
import ddae
import xml.dom.minidom 

# Notes: TODO
# handling of kvars at line 356 - please improve
# for all kvars; just print variablevalue pairs.
# for all missing ones; raise an alarm
# 5 Aug, 2014: Using only orderedVariables for creating slices...

# 17 Aug, 2014: initialEquations absent in slice
# 17 Aug, 2014: aliasVariables  absent in slice

# Notes for SLICER:
# 2. Maintain equivalence class of variables
#  if x+y=10 is an equation, then x,y are in the same class
#  if dx/dt = x+y+z, then x points_to y,z
# compute influence variables modulo equivalence...

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

# Helpers for creating DOM nodes
def helper_create_app(tag, childs, position = None, arity = None):
    global dom
    node = dom.createElement(tag)
    if arity != None:
        node.setAttribute('arity', str(arity))
    if position != None:
        node.setAttribute('col', str(position.col))
        node.setAttribute('line', str(position.line))
    for i in childs:
        if i == None:
            print 'ERROR: Null node found, tag = %s', tag
            for j in childs:
                if j != None:
                    print j.toprettyxml() 
        else:
            node.appendChild(i)
    return node 

def helper_create_tag_val(tag, val, position = None):
    global dom
    node = dom.createElement(tag)
    if position != None:
        node.setAttribute('col', str(position.col))
        node.setAttribute('line', str(position.line))
    node.appendChild( dom.createTextNode( val ) )
    return node 

def helper_collect_child(node, base=0):
    ans = list()
    for i in node:
        ans.append(i[base])
    return ans
# -------------------------------------------------------------------

# -------------------------------------------------------------------
def grand_children_count(node):
    child = getArg(node,1)
    childs = getArgs(child)
    return len(childs)

def getArgs(node):
    ans = []
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            ans.append(i)
    return ans

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None

def mathml2myxml(ml):
    math = getArg(ml, 1)
    assert math.tagName == 'math', 'MathML expected math, found {0}'.format(math.tagName)
    ml_expr = getArg(math, 1)
    if ml_expr == None: 
        print 'Null MathML found'
        return None
    return mlexpr2myexpr(ml_expr)

def mlexpr2myexpr(mle):
    tag = mle.tagName
    if tag == 'cn':
        return helper_create_tag_val('number',valueOf(mle)) 
    elif tag == 'ci':
        return helper_create_tag_val('identifier',valueOf(mle))
    elif tag == 'apply':
        return mlapply2myexpr(mle)
    elif tag == 'matrix' or tag == 'matrixrow':
        mlargs = getArgs(mle)
        args = [ mlexpr2myexpr(i) for i in mlargs ]
        ans = helper_create_app('set', args)
        ans.setAttribute('cardinality', str( len(args) ) )
        return ans
    else:
         assert False, 'Code missing for {0}'.format(tag)
        
def mlapply2myexpr(mle):
    arg1 = getArg(mle,1)
    op = arg1.tagName
    opmap = {'divide':'/','times':'*','plus':'+','equivalent':'==','gt':'>','lt':'<','ge':'>=','le':'<='}
    if op in ['true','false','True','False']:
        return helper_create_tag_val('string', op)
    elif op == 'piecewise':
        mlarg1 = getArg(arg1, 1) 	# piece
        mlarg2 = getArg(arg1, 2)  	# otherwise
        assert mlarg1.tagName == 'piece', 'tag piece expected, found {0}'.format(mlarg1.tagName)
        assert mlarg2.tagName == 'otherwise', 'tag ow expected, found {0}'.format(mlarg2.tagName)
        mlval1 = getArg(mlarg1, 1)
        mlcond = getArg(mlarg1, 2)
        mlval2 = getArg(mlarg2, 1)
        val1 = mlexpr2myexpr(mlval1)
        val2 = mlexpr2myexpr(mlval2)
        cond = mlexpr2myexpr(mlcond)
        return helper_create_app('IF', [cond, val1, val2])
    elif opmap.has_key(op): # op in ['divide','times','plus','equivalent']:
        arg1 = mlexpr2myexpr(getArg(mle,2))
        arg2 = mlexpr2myexpr(getArg(mle,3))
        op1 = opmap[op]
        op2 = helper_create_tag_val('BINARY_OPERATOR', op1)
        return helper_create_app('BAPP', [op2,arg1,arg2])
    elif op == 'minus':
        mlargs = getArgs(mle)
        if len(mlargs) == 3:
            arg1 = mlexpr2myexpr( mlargs[1] )
            arg2 = mlexpr2myexpr( mlargs[2] )
            op2 = helper_create_tag_val('BINARY_OPERATOR', '-')
            return helper_create_app('BAPP', [op2,arg1,arg2], None, 2)
        elif len(mlargs) == 2:
            arg1 = mlexpr2myexpr( mlargs[1] )
            op2 = helper_create_tag_val('UNARY_OPERATOR', '-')
            return helper_create_app('UAPP', [op2,arg1], None, 1)
    elif op == 'diff': 	# has 3 args; return semiLinear(x,y,z)
        arg1 = mlexpr2myexpr(getArg(mle,2))
        return helper_create_app('der', [arg1])
    elif op == 'pre': 	# has 3 args; return semiLinear(x,y,z)
        arg1 = mlexpr2myexpr(getArg(mle,2))
        return helper_create_app('pre', [arg1])
    # elif op == 'semiLinear': 	# has 3 args; return semiLinear(x,y,z)
    elif op == 'initial':
        return helper_create_app('INITIAL', [], None, 0)
    elif op == 'transpose': # change to set too....
        arg1 = getArg(mle, 2)
        if arg1.tagName == 'vector':
            vector_elmts = getArgs(arg1)
            myexpr_elmts = [ mlexpr2myexpr(k) for k in vector_elmts ]
            ans = helper_create_app('set', myexpr_elmts)
            ans.setAttribute('cardinality', str( len(myexpr_elmts) ) )
            return ans 
        else:
            assert False, 'transpose applied to something not a vector; cant handle'
    else: # op in ['semiLinear', 'noEvent', etc.]
        # print 'Operator {0} is being generic handled'.format(op)
        arity2op = {1:'UAPP',2:'BAPP',3:'TAPP',4:'QAPP',5:'NAPP',6:'NAPP'}
        mlargs = getArgs(mle)
        args = [ mlexpr2myexpr( i ) for i in mlargs[1:] ]
        arity = len(args)
        if arity >= 1 and arity <= 6:
          op1 = arity2op[arity]
        elif arity >= 7:
          print "Warning: NEW Operator {0} has arity {1}".format(op,arity)
          op1 = arity2op[6]
        else:
          print "Warning: NEW Operator {0} has arity ZERO? {1}?".format(op,arity)
          print "Warning: Turning {0} to an identifier??".format(op,arity)
          return helper_create_tag_val('identifier', op)
        op2 = helper_create_tag_val('op', op)
        args.insert(0, op2)
        return helper_create_app(op1, args, None, arity)

def wrap_in_mathml(node):
    return helper_create_app('MathML', [helper_create_app('math',[node])])

# -------------------------------------------------------------------

# -------------------------------------------------------------------
def remove_nested_mathml(node, parentnode):
    '''in place removal; destructive operator'''
    args = getArgs(node)
    for argi in args:
        node = remove_nested_mathml(argi, node)
    if node.tagName == 'MathML':
        newnode = getArg( getArg(node, 1), 1)
        parentnode.replaceChild(newChild=newnode,oldChild=node)
    return parentnode

def getMathMLclone(node, backup_val):
    mathml = getChildByTagName(node, 'MathML')
    if mathml == None:
        global dom
        ans = dom.createElement('MathML')
        ans1 = dom.createElement('math')
        ans.appendChild( ans1 )
        node.appendChild( ans )
        num_gc = 0
    else:
        # assert mathml != None, 'MathML missing'
        ans = mathml.cloneNode(True)
        num_gc = grand_children_count(ans)
        # sick case: MathML parses, but as nested MathML exprs!!!
        ans = remove_nested_mathml( getChildByTagName(ans, 'math'), ans )
    if num_gc == 0:	# sick case: MathML fails to parse modelica expr!!!
        print 'NOTE: Missing MathML expr; using fallback string'
        ans.setAttribute('string', backup_val)
    return ans

def getMathMLcloneEqn(node, backup_val):
    def mathml_equation_parse(mathmleqn):
        eml = getArg( getArg(mathmleqn, 1), 1)
        if eml == None:
            return None	# we will use STRING repr to get correct parse
        assert eml.tagName == 'apply', 'Expecting apply, found {0}'.format(eml.toprettyxml())
        args = getArgs(eml)
        op = args[0]
        assert op.tagName == 'equivalent', 'Expecting equivalent, found {0}'.format(eml.toprettyxml())
        return (args[1], args[2])

    def topleveleqn(mathmleqn):
        "mathML equation -> equation mathML-LHS mathML-rhs "
        arg12 = mathml_equation_parse( mathmleqn )
        if arg12 == None:
            return (mathmleqn, None)
        (arg1, arg2) = arg12
        lhs = wrap([arg1])
        rhs = wrap([arg2])
        ans = helper_create_app('equation', [lhs,rhs])
        return (ans, (arg1, arg2))

    mathml = getChildByTagName(node, 'MathML')
    wrap = lambda x: helper_create_app('MathML', [helper_create_app('math',x)])
    if mathml == None or grand_children_count(mathml) == 0:
        global dom
        (head, sep, tail) = backup_val.partition(':=')
        if sep == '':
            (head, sep, tail) = backup_val.partition('=')
        assert sep != '', 'Expected to see = or := in equation {0}'.format(backup_val)
        lhs = wrap([])
        lhs.setAttribute('string', head)
        rhs = wrap([])
        rhs.setAttribute('string', tail)
        ans = helper_create_app('equation', [lhs,rhs])
        return (ans, None)
    else:
        # assert mathml != None, 'MathML missing'
        ans = mathml.cloneNode(True)
        # sick case: MathML parses, but as nested MathML exprs!!!
        ans = remove_nested_mathml( getChildByTagName(ans, 'math'), ans )
        return topleveleqn( ans )

def getInitialValue(node):
    ival = node.getElementsByTagName('initialValue')
    if ival == None or len(ival) == 0:
        return None
    return getMathMLclone(ival[0], ival[0].getAttribute('string'))

def getVariableValue(var, tags = ['bindExpression', 'initialValue']):
    "return value of the variable by looking at different places"
    # tags = [ 'bindExpression', 'initialValue' ]
    for i in tags:
        val = var.getElementsByTagName(i)
        if val != None and len(val) > 0:
            # value = val[0].getAttribute('string')
            ans = getMathMLclone( val[0], val[0].getAttribute('string') )
            return (ans, i == 'initialValue')
    name = var.getAttribute('name')
    if name.endswith('OnFileRead'):
        one = helper_create_tag_val('cn','1')
        return (wrap_in_mathml(one), False)
    return (None, False)

def printFixedParametersNew(varList, tags=['bindExpression']):
    "return a list of variablevalue daexml-nodes"
    ans = []
    varvals = []
    for i in varList:
        if i.getAttribute('type') == 'String' and i.getAttribute('fixed') == 'true':
          continue
        (value, isInit) = getVariableValue(i, tags)
        name = i.getAttribute('name')
        if value != None:
            var = helper_create_tag_val('identifier',name)
            varval = helper_create_app('variablevalue', [var, value])
            varvals.append(varval)
        else:
            ans.append(i)
    return (varvals, ans)

def printFixedParameters(varList, varTypeList, valueTagList):
    "return a list of variablevalue daexml-nodes"
    ans = []
    varvals = []
    for i in varList:
        # fixed = i.getAttribute('fixed')
        param = i.getAttribute('variability')
        inout = i.getAttribute('direction')
        isfixed = i.getAttribute('fixed')
        if param in varTypeList and inout != 'input':
            (value, isInit) = getVariableValue(i, valueTagList)
            name = i.getAttribute('name')
            if value != None:
                var = helper_create_tag_val('identifier',name)
                varval = helper_create_app('variablevalue', [var, value])
                varvals.append(varval)
                # print >> fp, '{0} = {1}'.format(name, value)
            else:
                ans.append(name)
    return (varvals, ans)

def printFixedParametersZero(varList):
    '''This is a hack. Set remaining params to ZERO'''
    ans = []
    varvals = []
    for i in varList:
        print 'WARNING: Unknown parameter {0} set to 0'.format(i)
        var = helper_create_tag_val('identifier',i)
        zero = helper_create_tag_val('cn','0')
        zero = helper_create_app('math',[zero])
        zero = helper_create_app('MathML',[zero])
        varval = helper_create_app('variablevalue', [var, zero])
        varvals.append(varval)
        # print >> fp, '{0} = 0'.format(i)
    return (varvals,ans)

def getVarValFromAlgo( simpleEquations, leftOutVars1 ):
    if simpleEquations == None or len(simpleEquations) == 0:
        return ([], leftOutVars1 )
    done_vars = []
    varvals = []
    childNodes = simpleEquations[0].getElementsByTagName('equation')
    childNodes1 = simpleEquations[0].getElementsByTagName('algorithm')
    childNodes.extend(childNodes1)
    for child in childNodes:
        code = valueOf(child)
        if code == None:
            continue
        for dangling_var in leftOutVars1:
            var_name = dangling_var.getAttribute('name').strip()
            index1 = code.find( var_name )
            if index1 == -1:
                continue
            index2 = code.find( ';', index1 )
            index3 = code.find( ':=', index1 )
            if index2 == -1 or index3 == -1:
                print 'Huh?: expected var := expr ; unexpected syntax found'
                continue
            rhs = ddae.parse_expr( code[index3+2:index2] )
            var = helper_create_tag_val('identifier', var_name)
            varvals.append(helper_create_app('variablevalue', [var, rhs]))
            done_vars.append( dangling_var )
    leftOutVars = [ i for i in leftOutVars1 if i not in done_vars ]
    return (varvals, leftOutVars)

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
  '''aliases...'''
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
      other_vars.extend( restv )
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
def modelicadom2daexml(modelicadom, varlist):
    "dom = modelicaXML dom; output daexml DOM... WITH MathMLs now"
    global dom
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, "daexml", None)
    ctxt = modelicadom.getElementsByTagName('dae')[0]
    variables = getChildByTagName(ctxt, 'variables')
    equations = getChildByTagName(ctxt, 'equations')
    zeroCrossing = getChildByTagName(ctxt, 'zeroCrossingList')
    arrayOfEqns = getChildByTagName(ctxt, 'arrayOfEquations')
    algorithms = getChildByTagName(ctxt, 'algorithms')
    functions = getChildByTagName(ctxt, 'functions')
    assert variables != None, 'Variables not found in input XML file!'
    # Now start printing .dae file
    tmp = getChildByTagName(variables, 'orderedVariables')
    ovars = tmp.getElementsByTagName('variable') if tmp != None else []
    ovarl = [i.getAttribute('name') for i in ovars]

    kvars = []
    tmp = getChildByTagName(variables, 'externalVariables')
    kvars.extend( tmp.getElementsByTagName('variable') if tmp != None else [] )
    tmp = getChildByTagName(variables, 'aliasVariables')
    aliases = tmp.getElementsByTagName('variable') if tmp != None else []
    kvars.extend( aliases )

    ## update varlist given ovarl
    ovarl = extend_ovarl( ovarl, aliases )
    # ovarl.extend( [i.getAttribute('name') for i in aliases] )
    varlist = find_matching_vars( varlist, ovarl )
    # Now, do a LFP fixpoint on
    # var,eqn -> newvar,neweqn adding keeping id's
    equationL = equations.getElementsByTagName('equation')
    union_find,  relies_on = UnionFind(), LabeledBinaryRelation()
    (uf, reliesOn) = eqnsxml2dict(equationL, union_find, relies_on, ovarl)
    # print 'reliesOn after equations before normalizing...'
    # print reliesOn
    (uf, reliesOn) = kvars2dict( kvars, uf, reliesOn, ovarl )
    # print 'reliesOn before normalizing...'
    # print reliesOn
    reliesOn.normalize( uf )
    # print 'Done creating UF and the reliesOn DS'
    # print uf
    # print reliesOn
    (relevantv, relevante) = varbackwards( varlist, union_find, relies_on )
    print 'No. of relevant nodes = {0}:'.format(len(relevantv))
    print relevantv 
    print 'No. of relevant equations = {0}:'.format(len(relevante))
    print relevante
    sliced_v, roots = [], []
    for i in relevantv:
      print 'Equivalence class of {0}'.format(i)
      rooti = union_find.find( i )
      if rooti in roots:
        continue
      roots.append( rooti )
      eq_class = union_find.get_eq_class( i )
      sliced_v.extend(eq_class)
      print eq_class
    print 'Num of different eq classes = {0}'.format(len(roots))
    print 'Sum of all eq classes = {0}'.format(len(sliced_v))
    # get all equations containing only vars in sliced_v
    (slice_e, other_v) = getRelevantE(equationL, sliced_v, ovarl)
    print 'Number of relevant equations = {0}'.format(len(slice_e))
    # sliced_v -> name -> XML map using ovars
    (sliced_v, rest) = map_name_to_xml( sliced_v, ovars)
    tmp = getChildByTagName(variables, 'knownVariables')
    kvars = tmp.getElementsByTagName('variable') if tmp != None else []
    (other_v, rest2) = map_name_to_xml(other_v, kvars)
    print 'Rest has {0} elements'.format(len(rest))
    print 'Rest2 has {0} elements'.format(len(rest2))
    return ( slice_e, sliced_v, other_v )
    # sys.exit(1)
    # return (relevantv, relevante)

'''
    # print >> fp, '#####{0}'.format('continuousState')
    statevars = []
    for i in ovars:
        if i.getAttribute('variability') == 'continuousState':
            newvar = helper_create_tag_val('identifier', i.getAttribute('name'))
            statevars.append(newvar)
    continuousState = helper_create_app('continuousState', statevars, None, len(statevars))
    # print 'continuousState XML creation done............'
    # print >> fp, '#####{0}'.format('discreteState')
    statevars = []
    for i in ovars:
        if i.getAttribute('variability') == 'discrete':
            newvar = helper_create_tag_val('identifier', i.getAttribute('name'))
            statevars.append(newvar)
    discreteState = helper_create_app('discreteState', statevars, None, len(statevars))
    # print 'discreteState XML creation done............'
    # print constants or parameters with their values
    # print >> fp, '#####{0}'.format('knownVariables')
    (vv1,leftOutVars1) = printFixedParametersNew(kvars)
    if len(leftOutVars1) > 0:
        print 'Note: {0} known variable do not have a bindExpression; for e.g., {1}. Trying initialValue'.format(len(leftOutVars1), leftOutVars1[0].getAttribute('name'))
        print 'Using initialValue as the values for these kvars'
        (vv2,leftOutVars1) = printFixedParametersNew(leftOutVars1, ['initialValue'])
        vv1.extend(vv2)
    #(vv2,leftOutVars1) = printFixedParametersZero(leftOutVars1)
    #(vv3,leftOutVars1)  = printFixedParameters(kvars, ['continuous'])
    if len(leftOutVars1) > 0:
        print 'Note: {0} known vars have no bind expr and no initialValue; for e.g., {1}'.format(len(leftOutVars1),leftOutVars1[0].getAttribute('name'))
        print 'Trying to find bindExpression from initialEquations section'
        simpleEquations = ctxt.getElementsByTagName('initialEquations')
        (vv3,leftOutVars1) = getVarValFromAlgo( simpleEquations, leftOutVars1 )
        print 'Found values from initialEquations for {0} vars'.format(len(vv3))
        vv1.extend(vv3)
    if len(leftOutVars1) > 0:
        print 'WARNING: {0} known vars have NO bindexpr/initialValue/initialEquation; for e.g., {1}'.format(len(leftOutVars1),leftOutVars1[0].getAttribute('name'))
    # TODO: the following line is NOT SOUND.....
    (vv4, leftOutVars)  = printFixedParameters(ovars, ['continuous'],['bindExpression'])
    leftOutVars.extend(leftOutVars1)
    print 'Note: {0} ordered vars have bind exprs; {1} ordered vars remaining now...'.format(len(vv4),len(leftOutVars))
    #vv1.extend(vv2)
    #vv1.extend(vv3)
    vv1.extend(vv4)
    # 
    assert equations != None, 'No Equations found in input XML file!!'
    equationL = equations.getElementsByTagName('equation')
    eqns = []
    print 'Note: Processing {0} equations to find var=val equations'.format(len(equationL))
    for i in equationL:
        (val, lhsrhs) = getMathMLcloneEqn( i, valueOf(i) )
        # lhsrhs = mathml_equation_parse( val )
        if lhsrhs == None:	# No MathML parse for the equation!!!
            eqns.append( val )
            continue
        (lhs, rhs) = lhsrhs
        lhs = valueOf(lhs).strip()
        if lhs in leftOutVars:
            var = helper_create_tag_val('identifier', lhs)
            rhs = wrap_in_mathml(rhs)
            varval = helper_create_app('variablevalue', [var, rhs])
            vv1.append(varval)
        else:
            eqns.append( val )
    print 'Note: Found {0} var=val equations'.format(len(equationL)-len(eqns))
    knownVariables = helper_create_app('knownVariables', vv1, None, len(vv1))
    knownVariables.setAttribute('arity',str(len( vv1 )))
    # print 'knownVariables XML creation done............'
    equationL = equations.getElementsByTagName('whenEquation')
    for i in equationL:
        (val, lhsrhs) = getMathMLcloneEqn( i, valueOf(i) )
        eqns.append( val )
    # print >> fp, '#####equations'
    equations = helper_create_app('equations', eqns, None, len(eqns))
    equations.setAttribute('arity',str(len( eqns )))
    # print 'Equation XML creation done............'
    # print >> fp, '#####initializations'
    inits = []
    for node in statevars:
        val0 = getInitialValue(node)
        if val0 != None:
            initid = helper_create_tag_val('initidentifier', node.getAttribute('name'))
            eqn = helper_create_app('equation', [initid, val0])
            inits.append(eqn)
            #print >> fp, '{0} = {1}'.format(node.getAttribute('name'), val0)
    initializations = helper_create_app('initializations', inits, None, len(inits))
    #print 'Initializations XML creation done............'
    allnodes = [continuousState, discreteState, knownVariables, equations, initializations]
    ans = helper_create_app('source_text', allnodes)
    dom.documentElement.appendChild(ans)
    return dom
'''

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
    modelica2daexml(filename, sys.argv[2:])

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
    orderedVars_varlists = getElementsByTagTagName(dom2, 'orderedVariables', 'variablesList')
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
            name = valueOf(identifier).strip()
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

def output_sliced_dom(slice_filename, sliced_e, sliced_v, other_v, dom):
  '''output XML in the given filename'''
  with open(slice_filename, 'w') as fp:
    print >> fp, '''
<?xml version="1.0" encoding="UTF-8"?>
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
    print >> fp, '</equations dimension="{0}">'.format(len(sliced_e))
    for i in sliced_e:
      print >> fp, i.toxml()
    print >> fp, '</equations>'
    print >> fp, '</dae>'
  print 'Created file {0}'.format( slice_filename )

def modelica2daexml(filename, options = []):
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
    if '--addTime' in options:
        modelicadom = addTime(modelicadom)
    print >> sys.stderr, 'Creating .daexml file......'
    if '--slicewrt' in options:
      index = options.index('--slicewrt')
      varlist = options[index+1].split(',')
      (sliced_e, sliced_v, other_v) = modelicadom2daexml(modelicadom, varlist)
      slice_filename = basename + '_slice.xml'
      if not existsAndNew(slice_filename, filename):
        # Bug: slice created using different variables have same filename
        output_sliced_dom(slice_filename, sliced_e, sliced_v, other_v, modelicadom)
    # now parse the dae into daexml
    else:
      print 'Specify which variables to slice for'
      printUsage()
      sys.exit(1)
    return (slice_filename, modelicadom)

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
