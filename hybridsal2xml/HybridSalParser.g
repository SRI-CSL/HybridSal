// --------------------------------------------------------------------
// HybridSAL
// Copyright (C) 2006, SRI International.  All Rights Reserved.
// 
// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// 
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
// --------------------------------------------------------------------

/* -*- Mode: Java -*- */
// HybridSAL Parser
// header {
// import SalLexer;
// }

class HybridSalParser extends Parser;
options {
    k = 1;                           // two token lookahead
    exportVocab=HybridSal;                // Call its vocabulary "HybridSal"
    codeGenMakeSwitchThreshold = 2;  // Some optimizations
    codeGenBitsetTestThreshold = 3;
    defaultErrorHandler = false;     // Don't generate parser error handlers
    buildAST = true;
    ASTLabelType = "XmlAst";
}

tokens {
  CONTEXT; CONTEXTBODY; CONTEXTNAME; CONSTANTDECLARATION; PARAMETERS;
  EXPRESSION; CONDITIONAL; RECORDLITERAL; RECORDENTRY;
  TYPE; TYPEDECLARATION; ASSERTIONDECLARATION; CONTEXTDECLARATION;
  MODULEDECLARATION; IDENTIFIER; VARDECL; INPUTDECL; OUTPUTDECL; GLOBALDECL;
  LOCALDECL; ARRAYTYPE; BASEMODULE; MODULE; BASICTYPE; LAMBDAABSTRACTION;
  REAL; NZREAL; INTEGER; NZINTEGER; NATURAL; BOOLEAN; TRANSDECL;
  DEFINITION; SIMPLEDEFINITION; LHS; RHSEXPRESSION; RHSSELECTION; APPLICATION;
  OR; SIMPLEEXPRESSION; SCALARTYPE; SUBRANGE; FUNCTIONTYPE; TUPLETYPE;
  RECORDTYPE; CONSTRUCTOR; ACCESSOR; FULLNAME; FIELDDECLARATION; TYPENAME;
  QUALIFIEDTYPENAME; DEFDECL; FORALLDEFINITION; LABEL; INVARDECL; INITFORDECL;
  INITDECL; GUARDEDCOMMAND; LABELEDCOMMAND; ASSIGNMENTS; GUARD; NAME;
  ACTUALTYPES; ACTUALEXPRS; NAMEEXPR; QUALIFIEDNAMEEXPR; EQUATION; DISEQUATION;
  VARDECLS; NEGATION; IFFEXPRESSION; IMPLICATION; DISJUNCTION; XOREXPRESSION;
  CONJUNCTION; GTEXPRESSION; GEEXPRESSION; LTEXPRESSION; LEEXPRESSION;
  PLUSEXPRESSION; MINUSEXPRESSION; MULTEXPRESSION; DIVEXPRESSION; ARGUMENT;
  ARRAYACCESS; ARRAYSELECTION; RECORDACCESS; RECORDSELECTION; TUPLEACCESS;
  TUPLESELECTION; UPDATESUFFIX; UPDATE; UPDATEEXPRESSION; UPDATEPOSITION;
  TUPLELITERAL; ACTUALPARAMETERS; ARRAYLITERAL; INDEXVARDECL;
  NEXTOPERATOR; SETPREDEXPRESSION; SETLISTEXPRESSION; SOMECOMMANDS;
  MULTICOMMAND; QUANTIFIEDEXPRESSION; QUANTIFIER; LETEXPRESSION;
  LETDECLARATIONS; LETDECLARATION; ASYNCHRONOUSCOMPOSITION;
  SYNCHRONOUSCOMPOSITION; SCALARELEMENT; MODULENAME; QUALIFIEDMODULENAME;
  MODULEINSTANCE; MODULEACTUALS; NEWOUTPUT; RENAMING; RENAME; HIDING;
  NEWVARDECLS; MODULEMODELS; MODULEIMPLEMENTS;
  ASSERTIONPROPOSITION; QUANTIFIEDASSERTION;
  ASSERTIONOPERATOR; ASSERTIONFORM;
  MULTISYNCHRONOUS; MULTIASYNCHRONOUS; OBSERVEMODULE;
  TYPEDECLS; TYPEDECL; WITHMODULE; IDENTIFIERS; RENAMES;
  STATETYPE; MODINIT; MODTRANS;
}

