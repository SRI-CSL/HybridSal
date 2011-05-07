# Generate relational abstraction of hybrid systems with
# linear dynamics in each mode

# Input:  Hybrid Sal model in XML syntax
# Output: Hybrid Sal model in XML syntax
# Output will have relational abstractions 
# of all continuous modes

# Caveat: FLOW should define ALL continuous variables.

# Algorithm for constructing relational abstraction:
# Partition variables into x;y s.t.
# d/dt (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# Then, d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p
# If we fail to find eigenvector with real eigenvalues, 
# we need BOX invs and other things -- for later...

# We use eigenvalue and eigenvector computation from linearAlgebra.py
# linearAlgebra.py uses an iteration method for computing eigenvectors

# For imaginary eigenvalues:
# Suppose u' A1 = a u' + b v' and v' A1 = -b u' + a v'
# We find unknowns w1 and w2 and constant c1 and c2 s.t.
# if p1 = (u' x + w1' y + c1) and p2 = ( v' x + w2' y + c2) then
# d/dt p1 = a p1 + b p2 and d/dt p2 = -b p1 + a p2...
# for this to happen, the unknowns should satisfy the following:
# u' b1 + w1' b2 = a c1 + b c2  (Matching CONST COEFF)
# v' b1 + w2' b2 = -b c1 + a c2  (Matching CONST COEFF)
# u' A2 = a w1' + b w2'  (Matching y coeff)
# v' A2 = -b w1' + a w2'  (Matching y coeff)
# Solving this we get w1,w2, then we get c1,c2 and hence p1,p2
# If p1,p2 have the above relation, then we get the following relational abstraction:
# 3 cases: a >0, a = 0, a < 0
# if a > 0:
# p1 >= 0 and p2 >= 0 => p1' >= p1 and p2' >= 0 AND
# p1 <= 0 and p2 <= 0 => p1' <= p1 and p2' <= 0 AND
# p1 >= 0 and p2 <= 0 => p2' <= p2 and p1' >= 0 AND
# p1 <= 0 and p2 >= 0 => p2' >= p2 and p1' >= 0 


import xml.dom.minidom
import sys	# for sys.argv[0]
import linearAlgebra
import HSalExtractRelAbs
import polyrep # internal representation for expressions
import HSalXMLPP
import os.path
import shutil
#import polyrep2XML

equal = linearAlgebra.equal
isZero = linearAlgebra.isZero
exprs2poly = polyrep.exprs2poly
simpleDefinitionLhsVar = HSalExtractRelAbs.SimpleDefinitionLhsVar
isCont = HSalExtractRelAbs.isCont
#createNodeAnd = polyrep2XML.createNodeAnd
#createNodeInfixApp = polyrep2XML.createNodeInfixApp
#createNodeTagChild = polyrep2XML.createNodeTagChild
#createNodeTagChild2 = polyrep2XML.createNodeTagChild2
#createNodeTime = polyrep2XML.createNodeTime
#createNodePnew = polyrep2XML.createNodePnew
#createNodePold = polyrep2XML.createNodePold
#dictKey = polyrep2XML.dictKey

# ********************************************************************
# Functions for creating XML node for expressions
# ********************************************************************
def createNodeTagChild(tag, childNode):
    global dom
    node = dom.createElement(tag)
    node.appendChild(childNode)
    return node

def createNodeTagChild2(tag, childNode, childNode2):
    node = createNodeTagChild(tag, childNode)
    node.appendChild(childNode2)
    return node

def createNodeTagChild3(tag, childNode, childNode2, childNode3):
    node = createNodeTagChild2(tag, childNode, childNode2)
    node.appendChild(childNode3)
    return node

def createNodeTag(tag, val):
    global dom
    valNode = dom.createTextNode(val)
    return createNodeTagChild(tag, valNode)

