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

# Aug 26, 2011: Adding support for INVARIANT and INITFORMULA
# INITFORMULA \phi will be replaced by INITIALIZATION [ \phi --> ]
# INVARIANT \phi will be deleted and each guarded command with
# get \phi AND \phi' in its guard.
# Aug 29, 2011: Flow need not define all variables. Undefined variables are
# treated as unchanging...

import xml.dom.minidom
import sys	# for sys.argv[0]
import math
import linearAlgebra
import HSalExtractRelAbs
import polyrep # internal representation for expressions
import HSalXMLPP
import os.path
import inspect
import shutil
import subprocess
import HSalPreProcess
import HSalPreProcess2
from xmlHelpers import *
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


# def mystr(k):
    # """return floating value k as a string; str(k) uses e notation
       # use 8 decimal places"""
    # return '{0:.8f}'.format(k)
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
    # print "printing flow"
    # print flow
    return flow

def flow2var(flow):
    "extract variables from the flow: LHS and RHS"
    i = 0
    varlist = dict()
    # get variables from LHS
    while i < len(flow):
        varnamedot = flow[i]
        varlist[varnamedot[0:-3]] = i/2
        i += 2
    # now get variables from RHS too
    i = 1
    j = len(varlist)
    while i < len(flow):
        rhsExpr = flow[i]
        for [c,pp] in rhsExpr:
            for var in pp.keys():
                if not(var in varlist): 
                    varlist[var] = j
                    j += 1
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
        if 2*i+1 < len(flow): 
            Aibi = flow2Aibi(flow[2*i+1], varlist)
        else:
            Aibi = [ [ 0 for j in range(n) ], 0 ]
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
    # print "A1 below should be nxn where n is %d" % n
    # print A
    # print "A2 below should be nxm where m is %d" % m
    # print A2
    # print "b1 below should be nx1 where n is %d" % n
    # print b
    # print "b2 below should be mx1 where m is %d" % m
    # print b2
    return [A, A2, b, b2]



def ifGoodCreateNodes(soln, vectors, lamb, m, l):
    """soln is (m+l+1) vector, vectors has l (nx1) vectors, lamb is a scalar"""
    assert l == len(vectors)
    nzCount = 0
    for i in range(l):
        if not(equal(soln[m+i],0)):
            nzCount += 1
            if nzCount > 1:
                break
    if nzCount <= 1:
        return (None, None)
    wec = [0 for i in range(m)]
    for i in range(m):
        wec[i] = soln[i]
    n = len(vectors[0])
    vec = [0 for i in range(n)]
    for i in range(n):
        for j in range(l):
            vec[i] += soln[m+j]*vectors[j][i]
    return (vec,wec)

