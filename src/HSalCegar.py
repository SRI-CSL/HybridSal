# I did sudo aptitude install python-glpk
# import sys
# sys.path.append('/usr/lib/python-support/python-glpk/python2.6')
# import glpk
# But it is not so user-friendly; so I tried to install pyglpk, by first
# doing sudo aptitude install libc6-dev-i386
# (becos when I run make on softwares/pyglpk-0.3/ I got an error), but didn't work out.
# Now, I will just use the raw python-glpk connection; and not pyglpk

import xml.dom.minidom
import sys	# for sys.argv[0]
import HSalExtractRelAbs
import polyrep # internal representation for expressions
import HSalXMLPP
import os.path
import HSalPreProcess
import HSalPreProcess2
from xmlHelpers import *
import HSalRelAbsCons
import copy
#import polyrep2XML

simpleDefinitionLhsVar = HSalExtractRelAbs.SimpleDefinitionLhsVar
isCont = HSalExtractRelAbs.isCont

# def mystr(k):
    # """return floating value k as a string; str(k) uses e notation
       # use 8 decimal places"""
    # return '{0:.8f}'.format(k)
# ********************************************************************

# class - Cont. Dyn. Sys;
# types of fields are as follows:
# safe, init, modeinv: DNF = objects of class DNF = list of REGIONS
# Region = list of atoms
# atom = Atom class = {'p':poly,'op':op} where poly = list of monomials
# monomial = [c {'x':1,'y':2}] denotes c*x*y^2
# eigen = list of (eigenvector,eigenvalue) pairs where eigenvector = poly
# multi = list of (poly, rate) pairs
# quad = list of (poly1, poly2, a, b) tuples s.t. poly1dot = a*poly1-b*poly2; poly2dot=b*poly1+a*poly2
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
    def getmodeinv(self):
        return self.modeinv
    def getsafe(self):
        return self.safe
    def getinit(self):
        return self.init
    def geteigen(self):
        return self.eigen
    def getmulti(self):
        return self.multi
    def getquad(self):
        return self.quad
    def toStr(self):
         out = 'CDS:\n x = {0},'.format(self.x)
         out += '\n init = '
         out += '{0},'.format( self.init.tostr() ) 
         out += '\n A = {0},\n b = {1},'.format(self.A, self.b, self.safe)
         # out += '\n safe = {0},'.format(self.safe.toxml())
         out += '\n safe = {0},'.format( self.safe.tostr() )
         out += '\n modeinv = {0},'.format( self.modeinv.tostr() )
         out += '\n inputs  = {0},'.format(self.inputs)
         out += '\n\n eigen = {0},'.format(self.eigen)
         out += '\n multi = {0},'.format(self.multi)
         out += '\n quad = {0},'.format(self.quad)
         return out
    # d = dict from 'A1', 'A2', 'b1', 'b2', 'x', 'y' to values

class Atom:
    def __init__(self,p,op):
        self.p = p
        self.op = op
    op_neg = {'<':'>=','<=':'>','>':'<=','>=':'<','=':'!=','!=':'='}
    def neg(self):
        '''negate atom; for e.g. p > 0 to p <= 0'''
        self.op = self.op_neg[self.op]
    def tostr(self):
        '''return string representing p > 0'''
        return '{0} {1} 0'.format( poly2str( self.p), self.op )
    def get_poly(self):
        return self.p
    def get_op(self):
        return self.op
    def deep_copy(self):
        newp = self.get_poly()
        ans = Atom(copy.deepcopy(newp), self.op)
        return ans

