import xml.dom.minidom
import xml.parsers.expat
import sys

precedence = ['/', '*', '-', '+', '>', '>=', '<', '<=', '=', 'NOT', 'AND', 'OR', '=>']

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

def HSalPPDecl(node):
    return getName(node)+HSalPPType(getArg(node,2), ":", "")
    
def HSalPPDecls(nodes, str1, str2):
    """print >> fp, every VARDECL in nodes"""
    k = 0
    str0 = ""
    for j in nodes:
        if (j.localName == "VARDECL"):
            if (k > 0):
                str0 = str0+","
            else:
                str0 = str0+str1
            str0 = str0 + HSalPPDecl(j)
            k = k + 1
    if (k > 0):
        str0 = str0 + str2
    return str0

def HSalPPLocalGlobalDecl(i, kind):
    global fp
    print >> fp, kind + HSalPPDecls(i.childNodes, "", "")

def HSalPPNameExpr(node):
    return valueOf(node)

def HSalPPNumeral(node):
    return valueOf(node)

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None

def appArg(node,index):
    tuples = node.getElementsByTagName('TUPLELITERAL')[0]
    return getArg(tuples,index)

def higherPrec(op1, op2):
    """Does op1 have higher precedence than op2?"""
    global precedence
    if op1 in precedence and op2 in precedence:
        return precedence.index(op1) < precedence.index(op2)
    elif op1 == None:
        return False
    else:
        print >> sys.stderr, "EITHER Op not found %s" % op1 
        print >> sys.stderr, "OR Op not found %s" % op2 
        return True

def HSalPPInfixApp(node,outerSymb=None):
    str2 = getNameTag(node, 'NAMEEXPR')
    str1 = HSalPPExpr(appArg(node,1),outerSymb=str2)
    str3 = HSalPPExpr(appArg(node,2),outerSymb=str2)
    if higherPrec(outerSymb,str2):
        ans = "("+str1+" "+str2+" "+str3+")"
    else:
        ans = str1+" "+str2+" "+str3
    return ans

def HSalPPPrefixApp(node):
    str0 = getNameTag(node, 'NAMEEXPR')
    i = 1
    expr = appArg(node,i)
    while not(expr == None):
        if (i == 1):
            str0 = str0 + "("
        else:
            str0 = str0 + ","
        str0 = str0 + HSalPPExpr(expr)
	i = i + 1
        expr = appArg(node,i)
    if (i > 1):
        str0 = str0 + ")"
    return str0

def HSalPPApp(node,outerSymb=None):
    if node.getAttribute('INFIX') == 'YES':
        return HSalPPInfixApp(node,outerSymb)
    else:
        return HSalPPPrefixApp(node)

def HSalPPNextOperator(node):
    name = getNameTag(node, "NAMEEXPR")
    return name+"'"

def HSalPPSetPredExpr(node):
    str0 = "{ "
    str0 += getNameTag(node, "IDENTIFIER")
    str0 += " : "
    str0 += getNameTag(node, "TYPENAME")
    str0 += " | "
    str0 += HSalPPExpr(getArg(node,3))
    str0 += " }"
    return str0

def HSalPPConditional(node):
    str0 = "IF "
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j += 1
            if j == 1:
                str0 += HSalPPExpr(i)
            elif j == 2:
                str0 += " THEN "
                str0 += HSalPPExpr(i)
            elif j == 3:
                str0 += " ELSE "
                str0 += HSalPPExpr(i)
                str0 += " ENDIF "
    return str0

def HSalPPExpr(node, outerSymb=None):
    if (node == None) or not(node.nodeType == node.ELEMENT_NODE):
        return ""
    if node.localName == "NAMEEXPR":
        return HSalPPNameExpr(node)
    elif node.localName == "APPLICATION":
        return HSalPPApp(node,outerSymb)
    elif node.localName == "NUMERAL":
        return HSalPPNumeral(node)
    elif node.localName == "NEXTOPERATOR":
        return HSalPPNextOperator(node)
    elif node.localName == "SETPREDEXPRESSION":
        return HSalPPSetPredExpr(node)
    elif node.localName == "CONDITIONAL":
        return HSalPPConditional(node)
    else:
        print >> sys.stderr, node.toxml()
        print >> sys.stderr, 'Node EXPR %s unknown. Missing code' % node.localName
    return None