{
  public void setPlaceAttribute(XmlAst t,
        int sLine, int sCol, int eLine, int eCol) {
    t.startLine = sLine;
    t.startColumn = sCol;
    t.endLine = eLine;
    t.endColumn = eCol;
  }
  public void setPlaceAttribute(XmlAst t, XmlAst source)
  {
    t.startLine   = source.startLine;
    t.startColumn = source.startColumn;
    t.endLine = source.endLine;
    t.endColumn = source.endColumn;
  }
  public void setPlaceAttribute(XmlAst t, XmlAst begin, XmlAst end)
  {
    t.startLine = begin.startLine;
    t.startColumn = begin.startColumn;
    t.endLine = end.endLine;
    t.endColumn = end.endColumn;
  }
  public void setSimplePlaceAttribute(XmlAst t) throws TokenStreamException
  {
    String text = t.getText();
    if (text != null && !text.equals("")) {
      t.startLine = LT(0).getLine();
      t.startColumn = LT(0).getColumn();
      t.endLine = LT(0).getLine();
      t.endColumn = LT(0).getColumn() + text.length();
      return;
    }
  }
  public void setPlaceAttribute(XmlAst t) throws TokenStreamException
  {
    XmlAst child = (XmlAst) t.getFirstChild();  
    if (child == null)
      return;
    t.startLine   = child.startLine;
    t.startColumn = child.startColumn;
    while (child.getNextSibling() != null)
      child = (XmlAst) child.getNextSibling();
    t.endLine = child.endLine;
    t.endColumn = child.endColumn;
  }
  public XmlAst infix_to_prefix(XmlAst e) {
    XmlAst op = (XmlAst)e.getNextSibling();
    if (op == null)
      return e;
    else {
      XmlAst rootAST = rootApplAST(op);
      if (rootAST == null)
        return e;
      else {
        XmlAst arg2 = (XmlAst)op.getNextSibling();
        XmlAst rest = (XmlAst)arg2.getNextSibling();
        arg2.setNextSibling(null);
        // Build the new application op(e, arg2)
        XmlAst infixAST = makeInfixApplication(rootAST, op, e, arg2);
        if (rest == null) 
          return infixAST;
        else {
          infixAST.setNextSibling(rest);
          //return infixAST;
          return infix_to_prefix(infixAST);
        }
      }
    }
  }
  // Right-associative version of infix_to_prefix
  public XmlAst infix_to_prefix_right(XmlAst e) {
    XmlAst op = (XmlAst)e.getNextSibling();
    if (op == null)
      return e;
    else {
      XmlAst rootAST = rootApplAST(op);
      if (rootAST == null) 
        return e;
      else {
        XmlAst arg2 = infix_to_prefix_right((XmlAst)op.getNextSibling());
        // Build the new application op(e, arg2)
        XmlAst infixAST = makeInfixApplication(rootAST, op, e, arg2);
        return infixAST;
      }
    }
  }
  public XmlAst makeInfixApplication(XmlAst rootAST, XmlAst op,
             XmlAst arg1, XmlAst arg2) {
    AST opExpr = makeOperatorExpr(op);
    AST argExpr = makeArgumentExpr(arg1,arg2);
    ASTPair applPair = new ASTPair();
    AST applAST;
    astFactory.addASTChild(applPair,opExpr);
    astFactory.addASTChild(applPair,argExpr);
    applAST = applPair.root;
    applAST = astFactory.make((new ASTArray(2)).add(rootAST).add(applAST));
    applPair.root = applAST;
    applPair.child =
      applAST.getFirstChild()!=null
      ? applAST.getFirstChild()
      : applAST;
    applPair.advanceChildToEnd();
    setPlaceAttribute((XmlAst)applPair.root, arg1.startLine, arg1.startColumn, arg2.endLine, arg2.endColumn);
    return (XmlAst)applPair.root;
  }
  public AST makeOperatorExpr(XmlAst ex) {
    XmlAst result = (XmlAst)astFactory.create(NAMEEXPR,ex.getText());
    setPlaceAttribute(result, ex);
    return result;
  }
  public XmlAst makeScalarElement(XmlAst ex) {
    ex.setType(SCALARELEMENT);
    return ex;
  }
  public XmlAst makeNameExpr(XmlAst ex) {
    if (ex.getType() == FULLNAME) {
      ex.setType(QUALIFIEDNAMEEXPR);
      ex.setText("QUALIFIEDNAMEEXPR");
    } else {
      ex.setType(NAMEEXPR);
      //ex.setText("NAMEEXPR");
    }
    return (XmlAst)ex;
  }
  public XmlAst makeModuleName(XmlAst ex) {
    if (ex.getType() == FULLNAME) {
      ex.setType(QUALIFIEDMODULENAME);
      ex.setText("QUALIFIEDMODULENAME");
    } else ex.setType(MODULENAME);
    ex.setNextSibling(null);
    return (XmlAst)ex;
  }
  public XmlAst makeNextOperator(XmlAst ex) {
    AST rootAST = astFactory.create(NEXTOPERATOR,"NEXTOPERATOR");
    ex.setType(NAMEEXPR);
    return (XmlAst)astFactory.make((new ASTArray(2)).add(rootAST).add(ex));
  }
  public XmlAst makeUnaryApplication(XmlAst ex) {
    XmlAst rootAST = (XmlAst)astFactory.create(APPLICATION,"APPLICATION");
    ex.setType(NAMEEXPR);
    XmlAst arg = (XmlAst)ex.getNextSibling();
    ex.setNextSibling(null);
    XmlAst tupAST = (XmlAst)astFactory.create(TUPLELITERAL,"TUPLELITERAL");
    XmlAst tuple = (XmlAst)astFactory.make((new ASTArray(2))
                                           .add(tupAST)
                                           .add(arg));
    setPlaceAttribute(tuple, arg);
    XmlAst result = (XmlAst)astFactory.make((new ASTArray(3))
                                            .add(rootAST)
                                            .add(ex)
                                            .add(tuple));
    result.attributes.put("UNARY","YES");
    setPlaceAttribute(result, ex, arg);
    return result;
  }
  public XmlAst makeQuantifiedExpr(XmlAst quant) {
    XmlAst rootAST = (XmlAst)astFactory.create(QUANTIFIEDEXPRESSION,"QUANTIFIEDEXPRESSION");
    XmlAst varDecls = (XmlAst)quant.getNextSibling();
    XmlAst expr = (XmlAst)varDecls.getNextSibling();
    quant.setNextSibling(null);
    varDecls.setNextSibling(null);
    quant.setType(QUANTIFIER);
    return (XmlAst)astFactory.make((new ASTArray(4))
           .add(rootAST)
           .add(quant)
           .add(varDecls)
           .add(expr));
  }
  public XmlAst makeLhs(XmlAst ex) {
    ex.setType(NAMEEXPR);
    XmlAst next = (XmlAst)ex.getNextSibling();
    ex.setNextSibling(null);
    while (next != null) {
      int sLine = ex.startLine;
		  int sCol  = ex.startColumn;
      switch (next.getType()) {
      case QUOTE:
        XmlAst rootAST = (XmlAst)astFactory.create(NEXTOPERATOR,"NEXTOPERATOR");
        ex = (XmlAst)astFactory.make((new ASTArray(2)).add(rootAST).add(ex));
        break;
      case RECORDACCESS:
      case TUPLEACCESS:
      case ARRAYACCESS:
        rootAST = (XmlAst)rootSuffixExprAST(next);
        ex = (XmlAst)astFactory.make((new ASTArray(3)).add(rootAST).add(ex).add(next.getFirstChild()));
        break;
      }
			setPlaceAttribute(ex, sLine, sCol, next.endLine, next.endColumn);
      XmlAst tmp = (XmlAst)next.getNextSibling();
      next.setNextSibling(null);
      next = tmp;
    }
    return (XmlAst)ex;
  }
  public XmlAst makeTypeName(XmlAst ex) {
    if (ex.getType() == FULLNAME) {
      ex.setType(QUALIFIEDTYPENAME);
      ex.setText("QUALIFIEDTYPENAME");
    } else {
      ex.setType(TYPENAME);
      //ex.setText("TYPENAME");
    }
    return (XmlAst)ex;
  }
  public XmlAst setModuleParens(XmlAst mod) {
    mod.parens += 1;
    return mod;
  }
  public XmlAst makeTupleLiteralOrSetParens(XmlAst exprs) {
    if (exprs.getNextSibling() != null) {
      AST rootAST = astFactory.create(TUPLELITERAL,"TUPLELITERAL");
      return (XmlAst)astFactory.make((new ASTArray(2))
             .add(rootAST)
             .add(exprs));
    } else {
      exprs.parens += 1;
      return exprs;
    }
  }
  public XmlAst makeArgumentExpr(XmlAst arg1, XmlAst arg2) {
    ASTPair argASTPair = new ASTPair();
    XmlAst argAST;
    XmlAst rootAST = (XmlAst) astFactory.create(TUPLELITERAL,"TUPLELITERAL");
    setPlaceAttribute(rootAST, arg1.startLine, arg1.startColumn, arg2.endLine, arg2.endColumn);
    arg1.setNextSibling(null);
    astFactory.addASTChild(argASTPair, arg1);
    astFactory.addASTChild(argASTPair, arg2);
    argAST = (XmlAst)argASTPair.root;
    argAST = (XmlAst)astFactory.make((new ASTArray(2)).add(rootAST).add(argAST));
    return argAST;
  }
  public XmlAst rootApplAST(XmlAst op) {
    int opType;
    String opText;
    switch (op.getType()) {
    case IFF:
    case IMPLIES:
    case OR:
    case XOR:
    case AND:
    case EQ:
    case NEQ:
    case GT:
    case GE:
    case LT:
    case LE:
    case PLUS:
    case MINUS:
    case MULT:
    case DIV:
    case IDENTIFIER:
      XmlAst root = (XmlAst)astFactory.create(APPLICATION,"APPLICATION");
      root.attributes.put("INFIX","YES");
      return root;
    }
    //System.err.println("Unknown op: "+op.getType()+", "+op.toStringList());
    return (XmlAst)null;
  }
  public XmlAst makeVarDecl(XmlAst ids, XmlAst ty) {
    ASTPair varDecl = new ASTPair();
    while (ids != null) {
      XmlAst id = ids;
      XmlAst varDeclAST = (XmlAst)astFactory.create(VARDECL,"VARDECL");
      ids = (XmlAst)ids.getNextSibling();
      id.setNextSibling(null);
      if (ids != null) 
        varDeclAST.attributes.put("CHAIN","YES");
      varDeclAST = (XmlAst)astFactory.make((new ASTArray(3))
             .add(varDeclAST)
             .add(id)
             .add(ty));
      astFactory.addASTChild(varDecl,varDeclAST);
    }
    return (XmlAst)varDecl.root;
  }
  public XmlAst makeTypeDecls(XmlAst ids) {
    AST rootAST = astFactory.create(TYPEDECLS,"TYPEDECLS");
    int numDecls = 1;
    XmlAst nextids = ids;
    while (nextids != null) {
      numDecls += 1;
      nextids = (XmlAst)nextids.getNextSibling();
    }
    ASTArray typeDecls = (new ASTArray(numDecls));
    typeDecls = typeDecls.add(rootAST);
    nextids = ids;
    while (ids != null) {
      nextids = (XmlAst)ids.getNextSibling();
      ids.setNextSibling(null);
      AST tdeclAST = astFactory.create(TYPEDECL,"TYPEDECL");
      typeDecls = typeDecls.add((XmlAst)astFactory.make((new ASTArray(2))
													 .add(tdeclAST).add(ids)));
      ids = nextids;
    }
    XmlAst tdecls = (XmlAst)astFactory.make(typeDecls);
    return tdecls;
  }
  public XmlAst makeSimpleExpression (XmlAst ex) {
    XmlAst prefix = ex;
    XmlAst suffix = (XmlAst)ex.getNextSibling();
    while (suffix != null) {
      XmlAst next = (XmlAst)suffix.getNextSibling();
      ex.setNextSibling(null);
      XmlAst rootAST = rootSuffixExprAST(suffix);
			int sLine = ex.startLine;
			int sCol = ex.startColumn;
      switch (suffix.getType()) {
      case TUPLELITERAL:
        suffix.setNextSibling(null);
        ex = (XmlAst)astFactory.make((new ASTArray(3))
                     .add(rootAST).add(ex).add(suffix));
        break;
      case ARRAYACCESS:
      case RECORDACCESS:
      case TUPLEACCESS:
        ex = (XmlAst)astFactory.make((new ASTArray(3))
           .add(rootAST)
           .add(ex).add(suffix.getFirstChild()));
        break;
      case UPDATESUFFIX:
        XmlAst updatePos = (XmlAst)suffix.getFirstChild();
        XmlAst updateAppl = makeUpdateApplication(ex,updatePos);
        XmlAst updateExpr = (XmlAst)updatePos.getNextSibling();
        suffix.setNextSibling(null);
        ex = (XmlAst)astFactory.make((new ASTArray(4))
           .add(rootAST)
           .add(ex).add(updateAppl).add(updateExpr));
        break;
      }
			setPlaceAttribute(ex, sLine, sCol, suffix.endLine, suffix.endColumn);
      suffix = next;
    }
    return ex;
  }
  public XmlAst makeUpdateApplication(XmlAst ex, XmlAst updatePos) {
    XmlAst updateAppl = (XmlAst)astFactory.dupTree(ex);
    updatePos = (XmlAst)updatePos.getFirstChild();
    while (updatePos != null) {
      XmlAst rootAST = (XmlAst)rootSuffixExprAST(updatePos);
      updateAppl = (XmlAst)astFactory.make((new ASTArray(3))
             .add(rootAST)
             .add(updateAppl)
             .add(updatePos.getFirstChild()));
      XmlAst next = (XmlAst)updatePos.getNextSibling();
      updatePos.setNextSibling(null);
      updatePos = next;
    }
    return updateAppl;
  }
  public XmlAst rootSuffixExprAST(XmlAst suffix) {
    // tupleliteral | access | updatesuffix
    switch (suffix.getType()) {
    case TUPLELITERAL:
      return (XmlAst)astFactory.create(APPLICATION,"APPLICATION");
    case ARRAYACCESS:
      return (XmlAst)astFactory.create(ARRAYSELECTION,"ARRAYSELECTION");
    case RECORDACCESS:
      return (XmlAst)astFactory.create(RECORDSELECTION,"RECORDSELECTION");
    case TUPLEACCESS:
      return (XmlAst)astFactory.create(TUPLESELECTION,"TUPLESELECTION");
    case UPDATESUFFIX:
      return (XmlAst)astFactory.create(UPDATEEXPRESSION,"UPDATEEXPRESSION");
    }
    return (XmlAst)null;
  }
  public XmlAst makeConditional(XmlAst condEx) {
    XmlAst rootAST = (XmlAst)astFactory.create(CONDITIONAL,"CONDITIONAL");
    XmlAst thenEx = (XmlAst)condEx.getNextSibling();
    XmlAst elseEx = (XmlAst)thenEx.getNextSibling();
    if (elseEx.getNextSibling() != null) {
      elseEx = makeConditional(elseEx);
      elseEx.attributes.put("ELSIF","YES");
    }
    condEx.setNextSibling(null);
    thenEx.setNextSibling(null);
    return (XmlAst)astFactory.make((new ASTArray(4))
           .add(rootAST)
           .add(condEx)
           .add(thenEx)
           .add(elseEx));
  }
  public XmlAst makeInfixModule(XmlAst mod1) {
    XmlAst op = (XmlAst)mod1.getNextSibling();
    XmlAst root;
    if (op == null)
      return mod1;
    else {
      switch (op.getType()) {
      case ASYNC:
        root = (XmlAst)astFactory.create(ASYNCHRONOUSCOMPOSITION,
                                         "ASYNCHRONOUSCOMPOSITION");
        break;
      case SYNC:
        root = (XmlAst)astFactory.create(SYNCHRONOUSCOMPOSITION,
                                         "SYNCHRONOUSCOMPOSITION");
        break;
      default:
        return mod1;
      }
      XmlAst mod2 = (XmlAst)op.getNextSibling();
      XmlAst rest = (XmlAst)mod2.getNextSibling();
      mod2.setNextSibling(null);
      mod1.setNextSibling(null);
      op.setNextSibling(null);
      XmlAst infixModule =  (XmlAst)astFactory.make((new ASTArray(3))
                                                    .add(root)
                                                    .add(mod1)
                                                    .add(mod2));
      setPlaceAttribute(infixModule, mod1, mod2);
      if (rest == null)
        return infixModule;
      else {
        infixModule.setNextSibling(rest);
        return makeInfixModule(infixModule);
      }
    }
  }
  public XmlAst makeAssertionForm(XmlAst ex) {
    ex.setType(ASSERTIONFORM);
    return ex;
  }
  public XmlAst makeAssertionProposition(XmlAst ex) {
    XmlAst rootAST = (XmlAst)astFactory.create(ASSERTIONPROPOSITION,
                 "ASSERTIONPROPOSITION");
    ex.setType(ASSERTIONOPERATOR);
    XmlAst arg1 = (XmlAst)ex.getNextSibling();
    ex.setNextSibling(null);
    XmlAst arg2 = (XmlAst)arg1.getNextSibling();
    if (arg2 == null) {
      return (XmlAst)astFactory.make((new ASTArray(3))
             .add(rootAST)
             .add(ex)
             .add(arg1));
    } else {
      arg1.setNextSibling(null);
      return (XmlAst)astFactory.make((new ASTArray(4))
             .add(rootAST)
             .add(ex)
             .add(arg1)
             .add(arg2));
    }
  }
  public XmlAst makeQuantifiedAssertion(XmlAst quant) {
    XmlAst rootAST = (XmlAst)astFactory.create(QUANTIFIEDASSERTION,
                 "QUANTIFIEDASSERTION");
    XmlAst varDecls = (XmlAst)quant.getNextSibling();
    XmlAst expr = (XmlAst)varDecls.getNextSibling();
    quant.setNextSibling(null);
    varDecls.setNextSibling(null);
    quant.setType(QUANTIFIER);
    return (XmlAst)astFactory.make((new ASTArray(4))
           .add(rootAST)
           .add(quant)
           .add(varDecls)
           .add(expr));
  }
}

