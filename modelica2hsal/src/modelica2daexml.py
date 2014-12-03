import sys
import os
import ddae
import xml.dom.minidom 

# Notes: TODO
# Sep 3, 2014: Initializations included for all ovars....
# Sep 3, 2014: trackPreserve attribute is carried forward

# -------------------------------------------------------------------
# Usage: Via python call
# -------------------------------------------------------------------
# modelica2daexml(modelicaXML_filename, options = [])
# options in '--addTime' or '--removeTime'
# Returns (modelicadom, daexml-dom, daexmlfilename)
#
# Warning: Do not use "modelicadom2daexml(modelicadom)"
# since it does not convert the MathML to my localXML
# LocalXML is used by the simplifier later on.
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Usage: Command-line
# -------------------------------------------------------------------
def printUsage():
    print '''
modelica2daexml -- a converter from Modelica to internal daexml file

Usage: python src/modelica2daexml.py <modelica_file.xml> [--addTime|--removeTime]

Description: This will create a file called modelica_file.daexml
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

def getNameTag(node, tag):
    nodes = node.getElementsByTagName(tag)
    if (len(nodes) < 1):
        print >> sys.stderr, node.toxml()
    childnode = nodes[0]
    return(valueOf(childnode))

def getName(node):
    return getNameTag(node, "IDENTIFIER")

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
                    print 'Null'
            assert False, 'Null children'
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
# mathml2localxml
# -------------------------------------------------------------------
def mathml2localxml(dom1):
    "dom1 = daexml DOM that uses MathML; rewrite mathml to my local XML on which simplifier works"
    mmls = dom1.getElementsByTagName('MathML')
    for i in mmls:
        j = mathml2myxml(i)
        if j == None:
            # use string attribute
            print 'No MathML expression found; parsing string expression'
            estr = i.getAttribute('string')
            j = ddae.parse_expr( estr )
        replace(i, j)
    return dom1

def replace(node, newnode):
    parentnode = node.parentNode
    parentnode.replaceChild(newChild=newnode,oldChild=node)

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
# REC apply: <MathML><math><expr></math></MathML> --> <expr>
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

# -------------------------------------------------------------------
# Get value of a variable, if possible, from its bindExpression
# Used to create variable=value equations in daexml DOM
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Modelica Var-xml list --> (variablevalue-list, rest-list)
# -------------------------------------------------------------------
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
            if i.getAttribute('trackPreserve')=='1':
              varval.setAttribute('trackPreserve', '1')
        else:
            ans.append(i)
    return (varvals, ans)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Same as above, but it is applied to ordered-variables.
# -------------------------------------------------------------------
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
                if i.getAttribute('trackPreserve')=='1':
                  varval.setAttribute('trackPreserve', '1')
                # print >> fp, '{0} = {1}'.format(name, value)
            else:
                ans.append(name)
    return (varvals, ans)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# This hack function is not used.
# -------------------------------------------------------------------
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
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Extract value from algorithm
# -------------------------------------------------------------------
def getVarValFromNominal( leftOutVars1 ):
    done_vars = []
    varvals = []
    for dangling_var in leftOutVars1:
      nominal = dangling_var.getElementsByTagName('nominal')
      if len(nominal) > 0:
        var_name = dangling_var.getAttribute('name').strip()
        rhs = getMathMLclone( nominal[0], nominal[0].getAttribute('string') )
        var = helper_create_tag_val('identifier', var_name)
        varvals.append(helper_create_app('variablevalue', [var, rhs]))
        done_vars.append( dangling_var )
    leftOutVars = [ i for i in leftOutVars1 if i not in done_vars ]
    return (varvals, leftOutVars)

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
            index2 = index2 if index2!=-1 else code.find(os.linesep, index1)
            index3 = index3 if index3!=-1 else code.find('=', index1 )
            if index2 == -1 or index3 == -1:
                # print 'Found variable {0} in initialEquation, but not in var := expr form'.format(var_name)
                continue
            if index3 > index1 + len(var_name) + 4:
                continue
            rhs = ddae.parse_expr( code[index3+2:index2] )
            var = helper_create_tag_val('identifier', var_name)
            varvals.append(helper_create_app('variablevalue', [var, rhs]))
            done_vars.append( dangling_var )
    leftOutVars = [ i for i in leftOutVars1 if i not in done_vars ]
    return (varvals, leftOutVars)
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# Main function to convert modelicaDOM to daexml-DOM
# -------------------------------------------------------------------
def modelicadom2daexml(modelicadom):
    "dom = modelicaXML dom; output daexml DOM... WITH MathMLs now"
    global dom
    impl = xml.dom.minidom.getDOMImplementation()
    dom = impl.createDocument(None, "daexml", None)
    ctxt = modelicadom.getElementsByTagName('dae')[0]
    variables = getChildByTagName(ctxt, 'variables')
    equations = getChildByTagName(ctxt, 'equations')
    # zeroCrossing = getChildByTagName(ctxt, 'zeroCrossingList')
    # arrayOfEqns = getChildByTagName(ctxt, 'arrayOfEquations')
    # algorithms = getChildByTagName(ctxt, 'algorithms')
    # functions = getChildByTagName(ctxt, 'functions')
    assert variables != None, 'Variables not found in input XML file!'
    # Now start printing .dae file
    tmp = getChildByTagName(variables, 'orderedVariables')
    ovars = tmp.getElementsByTagName('variable') if tmp != None else []
    tmp = getChildByTagName(variables, 'knownVariables')
    kvars = tmp.getElementsByTagName('variable') if tmp != None else []
    tmp = getChildByTagName(variables, 'externalVariables')
    kvars.extend( tmp.getElementsByTagName('variable') if tmp != None else [] )
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

    # Now collect variable=value expressions from knownVariables
    (vv1,leftOutVars1) = printFixedParametersNew(kvars)
    if len(leftOutVars1) > 0:
        print >> sys.stderr, 'Note: {0} known variable do not have a bindExpression; for e.g., {1}. Trying initialValue'.format(len(leftOutVars1), leftOutVars1[0].getAttribute('name'))
        (vv2,leftOutVars1) = printFixedParametersNew(leftOutVars1, ['initialValue'])
        vv1.extend(vv2)
    if len(leftOutVars1) > 0:
        print >> sys.stderr, 'Note: {0} known vars have no bind expr and no initialValue; for e.g., {1}'.format(len(leftOutVars1),leftOutVars1[0].getAttribute('name'))
        print >> sys.stderr, 'Trying to find bindExpression from initialEquations section...',
        simpleEquations = ctxt.getElementsByTagName('initialEquations')
        (vv3,leftOutVars1) = getVarValFromAlgo( simpleEquations, leftOutVars1 )
        print >> sys.stderr, '{0} found.'.format(len(vv3))
        vv1.extend(vv3)
    if len(leftOutVars1) > 0:
        print >> sys.stderr, 'Trying to find bindExpression from nominal section...',
        (vv3_2,leftOutVars1) = getVarValFromNominal( leftOutVars1 )
        print >> sys.stderr, '{0} found.'.format(len(vv3_2))
        vv1.extend(vv3_2)
    if len(leftOutVars1) > 0:
        print >> sys.stderr, 'WARNING: {0} known vars have NO bindexpr/initialValue/initialEquation; for e.g., {1}'.format(len(leftOutVars1),leftOutVars1[0].getAttribute('name'))
    # vv1 = all variable-value pairs from knownVariables

    # Collect variable=value expressions from orderedVariables
    (vv4, leftOutVars)  = printFixedParameters(ovars, ['continuous'],['bindExpression'])
    leftOutVars.extend(leftOutVars1)
    print 'Note: {0} ordered vars have bind exprs; {1} ordered vars remaining now...'.format(len(vv4),len(leftOutVars))
    #vv1.extend(vv2)
    #vv1.extend(vv3)
    vv1.extend(vv4)
    # vv1 = all variable-value pairs from kvars and ovars
    # leftOutVars = all ovars+kvars that are not= anything so far.

    # Extract variable=value from the equations
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
            if i.getAttribute('trackPreserve')=='1':
              varval.setAttribute('trackPreserve', '1')
            vv1.append(varval)
        else:
            eqns.append( val )
    print 'Note: Found {0} var=val equations'.format(len(equationL)-len(eqns))
    # Now vv1 = all var-value pairs, eqns = remaining equations

    # In daexml dom, put all of vv1
    knownVariables = helper_create_app('knownVariables', vv1, None, len(vv1))
    knownVariables.setAttribute('arity',str(len( vv1 )))
    # print 'knownVariables XML creation done............'

    # Add whenEquation to eqns
    equationL = equations.getElementsByTagName('whenEquation')
    for i in equationL:
        (val, lhsrhs) = getMathMLcloneEqn( i, valueOf(i) )
        eqns.append( val )

    # In daexml dom, put all of eqns
    # print >> fp, '#####equations'
    equations = helper_create_app('equations', eqns, None, len(eqns))
    equations.setAttribute('arity',str(len( eqns )))
    # print 'Equation XML creation done............'
    # print >> fp, '#####initializations'

    # var=val and eqns have been added to the DOM. Now, get inits
    inits = []
    # for node in statevars:
    for node in ovars:
        val0 = getInitialValue(node)
        if val0 != None:
            initid = helper_create_tag_val('initidentifier', node.getAttribute('name'))
            eqn = helper_create_app('equation', [initid, val0])
            inits.append(eqn)
            #print >> fp, '{0} = {1}'.format(node.getAttribute('name'), val0)
    initializations = helper_create_app('initializations', inits, None, len(inits))
    #print 'Initializations XML creation done............'

    # Now, var=val, eqns, and inits have been added to the daexml DOM
    allnodes = [continuousState, discreteState, knownVariables, equations, initializations]
    ans = helper_create_app('source_text', allnodes)
    dom.documentElement.appendChild(ans)
    return dom
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# argcheck function
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

# -------------------------------------------------------------------
# Main function -- from filename now.
# -------------------------------------------------------------------
def modelica2daexml(filename, options = []):
    def existsAndNew(filename1, filename2):
        if os.path.isfile(filename1) and os.path.getmtime(filename1) >= os.path.getmtime(filename2):
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
    # now parse the dae into daexml
    daexmlfilename = basename + '.daexml'
    if not existsAndNew(daexmlfilename, filename):
        dom1 = modelicadom2daexml(modelicadom)
        dom1 = mathml2localxml(dom1)
        if '--removeTime' in options:
            dom1 = removeTime(dom1)
        with open(daexmlfilename, 'w') as fp:
            print >> fp, dom1.toprettyxml()
        print >> sys.stderr, 'Created file {0}'.format(daexmlfilename)
    else: 
        print >> sys.stderr, 'Using existing {0} file'.format(daexmlfilename)
        try:
            dom1 = xml.dom.minidom.parse(daexmlfilename)
        except:
            print 'Model not supported: Unable to handle some expressions currently'
            sys.exit(-1)
    return (modelicadom, dom1, daexmlfilename)
# -------------------------------------------------------------------

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