def HSalPPExprs(nodes):
    for node in nodes:
        if (node.nodeType == node.ELEMENT_NODE):
            return HSalPPExpr(node)

def HSalPPInvarDecl(invardecl):
    global fp
    print >> fp, "INVARIANT",
    exprs = invardecl.childNodes
    print >> fp, HSalPPExprs(exprs),
    print >> fp, "\n",

def HSalPPInitForDecl(initdecl):
    global fp
    print >> fp, "INITFORMULA",
    print >> fp, HSalPPExprs(initdecl.childNodes),
    print >> fp, "\n",

def HSalPPInitDecl(initdecl):
    global fp
    print >> fp, "INITIALIZATION"
    firstChild = getArg(initdecl, 1)
    if firstChild.localName == "SIMPLEDEFINITION":
        HSalPPAssgns(initdecl)
    elif firstChild.localName == "SOMECOMMANDS":
        HSalPPSomecommands(initdecl)
    else:
        print "ERROR: INITIALIZATION block found unexpected tag ",
        print firstChild.localName
    print >> fp, "\n",

def HSalPPDefDecl(defdecl):
    global fp
    print >> fp, "DEFINITION"
    firstChild = getArg(defdecl, 1)
    if not(firstChild.localName == "SIMPLEDEFINITION"):
        print "ERROR: DEFINITION block found unexpected tag ",
        print firstChild.localName
    else: 
        HSalPPAssgns(defdecl)
    print >> fp, "\n",

def HSalPPGuard(guard):
    global fp
    print >> fp, HSalPPExprs(guard.childNodes),

def HSalPPSimpleDefn(node):
    global fp
    str0 = '\t'+HSalPPExpr(getArg(node,1))
    rhsexpr = node.getElementsByTagName("RHSEXPRESSION")
    rhssel  = node.getElementsByTagName("RHSSELECTION")
    if not(rhsexpr.length == 0):
        str0 += " = "
        str0 += HSalPPExprs(rhsexpr[0].childNodes)
    elif not(rhssel.length == 0):
        str0 += " IN "
        str0 += HSalPPExprs(rhssel[0].childNodes)
    print >> fp, str0,

def HSalPPAssgns(assgns):
    global fp
    defs = assgns.getElementsByTagName("SIMPLEDEFINITION")
    flag = False
    for i in defs:
        if flag:
            print >> fp, ";\n",
        HSalPPSimpleDefn(i)
        flag = True
    print >> fp, "\n",

def HSalPPGuardedCommand(node):
    global fp
    guard = node.getElementsByTagName("GUARD")[0]
    HSalPPGuard(guard)
    print >> fp, " --> "
    assgns = node.getElementsByTagName("ASSIGNMENTS")
    if (not(assgns == None) and len(assgns) > 0):
        HSalPPAssgns(assgns[0])
    
def HSalPPMultiCommand(node):
    global fp
    print >> fp, "["
    gcmds = node.getElementsByTagName("GUARDEDCOMMAND")
    i = 0
    for j in gcmds:
        if not(i == 0):
            print >> fp, " || "
        HSalPPGuardedCommand(j)
        i = i + 1
    print >> fp, "]"

def HSalPPTransDecl(transdecl):
    global fp
    print >> fp, "TRANSITION"
    HSalPPSomecommands(transdecl)

