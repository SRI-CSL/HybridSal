#!/usr/bin/python

import xml.dom.minidom
import os.path
import sys
import subprocess

import polyrep # internal representation for expressions
import HSalXMLPP
import HSalExtractRelAbs

#These helper functions need to separated out to a common file
import HSalRelAbsCons
from xmlHelpers import *

import numpy
import scipy
from scipy import linalg

exprs2poly = polyrep.exprs2poly
simpleDefinitionLhsVar = HSalExtractRelAbs.SimpleDefinitionLhsVar
isCont = HSalExtractRelAbs.isCont

# ********************************************************************
# The dictionary containing the plant - frequency mapping,
# populated by parseSchedule() given the respective file
# ********************************************************************
schedDict = {}
scheduleFileName = "./sched"
intermedFile = "./intermed.sal"

def parseSchedule():
    with open(scheduleFileName, "r") as fp:
      schedStr = fp.read()
    schedList = schedStr.rsplit('\n')
    for i in schedList[:-1]:
      schedPeriodMap = i.rsplit(' ')
      if len(schedPeriodMap) == 2:
        plantName = schedPeriodMap[0]
        samplingPeriod = float(schedPeriodMap[1])
        schedDict[plantName] = samplingPeriod
        print '\nSampling Period = ' + str(samplingPeriod)
      else:
        print "error: incorrect format of sched"
        print "correct format::"
        print "plant_name<space>freq<\\n>"
        print "plant_name freq"
        print "..."
        print "plant_name freq"
    return schedDict


def getT(plantName):
  #plant name in the schedule file should be the same as the module name in 
  #the hybridSAL description
  schedDict = parseSchedule()
  try:
    return schedDict[plantName]
  except:
    print "error: plant %s not found in sched file" %plantName

def isNumZero(x):
  #numerical tolerance to handle floating point issues
  numTol = pow(numpy.e,-5)
  if abs(x) <= numTol:    
    return True
  else:
    return False

#str(float) if non zero
def floatToStr(x):
  if isNumZero(x):
    return ''
  else:
    return str(x)

#returns string of (coeff*var) only if coeff is not zero, else returns ''
#s is unused
def coeffStr(c,v,s=''):
  if isNumZero(c):
    return ''
  elif c == 1.0:
    return '+ '+v
  else:
    return '+ '+str(c)+"*"+v

#get the element at row r and column c from a matrix
def getMatE(mat, r, c):
  tmpArr = numpy.array(mat)
  return tmpArr[r][c]

# varlist
# eigen vector array where each column comprises of an eigen vector
# array of eigen values
def convertToSal2(varlist, evsMatT, ls, D, t):
  n = len(ls)
  if n != len(varlist):
    print 'length of eigen vectors don\'t the length of X !!?? '
  #each element of this nested list is an eigen vector
  evsTL = evsMatT.tolist()
  i = 0
  for eigV in evsTL:
    if D[i] == numpy.inf or D[i] == -numpy.inf:
      i = i + 1
      continue
    pdot = ''
    for var in varlist:
      #using the varlist indexing get the coefficient(ev component)
      #from the eigen vector
      vc = eigV[varlist[var]]
      pdot = pdot + coeffStr(vc,var+'\' ')
    elt = pow(numpy.e,t*ls[i])
    p = ''
    for var in varlist:
      vc = eigV[varlist[var]]
      p = p + coeffStr(vc,var)
    pd = '(' + p + '+ ' + str(D[i]) + ')'
    rel = pdot + '= ' + coeffStr(elt,pd) + '\n'
    i = i + 1
    print rel
#DEAD
def plantRetType(varlist):
  s = '% plant return type\nA record of all plant output variables\n'
  s +='rec:TYPE = [#'
  i=0  
  for var in varlist:
    s += var
    if i == len(varlist):
      s+=':REAL'
    else:
      s+=':REAL,'
      #];'
#  for var in varlist:
    
def convertToSalOld(varlist, eAT):
#  plantRetType(varlist)
#  exit(0)
  s = ''
  s += 'plant_mode_1 (prev_plant_state) : plant_ret =\n'
  s += '(#\n'

  for var in varlist:
    s += var + ' := '
    idx = varlist[var]
    eATList = (eAT.tolist())
    eATRow = eATList[idx]
    for var in varlist:
      idx2 = varlist[var]
      newVarName = 'prev_plant_state.' + var
      s += coeffStr(eATRow[idx2],newVarName)
    s += '\n'
  s += '#)'
  return s

