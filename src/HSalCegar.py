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
import HSalRelAbsCons
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

# class - Cont. Dyn. Sys;
class CDS:
    def __init__(self, x):
        self.x = x
    def setAb(self, A, b):
        self.A, self.b = A, b
    def seteigen(self,elist):
        self.eigen = elist
    def setmulti(self, mlist):
        self.multi = mlist
    def setquad(self, qlist):
        self.quad = qlist
    def setsafe(self, prop):
        self.safe = prop
    def setmodeinv(self, inv):
        self.modeinv = inv
    def setinputs(self, inputs):
        self.inputs = inputs
    def setinit(self, init):
        self.init = init
    def toStr(self):
         out = 'CDS:\n x = {0},'.format(self.x)
         out += '\n init = '
         for i in self.init:
             out += '{0},'.format(i.toxml())
         out += '\n A = {0},\n b = {1},'.format(self.A, self.b, self.safe)
         out += '\n safe = {0},'.format(self.safe.toxml())
         out += '\n modeinv = {0},'.format(self.modeinv.toxml())
         out += '\n inputs  = {0},'.format(self.inputs)
         out += '\n\n eigen = {0},'.format(self.eigen)
         out += '\n multi = {0},'.format(self.multi)
         out += '\n quad = {0},'.format(self.quad)
         return out
    # d = dict from 'A1', 'A2', 'b1', 'b2', 'x', 'y' to values

def simpleDefinitionRhsExpr(defn):
    "Return the RHS expression in definition def"
    rhs = defn.getElementsByTagName("RHSEXPRESSION")
    if rhs == None:
        return None
    else:
        return exprs2poly(rhs[0].childNodes)
    
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
            multirateL.append((varName, b2[i]))
        return multirateL

    [x,y,A1,A2,b1,b2] = HSalRelAbsCons.partition(varlist,A,b)
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

def handleGuardedCommand(gc):
    guard = gc.getElementsByTagName("GUARD")[0]
    assigns = gc.getElementsByTagName("ASSIGNMENTS")[0]
    defs = assigns.getElementsByTagName("SIMPLEDEFINITION")
    flow = HSalRelAbsCons.getFlow(defs)
    [varlist,A,b] = HSalRelAbsCons.flow2Ab(flow)
    # print "A"
    # print A
    # print "b"
    # print b
    guard = HSalXMLPP.getArg(guard,1)
    return (guard, varlist, A, b)

def init2Formula( xmlnode ):
    "xmlnode is XML for INITDECL; turn it into XML for formula represented by INITDECL"
    def simpledef2fmlalist( node ):
        "node is XML node for SIMPLEDEFINITION, return list of formula XML-nodes"
        lhs = HSalXMLPP.getArg(node, 1)
        rhs = HSalXMLPP.getArg(node, 2)
        assert lhs.tagName == 'NAMEEXPR','ERROR: Unidentified tagName {0} for LHS in simpledefinition'.format(lhs.tagName)
        if rhs.tagName == 'RHSEXPRESSION':
            rhsVal = HSalXMLPP.getArg(rhs,1)
            return [ createNodeInfixApp('=', lhs, rhsVal) ]
        elif rhs.tagName == 'RHSSELECTION':
            rhsVal = HSalXMLPP.getArg(rhs,1)
            assert rhsVal.tagName == 'SETPREDEXPRESSION', 'ERROR: Unidentified tagName {0}'.format(rhsVal.tagName)
            dummyvar = HSalXMLPP.getNameTag(rhsVal, 'IDENTIFIER').strip()
            lhsvar = HSalXMLPP.valueOf( lhs ).strip()
            rhsfmla = HSalXMLPP.getArg(rhsVal, 3)
            # replace dummyvar by lhsvar in rhsfmla
            allnames = rhsfmla.getElementsByTagName('NAMEEXPR')
            for i in allnames:
                if HSalXMLPP.valueOf(i).strip() == dummyvar:
                    i.firstChild.data = lhsvar
            return [ rhsfmla ]
        else:
            assert False, 'ERROR: Unreachable code'
    assert xmlnode.tagName == 'INITDECL', 'ERROR: Initialization not as expected'
    simpledefs = xmlnode.getElementsByTagName("SIMPLEDEFINITION")
    fmla = []
    for i in simpledefs:
        fmla.extend( simpledef2fmlalist(i) )
    return fmla