def HSalPPSomecommands(transdecl):
    global fp
    print >> fp, "["
    j = 0
    cmds = transdecl.getElementsByTagName("SOMECOMMANDS")[0]
    if not(cmds == None):
        cmds = cmds.childNodes
    for i in cmds:
        j += 1
        if i.localName == "GUARDEDCOMMAND":
            if not(j == 1):
                print >> fp, "[]"
            HSalPPGuardedCommand(i)
        elif i.localName == "MULTICOMMAND":
            if not(j == 1):
                print >> fp, "[]"
            HSalPPMultiCommand(i)
        else:
            j -= 1
    print >> fp, "]"

def HSalPPBaseModule(basemod):
    ldecls = basemod.getElementsByTagName("LOCALDECL")
    for i in ldecls:
        HSalPPLocalGlobalDecl(i, 'LOCAL ')
    ldecls = basemod.getElementsByTagName("GLOBALDECL")
    for i in ldecls:
        HSalPPLocalGlobalDecl(i, 'GLOBAL ')
    ldecls = basemod.getElementsByTagName("INPUTDECL")
    for i in ldecls:
        HSalPPLocalGlobalDecl(i, 'INPUT ')
    ldecls = basemod.getElementsByTagName("OUTPUTDECL")
    for i in ldecls:
        HSalPPLocalGlobalDecl(i, 'OUTPUT ')
    invardecl = basemod.getElementsByTagName("INVARDECL")
    if not(invardecl == None) and len(invardecl) > 0:
        HSalPPInvarDecl(invardecl[0])
    defdecl = basemod.getElementsByTagName("DEFDECL")
    if not(defdecl == None) and len(defdecl) > 0:
        HSalPPDefDecl(defdecl[0])
    initdecl = basemod.getElementsByTagName("INITFORDECL")
    if not(initdecl == None) and len(initdecl) > 0:
        HSalPPInitForDecl(initdecl[0])
    initdecl = basemod.getElementsByTagName("INITDECL")
    if not(initdecl == None) and len(initdecl) > 0:
        HSalPPInitDecl(initdecl[0])
    transdecl = basemod.getElementsByTagName("TRANSDECL")
    if not(transdecl == None) and len(transdecl) > 0:
        HSalPPTransDecl(transdecl[0])

def HSalPPComposition(node, op, opTop):
    if not(op == opTop):
        print >> fp, '(', 
    HSalPPMod(node.childNodes, op)
    if not(op == opTop):
        print >> fp, ')', 

def HSalPPMod(nodeL, op = None):
    global fp
    first = True
    for node in nodeL:
        if not(node.nodeType == node.ELEMENT_NODE):
            continue
        if node.localName == 'IDENTIFIER' or node.localName == 'VARDECLS':
            continue
        if first:
            first = False
        else:
            print >> fp, op,
        if node.localName == 'BASEMODULE':
            print >> fp, "BEGIN" 
            HSalPPBaseModule(node)
            print >> fp, "END",
        elif node.localName == 'ASYNCHRONOUSCOMPOSITION':
            HSalPPComposition(node, '[]', op)
        elif node.localName == 'SYNCHRONOUSCOMPOSITION':
            HSalPPComposition(node, '||', op)
        elif node.localName == 'MODULEINSTANCE':
            modName = getNameTag(node, "MODULENAME")
            # ignoring MODULEACTUALS
            print >> fp, modName,
        else:
            print "Unrecognized module type. Fill in code later"
    if op == None:
        print >> fp, ";\n"

def HSalPPModDecl(node):
    global fp
    print >> fp, "\n%s: MODULE =" % getName(node)
    childNodes = node.childNodes
    HSalPPMod(childNodes)

def HSalPPModuleInstance(node):
    return getNameTag(node, "MODULENAME")
    
def HSalPPModuleModels(node):
    global fp
    str1 = HSalPPModuleInstance(node.getElementsByTagName("MODULEINSTANCE")[0])
    str2 = HSalPPExpr(getArg(node,2))
    print >> fp, str1+" |- "+str2+";"

def HSalPPAssertionDecl(node):
    global fp
    print >> fp, getNameTag(node,"IDENTIFIER"),
    print >> fp, ":",
    print >> fp, getNameTag(node,"ASSERTIONFORM")
    HSalPPModuleModels(node.getElementsByTagName("MODULEMODELS")[0])

