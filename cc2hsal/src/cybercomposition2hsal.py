# Translating CyberComposition XML representation of Simulink/Stateflow models to HybridSal

# Algorithm:
# 1. Each primitive block is first translated into a local 'Component' object 
# 2. Each subsystem is translated to a 'Component' object -- by 'composing' its subsystems
# 3. Do this recursively all the way to the top.

# Latest changes: 09/28/2014
# 1. Component class has a method 'divide2mult' that rewrites division to multiplication
# 2. Component class has a method 'move_to_params' that will make local vars->global params
# 3. Parse properties' XML using minidom parser; if fails, then rewrite the XML string
# 4. Global parameters are printed in a certain order. Eg. x=0 first; then y=x+3;
# 5. Code for Compose and projection on transitions added
# 6. Code for Compose on initializations added: ParameterRef init used if Simulink:Data not init-ed.
# 7. Code for composing property added.

# INTERFACE: (base_filename,propNameList) = cybercomposition2hsal(cc_xml_filename)

import sys
import os
import copy
import xml.dom.minidom 

def printUsage():
    print '''
cybercomposition2hsal -- a converter from CyberComposition to HSAL file

Usage: python cybercomposition2hsal.py <cybercomposition.xml>

Description: This will create a file called <cybercomposition.hsal>
    '''

# -------------------------------------------------------------------
testStr = '''<?xml version="1.0" encoding="UTF8" standalone="no" ?>
<ltlProperties>
   <ltlProperty expr="[](((y == 1) &amp; !(y == 2) &amp; &lt;&gt;(y == 2)) -&gt; ((x == 1) -&gt; (!(y == 2)U ((x == 2) &amp; !(y == 2)))) U(y == 2))" name="ResponseProperty" type="Response"/>
   <ltlProperty expr="[]((x == 0 &amp;&amp; y == 0) -&gt; &lt;&gt;(x == 1 &amp;&amp; y == 1))" name="ResponseProperty" type="Response"/> 
</ltlProperties>
'''

testStr2 = '''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<ltlProperties>
   <ltlProperty expr="[](y == 1)" name="ResponseProperty" type="Response"/>
</ltlProperties>
'''

testStr3 = '''<?xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot; standalone="no" ?>
<ltlProperties>
   <ltlProperty expr=&quot;[](y == 1)&quot; name=&quot;ResponseProperty&quot; type=&quot;Response&quot;/>
</ltlProperties>
'''
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# LTL-XML-string -> XMLminidom parse -> extract LTL string -> SAL string
# -------------------------------------------------------------------
def process_propStr(componentObj):
  '''Parse propstr - convert to SAL property'''
  def match_brac_index( propstr, i, leftbrac='(', rightbrac=')'):
    '''return index j s.t. propstr[j-1] is matching ')' for '(' at propstr[i+]'''
    start = i
    length = len(propstr)
    while start < length and propstr[start] == ' ' :
      start += 1
    assert start < length and propstr[start] == leftbrac, 'ERR: Expecting {3} in LTL property {0} at index {1}+; but start={2}'.format(propstr,i,start,leftbrac)
    end, count = start + 1, 1
    while end < length and count > 0:
      if propstr[end] == rightbrac:
        count = count - 1
      elif propstr[end] == leftbrac:
        count = count + 1
      end = end + 1
    assert end <= length and propstr[end-1] == rightbrac, 'ERR: Closing {0} missing in LTL property {1} at end position {2}'.format(rightbrac, propstr, end)
    # The following is a hack for handling !(something) U (something)
    if rightbrac == '(' and end < length and propstr[end] == '!':
      end += 1
    return end
  def remove_U(propstr, op):
    '''replace (A U B) by U(A, B); op = U'''
    def find_pos(propstr, op):
      '''find index of op in propstr'''
      tests = [ ' '+op+' ',  ')'+op+'(',  ')'+op+' ',  ' '+op+'(' ]
      for test in tests:
        i = propstr.find( test )
        if i != -1:
          return i + 1
      return -1
    pos = find_pos(propstr, op)
    if pos == -1:
      return propstr
    # now pos points to the index of U in propstr
    # print 'found op {0} at position {1} in {2}'.format( op, pos, propstr )
    right_end = match_brac_index(propstr, pos+1, '(', ')') 
    propstr_reverse = propstr[pos::-1]
    left_begin = pos+1 - match_brac_index(propstr_reverse, 1, ')', '(')
    ltlstr = '{0} {4}({1},{2}) {3}'.format(propstr[0:left_begin], propstr[left_begin:pos], propstr[pos+1:right_end], propstr[right_end:], op)
    # print 'done ', ltlstr
    return ltlstr
  def remove_F(propstr, ff, xx):
    ltlstr = propstr
    while ltlstr.find(ff) != -1:
      i = ltlstr.find(ff)
      i += len(ff)
      j = match_brac_index( ltlstr, i, '(', ')' )
      newstr = '({0} OR {1}{0} OR {1}({1}{0}) OR {1}({1}({1}{0})))'.format(ltlstr[i:j],xx)
      ltlstr = ltlstr[0:i-len(ff)] + newstr + ltlstr[j:]
    return ltlstr
  def ltl2sal( propstr ):
    ltlstr = remove_U(propstr, 'U')
    ltlstr = remove_U(ltlstr, 'W')
    #ltlstr = remove_F(ltlstr, '<>', 'X')
    ltlstr = ltlstr.replace( '[]', 'G' )
    ltlstr = ltlstr.replace( '<>', 'F' )
    ltlstr = ltlstr.replace( '&&', ' AND ' )
    ltlstr = ltlstr.replace( '||', ' OR ' )
    ltlstr = ltlstr.replace( '&', ' AND ' )
    ltlstr = ltlstr.replace( '|', ' OR ' )
    ltlstr = ltlstr.replace( '==', ' = ' )
    ltlstr = ltlstr.replace( '!=', ' /= ' )
    ltlstr = ltlstr.replace( '!', 'NOT ' )
    ltlstr = ltlstr.replace( '->', '=>' )
    return ltlstr
  def replace_and_if_needed( pstr ):
    '''replace & by &amp; if & is not followed by lt; or gt;'''
    a = pstr.split('&lt;')
    newa = []
    for i in a:
      ib = i.split('&gt;')
      newib = []
      for j in ib:
        jc = j.split('&amp;')
        jc = [ k.replace('&', '&amp;') for k in jc ]
        newib.append( '&amp;'.join(jc) )
      newa.append('&gt;'.join(newib) )
    return '&lt;'.join(newa)
  def re_escape_ops( pstr ):
    '''replace < by &lt; and > by &gt; in pstr's expr attribute'''
    i = pstr.find( 'expr' )
    assert i != -1, 'ERR: LTL property has no expr attribute?'
    while i != -1:
      i = pstr.find( '"', i)
      assert i != -1, 'ERR: LTL property has no expr attribute?'
      j = pstr.find( '"', i+1)
      assert j != -1, 'ERR: LTL property expr attribute is incomplete?'
      expr = pstr[i:j+1]
      # expr = expr.replace( '&', '&amp;' )
      expr = replace_and_if_needed( expr )
      expr = expr.replace( '<', '&lt;' )
      expr = expr.replace( '>', '&gt;' )
      ans = pstr[0:i] + expr + pstr[j+1:]
      pstr = ans
      i = pstr.find( 'expr', j )
    return pstr
  propStr = componentObj.prop
  if propStr == '':
    return propStr, []
  try:
    prop_dom = xml.dom.minidom.parseString(propStr)
  except Exception, e:
    propStr1 = propStr.replace("&quot;", '"')
    propStr1 = re_escape_ops( propStr1 )
    try:
      prop_dom = xml.dom.minidom.parseString(propStr1)
    except Exception, e:
      print 'property XML: unable to parse, invalid XML'
      print propStr1
      # prop_dom = xml.dom.minidom.parseString(testStr)
      # prop_dom = xml.dom.minidom.parseString(testStr2)
      # testStr33 = testStr3.replace("&quot;", '"')
      # prop_dom = xml.dom.minidom.parseString(testStr33)
      print 'Quitting', sys.exc_info()[0]
      sys.exit(-1)
  props = prop_dom.getElementsByTagName('ltlProperty')
  ans, propNameList = '', []
  for pnode in props:
    propName = pnode.getAttribute('name')
    propStr = pnode.getAttribute('expr')
    newPropStr = ltl2sal( propStr )
    ans += '\n{0}: THEOREM\n  '.format( propName )
    ans += '{1} |- {0}'.format( newPropStr, componentObj.get_name() )
    ans += ';\n'
    propNameList.append( propName )
  #print ans
  return (ans, propNameList)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------
def replace(node, newnode):
    parentnode = node.parentNode
    parentnode.replaceChild(newChild=newnode,oldChild=node)

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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# key=Var object; dict: (Var,Expr)->Expr; Is Var assigned ?
# Used for identifying which local variables are global parameters.
# -------------------------------------------------------------------
def is_key_in_dict(k, assgn):
  for lhs in assgn.keys():
    if lhs==k or (isinstance(lhs,(Expr,Var)) and lhs.contains_variable(k)):
      return True
    elif isinstance(lhs,(str,unicode)) and lhs==k.name:
      return True
  return False

def is_key_in_some_dict(k, dictL):
  for d in dictL:
    if is_key_in_dict(k, d):
      return True
  return False