// Contexts

context! :
  id:identifier (LC! p:parameters RC!)? CLN! "CONTEXT"! EQ! b:contextbody EOF!
  {if (p_AST != null) {
    #context = #(#[CONTEXT,"CONTEXT"],id,p,b);
  } else {
    #context = #(#[CONTEXT,"CONTEXT"],id,#(#[PARAMETERS,"PARAMETERS"], p), b);
  }
  setPlaceAttribute(#context);
  }
  ;

parameters :
  (typedecls)? SEMI! (pvarDecls)?
  {#parameters = #(#[PARAMETERS,"PARAMETERS"], #parameters);
   setPlaceAttribute(#parameters);
  };

pvarDecls :
  varDecls
  {#pvarDecls = #(#[VARDECLS,"VARDECLS"],#pvarDecls);
   setPlaceAttribute(#pvarDecls);};

contextbody 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  "BEGIN"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
    declarations 
  "END"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+3;}
  {#contextbody = #(#[CONTEXTBODY,"CONTEXTBODY"], #contextbody);
   setPlaceAttribute(#contextbody, sLine, sCol, eLine, eCol); }
  ;

declarations : (declaration SEMI!)+ ;

declaration :
  ( (identifier CLN "TYPE")=> typeDeclaration 
  | (identifier CLN assertionForm)=> assertionDeclaration
  | (identifier CLN "CONTEXT")=> contextDeclaration 
  | (identifier (LB! varDecls RB!)? CLN "MODULE") => moduleDeclaration
  | constantDeclaration
  )
  ;

constantDeclaration! :
  id:identifier (LP! v:varDecls RP!)? CLN! t:type (EQ! e:expression)?
  {#constantDeclaration = #(#[CONSTANTDECLARATION,"CONSTANTDECLARATION"],
                            id,#(#[VARDECLS,"VARDECLS"],v),t,e);
   setPlaceAttribute(#constantDeclaration);};

typeDeclaration :
  identifier CLN! "TYPE"! (EQ! typedef)?
  {
   #typeDeclaration = #(#[TYPEDECLARATION,"TYPEDECLARATION"],
                        #typeDeclaration);
   setPlaceAttribute(#typeDeclaration);
  }
  ;

assertionDeclaration :
  identifier CLN! assertionForm assertionExpression
  {#assertionDeclaration = #(#[ASSERTIONDECLARATION,"ASSERTIONDECLARATION"],
                             #assertionDeclaration);
   setPlaceAttribute(#assertionDeclaration);};

assertionForm :
  ("OBLIGATION" | "CLAIM" | "LEMMA" | "THEOREM")
  {#assertionForm = #makeAssertionForm(#assertionForm);
   setSimplePlaceAttribute(#assertionForm);};

assertionExpression :
  ( (AND | OR | IMPLIES | IFF | NOT)=> assertionProposition
  | ("FORALL" | "EXISTS")=> quantifiedAssertion
  | (module (moduleModels | moduleImplements)) => moduleAssertion
  | expression
  );

assertionProposition 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  (((AND|OR|IMPLIES|IFF) {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
     LP! assertionExpression COMMA! assertionExpression RP! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;})
   | (NOT {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
      LP! assertionExpression RP! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}))
  {#assertionProposition = #makeAssertionProposition(#assertionProposition);
   setPlaceAttribute(#assertionProposition, sLine, sCol, eLine, eCol);};

quantifiedAssertion 
  {int sLine=0, sCol=0;} : 
  ("FORALL" | "EXISTS") {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  LP! pvarDecls RP! CLN! aexp : assertionExpression
  {#quantifiedAssertion = makeQuantifiedAssertion(#quantifiedAssertion);
   setPlaceAttribute(#quantifiedAssertion, sLine, sCol, #aexp.endLine, #aexp.endColumn);};

moduleAssertion :
  module (m:moduleModels | i:moduleImplements)
{if (#m != null) {
  #moduleAssertion = #(#[MODULEMODELS,"MODULEMODELS"],#moduleAssertion);
  } else {
  #moduleAssertion = #(#[MODULEIMPLEMENTS,"MODULEIMPLEMENTS"],#moduleAssertion);
  }
  setPlaceAttribute(#moduleAssertion);
};

moduleModels :
  TURNSTILE! expression ;

moduleImplements :
  "IMPLEMENTS"! module ;

moduleRefines :
  "REFINES"! module ;

contextDeclaration :
  identifier CLN! "CONTEXT"! EQ! contextName
  {#contextDeclaration = #(#[CONTEXTDECLARATION,"CONTEXTDECLARATION"],
         #contextDeclaration);
   setPlaceAttribute(#contextDeclaration);};

contextName 
  {int eLine=-1, eCol=-1;} :
  id : identifier (LC! actualparameters RC! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;})?
  {#contextName = #(#[CONTEXTNAME,"CONTEXTNAME"],#contextName);
   if (eCol != -1)
     setPlaceAttribute(#contextName, #id.startLine, #id.startColumn, eLine, eCol);
   else
     setPlaceAttribute(#contextName);};

moduleDeclaration! :
  id:identifier (LB! v:varDecls RB!)? CLN! "MODULE"! EQ! m:module
  {#moduleDeclaration = #(#[MODULEDECLARATION,"MODULEDECLARATION"],
                          id,#(#[VARDECLS,"VARDECLS"],v),m);
   setPlaceAttribute(#moduleDeclaration);};


// Types

typedef :
  type | scalartype | datatype ;

type :
  basictype
  | (module DOT)=> statetype
  | typeName
  | (subrange)=> subrange
  | arraytype
  | (functiontype)=> functiontype
  | tupletype
  | recordtype
  ;

typeName :
  name
  {#typeName = #makeTypeName((XmlAst)#typeName);};

scalartype
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LC! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
    scalarElements 
  RC! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#scalartype = #(#[SCALARTYPE,"SCALARTYPE"],#scalartype);
   setPlaceAttribute(#scalartype, sLine, sCol, eLine, eCol);};

scalarElements :
  scalarElement (COMMA! scalarElement)* ;

scalarElement :
  identifier
{#scalarElement = #makeScalarElement((XmlAst)#scalarElement);};

datatype
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  "DATATYPE"^ {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
     constructors 
  "END"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+3;
          setPlaceAttribute(#datatype, sLine, sCol, eLine, eCol);};

constructors :
  constructor (COMMA! constructor)* ;

constructor 
  {int eLine=0, eCol=0;} :
  id : identifier (LP! accessors RP! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;})?
  {#constructor = #(#[CONSTRUCTOR,"CONSTRUCTOR"],#constructor);
   if (eLine != 0)
     setPlaceAttribute(#constructor, #id.startLine, #id.startColumn, eLine, eCol);
   else
     setPlaceAttribute(#constructor);};

accessors :
  accessor (COMMA! accessor)* ;

accessor : 
  identifier CLN! type
  {#accessor = #(#[ACCESSOR,"ACCESSOR"],#accessor);
   setPlaceAttribute(#accessor);};

indextype : 
    integertype {#indextype = #makeTypeName((XmlAst)#indextype);}
  | name {#indextype = #makeTypeName((XmlAst)#indextype);}
  | subrange ;

integertype: 
  i : INTEGER^ 
  {setPlaceAttribute(#integertype, #i);};

name : 
  (fullname)=> fullname
  | identifier
  ;

fullname! 
  {int eLine=0, eCol=0;} :
  cid:identifier (LC! p:actualparameters RC! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;})? BANG! id:identifier
  {XmlAst ctxName = #(#[CONTEXTNAME,"CONTEXTNAME"],cid,p);
   if (eLine == 0)
     setPlaceAttribute(ctxName, #cid);
   else
     setPlaceAttribute(ctxName, #cid.startLine, #cid.startColumn, eLine, eCol);
   #fullname = #(#[FULLNAME,"FULLNAME"],id, ctxName);
   setPlaceAttribute(#fullname, #cid, #id);};

basictype : 
  (REAL | NZREAL | INTEGER | NZINTEGER | NATURAL | BOOLEAN)
  {#basictype = #(#[TYPENAME,"TYPENAME"],#basictype);
   setSimplePlaceAttribute(#basictype);};

unbounded :
  UNBOUNDED
  {#unbounded = #makeNameExpr((XmlAst)#unbounded);
   setSimplePlaceAttribute(#unbounded);};

bound :
  unbounded | expression ;

subrange 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LB! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
    bound DOTDOT! bound 
  RB! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#subrange = #(#[SUBRANGE,"SUBRANGE"],#subrange);
   setPlaceAttribute(#subrange, sLine, sCol, eLine, eCol);};

arraytype 
  {int sLine=0, sCol=0;} :
  "ARRAY"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
   indextype "OF"! t : type
  {#arraytype = #(#[ARRAYTYPE,"ARRAYTYPE"], #arraytype);
  setPlaceAttribute(#arraytype, sLine, sCol, #t.endLine, #t.endColumn);};

tupletype {int sline=0; int scol=0;} :
  LB! {sline = LT(0).getLine(); scol = LT(0).getColumn();}
  type (COMMA! type)+ RB!
  {#tupletype = #(#[TUPLETYPE,"TUPLETYPE"],#tupletype);
   #setPlaceAttribute(#tupletype, sline, scol,
          LT(0).getLine(), LT(0).getColumn()+1);};

functiontype {int sline=0; int scol=0;} :
  LB! {sline = LT(0).getLine(); scol = LT(0).getColumn();}
  type ARROW! type RB!
  {#functiontype = #(#[FUNCTIONTYPE,"FUNCTIONTYPE"],#functiontype);
   #setPlaceAttribute(#functiontype, sline, scol,
          LT(0).getLine(), LT(0).getColumn()+1);};

recordtype {int sline=0; int scol=0;} : 
  RECS! {sline = LT(0).getLine(); scol = LT(0).getColumn();}
  fielddeclaration (COMMA! fielddeclaration)* RECE!
{#recordtype = #(#[RECORDTYPE,"RECORDTYPE"],#recordtype);
 #setPlaceAttribute(#recordtype, sline, scol,
        LT(0).getLine(), LT(0).getColumn()+2);};

fielddeclaration : 
  identifier CLN! type
  {#fielddeclaration = #(#[FIELDDECLARATION,"FIELDDECLARATION"],
                         #fielddeclaration);
   setPlaceAttribute(#fielddeclaration);};

statetype 
  {int eLine=0, eCol=0;} :
  mod: module DOT! "STATE"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+5;}
  {#statetype = #(#[STATETYPE,"STATETYPE"],#statetype);
   setPlaceAttribute(#statetype, #mod.startLine, #mod.startColumn, eLine, eCol);};

// Expressions

expression :
  iffExpression
  ;

iffExpression :
  impliesexpression
  (options {warnWhenFollowAmbig=false;}:
   op : IFF {setSimplePlaceAttribute(#op);} impliesexpression)*
  {#iffExpression = infix_to_prefix(#iffExpression);};

impliesexpression :
  orexpression
  (options {warnWhenFollowAmbig=false;}:
   op : IMPLIES {setSimplePlaceAttribute(#op);} orexpression)*
  {#impliesexpression = infix_to_prefix_right(#impliesexpression);};

orexpression :
  andexpression
  (options {warnWhenFollowAmbig=false;}:
   (  op1: OR {setSimplePlaceAttribute(#op1);} 
    | op2: XOR {setSimplePlaceAttribute(#op2);}) andexpression)*
  {#orexpression = infix_to_prefix(#orexpression);};

andexpression :
  notexpression
  (options {warnWhenFollowAmbig=false;}:
   op : AND {setSimplePlaceAttribute(#op);} notexpression)*
   {#andexpression = infix_to_prefix(#andexpression);};

notexpression :
  (op : NOT {setSimplePlaceAttribute(#op);} notexpression
  {#notexpression = #makeUnaryApplication(#notexpression);})
  | eqexpression ;

eqexpression :
  relexpression
  (options {warnWhenFollowAmbig=false;}:
   (  op1 : EQ {setSimplePlaceAttribute(#op1);} 
    | op2 : NEQ {setSimplePlaceAttribute(#op2);} ) relexpression)*
  {#eqexpression = infix_to_prefix(#eqexpression);};

relexpression :
  infixapplication
  (options {warnWhenFollowAmbig=false;}:
   (   op1 : GT {setSimplePlaceAttribute(#op1);}
     | op2 : GE {setSimplePlaceAttribute(#op2);}
     | op3 : LT {setSimplePlaceAttribute(#op3);}
     | op4 : LE {setSimplePlaceAttribute(#op4);}) infixapplication)*
  {#relexpression = infix_to_prefix(#relexpression);};

infixapplication :
  additiveexpression
  (options {warnWhenFollowAmbig=false;}:
   op : IDENTIFIER {setSimplePlaceAttribute(#op);} additiveexpression)*
  {#infixapplication = infix_to_prefix(#infixapplication);};

additiveexpression :
  multiplicativeexpression
  (options {warnWhenFollowAmbig=false;}:
   (  op1 : PLUS {setSimplePlaceAttribute(#op1);}
    | op2 : MINUS {setSimplePlaceAttribute(#op2);} ) multiplicativeexpression)*
  {#additiveexpression = infix_to_prefix(#additiveexpression);};

multiplicativeexpression :
  unaryexpression
  (options {warnWhenFollowAmbig=false;}:
   (  op1 : MULT {setSimplePlaceAttribute(#op1);}
    | op2 : DIV {setSimplePlaceAttribute(#op2);} ) unaryexpression)*
  {#multiplicativeexpression = infix_to_prefix(#multiplicativeexpression);};

unaryexpression :
  ( op: MINUS {setSimplePlaceAttribute(#op);} unaryexpression
   {#unaryexpression = #makeUnaryApplication(#unaryexpression);})
  | simpleExpression
  ;

simpleExpression :
  expressionprefix (options {warnWhenFollowAmbig=false;}:
        expressionSuffix)*
  {#simpleExpression = makeSimpleExpression(#simpleExpression);};

nameexpr :
  name
  {#nameexpr = #makeNameExpr((XmlAst)#nameexpr);};

expressionprefix :
  ( (nextvariable)=> nextvariable
  | (module DOT ("INIT"|"TRANS"))=> statepreds
  | nameexpr
  | numeral
  | lambdaabstraction
  | quantifiedexpression
  | letexpression
  | arrayliteral 
  | recordliteral 
  | tupleLiteral 
  | setexpression
  | conditional
  ) ;

expressionSuffix :
  argument
  | access
  | updatesuffix
  ;

nextvariable 
  {int eLine=0, eCol=0;} :
  id : identifier QUOTE! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#nextvariable = #makeNextOperator((XmlAst)#nextvariable);
   setPlaceAttribute(#nextvariable, #id.startLine, #id.startColumn, eLine, eCol);};

lambdaabstraction 
  {int sLine=0, sCol=0;} :
  "LAMBDA"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
  LP! pvarDecls RP! CLN! expr : expression
  {#lambdaabstraction = #(#[LAMBDAABSTRACTION,"LAMBDAABSTRACTION"],
                          #lambdaabstraction);
   setPlaceAttribute(#lambdaabstraction, sLine, sCol, #expr.endLine, #expr.endColumn);};

quantifiedexpression : 
  (  op1 : "FORALL" {setSimplePlaceAttribute(#op1);} 
   | op2 : "EXISTS" {setSimplePlaceAttribute(#op2);})
  LP! pvarDecls RP! CLN! expression
  {#quantifiedexpression = #makeQuantifiedExpr(#quantifiedexpression);
   setPlaceAttribute(#quantifiedexpression);};

letexpression 
  {int sLine=0, sCol=0;} :
  "LET"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
  letdeclarations "IN"! expr : expression
  {#letexpression = #(#[LETEXPRESSION,"LETEXPRESSION"],#letexpression);
   setPlaceAttribute(#letexpression, sLine, sCol, #expr.endLine, #expr.endColumn);};

letdeclarations : 
  letDeclaration (COMMA! letDeclaration)*
  {#letdeclarations = #(#[LETDECLARATIONS,"LETDECLARATIONS"],#letdeclarations);
   setPlaceAttribute(#letdeclarations);};

letDeclaration :
  identifier CLN! type EQ! expression
  {#letDeclaration = #(#[LETDECLARATION,"LETDECLARATION"],#letDeclaration);
   setPlaceAttribute(#letDeclaration);};

arrayliteral 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LB! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
  LB! indexVarDecl RB! expression RB! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#arrayliteral = #(#[ARRAYLITERAL,"ARRAYLITERAL"],#arrayliteral);
   setPlaceAttribute(#arrayliteral, sLine, sCol, eLine, eCol); };

recordliteral 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  RECEXS! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
  recordentry (COMMA! recordentry)* RECEXE! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+2;}
  {#recordliteral = #(#[RECORDLITERAL,"RECORDLITERAL"],#recordliteral);
   setPlaceAttribute(#recordliteral, sLine, sCol, eLine, eCol); };

recordentry :
  identifier ASSIGN! expression
  {#recordentry = #(#[RECORDENTRY,"RECORDENTRY"],#recordentry);
   setPlaceAttribute(#recordentry);};

tupleLiteral 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LP! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
  expressions RP! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#tupleLiteral = #makeTupleLiteralOrSetParens(#tupleLiteral);
   setPlaceAttribute(#tupleLiteral, sLine, sCol, eLine, eCol); };

setexpression :
  (setpredexpression)=> setpredexpression
  | setlistexpression
  ;

setpredexpression 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LC! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}   
  identifier CLN! type VBAR! expression RC! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#setpredexpression = #(#[SETPREDEXPRESSION,"SETPREDEXPRESSION"],
                          #setpredexpression);
   setPlaceAttribute(#setpredexpression, sLine, sCol, eLine, eCol); };


setlistexpression 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LC! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}   
  (expression (COMMA! expression)*)? RC! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#setlistexpression = #(#[SETLISTEXPRESSION,"SETLISTEXPRESSION"],
                          #setlistexpression);
   setPlaceAttribute(#setlistexpression, sLine, sCol, eLine, eCol); };

conditional 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  "IF"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}    
     expression
  "THEN"! expression
  (elsif)*   
  "ELSE"! expression
  "ENDIF"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+5;} 
  {#conditional = #makeConditional(#conditional);
   setPlaceAttribute(#conditional, sLine, sCol, eLine, eCol);};

elsif :
  "ELSIF"! expression "THEN"! expression ;

statepreds 
  {int eLine=0, eCol=0;} :
  mod: module DOT!
  ("INIT"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+4;
            #statepreds = #(#[MODINIT,"MODINIT"],#statepreds);}
  |"TRANS"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+5;
             #statepreds = #(#[MODTRANS,"MODTRANS"],#statepreds);}
  )
  {setPlaceAttribute(#statepreds, #mod.startLine, #mod.startColumn, eLine, eCol);}
  ;
  
argument 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LP! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}   
    expressions 
  RP! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#argument = #(#[TUPLELITERAL,"TUPLELITERAL"],#argument);
   setPlaceAttribute(#argument, sLine, sCol, eLine, eCol); };

expressions :
  expression (COMMA! expression )* ;

updatesuffix 
  {int sLine=0, sCol=0;} :
  "WITH"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}   
  up: update
  {#updatesuffix = #(#[UPDATESUFFIX,"UPDATESUFFIX"],#updatesuffix);
   setPlaceAttribute(#updatesuffix, sLine, sCol, #up.endLine, #up.endColumn);};

update :
  updateposition ASSIGN! expression ;

updateposition :
  (argument | access)+
  {#updateposition = #(#[UPDATEPOSITION,"UPDATEPOSITION"],#updateposition);
   setPlaceAttribute(#updateposition);};

indexVarDecl :
  identifier CLN! indextype
  {#indexVarDecl = #(#[INDEXVARDECL,"INDEXVARDECL"],#indexVarDecl);
   setPlaceAttribute(#indexVarDecl);};

identifiers :
  identifier (COMMA! identifier)* ;

pidentifiers :
  ids: identifiers
  {#pidentifiers = #(#[IDENTIFIERS,"IDENTIFIERS"],#pidentifiers);
  setPlaceAttribute(#pidentifiers);};

varDecl! :
  ids:identifiers CLN! ty:type
  {#varDecl=makeVarDecl(#ids,#ty);
   setPlaceAttribute(#varDecl);};

varDecls :
  varDecl (COMMA! varDecl)*;

/* The Transition Language */

lhs :
  identifier (q : QUOTE {setSimplePlaceAttribute(#q);})? (access)*
  {#lhs = #makeLhs((XmlAst)#lhs);};

access 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
    (LB! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}    
       expression 
     RB! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
    ) {#access = #(#[ARRAYACCESS,"ARRAYACCESS"],#access);
       setPlaceAttribute(#access, sLine, sCol, eLine, eCol);}
  | (DOT identifier)=> DOT! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
                       id: identifier 
                       {#access = #(#[RECORDACCESS,"RECORDACCESS"],#access);
                        setPlaceAttribute(#access, sLine, sCol, #id.endLine, #id.endColumn); }
  | DOT! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
    n : numeral 
    {#access = #(#[TUPLEACCESS,"TUPLEACCESS"],#access);
     setPlaceAttribute(#access, sLine, sCol, #n.endLine, #n.endColumn);}
  ;

rhsexpression 
  {int sLine=0, sCol=0;} :
  EQ! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
  expr : expression
  {#rhsexpression = #(#[RHSEXPRESSION,"RHSEXPRESSION"],#rhsexpression);
   setPlaceAttribute(#rhsexpression, sLine, sCol, #expr.endLine, #expr.endColumn);};

rhsselection 
  {int sLine=0, sCol=0;} :
  "IN"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
  expr : expression
  {#rhsselection = #(#[RHSSELECTION,"RHSSELECTION"],#rhsselection);
   setPlaceAttribute(#rhsselection, sLine, sCol, #expr.endLine, #expr.endColumn);};

rhsdefinition :
  rhsexpression | rhsselection ;

simpleDefinition :
  lhs rhsdefinition
  {#simpleDefinition = #(#[SIMPLEDEFINITION,"SIMPLEDEFINITION"],
                         #simpleDefinition);
   setPlaceAttribute(#simpleDefinition);};

foralldefinition 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LP! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
    "FORALL"! LP! pvarDecls RP! CLN! definitions 
  RP! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#foralldefinition = #(#[FORALLDEFINITION,"FORALLDEFINITION"],
                         #foralldefinition);
   setPlaceAttribute(#foralldefinition, sLine, sCol, eLine, eCol);};

definition :
  simpleDefinition | foralldefinition ;

definitions :
  definition (SEMI! definition)* ;

guard :
  expression
  {#guard = #(#[GUARD,"GUARD"],#guard);
   setPlaceAttribute(#guard);};

assignments :
  simpleDefinition (SEMI! simpleDefinition)*
    {#assignments = #(#[ASSIGNMENTS,"ASSIGNMENTS"],#assignments);
     setPlaceAttribute(#assignments);};

guardedcommand :
  guard LONGARROW! (assignments)?
  {#guardedcommand = #(#[GUARDEDCOMMAND,"GUARDEDCOMMAND"],#guardedcommand);
   setPlaceAttribute(#guardedcommand);};

/* The Module Language */

module : 
  basicmodule (options {warnWhenFollowAmbig=false;}:
         (ASYNC|SYNC) basicmodule)*
  {#module = #makeInfixModule(#module);};

basicmodule :
  basemodule
  | (LP SYNC)=> multisynchronous
  | (LP ASYNC)=> multiasynchronous
  | hiding
  | newoutput
  | renaming
  | withModule
  | modulename
  | observeModule
  | (LP! module RP!) {#basicmodule = #setModuleParens(#basicmodule);}
  ;

basemodule
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  "BEGIN"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
    basedeclarations
  "END"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+3;}
{#basemodule=#(#[BASEMODULE,"BASEMODULE"],#basemodule);
 setPlaceAttribute(#basemodule,sLine,sCol,eLine,eCol);};

basedeclarations :
  (basedeclaration)* ;

basedeclaration :
  inputdecl | outputdecl | globaldecl | localdecl | defdecl | invardecl
  | initfordecl | initdecl | transdecl ;

multisynchronous 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LP! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  SYNC! LP! indexVarDecl RP! CLN! module RP! 
  {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#multisynchronous = #(#[MULTISYNCHRONOUS,"MULTISYNCHRONOUS"],
                         #multisynchronous);
   setPlaceAttribute(#multisynchronous,sLine,sCol,eLine,eCol);};

multiasynchronous 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  LP! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  ASYNC! LP! indexVarDecl RP! CLN! module RP!
  {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  {#multiasynchronous = #(#[MULTIASYNCHRONOUS,"MULTIASYNCHRONOUS"],
                         #multiasynchronous);
   setPlaceAttribute(#multiasynchronous,sLine,sCol,eLine,eCol);};

hiding
  {int sLine=0, sCol=0;} :
  "LOCAL"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
  pidentifiers "IN"! mod: module
  {#hiding = #(#[HIDING,"HIDING"],#hiding);
   setPlaceAttribute(#hiding, sLine, sCol, #mod.endLine, #mod.endColumn);};

newoutput 
  {int sLine=0, sCol=0;} :
  "OUTPUT"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  pidentifiers "IN"! mod: module
  {#newoutput = #(#[NEWOUTPUT,"NEWOUTPUT"],#newoutput);
   setPlaceAttribute(#newoutput,sLine,sCol, #mod.endLine, #mod.endColumn);};

renaming 
  {int sLine=0, sCol=0;} :
  "RENAME"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  renames "IN"! mod: module 
  {#renaming = #(#[RENAMING,"RENAMING"],#renaming);
   setPlaceAttribute(#renaming, sLine, sCol, #mod.endLine, #mod.endColumn);};

renames :
  rename (COMMA! rename)*
  {#renames = #(#[RENAMES,"RENAMES"],#renames);
   setPlaceAttribute(#renames);};

rename : 
  lhs "TO"! lhs
  {#rename = #(#[RENAME,"RENAME"],#rename);
   setPlaceAttribute(#rename);};

withModule
  {int sLine=0, sCol=0;} :
  "WITH"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  newVarDecls mod: module
  {#withModule = #(#[WITHMODULE,"WITHMODULE"],#withModule);
   setPlaceAttribute(#withModule, sLine, sCol, #mod.endLine, #mod.endColumn);};

modulename :
  n:name a:moduleActuals
  {#modulename = #(#[MODULEINSTANCE,"MODULEINSTANCE"],#makeModuleName(n),a);
   if (#a.startLine != 0)
     setPlaceAttribute(#modulename); // "a" (moduleActuals) is not empty.
   else
     setPlaceAttribute(#modulename, #n);};

moduleActuals 
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  (LB! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();} 
   expressions RB!
   {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;}
  )?
  {#moduleActuals = #(#[MODULEACTUALS,"MODULEACTUALS"],#moduleActuals);
   if (sLine != 0)
     setPlaceAttribute(#moduleActuals, sLine, sCol, eLine, eCol);
  };

observeModule 
  {int sLine=0, sCol=0;} :
  "OBSERVE"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}
  module "WITH"! mod: module
  {#observeModule = #(#[OBSERVEMODULE,"OBSERVEMODULE"],#observeModule);
   setPlaceAttribute(#observeModule, sLine, sCol, #mod.endLine, #mod.endColumn);};


/* Declarations within modules */

inputdecl 
  {int sLine=0, sCol=0;} :
  "INPUT"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}    
  v: varDecls 
  {#inputdecl = #(#[INPUTDECL,"INPUTDECL"], #inputdecl);
   setPlaceAttribute(#inputdecl, sLine, sCol, #v.endLine, #v.endColumn);};

outputdecl 
  {int sLine=0, sCol=0;} :
  "OUTPUT"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
  v: varDecls
  {#outputdecl = #(#[OUTPUTDECL,"OUTPUTDECL"], #outputdecl);
   setPlaceAttribute(#outputdecl, sLine, sCol, #v.endLine, #v.endColumn);};

globaldecl 
  {int sLine=0, sCol=0;} :
  "GLOBAL"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
   v: varDecls
  {#globaldecl = #(#[GLOBALDECL,"GLOBALDECL"], #globaldecl);
   setPlaceAttribute(#globaldecl, sLine, sCol, #v.endLine, #v.endColumn);};

localdecl
  {int sLine=0, sCol=0;} :
  "LOCAL"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
   v: varDecls
  {#localdecl = #(#[LOCALDECL,"LOCALDECL"], #localdecl);
   setPlaceAttribute(#localdecl, sLine, sCol, #v.endLine, #v.endColumn);};

defdecl
  {int sLine=0, sCol=0;} :
  "DEFINITION"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
  d: definitions
  {#defdecl = #(#[DEFDECL,"DEFDECL"], #defdecl);
   setPlaceAttribute(#defdecl, sLine, sCol, #d.endLine, #d.endColumn);};

invardecl 
  {int sLine=0, sCol=0;} :
  "INVARIANT"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
   expression
  { XmlAst tmp = #invardecl;
    setPlaceAttribute(tmp);
    #invardecl = #(#[INVARDECL,"INVARDECL"], #invardecl);
    setPlaceAttribute(#invardecl, sLine, sCol, tmp.endLine, tmp.endColumn);};

initfordecl 
  {int sLine=0, sCol=0;} :
  "INITFORMULA"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
   expression
  { XmlAst tmp = #initfordecl;
    setPlaceAttribute(tmp);
    #initfordecl = #(#[INITFORDECL,"INITFORDECL"], #initfordecl);
    setPlaceAttribute(#initfordecl, sLine, sCol, tmp.endLine, tmp.endColumn);};

initdecl 
  {int sLine=0, sCol=0;} :
  "INITIALIZATION"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
  definitionorcommand (SEMI! definitionorcommand)*
  { XmlAst tmp = #initdecl;
    setPlaceAttribute(tmp);
    #initdecl = #(#[INITDECL,"INITDECL"], #initdecl);
    setPlaceAttribute(#initdecl, sLine, sCol, tmp.endLine, tmp.endColumn);};

transdecl 
  {int sLine=0, sCol=0;} :
  "TRANSITION"! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}     
  definitionorcommand (SEMI! definitionorcommand)*
  { XmlAst tmp = #transdecl;
    setPlaceAttribute(tmp);
    #transdecl = #(#[TRANSDECL,"TRANSDECL"],#transdecl);
    setPlaceAttribute(#transdecl, sLine, sCol, tmp.endLine, tmp.endColumn);}; 

labeledcommand :
  id:identifier CLN! gc:guardedcommand
  {#id.setType(LABEL);
   #labeledcommand = #(#[LABELEDCOMMAND,"LABELEDCOMMAND"],#labeledcommand);
   setPlaceAttribute(#labeledcommand);};

namedcommand :
  (identifier CLN)=> labeledcommand
  | guardedcommand ;

somecommand :
  (namedcommand)=> namedcommand | multicommand ;

somecommands :
  somecommand (ASYNC! somecommand)*
  {#somecommands = #(#[SOMECOMMANDS,"SOMECOMMANDS"],#somecommands);
   setPlaceAttribute(#somecommands);};

multicommand :
  LB! guardedcommand (SYNC! guardedcommand)* RB!
  {#multicommand = #(#[MULTICOMMAND,"MULTICOMMAND"],#multicommand);
   setPlaceAttribute(#multicommand);};

definitionorcommand
  {int sLine=0, sCol=0, eLine=0, eCol=0;} :
  definition
  | (LB! {sLine = LT(0).getLine(); sCol = LT(0).getColumn();}  
      sc : somecommands 
     RB! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
          setPlaceAttribute(#sc, sLine, sCol, eLine, eCol);}
    )
  ;

newVarDecl :
  inputdecl | outputdecl | globaldecl;

newVarDecls :
  newVarDecl (SEMI! newVarDecl)*
  {#newVarDecls = #(#[NEWVARDECLS,"NEWVARDECLS"],#newVarDecls);
   setPlaceAttribute(#newVarDecls);};

typedecls 
   {int eLine=0, eCol=0;} :
   ids: identifiers CLN! "TYPE"! {eLine = LT(0).getLine(); eCol = LT(0).getColumn()+4;}
  {#typedecls = #makeTypeDecls(#typedecls);
   setPlaceAttribute(#typedecls, #ids.startLine, #ids.startColumn, eLine, eCol);};

actualparameters :
	(actualtypes)? SEMI! (actualexprs)?
  {#actualparameters = #(#[ACTUALPARAMETERS,"ACTUALPARAMETERS"],#actualparameters);
   setPlaceAttribute(#actualparameters);};

actualtypes :
  (type (COMMA! type)*)?
  {#actualtypes = #(#[ACTUALTYPES,"ACTUALTYPES"],#actualtypes);
   setPlaceAttribute(#actualtypes);};

actualexprs :
  (expression (COMMA! expression)*)?
  {#actualexprs = #(#[ACTUALEXPRS,"ACTUALEXPRS"],#actualexprs);
   setPlaceAttribute(#actualexprs);};

identifier :
  IDENTIFIER^
{#setPlaceAttribute(#identifier,
                    LT(0).getLine(),
        LT(0).getColumn(),
        LT(0).getLine(),
        LT(0).getColumn()+#identifier.getText().length());};

numeral :
  NUMERAL^
  {#setPlaceAttribute(#numeral,
                    LT(0).getLine(),
        LT(0).getColumn(),
        LT(0).getLine(),
        LT(0).getColumn()+#numeral.getText().length());
    System.err.println("Numeral Parsed" + #numeral.getText());
};

class HybridSalLexer extends Lexer;

options {
  exportVocab=HybridSal;      // call the vocabulary "HybridSal"
  testLiterals=false;    // don't automatically test for literals
  k=3;                   // four characters of lookahead
}
 
// Whitespace
WS : ( ' ' | '\t' | '\n' {newline();} | '\r' | '\f')
     { _ttype = Token.SKIP; }
   ;

// Single-line comments
SL_COMMENT
  : "%" (~('\n'|'\r'))* ('\n'|'\r'('\n')?)
    {$setType(Token.SKIP); newline();}
  ;

LP: '(';
RP: ')';
LB: '[';
RB: ']';
LC: '{';
RC: '}';
RECS: "[#";
RECE: "#]";
RECEXS: "(#";
RECEXE: "#)";
DOT: '.';
COMMA: ',';
CLN: ':';
SEMI: ';';
BANG: '!';
VBAR: '|';
PERCENT: '%';
HASH: '#';
QMARK: '?';

NUMERAL: ('0'..'9')+ ('.'('0'..'9')+)?;
protected ALPHANUM: (ALPHA|'0'..'9'|'?'|'_');

// logical operators
AND : ("AND" ALPHANUM) => "AND" (ALPHANUM)+ {$setType(IDENTIFIER);}
    | "AND" ;
OR : ("OR" ALPHANUM) => "OR" (ALPHANUM)+ {$setType(IDENTIFIER);}
   | "OR";
XOR : ("XOR" ALPHANUM) => "XOR" (ALPHANUM)+ {$setType(IDENTIFIER);}
    | "XOR";
NOT : ("NOT" ALPHANUM) => "NOT" (ALPHANUM)+ {$setType(IDENTIFIER);}
    | "NOT";

ASSIGN : ":=" ;
DOTDOT : ".." ;
QUOTE : "\'" ;
protected IMPLIES : "=>" ;
protected EQ : '=' ;
EQIMPL : ("=>" OPCHAR) => "=>" (OPCHAR)+ {$setType(IDENTIFIER);}
       | "=>" {$setType(IMPLIES);}
       | ('=' OPCHAR_NO_GT) => '=' OPCHAR_NO_GT (OPCHAR)* {$setType(IDENTIFIER);}
       | '=' {$setType(EQ);}
       ;
protected DIV : '/' ;
protected NEQ : "/=" ;
SLASH : ("/=" OPCHAR) => "/=" (OPCHAR)+ {$setType(IDENTIFIER);}
      | "/=" {$setType(NEQ);}
      | ('/' OPCHAR_NO_EQ) => '/' OPCHAR_NO_EQ (OPCHAR)* {$setType(IDENTIFIER);}
      | '/' {$setType(DIV);}
      ;
SYNC: "||" ;
ASYNC: "[]";

// Arithmetic operators
PLUS : ('+' OPCHAR) => '+' (OPCHAR)+ {$setType(IDENTIFIER);}
     | '+';
protected LONGARROW : "-->" ;
protected ARROW : "->" ;
protected MINUS : '-' ;
HYPHEN : ("-->" OPCHAR) => "-->" (OPCHAR)+ {$setType(IDENTIFIER);}
       | "-->" {$setType(LONGARROW);}
       | ("--" OPCHAR_NO_GT) => "--" OPCHAR_NO_GT (OPCHAR)* {$setType(IDENTIFIER);}
       | ("->" OPCHAR) => "->" (OPCHAR)+ {$setType(IDENTIFIER);}
       | "->" {$setType(ARROW);}
       | ('-' OPCHAR_NO_HYPHEN_OR_GT) => '-' OPCHAR_NO_HYPHEN_OR_GT (OPCHAR)* {$setType(IDENTIFIER);}
       | "--" {$setType(IDENTIFIER);}
       | '-' {$setType(MINUS);}
       ;
protected MULT : '*' ;
STAR : ('*' OPCHAR) => '*' (OPCHAR)+ {$setType(IDENTIFIER);}
     | '*' {$setType(MULT);}
     ;


// Relational operators
protected IFF : "<=>" ;
protected LE : "<=" ;
protected LT : '<' ;
LTE : ("<=>" OPCHAR) => "<=>" (OPCHAR)+ {$setType(IDENTIFIER);}
    | "<=>" {$setType(IFF);}
    | ("<=" OPCHAR_NO_GT) => "<=" OPCHAR_NO_GT (OPCHAR)* {$setType(IDENTIFIER);}
    | "<=" {$setType(LE);}
    | ('<' OPCHAR_NO_EQ) => '<' OPCHAR_NO_EQ (OPCHAR)* {$setType(IDENTIFIER);}
    | '<' {$setType(LT);}
    ;
protected GE : ">=" ;
protected GT : '>' ;
GTE : (">=" OPCHAR) => ">=" (OPCHAR)+ {$setType(IDENTIFIER);}
    | ">=" {$setType(GE);}
    | ('>' OPCHAR_NO_EQ) => '>' OPCHAR_NO_EQ (OPCHAR)* {$setType(IDENTIFIER);}
    | '>' {$setType(GT);}
    ;

// Misc
TURNSTILE : "|-" ;
UNBOUNDED : '_' ;

/* From the language description: an identifier is taken to be any string
of ASCII characters that is not a numeral and does not contain spaces,
parentheses, brackets, braces, the percent sign, equality, comma, period,
colon, semi-colon, and hash.  */

// IDENTIFIER
IDENTIFIER
  options {testLiterals=true;} :
  (ALPHA(ALPHA|'0'..'9'|'?'|'_')*) | (OPCHAR1 (OPCHAR)*) ;
protected ALPHA: ('a'..'z'|'A'..'Z');
protected OPCHAR1: ('$'|'&'|'@'|'^'|'~');
protected OPCHAR: ~('a'..'z'|'A'..'Z'|'0'..'9'|'('|')'|'['|']'|'{'|'}'|'%'|','|'.'|':'|';'|'#'|'\''|'!'|'?'|'_'|'|'|' '|'\t'|'\n'|'\r'|'\f') ;

// These are used to remove ambiguities in the EQIMPL, SLASH, HYPHEN, LTE,
// and GTE tokens.
protected OPCHAR_NO_GT : ~('a'..'z'|'A'..'Z'|'0'..'9'|'>'|'('|')'|'['|']'|'{'|'}'|'%'|','|'.'|':'|';'|'#'|'\''|'!'|'?'|'_'|'|'|' '|'\t'|'\n'|'\r'|'\f') ;
protected OPCHAR_NO_EQ : ~('a'..'z'|'A'..'Z'|'0'..'9'|'='|'('|')'|'['|']'|'{'|'}'|'%'|','|'.'|':'|';'|'#'|'\''|'!'|'?'|'_'|'|'|' '|'\t'|'\n'|'\r'|'\f') ;
protected OPCHAR_NO_HYPHEN_OR_GT : ~('a'..'z'|'A'..'Z'|'0'..'9'|'-'|'>'|'('|')'|'['|']'|'{'|'}'|'%'|','|'.'|':'|';'|'#'|'\''|'!'|'?'|'_'|'|'|' '|'\t'|'\n'|'\r'|'\f') ;

// The only purpose of the following line is to allow the user to use the double quote character inside comments.
DOUBLEQUOTE : "\"";
