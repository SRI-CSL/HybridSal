# Pretty Printer for HSal XML
# Reads salfile.xml and outputs salfile.sal

# TODO:
# INITDECL not handled yet -- initfordecl should be changed too.

import xml.dom.minidom
import sys

# Caveat1: Some functions return a string, others print >> fp
# Caveat2: global fp is used as a file pointer; 
#   From this file, you can safely use HSalPPContext; 
#   For using other functions, need to set fp

precedence = ['/', '*', '-', '+', '>', '>=', '<', '<=', '=', '/=', 'NOT', 'AND', 'and', 'OR', 'or', 'XOR', '=>', '<=>']

def valueOf(node):
    """return text value of node"""
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(i.data)

def getNameTag(node, tag):
    nodes = node.getElementsByTagName(tag)
    try:
        childnode = nodes[0]
        return(valueOf(childnode))
    except IndexError as e:
        print e 
        print node.toxml()
        raise

def getName(node):
    return getNameTag(node, "IDENTIFIER")

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
        print "EITHER Op not found %s" % op1 
        print "OR Op not found %s" % op2 
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

def HSalPPSetListExpr(node):
    first = True
    str1 = "{ "
    for i in node.getElementsByTagName("NAMEEXPR"):
        if first:
            first = False
        else:
            str1 += " , "
        str1 += valueOf(i)
    return str1+" }"

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

def HSalPPArrayLiteral(node):
    '''<ARRAYLITERAL> <INDEXVARDECL><ID><SUBRANGE></INDEXVARDECL> <EXPR>
       print [ [i:TYPE] Expr ] '''
    lhs = getArg(node,1)
    rhs = getArg(node,2)
    str1 = HSalPPDecl(lhs)
    str2 = HSalPPExpr(rhs)
    return "[ ["+str1+"] "+str2+" ]"

def HSalPPArraySelection(node):
    '''<ARRAYSELECTION PLACE="122 46 122 55">
         EXPR EXPR <ARRAYSELECTION> PRINT EXPR[EXPR]'''
    lhs = getArg(node,1)
    rhs = getArg(node,2)
    str1 = HSalPPExpr(lhs)
    str2 = HSalPPExpr(rhs)
    return str1+"["+str2+"]"

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
    elif node.localName == "ARRAYLITERAL":
        return HSalPPArrayLiteral(node)
    elif node.localName == "ARRAYSELECTION":
        return HSalPPArraySelection(node)
    else:
        print node.toxml()
        print 'Node EXPR %s unknown. Missing code' % node.localName
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

def HSalPPLabeledCommand(node):
    global fp
    label = node.getElementsByTagName("LABEL")[0]
    print >> fp, "{0}: ".format(valueOf(label))
    gc = node.getElementsByTagName("GUARDEDCOMMAND")[0]
    HSalPPGuardedCommand(gc)

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
    cmds = transdecl.getElementsByTagName("SOMECOMMANDS")
    if cmds != None and len(cmds) > 0:
        HSalPPSomecommands(cmds[0])
        return
    # transdecl is a list of simpledefinitions...
    HSalPPAssgns(transdecl)

def HSalPPSomecommands(cmds):
    global fp
    print >> fp, "["
    j = 0
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
        elif i.localName == "LABELEDCOMMAND":
            if not(j == 1):
                print >> fp, "[]"
            HSalPPLabeledCommand(i)
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

def HSalPPArrayType(node):
    '''Print ARRAY A OF B given <ARRAYTYPE PLACE="46 7 46 51">
        A B </ARRAYTYPE>'''
    lhs = getArg(node,1)
    rhs = getArg(node,2)
    str1 = HSalPPType(lhs, '', '')
    str2 = HSalPPType(rhs, '', '')
    return "ARRAY "+str1+" OF "+str2
    
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
    elif node.localName == "ARRAYTYPE":
        str0 = HSalPPArrayType(node)
    elif node.localName == "SETPREDEXPRESSION":
        str0 = HSalPPSetPredExpr(node)
    elif node.localName == "SETLISTEXPRESSION":
        str0 = HSalPPSetListExpr(node)
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

def HSalPPContext(ctxt, filepointer=sys.stdout):
    global fp 
    fp = filepointer
    print >> fp, "%s: CONTEXT = " % getName(ctxt)
    print >> fp, "BEGIN" 
    HSalPPContextBody(ctxt.getElementsByTagName("CONTEXTBODY")[0])
    print >> fp, "END"

if __name__ == "__main__":
    dom = xml.dom.minidom.parse(sys.argv[1])
    HSalPPContext(dom)