def is_key_in_trans(i_var, trans):
  for (gg,actions) in trans:
    if is_key_in_dict(i_var, actions):
      return True
  return False
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# cybercomposition XML dom --> Internal Component-Object-List repr.
# -------------------------------------------------------------------
def ccdom2ComponentList(ccdom):
    "ccdom = cyber-composition dom; output HybridSal DOM..."
    components = ccdom.getElementsByTagName('Components')
    assert components != None and len(components) == 1, 'Error: Missing code 1'
    components = getArgs(components[0])
    top_systems = []
    for i in range(len(components)):
      top_system = subsystemXML2ComponentObj(components[i])
      top_system.xmlnode = components[i]  # SHOULD have been in constructor
      top_system.project()
      top_systems.append(top_system)
      # print 'top_system {1} = {0}'.format(top_system, i)
    return top_systems
# -------------------------------------------------------------------
 
# -------------------------------------------------------------------
# Class definitions for Internal representation
# -------------------------------------------------------------------
class Var:
  def __init__(self, name, xml = None):
    self.name = name
    self.xmlnode = xml
    self.usedby = []
  def add(self,e):
    if e not in self.usedby:
      self.usedby.append(e)
  def contains_variable(self, v):
    return (self is v) or (self.name == v.name)
  def substitute(self, sigma):
    if sigma.has_key(self):
      return sigma[self]
    return self
  def get_type(self):
    (name,typestr) = find_var_and_type(self.xmlnode)
    return typestr
  def set_type(self, typestr):
    self.xmlnode.setAttribute('type', typestr)
  def __str__(self):
    return self.name # +self.xmlnode.getAttribute('_id')
  def toStrPrime(self):
    return self.name + "'"  # +self.xmlnode.getAttribute('_id')
  def __deepcopy__(self, memo):
    return self

class Expr:
  def __init__(self):
    self.op, self.arity, self.args = None, None, None
  def __init__(self, op, arity, args):
    self.op, self.arity, self.args = op, arity, args
  # def __deepcopy__(self, memo):
    # return self
  def __hash__(self):    # some dicts hash on next(Var)
    if self.op == 'next':
      return hash(self.args[0])
    else:
      return hash(self.op)
  def __eq__(self, other):
    return isinstance(other,Expr) and self.op==other.op and self.args==other.args
  def contains_variable(self, v):
    for i in self.args:
      if isinstance(i, Var) and i.contains_variable( v ):
        return True
      elif isinstance(i, Expr) and i.contains_variable(v):
        return True
      elif isinstance(i, (str, unicode)) and v.name==i:
        return True
    return False
  def substitute(self, sigma):
    'NOTE: destructive operation'
    for i in range(self.arity):
      argi = self.args[i]
      if isinstance(argi, Var) and sigma.has_key(argi):
        # print 'debug: Some success here...'
        self.args[i] = sigma[argi]
      elif isinstance(argi, Expr):
        self.args[i] = argi.substitute(sigma)
    return self
  def divide2mult(self):
    '''replace e relop a/b by e*b relop a assuming b>0'''
    if self.op in ['<', '>', '<=', '>=', '=', '/=']:
      lhs = self.args[0]
      rhs = self.args[1]
      if isinstance(rhs,Expr) and rhs.op == '/':
        a,b = rhs.args[0], rhs.args[1]
        lhsb = Expr('*', 2, [lhs, b])
        lhsbopa = Expr(self.op, 2, [lhsb, a])
        bgt0 = Expr('>', 2, [b,0])
        case1 = Expr('AND', 2, [bgt0, lhsbopa])
        blt0 = Expr('<', 2, [b,0])
        lhsbnegopa = Expr(self.op, 2, [a, lhsb])
        case2 = Expr('AND', 2, [blt0, lhsbnegopa])
        return Expr('OR', 2, [case1, case2])
      elif isinstance(lhs,Expr) and lhs.op == '/':
        # a/b op rhs
        a,b = lhs.args[0], lhs.args[1]
        rhsb = Expr('*', 2, [rhs, b])
        rhsbopa = Expr(self.op, 2, [a, rhsb])
        bgt0 = Expr('>', 2, [b,0])
        case1 = Expr('AND', 2, [bgt0, rhsbopa])
        blt0 = Expr('<', 2, [b,0])
        rhsbnegopa = Expr(self.op, 2, [rhsb, a])
        case2 = Expr('AND', 2, [blt0, rhsbnegopa])
        return Expr('OR', 2, [case1, case2])
      else:
        return self
    else:
      return self
  def __str__(self):
    '''if next(x) -> x';; der(x) --> xdot';; else usual...??'''
    def brac_it(x):
      xstr = str(x)
      if xstr.find(' ') != -1:
        xstr = '({0})'.format(xstr)
      return xstr
    ans = ''
    if self.op == 'next':
      ans += str(self.args[0]) + "'"
    elif self.op in [ 'der', 'dot' ]:
      ans += str(self.args[0]) + "dot'"
    elif self.arity == 2:
      lhs = brac_it(self.args[0]) 
      rhs = brac_it(self.args[1])
      ans += lhs + ' ' + self.op + ' ' + rhs
    elif self.op in ['OR','AND','+']:
      for i in range(self.arity):
        argi = brac_it(self.args[i]) 
        ans += ' ' + self.op + ' ' if ans != '' else ''
        ans += argi
    else:
      ans = self.op + "("
      for i in range(self.arity):
        ans += ", " if i != 0 else ''
        ans += str(self.args[i])
      ans += ')'
    return ans
  def toStrPrime(self):
    '''if next(x) -> x';; der(x) --> xdot';; else usual...??'''
    def brac_it(x):
      xstr = x.toStrPrime()
      if xstr.find(' ') != -1:
        xstr = '({0})'.format(xstr)
      return xstr
    ans = ''
    if self.op == 'next':
      ans += str(self.args[0]) + "'"
    elif self.op in [ 'der', 'dot' ]:
      ans += str(self.args[0]) + "dot'"
    elif self.arity == 2:
      arg1,arg2 = self.args[0], self.args[1]
      if isinstance(arg1,Expr) or isinstance(arg1,Var):
        lhs = brac_it(self.args[0]) 
      else:
        lhs = str(arg1) 
      if isinstance(arg2,Expr) or isinstance(arg2,Var):
        rhs = brac_it(arg2)
      else:
        rhs = str(arg2)
      ans += lhs + ' ' + self.op + ' ' + rhs
    elif self.op in ['OR','AND','+','*']:
      for i in range(self.arity):
        argi = self.args[i]
        if isinstance(argi,Expr) or isinstance(argi,Var):
          argi = brac_it(argi) 
        else:
          argi = str(argi) 
        ans += ' ' + self.op + ' ' if ans != '' else ''
        ans += argi
    else:
      ans = self.op + "("
      for i in range(self.arity):
        argi = self.args[i]
        ans += ", " if i != 0 else ''
        if isinstance(argi,Expr) or isinstance(argi,Var):
          ans += argi.toStrPrime()
        else:
          ans += str(argi)
      ans += ')'
    return ans

class Eqn:
  def __init__(self):
    self.lhs, self.rhs = None, None
  def __init__(self, lhs, rhs):
    self.lhs, self.rhs = lhs, rhs
  def contains_variable(self, v):
    self.lhs.contains_variable(v) or self.rhs.contains_variable(v)
  def substitute(self, sigma):
    'NOTE: destructive operation'
    self.lhs = self.lhs.substitute(sigma)
    self.rhs = self.rhs.substitute(sigma)
    