def handleBasemodule(basemod):
    """populate the data-structure"""
    inputs = HSalPreProcess2.getInputs(basemod)
    cbody = basemod.getElementsByTagName("GUARDEDCOMMAND")
    assert len(cbody) == 1, 'ERROR: Expecting exactly 1 guarded command in module'
    i = cbody[0]
    assert isCont(i), 'ERROR: Expecting exactly 1 continuous transition in module'
    (guard, varlist, A, b) = handleGuardedCommand(i)
    (mlist, elist, qlist) = HSalRelAbsCons.Ab2eigen(varlist, A, b, inputs)
    cds = CDS( varlist )
    cds.setAb( A, b )
    cds.setmodeinv( guard )
    cds.setmulti( mlist )
    cds.seteigen( elist )
    cds.setquad( qlist )
    cds.setinputs( inputs )
    # now I need to set the initial state
    init = basemod.getElementsByTagName("INITDECL")
    assert len(init) > 0, 'Error: Need INITIALIZATION'
    cds.setinit( init2Formula( init[0] ) )
    return cds

def prop2modpropExpr(ctxt, prop):
    "create and output the shared data-structure"
    # first, find the assertiondecl for prop in ctxt
    # get list of all assertiondeclarations in ctxt
    modulemodels = None
    adecls = ctxt.getElementsByTagName("ASSERTIONDECLARATION")
    assert len(adecls) > 0, 'ERROR: Property {0} not found in input HSal file'.format(prop)
    for i in adecls:
        propName = HSalXMLPP.getNameTag(i, 'IDENTIFIER')
        if propName == prop:
            modulemodels = HSalXMLPP.getArg(i, 3)
            break
    assert modulemodels != None, 'ERROR: Property {0} not found in input HSal file'.format(prop)
    # second, extract modulename and property expression
    modulename = None
    try:
        modulename = HSalXMLPP.getNameTag(modulemodels, 'MODULENAME')
    except IndexError:
        print 'ERROR: Expecting MODULENAME inside property {0}'.format(prop)
        sys.exit(1)
    propExpr = HSalXMLPP.getArg(modulemodels, 2)
    assert propExpr != None, 'ERROR: Failed to find property expression'
    # Now, I have modulename and propExpr
    # Next, find module modulename from the list of ALL basemodules...
    moddecl = None
    moddecls = ctxt.getElementsByTagName("MODULEDECLARATION")
    for i in moddecls:
        tmp = HSalXMLPP.getArg(i, 1)
        assert tmp != None, 'ERROR: Module declaration has no NAME ??'
        identifier = HSalXMLPP.valueOf(tmp).strip()
        if identifier == modulename:
            moddecl = i
            break
    assert moddecl != None, 'ERROR: Module {0}, referenced in property {1}, not found'.format(modulename, prop)
    # Now, I have moddecl and propExpr
    basemod = HSalXMLPP.getArg(moddecl, 3)
    assert basemod != None, 'ERROR: Module {0} is not a base module'.format(modulename)
    # Now I have basemod and propExpr; check if propExpr is G( inv )
    assert propExpr.tagName == 'APPLICATION', 'ERROR: Property must be of the form G(inv)'
    functionName = HSalXMLPP.valueOf( HSalXMLPP.getArg(propExpr, 1) ).strip()
    assert functionName == 'G', 'ERROR: Property must be of the form G(inv)'
    invExpr = HSalXMLPP.getArg( HSalXMLPP.getArg(propExpr, 2), 1)
    return (basemod, invExpr)

def handleContext(ctxt, prop):
    (basemod, propExpr) = prop2modpropExpr(ctxt, prop)
    # basemod and propExpr are XML nodes
    # basemod -> (x, init, dynamics)
    cds = handleBasemodule(basemod)
    cds.setsafe( propExpr )
    return cds 

def hxml2cegar(xmlfilename, prop, depth = 4):
    basename,ext = os.path.splitext(xmlfilename)
    dom = xml.dom.minidom.parse(xmlfilename)
    setDom(dom)
    # standard pre-processing for HybridSal models
    ctxt = HSalPreProcess.handleContext(dom)
    ctxt = HSalPreProcess2.handleContext(ctxt)
    # 
    mydatastructure = handleContext(ctxt, prop)
    print "Cegar: First phase of initialization of data-structures is complete"
    print mydatastructure.toStr()
    pass
    print "Cegar: Second phase of CEGAR terminated"
    return 0

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
        Copyright 2012 Ashish Tiwari, SRI International.
-------------------------------------------------------------------------
"""

def main():
    depth = 4
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
    xmlfilename = HSalRelAbsCons.hsal2hxml(filename)
    ans = hxml2cegar(xmlfilename, prop, depth)
    return ans

if __name__ == '__main__':
    main()