def absGuardedCommandAux(varlist,A,b,inputs):
    """varlist is a dict from var to indices
    A,b are the A,b matrix defined wrt these indices
    inputs is a list of string names of all input variables
    Return an abstract GC"""

    def multirateList(y, b2, inputs):
        """Return list of [y[i]',y[i],b1[i]],
           where y,y' are XML nodes, b1[i] is a float"""
        multirateL = list()
        yindices = y.values()
        yindices.sort()
        for i,v in enumerate(yindices):
            varName = dictKey(y, v)
            if varName in inputs:
                continue
            yold = createNodeTag("NAMEEXPR", varName)
            ynew = createNodeTagChild("NEXTOPERATOR", yold.cloneNode(True))
            multirateL.append([ynew, yold, b2[i]])
        return multirateL

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

    [x,y,A1,A2,b1,b2] = partition(varlist,A,b)
    # [x,y,A1,A2,b1,b2] s.t. (x;y) = (A1 A2; 0 0) (x;y) + (b1;b2)"
    n = len(x)
    m = len(y)
    if n == 0:
        print "dx/dt is a constant for all x"
    multirateL = multirateList(y, b2, inputs) 
    # guardAbs1 = multirateAbs(y, b2)
    A1trans = linearAlgebra.transpose(A1)
    eigen = linearAlgebra.eigen(A1trans)
    # CHECK above, tranpose added, [ l [ vectors ] l [ vectors ] ]
    # print "The LEFT eigenvectors computed are:"
    # print eigen
    num = len(eigen)
    i = 0
    A2trans = linearAlgebra.transpose(A2)
    nodeL = list()
    #if not(guardAbs1 == None):
        #nodeL.append(guardAbs1)
    while i < num:
        vectors = eigen[i+1]
        lambL = eigen[i]
        i += 2
        if vectors == None or len(vectors) == 0:
            continue
        if len(lambL) > 1:
            continue
        lamb = lambL[0]
        # Suppose d/dt(vec.x+wec.y+b)= 0
        # vec.(A1 x + A2 y + b1) + wec.(b2) = 0
        # vec.A1 = lamb.vec; Suppose d/dt(vec.x+wec.y+b)=lamb(...)
        # Then, vec.(A1 x + A2 y + b1) + wec.(b2) = lamb(...)
        # lamb.vec.x + vec.A2.y+vec.b1 + wec.b2 = lamb(vec.x+wec.y+b)
        # vec.A2.y = lamb.wec.y AND vec.b1 + wec.b2 = lamb(b)
        for vec in vectors:
            if isZero(vec):
                continue
            wec = linearAlgebra.multiplyAv(A2trans, vec)
            const = linearAlgebra.dotproduct(vec,b1)
            if equal(lamb, 0):
                if isZero(wec):
                    pold = createNodeCX(vec,x,False,None)
                    pnew = createNodeCX(vec,x,True,inputs)
                    multirateL.append([pnew,pold,const])
                else:
                    print "lamb==0, but no corr. invariant found"
                    continue
            else:
                for j in range(len(wec)):
                    wec[j] /= lamb
                const += linearAlgebra.dotproduct(wec,b2)
                const = float(const) / lamb
                nodePnew = createNodePnew(vec,x,wec,y,const,inputs)
                nodePold = createNodePold(vec,x,wec,y,const)
                if not(nodePnew == None):
                    nodeL.append(createCallToEigenInv(nodePnew,nodePold,lamb))
            # Pick d' s.t. l d' = c' A2 or, d l = A2' c
            # Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p
        if len(vectors) > 1:
            if equal(lamb, 0):	# multirate above gets all the relations...
                continue
            # Test if vec0'x + c1* vec1'x + ci*veci'x + w'y+c is an eigenInv
            # (vec0'+ci*veci')(A1x+A2y+b1) + w'b2 = lamb*((ci*veci')x+w'y+c)
            # iff (vec0'+ci*veci')(A2y+b1) + w'b2 = lamb*(w'y+c)
            # iff (vec0'+ci*veci')A2=lamb*w' and (vec0'+ci*veci')*b1+w'b2=lamb*c
            # iff lamb*w=(A2'vec0+ci*A2'*veci) &&(vec0'+ci*veci')*b1+w'b2=lamb*c
            l = len(vectors)
            # m+l+1 variables, |w|=m, |veci|=l, const c 
            row = [ 0 for j in range(m+l+1) ]
            for j in range(m):
                row[j] = b2[j]
            for j in range(l):
                row[m+j] = linearAlgebra.dotproduct(vectors[j],b1)
            row[m+l] = -lamb
            AA = []
            bb = []
            AA.append(row)
            bb.append( 0 )
            for j in range(m):
                row = [ 0 for k in range(m+l+1) ]
                row[j] = lamb
                for k in range(l):
                    row[m+k] = linearAlgebra.dotproduct(A2trans[j], vectors[k])
                AA.append(row)
                bb.append( 0 )
            soln = linearAlgebra.solve(AA,bb)
            for j in range(len(soln)):
                (vec,wec) = ifGoodCreateNodes(soln[j],vectors,lamb,m,l)
                if vec != None:
                    nodePnew = createNodePnew(vec,x,wec,y,soln[j][m+l],inputs)
                    nodePold = createNodePold(vec,x,wec,y,soln[j][m+l])
                    nodeL.append(createCallToEigenInv(nodePnew,nodePold,lamb))
    multirateGuard = createCallToMultirateInv(multirateL)
    if not(multirateGuard == None):
        nodeL.append(multirateGuard)
    i = 0
    while i < num:
        lamb = eigen[i]
        vectors = eigen[i+1]
        i += 2
        if vectors == None or len(vectors) == 0:
            continue
        if not(len(lamb) == 2):
            continue
        a = lamb[0]
        d = lamb[1]
        assert len(vectors) == 2
        u = vectors[0]
        v = vectors[1]
        # We know that A1'u=au-dv AND A1'v=bu+av
        # add something to nodeL
        # we want d/dt(u'x+w1'y+c1)= a*(u'x+w1'y+c1)-d*(v'x+w2'y+c2)
        # we want d/dt(v'x+w2'y+c2)= d*(u'x+w1'y+c1)+a*(v'x+w2'y+c2)
        # find w1,w2,c1,c2 s.t.
        # u'*(A1*x+A2*y+b1)+w1'*b2 = a*(u'x+w1'y+c1)-d*(v'x+w2'y+c2)
        # i.e., u'*(A2*y+b1)+w1'*b2 = a*(w1'y+c1)-d*(w2'y+c2)
        # i.e., u' A2 = a*w1'-d*w2' and u'*b1+w1'*b2 = a*c1-d*c2
        # v'*(A1*x+A2*y+b1)+w2'*b2 = d*(u'x+w1'y+c1)+a*(v'x+w2'y+c2)
        # i.e., v'*(A2*y+b1)+w2'*b2 = d*(w1'y+c1)+a*(w2'y+c2)
        # i.e., v' A2 = d w1' + a w2' and v'*b1+w2'*b2 = d*c1+a*c2
        # find w1,w2 such that v' A2 = d w1' + a w2' and u' A2 = a*w1'-d*w2' 
        # then find c1,c2 s.t v'*b1+w2'*b2 = d*c1+a*c2 and u'*b1+w1'*b2 = a*c1-d*c2
        # w1,w2 satisfy v' A2 = d w1' + a w2' and u' A2 = a*w1'-d*w2' 
        # w1,w2 satisfy (a*v'-d*u')*A2 = (a*a+d*d)*w2' 
        # w1,w2 satisfy (d*v'+a*u')*A2 = (a*a+d*d)*w1' 
        # c1,c2 satisfy v'*b1+w2'*b2 = d*c1+a*c2 and u'*b1+w1'*b2 = a*c1-d*c2
        # c1,c2 satisfy a*(v'*b1+w2'*b2)-d*(u'*b1+w1'*b2)=(a*a+d*d)*c2
        # c1,c2 satisfy d*(v'*b1+w2'*b2)+a*(u'*b1+w1'*b2)=(a*a+d*d)*c1
        if isZero(u):
            continue
        # w1,w2 satisfy (d*v'+a*u')*A2 = (a*a+d*d)*w1' 
        DD = a*a + d*d
        tmp = [ (a*v[j]-d*u[j])/DD for j in range(n) ]
        w2 = linearAlgebra.nmultiplyAv(A2trans, tmp)
        # w1 satisfies (d*v'+a*u')*A2 = (a*a+d*d)*w1' 
        tmp = [ (d*v[j]+a*u[j])/DD for j in range(n) ]
        w1 = linearAlgebra.nmultiplyAv(A2trans, tmp)
        # c2 satisfies a*(v'*b1+w2'*b2)-d*(u'*b1+w1'*b2)=(a*a+d*d)*c2
        tmp1 = linearAlgebra.dotproduct(v,b1)
        tmp1 += linearAlgebra.dotproduct(w2,b2)
        tmp2 = linearAlgebra.dotproduct(u,b1)
        tmp2 += linearAlgebra.dotproduct(w1,b2)
        c2 = (a*tmp1 - d*tmp2)/DD 
        # c1 satisfies d*(v'*b1+w2'*b2)+a*(u'*b1+w1'*b2)=(a*a+d*d)*c1
        c1 = (d*tmp1 + a*tmp2)/DD
        #ux+w1y+c1 and vx+w2y+c2 are position,velocity pair.
        # related by quadInv(_,_)
        nodePnew = createNodePnew(u,x,w1,y,c1,inputs)
        nodePold = createNodePold(u,x,w1,y,c1)
        nodeQnew = createNodePnew(v,x,w2,y,c2,inputs)
        nodeQold = createNodePold(v,x,w2,y,c2)
        # vec could be 0 vector and hence nodePnew could be None
        nodeL.append(createCallToQuadInv(nodePnew,nodePold,nodeQnew,nodeQold,a,d))
    return createNodeAnd(nodeL)