def formatRelAbs(varlist, eAT):
  relAbs = {}
  for var in varlist:
    RHS = []
    idx = varlist[var]
    eATList = (eAT.tolist())
    eATRow = eATList[idx]
    for var2 in varlist:
      idx2 = varlist[var2]
      cx = (eATRow[idx2],var2)
      RHS.append(cx)
      #s = coeffStr(eATRow[idx2],var2)
    relAbs[var] = RHS
  return relAbs


def convertToSal(varlist, eAT):
  s = ''
  for var in varlist:
    s += var + '\' = '
    idx = varlist[var]
    eATList = (eAT.tolist())
    eATRow = eATList[idx]
    for var2 in varlist:
      idx2 = varlist[var2]
      s += coeffStr(eATRow[idx2],var2)
    s += '\n'
  return s

def matrixExp(matA,t):
  matAT = matA * t
  eAT = scipy.linalg.expm(matAT) #using Pade approximation, default order = 7
  print "Abstraction Matrix"
  print matAT
  print ""
  #get X(0)
  #X0 = [0.0 for i in range(len(initVarDict))]
  #for var in varlist:
  #  X0[varlist[var]] = initVarDict[var]
  #X0 = mat(X0)
  #X = eAT* X0
#  guard = HSalXMLPP.getArg(guard,1)
#  absgc = absGuardedCommandAux(varlist,A,b)
#  absguardnode = createNodeInfixApp('AND',guard,absgc)
#  absguard = createNodeTagChild('GUARD',absguardnode)
  # absassigns = assigns.cloneNode(True)
#  absassigns = absAssignments(varlist)
  return eAT


def detectDupEig(evl):
  if mylist:
    mylist.sort()
    last = mylist[-1]
    for i in range(len(mylist)-2, -1, -1):
      if last == mylist[i]:
        del mylist[i]
      else:
        last = mylist[i]

#     Xdot = Ax + B
#     Pdot = ,\P
# ==> P(t) = e^(,\*t) * P(0)
#     where P = (CT)X + D
#     where D = (CT)B/,\, where C is the eigen vector of A and CT = transpose(C)

def timedRelAbs(varlist,matA,matB,t):
  #complex eigen vals
  complx_ls = []
  #real eigen vals
  real_ls = []
  #purely imaginary eigen vals
  imag_ls = []
  #count of zero eigen vals
  zc = 0
  matAT = matA.getT()
  ls,evs = linalg.eig(matAT)
  for li in ls:
    if isNumZero(li.imag) and isNumZero(li.real):
      print 'warning: one eigen value ~ 0!'
      zc = zc + 1
    elif isNumZero(li.imag) and not isNumZero(li.real):
      real_ls.append(li.real)
    elif not isNumZero(li.imag) and isNumZero(li.real):
      imag_ls.append(li.imag)
    #elif li.imag != 0 and li.real != 0:
    else:
      complx_ls.append(li)
      print 'warning:complex eigen value found!'
  
  #detectDupEig()

#  if len(complx_ls) == 0 and len(imag_ls) == 0:    
#    convertToSal(varlist,evs)
  print 'varlist'
  print varlist
  print 'matA'
  print matA
  print 'matB'
  print matB

  print '========================'
  print 'eigen vals'
  print ls
  print 'eigen vectors'
  print evs
  print '========================'

#calculate D = (CT)B/(,\)
#for that we find CT[i]
  #D is a list of scalars (CT * B)/(,\)
  evsMatT = (scipy.mat(evs)).getT()
  n = len(ls)
  D = [0.0 for i in range(n)]
  for i in range(n):
    tmpMat = (evsMatT[i]*matB)/ls[i]
    D[i] = getMatE(tmpMat,0,0)
    if D[i] == numpy.inf or D[i] == -numpy.inf:
      print 'warning: D = nz/(,\=0) \n will ommit eqn'
    elif numpy.isnan(D[i]):
      print 'warning D = 0/0, assigning D = 0'
      D[i] = 0.0
    else:
      pass
    
#    if isNumZero(tmp) and isNumZero(ls[i]):
#      print 'warning D = 0/0, assigning D = 0'
#      D[i] = 0
#    elif not isNumZero(tmp) and isNumZero(ls[i]):
#      print 'warning: D = nz/(,\=0) \n will ommit eqn'
#      D[i] = 
#    else:
#      D[i] = tmp/ls[i]

  #D = [evsMatT[i]*matB/ls[i] for i in range(n)]
  convertToSal2(varlist, evsMatT, ls, D, t)

def writeIntermedFile(relAbs, varTypeDict):
  hdr = 'IMF\n'
  tl = '\nEND\n'
  with open(intermedFile, "w") as fp:
