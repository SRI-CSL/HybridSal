# Pretty Printer for HSal XML
# Reads salfile.xml and outputs salfile.sal

# TODO:
# INITDECL not handled yet -- initfordecl should be changed too.

from __future__ import print_function
import xml.dom.minidom
import sys

# Caveat1: Some functions return a string, others print >> fp
# Caveat2: global fp is used as a file pointer; 
#   From this file, you can safely use HSalPPContext; 
#   For using other functions, need to set fp

precedence = ['/', '*', '-', '+', '>', '>=', '<', '<=', '=', '/=', 'NOT', 'AND', 'and', 'OR', 'or', 'XOR', '=>', '<=>']

defDecls = []

in_module = False

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
        print(e)
        print((node.toxml()))
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
    print(kind + HSalPPDecls(i.childNodes, "", ""), file=fp)

def HSalPPNameExpr(node):
    global in_module
    if gen_sally:
        name = valueOf(node)
        if name in ['TRUE', 'FALSE']:
            return name.lower()
        elif in_module:
            return 'state.' + name
        else:
            return name
    else:
        return valueOf(node)

def HSalPPNumeral(node):
    global gen_sally
    v = valueOf(node)
    if gen_sally and (v[0] == '-'):
        return '(- %s)' % v[1:]
    else:
        return valueOf(node)

def getArg(node,index):
    j = 0
    for i in node.childNodes:
        if (i.nodeType == i.ELEMENT_NODE):
            j = j+1
            if j == index:
                return(i)
    return None

# def setAppArg(node,index,arg):
#     print('setAppArg: node = %s\n' % node.toxml())
#     tuples = getArg(node, 2)
#     print('setAppArg: tuples = %s\n' % tuples.toxml())
#     j = 0
#     for cnode in tuples.childNodes:
#         if (cnode.nodeType == cnode.ELEMENT_NODE):
#             j += 1
#             if j == index:
#                 tuples.replaceChild(arg, cnode)
#                 print('setAppArg: new tuples = %s\n' % tuples.toxml())
#     if j == 0:
#         print('Empty tuple?')
#         raise
#     print('setAppArg: after = %s\n' % node.toxml())
#     return None

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
        print(("EITHER Op not found %s" % op1))
        print(("OR Op not found %s" % op2))
        return True

def HSalPPInfixApp(node,outerSymb=None):
    str2 = getNameTag(node, 'NAMEEXPR')
    str1 = HSalPPExpr(appArg(node,1),outerSymb=str2)
    str3 = HSalPPExpr(appArg(node,2),outerSymb=str2)
    if higherPrec(outerSymb,str2) or node.getAttribute('PARENS')=='1':
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
    if gen_sally:
        op = getNameTag(node, 'NAMEEXPR')
        if op in ['AND', 'OR', 'NOT']:
            op = op.lower()
        # if op == 'eigenInv':
        #     print('App: defDecls for %s' % op)
        #     print(node.toxml())
        defn = next((d for d in defDecls if getNameTag(d, "IDENTIFIER") == op), None)
        if defn:
            enode = expandDefn(node, defn)
            # print('expandDefn: enode = %s\n' % enode.toxml())
            return HSalPPExpr(enode)
        else:
            str0 = "(" + op
            i = 1
            arg = appArg(node, i)
            while arg:
                expr = HSalPPExpr(arg)
                str0 += " " + expr
                i += 1
                arg = appArg(node,i)
            return str0 + ")"
    else:
        if node.getAttribute('INFIX') == 'YES':
            return HSalPPInfixApp(node,outerSymb)
        else:
            return HSalPPPrefixApp(node)

def expandDefn(app, defn):
    '''app is an App, with operator matching defn'''
    dvars = collectVars(defn)
    args = collectArgs(app)
    dbody = defn.childNodes[3]
    if len(dvars) == len(args):
        substitute(args, dvars, dbody)
        return dbody
    else:
        print((app.toxml()))
        print('Bad defn')
        raise

def collectArgs(app):
    i = 1
    args = []
    expr = appArg(app, i)
    if expr is None:
        print(('collectArgs: bad app %s' % app.toxml()))
    while expr:
        args.append(expr)
        i += 1
        expr = appArg(app, i)
    return args