class DNF:
    class Region:
        def __init__(self,r=[]):
            self.r = r
        def get(self):
            return self.r
        @staticmethod
        def true():
            return DNF.Region([])
        def isTrue(self):
            return self.r == []
        def get_atoms(self):
            return self.r
        def and_atom(self, atom ):
            self.r.append( atom )
        def and_region(self, r2):
            self.r.extend(r2.r)
        def deep_copy(self):
            ans = DNF.Region()
            for i in self.get_atoms():
                ans.and_atom( i.deep_copy() )
            return ans
        def over_approx(self, directions, other_constraints):
            '''given a Region, return a DNF that over-approximates it 
               in the given directions'''
            ans = {}
            for d in directions:
                lb = lp_minimize(d, self.r, other_constraints)
                ub = lp_maximize(d, self.r, other_constraints)
                ans[d] = (lb, ub)
            return ans
        def tostr(self):
            ans = ''
            first = True
            for i in self.r:
                sep = ' AND' if not(first) else ''
                first = False
                ans += '{0} {1}'.format(sep, i.tostr())
            return ans
    def __init__(self, fmla=False):
        self.fmla = fmla if fmla else []
    @staticmethod
    def true():
        return DNF([ DNF.Region.true() ])
    @staticmethod
    def false():
        return DNF()
    @staticmethod
    def atom2region(atom):
        return DNF.Region([ atom ])
    @staticmethod
    def atom2dnf(atom):
        return DNF( [ DNF.atom2region(atom) ] )
    @staticmethod
    def region2dnf(region):
        return DNF( [ region ] )
    def get_regions(self):
        return self.fmla
    def free(self):
        del self.fmla 
    def or_atom(self, atom):
        self.fmla.append( DNF.atom2region(atom) )
    def or_region(self, region):
        self.fmla.append( region )
    def and_atom(self, atom):
        for f in self.fmla:
            f.and_atom( atom )
    def neg_conj(f):
        ans = DNF.false()
        for i in f:
            i.neg()
            ans.or_atom(i)
        return ans
    def deep_copy(self):
        ans = DNF()
        for i in self.get_regions():
            ans.or_region( i.deep_copy() )
        return ans
    def neg(self):
        '''return not(f)'''
        def neg_conj(f):
            ans = DNF.false()
            for i in f.get_atoms():
                i.neg()
                ans.or_atom(i)
            return ans
        ans = DNF.true()
        for f in self.fmla:
            notf = neg_conj(f)
            ans.and_dnf( notf )
            notf.free()
        del self.fmla
        self.fmla = ans.fmla
    @staticmethod
    def copy_region(region):
        return DNF.Region( list(region.get()) )
    def and_dnf(self, dnf2):
        "self := self and dnf2"
        f1,f2 = self.fmla, dnf2.fmla
        ans = DNF.false()
        for i in f1:
            for j in f2:
                # ij = list(i)
                ij = DNF.copy_region(i)
                # ij.extend(j)
                ij.and_region(j)
                ans.or_region(ij)
        del self.fmla
        self.fmla = ans.fmla
    def or_dnf(self, dnf2):
        self.fmla.extend(dnf2.fmla)
    def tostr(self):
        if self.fmla == []:
            return 'FALSE'
        elif self.fmla[0].isTrue():
            return 'TRUE'
        ans = ''
        first = True
        for i in self.fmla:
            sep = ' OR' if not(first) else ''
            first = False
            ans += '{0} {1}'.format(sep, i.tostr())
        return ans
    def over_approx(self, directions, other_constraints):
        '''over-approximation this dnf in the given directions:
           return a mapping 'over' from this DNF's regions to DNF s.t.
           over[region] = over_approx_region(region, directions)'''
        ans = {}
        for region in self.get_regions():
            ans[region] = region.over_approx(directions, other_constraints)
        return ans


def applyBOp(op, f1, f2):
    '''return f1 op f2, where op=OR or op=AND'''
    assert op in ['OR','AND']
    if op == 'OR':
        f1.or_dnf(f2)
        return f1
    else:
        f1.and_dnf(f2)
        return f1

def applyArithOp(op, e1, e2):
    '''return e1 op e2'''
    e = polyrep.polySub(e1,e2)
    return DNF.atom2dnf( Atom(p=e, op=op) )