def createNodeInfixApp(op, child1, child2):
    tupleNode = createNodeTagChild2("TUPLELITERAL", child1, child2)
    opNode = createNodeTag("NAMEEXPR", op)
    appNode = createNodeTagChild2("APPLICATION", opNode, tupleNode)
    appNode.setAttribute('INFIX', 'YES')
    return appNode

def createNodeTime(varName, rate):
    "Return varName' - varName / rate"
    rateNode = createNodeTag("NUMERAL", str(rate))
    varNode = createNodeTag("NAMEEXPR", varName)
    varPrimeNode = createNodeTagChild("NEXTOPERATOR", varNode.cloneNode(True))
    differenceNode = createNodeInfixApp('-', varPrimeNode, varNode)
    if equal(rate, 1):
        quotientNode = differenceNode
    else:
        quotientNode = createNodeInfixApp('/', differenceNode, rateNode)
    return quotientNode

def createNodeInfixAppRec(op, nodeList):
    n = len(nodeList)
    if n == 0:
        return None
    node = nodeList[0]
    for i in range(n-1):
        node = createNodeInfixApp(op, node, nodeList[i+1])
    return node

def createNodeAnd(nodeList):
    ans = createNodeInfixAppRec('AND', nodeList)
    if ans == None:
        return createNodeTag("NAMEEXPR", "TRUE")
    return ans

def createNodePlus(nodeList):
    ans = createNodeInfixAppRec('+', nodeList)
    #if ans == None:
        #return createNodeTag("NUMERAL", "0")
    return ans

def createNodeCXOne(c, x, flag):
    node1 = createNodeTag("NUMERAL", str(c))
    node2 = createNodeTag("NAMEEXPR", x)
    if flag:
        node2 = createNodeTagChild("NEXTOPERATOR", node2)
    node3 = createNodeInfixApp('*', node1, node2)
    return node3

def dictKey(varlist, value):
    "Return key given the value"
    for var,index in varlist.iteritems():
        if index == value:
            return var
    return None

def createNodeCX(c,x,flag):
    "create node for c1 x1+...+cn xn, use primes if flag"
    xindices = x.values()
    xindices.sort()
    n = len(xindices)
    cx = list()
    for i,v in enumerate(xindices):
        if not(equal(c[i], 0)):
            cx.append(createNodeCXOne(c[i], dictKey(x,v), flag))
    return createNodePlus(cx)

def createNodePaux(c,x,d,y,e,flag):
    "create node for c.x + d.y + e; with PRIME variables if flag"
    print "createNodePaux entering"
    node1 = createNodeCX(c,x,flag)
    node2 = createNodeCX(d,y,flag)
    if equal(e,0):
        node3 = None
    else:
        node3 = createNodeTag("NUMERAL", str(e))
    nodeL = [ node1, node2, node3 ]
    while None in nodeL:
        nodeL.remove(None)
    return createNodePlus(nodeL)

def createNodePnew(vec,x,A2transvec,y,const):
    return createNodePaux(vec,x,A2transvec,y,const,True)

def createNodePold(vec,x,A2transvec,y,const):
    return createNodePaux(vec,x,A2transvec,y,const,False)

def createEigenInv(nodePnew,nodePold,lamb):
    "0 <= nodePnew <= nodePold OR nodePold <= nodePnew <= 0 if lamb < 0"
    "0 <= nodePold <= nodePnew OR nodePnew <= nodePold <= 0 if lamb > 0"
    "nodePold = nodePnew if lamb == 0"
    if lamb == 0:
        return createNodeInfixApp('=', nodePold, nodePnew)
    if lamb < 0:
        tmp = nodePold
        nodePold = nodePnew
        nodePnew = tmp
    node1 = createNodeInfixApp('<=', createNodeTag('NUMERAL', '0'), nodePold)
    node2 = createNodeInfixApp('<=', nodePold.cloneNode(True), nodePnew)
    node = createNodeInfixApp('AND', node1, node2)
    node1 = createNodeInfixApp('<=', nodePnew.cloneNode(True), nodePold.cloneNode(True))
    node2 = createNodeInfixApp('<=', nodePold.cloneNode(True), createNodeTag('NUMERAL', '0'))
    node0 = createNodeInfixApp('AND', node1, node2)
    node = createNodeInfixApp('OR', node, node0)
    return node