#    ipStr = [varTypeDict['inputs'][i] for i in varTypeDict['inputs']]
    ipStr = ''
    opStr = ''
    for var in varTypeDict['inputs']:
      ipStr += var + '\n'
    for var in varTypeDict['outputs']:
      opStr += var + '\n'
    s = hdr
    s += '\ninputs:\n' + ipStr
    s += '\noutputs:\n' + opStr
    s += '\nplant_def:\n' + relAbs
    s += tl
    print s
    fp.write(s)

def solutionAbs(varTypeDict,varlist,matA,matB,t):
  eAT = matrixExp(matA,t)
  #relAbs = convertToSal(varlist,eAT)
  relAbs = formatRelAbs(varlist,eAT)
  #writeIntermedFile(relAbs,varTypeDict)
  return relAbs


def HSalPPSimpleDefn(node):
    lhsVar = HSalXMLPP.HSalPPExpr(HSalXMLPP.getArg(node,1))
    rhsexpr = node.getElementsByTagName("RHSEXPRESSION")
    if not(rhsexpr.length == 0):
      try:
        rhsVal = float(HSalXMLPP.HSalPPExprs(rhsexpr[0].childNodes))
        return (lhsVar, rhsVal)
      except:
        print "init expr rhs is not a number"
    else:
      print "init expr not of the form lhs = rhs"
    return

def HSalPPAssgns(assgns):
  initVarDict = {}
  defs = assgns.getElementsByTagName("SIMPLEDEFINITION")
  for i in defs:
    (var, val) = HSalPPSimpleDefn(i)
    initVarDict[var] = val
  return initVarDict

def getDecls(basemod, declTag):
  declNodes = basemod.getElementsByTagName(declTag)
  if len(declNodes) <= 0:
    print 'Warning: no '+declTag+' in plant'
    declList = []
  else:    
    for node in declNodes:
      declList = HSalPPDecls(node.childNodes)
    print declTag
    print declList
  return declList

def HSalPPBaseModule(basemod):

  varTypeDict = {'locals':[], 'inputs':[], 'outputs':[], 'inits':[]}

  varTypeDict['locals'] = getDecls(basemod,'LOCALDECL')
  varTypeDict['inputs'] = getDecls(basemod,'INPUTDECL')
  varTypeDict['outputs'] = getDecls(basemod,'OUTPUTDECL')

  initdecl = basemod.getElementsByTagName("INITDECL")
  if not(initdecl == None) and len(initdecl) > 0:
    varTypeDict['inits'] = HSalPPAssgns(initdecl[0])
  
  return varTypeDict




#DUP:HSalRelAbsCons.py

def simpleDefinitionRhsExpr(defn):
    "Return the RHS expression in definition def"
    rhs = defn.getElementsByTagName("RHSEXPRESSION")
    if rhs == None:
        return None
    else:
        return exprs2poly(rhs[0].childNodes)
#DUP:HSalRelAbsCons.py

def getFlow(defs):
    "Return flow of the continuous dynamics stored in definitions"
    flow = list()
    for i in defs:
        lhsvar = simpleDefinitionLhsVar(i)
        rhsexpr = simpleDefinitionRhsExpr(i)
        flow.append(lhsvar)
        flow.append(rhsexpr)
    #print "printing flow"
    #print flow
    return flow


#DUP:HSalRelAbsCons.py
def flow2var(flow):
    "extract variables from the flow"
    i = 0
    varlist = dict()
    while i < len(flow):
        varnamedot = flow[i]
        varlist[varnamedot[0:-3]] = i/2
        i += 2
    return varlist

def findInList(se,l):
  for e in l:
    if se == e:
      return True
  return False

def alignMat(A):
  'equivalent to adding vdot\'= 0, if v is a var present in RHS of flow eqns\
  but is not defined in the LHS of the flow eqns'
  #no. of rows
  r = len(A)
  #no. of columns
  c = 0
  for i in A:
    c = max(c, len(i))
  #while no. of columns != no. of rows
  while c != len(A):
    A.append([0 for j in range(c)])    
  return A

def fixVarlist(flowi, varlist, varTypeDict):
  "it fixes up varlist generated by looking only at the LHS of the flow eqns.\
  it does this by adding undefined variables present in RHS of the flow eqns"
  n = len(varlist)

  for [c,pp] in flowi:
    degree = sum(pp.values())
    var = pp.keys()[0]
    try:
      index = varlist[var]
    except KeyError:
      print 'Warning: '+var+' found in flow eqn but is not defined in plant'
      if findInList(var, varTypeDict['inputs']):
        print 'found it as an input, addidng v\'=0 (everything is ok!)'
        varlist[var] = len(varlist)        
      else:
        exit(0)          
  return varlist