def xml_fmla_2_dnf_fmla(fmla):
    assert fmla != None and (isinstance(fmla,list) or fmla.nodeType == fmla.ELEMENT_NODE), 'Error: expecting ELEMENT node'
    if isinstance(fmla, list):
        polyllL = [ xml_fmla_2_dnf_fmla(i) for i in fmla ]
        ans = DNF.true()
        for i in polyllL:
            ans = applyBOp('AND', ans, i)
        return ans
    elif fmla.localName == 'NAMEEXPR':
        bcst = HSalXMLPP.valueOf(fmla).strip()
        assert bcst in ['TRUE','FALSE'], 'Error: Boolean constant is not TRUE/FALSE?'
        return DNF.false() if bcst == "FALSE" else DNF.true()
    elif fmla.localName == 'APPLICATION':
        if fmla.getAttribute('INFIX') == 'YES':
            op = HSalXMLPP.valueOf( HSalXMLPP.getArg(fmla,1) ).strip()
            if op in ['AND','OR']: 
                fmla1 = xml_fmla_2_dnf_fmla( HSalXMLPP.appArg(fmla,1) )
                fmla2 = xml_fmla_2_dnf_fmla( HSalXMLPP.appArg(fmla,2) )
                return applyBOp(op, fmla1, fmla2)
            elif op in ['<','<=','>','>=','=']:
                fmla1 = polyrep.expr2poly ( HSalXMLPP.appArg(fmla,1), ignoreNext = True )
                fmla2 = polyrep.expr2poly ( HSalXMLPP.appArg(fmla,2), ignoreNext = True )
                return applyArithOp(op, fmla1, fmla2)
            else: 
                assert False, 'Error: Unknown op {0} in formula'.format(op)
        else:
            op = HSalXMLPP.valueOf( HSalXMLPP.getArg(fmla,1) ).strip()
            assert op in ['NOT'], 'Error: Unhandled bool connective {0}'.format(op)
            fmla1 = xml_fmla_2_dnf_fmla( HSalXMLPP.appArg(fmla,1) )
            fmla1.neg()
            return fmla1 
    else: 
        assert False, 'Error: Unknown tag {0} in formula'.format(fmla.localName)
 
def poly2str(poly):
    '''return string representing the polynomial'''
    def mono2str(mono):
        '''convert monomial to its string representation'''
        c = mono[0] if len(mono) > 0 else 0
        mu = mono[1] if len(mono) > 1 else {}
        ans = ''
        for (k,v) in mu.items():
            ans += '{0}'.format(k) if v==1 else '{0}^{1}'.format(k,v)
        ans = '{0}{1}'.format(c,ans) if c != 1 else ans
        return ans
    ans = ''
    first = True
    for i in poly:
        sep = ' +' if not(first) else ''
        first = False
        ans += '{0} {1}'.format(sep, mono2str(i))
    return ans

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
    def equal(c,d,tolerance=1e-4):
        return(abs(c-d) < tolerance)
    def dictKey(varlist, value):
        "Return key given the value"
        for var,index in varlist.iteritems():
            if index == value:
                return var
        return None
    def mk_cx(c,x):
        xindices = x.values()
        xindices.sort()
        n = len(xindices)
        cx = list()
        for i,v in enumerate(xindices):
            if not(equal(c[i], 0)):
                cx.append( [ c[i], { dictKey(x,v): 1} ] )
        return cx
    def mk_cxdye(vec,x,wec,y,const):
        cx = mk_cx(vec,x)
        dy = mk_cx(wec,y)
        cx.extend(dy)
        if not(equal(const,0)):
            cx.append( [const,{}] )
        return cx
    def elist_2_eig(elist):
        ans = [ (mk_cxdye(vec,x,wec,y,const),lamb) for ((vec,x,wec,y,const),lamb) in elist ]
        return ans
    def mlist_2_poly(mlist):
        multirateL = []
        for (c, x, rate) in mlist:
            yold = mk_cx(c, x)
            multirateL.append( (yold, rate) )
        return multirateL
    def qlist_2_poly(qlist):
        qcalls = []
        for ( (u,x,w1,y,c1), (v,x,w2,y,c2), a, d) in qlist: 
            nodePnew = mk_cxdye(u,x,w1,y,c1)
            nodeQnew = mk_cxdye(v,x,w2,y,c2)
            # CHECK: vec could be 0 vector and hence nodePnew could be None
            qcalls.append( (nodePnew,nodeQnew,a,d) )
        return qcalls
    inputs = HSalPreProcess2.getInputs(basemod)
    cbody = basemod.getElementsByTagName("GUARDEDCOMMAND")
    assert len(cbody) == 1, 'ERROR: Expecting exactly 1 guarded command in module'
    i = cbody[0]
    assert isCont(i), 'ERROR: Expecting exactly 1 continuous transition in module'
    (guard, varlist, A, b) = handleGuardedCommand(i)
    (mlist, elist, qlist) = HSalRelAbsCons.Ab2eigen(varlist, A, b, inputs)
    cds = CDS( varlist )
    cds.setAb( A, b )
    cds.setmodeinv( xml_fmla_2_dnf_fmla(guard) )
    cds.setmulti( mlist_2_poly(mlist) )
    cds.seteigen( elist_2_eig(elist) )
    cds.setquad( qlist_2_poly(qlist) )
    cds.setinputs( inputs )
    # now I need to set the initial state
    init = basemod.getElementsByTagName("INITDECL")
    assert len(init) > 0, 'Error: Need INITIALIZATION'
    cds.setinit( xml_fmla_2_dnf_fmla( init2Formula( init[0] ) ) )
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
    cds.setsafe( xml_fmla_2_dnf_fmla( propExpr) )
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
    safety_check(mydatastructure)
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