class Component:
  def __init__(self, symtab, dynamics, mode_invs=[[]], init={}, tran = [], ins=[], outs=[], local=[], params=None, prop='', xmlnode=None):
    self.symtab = symtab
    assert type(dynamics)==list, 'ERR: dynamics not a list?'
    self.dynamics = dynamics
    self.mode_invs = mode_invs
    self.init = init
    self.trans = tran
    self.ins = ins
    self.outs = outs
    self.local = local
    self.xmlnode = xmlnode
    self.params = params
    self.prop = prop
  def divide2mult(self):
    for mode_eqns in self.dynamics:
      for k in mode_eqns.keys():
        mode_eqns[k] = divide2multRec(mode_eqns[k])
    for i in range(len(self.mode_invs)):
      for j in range(len(self.mode_invs[i])):
        self.mode_invs[i][j] = divide2multRec( self.mode_invs[i][j] )
    for (gg,acts) in self.trans:
      for i in range(len(gg)):
        gg[i] = divide2multRec( gg[i] )
  def get_name(self):
    if self.xmlnode != None:
      return self.xmlnode.getAttribute('name')
  def move_to_params(self, paramdict):
    '''just remove from init and local decl'''
    self.local = [i for i in self.local if not paramdict.has_key(i.getAttribute('name'))]
    for i in paramdict.keys():
      for j in self.init.keys():
        if j.name == i:
          del self.init[j]
    self.params.update( paramdict )
  def get_potential_params(self):
    '''Make local variable a global parameter so that nonlinearity becomes linearity in SAL '''
    param = {}
    for i in self.local:
      i_var = get_var(self.symtab, i)
      if is_key_in_some_dict(i_var, self.dynamics):
        continue
      if is_key_in_trans(i_var, self.trans):
        continue
      (varname, vartype) = find_var_and_type( i )
      if self.init.has_key(i_var):
        param[varname] = (vartype, self.init[i_var])
      else:
        param[varname] = (vartype, None)
      #print '{0}:{1} potential param'.format(varname, param[varname])
      print 'P{0}'.format(varname, param[varname]),
    return param
  def __str__(self):
    if self.xmlnode != None:
      print self.xmlnode.getAttribute('name')
    ans = 'Modes = {0}\n'.format(len(self.mode_invs))
    ans += 'Inputs = {0}, {1}\n'.format(len(self.ins), [i.getAttribute('name') for i in self.ins])
    ans += 'Output = {0}, {1}\n'.format(len(self.outs), [i.getAttribute('name') for i in self.outs])
    for i in range(len(self.mode_invs)):
      ans += 'Mode {0}:'.format(i)
      ans += '  Mode_Inv = \n'
      for j in self.mode_invs[i]:
        ans += '    ' + str(j) + '\n'
      ans += '  Mode_Eqn = \n'
      j = self.dynamics[i]
      for (k,v) in j.items():
        ans += '    ' + str(k) + ' = ' + str(v) + '\n'
    ans += '------------\n'
    return ans
  def project(self):
    ins, outs, eqns, invs, symtab = self.ins, self.outs, self.dynamics, self.mode_invs, self.symtab
    out_vars = []
    for i in outs:
      out_vars.append( get_var(symtab, i) )
    local_vars = [ get_var(symtab,i) for i in self.local ]
    # print 'Project out_vars: ', [str(i) for i in out_vars]
    for i in range(len(eqns)):
      modei_eqn, modei_inv = eqns[i], invs[i]
      for k in modei_eqn.keys():
        if isinstance(k, Var) and k not in out_vars:  
          # stateflow actions y' = 0; y' is not projected coz it is an Expr, not Var
          del modei_eqn[k]
          # check: intermediate state variables...
      # print 'Projected eqns {0}'.format([(str(k),str(v)) for k,v in modei_eqn.items()])
    #print 'Projected invs {0}'.format([str(i) for i in invlist])
    for (gg, action) in self.trans:
      for k in action.keys():
        if isinstance(k, Var) and k not in out_vars and k not in local_vars:  
          del action[k]
    for k in self.init.keys():
      if isinstance(k, Var) and k not in out_vars and k not in local_vars:
        # if isinstance(self.init[k], (Var,Expr)):
        del self.init[k]
  def addLocals(self, params):
    '''Add ParameterRef's as locals and add their initialization too'''
    for i in params:
      varname = i.getAttribute('name')
      varObj = parse_variable(varname, self.symtab)
      if varObj != None:    # ignore param already declared as local_var
        if self.init.has_key( varObj ): # ignore only if initialized
          continue
      else:
        varObj = get_var(self.symtab, i)
        self.local.append( i )
      type_str = i.getAttribute('Class')
      val = i.getAttribute('Value')
      if type_str == 'Real':
        type_str = 'REAL'
      elif type_str == 'Integer':
        type_str = 'INTEGER'
      else:
        assert False, 'ERR: Unknown type {0} for param {1}'.format(type_str,name)
      i.setAttribute('type', type_str)
      value = parse_number(val)
      assert value != None, 'ERR: Unable to parse value for param {0}'.format(name)
      if not self.init.has_key( varObj ):
        self.init[ varObj ] = value
      # ans[name] = (type_str, value)
  def toHSalTopDecls(self):
    '''return string -- top TYPE/Constant decls -- generated by this mod'''
    ans = ''
    if self.params != None:
      for (name,(type_str, value)) in self.params.items():
        if value != None:
          ans += '{0}: {1} = {2};\n'.format(name,type_str,value)
        else:
          ans += '{0}: {1};\n'.format(name,type_str)
    return ans
  def toHSalModDecl(self, params):
    '''return string -- MODULE decl'''
    name = self.xmlnode.getAttribute('name')
    assert name != '', 'ERROR: Subsystem has no NAME attribute \n{0}'.format(xmlnode.toxml())
    ans = '\n{0}: MODULE ='.format( name )
    ans += '\n BEGIN'
    for i in self.ins:
      (varname, vartype) = find_var_and_type( i )
      ans += '\n  INPUT {0}: {1}'.format(varname, vartype)
      assert vartype != '', 'ERR: Var {0} has no type'.format(varname)
    for i in self.outs:
      (varname, vartype) = find_var_and_type( i )
      ans += '\n  OUTPUT {0}: {1}'.format(varname, vartype)
      assert vartype != '', 'ERR: Var {0} has no type'.format(varname)
    for i in self.local:
      (varname, vartype) = find_var_and_type( i )
      if params.has_key(varname):
        # print 'Warning: Local variable {0} is a global parameter'.format(varname)
        print 'W5{0}'.format(varname),
      elif find_magic(self.outs, 'name', varname, 'name') != None:
        #print 'Warning: Local variable {0} is an output var'.format(varname)
        print 'W6{0}'.format(varname),
      else:
        ans += '\n  LOCAL {0}: {1}'.format(varname, vartype)
      assert vartype != '', 'ERR: Var {0} has no type'.format(varname)
    if len(self.init) > 0:
      ans += '\n  INITIALIZATION'
      init_var_done = []
      for (var,val) in self.init.items():
        if str(var) not in init_var_done:
          ans += '\n    {0} = {1};'.format(var, val)
          init_var_done.append( str(var))
      for k in self.dynamics[0].keys():  # defs has y' = offset; output_var = expr;
        if isinstance(k, Var):      # y' is an Expr, so y' = offset is NOT added
          if not self.init.has_key(k) and str(k) not in init_var_done:
            ans += '\n    {0} = {1};'.format(str(k), str(self.dynamics[0][k]))
            init_var_done.append( str(k))
    ans += '\n  TRANSITION'
    if len(self.dynamics) == 1:
      ans += mode_dynamics2str(self.dynamics[0], 3)
    else:
      ans += '\n  ['
      for i in range(len(self.dynamics)):
        if i > 0:
          ans += '\n  []'
        mode_dynamics = self.dynamics[i]
        mode_inv = self.mode_invs[i]
        ans += mode_inv2str(mode_inv, 3)
        ans += ' -->'
        ans += mode_dynamics2str(mode_dynamics, 4)
      for j in range(len(self.trans)):
        if len(self.dynamics) > 0 or j > 0:
          ans += '\n  []'
        (guard, action) = self.trans[j]
        # guard is a list of EXPRs, action = dict from varname to Expr
        guard_str = ''
        for gg in guard:
          guard_str += ' AND ' if guard_str != '' else ''
          guard_str += '(' + str(gg) + ')'
        action_str = mode_dynamics2str( action, 4 )
        '''
        action_str = ''
        for (k,v) in action.items():
          action_str += ';\n    ' if action_str != '' else ''
          action_str += str(k) + ' = ' + str(v)
        '''
        ans += guard_str + ' -->\n    ' + action_str
      ans += '\n  ]'
    ans += '\n END;'
    return ans
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Replace a/b by multiplication so that things become linear
# -------------------------------------------------------------------
def divide2multRec(expr):
  if not isinstance(expr, Expr):
    return expr
  newargs = [ divide2multRec(i) for i in expr.args ]
  if newargs == expr.args:
    newexpr = expr
  else:
    newexpr = Expr(expr.op, expr.arity, newargs)
  return newexpr.divide2mult()
# -------------------------------------------------------------------
      
# -------------------------------------------------------------------
# Pretty print string generator for transitions: actions  and guards
# -------------------------------------------------------------------
def mode_dynamics2str( mode_dynamics, offset ):
  '''print actions: print the dict mode_dynamics at offset; 
     if LHS is prime, print as is; else make LHS and RHS PRIMEd'''
  ans = ''
  tab = ' '*offset
  for (k,v) in mode_dynamics.items():
    if isinstance(k, (Var, str)):   # LHS is not primed
      v_str = v.toStrPrime() if isinstance(v, (Var, Expr)) else str(v)
      k_str = str(k) + "'"
    else:
      v_str, k_str = str(v), str(k)
    if k_str != v_str:    # avoid gear_selected' = gear_selected'
      ans += "\n{0}{1} = {2};".format(tab, k_str, v_str)
  return ans

def mode_inv2str( mode_inv, offset ):
  '''print guard: print the LIST mode_inv at offset'''
  ans = ''
  tab = ' '*offset
  for v in mode_inv:
    and_str = ' AND ' if ans != '' else ''
    ans += "\n{0}{1}{2}".format(tab, and_str, v)
  return ans
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Variable name and type string generator
# -------------------------------------------------------------------
def find_var_and_type( xmlnode ):
  ''' xmlnode = CyberController node '''
  varname = xmlnode.getAttribute('name')
  assert varname != '', 'ERROR: variable has no name {0}'.format(xmlnode.toxml())
  vartype = getArg(xmlnode,1)
  vartype_str = ''
  if vartype != None:
    vartype_str = vartype.getAttribute('name')
  if vartype_str == '':
    vartype_str = xmlnode.getAttribute('type')
  if vartype_str == '':
    vartype_str = ''
  if vartype_str in ['REAL','INTEGER','BOOLEAN']:
    pass
  elif vartype_str.endswith('Type'):
    pass
  elif vartype_str in ['double', 'float']:
    vartype_str = 'REAL'
  elif vartype_str.startswith('int'):
    vartype_str = 'INTEGER'
  elif vartype_str in ['boolean']:
    vartype_str = 'BOOLEAN'
  #else:
    #assert False, 'ERROR: {0} unknown type'.format(vartype_str)
  return (varname, vartype_str)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Helper for extracting info from CyberComposition XML
# -------------------------------------------------------------------
def find_node_attr_val( xmlnodes, attr, val):
  "find xmlnode whose attr=val, and return it"
  for p in xmlnodes:
    name = p.getAttribute(attr)
    if name == val or name.strip() == val.strip():
      return p
  return None

def find_magic( xmlnodes, attr, val, key, key2=None):
  "find xmlnode whose attr=val, and return its.key"
  for p in xmlnodes:
    name = p.getAttribute(attr)
    # print 'debug: Parameter name is {0} '.format(name)
    if name == val:
      retval = p.getAttribute(key)
      if retval == '' and key2 != None:
        retval = p.getAttribute(key2)
        assert retval != '','ERR: Attr {0} not found in {1}'.format(key,p.toxml())
      return retval
  return None