# collect all x s.t. dx/dt = constant
# replace them by their rel abs.
# all other x's: d (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c'A=l c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p

# If we fail to find eigen, we need BOX invs -- for later...

def absGuardedCommand(gc, inputs, basemod):
    """Return a new guarded command that is a rel abs of input GC.
       gc is the XML node of the guarded command, 
       inputs is a list of string names of all input variables
       basemod is the XML node of the basemodule of the gc"""
    global opt
    guard = gc.getElementsByTagName("GUARD")[0]
    assigns = gc.getElementsByTagName("ASSIGNMENTS")[0]
    defs = assigns.getElementsByTagName("SIMPLEDEFINITION")
    flow = getFlow(defs)
    [varlist,A,b] = flow2Ab(flow)
    # print "A"
    # print A
    # print "b"
    # print b
    guard = HSalXMLPP.getArg(guard,1)
    guardCopy = guard.cloneNode(True)
    if (opt & 0x4 != 0) :
        primeguard = HSalPreProcess2.makePrime(guardCopy, inputs, basemod)
        guardCopy = createNodeInfixApp('AND',guardCopy,primeguard)
    absgc = absGuardedCommandAux(varlist,A,b,inputs)
    absguardnode = createNodeInfixApp('AND',guardCopy,absgc)
    absguard = createNodeTagChild('GUARD',absguardnode)
    # absassigns = assigns.cloneNode(True)
    absassigns = absAssignments(varlist, keyLimit=len(flow)/2)
    return createNodeTagChild2('GUARDEDCOMMAND', absguard, absassigns)