def HSalPPFuncType(node):
    lhs = getArg(node,1)
    rhs = getArg(node,2)
    str1 = HSalPPType(lhs,"","")
    str2 = HSalPPType(rhs,"","")
    return "["+str1+"->"+str2+"]"

def HSalPPStateType(node):
    str1 = HSalPPModuleInstance(node.getElementsByTagName("MODULEINSTANCE")[0])
    return str1+".STATE"

def HSalPPScalarType(node):
    """Print { s1,s2,s3,s4 } given
      <SCALARTYPE PLACE="5 14 5 30">
        <SCALARELEMENT PLACE="5 15 5 17">s1</SCALARELEMENT>
        <SCALARELEMENT PLACE="5 19 5 21">s2</SCALARELEMENT>
        <SCALARELEMENT PLACE="5 23 5 25">s3</SCALARELEMENT>
        <SCALARELEMENT PLACE="5 27 5 29">s4</SCALARELEMENT>
      </SCALARTYPE>"""
    first = True
    str1 = "{ "
    for i in node.getElementsByTagName("SCALARELEMENT"):
        if first:
            first = False
        else:
            str1 += " , "
        str1 += valueOf(i)
    return str1+" }"

def HSalPPSubrange(node):
    """Print [1 .. 2] given 
            <SUBRANGE PLACE="60 15 60 23">
              <NUMERAL PLACE="60 16 60 17">1</NUMERAL>
              <NUMERAL PLACE="60 21 60 22">2</NUMERAL>
            </SUBRANGE>"""
    lhs = getArg(node,1)
    rhs = getArg(node,2)
    str1 = HSalPPExpr(lhs)
    str2 = HSalPPExpr(rhs)
    return "["+str1+" .. "+str2+"]"
    
def HSalPPType(node,str1,str2):
    if not(node.nodeType == node.ELEMENT_NODE):
        return None
    str0 = None
    if node.localName == "TYPENAME":
        str0 = valueOf(node)
    elif node.localName == "FUNCTIONTYPE":
        str0 = HSalPPFuncType(node)
    elif node.localName == "STATETYPE":
        str0 = HSalPPStateType(node)
    elif node.localName == "SCALARTYPE":
        str0 = HSalPPScalarType(node)
    elif node.localName == "SUBRANGE":
        str0 = HSalPPSubrange(node)
    else:
        print node.toxml()
        print 'Node TYPE %s not handled. Missing code' % node.localName
    if not(str0 == None):
        return str1+str0+str2

def HSalPPCnstDecl(node):
    global fp
    print >> fp, getNameTag(node, "IDENTIFIER"),
    vardecls = node.getElementsByTagName("VARDECLS")
    if not(vardecls == None) and len(vardecls) > 0:
        arg = vardecls[0]
        print >> fp, HSalPPDecls(arg.childNodes,"(",")"),
    arg = getArg(node,3)
    print >> fp, HSalPPType(arg,": ",""),
    arg = getArg(node,4)
    value = HSalPPExpr(arg)
    if not(value == None) and not(value == ""):
        print >> fp, " = \n %s" % value,
    print >> fp, ";\n"

def HSalPPTypeDecl(node):
    global fp
    print >> fp, "\n%s: TYPE =" % getName(node),
    print >> fp, HSalPPType(getArg(node,2), "", ""),
    print >> fp, ";\n"

def HSalPPNode(node):
    if node.localName == "MODULEDECLARATION":
        HSalPPModDecl(node)
    elif node.localName == "TYPEDECLARATION":
        HSalPPTypeDecl(node)
    elif node.localName == "ASSERTIONDECLARATION":
        HSalPPAssertionDecl(node)
    elif node.localName == "CONSTANTDECLARATION":
        HSalPPCnstDecl(node)
    elif node.nodeType == node.ELEMENT_NODE:
        print "Missing code for Node %s" % node.localName

