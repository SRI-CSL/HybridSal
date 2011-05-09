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

def valueOf(node):
    """return text value of node"""
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(i.data)

def getNameTag(node, tag):
    nodes = node.getElementsByTagName(tag)
    if (len(nodes) < 1):
        print node.toxml()
    childnode = nodes[0]
    return(valueOf(childnode))

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

def HSalPPLocalDecl(i):
    global fp
    print >> fp, "LOCAL " + HSalPPDecls(i.childNodes, "", "")

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

def HSalPPInfixApp(node):
    str1 = HSalPPExpr(appArg(node,1))
    str2 = getNameTag(node, 'NAMEEXPR')
    str3 = HSalPPExpr(appArg(node,2))
    return "("+str1+" "+str2+" "+str3+")"

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

def HSalPPApp(node):
    if node.getAttribute('INFIX') == 'YES':
        return HSalPPInfixApp(node)
    else:
        return HSalPPPrefixApp(node)

def HSalPPNextOperator(node):
    name = getNameTag(node, "NAMEEXPR")
    return name+"'"

def HSalPPSetPredExpr(node):
    str0 = "{"
    str0 += getNameTag(node, "IDENTIFIER")
    str0 += ":"
    str0 += getNameTag(node, "TYPENAME")
    str0 += "|"
    str0 += HSalPPExpr(getArg(node,3))
    str0 += "}"
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

def HSalPPExpr(node):
    if (node == None) or not(node.nodeType == node.ELEMENT_NODE):
        return ""
    if node.localName == "NAMEEXPR":
        return HSalPPNameExpr(node)
    elif node.localName == "APPLICATION":
        return HSalPPApp(node)
    elif node.localName == "NUMERAL":
        return HSalPPNumeral(node)
    elif node.localName == "NEXTOPERATOR":
        return HSalPPNextOperator(node)
    elif node.localName == "SETPREDEXPRESSION":
        return HSalPPSetPredExpr(node)
    elif node.localName == "CONDITIONAL":
        return HSalPPConditional(node)
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
    HSalPPAssgns(initdecl)
    print >> fp, "\n",

def HSalPPGuard(guard):
    global fp
    print >> fp, HSalPPExprs(guard.childNodes),

def HSalPPSimpleDefn(node):
    global fp
    str0 = HSalPPExpr(getArg(node,1))
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
            print >> fp, ";",
        HSalPPSimpleDefn(i)
        flag = True
    print >> fp, "\n",

def HSalPPGuardedCommand(node):
    global fp
    guard = node.getElementsByTagName("GUARD")[0]
    HSalPPGuard(guard)
    print >> fp, " --> "
    assgns = node.getElementsByTagName("ASSIGNMENTS")[0]
    HSalPPAssgns(assgns)
    
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
        HSalPPLocalDecl(i)
    invardecl = basemod.getElementsByTagName("INVARDECL")
    if not(invardecl == None) and len(invardecl) > 0:
        HSalPPInvarDecl(invardecl[0])
    initdecl = basemod.getElementsByTagName("INITFORDECL")
    if not(initdecl == None) and len(initdecl) > 0:
        HSalPPInitForDecl(initdecl[0])
    initdecl = basemod.getElementsByTagName("INITDECL")
    if not(initdecl == None) and len(initdecl) > 0:
        HSalPPInitDecl(initdecl[0])
    transdecl = basemod.getElementsByTagName("TRANSDECL")
    if not(transdecl == None) and len(transdecl) > 0:
        HSalPPTransDecl(transdecl[0])

def HSalPPModDecl(node):
    global fp
    print >> fp, "\n%s: MODULE =" % getName(node)
    print >> fp, "BEGIN" 
    basemods = node.getElementsByTagName("BASEMODULE")
    if (basemods == None) or len(basemods) == 0:
        print "Module is not a base module. Fill in code later"
    else:
        HSalPPBaseModule(basemods[0])
    print >> fp, "END;\n" 

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
        print >> fp, " = %s" % value
    print >> fp, ";"

def HSalPPNode(node):
    if node.localName == "MODULEDECLARATION":
        HSalPPModDecl(node)
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