#DUP:HSalRelAbsCons.py
def flow2Aibi(flowi, varlist, varTypeDict):
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


#DUP:HSalRelAbsCons.py

def HSalPPDecls(nodes):
    k = 0
    l=[]
    for j in nodes:
        if (j.localName == "VARDECL"):
            l.append(HSalXMLPP.getName(j))
    return l

#DUP:HSalRelAbsCons.py
def HSalPPLocalGlobalDecl(i):
  return HSalPPDecls(i.childNodes, "", "")

#DUP:HSalRelAbsCons.py
def flow2Ab(flow, varTypeDict):
    "get A,b matrices from the flow, if possible"
    "flow is a list of alternative variabledot, poly"
    #varlist contains all the lhs vars in the flows
    varlist = flow2var(flow)

    n = len(varlist)
    i = 0
    A = list()
    b = list()
    for i in range(n):
      varlist = fixVarlist(flow[2*i+1], varlist,varTypeDict)
    #reset i
    i=0
    while i < n:
        Aibi = flow2Aibi(flow[2*i+1], varlist,varTypeDict)
        if Aibi == None:
            return None
        A.append(Aibi[0])
        b.append(Aibi[1])
        i += 1
    A = alignMat(A)
    return [varlist,A,b]

globalPD = {}

def interpretSALXML():
  global dom
###################### AUX functions ##################
  def getModeData(gc, varTypeDict):
    "Return a new guarded command that is a rel abs of input GC"
    
    #Separate the type var lists
    initVarDict = varTypeDict['inits']

    #Assumes each guard-transition  represent a mode
    guard = gc.getElementsByTagName("GUARD")[0]
    clonedGuard = guard.cloneNode(True)
    assigns = gc.getElementsByTagName("ASSIGNMENTS")[0]
    defs = assigns.getElementsByTagName("SIMPLEDEFINITION")
    #Assuming that all the flows have been recieved in one call
    flow = getFlow(defs)
    [varlist,A,b] = flow2Ab(flow, varTypeDict)
    #Check if all plant variables are initialised
    if len(varlist) != len(initVarDict):
      print "error:no. of plant variables dont match the no. of initial values\n"
      exit(0)
    matA = scipy.mat(A)
    matBT = scipy.mat(b)
    matB = matBT.getT()
    return (clonedGuard,varlist,matA,matB)
#######################################################
  ctxt = dom
  ctxtName = HSalXMLPP.getName(ctxt)
  global globalPD
  globalPD['context'] = ctxtName
  print "\n############################################"
  print "Context: %s" % ctxtName
  ctxtBody = (ctxt.getElementsByTagName("CONTEXTBODY")[0])
  modules = ctxtBody.getElementsByTagName("MODULEDECLARATION")
  if len(modules) > 1:
    print "FATAL: more than 1 module:(%d) found\n" %len(modules)
    exit(0)

#  for module in modules:
  module = modules[0]
  moduleName = HSalXMLPP.getName(module)
  globalPD['module'] = moduleName
  print "Module: %s" % moduleName
  print "############################################\n"
  moduleChildNodes = module.childNodes
  for node in moduleChildNodes:
    if node.localName == 'BASEMODULE':
      varTypeDict = HSalPPBaseModule(node)
  gc = ctxtBody.getElementsByTagName("GUARDEDCOMMAND")
  if len(gc) > 1:
    print "each transition will be interpreted as a HA mode\n"
  elif len(gc) < 1:    
    print "error:less than one transition\n"
  else:
    i = 0
    modeDataList = []
    #each gc represents a mode 
    for mode in gc:
      #What exactly does it check? only the first assignment??!!
      if isCont(mode):
        #return (varlist,matA,matB,t)
        modeDataList.append(getModeData(mode, varTypeDict))
      else:
        print "error: no flow found in a mode\n"
        exit(0)
  plantName = moduleName
  t = getT(plantName)
  return (modeDataList,varTypeDict,t)

def writeIntermedFile(relAbs, varTypeDict):
  hdr = 'IMF\n'
  tl = '\nEND\n'
  with open(intermedFile, "w") as fp:
#    ipStr = [varTypeDict['inputs'][i] for i in varTypeDict['inputs']]
    ipStr = ''
    opStr = ''
    for var in varTypeDict['inputs']:
      ipStr += var + '\n'
    for var in varTypeDict['outputs']:
      opStr += var + '\n'
    s = hdr
    s += '\ninputs:\n' + ipStr
    s += '\noutputs:\n' + opStr
    s += '\nplant_def:\n' + relAbs
    s += tl
    print s
    fp.write(s)