def HSalPPContextBody(ctxtbody):
    for i in ctxtbody.childNodes:
        HSalPPNode(i)

def getVariableValue(var):
    "return value of the variable by looking at different places"
    tags = [ 'bindExpression', 'initialValue' ]
    for i in tags:
        val = var.getElementsByTagName(i)
        if val != None and len(val) > 0:
            value = val[0].getAttribute('string')
            return value
    print >> sys.stderr, 'Note: value for variable {0} not fixed'.format(var.getAttribute('name'))
    return None

def printFixedParameters(varList, varTypeList):
    ans = []
    for i in varList:
        # fixed = i.getAttribute('fixed')
        param = i.getAttribute('variability')
        inout = i.getAttribute('direction')
        if param in varTypeList and inout != 'input':
            value = getVariableValue(i)
            name = i.getAttribute('name')
            if value != None:
                print >> fp, '{0} = {1}'.format(name, value)
            else:
                ans.append(name)
    return ans

def HSalPPContext(dom, filepointer=sys.stdout):
    global fp 
    fp = filepointer
    ctxt = dom.getElementsByTagName('dae')[0]
    #print ctxt.tagName
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
    tmp = getChildByTagName(variables, 'knownVariables')
    kvars = tmp.getElementsByTagName('variable') if tmp != None else []
    #
    print >> fp, '#####{0}'.format('continuousState')
    for i in ovars:
        if i.getAttribute('variability') == 'continuousState':
            print >> fp, i.getAttribute('name')
    print >> fp, '#####{0}'.format('discreteState')
    for i in ovars:
        if i.getAttribute('variability') == 'discrete':
            print >> fp, i.getAttribute('name')
    # print constants or parameters with their values
    print >> fp, '#####{0}'.format('knownVariables')
    leftOutVars1 = printFixedParameters(kvars, ['parameter', 'constant', 'discrete'])
    assert len(leftOutVars1) == 0, 'ERROR: Some fixed param  equation missed'
    leftOutVars1  = printFixedParameters(kvars, ['continuous'])
    assert len(leftOutVars1) == 0, 'ERROR: Some fixed cont equation missed {0}'.format(leftOutVars1)
    leftOutVars  = printFixedParameters(ovars, ['continuous'])
    leftOutVars.extend(leftOutVars1)
    # 
    assert equations != None, 'No Equations found in input XML file!!'
    equationL = equations.getElementsByTagName('equation')
    eqns = []
    for i in equationL:
        eqni = valueOf(i)
        eq_index = eqni.index('=')
        lhs = eqni[0:eq_index].strip()
        if lhs in leftOutVars:
            print >> sys.stderr, 'Note: Found value for {0} in equations'.format(lhs)
            print >> fp, eqni.strip() 
        else:
            eqns.append(eqni)
    equationL = equations.getElementsByTagName('whenEquation')
    for i in equationL:
        eqni = valueOf(i)
        eq_index = eqni.index(':=')
        lhs = eqni[0:eq_index].strip()
        rhs = eqni[eq_index+1:].strip()
        eqns.append(lhs + rhs)
    print >> fp, '#####equations'
    for i in eqns:
        print >> fp, i.strip()

def start_element(name, attrs):
    if name == 'bindExpression':
        print >> fp, name, attrs
        attrs['string'] = ''

def attlistdeclhandler(elname, attname, typeN ):
    print elname, attname, typeN
    if elname == 'bindExpression':
        print elname, attname, typeN

def elmtdeclhandle(name,model):
    print name

if __name__ == "__main__":
    #xmlparser = xml.parsers.expat.ParserCreate()
    dom = xml.dom.minidom.parse(sys.argv[1])
    #xmlparser.StartElementHandler = start_element
    #xmlparser.ElementDeclHandler = elmtdeclhandle
    #xmlparser.AttlistDeclHandler = attlistdeclhandler
    #fp = open(sys.argv[1])
    #dom = xmlparser.ParseFile(fp)
    HSalPPContext(dom)