# ********************************************************************

def simpleDefinitionRhsExpr(defn):
    "Return the RHS expression in definition def"
    rhs = defn.getElementsByTagName("RHSEXPRESSION")
    if rhs == None:
        return None
    else:
        return exprs2poly(rhs[0].childNodes)
    
def getFlow(defs):
    "Return flow of the continuous dynamics stored in definitions"
    flow = list()
    for i in defs:
        lhsvar = simpleDefinitionLhsVar(i)
        rhsexpr = simpleDefinitionRhsExpr(i)
        flow.append(lhsvar)
        flow.append(rhsexpr)
    print "printing flow"
    print flow
    return flow

def flow2var(flow):
    "extract variables from the flow"
    i = 0
    varlist = dict()
    while i < len(flow):
        varnamedot = flow[i]
        varlist[varnamedot[0:-3]] = i/2
        i += 2
    return varlist

def flow2Aibi(flowi, varlist):
    "flowi is an expression polynomial"
    n = len(varlist)
    Ai = [ 0 for i in range(n) ]
    bi = 0
    for [c,pp] in flowi:
        degree = sum(pp.values())
        if degree > 1:
            print "ERROR: Nonlinear dynamics found; can't handle"
            return None
        elif degree == 1:
            var = pp.keys()[0]
            index = varlist[var]
            Ai[index] = c
        else:
            bi = c
    return [Ai,bi]

def flow2Ab(flow):
    "get A,b matrices from the flow, if possible"
    "flow is a list of alternative variabledot, poly"
    varlist = flow2var(flow)
    n = len(varlist)
    i = 0
    A = list()
    b = list()
    while i < n:
        Aibi = flow2Aibi(flow[2*i+1], varlist)
        if Aibi == None:
            return None
        A.append(Aibi[0])
        b.append(Aibi[1])
        i += 1
    return [varlist,A,b]

def partitionAux(x, y, A, b):
    "Rearrange A,b s.t. (x;y) = (A1,A2;0,0)(x;y) + (b1;b2); DESTRUCTIVE"
    xindices = x.values()
    yindices = y.values()
    xindices.sort()
    xindices.reverse()
    yindices.sort()
    yindices.reverse()
    n = len(x)
    m = len(y)
    A2 = [ [0 for i in range(m) ] for j in range(n) ]
    b2 = [ 0 for i in range(m) ] 
    ib2 = m-1
    for i in yindices:
        del A[i]
        b2[ib2] = b[i]
        del b[i]
        ib2 -= 1
    iA2 = m-1
    for i in yindices:
        for j in range(len(A)):
            A2[j][iA2] = A[j][i]
            del A[j][i]
        iA2 -= 1
    print "A1 below should be nxn where n is %d" % n
    print A
    print "A2 below should be nxm where m is %d" % m
    print A2
    print "b1 below should be nx1 where n is %d" % n
    print b
    print "b2 below should be mx1 where m is %d" % m
    print b2
    return [A, A2, b, b2]

def partition(varlist, A, b):
    "output [x,y,A1,A2,b1,b2] s.t. (x;y) = (A1 A2; 0 0) (x;y) + (b1;b2)"
    x = dict()
    y = dict()
    index = 0
    for i in A:
        if isZero(i):
            var = dictKey(varlist, index)
            y[var] = index
        else:
            var = dictKey(varlist, index)
            x[var] = index
        index += 1
    [A1,A2,b1,b2] = partitionAux(x, y, A, b)
    return [x,y,A1,A2,b1,b2]

