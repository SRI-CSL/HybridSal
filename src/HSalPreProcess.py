# Preprocess .hybridsal (.hsal) file to remove constant declarations

# Input:  Hybrid Sal model in XML syntax
# Output: Hybrid Sal model in XML syntax
# All constant declarations in input will be removed.

# Caveat: All constant declarations should indeed evaluate to CONSTANTS

# Algorithm:
# collect all constant decls inside the CONTEXTBODY
#    <CONSTANTDECLARATION PLACE="6 1 6 15">
#      <IDENTIFIER PLACE="6 1 6 2">M</IDENTIFIER>
#      <VARDECLS></VARDECLS>
#      <TYPENAME PLACE="6 4 6 8">REAL</TYPENAME>
#      <NUMERAL PLACE="6 11 6 15">1769</NUMERAL>
#    </CONSTANTDECLARATION>
# or of the following form
#    <CONSTANTDECLARATION PLACE="16 1 16 31">
#      <IDENTIFIER PLACE="16 1 16 3">R1</IDENTIFIER>
#      <VARDECLS></VARDECLS>
#      <TYPENAME PLACE="16 5 16 9">REAL</TYPENAME>
#      <APPLICATION PLACE="16 12 16 31" INFIX="YES">
#        <NAMEEXPR PLACE="16 19 16 20">/</NAMEEXPR>
#        <TUPLELITERAL PLACE="16 12 16 31">
#          <APPLICATION PLACE="16 12 16 19" INFIX="YES">
#            <NAMEEXPR PLACE="16 15 16 16">*</NAMEEXPR>
#            <TUPLELITERAL PLACE="16 12 16 19">
#              <NAMEEXPR PLACE="16 12 16 15">Rci</NAMEEXPR>
#              <NAMEEXPR PLACE="16 16 16 19">Rsi</NAMEEXPR>
#            </TUPLELITERAL>
#          </APPLICATION>
#          <APPLICATION PLACE="16 20 16 31" INFIX="YES" PARENS="1">
#            <NAMEEXPR PLACE="16 22 16 23">-</NAMEEXPR>
#            <TUPLELITERAL PLACE="16 21 16 30">
#              <NUMERAL PLACE="16 21 16 22">1</NUMERAL>
#              <APPLICATION PLACE="16 23 16 30" INFIX="YES">
#                <NAMEEXPR PLACE="16 26 16 27">*</NAMEEXPR>
#                <TUPLELITERAL PLACE="16 23 16 30">
#                  <NAMEEXPR PLACE="16 23 16 26">Rci</NAMEEXPR>
#                  <NAMEEXPR PLACE="16 27 16 30">Rcr</NAMEEXPR>
#                </TUPLELITERAL>
#              </APPLICATION>
#            </TUPLELITERAL>
#          </APPLICATION>
#        </TUPLELITERAL>
#      </APPLICATION>
#    </CONSTANTDECLARATION>

import xml.dom.minidom
import sys	# for sys.argv[0]
import polyrep # internal representation for expressions
import os.path
import shutil
import subprocess
import HSalXMLPP
import polyrep

#createNodeAnd = polyrep2XML.createNodeAnd
#createNodeInfixApp = polyrep2XML.createNodeInfixApp
#createNodeTagChild = polyrep2XML.createNodeTagChild
#createNodeTagChild2 = polyrep2XML.createNodeTagChild2
#dictKey = polyrep2XML.dictKey

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
def createNodeTagChildn(tag, childNodes):
    global dom
    node = dom.createElement(tag)
    for i in childNodes:
        node.appendChild(i)
    return node

def createNodeTag(tag, val):
    global dom
    return createNodeTagChildn(tag, [ dom.createTextNode( val ) ])

def replaceNameexprsNumerals(ufu, xmlnode):
    """Replace all nameexprs in xmlnode by their numeral value from ufu"""
    if xmlnode.localName == 'NAMEEXPR':
        nameexprs = [ xmlnode ]
    else:
        nameexprs = xmlnode.getElementsByTagName("NAMEEXPR")
    # print "Found so many NAMEEXPRSs to possibly replace"
    # print len(nameexprs)
    for j in nameexprs:
        v = HSalXMLPP.valueOf(j)
        if v in ufu:
            fv = ufu[v]
            fvXML = createNodeTag("NUMERAL", fv)
            # replace j by fvXML 
	    jParent = j.parentNode
            jParent.replaceChild(fvXML, j)
            if j == xmlnode:
                xmlnode = fvXML
    return xmlnode

def handleContext(ctxt):
    global dom
    dom = ctxt
    cdecls = ctxt.getElementsByTagName("CONSTANTDECLARATION")
    defs = dict();
    for i in cdecls:
        uStr = HSalXMLPP.getNameTag(i, "IDENTIFIER")
        # print HSalXMLPP.getNameTag(i, "TYPENAME")
        fuXML = HSalXMLPP.getArg(i, 4)
        # get all NAMEEXPR in fuXML; replace by f(nameexpr)
        fuXML = replaceNameexprsNumerals(defs, fuXML)
        # Now evaluate the expression and check if it is a constant.
        # print polyrep.expr2poly(varValueInXML)
        fuPolyrep =  polyrep.expr2poly(fuXML)
        if polyrep.isConstant(fuPolyrep):
            value = polyrep.getConstant(fuPolyrep)
            defs[uStr] = format(value,'.1g')  # ASHISH: CHECK LATER
        else:
            print fuXML.toxml()
            print fuPolyrep
            print "ERROR: Preprocessor can't eliminate constant decls"
            return ctxt
    print "All constant decls are indeed constants"
    # get all NAMEEXPR in the document; see if their textvalue == above; replace
    ctxt = replaceNameexprsNumerals(defs, ctxt)
    return ctxt
# ********************************************************************

if __name__ == '__main__':
    main()