def handleBasemodule(basemod, ctxt):
    """Side effect: replace cont. transition by relational abstraction
       by changing the DOM of the basemod, doms root is ctxt"""
    inputs = HSalPreProcess2.getInputs(basemod)
    cbody = basemod.getElementsByTagName("GUARDEDCOMMAND")
    for i in cbody:
        if isCont(i):
            absGC = absGuardedCommand(i, inputs, basemod)
            parentNode = i.parentNode
            if parentNode.localName == 'MULTICOMMAND':
                if not(absGC == None):
                    parentNode.appendChild(absGC)
                # print "Parent is a multicommand"
            elif parentNode.localName == 'SOMECOMMANDS':
                # print "Parent is SOMECOMMANDS"
                newnode = ctxt.createElement("MULTICOMMAND")
                oldChild = i.cloneNode(True)
                newnode.appendChild(oldChild)
                newnode.appendChild(absGC)
                parentNode.replaceChild(newChild=newnode, oldChild=i)
            else:
                print "Unknown parent node type"

def handleContext(ctxt):
    global opt
    basemodules = ctxt.getElementsByTagName("BASEMODULE")
    for i in basemodules:
        handleBasemodule(i, ctxt)
    cbody = ctxt.getElementsByTagName("CONTEXTBODY")
    assert len(cbody) == 1
    if (opt & 0x1 != 0):
        cbody[0].insertBefore(newChild=createNodeQuadInvOpt(),refChild=cbody[0].firstChild)
    if (opt & 0x2 != 0):
        cbody[0].insertBefore(newChild=createNodeQuadInvNonlinear(),refChild=cbody[0].firstChild)
    if (opt & 0x2 == 0):
        cbody[0].insertBefore(newChild=createNodeQuadInv(),refChild=cbody[0].firstChild)
    if (opt & 0x8 != 0):
        cbody[0].insertBefore(newChild=createTimedNodeQuadInv(),refChild=cbody[0].firstChild)
        cbody[0].insertBefore(newChild=createTimedNodeEigenInv(),refChild=cbody[0].firstChild)
    else:
        cbody[0].insertBefore(newChild=createNodeEigenInv(),refChild=cbody[0].firstChild)
        cbody[0].insertBefore(newChild=createNodeMultirateInv(),refChild=cbody[0].firstChild)
    cbody[0].insertBefore(newChild=createModNode(),refChild=cbody[0].firstChild)
    return ctxt

#def changeContextName(ctxt):
    #idnode = ctxt.getElementsByTagName("IDENTIFIER")[0]
    #for i in idnode.childNodes:
        #if i.nodeType == i.TEXT_NODE:
            #newnode = ctxt.createTextNode(i.data+"ABS")
            #idnode.replaceChild(newnode, i)
    #return ctxt