def main_aux(filename, prop, depth):
    xmlfilename = HSalRelAbsCons.hsal2hxml(filename)
    ans = hxml2cegar(xmlfilename, prop, depth)
    return ans

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
    return main_aux(filename, prop, depth)

# -----------------------------------------------------------------------------------
# Second Phase Algorithm:
# overinit = map from region (in init) to DNF;
# oversafe; overinv = same?
# for each region in Init: compute overapprox in eigen-directions; multi-directions
# we need a method to complete a DNF...
# e.g. x>0 or y>0 ---> x>0 AND y<=0 OR y>0 AND x<=0 OR x>0 AND y>0
# Then we need a method to compute an over-approx of a completed REGION
# for each overinitregion, overunsaferegion, we can check intersection
# we do this by computing time-bounds for possible intersection;
# then we can pick times in the MIDDLE...and compute Xn with EXACT unsafe...
# if it does; we can see if the corr. initial state is real/spurious and refine INIT-over
# if it doesn't; we refine unsafe-over
# refining algo: once you get a point; move it in all eigen-directions as long as it is
# spurious; get the most internal point ...we get n-factor multiplication...
# -----------------------------------------------------------------------------------
def poly2linear(d):
    "convert polynomial d to linear form"
    ans = {}
    for mono in d:
        c = mono[0]
        if len(mono[1])==0:
            ans['_const_'] = ans['_const_'] + c if ans.has_key('_const_') else c
        else:
            assert len(mono[1]) == 1, 'error: non-linear direction?'
            (var,power) = mono[1].items()[0]
            assert power==1, 'error: non-linear direction?'
            ans[var] = ans[var] + c if ans.has_key(var) else c 
    return ans

class Direction:
    def __init__(self, d, rate, description, buddy = None):
        '''d = [ [1,{x:1}],[2,{y:1}] ]'''
        self.d = poly2linear( d )
        self.rate = rate
        self.description = description
        self.buddy = buddy
    def get_vars(self):
        return self.d.keys()
    def tostr(self):
        ans = self.description
        for (k,v) in self.d.items():
            ans += ' + {0} {1}'.format(v,k)
        return  ans