def getVarDefsSAL(varTypeDict):
    ipStr = 'INPUT '
    opStr = 'OUTPUT '
    loccalStr = 'LOCAL '

    for var in varTypeDict['inputs']:
      ipStr += var + ','
    ipStr = ipStr[0:-1]
    #!!!!!!! Assume all vars are REAL
    ipStr += ':REAL'

    for var in varTypeDict['outputs']:
      opStr += var + ','
    opStr = opStr[0:-1]
    opStr += ':REAL'
    s = ''
    s += globalPD['context'] + ':CONTEXT=\nBEGIN\n'
    s += globalPD['module'] + ':MODULE=\nBEGIN\n'
    s += ipStr + '\n'
    s += opStr + '\n'
#    print s
    return s
    #fp.write(s)

def convertToSal(varlist, eAT):
  s = ''
  for var in varlist:
    s += var + '\' = '
    idx = varlist[var]
    eATList = (eAT.tolist())
    eATRow = eATList[idx]
    for var2 in varlist:
      idx2 = varlist[var2]
      s += coeffStr(eATRow[idx2],var2)
    s += '\n'
  return s


def printRelAbsDBG(relAbs):
  s = ''
  for lhs,rhs in relAbs.iteritems():
    s += lhs + '\' = '
    for c,x in rhs:
      s += ' + ' + str(c) + '*' + x
#    c = rhs[0]
#    x = rhs[1]
#    for i,v in enumerate(c):
#      s += ' + ' + str(v) + '*' + x[i]
    s += '\n'
  print s
  exit(0)
  return None

def calcAbs():
  global dom
  modeDataList,varTypeDict,t = interpretSALXML()
  s = getVarDefsSAL(varTypeDict)
  transitions = []
  for modeData in modeDataList:
    guard,varlist,matA,matB = modeData
    relAbs = solutionAbs(varTypeDict,varlist,matA,matB,t)
    transitions.append((guard,relAbs))
  #printRelAbsDBG(relAbs)
  return transitions


def relAbsToXml(absTrans):
  """returns the timed relational abstraction in xml format"""
  # retrieve the SOMECOMANDS node from the hsal file
  # and replace it with 
  global dom
  ctxtBody = dom.getElementsByTagName("CONTEXTBODY")[0]
  modules = ctxtBody.getElementsByTagName("MODULEDECLARATION")
  baseMod = modules[0].getElementsByTagName("BASEMODULE")
  transDecl = baseMod[0].getElementsByTagName("TRANSDECL")
  someCommandsOld = transDecl[0].getElementsByTagName("SOMECOMMANDS")
  
  # Form the new SOMECOMMANDS node using the relational abstraction
  someCommandsNew = dom.createElement("SOMECOMMANDS")

  #for every transition, create an abstracted transition
  for guard,relAbs in absTrans:
    #for every lhs var, create an assignment
    assignment = dom.createElement("ASSIGNMENTS")
    for lhs,rhs in relAbs.iteritems():
      nameexpr = createNodeTag("NAMEEXPR",lhs)
      nextop = createNodeTagChild("NEXTOPERATOR",nameexpr)
      rhsExpr = createNodeCXFromLinXpr(rhs, False)
      rhsExprNode = createNodeTagChild("RHSEXPRESSION",rhsExpr)
      simpleDef = createNodeTagChild2("SIMPLEDEFINITION",nextop,rhsExprNode)
      assignment.appendChild(simpleDef)
    guardedCommand = createNodeTagChild2('GUARDEDCOMMAND', guard, assignment)
    someCommandsNew.appendChild(guardedCommand)
  # Carry out the actual replacement
  transDecl[0].replaceChild(someCommandsNew,someCommandsOld[0])
  #return dom
  return None

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
        print "Unknown file extension; Expecting .hsal; Quitting"
        return 1
    dom = xml.dom.minidom.parse(xmlfilename)
    setDom(dom)
    absTransitions = calcAbs()
    relAbsToXml(absTransitions)
    newCtxt = dom
    
    xmlFile = basename+".xml"
    with open(xmlFile, "w") as fp:
      print >> fp, newCtxt.toxml() 

    absSalFile = basename+".sal"
    print "Abstraction saved as a SAL file::" + absSalFile
    with open(absSalFile, "w") as fp:
        HSalXMLPP.HSalPPContext(newCtxt, fp)


main()