def hxml2sal(xmlfilename, optarg = 0, timearg = None):
    global dom
    global opt
    global time
    opt = optarg
    time = timearg
    basename,ext = os.path.splitext(xmlfilename)
    dom = xml.dom.minidom.parse(xmlfilename)
    setDom(dom)
    ctxt = HSalPreProcess.handleContext(dom)
    ctxt = HSalPreProcess2.handleContext(ctxt)
    newctxt = handleContext(ctxt)
    absfilename = basename + ".haxml"
    moveIfExists(absfilename)
    with open(absfilename, "w") as fp:
        print >> fp, newctxt.toxml()
    print "Created file %s containing the original+abstract model (XML)" % absfilename
    absfilename = basename + ".hasal"
    moveIfExists(absfilename)
    with open(absfilename, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the original+abstract model" % absfilename
    absXMLFile = basename + ".xml"
    moveIfExists(absXMLFile)
    with open(absXMLFile, "w") as fp:
        HSalExtractRelAbs.extractRelAbs(newctxt, fp)
    absSalFile = basename + ".sal"
    moveIfExists(absSalFile)
    with open(absSalFile, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the abstract model" % absSalFile
    return 0

def hsal2hxml(filename):
    def getexe():
        folder = os.path.split(inspect.getfile( inspect.currentframe() ))[0]
        relabsfolder = os.path.join(folder, '..', 'hybridsal2xml')
        relabsfolder = os.path.realpath(os.path.abspath(relabsfolder))
        return relabsfolder
    basename,ext = os.path.splitext(filename)
    if ext == '.hxml':
        xmlfilename = filename
    elif ext == '.hsal':
        xmlfilename = basename + ".hxml"
        hybridsal2xml = 'hybridsal2xml'
        if sys.platform.startswith('win'):
            hybridsal2xml += '.bat'
        exe = os.path.join(getexe(), hybridsal2xml)
        retCode = subprocess.call([exe, "-o", xmlfilename, filename])
        if retCode != 0 or not(os.path.isfile(xmlfilename)):
            print "hybridsal2xml failed to create XML file. Quitting."
            return 1
    else:
        print "Unknown file extension; Expecting .hsal or .hxml; Quitting"
        return 1
    return xmlfilename

def moveIfExists(filename):
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def printUsage():
    print "Usage: hsal-cegar [-h|--help] filename.hsal property"

def printHelp():
    print """
-------------------------------------------------------------------------
NAME
        bin/hsal-cegar - prove safety of HybridSAL models using CEGAR

SYNOPSIS
        bin/hsal-cegar [OPTION]... <file.hsal> <property>

DESCRIPTION
        Perform CEGAR-based verification of <property> in <file.hsal>
        Output a counter-example, or say proved.
        Input file is expected to be in HybridSAL (.hsal) syntax, or
        HybridSAL's XML representation (.hxml).

        Options include:
        -h, --help
            Print this help.
        -d, --depth
            Number of refinements to pursue before giving up.

EXAMPLE
        bin/hsal-cegar examples/Linear1.hsal correct

AUTHOR
        Written by Ashish Tiwari and Sridhar

REPORTING BUGS
        Report bin/hsal-cegar bugs to ashish_dot_tiwari_at_sri_dot_com

COPYRIGHT
        Copyright 2011 Ashish Tiwari, SRI International.
-------------------------------------------------------------------------
"""

def main():
    global dom
    global depth
    args = sys.argv[1:]
    if len(args) < 2:
        printUsage()
        return 1
    if ('-h' in args) | ('--help' in args) | ('-help' in args) | ('--h' in args):
        printHelp()
        return 0
    if ('-d' in args) | ('--depth' in args) :
        if ('-d' in args):
            index = args.index('-d')
        else:
            index = args.index('--depth')
        assert len(args) > index+1
        try:
            depth = int(args[index+1])
            assert depth > 0, "-d|--depth should be followed by a positive number"
        except ValueError:
            print "-d|--depth should be followed by a number"
            printUsage()
            return 1
    filename = args[len(args)-2] 
    prop = args[len(args)-1] 
    if not(os.path.isfile(filename)):
        print "File {0} does not exist. Quitting.".format(filename)
        return 1
    xmlfilename = hsal2hxml(filename)
    ans = hxml2sal(xmlfilename, opt, time)
    return ans

if __name__ == '__main__':
    main()

