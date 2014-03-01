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
import HSalTimeAwareAux
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


# ********************************************************************
# Functions for creating specific XML node for expressions
# ********************************************************************
def createNodeMultirateInv():
    """y'-y/s = x-x'/r"""
    fname = createNodeTag("IDENTIFIER", "multirateInv")
    vds = []
    vds.append(createNodeVarType("xold", "REAL"))
    vds.append(createNodeVarType("xnew", "REAL"))
    vds.append(createNodeVarType("r", "REAL"))
    vds.append(createNodeVarType("yold", "REAL"))
    vds.append(createNodeVarType("ynew", "REAL"))
    vds.append(createNodeVarType("s", "REAL"))
    fparams = createNodeTagChildn("VARDECLS", vds)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    num1 = createNodeApp("-", [ "xnew", "xold" ])
    num2 = createNodeApp("-", [ "ynew", "yold" ])
    lhs = createNodeApp("/", [ num1, "r" ])
    rhs = createNodeApp("/", [ num2, "s" ])
    fval = createNodeApp("=", [ lhs, rhs ])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createNodeEigenInv():
    """0 <= nodePnew <= nodePold OR nodePold <= nodePnew <= 0 """
    fname = createNodeTag("IDENTIFIER", "eigenInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("xnew", "REAL")
    fparams = createNodeTagChild2("VARDECLS", vd1, vd2)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    zero = createNodeTag("NUMERAL", "0")
    fact1 = createNodeApp("<", [ zero, "xnew" ])
    fact2 = createNodeApp("<", [ "xnew", "xold" ])
    fact3 = createNodeApp("<", [ "xold", "xnew" ])
    fact4 = createNodeApp("<", [ "xnew", zero.cloneNode(True) ])
    fact5 = createNodeApp("=", [ "xold", zero.cloneNode(True) ])
    fact6 = createNodeApp("=", [ "xnew", zero.cloneNode(True) ])
    fact12 = createNodeApp("AND", [ fact1, fact2 ])
    fact34 = createNodeApp("AND", [ fact3, fact4 ])
    fact56 = createNodeApp("AND", [ fact5, fact6 ])
    fact78 = createNodeApp("OR", [ fact12, fact34 ])
    fval = createNodeApp("OR", [ fact78, fact56 ])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

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

def createNodeVarType(varName, typeName):
    xold = createNodeTag("IDENTIFIER", varName)
    real = createNodeTag("TYPENAME", typeName)
    vd = createNodeTagChild2("VARDECL", xold, real)
    return vd

def createNodeApp(funName, argList, infix=True):
    """ funName(argList) """
    absNode = createNodeTag("NAMEEXPR", funName)
    argNode = createNodeTagChildn("TUPLELITERAL", [])
    for i in argList:
        if isinstance(i, basestring):
            node = createNodeTag("NAMEEXPR", i)
        else:
            node = i
        argNode.appendChild(node)
    ans = createNodeTagChild2("APPLICATION", absNode, argNode)
    if len(argList) == 2 and infix:
        ans.setAttribute('INFIX', 'YES')
    return ans

def createModNode():
    """mod(x:REAL):REAL = if x < 0 THEN -x ELSE x endif"""
    fname = createNodeTag("IDENTIFIER", "abs")
    vardecl = createNodeVarType("a", "REAL")
    fparams = createNodeTagChild("VARDECLS", vardecl)
    ftype = createNodeTag("TYPENAME", "REAL")
    a = createNodeTag("NAMEEXPR", "a")
    zero = createNodeTag("NUMERAL", "0")
    ifn = createNodeApp("<", [a, zero])		# a < 0
    thenn = createNodeApp("-", [ "a" ])		# -a
    elsen = createNodeTag("NAMEEXPR", "a")
    fval = createNodeTagChild3("CONDITIONAL", ifn, thenn, elsen)
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createNodeAbsVar(varName):
    """ |varName| """
    return createNodeApp("abs", [ varName ])

def createNodeQuadInvNonlinear():
    """ xnew^2+ynew^2 <= xold^2 + yold^2 """
    fname = createNodeTag("IDENTIFIER", "quadInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("yold", "REAL")
    vd3 = createNodeVarType("xnew", "REAL")
    vd4 = createNodeVarType("ynew", "REAL")
    fparams = createNodeTagChild4("VARDECLS", vd1, vd2, vd3, vd4)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    xoldSq = createNodeApp("*", ["xold", "xold"])
    yoldSq = createNodeApp("*", ["yold", "yold"])
    xnewSq = createNodeApp("*", ["xnew", "xnew"])
    ynewSq = createNodeApp("*", ["ynew", "ynew"])
    xoldPlusyold = createNodeApp("+", [xoldSq, yoldSq])
    xnewPlusynew = createNodeApp("+", [xnewSq, ynewSq])
    fact1 = createNodeApp("<=", [xnewPlusynew, xoldPlusyold])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fact1)
    return ans

def createNodeQuadInv():
    """ if a < 0: |xnew|,|ynew| <= |xold| + |yold|
        |xnew| <= |xold| or |ynew| <= |yold|
        |xnew| <= |yold| or |ynew| <= |xold| """
    fname = createNodeTag("IDENTIFIER", "quadInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("yold", "REAL")
    vd3 = createNodeVarType("xnew", "REAL")
    vd4 = createNodeVarType("ynew", "REAL")
    fparams = createNodeTagChild4("VARDECLS", vd1, vd2, vd3, vd4)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    modxnew = createNodeAbsVar("xnew")
    modynew = createNodeAbsVar("ynew")
    modxold = createNodeAbsVar("xold")
    modyold = createNodeAbsVar("yold")
    xoldPlusyold = createNodeApp("+", [modxold, modyold])
    fact1 = createNodeApp("<=", [modxnew, xoldPlusyold])
    fact2 = createNodeApp("<=", [modynew, xoldPlusyold.cloneNode(True)])
    fact31 = createNodeApp("<=", [modxnew.cloneNode(True), modxold.cloneNode(True)])
    fact32 = createNodeApp("<=", [modynew.cloneNode(True), modyold.cloneNode(True)])
    fact3 = createNodeApp("OR", [ fact31, fact32 ])
    fact41 = createNodeApp("<=", [modxnew.cloneNode(True), modyold.cloneNode(True)])
    fact42 = createNodeApp("<=", [modynew.cloneNode(True), modxold.cloneNode(True)])
    fact4 = createNodeApp("OR", [ fact41, fact42 ])
    fval = createNodeAnd([fact1, fact2, fact3, fact4])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createNodeQuadInvOpt():
    """ if a < 0: |xnew|,|ynew| <= |xold| + |yold|
        |xnew| <= |xold| or |ynew| <= |yold|
        |xnew| <= |yold| or |ynew| <= |xold| """
    fname = createNodeTag("IDENTIFIER", "quadInvOpt")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("yold", "REAL")
    vd3 = createNodeVarType("xnew", "REAL")
    vd4 = createNodeVarType("ynew", "REAL")
    fparams = createNodeTagChild4("VARDECLS", vd1, vd2, vd3, vd4)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    rcst = createNodeTag("NUMERAL", "1/10")
    lcst = createNodeTag("NUMERAL", "-1/10")
    fact1 = createNodeApp("<=", [ lcst, "xnew" ])
    fact2 = createNodeApp("<=", [ "xnew", rcst ])
    fact3 = createNodeApp("<=", [ lcst.cloneNode(True), "ynew" ])
    fact4 = createNodeApp("<=", [ "ynew", rcst.cloneNode(True) ])
    fval = createNodeAnd([fact1, fact2, fact3, fact4])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans


# *****************************************************************************
# Wrapper for creating call to EigenInv or QuadInv or MultiAffineInv
# *****************************************************************************
def createCallToMultirateInv(rateL):
    """rateL is list of [ynew, yold, rate].  Return an XML SAL 
       expression for the guard that calls multiAffine(...)"""

    def createMultirateInv(xold, xnew, r, yold, ynew, s):
        return createNodeApp("multirateInv", [xold,xnew,r,yold,ynew,s])

    def createTimedMultirateInv(xold, xnew, delta):
        deltanode = createNodeTag("NUMERAL", mystr(delta))
        xoldPlusDelta = createNodeInfixApp('+', xold, deltanode)
        return createNodeInfixApp('=', xoldPlusDelta, xnew)

    def createMinDwellMultirateInv(xold, xnew, delta):
        deltanode = createNodeTag("NUMERAL", mystr(delta))
        xoldPlusDelta = createNodeInfixApp('+', xold, deltanode)
        if delta > 0:
            return createNodeInfixApp('<=', xoldPlusDelta, xnew)
        elif delta < 0:
            return createNodeInfixApp('>=', xoldPlusDelta, xnew)
        else:
            return createNodeInfixApp('=', xoldPlusDelta, xnew)

    def createBaseCase(xold, xnew, rate):
        global opt, time
        if (opt & 0x8 != 0):
            return createTimedMultirateInv(xold, xnew, rate*time)
        if (opt & 0x10 != 0):
            return createMinDwellMultirateInv(xold, xnew, rate*time)
        if rate > 0:
            return createNodeInfixApp('<=', xold, xnew)
        else:
            return createNodeInfixApp('>=', xold, xnew)

    def createInductionCase(xold, xnew, r, yold, ynew, s):
        global opt, time
        if (opt & 0x8 != 0):
            return createTimedMultirateInv(yold, ynew, s*time)
        if (opt & 0x10 != 0):
            return createMinDwellMultirateInv(yold, ynew, s*time)
        rn = createNodeTag("NUMERAL", mystr(r))
        sn = createNodeTag("NUMERAL", mystr(s))
        (xold,xnew) = (xold.cloneNode(True),xnew.cloneNode(True))
        return createMultirateInv(xold,xnew,rn,yold,ynew,sn)

    (xold,xnew,r) = (None,None,None)
    nodes = list()
    for [ynew,yold,srate] in rateL:
        if equal(srate, 0):
            nodes.append(createNodeInfixApp('=', yold, ynew))
        elif xold == None:
            (xold,xnew,r) = (yold,ynew,srate)
            nodes.append( createBaseCase(xold, xnew, r) )
        else:
            nodes.append( createInductionCase(xold,xnew,r,yold,ynew,srate) )
    return createNodeAnd(nodes)

def createCallToEigenInv(xnew, xold, lamb):
    """create call to appropriate eigenInv( ) function"""
    global opt
    global time

    def createEigenInv(nodePnew,nodePold,lamb):
        """create in XML call for eigenInv(xnew,xold,lamb)"""
        if lamb < 0:
            ans = createNodeApp("eigenInv", [ nodePold, nodePnew ], infix=False)
        else:
            ans = createNodeApp("eigenInv", [ nodePnew, nodePold ], infix=False)
        return ans

    def createTimedEigenInv(nodePnew,nodePold,lamb,time):
        """eigenTimedInv(nodePold,nodePnew,exp(lamb*time))"""
        k = math.exp(lamb*time)
        knode = createNodeTag("NUMERAL", mystr(k))
        ans = createNodeApp("eigenTimedInv", [ nodePold, nodePnew, knode ], infix=False)
        return ans

    def createMinDwellEigenInv(nodePnew,nodePold,lamb,time):
        """eigenTimedInv(nodePold,nodePnew,exp(lamb*time))"""
        k = math.exp(-abs(lamb)*time)
        knode = createNodeTag("NUMERAL", mystr(k))
        nodePold1 = createNodeApp("*", [ knode, nodePold ], infix=True)
        ans = createEigenInv(nodePnew, nodePold1, lamb)
        return ans

    def createTimeAwareEigenInv(nodePnew,nodePold,lamb,time):
        """eigenInvTime(nodePold,nodePnew,lamb>0,time[0],time[0]')"""
        lambNode = createNodeTag("NUMERAL", mystr(abs(lamb)))
        told = createNodeTag("NAMEEXPR", time[0])
        tnew = createNodeTagChild("NEXTOPERATOR", told.cloneNode(True))
        if lamb < 0:
            ans = createNodeApp("eigenInvTime", [ nodePnew, nodePold, lambNode, told, tnew ], infix=False)
        else:
            ans = createNodeApp("eigenInvTime", [ nodePold, nodePnew, lambNode, told, tnew ], infix=False)
        return ans

    if equal(lamb, 0):
        ans = createNodeInfixApp('=', xold, xnew)
    elif opt & 0x8 != 0:
        ans = createTimedEigenInv(xnew,xold,lamb,time)
    elif opt & 0x10 != 0:
        ans = createMinDwellEigenInv(xnew,xold,lamb,time)
    elif opt & 0x20 != 0:
        ans = createTimeAwareEigenInv(xnew,xold,lamb,time)
    else:
        ans = createEigenInv(xnew,xold,lamb)
    return ans

def createCallToQuadInv(xnew,xold,ynew,yold,a,b):
    """create appropriate call in XML to quadInv"""

    def createQuadInv(xnew, xold, ynew, yold):
        """create in XML call to quadInv(xold, xold, xnew, ynew)"""
        return createNodeApp("quadInv", [ xold, yold, xnew, ynew ])

    def createQuadInvOpt(xnew, xold, ynew, yold):
        """create in XML call to quadInvOpt(xnew, xnew, xold, yold)"""
        return createNodeApp("quadInvOpt", [ xold, yold, xnew, ynew ])

    def createQuadTimedInv(xnew, xold, ynew, yold, a, b):
        """create in XML call to quadTimedInv(xnew, xnew, xold, yold, k)"""
        return createNodeApp("quadTimedInv", [ xold, yold, xnew, ynew, a, b ])

    def createCallToTimedQuadInv(xnew,xold,ynew,yold,a,b,time):
        """quadTimedInv(nodePold,nodeQold,nodePnew,nodeQnew,exp(a*t))"""
        k = math.exp((a/2.0)*time)
        l = math.cos(b*time)
        knode = createNodeTag("NUMERAL", mystr(k*l))
        l = math.sin(b*time)
        lnode = createNodeTag("NUMERAL", mystr(k*l))
        return createQuadTimedInv(xnew, xold, ynew, yold, knode, lnode)

    def createCallToMinDwellQuadInv(xnew,xold,ynew,yold,a,b,time):
        """x(t) = exp(-a/2*t) * ( x(0) cos(wt) - y(0) sin(wt) )
        y(t) = exp(-a/2*t) * ( x(0) sin(wt) + y(0) cos(wt) )
        x(t) = a * x(0) - b * y(0)
        y(t) = b * x(0) + a * y(0) """
        k = math.exp((a/2.0)*time)
        l = math.cos(b*time)
        a1 = createNodeTag("NUMERAL", mystr(k*l))
        l = math.sin(b*time)
        b1 = createNodeTag("NUMERAL", mystr(k*l))
        xold11 = createNodeApp("*", [ a1, xold], infix=True) 
        xold12 = createNodeApp("*", [ b1, yold], infix=True) 
        xold1 = createNodeApp("-", [ xold11, xold12], infix=True)
        yold11 = createNodeApp("*", [ b1.cloneNode(True), xold.cloneNode(True)], infix=True) 
        yold12 = createNodeApp("*", [ a1.cloneNode(True), yold.cloneNode(True)], infix=True) 
        yold1 = createNodeApp("+", [ yold11, yold12], infix=True)
        return (xold1, yold1)

    def createCallToTimeAwareQuadInv(xnew,xold,ynew,yold,a,b,time):
        """quadInvTime(nodePold,nodeQold,nodePnew,nodeQnew,a>0,b>0,t,t')"""
        anode = createNodeTag("NUMERAL", mystr(abs(a)))
        bnode = createNodeTag("NUMERAL", mystr(abs(b)))
        told = createNodeTag("NAMEEXPR", time[0])
        tnew = createNodeTagChild("NEXTOPERATOR", told.cloneNode(True))
        if a > 0 and b > 0:
            return createNodeApp("quadInvTime", [ xold, yold, xnew, ynew, anode, bnode, told, tnew ])
        elif a > 0 and b < 0:
            return createNodeApp("quadInvTime", [ yold, xold, ynew, xnew, anode, bnode, told, tnew ])
        elif a < 0 and b < 0:
            return createNodeApp("quadInvTime", [ ynew, xnew, yold, xold, anode, bnode, told, tnew ])
        else:
            return createNodeApp("quadInvTime", [ xnew, ynew, xold, yold, anode, bnode, told, tnew ])

    global opt
    global time
    if (opt & 0x8 != 0):
        return createCallToTimedQuadInv(xnew, xold, ynew, yold, a, b, time)
    if (opt & 0x20 != 0):
        return createCallToTimeAwareQuadInv(xnew, xold, ynew, yold, a, b, time)
    if (opt & 0x10 != 0):
        (xold,yold) = createCallToMinDwellQuadInv(xnew, xold, ynew, yold, a, b, time)
    if equal(a, 0):
        ans1=createQuadInv(xnew, xold, ynew, yold)
        ans2=createQuadInv(xold.cloneNode(True), xnew.cloneNode(True), yold.cloneNode(True), ynew.cloneNode(True))
        return createNodeAnd([ ans1, ans2 ])
    if (opt & 0x1 != 0) & (a < 0):
        return createQuadInvOpt(xnew, xold, ynew, yold)
    if a < 0:
        return createQuadInv(xnew, xold, ynew, yold)
    if a > 0:
        return createQuadInv(xold, xnew, yold, ynew)
    print "Unreachable code"
    return None
# *****************************************************************************

# *****************************************************************************
# Functions for creating specific XML node for Timed Invariants
# This code is executed when flag -t is used.
# *****************************************************************************
def createTimedNodeEigenInv():
    """eigenTimedInv(xold,xnew,k): BOOLEAN = (xnew = k*xold) ;"""
    fname = createNodeTag("IDENTIFIER", "eigenTimedInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("xnew", "REAL")
    vd3 = createNodeVarType("k", "REAL")
    fparams = createNodeTagChild3("VARDECLS", vd1, vd2, vd3)
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    fact0 = createNodeApp("*", [ "k", "xold" ])
    fval = createNodeApp("=", [ "xnew", fact0 ])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createTimedNodeQuadInv():
    """ quadTimedInv(xold,yold,xnew,ynew,a,b:REAL):BOOLEAN =
        x(t) = exp(-a/2*t) * ( x(0) cos(wt) - y(0) sin(wt) )
        y(t) = exp(-a/2*t) * ( x(0) sin(wt) + y(0) cos(wt) )
        x(t) = a * x(0) - b * y(0)
        y(t) = b * x(0) + a * y(0) """
    fname = createNodeTag("IDENTIFIER", "quadTimedInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("yold", "REAL")
    vd3 = createNodeVarType("xnew", "REAL")
    vd4 = createNodeVarType("ynew", "REAL")
    vd5 = createNodeVarType("a", "REAL")
    vd6 = createNodeVarType("b", "REAL")
    fparams = createNodeTagChildn("VARDECLS", [vd1,vd2,vd3,vd4,vd5,vd6])
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    axold = createNodeApp("*", ["a", "xold"])
    byold = createNodeApp("*", ["b", "yold"])
    bxold = createNodeApp("*", ["b", "xold"])
    ayold = createNodeApp("*", ["a", "yold"])
    axMby = createNodeApp("-", [ axold, byold ])
    bxPay = createNodeApp("+", [ bxold, ayold ])
    fact1 = createNodeApp("=", [ "xnew", axMby ])
    fact2 = createNodeApp("=", [ "ynew", bxPay ])
    fval = createNodeAnd([fact1, fact2])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans

def createMinDwellNodeQuadInv():
    """ quadMinDwellInv(xold,yold,xnew,ynew,a,b:REAL):BOOLEAN =
        x(t) = exp(-a/2*t) * ( x(0) cos(wt) - y(0) sin(wt) )
        y(t) = exp(-a/2*t) * ( x(0) sin(wt) + y(0) cos(wt) )
        x(t) = a * x(0) - b * y(0)
        y(t) = b * x(0) + a * y(0) """
    fname = createNodeTag("IDENTIFIER", "quadTimedInv")
    vd1 = createNodeVarType("xold", "REAL")
    vd2 = createNodeVarType("yold", "REAL")
    vd3 = createNodeVarType("xnew", "REAL")
    vd4 = createNodeVarType("ynew", "REAL")
    vd5 = createNodeVarType("a", "REAL")
    vd6 = createNodeVarType("b", "REAL")
    fparams = createNodeTagChildn("VARDECLS", [vd1,vd2,vd3,vd4,vd5,vd6])
    ftype = createNodeTag("TYPENAME", "BOOLEAN")
    axold = createNodeApp("*", ["a", "xold"])
    byold = createNodeApp("*", ["b", "yold"])
    bxold = createNodeApp("*", ["b", "xold"])
    ayold = createNodeApp("*", ["a", "yold"])
    axMby = createNodeApp("-", [ axold, byold ])
    bxPay = createNodeApp("+", [ bxold, ayold ])
    fact1 = createNodeApp("=", [ "xnew", axMby ])
    fact2 = createNodeApp("=", [ "ynew", bxPay ])
    fval = createNodeAnd([fact1, fact2])
    ans = createNodeTagChild4("CONSTANTDECLARATION", fname, fparams, ftype, fval)
    return ans
# *****************************************************************************


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
    def processMlist(mlist, inputs):
        multirateL = []
        for (c, x, rate) in mlist:
            yold = createNodeCX(c, x, False, None)
            ynew = createNodeCX(c, x, True, inputs)
            multirateL.append([ynew, yold, rate])
        multirateGuard = createCallToMultirateInv(multirateL)
        return multirateGuard

    def processElist(elist, inputs):
        eigencalls = []
        for ((vec,x,wec,y,const),lamb) in elist:
            nodePnew = createNodePnew(vec,x,wec,y,const,inputs)
            nodePold = createNodePold(vec,x,wec,y,const)
            if not(nodePnew == None):
                eigencalls.append(createCallToEigenInv(nodePnew,nodePold,lamb))
        return eigencalls

    def processQlist(qlist, inputs):
        qcalls = []
        for ( (u,x,w1,y,c1), (v,x,w2,y,c2), a, d) in qlist: 
            nodePnew = createNodePnew(u,x,w1,y,c1,inputs)
            nodePold = createNodePold(u,x,w1,y,c1)
            nodeQnew = createNodePnew(v,x,w2,y,c2,inputs)
            nodeQold = createNodePold(v,x,w2,y,c2)
            # vec could be 0 vector and hence nodePnew could be None
            qcalls.append(createCallToQuadInv(nodePnew,nodePold,nodeQnew,nodeQold,a,d))
        return qcalls

    (mlist, elist, qlist) = Ab2eigen(varlist, A, b, inputs)
    nodeL = []
    multirateGuard = processMlist(mlist, inputs)
    if not(multirateGuard == None):
        nodeL.append(multirateGuard)
    eigencalls = processElist(elist, inputs)
    nodeL.extend(eigencalls)
    qcalls = processQlist(qlist, inputs)
    nodeL.extend(qcalls)
    return createNodeAnd(nodeL)
    
def Ab2eigen(varlist,A,b,inputs):
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
            # yold = createNodeTag("NAMEEXPR", varName)
            # ynew = createNodeTagChild("NEXTOPERATOR", yold.cloneNode(True))
            # multirateL.append([ynew, yold, b2[i]])
            multirateL.append(([1], {varName:0}, b2[i]))
        return multirateL

    [x,y,A1,A2,b1,b2] = partition(varlist,A,b)
    # [x,y,A1,A2,b1,b2] s.t. (x;y) = (A1 A2; 0 0) (x;y) + (b1;b2)"
    n = len(x)
    m = len(y)
    if n == 0:
        print "dx/dt is a constant for all x"
    mlist = multirateList(y, b2, inputs) 
    # guardAbs1 = multirateAbs(y, b2)
    A1trans = linearAlgebra.transpose(A1)
    eigen = linearAlgebra.eigen(A1trans)
    # CHECK above, tranpose added, [ l [ vectors ] l [ vectors ] ]
    # print "The LEFT eigenvectors computed are:"
    # print eigen
    num = len(eigen)
    i = 0
    A2trans = linearAlgebra.transpose(A2)
    #nodeL = list()
    #if not(guardAbs1 == None):
        #nodeL.append(guardAbs1)
    elist = []
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
                    # pold = createNodeCX(vec,x,False,None)
                    # pnew = createNodeCX(vec,x,True,inputs)
                    # multirateL.append([pnew,pold,const])
                    mlist.append( ( vec, x, const ) )
                else:
                    print "lamb==0, but no corr. invariant found"
                    continue
            else:
                for j in range(len(wec)):
                    wec[j] /= lamb
                const += linearAlgebra.dotproduct(wec,b2)
                const = float(const) / lamb
                elist.append( ((vec,x,wec,y,const),lamb) )
                # nodePnew = createNodePnew(vec,x,wec,y,const,inputs)
                # nodePold = createNodePold(vec,x,wec,y,const)
                # if not(nodePnew == None):
                    # nodeL.append(createCallToEigenInv(nodePnew,nodePold,lamb))
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
                    #nodePnew = createNodePnew(vec,x,wec,y,soln[j][m+l],inputs)
                    #nodePold = createNodePold(vec,x,wec,y,soln[j][m+l])
                    #nodeL.append(createCallToEigenInv(nodePnew,nodePold,lamb))
                    elist.append( ((vec,x,wec,y,soln[j][m+l]),lamb) )
    # multirateGuard = createCallToMultirateInv(multirateL)
    # if not(multirateGuard == None):
        # nodeL.append(multirateGuard)
    qlist = []
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
        # nodePnew = createNodePnew(u,x,w1,y,c1,inputs)
        # nodePold = createNodePold(u,x,w1,y,c1)
        # nodeQnew = createNodePnew(v,x,w2,y,c2,inputs)
        # nodeQold = createNodePold(v,x,w2,y,c2)
        # vec could be 0 vector and hence nodePnew could be None
        # nodeL.append(createCallToQuadInv(nodePnew,nodePold,nodeQnew,nodeQold,a,d))
        qlist.append( ((u,x,w1,y,c1), (v,x,w2,y,c2), a, d) )
    # return createNodeAnd(nodeL)
    return (mlist, elist, qlist)

# collect all x s.t. dx/dt = constant
# replace them by their rel abs.
# all other x's: d (x;y) = (A B; 0 0) (x;y) + (b1;b2)
# Suppose c'A=l c' is a left eigenvector of A with eigenvalue l
# Pick d' s.t. l d' = c' B
# d/dt(c'x+d'y)=c'(Ax+By+b1)+d'b2 = l c'x + l d'y + c'b1 + d'b2
# Let p := (c'x+d'y+ (c'b1+d'b2)/l) THEN dp/dt = l p

# If we fail to find eigen, we need BOX invs -- for later...

def absAssignments(varlist, keyLimit):
    """For each variable in varlist, create RHSSELECTION"""
    global dom
    ans = dom.createElement("ASSIGNMENTS")
    for var,index in varlist.iteritems():
        if index >= keyLimit:
            continue
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
            if absGC == None:
                continue
            parentNode = i.parentNode
            if parentNode.localName == 'MULTICOMMAND':
                parentNode.appendChild(absGC)
                # print "Parent is a multicommand"
            elif parentNode.localName == 'SOMECOMMANDS':
                # print "Parent is SOMECOMMANDS"
                newnode = ctxt.createElement("MULTICOMMAND")
                oldChild = i.cloneNode(True)
                newnode.appendChild(oldChild)
                newnode.appendChild(absGC)
                parentNode.replaceChild(newChild=newnode, oldChild=i)
            elif parentNode.localName == 'LABELEDCOMMAND':
                absGCNew = ctxt.createElement("LABELEDCOMMAND")
                label = parentNode.getElementsByTagName('LABEL')[0]
                newlabel = label.cloneNode(True)
                absGCNew.appendChild(newlabel)
                absGCNew.appendChild(absGC)
                absGC = absGCNew
                grandparentNode = parentNode.parentNode
                if grandparentNode.localName == 'MULTICOMMAND':
                    grandparentNode.appendChild(absGC)	# should add LABELED
                elif grandparentNode.localName == 'SOMECOMMANDS':
                    newnode = ctxt.createElement("MULTICOMMAND")
                    oldChild = parentNode.cloneNode(True)
                    newnode.appendChild(oldChild)
                    newnode.appendChild(absGC)
                    grandparentNode.replaceChild(newChild=newnode, oldChild=parentNode)
                else:
                    print "Unknown grandparent node type"
            else:
                print "Unknown parent node type"

def handleContext(ctxt):
    global dom
    global opt
    global time

    def createTimeAwareAux(time):
        newnode = dom.createElement("VERBATIM")
        newnode.appendChild( dom.createTextNode( HSalTimeAwareAux.createSALAuxFunc( time[1][0], time[1][1], time[1][2]) ) )
        return newnode

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
    if (opt & 0x20 != 0):
        cbody[0].insertBefore(newChild=createTimeAwareAux(time),refChild=cbody[0].firstChild)
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
    '''absfilename = basename + ".haxml"
    moveIfExists(absfilename)
    with open(absfilename, "w") as fp:
        print >> fp, newctxt.toxml()
    print "Created file %s containing the original+abstract model (XML)" % absfilename
    absfilename = basename + ".hasal"
    moveIfExists(absfilename)
    with open(absfilename, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the original+abstract model" % absfilename
    '''
    absXMLFile = basename + ".xml"
    moveIfExists(absXMLFile)
    with open(absXMLFile, "w") as fp:
        HSalExtractRelAbs.extractRelAbs(newctxt, fp)
    absSalFile = basename + ".sal"
    moveIfExists(absSalFile)
    with open(absSalFile, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the abstract model" % absSalFile
    assertions = ctxt.getElementsByTagName("ASSERTIONDECLARATION")
    p1_exists = (assertions != None and len(assertions) > 0)
    return absSalFile, p1_exists

def hsal2hxml(filename):
    def checkexe(filename):
        exepaths = os.environ['PATH'].split(os.path.pathsep)
        for i in exepaths:
            exefile = os.path.join(i, filename)
            if os.path.exists(exefile):
                return True
        print 'ERROR: File {0} not found in PATH.'.format(filename)
        return False
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
        if checkexe(hybridsal2xml):
            exe = hybridsal2xml
        else:
            exe = os.path.join(getexe(), hybridsal2xml)
            assert os.path.exists(exe), 'ERROR: {0} not found'.format(exe)
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
    print "Usage: hsal2hasal [-o|--opt|-n|--nonlinear|-c|--copyguard|-mdt <t>|--mindwelltime <t>|-t <t>|--time <t>] filename.hsal"

def printHelp():
    print """
-------------------------------------------------------------------------
NAME
        bin/hsal2hasal - construct relational abstraction of HybridSAL models

SYNOPSIS
        bin/hasal [OPTION]... [FILE]

DESCRIPTION
        Construct a relational abstraction of the model in [FILE].
        Create a new SAL file containing the abstract model.
        Input file is expected to be in HybridSAL (.hsal) syntax, or
        HybridSAL's XML representation (.hxml).
        The new file will have the same name as [FILE], but
        a different extension, .sal

        Options include:
        -c, --copyguard
            Explicitly handle the guards in the continuous dynamics
            as state invariants
        -n, --nonlinear
            Create a nonlinear abstract model
            Note that freely available model checkers are unable
            to handle nonlinear models, hence this option is 
            useful for research purposes only
        -t <T>, --timed <T>
            Create a timed relational abstraction assuming that
            the controller is run every <T> time units.
            <T> should be a number (such as, 0.01)
        -o, --optimize
            Create an optimized relational abstraction.
            Certain transient's are unsoundly eliminated from the
            abstract SAL model to improve performance of the model 
            checkers on the generated SAL model
        -mdt <T>, --mindwelltime <T>
            Create a relational abstraction assuming a minimum of 
            <T> time units is spent in each mode.
        -ta <time,l,m,n>
            Create a time-aware relational abstraction assuming <time> 
            to be the time variable, l, m, n as the parameters 
            l = number of intervals left of e^0 for real eigenvalues to use
            m = number of intervals right of e^0 for real eigenvalues to use
            n = number of cycles for complex eigenvalues to use 

EXAMPLE
        bin/hsal2hasal examples/Linear1.hsal
        This command creates a file examples/Linear1.sal

        bin/hsal2hasal -ta time,3,4,2 examples/Linear1.hsal
        This command creates a file examples/Linear1.sal containing a more
        precise abstraction 

AUTHOR
        Written by Ashish Tiwari

REPORTING BUGS
        Report bin/hsal2hasal bugs to ashish_dot_tiwari_at_sri_dot_com

COPYRIGHT
        Copyright 2011 Ashish Tiwari, SRI International.
-------------------------------------------------------------------------
"""

def main():
    global dom
    global opt
    global time
    opt = 0
    time = None
    args = sys.argv[1:]
    if len(args) < 1:
        printUsage()
        return 1
    if ('-h' in args) | ('--help' in args) | ('-help' in args) | ('--h' in args):
        printHelp()
        return 0
    if ('-o' in args) | ('--opt' in args) :
        opt |= 0x1
    if ('-n' in args) | ('--nonlinear' in args) :
        opt |= 0x2
    if ('-c' in args) | ('--copyguard' in args) :
        opt |= 0x4
    if ('-t' in args) | ('--time' in args) :
        opt |= 0x8
        if ('-t' in args):
            index = args.index('-t')
        else:
            index = args.index('--time')
        assert len(args) > index+1
        try:
            time = float(args[index+1])
        except ValueError:
            print "-t|--time should be followed by a float"
            printUsage()
            return 1
    if ('-mdt' in args) | ('--mindwelltime' in args) :
        opt |= 0x10
        if ('-mdt' in args):
            index = args.index('-mdt')
        else:
            index = args.index('--mindwelltime')
        assert len(args) > index+1
        try:
            time = float(args[index+1])
        except ValueError:
            print "-t|--time should be followed by a float"
            printUsage()
            return 1
    if ('-ta' in args) | ('--timeaware' in args) :
        opt |= 0x20
        if ('-ta' in args):
            index = args.index('-ta')
        else:
            index = args.index('--timeaware')
        try:
            assert len(args) > index+1
            timeNML = args[index+1]
	    timeNMLlist = timeNML.split(',')
            assert len(timeNMLlist) == 4
            time = (timeNMLlist[0], [ int(x) for x in timeNMLlist[1:] ])
        except : # AssertionError ValueError
            print "-ta|--timeaware should be followed by (timeVarName,M,N,L)"
            printUsage()
            return 1
    # for i in sys.argv[1:]:
        # if (len(i) > 0) & (i[0] == '-'):
            # print "Unknown option" + i
            # printUsage()
            # return 1
        # filename = i
    filename = args[len(args)-1] # sys.argv[1]
    if not(os.path.isfile(filename)):
        print "File does not exist. Quitting."
        return 1
    xmlfilename = hsal2hxml(filename)
    ans = hxml2sal(xmlfilename, opt, time)
    return ans

if __name__ == '__main__':
    main()