def find_param_value( params, key ):
  return find_magic( params, 'name', key, 'Value')
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Equality on lists of numbers..for translating transfer function blocks
# -------------------------------------------------------------------
def eq_num(a,b):
  return abs(a-b) < 1e-6

def eq(a, b):
  if type(a) == list and type(b) == list:
    if len(a) != len(b):
      return False
    return all([ eq_num(a[i],b[i]) for i in range(len(a)) ])
  elif type(a) == list and len(a) == 1:
    return eq_num(a[0],b)
  elif type(b) == list and len(b) == 1:
    return eq_num(b[0],a)
  else:
    return eq_num(b,a)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Parsing routines for Variable--map from name/id/etc to Var Object
# Symtab is a GLOBAL dict from node_id_str to Var-object.
# -------------------------------------------------------------------
def get_var(symtab, xmlnode):
  '''xmlnode -> Var-obj '''
  node_id = xmlnode.getAttribute('_id')
  if symtab.has_key(node_id):
    return symtab[node_id]
  name = xmlnode.getAttribute('Name')
  name = name if name != '' else xmlnode.getAttribute('name')
  assert name != '', 'ERR: xmlnode has no name {0}'.format(xmlnode.toxml())
  symtab[node_id] = Var(name, xml = xmlnode) 
  return symtab[node_id]

def parse_variable(vstr, symtab):
  '''v_name_str -> Var-obj; return None/object from symtab whose name = vstr'''
  return get_var_attr(symtab, 'Name', vstr)

def get_var_id(symtab, var_id):
  '''var_id_str --> Var-obj'''
  if not symtab.has_key(var_id): 
    #print 'Warning: variable _id={0} NOT found in {1}. id maybe part of demux/scope/terminator'.format(var_id, symtab.keys())
    return None
  return symtab[var_id]

def get_var_attr(symtab, attr, val, avoid=None):
  '''(var-attr,value) --> Var-obj'''
  for i in symtab.values():
    if i.xmlnode.getAttribute(attr) == val:
      if avoid != i:
        return i
  return None
  #assert False, 'Err: variable {0}={1} NOT found'.format(attr, val)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Parsing for discrete transfer functions
# -------------------------------------------------------------------
def parse_num_den_str(numStr):
  try:
    if numStr[0] == '[' and numStr[-1] == ']':
      return [ float(i) for i in numStr[1:-1].split() ]
    else: 
      return [ float(numStr) ]
  except Exception, e:
    print 'Error: Unexpected str {0} in transfer fcn'.format(numStr)
    sys.exit(-1)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Primitive SL/SF XML nodes --> Component Objects
# -------------------------------------------------------------------
def parse_sum(ins, outs, params):
  # check value of param name=='Inputs', its Value='|+++'
  inputs = find_param_value( params, 'Inputs')
  if inputs.endswith( '+'*len(ins) ):
    op = '+'
  elif inputs == '|+-':
    op = '-'
  else:
    assert False, 'ERROR: Missing code, sum.Inputs = {0}'.format(inputs)
  symtab, sigma = {}, {}
  args = [ get_var( symtab, i ) for i in ins ]
  args.sort( key=lambda x: x.xmlnode.getAttribute('Number') )
  assert len(outs) == 1, 'ERROR: Sum block has more than one OUTPUTs'
  out = get_var(symtab, outs[0])
  sigma[out] = Expr(op, len(ins), args)
  return Component(symtab, [sigma])

def parse_unitdelay(ins, outs, params):
  symtab = {}
  assert len(ins) == 1, 'ERROR: UnitDelay block has more than one INPUTS'
  assert len(outs) == 1, 'ERROR: UnitDelay block has more than one OUTPUTs'
  invar = get_var(symtab, ins[0])
  local_var = outs[0].cloneNode(True)
  old_id = local_var.getAttribute('_id')
  local_var.setAttribute('name', 'l'+old_id)
  local_var.setAttribute('_id',  'l'+old_id)
  outvar = get_var(symtab, outs[0])
  locvar = get_var(symtab, local_var)
  sigma = { Expr('next',1, [ locvar ]) : invar, outvar: locvar }
  init_val_str = find_param_value( params, 'InitialCondition')
  inits = {}
  add_initialization(inits, locvar, init_val_str)
  ans = Component(symtab, [sigma], init=inits, local=[local_var])
  #print ans
  return ans

def parse_relational_op(ins, outs, params):
  op_str = find_param_value( params, 'Operator')
  op_str = op_str.strip()
  assert op_str in ['>=', '<=', '>', '<'], 'ERR: Unknown op {0}'.format(op_str)
  symtab, sigma = {}, {}
  args = [ get_var( symtab, i ) for i in ins ]
  args.sort( key=lambda x: x.xmlnode.getAttribute('Number') )
  assert len(outs) == 1, 'ERROR: RelOp block has more than one OUTPUTs'
  out = get_var(symtab, outs[0])
  sigma[out] = Expr(op_str, len(ins), args)
  return Component(symtab, [sigma])

def parse_logic(ins, outs, params):
  op_str = find_param_value( params, 'Operator')
  op_str = op_str.strip()
  assert op_str in ['NOT', 'AND', 'OR'], 'ERR: Unknown logic operator {0}'.format(op_str)
  symtab, sigma = {}, {}
  args = [ get_var( symtab, i ) for i in ins ]
  args.sort( key=lambda x: x.xmlnode.getAttribute('Number') )
  assert len(outs) == 1, 'ERROR: Logic operator block has more than one OUTPUTs'
  out = get_var(symtab, outs[0])
  sigma[out] = Expr(op_str, len(ins), args)
  return Component(symtab, [sigma])

def parse_minmax(ins, outs, params):
  min_or_max = find_param_value( params, 'Function')
  arity_str = find_param_value( params, 'Inputs')
  arity = int(arity_str) if arity_str != '' else 2
  assert len(ins) == arity, 'Error: MinMax block - num of inputs does not match declared arity'
  assert len(outs) == 1, 'Error: MinMax block - how can it have more than one output??'
  symtab = {}
  invars = [ get_var( symtab, i ) for i in ins ]
  out = get_var(symtab, outs[0])
  sigmas, mode_invs = [], []
  assert arity == 2, 'Error: MinMax block has arity /= 2; can not handle currently'
  if min_or_max == 'max':
    mode_inv = Expr('>=', 2, [invars[0], invars[1]])
    mode_invs.append([mode_inv]),  sigmas.append({out: invars[0]})
    mode_inv = Expr('<=', 2, [invars[0], invars[1]])
    mode_invs.append([mode_inv]),  sigmas.append({out: invars[1]})
  else:
    mode_inv = Expr('>=', 2, [invars[0], invars[1]])
    mode_invs.append([mode_inv]),  sigmas.append({out: invars[1]})
    mode_inv = Expr('<=', 2, [invars[0], invars[1]])
    mode_invs.append([mode_inv]),  sigmas.append({out: invars[0]})
  return Component(symtab, sigmas, mode_invs=mode_invs)

def parse_saturate(ins, outs, params):
  upperLimStr = find_param_value( params, 'UpperLimit')
  lowerLimStr = find_param_value( params, 'LowerLimit')
  assert len(ins) == 1, 'Error: ??'
  assert len(outs) == 1, 'Error: ??'
  symtab = {}
  invar = get_var( symtab, ins[0] )
  out = get_var(symtab, outs[0])
  sigmas, mode_invs = [], []
  assert upperLimStr != '', 'Err: Expecting UpperLimit in Saturate'
  assert lowerLimStr != '', 'Err: Expecting LowerLimit in Saturate'
  upperLim = float(upperLimStr)
  lowerLim = float(lowerLimStr)
  mode_inv = Expr('>=', 2, [invar, upperLim])
  mode_invs.append([mode_inv]),  sigmas.append({out: upperLim})
  mode_inv = Expr('<=', 2, [invar, lowerLim])
  mode_invs.append([mode_inv]),  sigmas.append({out: lowerLim})
  mode_inv1 = Expr('>=', 2, [invar, lowerLim])
  mode_inv2 = Expr('<=', 2, [invar, upperLim])
  mode_invs.append([mode_inv1,mode_inv2]),  sigmas.append({out: invar})
  return Component(symtab, sigmas, mode_invs=mode_invs)

def parse_product(ins, outs, params):
  inputs = find_param_value( params, 'Multiplication')
  assert inputs.startswith('Element-wise'), 'ERROR: Missing code, Product.Multiplication != Element-wise'
  symtab = {}
  args = [ get_var( symtab, i ) for i in ins ]
  args.sort( key=lambda x: x.xmlnode.getAttribute('Number') )
  assert len(outs) == 1, 'ERROR: Product block has more than one OUTPUTs'
  out = get_var(symtab, outs[0])
  inputs = find_param_value( params, 'Inputs')
  if inputs.endswith( '*'*len(ins) ) or inputs == str(len(ins)):
    op = '*'
  elif inputs == '*/':
    op = '/'
  elif inputs == '/*':
    op = '/'
    args.reverse()
  else:
    assert False, 'ERROR: Missing code, product.Inputs = {0}'.format(inputs)
  return Component(symtab, [{out: Expr(op, len(ins), args)}])

