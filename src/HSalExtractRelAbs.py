# Extract the relational abstraction from the HSal Model
# HSal model can contain relational abstractions inside them
# Each continuous transition can have an alternate description
# Here we just want to extract the alternate descriptions

# We need to take care of INITFORDECL and INVARDECL

# from xml.dom.minidom import parse, parseString
import xml.dom.minidom
import sys	# for sys.argv[0] and sys.stdout

def SimpleDefinitionLhsVar(defn):
    lhs = defn.getElementsByTagName("NEXTOPERATOR")[0]
    nameexpr = lhs.getElementsByTagName("NAMEEXPR")[0]
    return(nameexpr.childNodes[0].data)

def GuardedCommandLhsVar(gcmd):
    assgns = gcmd.getElementsByTagName("ASSIGNMENTS")
    if (assgns == None or len(assgns) == 0):
        return(0)
    defns = assgns[0].getElementsByTagName("SIMPLEDEFINITION")
    if (defns == None or len(defns) == 0):
        return(0)
    return SimpleDefinitionLhsVar(defns[0])

def isCont(gcmd):
    "Is this guarded command a continuous transition?"
    var = GuardedCommandLhsVar(gcmd)
    # print "Variable is %s" % var
    if var == 0:
        return(0)
    if var[-3:] == 'dot':
        return(1)

def handleTransDecl(tdecl):
    somecmds = tdecl.getElementsByTagName("SOMECOMMANDS")
    if somecmds == None or len(somecmds) == 0:
        return	# in this case, tdecl just has SIMPLEDEFINITIONS, so continue
    somecmds = somecmds[0]
    cmds = somecmds.childNodes
    for i in cmds:
        #if i.localName == "GUARDEDCOMMAND":
            #print "It is a guarded command"
        if i.localName == "MULTICOMMAND":
            # print "It is a multi command"
            gcmds = i.getElementsByTagName("GUARDEDCOMMAND")
            for j in gcmds:
                if (not(isCont(j))):
                    break
            if (j == None): 
                print "No abstraction found"
            else:
                somecmds.replaceChild(j, i)

def handleContext(ctxt):
    cbody = ctxt.getElementsByTagName("CONTEXTBODY")[0]
    mdecls = ctxt.getElementsByTagName("MODULEDECLARATION")
    # print 'Number of module declarations is %d\n' % mdecls.length
    for mdecl in mdecls:
        basemodule = mdecl.getElementsByTagName("BASEMODULE")
        if (basemodule == None or len(basemodule) == 0):
            print 'Module compositions are being abstracted compositionally\n'
        else:
            ldecls = basemodule[0].getElementsByTagName("LOCALDECL")
            invardecl = basemodule[0].getElementsByTagName("INVARDECL")
            initfmla = basemodule[0].getElementsByTagName("INITFORDECL")
            transdecl = basemodule[0].getElementsByTagName("TRANSDECL")
            # print 'Number of local declarations is %d' % ldecls.length
            # print 'Number of invar declarations is %d' % invardecl.length
            # print 'Number of initfmla is %d' % initfmla.length
            # print 'Number of transdecl is %d' % transdecl.length
            handleTransDecl(transdecl[0])
        # print mdecl.toxml()
    return ctxt

def extractRelAbs(dom, filePtr=sys.stdout, ptf=False):
    dom = handleContext(dom)	# Destructive
    if ptf:
      print >> filePtr, dom.toxml() 
    return dom

def main():
    dom = xml.dom.minidom.parse(sys.argv[1])
    dom = handleContext(dom)
    print dom.toxml() 

if __name__ == "__main__":
    main()

