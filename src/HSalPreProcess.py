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

exprs2poly = polyrep.exprs2poly
#createNodeAnd = polyrep2XML.createNodeAnd
#createNodeInfixApp = polyrep2XML.createNodeInfixApp
#createNodeTagChild = polyrep2XML.createNodeTagChild
#createNodeTagChild2 = polyrep2XML.createNodeTagChild2
#createNodeTime = polyrep2XML.createNodeTime
#createNodePnew = polyrep2XML.createNodePnew
#createNodePold = polyrep2XML.createNodePold
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
    return createNodeTagChildn("NAMEEXPR", [ dom.createTextNode( val ) ])

def handleContext(ctxt):
    cdecls = ctxt.getElementsByTagName("CONSTANTDECLARATION")
    defs = dict();
    for i in cdecls:
        varName = HSalXMLPP.getNameTag(i, "IDENTIFIER")
        # print HSalXMLPP.getNameTag(i, "TYPENAME")
        varValueInXML = HSALXMLPP.getArg(i, 4)
        # get all NAMEEXPR in varValueInXML; see if its textvalue == varName; replace by varExpr
        nameexprs = varValueInXML.getElementsByTagName("NAMEEXPR")
        for j in nameexprs:
        varExpr = createNodeTag("NUMERAL", varValueStr)
        varValueInXML.replace
        # print polyrep.expr2poly(varValueInXML)
        defs[varName] = varValue
        # get all NAMEEXPR in the document; see if their textvalue == above; replace
    return ctxt
# ********************************************************************

if __name__ == '__main__':
    main()