def collectVars(defn):
    vardecls = defn.getElementsByTagName("VARDECLS")
    if not(vardecls == None) and len(vardecls) > 0:
        arg = vardecls[0]
        return [getName(vdecl) for vdecl in arg.childNodes]

def HSalPPNextOperator(node):
    global in_module
    name = getNameTag(node, "NAMEEXPR")
    if gen_sally:
        if in_module:
            return 'next.' + name
        else:
            print('not in module')
            raise
    else:
        return name+"'"

def HSalPPSetPredExpr(node):
    if gen_sally:
        print('SetPredExpr not possible, unless reducible')
        raise
    else:
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
    if gen_sally:
        str0 = "(ite"
        j = 0
        for i in node.childNodes:
            str0 += " " + HSalPPExpr(i)
        return str0 + ")"
    else:
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
       print([ [i:TYPE] Expr ])'''
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
        print((node.toxml()))
        print(('Node EXPR %s unknown. Missing code' % node.localName))
    return None

def HSalPPExprs(nodes):
    for node in nodes:
        if (node.nodeType == node.ELEMENT_NODE):
            return HSalPPExpr(node)

def HSalPPInvarDecl(invardecl):
    global fp
    print("INVARIANT", end=' ', file=fp)
    exprs = invardecl.childNodes
    print(HSalPPExprs(exprs), end=' ', file=fp)
    print("\n", end=' ', file=fp)

def HSalPPInitForDecl(initdecl):
    global fp
    print("INITFORMULA", end=' ', file=fp)
    print(HSalPPExprs(initdecl.childNodes), end=' ', file=fp)
    print("\n", end=' ', file=fp)

def HSalPPInitDecl(initdecl):
    global fp
    if gen_sally:
        print("  ;; Initial states", file=fp)
    else:
        print("INITIALIZATION", file=fp)
    firstChild = getArg(initdecl, 1)
    if firstChild.localName == "SIMPLEDEFINITION":
        HSalPPAssgns(initdecl)
    elif firstChild.localName == "SOMECOMMANDS":
        HSalPPSomecommands(initdecl)
    else:
        print(("ERROR: INITIALIZATION block found unexpected tag ",))
        print((firstChild.localName))
        raise
    if not gen_sally:
        print("\n", end=' ', file=fp)

def HSalPPDefDecl(defdecl):
    global fp
    print("DEFINITION", file=fp)
    firstChild = getArg(defdecl, 1)
    if not(firstChild.localName == "SIMPLEDEFINITION"):
        print(("ERROR: DEFINITION block found unexpected tag ",))
        print((firstChild.localName))
    else: 
        HSalPPAssgns(defdecl)
    print("\n", end=' ', file=fp)

def HSalPPGuard(guard):
    global fp, in_module
    # for n in guard.childNodes:
    #     print('guard child = %s' % n.toxml())
    #     print('-----')
    in_module = True
    #exprs = HSalPPExprs(guard.childNodes)
    # print('Guard: exprs = %s' % exprs)
    if gen_sally:
        print("   ", end=' ', file=fp)
    sguard = HSalPPExprs(guard.childNodes)
    in_module = False
    # for n in sguard.childNodes:
    #     print('sguard child = %s' % n.toxml())
    #     print('-----')
    print(sguard, end=' ', file=fp)

def HSalPPSimpleDefn(node):
    global fp
    if gen_sally:
        str0 = HSalPPExpr(getArg(node,1))
    else:
        str0 = '\t'+HSalPPExpr(getArg(node,1))
    rhsexpr = node.getElementsByTagName("RHSEXPRESSION")
    rhssel  = node.getElementsByTagName("RHSSELECTION")
    # print('SimpleDefn: node = %s\n' % node.toxml())
    # if rhsexpr:
    #     print('SimpleDefn: rhsexpr = %s\n' % rhsexpr[0].toxml())
    # if rhssel:
    #     print('SimpleDefn: rhssel = %s\n' % rhssel[0].toxml())
    if not(rhsexpr.length == 0):
        if gen_sally:
            rhs = HSalPPExprs(rhsexpr[0].childNodes)
            str0 = '   (= %s %s)\n' % (str0, rhs)
        else:
            str0 += " = "
            str0 += HSalPPExprs(rhsexpr[0].childNodes)
    elif not(rhssel.length == 0):
        if gen_sally:
            str0 = reduceSel(getArg(node,1), rhssel[0].childNodes)
            #print('SimpleDefn: str0 = %s' % str0)
        else:
            str0 += " IN "
            str0 += HSalPPExprs(rhssel[0].childNodes)
    print(str0, end=' ', file=fp)

def reduceSel(var0, node):
    for rhssel in node:
        if rhssel.nodeType == rhssel.ELEMENT_NODE:
            if rhssel.localName == "SETPREDEXPRESSION":
                bid = getNameTag(rhssel, "IDENTIFIER")
                typ = getNameTag(rhssel, "TYPENAME")
                pred = getArg(rhssel,3)
                #print('reduceSel: %s: %s -> %s: %s' % (bid, type(bid), var0, type(var0)))
                #print('reduceSel: pred = %s' % pred.toxml())
                spred = substit(var0, bid, pred)
                #print('reduceSel: spred = %s' % spred.toxml())
                return HSalPPExpr(spred)
            else:
                print(('expected setPredExpr, not %s' % rhssel.localName))
                raise

def substitute(args, svars, node):
    '''This is a sequential substitution.'''
    i = 0
    nnode = node
    while i < len(svars):
        substit(args[i], svars[i], nnode)
        i += 1

ctr = 0
        
def substit(x, y, node):
    global ctr
    # print('%s:  y gets x in node: y = %s' % (ctr, y))
    # print('x = %s\n' % x.toxml())
    # print('node = %s\n-----' % node.toxml())
    ctr += 1
    if node.localName == "NAMEEXPR":
        if y == valueOf(node):
            parent = node.parentNode
            if parent:
                #print('  Replacing in parent:\n  %s\n' % parent.toxml())
                xcopy = x.cloneNode(True)
                parent.replaceChild(xcopy, node)
                #print('  Replaced  in parent:\n  %s\n' % parent.toxml())
                node = x
            else:
                print(('No parent for %s?' % node.toxml()))
                raise
    elif node.localName == "APPLICATION":
        op = getNameTag(node, 'NAMEEXPR')
        i = 1
        arg = appArg(node, i)
        while not(arg == None):
            substit(x, y, arg)
            i += 1
            arg = appArg(node, i)
    elif node.localName == "NUMERAL":
        pass
    elif node.localName == "NEXTOPERATOR":
        arg = getArg(node, 1)
        substit(x, y, arg)
    elif node.localName == "SETPREDEXPRESSION":
        raise
    elif node.localName == "CONDITIONAL":
        for cnode in node.childNodes:
            if (cnode.nodeType == cnode.ELEMENT_NODE):
                substit(x, y, cnode)
    elif node.localName == "ARRAYLITERAL":
        lhs = getArg(node,1)
        rhs = getArg(node,2)
        lid = getArg(lhs, 1)
        if lid == y:
            print('need to name apart')
            raise
        else:
            substit(x, y, rhs)
    elif node.localName == "ARRAYSELECTION":
        lhs = getArg(node,1)
        rhs = getArg(node,2)
        substit(x, y, lhs)
        substit(x, y, rhs)
    else:
        print('Node unknown. Missing substit code')
        print((node.toxml()))
        raise
    ctr -= 1
    #print('%s: result node = %s\n-----' % (ctr, node.toxml()))
    return node


def HSalPPAssgns(assgns):
    global fp
    defs = assgns.getElementsByTagName("SIMPLEDEFINITION")
    flag = False
    if gen_sally:
        print("\n  (and", file=fp)
    for i in defs:
        if flag:
            if not gen_sally:
                print(";\n", end=' ', file=fp)
        HSalPPSimpleDefn(i)
        flag = True
    if gen_sally:
        print("  )", file=fp)
    else:
        print("\n", end=' ', file=fp)

def HSalPPLabeledCommand(node):
    global fp
    label = node.getElementsByTagName("LABEL")[0]
    print("{0}: ".format(valueOf(label)), file=fp)
    gc = node.getElementsByTagName("GUARDEDCOMMAND")[0]
    HSalPPGuardedCommand(gc)

def HSalPPGuardedCommand(node):
    global fp, in_module
    guard = node.getElementsByTagName("GUARD")[0]
    if gen_sally:
        print('  (and  ;; guardedcommand', file=fp)
    HSalPPGuard(guard)
    if not gen_sally:
        print(" --> ", file=fp)
    assgns = node.getElementsByTagName("ASSIGNMENTS")
    if (not(assgns == None) and len(assgns) > 0):
        in_module = True
        HSalPPAssgns(assgns[0])
        in_module = False
    if gen_sally:
        print('  )  ;; end guardedcommand', file=fp)
    
def HSalPPMultiCommand(node):
    global fp
    print("[", file=fp)
    gcmds = node.getElementsByTagName("GUARDEDCOMMAND")
    i = 0
    for j in gcmds:
        if not(i == 0):
            print(" || ", file=fp)
        HSalPPGuardedCommand(j)
        i = i + 1
    print("]", file=fp)

def HSalPPTransDecl(transdecl):
    global fp, in_module
    if gen_sally:
        print("  ;; Transition", file=fp)
    else:
        print("TRANSITION", file=fp)
    cmds = transdecl.getElementsByTagName("SOMECOMMANDS")
    if cmds != None and len(cmds) > 0:
        if gen_sally and len(cmds) > 1:
            print("  (or", file=fp)
        HSalPPSomecommands(cmds[0])
        if gen_sally and len(cmds) > 1:
            print("  ) ;; end transition", file=fp)
        return
    # transdecl is a list of simpledefinitions...
    in_module = True
    HSalPPAssgns(transdecl)
    in_module = False

def HSalPPSomecommands(cmds):
    global fp
    if not gen_sally:
        print("[", file=fp)
    j = 0
    if not(cmds == None):
        cmds = cmds.childNodes
    for i in cmds:
        j += 1
        if i.localName == "GUARDEDCOMMAND":
            if not(gen_sally or j == 1):
                print("[]", file=fp)
            HSalPPGuardedCommand(i)
        elif i.localName == "MULTICOMMAND":
            if not(gen_sally or j == 1):
                print("[]", file=fp)
            HSalPPMultiCommand(i)
        elif i.localName == "LABELEDCOMMAND":
            if not(gen_sally or j == 1):
                print("[]", file=fp)
            HSalPPLabeledCommand(i)
        else:
            j -= 1
    if not gen_sally:
        print("]", file=fp)

def HSalPPSomecommandsSally(cmds):
    global fp
    if gen_sally:
        print("(", file=fp)
    else:
        print("[", file=fp)
    j = 0
    if not(cmds == None):
        print((cmds.toxml()))
        cmds = cmds.childNodes
    for i in cmds:
        j += 1
        if i.localName == "GUARDEDCOMMAND":
            if not(gen_sally or j == 1):
                print("[]", file=fp)
            HSalPPGuardedCommand(i)
        elif i.localName == "MULTICOMMAND":
            if not(gen_sally or j == 1):
                print("[]", file=fp)
            HSalPPMultiCommand(i)
        elif i.localName == "LABELEDCOMMAND":
            if not(gen_sally or j == 1):
                print("[]", file=fp)
            HSalPPLabeledCommand(i)
        else:
            j -= 1
    if gen_sally:
        print(")", file=fp)
    else:
        print("]", file=fp)

def HSalPPBaseModule(basemod):
    if not gen_sally:
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
        if gen_sally:
            print('no invardecls yet')
            raise
        else:
            HSalPPInvarDecl(invardecl[0])
    defdecl = basemod.getElementsByTagName("DEFDECL")
    if not(defdecl == None) and len(defdecl) > 0:
        if gen_sally:
            # Add defdecl to the defDecls list
            print('Adding defdecl')
            defDecls.append(defdecl[0])
        else:
            HSalPPDefDecl(defdecl[0])
    initdecl = basemod.getElementsByTagName("INITFORDECL")
    if not(initdecl == None) and len(initdecl) > 0:
        if gen_sally:
            print('no initfordecls yet')
            raise
        else:
            HSalPPInitForDecl(initdecl[0])
    initdecl = basemod.getElementsByTagName("INITDECL")
    if not(initdecl == None) and len(initdecl) > 0:
        HSalPPInitDecl(initdecl[0])
    transdecl = basemod.getElementsByTagName("TRANSDECL")
    if not(transdecl == None) and len(transdecl) > 0:
        HSalPPTransDecl(transdecl[0])

def HSalPPComposition(node, op, opTop):
    if not(op == opTop):
        print('(', end=' ', file=fp) 
    HSalPPMod(node.childNodes, op)
    if not(op == opTop):
        print(')', end=' ', file=fp) 

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
            if not gen_sally:
                print(op, end=' ', file=fp)
        if node.localName == 'BASEMODULE':
            if gen_sally:
                HSalPPBaseModule(node)
            else:
                print("BEGIN", file=fp) 
                HSalPPBaseModule(node)
                print("END", end=' ', file=fp)
        elif node.localName == 'ASYNCHRONOUSCOMPOSITION':
            HSalPPComposition(node, '[]', op)
        elif node.localName == 'SYNCHRONOUSCOMPOSITION':
            HSalPPComposition(node, '||', op)
        elif node.localName == 'MODULEINSTANCE':
            modName = getNameTag(node, "MODULENAME")
            # ignoring MODULEACTUALS
            print(modName, end=' ', file=fp)
        elif node.localName == 'RENAMING':
            renames = getArg(node, 1)
            renamings = renames.getElementsByTagName("RENAME")
            print("(RENAME ", end=' ', file=fp)
            comma = ''
            for i in renamings:
              lhs = valueOf(getArg(i, 1))       # Assuming nameexpr
              rhs = valueOf(getArg(i, 2))
              print("{0} {1} TO {2}".format(comma, lhs, rhs), end=' ', file=fp)
              comma = ','
            print(" IN ", end=' ', file=fp)
            HSalPPMod([getArg(node, 2)], op='')
            print(" )", end=' ', file=fp)
        else:
            print("Unrecognized module type. Fill in code later")
    if op == None:
        if not gen_sally:
            print(";\n", file=fp)

def HSalPPModDecl(node):
    global fp
    if gen_sally:
        name = getName(node)
        stype = getModDeclType(node.childNodes)
        print("\n(define-transition-system %s %s" % (name, stype), file=fp)
    else:
        print("\n%s: MODULE =" % getName(node), file=fp)
    childNodes = node.childNodes
    HSalPPMod(childNodes)
    if gen_sally:
        print(")", file=fp)

def getModDeclType(nodeL):
    for node in nodeL:
        if not(node.nodeType == node.ELEMENT_NODE):
            continue
        if node.localName == 'IDENTIFIER' or node.localName == 'VARDECLS':
            continue
        if node.localName == 'BASEMODULE':
            return getBaseModuleType(node, getName(node))
        elif node.localName == 'ASYNCHRONOUSCOMPOSITION':
            print('No module composition yet')
            raise
        elif node.localName == 'SYNCHRONOUSCOMPOSITION':
            print('No module composition yet')
            raise
        elif node.localName == 'MODULEINSTANCE':
            modName = getNameTag(node, "MODULENAME")
            print('No module instances yet')
            raise
        elif node.localName == 'RENAMING':
            renames = getArg(node, 1)
            renamings = renames.getElementsByTagName("RENAME")
            print('No renamings yet')
            raise
        else:
            print("Unrecognized module type. Fill in code later")
            raise

def getBaseModuleType(basemod, name):
    global fp
    tname = name + '_state_type'
    print('\n(define-state-type %s\n  (;; State variables' % tname, file=fp)
    ldecls = basemod.getElementsByTagName("LOCALDECL")
    for i in ldecls:
        sallyVarDecls(i) 
    ldecls = basemod.getElementsByTagName("GLOBALDECL")
    for i in ldecls:
        sallyVarDecls(i) 
    ldecls = basemod.getElementsByTagName("OUTPUTDECL")
    for i in ldecls:
        sallyVarDecls(i)
    print('  )\n  (;; Input variables', file=fp)
    ldecls = basemod.getElementsByTagName("INPUTDECL")
    for i in ldecls:
        sallyVarDecls(i)
    print('  ))\n', file=fp)
    return tname

def sallyVarDecls(i):
    global fp
    for j in i.childNodes:
        if (j.localName == "VARDECL"):
            vid = getName(j)
            vtype = HSalPPType(getArg(j,2),"","")
            print('   (%s %s)' % (vid, vtype), file=fp)

def HSalPPModuleInstance(node):
    return getNameTag(node, "MODULENAME")
    
def HSalPPModuleModels(node):
    global fp
    str1 = HSalPPModuleInstance(node.getElementsByTagName("MODULEINSTANCE")[0])
    if gen_sally:
        expr = getArg(node,2)
        if expr.localName == "APPLICATION":
            op = getNameTag(expr, 'NAMEEXPR')
            if op == 'G':
                str2 = HSalPPExpr(appArg(expr, 1))
            else:
                print('Formulas should start with "G"')
                raise
    else:
        str2 = HSalPPExpr(getArg(node,2))
    if gen_sally:
        print('(query %s %s)' % (str1, str2), file=fp)
    else:
        print(str1+" |- "+str2+";", file=fp)

def HSalPPAssertionDecl(node):
    global fp
    if not gen_sally:
        print(getNameTag(node,"IDENTIFIER"), end=' ', file=fp)
        print(":", end=' ', file=fp)
        print(getNameTag(node,"ASSERTIONFORM"), file=fp)
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
        if gen_sally and str0 == 'REAL':
            str0 = 'Real'
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
        print((node.toxml()))
        print(('Node TYPE %s not handled. Missing code' % node.localName))
        raise
    if not(str0 == None):
        return str1+str0+str2

def HSalPPCnstDecl(node):
    global fp
    if gen_sally:
        defDecls.append(node)
    else:
        print(getNameTag(node, "IDENTIFIER"), end=' ', file=fp)
        vardecls = node.getElementsByTagName("VARDECLS")
        if not(vardecls == None) and len(vardecls) > 0:
            arg = vardecls[0]
            print(HSalPPDecls(arg.childNodes,"(",")"), end=' ', file=fp)
        arg = getArg(node,3)
        print(HSalPPType(arg,": ",""), end=' ', file=fp)
        arg = getArg(node,4)
        value = HSalPPExpr(arg)
        if not(value == None) and not(value == ""):
            print(" = \n %s" % value, end=' ', file=fp)
        print(";\n", file=fp)

def HSalPPTypeDecl(node):
    global fp
    print("\n%s: TYPE =" % getName(node), end=' ', file=fp)
    print(HSalPPType(getArg(node,2), "", ""), end=' ', file=fp)
    print(";\n", file=fp)

def HSalPPVerbatim(node):
    global fp
    print(valueOf(node), file=fp)

def HSalPPNode(node):
    if node.localName == "MODULEDECLARATION":
        HSalPPModDecl(node)
    elif node.localName == "TYPEDECLARATION":
        HSalPPTypeDecl(node)
    elif node.localName == "ASSERTIONDECLARATION":
        HSalPPAssertionDecl(node)
    elif node.localName == "CONSTANTDECLARATION":
        # print('Hit CnstDecl')
        HSalPPCnstDecl(node)
    elif node.localName == "VERBATIM":
        print('Hit Verbatim')
        HSalPPVerbatim(node)
    elif node.nodeType == node.ELEMENT_NODE:
        print(("Missing code for Node %s" % node.localName))

def HSalPPContextBody(ctxtbody):
    for i in ctxtbody.childNodes:
        HSalPPNode(i)

def HSalPPContext(ctxt, filepointer=sys.stdout, generate_sally=False):
    global fp, gen_sally
    fp = filepointer
    gen_sally = generate_sally
    if gen_sally:
        print(";; HybridSal context %s" % getName(ctxt), file=fp)
        HSalPPContextBody(ctxt.getElementsByTagName("CONTEXTBODY")[0])
    else:
        print("%s: CONTEXT = " % getName(ctxt), file=fp)
        print("BEGIN", file=fp) 
        HSalPPContextBody(ctxt.getElementsByTagName("CONTEXTBODY")[0])
        print("END", file=fp)

if __name__ == "__main__":
    dom = xml.dom.minidom.parse(sys.argv[1])
    HSalPPContext(dom)
