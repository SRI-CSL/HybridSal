# Preprocess .hybridsal (.hsal) file to remove INITFORMULA and INVARIANT

# Input:  Hybrid Sal model in XML syntax
# Output: Hybrid Sal model in XML syntax
# INITFORMULA and INVARIANT will be removed.

# Algorithm:
# Adding support for INVARIANT and INITFORMULA
# INITFORMULA \phi will be replaced by INITIALIZATION [ \phi --> ]
# INVARIANT \phi will be deleted and each guarded command with
# get \phi AND \phi' in its guard.

# For each BASEMODULE, replace its two children:
# <INVARDECL PLACE="25 1 27 59">
#  <APPLICATION PLACE="26 116 27 59" INFIX="YES">
#   <NAMEEXPR PLACE="26 116 26 119">AND</NAMEEXPR>
#   <TUPLELITERAL PLACE="26 4 27 59">
#    ...
# </INVARDECL>
# Replace EACH child of TRANSDECL 
# if child is <GUARDEDCOMMAND><GUARD>\psi</GUARD><ASSIGNMENTS.../> 
# replace its GUARD by \psi AND \phi AND \phi'

# <INITFORDECL> SOMETHING </INITFORDECL>
# Replace by
# <INITDECL><SOMECOMMANDS><GUARDEDCOMMAND><GUARD> SOMETHING ...</INITDECL>

import xml.dom.minidom
import sys	# for sys.argv[0]
import os.path
import shutil
import subprocess
import HSalXMLPP
import xmlHelpers

createNodeTagChildn = xmlHelpers.createNodeTagChildn
createNodeAnd = xmlHelpers.createNodeAnd
getArg = HSalXMLPP.getArg

# ********************************************************************
# Main Function
# ********************************************************************
def moveIfExists(filename):
    if os.path.isfile(filename):
        print "File %s exists." % filename,
        print "Renaming old file to %s." % filename+"~"
        shutil.move(filename, filename + "~")

def main():
    global dom
    filename = sys.argv[1]
    if not(os.path.isfile(filename)):
        print "File does not exist. Quitting."
        return 1
    basename,ext = os.path.splitext(filename)
    if ext == '.hxml':
        xmlfilename = filename
    elif ext == '.hsal':
        xmlfilename = basename + ".hxml"
        subprocess.call(["hybridsal2xml/hybridsal2xml", "-o", xmlfilename, filename])
        if not(os.path.isfile(xmlfilename)):
            print "hybridsal2xml failed to create XML file. Quitting."
            return 1
    else:
        print "Unknown file extension; Expecting .hsal or .hxml; Quitting"
        return 1
    dom = xml.dom.minidom.parse(xmlfilename)
    newctxt = handleContext(dom)
    moveIfExists(xmlfilename)
    with open(xmlfilename, "w") as fp:
        print >> fp, newctxt.toxml()
    print "Created file %s containing the preprocessed model (XML)" % xmlfilename
    filename = basename + ".hsal.preprocessed"
    moveIfExists(filename)
    with open(filename, "w") as fp:
        HSalXMLPP.HSalPPContext(newctxt, fp)
    print "Created file %s containing the preprocessed model (HSal)" % filename
    return 0

# ********************************************************************
# Functions for handling CONTEXT 
# ********************************************************************
def handleContext(ctxt):
    xmlHelpers.setDom(ctxt)
    basemods = ctxt.getElementsByTagName("BASEMODULE")
    for i in basemods:
        handleBasemodule(i)
    return ctxt

def handleBasemodule(basemod):
    handleBasemoduleInitForDecl(basemod)
    handleBasemoduleInvarDecl(basemod)

def handleBasemoduleInitForDecl(basemod):
    """<INITFORDECL> PHI </INITFORDECL>
       is replaced by
       <INITDECL><SOMECOMMANDS><GUARDEDCOMMAND><GUARD> PHI ...</INITDECL>"""
    initfor = basemod.getElementsByTagName("INITFORDECL")
    assert len(initfor) <= 1
    if len(initfor) == 0:
        return
    initfordecl = initfor[0]
    # phi = initfordecl.firstChild
    phi = getArg(initfordecl, 1)
    guard = createNodeTagChildn("GUARD", [ phi ])
    gc = createNodeTagChildn("GUARDEDCOMMAND", [ guard ])
    sc = createNodeTagChildn("SOMECOMMANDS", [ gc ])
    initdecl = createNodeTagChildn("INITDECL", [ sc ])
    basemod.replaceChild(newChild=initdecl, oldChild=initfordecl)
    return

def makePrime(expr, basemod):
    """Replace var by var' in expr"""
    # first get the types of all variables from dom
    vdecls = basemod.getElementsByTagName('VARDECL')
    allRealVars = list()
    for i in vdecls:
        varnames = i.getElementsByTagName('IDENTIFIER')
        typenames = i.getElementsByTagName('TYPENAME')
        if len(typenames) > 0:
            typename = HSalXMLPP.valueOf(typenames[0])
            assert len(varnames) > 0
            varname = HSalXMLPP.valueOf(varnames[0])
            if typename == 'REAL':
                allRealVars.append(varname)
    # now allRealVars has names of all REAL variables in the CONTEXT
    ans = expr.cloneNode(True)
    # get all NAMEEXPR nodes; if its parent is TUPLELITERAL then add prime to it
    nameexprs = ans.getElementsByTagName("NAMEEXPR")
    for i in nameexprs:
        name = HSalXMLPP.valueOf(i)
        if not(name in allRealVars): 	# if name in ['TRUE', 'FALSE']:
            continue
        parentNode = i.parentNode
        if parentNode.tagName == 'NEXTOPERATOR': 	# if name in ['TRUE', 'FALSE']:
            continue
        icopy = i.cloneNode(True)
        primeVar = xmlHelpers.createNodeTagChild("NEXTOPERATOR", icopy)
        parentNode.replaceChild(oldChild=i, newChild=primeVar)
    return ans

def handleBasemoduleInvarDecl(basemod):
    """<INVARDECL> \phi </INVARDECL> is removed and 
       Replace EACH child of TRANSDECL:
       if child is <GUARDEDCOMMAND><GUARD>\psi</GUARD><ASSIGNMENTS.../> 
       replace its GUARD by \psi AND \phi AND \phi' """
    invardecls = basemod.getElementsByTagName("INVARDECL")
    assert len(invardecls) <= 1
    if len(invardecls) == 0:
        return
    invardecl = invardecls[0]
    # phi = invardecl.firstChild
    phi = getArg(invardecl, 1)
    if phi == None:
        print "ERROR: INVARIANT can not be EMPTY; Expression expected"
        return
    phiPrime = phi.cloneNode(True)
    phiPrime = makePrime(phiPrime, basemod)
    phiPhi = createNodeAnd([ phi, phiPrime ])
    tdecls = basemod.getElementsByTagName("TRANSDECL")
    assert len(tdecls) == 1
    tdecl = tdecls[0]
    gcs = tdecl.getElementsByTagName("GUARDEDCOMMAND")
    for i in gcs:
        guard = getArg(i,1)
        psi = getArg(guard, 1)
        psiPhi = createNodeAnd([ psi, phiPhi.cloneNode(True) ])
        newguard = createNodeTagChildn("GUARD", [ psiPhi ])
        i.replaceChild(oldChild=guard, newChild=newguard)
    basemod.removeChild(invardecl)
    return
# ********************************************************************

if __name__ == '__main__':
    main()