class CDS_Reach:
    def __init__(self, cds):
        self.cds = cds
        self.over_init = None
        self.over_unsafe = None
        self.unsafe = cds.safe.deep_copy()
        self.unsafe.neg()
        self.directions = None
    def set_directions(self):
        self.directions = []
        for (vec,val) in self.cds.geteigen():
            self.directions.append( Direction(vec, val, 'eigen') )
        for (vec,val) in self.cds.getmulti():
            self.directions.append( Direction(vec, val, 'multi') )
        for (vec,wec,val1,val2) in self.cds.getquad():
            d =  Direction(wec, val2, 'quad2') 
            self.directions.append( d )
            self.directions.append( Direction(vec, val1, 'quad1', buddy=d) )
    def get_directions(self):
        return self.directions
    def set_over_init(self):
        self.over_init = self.cds.getinit().over_approx(self.directions,self.cds.getmodeinv())
    def set_over_unsafe(self):
        assert self.unsafe != None
        self.over_unsafe = self.unsafe.over_approx(self.directions,self.cds.getmodeinv())
    def set_all(self):
        self.set_directions()
        self.set_over_init()
        self.set_over_unsafe()
    def toStr(self):
        def over_tostr( dictOfdictOfpairs ):
            ans = ''
            for (k,v) in dictOfdictOfpairs.items():
                ans += '\n  {0}-> '.format(k.tostr())	# region 
                for (k1,v1) in v.items():
                    ans += '{0}:{1}, '.format(k1.tostr(),v1) # direction:(lb,ub)
            return ans
        ans = self.cds.toStr()
        ans += '\nDirections of interest:'
        for d in self.directions:
            ans += d.tostr()
        ans += '\nOverapprox of Init: {0}'.format(over_tostr(self.over_init))
        ans += '\nOverapprox of Unsafe: {0}'.format(over_tostr(self.over_unsafe))
        return ans

def safety_check(cds):
    cdsr = CDS_Reach(cds)
    cdsr.set_all()
    print cdsr.toStr()
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
def lp_minimize(direction, region, dnf_constraint):
    '''min direction s.t. region and dnf_constraint'''
    # let us ignore
    glpk.glp_set_obj_dir(prob, glpk.GLP_MIN)	# maximize or minimize
    return 0

def lp_maximize(direction, region, dnf_constraint):
    '''max direction s.t. region and dnf_constraint'''
    glpk.glp_set_obj_dir(prob, glpk.GLP_MAX)	# maximize or minimize
    return 0

def lp_optimize(x, direction, region, region1):
    constraints = region.get_atoms()
    constraints1 = region1.get_atoms()
    contraints.extend(constraints1)
    n = len(constraints)
    m = len(x)
    variables = x.keys()
    prob = glpk.glp_create_prob()
    glpk.glp_add_rows(prob, n)
    glpk.glp_add_cols(prob, m)
    for i in constraints:
        poly = i.get_poly()
        rowi = poly2linear(poly)
        op = i.get_op()
        assert op != '!=', 'error: cant handle  not-eq yet'
        gop = glpk.GLP_UP if op in ['<','<='] else (glpk.GLP_LO if op in ['>','>='] else glpk.FX)
        value = rowi['_const_'] if rowi.has_key('_const_') else 0
        index = constraints.index(i) + 1
        glpk.glp_set_row_bnds(prob, index, gop, value, value)
        l = len(rowi) + 1
        ind = glpk.intArray(l)
        val = glpk.doubleArray(l)
        j = 1
        for (k,v) in rowi:
            if k != '_const_':
                ind[j] = x[k]+1
                val[j] = v
            else:
                ind[j] = 0
                val[j] = 0
            j += 1
        glpk.glp_set_mat_row(prob, index, l, ind, val)
    # add optimization function....
    return prob
# -----------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------
if __name__ == '__main__':
    if 'test' in sys.argv:
        main_aux('../examples/Linear1.hsal', 'correct', 4)
        main_aux('../examples/Linear2.hsal', 'correct', 4)
        main_aux('../examples/Linear3.hsal', 'correct', 4)
        main_aux('../examples/Linear4.hsal', 'correct', 4)
        main_aux('../examples/Linear5.hsal', 'correct', 4)
        main_aux('../examples/Linear6.hsal', 'correct', 4)
        main_aux('../examples/Linear7.hsal', 'correct', 4)
    else:
        main()
# -----------------------------------------------------------------------------------