def multirateAbs(y, b2):
    "Return y[i]'-y[i]/b1[i] are equal for all i"
    "Return an XML SAL expression -- guard"
    m = len(b2)
    node0 = None
    nodes = list()
    yindices = y.values()
    yindices.sort()
    for i,v in enumerate(yindices):
        if equal(b2[i], 0):
            varName = dictKey(y, v)
            varNode = createNodeTag("NAMEEXPR", varName)
            varPrimeNode = createNodeTagChild("NEXTOPERATOR", varNode.cloneNode(True))
            nodes.append(createNodeInfixApp('=', varNode, varPrimeNode))
        elif node0 == None:
            node0 = createNodeTime(dictKey(y,v), b2[i])
        else:
            nodei = createNodeTime(dictKey(y,v), b2[i])
            tmp = node0.cloneNode(True)
            nodes.append(createNodeInfixApp('=', node0, nodei))
            node0 = tmp
    return createNodeAnd(nodes)

def absGuardedCommandAux(varlist,A,b):
    """varlist is a dict from var to indices
    A,b are the A,b matrix defined wrt these indices
    Return an abstract GC"""
    [x,y,A1,A2,b1,b2] = partition(varlist,A,b)
    n = len(x)
    m = len(y)
    if n == 0:
        print "dx/dt is a constant for all x"
    guardAbs1 = multirateAbs(y, b2)
    A1trans = linearAlgebra.transpose(A1)
    eigen = linearAlgebra.eigen(A1trans)
    # CHECK above, tranpose added, [ l [ vectors ] l [ vectors ] ]
    print "The LEFT eigenvectors computed are:"
    print eigen
    n = len(eigen)
    i = 0
    A2trans = linearAlgebra.transpose(A2)
    nodeL = list()
    if not(guardAbs1 == None):
        nodeL.append(guardAbs1)
    while i < n:
        lamb = eigen[i]
        vectors = eigen[i+1]
        if vectors == None or len(vectors) == 0:
            continue
        if len(lamb) > 1:
            continue
        for vec in vectors:
            A2transvec = linearAlgebra.multiplyAv(A2trans, vec)
            for j in range(len(vec)):
                vec[j] *= lamb
            const = linearAlgebra.dotproduct(vec,b1)
            const += linearAlgebra.dotproduct(A2transvec,b2)
            nodePnew = createNodePnew(vec,x,A2transvec,y,const)
            nodePold = createNodePold(vec,x,A2transvec,y,const)
            # vec could be 0 vector and hence nodePnew could be None
            if not(nodePnew == None):
                nodeL.append(createEigenInv(nodePnew,nodePold,lamb))
            # Pick d' s.t. l d' = c' A2 or, d l = A2' c
            # Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p
        i += 2
    i = 0
    while i < n:
        lamb = eigen[i]
        vectors = eigen[i+1]
        if vectors == None or len(vectors) == 0:
            continue
        if not(len(lamb) == 2):
            continue
        # add something to nodeL
        i += 2
    return createNodeAnd(nodeL)

# collect all x s.t. dx/dt = constant
# replace them by their rel abs.
# all other x's: d (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c'A=l c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p

# If we fail to find eigen, we need BOX invs -- for later...

def makePrime(expr):
    """Replace var by var' in expr"""
    ans = expr.cloneNode(True)
    # get all NAMEEXPR nodes; if its parent is TUPLELITERAL then add prime to it
    nameexprs = ans.getElementsByTagName("NAMEEXPR")
    for i in nameexprs:
        parentNode = i.parentNode
        if parentNode.localName == 'TUPLELITERAL':
            icopy = i.cloneNode(True)
            primeVar = createNodeTagChild("NEXTOPERATOR", icopy)
            parentNode.replaceChild(oldChild=i, newChild=primeVar)
    return ans