def parse_discreteTransferFcn(ins, outs, params, sampleTimeStr):
  assert len(ins) == 1, 'Error: DTF??'
  assert len(outs) == 1, 'Error: DTF??'
  symtab = {}
  invar = get_var( symtab, ins[0] )
  out = get_var(symtab, outs[0])
  numStr = find_param_value( params, 'Numerator') # 0.01 or "[-1 1]"
  denStr = find_param_value( params, 'Denominator')  # "[1 -1]"
  initStr = find_param_value( params, 'InitialStates') # "0"
  init_value = parse_number(initStr)
  assert init_value != None, 'Param InitialStates is not a number!'
  # sampleTimeStr = find_param_value(params, 'SampleTime') # 0.01
  sampleTime = parse_num_den_str( sampleTimeStr)[0]
  num = parse_num_den_str( numStr )
  den = parse_num_den_str( denStr )
  assert type(num) == list and type(den) == list, 'ERROR: inv violated'
  if eq(num, [1,-1]) and len(den)==2 and eq(den[1],0): # derivative
    # y = du/dt * sampleTime/den[0]
    c = sampleTime/den[0]
    if eq(c,1):
      eqns = { Expr('der',1, [ invar ]) : out }
    else:
      eqns = { Expr('der',1, [ invar ]) : Expr('*',2,[1/c,out]) }
    inits = { invar: init_value}
    local = [ ins[0] ]
  elif eq(den,[1,-1]) and len(num)==1:
    # dy/dt*sampleTime = num[0]*u(t)
    c = sampleTime/num[0]
    if eq(c,1):
      eqns = { Expr('der',1, [ out ]) : invar }
    else:
      eqns = { Expr('der',1, [ out ]) : Expr('*',2,[1/c,invar]) }
    inits = { out: init_value }
    local = [ outs[0] ]
  else:
    print 'ERROR: Missing code. Cant handle generic transfer fcn'
    print 'num/den = {0}/{1}'.format(num,den)
    sys.exit(-1)
  return Component(symtab, [eqns], init=inits, local=local)

def parse_gain(ins, outs, params):
  gainStr = find_param_value( params, 'Gain')
  gain = float(gainStr)
  assert len(ins) == 1, 'ERROR: Gain block has > 1 inputs'
  symtab = {}
  args = [ get_var( symtab, i ) for i in ins ]
  assert len(outs) == 1, 'ERROR: Sum block has more than one OUTPUTs'
  out = get_var(symtab, outs[0])
  return Component(symtab, [ {out: Expr('*', 2, [gain, args[0]])}] )

def parse_SFunction(ins, outs, params, lines, subsystems, xmlnode):
  def parse_actions( action_str, symtab, flag=True ):
    # print 'parsing actions ', action_str
    actions = action_str.split(';')
    ans = {}
    for j in actions:
      if j.strip() == '':
        continue
      (lhs, rhs) = parse_eqn(j,symtab)
      lhs = Expr('next', 1, [lhs]) if flag else lhs # ASHISH: CHECK HERE
      ans[lhs] = rhs
    return ans
  def addNegatedGuard2State(src_state, guard, mode_type, modeinvs):
    '''update modeinvs[i] by appending NOT(guard),
       where mode_type[i] == src_state'''
    try:
      index = mode_type.index(src_state)
    except Exception, e:
      assert False, 'ERR: state {0} not found in {1}'.format(src_state, mode_type)
    modeinvs[index].append( Expr('NOT',1,[guard]) )
  # could be a wrapper for a state chart
  assert len(subsystems) == 1, 'Error: Expected one State in top-chart'
  state_xml = subsystems[0]
  symtab, states, modeinvs, trans, initialization = {}, [], [], [], {}
  # we should ignore ins, outs, because Joe Porter said we should ignore S-Function
  '''
  for i in ins:
    get_var(symtab, i)  # update symtab
  for i in outs:
    get_var(symtab, i)  # update symtab
  assert len(outs) > 0, 'Err: No output node in SFunction'
  '''
  chart_type = state_xml.getAttribute('Decomposition')
  assert chart_type == 'OR_STATE', 'Error: Cannot handle AND-node at root'
  # find the ins and outs from the stateflow
  outs, ins, local = [], [], []
  for i in getArgs(state_xml):    # state_xml == top_OR_state
    if i.tagName == 'Simulink:Data':
      ivar = get_var( symtab, i)    # put variable in the symtab
      scope = i.getAttribute('Scope')
      if scope == 'OUTPUT_DATA':
        outs.append(i)
        local.append(i)
        ivalstr = i.getAttribute('InitialValue')
        add_initialization(initialization, ivar, ivalstr)
      elif scope == 'INPUT_DATA':
        ins.append(i)
      elif scope == 'LOCAL_DATA':
        local.append(i)
        ivalstr = i.getAttribute('InitialValue')
        add_initialization(initialization, ivar, ivalstr)
        ## in_xmlnode = find_node_attr_val( ins, 'Number', port)
        ## assert in_xmlnode != None, 'ERROR: In statechart, IN port {0} not found'.format(port)
        ## in_var = get_var(symtab, in_xmlnode)
        ## sigma_base[data_var] = in_var
  # now we have the ins, outs for this CHART
  ccdom = xmlnode.ownerDocument
  mode_varname = state_xml.getAttribute('name') + 'Mode'
  mode_xmlnode = ccdom.createElement('Simulink:OutputPort')
  mode_xmlnode.setAttribute('name', mode_varname)
  mode_xmlnode.setAttribute('Name', mode_varname)
  mode_xmlnode.setAttribute('_id', 'myid0')
  local.append( mode_xmlnode )
  mode_type = []    # values that the mode_var can take...
  mode_var = get_var(symtab, mode_xmlnode)

  states_xmlnodes = []
  sigma_enter = {}
  for i in getArgs(state_xml):    # state_xml == top_OR_state
    if i.tagName == 'Simulink:Data':
      pass    # handled above
    elif i.tagName == 'Simulink:State':
      chart_type = i.getAttribute('Decomposition')
      assert chart_type == 'OR_STATE', 'Error: Missing code for AND states'
      name = i.getAttribute('Name')
      my_id = i.getAttribute('_id')
      mode_type.append(name)
      # state_name2xml_map[name] = i
      #enter_action = i.getAttribute('EnterAction')
      # now process enter_action -- store in sigma_enter -- use in trans
      mode_inv = Expr('=', 2, [ mode_var, name ] )  # changed from Eqn
      modeinvs.append( [ mode_inv ] )
      sigma_enter[my_id] = { Expr('next',1,[mode_var]): name}
      sigma = {}    # during_action + enter_action too
      # enter_action can be updated by the during action; hence do first
      enter_action = i.getAttribute('EnterAction')
      enters = parse_actions( enter_action, symtab, flag=True )
      sigma_enter[my_id].update( enters )
      sigma.update( enters )
      during_action = i.getAttribute('DuringAction')
      durings = parse_actions( during_action, symtab, flag=True)
      sigma.update( durings )
      states.append( sigma )
      states_xmlnodes.append( i )
    elif i.tagName == 'Simulink:Transition':
      pass # trans.append(i)
    elif i.tagName == 'Simulink:TransStart':
      dst_trans_id = i.getAttribute('dstTransition')
      xmlnodes = getArgs(state_xml)
      transNode = find_node_attr_val(xmlnodes, '_id', dst_trans_id)
      init_state_id = transNode.getAttribute('dstTransition_end_')
      init_state_xmlnode = find_node_attr_val(xmlnodes, '_id', init_state_id)
      # init_state_xmlnode = find_magic(xmlnodes, '_id', init_state_id, 'name')
      init_state = init_state_xmlnode.getAttribute( 'name')
      assert init_state != None, 'ERR: Dst of init transition not found'
      initialization[mode_var] = init_state
      actionStr = transNode.getAttribute('Action')
      if actionStr != '':
        actionStr += ';'
      cond_action_str = transNode.getAttribute('ConditionAction')
      actionStr += cond_action_str
      if not actionStr.endswith(';'):
        actionStr += ';'
      actionStr += init_state_xmlnode.getAttribute('EnterAction')
      init_actions = parse_actions(actionStr, symtab, flag=False)
      initialization.update( init_actions )
      #print 'Stateflow init: {0} = {1}'.format(mode_var.name,init_state)
      cond_action = transNode.getAttribute('Guard')
      assert cond_action=='', 'ERR: Cant handle guard in init transition'
    else:
      print 'ERR: Unexpected tag {0}'.format(i.tagName)
  assert dst_trans_id != None, 'ERR: Chart: No initial state found'
  # Now handle Simulink:Transition 
  for i in getArgs(state_xml):    # state_xml == top_OR_state
    if i.tagName == 'Simulink:Transition':
      trans_id = i.getAttribute('_id')
      if trans_id == dst_trans_id:
        continue
      src_id = i.getAttribute('srcTransition_end_')
      dst_id = i.getAttribute('dstTransition_end_')
      src_state = find_magic( states_xmlnodes, '_id', src_id, 'name' )
      dst_state = find_magic( states_xmlnodes, '_id', dst_id, 'name' )
      assert src_state != None, 'ERROR: tran_err {0}'.format(src_id)
      assert dst_state != None, 'ERROR: tran_err {0}'.format(dst_id)
      # guard = '{1} = {0}'.format(src_state, mode_varname)
      guard = [ Expr('=', 2, [ mode_var, src_state ]) ]
      # action = "{1}' = {0}".format(dst_state, mode_varname)
      # action = { mode_var: dst_state }
      action = sigma_enter[ dst_id ]
      guard2 = i.getAttribute('Guard')
      # print 'GUARD = {0}'.format(guard2)
      # guard += ' AND ' + guard2
      guard2_expr = parse_fmla(guard2, symtab)
      guard.append( guard2_expr )
      addNegatedGuard2State(src_state, guard2_expr, mode_type, modeinvs)
      action2 = i.getAttribute('Action')
      action2 += ';' if action2 != '' else ''
      action3 = i.getAttribute('ConditionAction')
      allactionsStr = action2 + action3
      allactionsDict = parse_actions(allactionsStr, symtab, flag=True)
      newaction = action.copy()
      newaction.update(allactionsDict)
      trans.append( (guard, newaction) )
  # ASHISH: add enum variable mode: { names } to variables...
  type_str = '{'
  for i in mode_type:
    if len(type_str) > 1:
      type_str += ','
    type_str += i
  type_str += '}'
  # mode_xmlnode.setAttribute('type', type_str)
  mode_vartype = mode_varname + 'Type'
  params = { mode_vartype: ('TYPE', type_str) }
  mode_xmlnode.setAttribute('type', mode_vartype)
  propStr = getPropStr(xmlnode)
  return Component(symtab,states,init=initialization,tran=trans,mode_invs=modeinvs, ins=ins, outs=outs, local=local, params=params, prop=propStr)

