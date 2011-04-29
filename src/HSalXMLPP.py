# Pretty Printer for HSal XML
# Reads salfile.xml and outputs salfile.sal
import xml.dom.minidom
import sys

# Some functions return a string, others print to stdout

def valueOf(node):
    "return text value of node"
    for i in node.childNodes:
        if i.nodeType == i.TEXT_NODE:
            return(i.data)

def getNameTag(node, tag):
    node = node.getElementsByTagName(tag)[0]
    return(valueOf(node))

def getName(node):
    return getNameTag(node, "IDENTIFIER")

def HSalPPDecl(node):
    return getName(node)+HSalPPType(getArg(node,2), ":", "")
    
def HSalPPDecls(nodes, str1, str2):
    "print every VARDECL in nodes"
    k = 0
    str0 = ""
    for j in nodes:
        if (j.localName == "VARDECL"):
            #print j
            #print j.toxml()
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
    print "LOCAL " + HSalPPDecls(i.childNodes, "", "")
    #print i.toxml()

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
    #print "Error: Argument not found!"
    return None

def appArg(node,index):
    #print node.toxml()
    tuples = node.getElementsByTagName('TUPLELITERAL')[0]
    return getArg(tuples,index)

def HSalPPInfixApp(node):
    str1 = HSalPPExpr(appArg(node,1))
    str2 = getNameTag(node, 'NAMEEXPR')
    str3 = HSalPPExpr(appArg(node,2))
    return str1+" "+str2+" "+str3

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

def HSalPPExpr(node):
    # print node.localName
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
    else:
        print node.toxml()
        print 'Node EXPR %s unknown. Missing code' % node.localName
    return None

def HSalPPExprs(nodes):
    for node in nodes:
        if (node.nodeType == node.ELEMENT_NODE):
            return HSalPPExpr(node)
        #if (node.nodeType == node.TEXT_NODE):
            #print node.data

def HSalPPInvarDecl(invardecl):
    print "INVARIANT",
    exprs = invardecl.childNodes
    print HSalPPExprs(exprs),
    print "\n",

def HSalPPInitForDecl(initdecl):
    print "INITFORMULA",
    print HSalPPExprs(initdecl.childNodes),
    print "\n",

def HSalPPGuard(guard):
    print HSalPPExprs(guard.childNodes),

def HSalPPSimpleDefn(node):
    str0 = HSalPPExpr(getArg(node,1))
    rhsexpr = node.getElementsByTagName("RHSEXPRESSION")
    rhssel  = node.getElementsByTagName("RHSSELECTION")
    if not(rhsexpr.length == 0):
        str0 += "="
        str0 += HSalPPExprs(rhsexpr[0].childNodes)
    elif not(rhssel.length == 0):
        str0 += "IN"
        str0 += HSalPPExprs(rhssel[0].childNodes)
    print str0,

def HSalPPAssgns(assgns):
    defs = assgns.getElementsByTagName("SIMPLEDEFINITION")
    flag = False
    for i in defs:
        if flag:
            print(";"),
        HSalPPSimpleDefn(i)
        flag = True
    print "\n",

def HSalPPGuardedCommand(node):
    guard = node.getElementsByTagName("GUARD")[0]
    HSalPPGuard(guard)
    print(" --> ")
    assgns = node.getElementsByTagName("ASSIGNMENTS")[0]
    HSalPPAssgns(assgns)
    
def HSalPPMultiCommand(node):
    print("[")
    gcmds = node.getElementsByTagName("GUARDEDCOMMAND")
    i = 0
    for j in gcmds:
        if not(i == 0):
            print " || "
        HSalPPGuardedCommand(j)
        i = i + 1
    print("]")

def HSalPPTransDecl(transdecl):
    print "TRANSITION"
    print "["
    j = 0
    cmds = transdecl.getElementsByTagName("SOMECOMMANDS")[0]
    if not(cmds == None):
        cmds = cmds.childNodes
    for i in cmds:
        j += 1
        if i.localName == "GUARDEDCOMMAND":
            if not(j == 1):
                print "[]"
            HSalPPGuardedCommand(i)
        elif i.localName == "MULTICOMMAND":
            if not(j == 1):
                print "[]"
            HSalPPMultiCommand(i)
        else:
            j -= 1
    print "]"

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
    transdecl = basemod.getElementsByTagName("TRANSDECL")
    if not(transdecl == None) and len(transdecl) > 0:
        HSalPPTransDecl(transdecl[0])

def HSalPPModDecl(node):
    print "\n%s: MODULE =" % getName(node)
    print "BEGIN" 
    basemods = node.getElementsByTagName("BASEMODULE")
    if (basemods == None) or len(basemods) == 0:
        print "Module is not a base module. Fill in code later"
    else:
        HSalPPBaseModule(basemods[0])
    print "END;\n" 

def HSalPPModuleInstance(node):
    return getNameTag(node, "MODULENAME")
    
def HSalPPModuleModels(node):
    str1 = HSalPPModuleInstance(node.getElementsByTagName("MODULEINSTANCE")[0])
    str2 = HSalPPExpr(getArg(node,2))
    print str1+" |- "+str2+";"

def HSalPPAssertionDecl(node):
    print getNameTag(node,"IDENTIFIER"),
    print ":",
    print getNameTag(node,"ASSERTIONFORM")
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
    print getNameTag(node, "IDENTIFIER"),
    vardecls = node.getElementsByTagName("VARDECLS")
    if not(vardecls == None) and len(vardecls) > 0:
        arg = vardecls[0]
        print HSalPPDecls(arg.childNodes,"(",")"),
    arg = getArg(node,3)
    print HSalPPType(arg,": ",""),
    arg = getArg(node,4)
    value = HSalPPExpr(arg)
    if not(value == None) and not(value == ""):
        print " = %s" % value
    print ";"

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

def HSalPPContext(ctxt):
    print "%s: CONTEXT = " % getName(ctxt)
    print "BEGIN" 
    HSalPPContextBody(ctxt.getElementsByTagName("CONTEXTBODY")[0])
    print "END" 

if __name__ == "__main__":
    dom = xml.dom.minidom.parse(sys.argv[1])
    HSalPPContext(dom)