def absAssignments(varlist):
    """For each variable in varlist, create RHSSELECTION"""
    global dom
    ans = dom.createElement("ASSIGNMENTS")
    for var,index in varlist.iteritems():
        nameexpr = createNodeTag("NAMEEXPR",var)
        nextop = createNodeTagChild("NEXTOPERATOR",nameexpr)
        ident = createNodeTag("IDENTIFIER","aZtQ")
        typename = createNodeTag("TYPENAME","REAL")
        expr = createNodeTag("NAMEEXPR","TRUE")
        setpred = createNodeTagChild3("SETPREDEXPRESSION",ident,typename,expr)
        rhssel = createNodeTagChild("RHSSELECTION",setpred)
        simpledef = createNodeTagChild2("SIMPLEDEFINITION",nextop,rhssel)
        ans.appendChild(simpledef)
    return ans

def absGuardedCommand(gc):
    "Return a new guarded command that is a rel abs of input GC"
    guard = gc.getElementsByTagName("GUARD")[0]
    assigns = gc.getElementsByTagName("ASSIGNMENTS")[0]
    defs = assigns.getElementsByTagName("SIMPLEDEFINITION")
    flow = getFlow(defs)
    [varlist,A,b] = flow2Ab(flow)
    print "A"
    print A
    print "b"
    print b
    guardExpr = HSalXMLPP.getArg(guard,1)
    guard = guardExpr.cloneNode(True)
    primeguard = makePrime(guard)
    guard = createNodeInfixApp('AND',guard,primeguard)
    absgc = absGuardedCommandAux(varlist,A,b)
    absguardnode = createNodeInfixApp('AND',guard,absgc)
    absguard = createNodeTagChild('GUARD',absguardnode)
    # absassigns = assigns.cloneNode(True)
    absassigns = absAssignments(varlist)
    return createNodeTagChild2('GUARDEDCOMMAND', absguard, absassigns)

def handleContext(ctxt):
    cbody = ctxt.getElementsByTagName("GUARDEDCOMMAND")
    for i in cbody:
        if isCont(i):
            absGC = absGuardedCommand(i)
            parentNode = i.parentNode
            if parentNode.localName == 'MULTICOMMAND':
                if not(absGC == None):
                    parentNode.appendChild(absGC)
                print "Parent is a multicommand"
            elif parentNode.localName == 'SOMECOMMANDS':
                print "Parent is SOMECOMMANDS"
                newnode = ctxt.createElement("MULTICOMMAND")
                oldChild = i.cloneNode(True)
                newnode.appendChild(oldChild)
                newnode.appendChild(absGC)
                parentNode.replaceChild(newChild=newnode, oldChild=i)
            else:
                print "Unknown parent node type"
    return ctxt

#def changeContextName(ctxt):
    #idnode = ctxt.getElementsByTagName("IDENTIFIER")[0]
    #for i in idnode.childNodes:
        #if i.nodeType == i.TEXT_NODE:
            #newnode = ctxt.createTextNode(i.data+"ABS")
            #idnode.replaceChild(newnode, i)
    #return ctxt

def main():
    global dom
    filename = sys.argv[1]
    dom = xml.dom.minidom.parse(filename)
    newctxt = handleContext(dom)
    basename,ext = os.path.splitext(filename)
    absfilename = basename + ".haxml"
    if os.path.isfile(absfilename):
        print "Abstract XML file exists. Renaming old file and recreating new file."
        shutil.move(absfilename, absfilename + "~")
    absfile = open(absfilename, "w")
    print >> absfile, newctxt.toxml()
    print "Created file %s containing the original+abstract model (XML)" % absfilename
    absfilename = basename + ".hasal"
    if os.path.isfile(absfilename):
        print "Abstract HSAL file exists. Renaming old file and recreating new file."
        shutil.move(absfilename, absfilename + "~")
    absfile = open(absfilename, "w")
    #newctxt = changeContextName(newctxt)
    HSalXMLPP.HSalPPContext(newctxt, absfile)
    print "Created file %s containing the original+abstract model" % absfilename


if __name__ == '__main__':
    main()