def parse_constant(ins, outs, params):
  '''ins = list of input XML nodes, outs = list of outputs,
     params = list of SF_Parameter nodes; Return COMPONENT'''
  def param(out, param_name = '', number = None):
    name = out.getAttribute('_id')
    var = Var(name, xml = out)
    symtab = { name: var }
    params = None
    if param_name != '':
      out.setAttribute('name', param_name)
    if number != None:
      sigma = { var: number }
    elif param_name != '':
      sigma = { var: param_name }
      params = {param_name: ('REAL', 1)}  # ASHISH: REAL default used
    else:
      assert False, 'Error: Constant {0} has no value'.format(name)
    return Component(symtab, [sigma], outs = [out], params=params )
  assert len(ins) == 0, 'Error: Constant block has inputs??'
  assert len(outs) == 1, 'Error: Constant block has /= 1 outputs??'
  for i in params:
    name = i.getAttribute('name')
    if name in ['Value', 'value']:
      value = i.getAttribute('Value')
      num_val = parse_number(value)
      if num_val != None:
        return param(outs[0], number = num_val)
      return param(outs[0], param_name = value)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Helper parsing functions -- for expressions
# -------------------------------------------------------------------
def parse_number(nstr):
  try:
    ans = float(nstr)
    return ans
  except ValueError:
    return None

def parse_term(estr, symtab):
  '''expr_string --> Expr Object; return float, or Var obj, or Expr obj'''
  estr = estr.strip()
  ans = parse_number(estr)
  if ans != None:
    return ans
  ans = parse_variable(estr,symtab)
  if ans != None:
    return ans
  if estr.find('+') != -1:
    pieces = estr.split('+')
    ans = [ parse_term(i, symtab) for i in pieces ]
    return Expr('+', len(ans), ans)
  if estr.find('-') != -1:
    pieces = estr.split('-')
    ans = [ parse_term(i, symtab) for i in pieces ]
    if len(ans) == 1:
      return Expr('-', 2, [0, ans[0]])
    assert len(ans) == 2, 'ERR: a-b expected'
    return Expr('-', len(ans), ans)
  return estr

def parse_fmla(estr, symtab):
  '''heuristic parser -- does not always work'''
  def chk_brac(estr):
    if estr.startswith('(') and estr.endswith(')'):
      count = 0
      for i in range(len(estr)):
        if estr[i] == '(':
          count += 1
        elif estr[i] == ')':
          count -= 1
        if count == 0 and i != len(estr) - 1:
          return False
      return True
    return False
  def merge_splits(estrs, op):
    ''' (a && b) && c --> splits into '(a', 'b)', 'c' --> '(a&&b)', 'c' '''
    def chk_brac2(e):
      return e.count('(') == e.count(')')
    if all( [ chk_brac2(i) for i in estrs ] ):
      return estrs
    if chk_brac2(estrs[0]):
      ans = [ estrs[0] ]
      ans.extend( merge_splits(estrs[1:], op) )
      return ans
    estr = estrs[0] + ' ' + op + ' ' + estrs[1]
    new_estrs = [ estr ]
    new_estrs.extend( estrs[2:] )
    return merge_splits( new_estrs, op)
  #print 'Parsing formula {0}'.format(estr)
  ops = ['>=', '<=', '==', '<', '>', '!=', '=']
  estr = estr.strip()
  if chk_brac(estr):
    return parse_fmla(estr[1:-1], symtab)
  if estr.find('||') != -1:
    pieces = estr.split('||')
    pieces = merge_splits( pieces, '||' )
    if len(pieces) > 1:
      ans = [ parse_fmla(i, symtab) for i in pieces ]
      return Expr('OR', len(ans), ans)
  if estr.find('&&') != -1:
    pieces = estr.split('&&')
    pieces = merge_splits( pieces, '&&' )
    if len(pieces) > 1:
      ans = [ parse_fmla(i, symtab) for i in pieces ]
      return Expr('AND', len(ans), ans)
  # if estr.find('=') != -1:
    # (lhs,rhs) = parse_eqn(estr, symtab)
    # return Expr('=', 2, [lhs, rhs])
  for op in ops:
    if estr.find(op) != -1:
      estr2 = estr.replace(op, '=')
      (lhs,rhs) = parse_eqn(estr2, symtab)
      op = op if op != '==' else '='
      op = op if op != '!=' else '/='
      return Expr(op, 2, [lhs, rhs])
  assert False, 'ERROR: Unable to parse fmla {0}'.format(estr)

def parse_eqn(estr,symtab):
  "parse gain = 0 into an equation"
  ops = ['+=', '=']
  for op in ops:
    if estr.find(op) == -1:
      continue
    sides = estr.split(op)
    sides[:] = [i for i in sides if i != '']
    assert len(sides) == 2, 'Error: {0} should have ONE ='.format(estr)
    lhs, rhs = sides[0].strip(), sides[1].strip()
    lhs_var = parse_term(lhs, symtab)
    rhs_var = parse_term(rhs, symtab)
    if op == '=':
      return (lhs_var, rhs_var)
    elif op == '+=':
      return (lhs_var, Expr('+', 2, [lhs_var, rhs_var]))
  assert False, 'ERR: Unparsed string {0}'.format(estr)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# update initialization dict from given Var-obj and its init-value-str
# -------------------------------------------------------------------
def add_initialization(initialization, varobj, ivalstr):
  ltype = varobj.get_type()
  if ivalstr == '':
    return
  if ltype == 'BOOLEAN':
    ival = 'FALSE' if ivalstr.strip()=='0' else 'TRUE'
  else:
    try:
      ival = float(ivalstr)
    except Exception, e:
      print 'Unable to convert to float', ivalstr
      assert False, 'ERR'
  initialization[ varobj ] = ival
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Get property string from the xmlnode
# -------------------------------------------------------------------
def getPropStr(xmlnode):
  '''from this node, or any of its subsystems, get property string'''
  propStr = xmlnode.getAttribute('Description')
  if propStr != '':
    return propStr
  childs = getArgs(xmlnode)
  for i in childs:
    propStr = i.getAttribute('Description')
    if propStr != '':
      return propStr
  return propStr

# -------------------------------------------------------------------
# One main function: subsystem CC XML --> Component Object
# -------------------------------------------------------------------
def subsystemXML2ComponentObj(xmlnode):
  '''xmlnode = CyberComposition node with tagName = Components; 
     presently, just create INTERNAL representation and return;'''
  (ins, outs, params, lines, subsystems) = component_partition(xmlnode)
  if xmlnode.tagName == 'SimulinkWrapper':
    assert len(subsystems) == 1, 'ERROR: Simulink wrapper has > 1 subsys'
    sub = subsystemXML2ComponentObj(subsystems[0])
    composed_system = compose( [sub], ins, outs, params, lines, xmlnode )
    composed_system.addLocals( params )
    return composed_system
  elif xmlnode.tagName == 'Simulink:Primitive':
    # base case
    blocktype = xmlnode.getAttribute('BlockType') 
    print 'b',    # base case
    if blocktype == 'Sum':
      return parse_sum(ins, outs, params)
    elif blocktype == 'Saturate':
      return parse_saturate(ins, outs, params)
    elif blocktype == 'Product':
      return parse_product(ins, outs, params)
    elif blocktype == 'DiscreteTransferFcn':
      sample_time = xmlnode.getAttribute('SampleTime')
      return parse_discreteTransferFcn(ins, outs, params, sample_time)
    elif blocktype == 'Gain':
      return parse_gain(ins, outs, params)
    elif blocktype == 'Terminator':
      return None
    elif blocktype == 'S-Function':
      return parse_SFunction(ins, outs, params, lines, subsystems, xmlnode)
    elif blocktype == 'Demux':
      return None
    elif blocktype == 'Scope':
      return None
    elif blocktype == 'Constant':
      return parse_constant(ins, outs, params)
    elif blocktype == 'RelationalOperator':
      return parse_relational_op(ins, outs, params)
    elif blocktype == 'MinMax':
      return parse_minmax(ins, outs, params)
    elif blocktype == 'Logic':
      return parse_logic(ins, outs, params)
    elif blocktype == 'UnitDelay':
      return parse_unitdelay(ins, outs, params)
    else:
      print 'ERROR: Missing code. Blocktype {0} not handled yet.'.format(blocktype)
  else:
    # recurse
    print 'r',
    subs = []
    for i in subsystems:
      my_subsystem = subsystemXML2ComponentObj(i)
      if my_subsystem == None:
        print 'c',   # 'component ignored'
      else:
        my_subsystem.xmlnode = i
        subs.append( my_subsystem )
    composed_system = compose( subs, ins, outs, params, lines, xmlnode )
    return composed_system
# -------------------------------------------------------------------
  
# -------------------------------------------------------------------
# Helper functions for extracting info from CC XML
# -------------------------------------------------------------------
def get_src_node_id( xmlnode ):
  i = xmlnode
  if xmlnode.tagName == 'Simulink:OutputPort':
    return i.getAttribute('srcLine')
  elif xmlnode.tagName == 'OutputSignalInterface':
    return i.getAttribute('srcOutputSignalInterfaceConnection')
  elif xmlnode.tagName == 'Simulink:Line':
    return i.getAttribute('srcLine_end_')
  elif xmlnode.tagName == 'OutputSignalInterfaceConnection':
    return i.getAttribute('srcOutputSignalInterfaceConnection_end_')
  assert False, 'ERR: Unknown xmlnode to go back upon'

def get_src_port_id( line ):
  srcPort_id = line.getAttribute('srcLine_end_')
  if srcPort_id == '':
    srcPort_id = line.getAttribute('srcOutputSignalInterfaceConnection_end_')
  if srcPort_id == '':
    srcPort_id = line.getAttribute('srcInputSignalInterfaceConnection_end_')
  assert srcPort_id != '', 'Err: Line {0} has NO SOURCE'.format(line.toxml())
  return srcPort_id

def get_dst_port_id( line ):
  srcPort_id = line.getAttribute('dstLine_end_')
  if srcPort_id == '':
    srcPort_id = line.getAttribute('dstOutputSignalInterfaceConnection_end_')
  if srcPort_id == '':
    srcPort_id = line.getAttribute('dstInputSignalInterfaceConnection_end_')
  assert srcPort_id != '', 'Err: Line {0} has NO DST'.format(line.toxml())
  return srcPort_id

def type_infer(var1, var2):
  type1 = var1.get_type()
  type2 = var2.get_type()
  if type1 == '':
    var1.set_type(type2)
  if type2 == '':
    var2.set_type(type1)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Second MAIN procedure: Compose subsystems to one Component Object
# algorithm:
# start with out = out equation for each out variable in supercomponent
# while RHS has a variable that has a definition in one of the components:
# replace var by val in RHS
# -------------------------------------------------------------------
def compose(subs, ins, outs, params, lines, rootnode):
  '''given list of Component-objs, as subs, compose them into ONE Component'''

  # first create the answer symtab, modes and equations
  symtab, ans_modes, eqns = {}, [[]], [{}]

  # remove IGNORED components
  subs = [i for i in subs if i != None]
  # print 'Number of subcomponents to compose = {0}'.format(len(subs))
  print 'c{0}('.format(len(subs)),
  # while there is a var on RHS of Eqns that has a definition in subs
  # multiply component into answer

  # print 'COMPOSING:'
  for component in subs:
    symtab.update(component.symtab)   # update answer symbol table
  for i in ins:                       # insert input vars in symtab
    get_var(symtab, i)
  # for i in outs:                      # insert output vars in symtab
    # ivar = get_var(symtab, i)
  outs_var = [ get_var(symtab, i) for i in outs ]
  '''
    src_port_id = get_src_of_outport(lines, i)
    var2 = get_var_id(symtab, src_port_id)
    eqns[0][ivar] = var2
  '''
  # print 'composed symtab: {0}'.format(symtab.keys())
  sys.stdout.flush()

  # base composed component has one mode and is defined by 
  # mapping of external interface vars to internal ones
  # eqns[0], currently {}, will hold these equations; 
  # see initialization above; we have 1 mode {}; mode_inv = []
  for i in lines:
    src_id = get_src_port_id(i)
    dst_id = get_dst_port_id(i)
    var1 = get_var_id(symtab, src_id)
    var2 = get_var_id(symtab, dst_id)
    if var1 != None and var2 != None:
      # print '{0} -> {1}'.format(var2, var1)
      eqns[0][var2] = var1
    elif var1 != None and var2 == None:
      var2 = get_var_attr(symtab, 'name', var1.name, avoid=var1)
      if var2 != None:
        # print '{0} -> {1}'.format(var2, var1)
        eqns[0][var2] = var1
      else:
        # print 'WARNING: Missing destination for input? signal {0}'.format(var1.name)
        print 'W1'.format(var1.name),
    elif var1 == None and var2 != None:
      var1 = get_var_attr(symtab, 'name', var2.name, avoid=var2)
      if var1 != None:
        # print '{0} -> {1}'.format(var2, var1)
        eqns[0][var2] = var1
      else:
        # print 'WARNING: Missing source for output? signal {0}'.format(var2.name)
        print 'W2'.format(var2.name),
    else:
        #print 'WARNING: Both source {0} and sink {1} of a line are missing'.format(src_id, dst_id)
        print 'W3'.format(src_id, dst_id),
  # now we have eqns[0] all set up correctly....

  # eqns[0] needs to be used to update initializations and transitions too; so make pointer to it for later.
  definitions = eqns[0]

  # make type(var1) == type(var2)
  for (var1,var2) in eqns[0].items():
    type_infer(var1, var2)

  # multiply the number of modes of all the subcomponents....
  # len(eqns) is the product... it is 1 initially...
  initialization = {}
  for component in subs:
    new_ans_modes, new_ans_eqns = [], []
    initialization.update( component.init )

    # new_ans_modes and new_ans_eqns = product of first i components
    for i in range(len(component.dynamics)):
      # for each mode of the new sub-component...
      assert len(component.dynamics)==len(component.mode_invs), 'ERR: modes = {0}; dynamics = {1}'.format(len(component.mode_invs), component.dynamics)
      mode_i, inv_i = component.dynamics[i], component.mode_invs[i]
      '''
      print 'Inv {0} of subcomponent: {1}'.format(i, [str(e) for e in inv_i])
      print 'Eqn {0} of subcomponent: {1}'.format(i, [(str(k),v) for (k,v) in mode_i.items() if isinstance(v,(float,int))])
      print 'Eqn {0} of subcomponent: {1}'.format(i, [(str(k),str(v)) for (k,v) in mode_i.items() if not isinstance(v,(float,int))])
      '''
      for j in range(len(eqns)):
        # for each existing mode of the partial product
        mode_j, inv_j = eqns[j], ans_modes[j]
        new_mode_inv = copy.deepcopy(inv_i)  # mode inv is union
        new_mode_inv.extend( copy.deepcopy(inv_j) )
        new_ans_modes.append( new_mode_inv )
        mode_ij = copy.deepcopy( mode_j )
        mode_ij.update( copy.deepcopy( mode_i ) )
        new_ans_eqns.append( mode_ij )
    eqns = new_ans_eqns
    ans_modes = new_ans_modes
    '''
    for i in range(len(eqns)):
      print 'Mode {0} Eqn: {1}'.format(i, [(str(k),v) for (k,v) in eqns[i].items() if isinstance(v,(float,int))])
      print 'Mode {0} Eqn: {1}'.format(i, [(str(k),str(v)) for (k,v) in eqns[i].items() if not isinstance(v,(float,int))])
      print 'Mode {0} Inv: {1}'.format(i, [str(e) for e in ans_modes[i]])
    '''
  # done: eqns, ans_modes contains the composition, but need to simplify
  # ASHISH: Need to multiply the trans too!!!!
  local, trans, params = [], [], {}
  for i in subs:
    local.extend( i.local )
    trans.extend( i.trans )
    if i.params != None:
      params.update( i.params )
  normalize( eqns, ans_modes, trans, symtab ) 
  normalize_trans( trans, definitions, eqns[0] )
  normalize_init( initialization, definitions, outs_var)

  # Now project onto ins, outs + extras...
  # project(ins, outs, eqns, ans_modes, symtab)
  # missing: info about initialization and transitions
  # print 'composition complete'
  print ')',
  # if len(subs) == 1:
    # ins, outs = subs[0].ins, subs[0].outs
  propStr = rootnode.getAttribute('Description')
  if propStr == '':
    for i in subs:
      propStr = i.prop
      propStr = compose_property( propStr, definitions )
      if propStr != '':
        break
  ans =  Component(symtab, eqns, ans_modes, ins=ins, outs=outs, tran=trans, init = initialization, local=local, params=params, xmlnode=rootnode, prop=propStr)
  ans.project()
  # print '------------------------------------'
  # print ans
  # print '------------------------------------'
  return ans

def compose_property( propStr, definitions ):
  '''definitions = Eqns[0] obtained form lines; apply it to propStr'''
  def compose_property_one( propStr, v_str1, v_str2, white_space):
    index = propStr.find(v_str1)
    ans = ''
    while index != -1:
      ans += propStr[0:index]
      if index+1 < len(propStr) and propStr[index+1] in white_space:
        ans += v_str2
      elif index-1 >= 0 and propStr[index-1] in white_space:
        ans += v_str2
      else:
        ans += v_str1
      propStr = propStr[index+len(v_str1):]
      index = propStr.find(v_str1)
    ans += propStr
    return ans
  white_space = ' ()+-*/=<>'
  for (k,v) in definitions.items():
    propStr = compose_property_one(propStr, k.name, v.name, white_space)
  return propStr

def normalize( eqns, invs, trans, symtab ):
  "just apply substitutions exhaustively"
  for i in range(len(eqns)):
    modei_eqn, modei_inv = eqns[i], invs[i]
    normalize_eqn_list( modei_eqn, modei_inv, trans )
  assert len(eqns) > 0, 'Err: Zero modes in system?'
  # we use just equations from ONE mode to normalize transitions
  # normalize_trans(trans, eqns[0])

def normalize_a_substitution( eqnlist ):
  '''Apply sigma to itself so that sigma(x) = sigma(sigma(x))'''
  for var in eqnlist.keys():
    sub = {var: eqnlist[var]}
    # print 'debug: var {0} -> val {1}'.format(var,val)
    if not isinstance(var, Var):
      continue
    for (k,v) in eqnlist.items():
      if isinstance(v, (Expr, Var)):
        # print 'debug: subbing var {0} -> val {1} in {2}'.format(var,val,v)
        eqnlist[k] = v.substitute( sub ) 
        # print 'debug: result = {2}'.format(var,val,eqnlist[k])
  return eqnlist

def normalize_eqn_list( eqnlist, invlist, trans ):
  # print 'Normalizing eqns {0}'.format([(str(k),str(v)) for k,v in eqnlist.items()])
  # print 'Normalizing invs {0}'.format([str(i) for i in invlist])
  # first normalize the substitution eqnlist
  eqnlist = normalize_a_substitution( eqnlist )
  # now apply substitution eqnlist to invlist
  for e1 in invlist:
    assert not isinstance(e1, Var), 'ERR: mode-inv shd not be a var {0}'.format(e1)
    e1.substitute( eqnlist )
  ''' # old code -- was using all mode equations to normalize transitions
  for (guard,action) in trans:
    for gg in guard:
      gg.substitute( eqnlist )
    for (k,v) in action.items():  # ASHISH: changed trans -> action.items() here
      if isinstance(v, Expr):
        v.substitute( eqnlist )
  '''
  # print 'Normalized eqns {0}'.format([(str(k),str(v)) for k,v in eqnlist.items()])
  # print 'Normalized invs {0}'.format([str(i) for i in invlist])

def normalize_trans( trans, definitions, mode0_equations ):
  '''apply definitions = sub to guard of each transition, and 
     add to the action and normalize action'''
  for (guard,action) in trans:
    for gg in guard:
      gg.substitute( mode0_equations )    # THIS IS A HACK...we need to properly COMPOSE
    action.update( definitions )
    action = normalize_a_substitution(action)
    '''for (k,v) in action.items():  # ASHISH: changed trans -> action.items() here
      if isinstance(v, Expr):
        v.substitute( definitions )
    # Mode changes are not assumed to influence 'output' variables
    for k in definitions.keys():  # defs has y' = offset; output_var = expr;
      if isinstance(k, Var):      # y' is an Expr, so y' = offset is NOT added
        if k in outs_var and not action.has_key(k):
          action[k] = definitions[k]
    '''

def normalize_init( initialization, definitions, outs_var ):
  initialization.update(definitions)
  normalize_a_substitution(initialization)
  # initialization: add output_var definition...done also for trans inside normalize
  '''
  for k in definition.keys():  # defs has y' = offset; output_var = expr;
    if isinstance(k, Var):      # y' is an Expr, so y' = offset is NOT added
      if k in outs_var and not initialization.has_key(k):
        initialization[k] = eqns[0][k]
  '''

# -------------------------------------------------------------------

# -------------------------------------------------------------------
# ASHISH: line to EQUATIONS
# get the value of ivar from the subs...
def get_src_of_outport(lines, i):
  srcLineStr = get_src_node_id( i )
  assert srcLineStr!='','ERR: attr srcLine not found in {0}'.format(i.toxml())
  srcPort_id = find_magic(lines, '_id', srcLineStr, 'srcLine_end_', key2='srcOutputSignalInterfaceConnection_end_')
  assert srcPort_id != None, 'ERR: backtracing Port {0} <- Line {1} <- ? failed'.format(ivar.name, srcLineStr)
  return srcPort_id
# -------------------------------------------------------------------

    # now find which subsystem has output port with _id = srcPort...
    # for j in subs:
      # if j.hasOutputPort(srcPort):
        # j

# -------------------------------------------------------------------
def component_partition(xmlnode):
  "partition xmlnode.children into inputs, outputs, etc."
  children = getArgs(xmlnode)
  ins, outs, params, lines, subsystems = [], [], [], [], []
  for i in children:
    if i.tagName in ['InputSignalInterface','Simulink:InputPort']:
      ins.append(i)
    elif i.tagName in ['OutputSignalInterface','Simulink:OutputPort']:
      outs.append(i)
    elif i.tagName in ['InputSignalInterfaceConnection','OutputSignalInterfaceConnection','Simulink:Line']:
      lines.append(i)
    elif i.tagName in ['ParameterRef','Simulink:SF_Parameter']:
      params.append(i)
    elif i.tagName in ['Simulink:Primitive','Simulink:Subsystem','Simulink:State']:
      subsystems.append(i)
    elif i.tagName in ['BusInterface']:
      inputs = i.getElementsByTagName('InputSignalInterface')
      ins.extend(inputs)
      outputs = i.getElementsByTagName('OutputSignalInterface')
      outs.extend(outputs)
    else:
      #print 'WARNING: Unrecognized tag {0}. Ignoring.'.format(i.tagName)
      print 'W4{0}'.format(i.tagName),
  return (ins,outs,params,lines,subsystems)
# -------------------------------------------------------------------


# -------------------------------------------------------------------
# INTERFACE function
# -------------------------------------------------------------------
def cybercomposition2hsal(filename, options = []):
    '''given filename = CC XML, generate HSAL, return HSALfilename, propNameList'''
    def existsAndNew(filename1, filename2):
        if os.path.isfile(filename1) and os.path.getmtime(filename1) >= os.path.getmtime(filename2):
            print "File {0} exists and is new".format(filename1)
            return True
        return False
    basename,ext = os.path.splitext(filename)
    try:
        ccdom = xml.dom.minidom.parse(filename)
    except xml.parsers.expat.ExpatError, e:
        print 'Syntax Error: Input XML ', e 
        print 'Error: Input XML file is not well-formed...Quitting.'
        sys.exit(-1)
    except:
        print 'Error: Input XML file is not well-formed'
        print 'Quitting', sys.exc_info()[0]
        sys.exit(-1)
    print >> sys.stderr, 'Creating .hsal file......'
    # now parse the dae into daexml
    hsalfilename = basename + '.hsal'
    if not existsAndNew(hsalfilename, filename):
        component_list = ccdom2ComponentList(ccdom)
        propList = component_list2hsal( component_list, hsalfilename)
    else: 
        f = open( hsalfilename, 'r' )
        hsal_model = f.read()
        f.close()
        propList = []
        offset, index = 0, hsal_model.find("THEOREM")
        while index != -1:
          endindex = hsal_model.rfind( ':', 0, index )
          startindex = hsal_model.rfind( ';', 0, endindex )
          propName = hsal_model[startindex+1:endindex].strip()
          propList.append( propName )
          offset = index + 1
          index = hsal_model.find("THEOREM", offset)
        print >> sys.stderr, 'Using existing {0} file'.format(hsalfilename)
        '''
        try:
            dom1 = xml.dom.minidom.parse(hsalfilename)
        except:
            print 'Model not supported: Unable to handle some expressions currently'
            sys.exit(-1)
        '''
    print '\nProperties in hybridsal model are ', propList
    return (basename, propList)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Part 2 of translation: From internal Component repr -> HSal
# -------------------------------------------------------------------
def component_list2hsal( component_list, hsalfilename):
  '''Dump the components, in my internal representation, to HSAL file'''
  contextname = os.path.basename(hsalfilename)
  with open(hsalfilename, 'w') as fp:
    print >> fp, '% Automatically generated by cybercomposition2hsal'
    print >> fp, '{0}: CONTEXT = '.format( contextname[:-5] )
    print >> fp, 'BEGIN'

    # print global declarations.... first collect them
    params = {}
    for component in component_list:
      for name in component.params.keys():
        if params.has_key(name):
          if params[name] == component.params[name]:
            pass
          elif params[name][0] == 'TYPE' and len(params[name][1])==len(component.params[name][1]):
            # ('TYPE','{gear0,gear1}') and ('TYPE','{gear1,gear0}')
            pass
          else:
            print params[name]
            print component.params[name]
            assert False, 'ERROR: Repeated inconsistent declaration for parameter {0}'.format(name)
      params.update( component.params )

    # try to extend params by including some local variables
    potential_params = {}
    for component in component_list:
      tmp = component.get_potential_params()
      if len(potential_params)==0:
        potential_params.update( tmp )
        continue
      for p_name in tmp.keys():
        if potential_params.has_key(p_name) and tmp[p_name] != potential_params[p_name]:
          # print 'Warning: {0} has different values in different components'.format(p_name)
          print 'W4{0}'.format(p_name),
          potential_params.clear()
          break
      if len(potential_params) != 0:
        potential_params.update( tmp )
      else:
        break   # failed to lift parameters...
    if len(potential_params) != 0:
      for component in component_list:
        component.move_to_params(potential_params)
    params.update( potential_params )
    # done: Now local vars that can be treated as params are moved up to params

    # print global declarations.... now print them
    ans = ''
    if params != None:
      # first print variable = constant
      for (name,(type_str, value)) in params.items():
        if value == None:
          ans += '{0}: {1};\n'.format(name,type_str,value)
        elif not isinstance(value, Expr) and (not isinstance(value,(str,unicode)) or len(value) < 6):
          ans += '{0}: {1} = {2};\n'.format(name,type_str,value)
      # next print variable = expression
      for (name,(type_str, value)) in params.items():
        if isinstance(value, Expr) or (isinstance(value,(str,unicode)) and len(value) >= 6):
          ans += '{0}: {1} = {2};\n'.format(name,type_str,value)
    print >> fp, ans
    for component in component_list:
      component.divide2mult() 
      print >> fp, component.toHSalModDecl(params) 
    propList = []
    for component in component_list:
      propSal, ipropList = process_propStr( component )
      print >> fp, propSal
      propList.extend( ipropList )    # update list of property names
    print >> fp, 'END'
    # print >> sys.stderr, 'Created file {0}'.format(hsalfilename)
    return propList
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Command-line invocation
# -------------------------------------------------------------------
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
    filename = argCheck(sys.argv, printUsage)
    cybercomposition2hsal(filename, sys.argv[2:])

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
# -------------------------------------------------------------------
