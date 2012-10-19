// $ANTLR 2.7.1: "HybridSalParser.g" -> "HybridSalParser.java"$

import antlr.TokenBuffer;
import antlr.TokenStreamException;
import antlr.TokenStreamIOException;
import antlr.ANTLRException;
import antlr.LLkParser;
import antlr.Token;
import antlr.TokenStream;
import antlr.RecognitionException;
import antlr.NoViableAltException;
import antlr.MismatchedTokenException;
import antlr.SemanticException;
import antlr.ParserSharedInputState;
import antlr.collections.impl.BitSet;
import antlr.collections.AST;
import antlr.ASTPair;
import antlr.collections.impl.ASTArray;

public class HybridSalParser extends antlr.LLkParser
       implements HybridSalTokenTypes
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

protected HybridSalParser(TokenBuffer tokenBuf, int k) {
  super(tokenBuf,k);
  tokenNames = _tokenNames;
}

public HybridSalParser(TokenBuffer tokenBuf) {
  this(tokenBuf,1);
}

protected HybridSalParser(TokenStream lexer, int k) {
  super(lexer,k);
  tokenNames = _tokenNames;
}

public HybridSalParser(TokenStream lexer) {
  this(lexer,1);
}

public HybridSalParser(ParserSharedInputState state) {
  super(state,1);
  tokenNames = _tokenNames;
}

	public final void context() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst context_AST = null;
		XmlAst id_AST = null;
		XmlAst p_AST = null;
		XmlAst b_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
		}
		{
		switch ( LA(1)) {
		case LC:
		{
			XmlAst tmp1_AST = null;
			tmp1_AST = (XmlAst)astFactory.create(LT(1));
			match(LC);
			parameters();
			if (inputState.guessing==0) {
				p_AST = (XmlAst)returnAST;
			}
			XmlAst tmp2_AST = null;
			tmp2_AST = (XmlAst)astFactory.create(LT(1));
			match(RC);
			break;
		}
		case CLN:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp3_AST = null;
		tmp3_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		XmlAst tmp4_AST = null;
		tmp4_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_CONTEXT);
		XmlAst tmp5_AST = null;
		tmp5_AST = (XmlAst)astFactory.create(LT(1));
		match(EQ);
		contextbody();
		if (inputState.guessing==0) {
			b_AST = (XmlAst)returnAST;
		}
		XmlAst tmp6_AST = null;
		tmp6_AST = (XmlAst)astFactory.create(LT(1));
		match(Token.EOF_TYPE);
		if ( inputState.guessing==0 ) {
			context_AST = (XmlAst)currentAST.root;
			if (p_AST != null) {
			context_AST = (XmlAst)astFactory.make( (new ASTArray(4)).add((XmlAst)astFactory.create(CONTEXT,"CONTEXT")).add(id_AST).add(p_AST).add(b_AST));
			} else {
			context_AST = (XmlAst)astFactory.make( (new ASTArray(4)).add((XmlAst)astFactory.create(CONTEXT,"CONTEXT")).add(id_AST).add((XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(PARAMETERS,"PARAMETERS")).add(p_AST))).add(b_AST));
			}
			setPlaceAttribute(context_AST);
			
			currentAST.root = context_AST;
			currentAST.child = context_AST!=null &&context_AST.getFirstChild()!=null ?
				context_AST.getFirstChild() : context_AST;
			currentAST.advanceChildToEnd();
		}
		returnAST = context_AST;
	}
	
	public final void identifier() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst identifier_AST = null;
		
		XmlAst tmp7_AST = null;
		if (inputState.guessing==0) {
			tmp7_AST = (XmlAst)astFactory.create(LT(1));
			astFactory.makeASTRoot(currentAST, tmp7_AST);
		}
		match(IDENTIFIER);
		if ( inputState.guessing==0 ) {
			identifier_AST = (XmlAst)currentAST.root;
			setPlaceAttribute(identifier_AST,
			LT(0).getLine(),
			LT(0).getColumn(),
			LT(0).getLine(),
			LT(0).getColumn()+identifier_AST.getText().length());
		}
		identifier_AST = (XmlAst)currentAST.root;
		returnAST = identifier_AST;
	}
	
	public final void parameters() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst parameters_AST = null;
		
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		{
			typedecls();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case SEMI:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp8_AST = null;
		tmp8_AST = (XmlAst)astFactory.create(LT(1));
		match(SEMI);
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		{
			pvarDecls();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case RC:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			parameters_AST = (XmlAst)currentAST.root;
			parameters_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(PARAMETERS,"PARAMETERS")).add(parameters_AST));
			setPlaceAttribute(parameters_AST);
			
			currentAST.root = parameters_AST;
			currentAST.child = parameters_AST!=null &&parameters_AST.getFirstChild()!=null ?
				parameters_AST.getFirstChild() : parameters_AST;
			currentAST.advanceChildToEnd();
		}
		parameters_AST = (XmlAst)currentAST.root;
		returnAST = parameters_AST;
	}
	
	public final void contextbody() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst contextbody_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp9_AST = null;
		tmp9_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_BEGIN);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		declarations();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp10_AST = null;
		tmp10_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_END);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+3;
		}
		if ( inputState.guessing==0 ) {
			contextbody_AST = (XmlAst)currentAST.root;
			contextbody_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(CONTEXTBODY,"CONTEXTBODY")).add(contextbody_AST));
			setPlaceAttribute(contextbody_AST, sLine, sCol, eLine, eCol);
			currentAST.root = contextbody_AST;
			currentAST.child = contextbody_AST!=null &&contextbody_AST.getFirstChild()!=null ?
				contextbody_AST.getFirstChild() : contextbody_AST;
			currentAST.advanceChildToEnd();
		}
		contextbody_AST = (XmlAst)currentAST.root;
		returnAST = contextbody_AST;
	}
	
	public final void typedecls() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst typedecls_AST = null;
		XmlAst ids_AST = null;
		int eLine=0, eCol=0;
		
		identifiers();
		if (inputState.guessing==0) {
			ids_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp11_AST = null;
		tmp11_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		XmlAst tmp12_AST = null;
		tmp12_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_TYPE);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+4;
		}
		if ( inputState.guessing==0 ) {
			typedecls_AST = (XmlAst)currentAST.root;
			typedecls_AST = makeTypeDecls(typedecls_AST);
			setPlaceAttribute(typedecls_AST, ids_AST.startLine, ids_AST.startColumn, eLine, eCol);
			currentAST.root = typedecls_AST;
			currentAST.child = typedecls_AST!=null &&typedecls_AST.getFirstChild()!=null ?
				typedecls_AST.getFirstChild() : typedecls_AST;
			currentAST.advanceChildToEnd();
		}
		typedecls_AST = (XmlAst)currentAST.root;
		returnAST = typedecls_AST;
	}
	
	public final void pvarDecls() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst pvarDecls_AST = null;
		
		varDecls();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			pvarDecls_AST = (XmlAst)currentAST.root;
			pvarDecls_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(VARDECLS,"VARDECLS")).add(pvarDecls_AST));
			setPlaceAttribute(pvarDecls_AST);
			currentAST.root = pvarDecls_AST;
			currentAST.child = pvarDecls_AST!=null &&pvarDecls_AST.getFirstChild()!=null ?
				pvarDecls_AST.getFirstChild() : pvarDecls_AST;
			currentAST.advanceChildToEnd();
		}
		pvarDecls_AST = (XmlAst)currentAST.root;
		returnAST = pvarDecls_AST;
	}
	
	public final void varDecls() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst varDecls_AST = null;
		
		varDecl();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop197:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp13_AST = null;
				tmp13_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				varDecl();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop197;
			}
			
		} while (true);
		}
		varDecls_AST = (XmlAst)currentAST.root;
		returnAST = varDecls_AST;
	}
	
	public final void declarations() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst declarations_AST = null;
		
		{
		int _cnt10=0;
		_loop10:
		do {
			if ((LA(1)==IDENTIFIER)) {
				declaration();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				XmlAst tmp14_AST = null;
				tmp14_AST = (XmlAst)astFactory.create(LT(1));
				match(SEMI);
			}
			else {
				if ( _cnt10>=1 ) { break _loop10; } else {throw new NoViableAltException(LT(1), getFilename());}
			}
			
			_cnt10++;
		} while (true);
		}
		declarations_AST = (XmlAst)currentAST.root;
		returnAST = declarations_AST;
	}
	
	public final void declaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst declaration_AST = null;
		
		{
		boolean synPredMatched14 = false;
		if (((LA(1)==IDENTIFIER))) {
			int _m14 = mark();
			synPredMatched14 = true;
			inputState.guessing++;
			try {
				{
				identifier();
				match(CLN);
				match(LITERAL_TYPE);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched14 = false;
			}
			rewind(_m14);
			inputState.guessing--;
		}
		if ( synPredMatched14 ) {
			typeDeclaration();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else {
			boolean synPredMatched16 = false;
			if (((LA(1)==IDENTIFIER))) {
				int _m16 = mark();
				synPredMatched16 = true;
				inputState.guessing++;
				try {
					{
					identifier();
					match(CLN);
					assertionForm();
					}
				}
				catch (RecognitionException pe) {
					synPredMatched16 = false;
				}
				rewind(_m16);
				inputState.guessing--;
			}
			if ( synPredMatched16 ) {
				assertionDeclaration();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				boolean synPredMatched18 = false;
				if (((LA(1)==IDENTIFIER))) {
					int _m18 = mark();
					synPredMatched18 = true;
					inputState.guessing++;
					try {
						{
						identifier();
						match(CLN);
						match(LITERAL_CONTEXT);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched18 = false;
					}
					rewind(_m18);
					inputState.guessing--;
				}
				if ( synPredMatched18 ) {
					contextDeclaration();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else {
					boolean synPredMatched21 = false;
					if (((LA(1)==IDENTIFIER))) {
						int _m21 = mark();
						synPredMatched21 = true;
						inputState.guessing++;
						try {
							{
							identifier();
							{
							switch ( LA(1)) {
							case LB:
							{
								match(LB);
								varDecls();
								match(RB);
								break;
							}
							case CLN:
							{
								break;
							}
							default:
							{
								throw new NoViableAltException(LT(1), getFilename());
							}
							}
							}
							match(CLN);
							match(LITERAL_MODULE);
							}
						}
						catch (RecognitionException pe) {
							synPredMatched21 = false;
						}
						rewind(_m21);
						inputState.guessing--;
					}
					if ( synPredMatched21 ) {
						moduleDeclaration();
						if (inputState.guessing==0) {
							astFactory.addASTChild(currentAST, returnAST);
						}
					}
					else if ((LA(1)==IDENTIFIER)) {
						constantDeclaration();
						if (inputState.guessing==0) {
							astFactory.addASTChild(currentAST, returnAST);
						}
					}
					else {
						throw new NoViableAltException(LT(1), getFilename());
					}
					}}}
					}
					declaration_AST = (XmlAst)currentAST.root;
					returnAST = declaration_AST;
				}
				
	public final void typeDeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst typeDeclaration_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp15_AST = null;
		tmp15_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		XmlAst tmp16_AST = null;
		tmp16_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_TYPE);
		{
		switch ( LA(1)) {
		case EQ:
		{
			XmlAst tmp17_AST = null;
			tmp17_AST = (XmlAst)astFactory.create(LT(1));
			match(EQ);
			typedef();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case SEMI:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			typeDeclaration_AST = (XmlAst)currentAST.root;
			
			typeDeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(TYPEDECLARATION,"TYPEDECLARATION")).add(typeDeclaration_AST));
			setPlaceAttribute(typeDeclaration_AST);
			
			currentAST.root = typeDeclaration_AST;
			currentAST.child = typeDeclaration_AST!=null &&typeDeclaration_AST.getFirstChild()!=null ?
				typeDeclaration_AST.getFirstChild() : typeDeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		typeDeclaration_AST = (XmlAst)currentAST.root;
		returnAST = typeDeclaration_AST;
	}
	
	public final void assertionForm() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst assertionForm_AST = null;
		
		{
		switch ( LA(1)) {
		case LITERAL_OBLIGATION:
		{
			XmlAst tmp18_AST = null;
			if (inputState.guessing==0) {
				tmp18_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp18_AST);
			}
			match(LITERAL_OBLIGATION);
			break;
		}
		case LITERAL_CLAIM:
		{
			XmlAst tmp19_AST = null;
			if (inputState.guessing==0) {
				tmp19_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp19_AST);
			}
			match(LITERAL_CLAIM);
			break;
		}
		case LITERAL_LEMMA:
		{
			XmlAst tmp20_AST = null;
			if (inputState.guessing==0) {
				tmp20_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp20_AST);
			}
			match(LITERAL_LEMMA);
			break;
		}
		case LITERAL_THEOREM:
		{
			XmlAst tmp21_AST = null;
			if (inputState.guessing==0) {
				tmp21_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp21_AST);
			}
			match(LITERAL_THEOREM);
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			assertionForm_AST = (XmlAst)currentAST.root;
			assertionForm_AST = makeAssertionForm(assertionForm_AST);
			setSimplePlaceAttribute(assertionForm_AST);
			currentAST.root = assertionForm_AST;
			currentAST.child = assertionForm_AST!=null &&assertionForm_AST.getFirstChild()!=null ?
				assertionForm_AST.getFirstChild() : assertionForm_AST;
			currentAST.advanceChildToEnd();
		}
		assertionForm_AST = (XmlAst)currentAST.root;
		returnAST = assertionForm_AST;
	}
	
	public final void assertionDeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst assertionDeclaration_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp22_AST = null;
		tmp22_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		assertionForm();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		assertionExpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			assertionDeclaration_AST = (XmlAst)currentAST.root;
			assertionDeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ASSERTIONDECLARATION,"ASSERTIONDECLARATION")).add(assertionDeclaration_AST));
			setPlaceAttribute(assertionDeclaration_AST);
			currentAST.root = assertionDeclaration_AST;
			currentAST.child = assertionDeclaration_AST!=null &&assertionDeclaration_AST.getFirstChild()!=null ?
				assertionDeclaration_AST.getFirstChild() : assertionDeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		assertionDeclaration_AST = (XmlAst)currentAST.root;
		returnAST = assertionDeclaration_AST;
	}
	
	public final void contextDeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst contextDeclaration_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp23_AST = null;
		tmp23_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		XmlAst tmp24_AST = null;
		tmp24_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_CONTEXT);
		XmlAst tmp25_AST = null;
		tmp25_AST = (XmlAst)astFactory.create(LT(1));
		match(EQ);
		contextName();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			contextDeclaration_AST = (XmlAst)currentAST.root;
			contextDeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(CONTEXTDECLARATION,"CONTEXTDECLARATION")).add(contextDeclaration_AST));
			setPlaceAttribute(contextDeclaration_AST);
			currentAST.root = contextDeclaration_AST;
			currentAST.child = contextDeclaration_AST!=null &&contextDeclaration_AST.getFirstChild()!=null ?
				contextDeclaration_AST.getFirstChild() : contextDeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		contextDeclaration_AST = (XmlAst)currentAST.root;
		returnAST = contextDeclaration_AST;
	}
	
	public final void moduleDeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst moduleDeclaration_AST = null;
		XmlAst id_AST = null;
		XmlAst v_AST = null;
		XmlAst m_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
		}
		{
		switch ( LA(1)) {
		case LB:
		{
			XmlAst tmp26_AST = null;
			tmp26_AST = (XmlAst)astFactory.create(LT(1));
			match(LB);
			varDecls();
			if (inputState.guessing==0) {
				v_AST = (XmlAst)returnAST;
			}
			XmlAst tmp27_AST = null;
			tmp27_AST = (XmlAst)astFactory.create(LT(1));
			match(RB);
			break;
		}
		case CLN:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp28_AST = null;
		tmp28_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		XmlAst tmp29_AST = null;
		tmp29_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_MODULE);
		XmlAst tmp30_AST = null;
		tmp30_AST = (XmlAst)astFactory.create(LT(1));
		match(EQ);
		module();
		if (inputState.guessing==0) {
			m_AST = (XmlAst)returnAST;
		}
		if ( inputState.guessing==0 ) {
			moduleDeclaration_AST = (XmlAst)currentAST.root;
			moduleDeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(4)).add((XmlAst)astFactory.create(MODULEDECLARATION,"MODULEDECLARATION")).add(id_AST).add((XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(VARDECLS,"VARDECLS")).add(v_AST))).add(m_AST));
			setPlaceAttribute(moduleDeclaration_AST);
			currentAST.root = moduleDeclaration_AST;
			currentAST.child = moduleDeclaration_AST!=null &&moduleDeclaration_AST.getFirstChild()!=null ?
				moduleDeclaration_AST.getFirstChild() : moduleDeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		returnAST = moduleDeclaration_AST;
	}
	
	public final void constantDeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst constantDeclaration_AST = null;
		XmlAst id_AST = null;
		XmlAst v_AST = null;
		XmlAst t_AST = null;
		XmlAst e_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
		}
		{
		switch ( LA(1)) {
		case LP:
		{
			XmlAst tmp31_AST = null;
			tmp31_AST = (XmlAst)astFactory.create(LT(1));
			match(LP);
			varDecls();
			if (inputState.guessing==0) {
				v_AST = (XmlAst)returnAST;
			}
			XmlAst tmp32_AST = null;
			tmp32_AST = (XmlAst)astFactory.create(LT(1));
			match(RP);
			break;
		}
		case CLN:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp33_AST = null;
		tmp33_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		type();
		if (inputState.guessing==0) {
			t_AST = (XmlAst)returnAST;
		}
		{
		switch ( LA(1)) {
		case EQ:
		{
			XmlAst tmp34_AST = null;
			tmp34_AST = (XmlAst)astFactory.create(LT(1));
			match(EQ);
			expression();
			if (inputState.guessing==0) {
				e_AST = (XmlAst)returnAST;
			}
			break;
		}
		case SEMI:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			constantDeclaration_AST = (XmlAst)currentAST.root;
			constantDeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(5)).add((XmlAst)astFactory.create(CONSTANTDECLARATION,"CONSTANTDECLARATION")).add(id_AST).add((XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(VARDECLS,"VARDECLS")).add(v_AST))).add(t_AST).add(e_AST));
			setPlaceAttribute(constantDeclaration_AST);
			currentAST.root = constantDeclaration_AST;
			currentAST.child = constantDeclaration_AST!=null &&constantDeclaration_AST.getFirstChild()!=null ?
				constantDeclaration_AST.getFirstChild() : constantDeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		returnAST = constantDeclaration_AST;
	}
	
	public final void type() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst type_AST = null;
		
		switch ( LA(1)) {
		case REAL:
		case NZREAL:
		case INTEGER:
		case NZINTEGER:
		case NATURAL:
		case BOOLEAN:
		{
			basictype();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			type_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_ARRAY:
		{
			arraytype();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			type_AST = (XmlAst)currentAST.root;
			break;
		}
		case RECS:
		{
			recordtype();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			type_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
			boolean synPredMatched59 = false;
			if (((_tokenSet_0.member(LA(1))))) {
				int _m59 = mark();
				synPredMatched59 = true;
				inputState.guessing++;
				try {
					{
					module();
					match(DOT);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched59 = false;
				}
				rewind(_m59);
				inputState.guessing--;
			}
			if ( synPredMatched59 ) {
				statetype();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				type_AST = (XmlAst)currentAST.root;
			}
			else if ((LA(1)==IDENTIFIER)) {
				typeName();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				type_AST = (XmlAst)currentAST.root;
			}
			else {
				boolean synPredMatched61 = false;
				if (((LA(1)==LB))) {
					int _m61 = mark();
					synPredMatched61 = true;
					inputState.guessing++;
					try {
						{
						subrange();
						}
					}
					catch (RecognitionException pe) {
						synPredMatched61 = false;
					}
					rewind(_m61);
					inputState.guessing--;
				}
				if ( synPredMatched61 ) {
					subrange();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
					type_AST = (XmlAst)currentAST.root;
				}
				else {
					boolean synPredMatched63 = false;
					if (((LA(1)==LB))) {
						int _m63 = mark();
						synPredMatched63 = true;
						inputState.guessing++;
						try {
							{
							functiontype();
							}
						}
						catch (RecognitionException pe) {
							synPredMatched63 = false;
						}
						rewind(_m63);
						inputState.guessing--;
					}
					if ( synPredMatched63 ) {
						functiontype();
						if (inputState.guessing==0) {
							astFactory.addASTChild(currentAST, returnAST);
						}
						type_AST = (XmlAst)currentAST.root;
					}
					else if ((LA(1)==LB)) {
						tupletype();
						if (inputState.guessing==0) {
							astFactory.addASTChild(currentAST, returnAST);
						}
						type_AST = (XmlAst)currentAST.root;
					}
				else {
					throw new NoViableAltException(LT(1), getFilename());
				}
				}}}
				returnAST = type_AST;
			}
			
	public final void expression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst expression_AST = null;
		
		iffExpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		expression_AST = (XmlAst)currentAST.root;
		returnAST = expression_AST;
	}
	
	public final void typedef() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst typedef_AST = null;
		
		switch ( LA(1)) {
		case IDENTIFIER:
		case REAL:
		case NZREAL:
		case INTEGER:
		case NZINTEGER:
		case NATURAL:
		case BOOLEAN:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case LITERAL_ARRAY:
		case RECS:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		{
			type();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			typedef_AST = (XmlAst)currentAST.root;
			break;
		}
		case LC:
		{
			setexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			typedef_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_DATATYPE:
		{
			datatype();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			typedef_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = typedef_AST;
	}
	
	public final void assertionExpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst assertionExpression_AST = null;
		
		{
		boolean synPredMatched33 = false;
		if (((_tokenSet_1.member(LA(1))))) {
			int _m33 = mark();
			synPredMatched33 = true;
			inputState.guessing++;
			try {
				{
				switch ( LA(1)) {
				case AND:
				{
					match(AND);
					break;
				}
				case OR:
				{
					match(OR);
					break;
				}
				case IMPLIES:
				{
					match(IMPLIES);
					break;
				}
				case IFF:
				{
					match(IFF);
					break;
				}
				case NOT:
				{
					match(NOT);
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
			}
			catch (RecognitionException pe) {
				synPredMatched33 = false;
			}
			rewind(_m33);
			inputState.guessing--;
		}
		if ( synPredMatched33 ) {
			assertionProposition();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else {
			boolean synPredMatched35 = false;
			if (((LA(1)==LITERAL_FORALL||LA(1)==LITERAL_EXISTS))) {
				int _m35 = mark();
				synPredMatched35 = true;
				inputState.guessing++;
				try {
					{
					switch ( LA(1)) {
					case LITERAL_FORALL:
					{
						match(LITERAL_FORALL);
						break;
					}
					case LITERAL_EXISTS:
					{
						match(LITERAL_EXISTS);
						break;
					}
					default:
					{
						throw new NoViableAltException(LT(1), getFilename());
					}
					}
					}
				}
				catch (RecognitionException pe) {
					synPredMatched35 = false;
				}
				rewind(_m35);
				inputState.guessing--;
			}
			if ( synPredMatched35 ) {
				quantifiedAssertion();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				boolean synPredMatched38 = false;
				if (((_tokenSet_0.member(LA(1))))) {
					int _m38 = mark();
					synPredMatched38 = true;
					inputState.guessing++;
					try {
						{
						module();
						{
						switch ( LA(1)) {
						case TURNSTILE:
						{
							moduleModels();
							break;
						}
						case LITERAL_IMPLEMENTS:
						{
							moduleImplements();
							break;
						}
						default:
						{
							throw new NoViableAltException(LT(1), getFilename());
						}
						}
						}
						}
					}
					catch (RecognitionException pe) {
						synPredMatched38 = false;
					}
					rewind(_m38);
					inputState.guessing--;
				}
				if ( synPredMatched38 ) {
					moduleAssertion();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else if ((_tokenSet_2.member(LA(1)))) {
					expression();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else {
					throw new NoViableAltException(LT(1), getFilename());
				}
				}}
				}
				assertionExpression_AST = (XmlAst)currentAST.root;
				returnAST = assertionExpression_AST;
			}
			
	public final void assertionProposition() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst assertionProposition_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		{
		switch ( LA(1)) {
		case OR:
		case AND:
		case IMPLIES:
		case IFF:
		{
			{
			{
			switch ( LA(1)) {
			case AND:
			{
				XmlAst tmp35_AST = null;
				if (inputState.guessing==0) {
					tmp35_AST = (XmlAst)astFactory.create(LT(1));
					astFactory.addASTChild(currentAST, tmp35_AST);
				}
				match(AND);
				break;
			}
			case OR:
			{
				XmlAst tmp36_AST = null;
				if (inputState.guessing==0) {
					tmp36_AST = (XmlAst)astFactory.create(LT(1));
					astFactory.addASTChild(currentAST, tmp36_AST);
				}
				match(OR);
				break;
			}
			case IMPLIES:
			{
				XmlAst tmp37_AST = null;
				if (inputState.guessing==0) {
					tmp37_AST = (XmlAst)astFactory.create(LT(1));
					astFactory.addASTChild(currentAST, tmp37_AST);
				}
				match(IMPLIES);
				break;
			}
			case IFF:
			{
				XmlAst tmp38_AST = null;
				if (inputState.guessing==0) {
					tmp38_AST = (XmlAst)astFactory.create(LT(1));
					astFactory.addASTChild(currentAST, tmp38_AST);
				}
				match(IFF);
				break;
			}
			default:
			{
				throw new NoViableAltException(LT(1), getFilename());
			}
			}
			}
			if ( inputState.guessing==0 ) {
				sLine = LT(0).getLine(); sCol = LT(0).getColumn();
			}
			XmlAst tmp39_AST = null;
			tmp39_AST = (XmlAst)astFactory.create(LT(1));
			match(LP);
			assertionExpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp40_AST = null;
			tmp40_AST = (XmlAst)astFactory.create(LT(1));
			match(COMMA);
			assertionExpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp41_AST = null;
			tmp41_AST = (XmlAst)astFactory.create(LT(1));
			match(RP);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			}
			break;
		}
		case NOT:
		{
			{
			XmlAst tmp42_AST = null;
			if (inputState.guessing==0) {
				tmp42_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp42_AST);
			}
			match(NOT);
			if ( inputState.guessing==0 ) {
				sLine = LT(0).getLine(); sCol = LT(0).getColumn();
			}
			XmlAst tmp43_AST = null;
			tmp43_AST = (XmlAst)astFactory.create(LT(1));
			match(LP);
			assertionExpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp44_AST = null;
			tmp44_AST = (XmlAst)astFactory.create(LT(1));
			match(RP);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			}
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			assertionProposition_AST = (XmlAst)currentAST.root;
			assertionProposition_AST = makeAssertionProposition(assertionProposition_AST);
			setPlaceAttribute(assertionProposition_AST, sLine, sCol, eLine, eCol);
			currentAST.root = assertionProposition_AST;
			currentAST.child = assertionProposition_AST!=null &&assertionProposition_AST.getFirstChild()!=null ?
				assertionProposition_AST.getFirstChild() : assertionProposition_AST;
			currentAST.advanceChildToEnd();
		}
		assertionProposition_AST = (XmlAst)currentAST.root;
		returnAST = assertionProposition_AST;
	}
	
	public final void quantifiedAssertion() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst quantifiedAssertion_AST = null;
		XmlAst aexp_AST = null;
		int sLine=0, sCol=0;
		
		{
		switch ( LA(1)) {
		case LITERAL_FORALL:
		{
			XmlAst tmp45_AST = null;
			if (inputState.guessing==0) {
				tmp45_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp45_AST);
			}
			match(LITERAL_FORALL);
			break;
		}
		case LITERAL_EXISTS:
		{
			XmlAst tmp46_AST = null;
			if (inputState.guessing==0) {
				tmp46_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp46_AST);
			}
			match(LITERAL_EXISTS);
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		XmlAst tmp47_AST = null;
		tmp47_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		pvarDecls();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp48_AST = null;
		tmp48_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		XmlAst tmp49_AST = null;
		tmp49_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		assertionExpression();
		if (inputState.guessing==0) {
			aexp_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			quantifiedAssertion_AST = (XmlAst)currentAST.root;
			quantifiedAssertion_AST = makeQuantifiedAssertion(quantifiedAssertion_AST);
			setPlaceAttribute(quantifiedAssertion_AST, sLine, sCol, aexp_AST.endLine, aexp_AST.endColumn);
			currentAST.root = quantifiedAssertion_AST;
			currentAST.child = quantifiedAssertion_AST!=null &&quantifiedAssertion_AST.getFirstChild()!=null ?
				quantifiedAssertion_AST.getFirstChild() : quantifiedAssertion_AST;
			currentAST.advanceChildToEnd();
		}
		quantifiedAssertion_AST = (XmlAst)currentAST.root;
		returnAST = quantifiedAssertion_AST;
	}
	
	public final void module() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst module_AST = null;
		
		basicmodule();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop232:
		do {
			if ((LA(1)==ASYNC||LA(1)==SYNC)) {
				{
				switch ( LA(1)) {
				case ASYNC:
				{
					XmlAst tmp50_AST = null;
					if (inputState.guessing==0) {
						tmp50_AST = (XmlAst)astFactory.create(LT(1));
						astFactory.addASTChild(currentAST, tmp50_AST);
					}
					match(ASYNC);
					break;
				}
				case SYNC:
				{
					XmlAst tmp51_AST = null;
					if (inputState.guessing==0) {
						tmp51_AST = (XmlAst)astFactory.create(LT(1));
						astFactory.addASTChild(currentAST, tmp51_AST);
					}
					match(SYNC);
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
				basicmodule();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop232;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			module_AST = (XmlAst)currentAST.root;
			module_AST = makeInfixModule(module_AST);
			currentAST.root = module_AST;
			currentAST.child = module_AST!=null &&module_AST.getFirstChild()!=null ?
				module_AST.getFirstChild() : module_AST;
			currentAST.advanceChildToEnd();
		}
		module_AST = (XmlAst)currentAST.root;
		returnAST = module_AST;
	}
	
	public final void moduleModels() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst moduleModels_AST = null;
		
		XmlAst tmp52_AST = null;
		tmp52_AST = (XmlAst)astFactory.create(LT(1));
		match(TURNSTILE);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		moduleModels_AST = (XmlAst)currentAST.root;
		returnAST = moduleModels_AST;
	}
	
	public final void moduleImplements() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst moduleImplements_AST = null;
		
		XmlAst tmp53_AST = null;
		tmp53_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IMPLEMENTS);
		module();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		moduleImplements_AST = (XmlAst)currentAST.root;
		returnAST = moduleImplements_AST;
	}
	
	public final void moduleAssertion() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst moduleAssertion_AST = null;
		XmlAst m_AST = null;
		XmlAst i_AST = null;
		
		module();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		switch ( LA(1)) {
		case TURNSTILE:
		{
			moduleModels();
			if (inputState.guessing==0) {
				m_AST = (XmlAst)returnAST;
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LITERAL_IMPLEMENTS:
		{
			moduleImplements();
			if (inputState.guessing==0) {
				i_AST = (XmlAst)returnAST;
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			moduleAssertion_AST = (XmlAst)currentAST.root;
			if (m_AST != null) {
			moduleAssertion_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MODULEMODELS,"MODULEMODELS")).add(moduleAssertion_AST));
			} else {
			moduleAssertion_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MODULEIMPLEMENTS,"MODULEIMPLEMENTS")).add(moduleAssertion_AST));
			}
			setPlaceAttribute(moduleAssertion_AST);
			
			currentAST.root = moduleAssertion_AST;
			currentAST.child = moduleAssertion_AST!=null &&moduleAssertion_AST.getFirstChild()!=null ?
				moduleAssertion_AST.getFirstChild() : moduleAssertion_AST;
			currentAST.advanceChildToEnd();
		}
		moduleAssertion_AST = (XmlAst)currentAST.root;
		returnAST = moduleAssertion_AST;
	}
	
	public final void moduleRefines() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst moduleRefines_AST = null;
		
		XmlAst tmp54_AST = null;
		tmp54_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_REFINES);
		module();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		moduleRefines_AST = (XmlAst)currentAST.root;
		returnAST = moduleRefines_AST;
	}
	
	public final void contextName() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst contextName_AST = null;
		XmlAst id_AST = null;
		int eLine=-1, eCol=-1;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		switch ( LA(1)) {
		case LC:
		{
			XmlAst tmp55_AST = null;
			tmp55_AST = (XmlAst)astFactory.create(LT(1));
			match(LC);
			actualparameters();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp56_AST = null;
			tmp56_AST = (XmlAst)astFactory.create(LT(1));
			match(RC);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			break;
		}
		case SEMI:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			contextName_AST = (XmlAst)currentAST.root;
			contextName_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(CONTEXTNAME,"CONTEXTNAME")).add(contextName_AST));
			if (eCol != -1)
			setPlaceAttribute(contextName_AST, id_AST.startLine, id_AST.startColumn, eLine, eCol);
			else
			setPlaceAttribute(contextName_AST);
			currentAST.root = contextName_AST;
			currentAST.child = contextName_AST!=null &&contextName_AST.getFirstChild()!=null ?
				contextName_AST.getFirstChild() : contextName_AST;
			currentAST.advanceChildToEnd();
		}
		contextName_AST = (XmlAst)currentAST.root;
		returnAST = contextName_AST;
	}
	
	public final void actualparameters() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst actualparameters_AST = null;
		
		{
		if ((_tokenSet_3.member(LA(1)))) {
			actualtypes();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else if ((LA(1)==SEMI)) {
		}
		else {
			throw new NoViableAltException(LT(1), getFilename());
		}
		
		}
		XmlAst tmp57_AST = null;
		tmp57_AST = (XmlAst)astFactory.create(LT(1));
		match(SEMI);
		{
		if ((_tokenSet_4.member(LA(1)))) {
			actualexprs();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else if ((LA(1)==RC)) {
		}
		else {
			throw new NoViableAltException(LT(1), getFilename());
		}
		
		}
		if ( inputState.guessing==0 ) {
			actualparameters_AST = (XmlAst)currentAST.root;
			actualparameters_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ACTUALPARAMETERS,"ACTUALPARAMETERS")).add(actualparameters_AST));
			setPlaceAttribute(actualparameters_AST);
			currentAST.root = actualparameters_AST;
			currentAST.child = actualparameters_AST!=null &&actualparameters_AST.getFirstChild()!=null ?
				actualparameters_AST.getFirstChild() : actualparameters_AST;
			currentAST.advanceChildToEnd();
		}
		actualparameters_AST = (XmlAst)currentAST.root;
		returnAST = actualparameters_AST;
	}
	
	public final void setexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst setexpression_AST = null;
		
		boolean synPredMatched168 = false;
		if (((LA(1)==LC))) {
			int _m168 = mark();
			synPredMatched168 = true;
			inputState.guessing++;
			try {
				{
				setpredexpression();
				}
			}
			catch (RecognitionException pe) {
				synPredMatched168 = false;
			}
			rewind(_m168);
			inputState.guessing--;
		}
		if ( synPredMatched168 ) {
			setpredexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			setexpression_AST = (XmlAst)currentAST.root;
		}
		else if ((LA(1)==LC)) {
			setlistexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			setexpression_AST = (XmlAst)currentAST.root;
		}
		else {
			throw new NoViableAltException(LT(1), getFilename());
		}
		
		returnAST = setexpression_AST;
	}
	
	public final void datatype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst datatype_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp58_AST = null;
		if (inputState.guessing==0) {
			tmp58_AST = (XmlAst)astFactory.create(LT(1));
			astFactory.makeASTRoot(currentAST, tmp58_AST);
		}
		match(LITERAL_DATATYPE);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		constructors();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp59_AST = null;
		tmp59_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_END);
		if ( inputState.guessing==0 ) {
			datatype_AST = (XmlAst)currentAST.root;
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+3;
			setPlaceAttribute(datatype_AST, sLine, sCol, eLine, eCol);
		}
		datatype_AST = (XmlAst)currentAST.root;
		returnAST = datatype_AST;
	}
	
	public final void basictype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst basictype_AST = null;
		
		{
		switch ( LA(1)) {
		case REAL:
		{
			XmlAst tmp60_AST = null;
			if (inputState.guessing==0) {
				tmp60_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp60_AST);
			}
			match(REAL);
			break;
		}
		case NZREAL:
		{
			XmlAst tmp61_AST = null;
			if (inputState.guessing==0) {
				tmp61_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp61_AST);
			}
			match(NZREAL);
			break;
		}
		case INTEGER:
		{
			XmlAst tmp62_AST = null;
			if (inputState.guessing==0) {
				tmp62_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp62_AST);
			}
			match(INTEGER);
			break;
		}
		case NZINTEGER:
		{
			XmlAst tmp63_AST = null;
			if (inputState.guessing==0) {
				tmp63_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp63_AST);
			}
			match(NZINTEGER);
			break;
		}
		case NATURAL:
		{
			XmlAst tmp64_AST = null;
			if (inputState.guessing==0) {
				tmp64_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp64_AST);
			}
			match(NATURAL);
			break;
		}
		case BOOLEAN:
		{
			XmlAst tmp65_AST = null;
			if (inputState.guessing==0) {
				tmp65_AST = (XmlAst)astFactory.create(LT(1));
				astFactory.addASTChild(currentAST, tmp65_AST);
			}
			match(BOOLEAN);
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			basictype_AST = (XmlAst)currentAST.root;
			basictype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(TYPENAME,"TYPENAME")).add(basictype_AST));
			setSimplePlaceAttribute(basictype_AST);
			currentAST.root = basictype_AST;
			currentAST.child = basictype_AST!=null &&basictype_AST.getFirstChild()!=null ?
				basictype_AST.getFirstChild() : basictype_AST;
			currentAST.advanceChildToEnd();
		}
		basictype_AST = (XmlAst)currentAST.root;
		returnAST = basictype_AST;
	}
	
	public final void statetype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst statetype_AST = null;
		XmlAst mod_AST = null;
		int eLine=0, eCol=0;
		
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp66_AST = null;
		tmp66_AST = (XmlAst)astFactory.create(LT(1));
		match(DOT);
		XmlAst tmp67_AST = null;
		tmp67_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_STATE);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+5;
		}
		if ( inputState.guessing==0 ) {
			statetype_AST = (XmlAst)currentAST.root;
			statetype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(STATETYPE,"STATETYPE")).add(statetype_AST));
			setPlaceAttribute(statetype_AST, mod_AST.startLine, mod_AST.startColumn, eLine, eCol);
			currentAST.root = statetype_AST;
			currentAST.child = statetype_AST!=null &&statetype_AST.getFirstChild()!=null ?
				statetype_AST.getFirstChild() : statetype_AST;
			currentAST.advanceChildToEnd();
		}
		statetype_AST = (XmlAst)currentAST.root;
		returnAST = statetype_AST;
	}
	
	public final void typeName() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst typeName_AST = null;
		
		name();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			typeName_AST = (XmlAst)currentAST.root;
			typeName_AST = makeTypeName((XmlAst)typeName_AST);
			currentAST.root = typeName_AST;
			currentAST.child = typeName_AST!=null &&typeName_AST.getFirstChild()!=null ?
				typeName_AST.getFirstChild() : typeName_AST;
			currentAST.advanceChildToEnd();
		}
		typeName_AST = (XmlAst)currentAST.root;
		returnAST = typeName_AST;
	}
	
	public final void subrange() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst subrange_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp68_AST = null;
		tmp68_AST = (XmlAst)astFactory.create(LT(1));
		match(LB);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		bound();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp69_AST = null;
		tmp69_AST = (XmlAst)astFactory.create(LT(1));
		match(DOTDOT);
		bound();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp70_AST = null;
		tmp70_AST = (XmlAst)astFactory.create(LT(1));
		match(RB);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			subrange_AST = (XmlAst)currentAST.root;
			subrange_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(SUBRANGE,"SUBRANGE")).add(subrange_AST));
			setPlaceAttribute(subrange_AST, sLine, sCol, eLine, eCol);
			currentAST.root = subrange_AST;
			currentAST.child = subrange_AST!=null &&subrange_AST.getFirstChild()!=null ?
				subrange_AST.getFirstChild() : subrange_AST;
			currentAST.advanceChildToEnd();
		}
		subrange_AST = (XmlAst)currentAST.root;
		returnAST = subrange_AST;
	}
	
	public final void arraytype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst arraytype_AST = null;
		XmlAst t_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp71_AST = null;
		tmp71_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_ARRAY);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		indextype();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp72_AST = null;
		tmp72_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_OF);
		type();
		if (inputState.guessing==0) {
			t_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			arraytype_AST = (XmlAst)currentAST.root;
			arraytype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ARRAYTYPE,"ARRAYTYPE")).add(arraytype_AST));
			setPlaceAttribute(arraytype_AST, sLine, sCol, t_AST.endLine, t_AST.endColumn);
			currentAST.root = arraytype_AST;
			currentAST.child = arraytype_AST!=null &&arraytype_AST.getFirstChild()!=null ?
				arraytype_AST.getFirstChild() : arraytype_AST;
			currentAST.advanceChildToEnd();
		}
		arraytype_AST = (XmlAst)currentAST.root;
		returnAST = arraytype_AST;
	}
	
	public final void functiontype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst functiontype_AST = null;
		int sline=0; int scol=0;
		
		XmlAst tmp73_AST = null;
		tmp73_AST = (XmlAst)astFactory.create(LT(1));
		match(LB);
		if ( inputState.guessing==0 ) {
			sline = LT(0).getLine(); scol = LT(0).getColumn();
		}
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp74_AST = null;
		tmp74_AST = (XmlAst)astFactory.create(LT(1));
		match(ARROW);
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp75_AST = null;
		tmp75_AST = (XmlAst)astFactory.create(LT(1));
		match(RB);
		if ( inputState.guessing==0 ) {
			functiontype_AST = (XmlAst)currentAST.root;
			functiontype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(FUNCTIONTYPE,"FUNCTIONTYPE")).add(functiontype_AST));
			setPlaceAttribute(functiontype_AST, sline, scol,
			LT(0).getLine(), LT(0).getColumn()+1);
			currentAST.root = functiontype_AST;
			currentAST.child = functiontype_AST!=null &&functiontype_AST.getFirstChild()!=null ?
				functiontype_AST.getFirstChild() : functiontype_AST;
			currentAST.advanceChildToEnd();
		}
		functiontype_AST = (XmlAst)currentAST.root;
		returnAST = functiontype_AST;
	}
	
	public final void tupletype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst tupletype_AST = null;
		int sline=0; int scol=0;
		
		XmlAst tmp76_AST = null;
		tmp76_AST = (XmlAst)astFactory.create(LT(1));
		match(LB);
		if ( inputState.guessing==0 ) {
			sline = LT(0).getLine(); scol = LT(0).getColumn();
		}
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		int _cnt95=0;
		_loop95:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp77_AST = null;
				tmp77_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				type();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				if ( _cnt95>=1 ) { break _loop95; } else {throw new NoViableAltException(LT(1), getFilename());}
			}
			
			_cnt95++;
		} while (true);
		}
		XmlAst tmp78_AST = null;
		tmp78_AST = (XmlAst)astFactory.create(LT(1));
		match(RB);
		if ( inputState.guessing==0 ) {
			tupletype_AST = (XmlAst)currentAST.root;
			tupletype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(TUPLETYPE,"TUPLETYPE")).add(tupletype_AST));
			setPlaceAttribute(tupletype_AST, sline, scol,
			LT(0).getLine(), LT(0).getColumn()+1);
			currentAST.root = tupletype_AST;
			currentAST.child = tupletype_AST!=null &&tupletype_AST.getFirstChild()!=null ?
				tupletype_AST.getFirstChild() : tupletype_AST;
			currentAST.advanceChildToEnd();
		}
		tupletype_AST = (XmlAst)currentAST.root;
		returnAST = tupletype_AST;
	}
	
	public final void recordtype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst recordtype_AST = null;
		int sline=0; int scol=0;
		
		XmlAst tmp79_AST = null;
		tmp79_AST = (XmlAst)astFactory.create(LT(1));
		match(RECS);
		if ( inputState.guessing==0 ) {
			sline = LT(0).getLine(); scol = LT(0).getColumn();
		}
		fielddeclaration();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop99:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp80_AST = null;
				tmp80_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				fielddeclaration();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop99;
			}
			
		} while (true);
		}
		XmlAst tmp81_AST = null;
		tmp81_AST = (XmlAst)astFactory.create(LT(1));
		match(RECE);
		if ( inputState.guessing==0 ) {
			recordtype_AST = (XmlAst)currentAST.root;
			recordtype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RECORDTYPE,"RECORDTYPE")).add(recordtype_AST));
			setPlaceAttribute(recordtype_AST, sline, scol,
			LT(0).getLine(), LT(0).getColumn()+2);
			currentAST.root = recordtype_AST;
			currentAST.child = recordtype_AST!=null &&recordtype_AST.getFirstChild()!=null ?
				recordtype_AST.getFirstChild() : recordtype_AST;
			currentAST.advanceChildToEnd();
		}
		recordtype_AST = (XmlAst)currentAST.root;
		returnAST = recordtype_AST;
	}
	
	public final void name() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst name_AST = null;
		
		boolean synPredMatched84 = false;
		if (((LA(1)==IDENTIFIER))) {
			int _m84 = mark();
			synPredMatched84 = true;
			inputState.guessing++;
			try {
				{
				fullname();
				}
			}
			catch (RecognitionException pe) {
				synPredMatched84 = false;
			}
			rewind(_m84);
			inputState.guessing--;
		}
		if ( synPredMatched84 ) {
			fullname();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			name_AST = (XmlAst)currentAST.root;
		}
		else if ((LA(1)==IDENTIFIER)) {
			identifier();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			name_AST = (XmlAst)currentAST.root;
		}
		else {
			throw new NoViableAltException(LT(1), getFilename());
		}
		
		returnAST = name_AST;
	}
	
	public final void scalartype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst scalartype_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp82_AST = null;
		tmp82_AST = (XmlAst)astFactory.create(LT(1));
		match(LC);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		scalarElements();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp83_AST = null;
		tmp83_AST = (XmlAst)astFactory.create(LT(1));
		match(RC);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			scalartype_AST = (XmlAst)currentAST.root;
			scalartype_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(SCALARTYPE,"SCALARTYPE")).add(scalartype_AST));
			setPlaceAttribute(scalartype_AST, sLine, sCol, eLine, eCol);
			currentAST.root = scalartype_AST;
			currentAST.child = scalartype_AST!=null &&scalartype_AST.getFirstChild()!=null ?
				scalartype_AST.getFirstChild() : scalartype_AST;
			currentAST.advanceChildToEnd();
		}
		scalartype_AST = (XmlAst)currentAST.root;
		returnAST = scalartype_AST;
	}
	
	public final void scalarElements() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst scalarElements_AST = null;
		
		scalarElement();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop68:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp84_AST = null;
				tmp84_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				scalarElement();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop68;
			}
			
		} while (true);
		}
		scalarElements_AST = (XmlAst)currentAST.root;
		returnAST = scalarElements_AST;
	}
	
	public final void scalarElement() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst scalarElement_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			scalarElement_AST = (XmlAst)currentAST.root;
			scalarElement_AST = makeScalarElement((XmlAst)scalarElement_AST);
			currentAST.root = scalarElement_AST;
			currentAST.child = scalarElement_AST!=null &&scalarElement_AST.getFirstChild()!=null ?
				scalarElement_AST.getFirstChild() : scalarElement_AST;
			currentAST.advanceChildToEnd();
		}
		scalarElement_AST = (XmlAst)currentAST.root;
		returnAST = scalarElement_AST;
	}
	
	public final void constructors() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst constructors_AST = null;
		
		constructor();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop73:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp85_AST = null;
				tmp85_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				constructor();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop73;
			}
			
		} while (true);
		}
		constructors_AST = (XmlAst)currentAST.root;
		returnAST = constructors_AST;
	}
	
	public final void constructor() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst constructor_AST = null;
		XmlAst id_AST = null;
		int eLine=0, eCol=0;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		switch ( LA(1)) {
		case LP:
		{
			XmlAst tmp86_AST = null;
			tmp86_AST = (XmlAst)astFactory.create(LT(1));
			match(LP);
			accessors();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp87_AST = null;
			tmp87_AST = (XmlAst)astFactory.create(LT(1));
			match(RP);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			break;
		}
		case LITERAL_END:
		case COMMA:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			constructor_AST = (XmlAst)currentAST.root;
			constructor_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(CONSTRUCTOR,"CONSTRUCTOR")).add(constructor_AST));
			if (eLine != 0)
			setPlaceAttribute(constructor_AST, id_AST.startLine, id_AST.startColumn, eLine, eCol);
			else
			setPlaceAttribute(constructor_AST);
			currentAST.root = constructor_AST;
			currentAST.child = constructor_AST!=null &&constructor_AST.getFirstChild()!=null ?
				constructor_AST.getFirstChild() : constructor_AST;
			currentAST.advanceChildToEnd();
		}
		constructor_AST = (XmlAst)currentAST.root;
		returnAST = constructor_AST;
	}
	
	public final void accessors() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst accessors_AST = null;
		
		accessor();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop78:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp88_AST = null;
				tmp88_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				accessor();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop78;
			}
			
		} while (true);
		}
		accessors_AST = (XmlAst)currentAST.root;
		returnAST = accessors_AST;
	}
	
	public final void accessor() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst accessor_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp89_AST = null;
		tmp89_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			accessor_AST = (XmlAst)currentAST.root;
			accessor_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ACCESSOR,"ACCESSOR")).add(accessor_AST));
			setPlaceAttribute(accessor_AST);
			currentAST.root = accessor_AST;
			currentAST.child = accessor_AST!=null &&accessor_AST.getFirstChild()!=null ?
				accessor_AST.getFirstChild() : accessor_AST;
			currentAST.advanceChildToEnd();
		}
		accessor_AST = (XmlAst)currentAST.root;
		returnAST = accessor_AST;
	}
	
	public final void indextype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst indextype_AST = null;
		
		switch ( LA(1)) {
		case INTEGER:
		{
			integertype();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			if ( inputState.guessing==0 ) {
				indextype_AST = (XmlAst)currentAST.root;
				indextype_AST = makeTypeName((XmlAst)indextype_AST);
				currentAST.root = indextype_AST;
				currentAST.child = indextype_AST!=null &&indextype_AST.getFirstChild()!=null ?
					indextype_AST.getFirstChild() : indextype_AST;
				currentAST.advanceChildToEnd();
			}
			indextype_AST = (XmlAst)currentAST.root;
			break;
		}
		case IDENTIFIER:
		{
			name();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			if ( inputState.guessing==0 ) {
				indextype_AST = (XmlAst)currentAST.root;
				indextype_AST = makeTypeName((XmlAst)indextype_AST);
				currentAST.root = indextype_AST;
				currentAST.child = indextype_AST!=null &&indextype_AST.getFirstChild()!=null ?
					indextype_AST.getFirstChild() : indextype_AST;
				currentAST.advanceChildToEnd();
			}
			indextype_AST = (XmlAst)currentAST.root;
			break;
		}
		case LB:
		{
			subrange();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			indextype_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = indextype_AST;
	}
	
	public final void integertype() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst integertype_AST = null;
		Token  i = null;
		XmlAst i_AST = null;
		
		i = LT(1);
		if (inputState.guessing==0) {
			i_AST = (XmlAst)astFactory.create(i);
			astFactory.makeASTRoot(currentAST, i_AST);
		}
		match(INTEGER);
		if ( inputState.guessing==0 ) {
			integertype_AST = (XmlAst)currentAST.root;
			setPlaceAttribute(integertype_AST, i_AST);
		}
		integertype_AST = (XmlAst)currentAST.root;
		returnAST = integertype_AST;
	}
	
	public final void fullname() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst fullname_AST = null;
		XmlAst cid_AST = null;
		XmlAst p_AST = null;
		XmlAst id_AST = null;
		int eLine=0, eCol=0;
		
		identifier();
		if (inputState.guessing==0) {
			cid_AST = (XmlAst)returnAST;
		}
		{
		switch ( LA(1)) {
		case LC:
		{
			XmlAst tmp90_AST = null;
			tmp90_AST = (XmlAst)astFactory.create(LT(1));
			match(LC);
			actualparameters();
			if (inputState.guessing==0) {
				p_AST = (XmlAst)returnAST;
			}
			XmlAst tmp91_AST = null;
			tmp91_AST = (XmlAst)astFactory.create(LT(1));
			match(RC);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			break;
		}
		case BANG:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp92_AST = null;
		tmp92_AST = (XmlAst)astFactory.create(LT(1));
		match(BANG);
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
		}
		if ( inputState.guessing==0 ) {
			fullname_AST = (XmlAst)currentAST.root;
			XmlAst ctxName = (XmlAst)astFactory.make( (new ASTArray(3)).add((XmlAst)astFactory.create(CONTEXTNAME,"CONTEXTNAME")).add(cid_AST).add(p_AST));
			if (eLine == 0)
			setPlaceAttribute(ctxName, cid_AST);
			else
			setPlaceAttribute(ctxName, cid_AST.startLine, cid_AST.startColumn, eLine, eCol);
			fullname_AST = (XmlAst)astFactory.make( (new ASTArray(3)).add((XmlAst)astFactory.create(FULLNAME,"FULLNAME")).add(id_AST).add(ctxName));
			setPlaceAttribute(fullname_AST, cid_AST, id_AST);
			currentAST.root = fullname_AST;
			currentAST.child = fullname_AST!=null &&fullname_AST.getFirstChild()!=null ?
				fullname_AST.getFirstChild() : fullname_AST;
			currentAST.advanceChildToEnd();
		}
		returnAST = fullname_AST;
	}
	
	public final void unbounded() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst unbounded_AST = null;
		
		XmlAst tmp93_AST = null;
		if (inputState.guessing==0) {
			tmp93_AST = (XmlAst)astFactory.create(LT(1));
			astFactory.addASTChild(currentAST, tmp93_AST);
		}
		match(UNBOUNDED);
		if ( inputState.guessing==0 ) {
			unbounded_AST = (XmlAst)currentAST.root;
			unbounded_AST = makeNameExpr((XmlAst)unbounded_AST);
			setSimplePlaceAttribute(unbounded_AST);
			currentAST.root = unbounded_AST;
			currentAST.child = unbounded_AST!=null &&unbounded_AST.getFirstChild()!=null ?
				unbounded_AST.getFirstChild() : unbounded_AST;
			currentAST.advanceChildToEnd();
		}
		unbounded_AST = (XmlAst)currentAST.root;
		returnAST = unbounded_AST;
	}
	
	public final void bound() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst bound_AST = null;
		
		switch ( LA(1)) {
		case UNBOUNDED:
		{
			unbounded();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			bound_AST = (XmlAst)currentAST.root;
			break;
		}
		case IDENTIFIER:
		case LC:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case NOT:
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		case MINUS:
		case LITERAL_LAMBDA:
		case LITERAL_LET:
		case RECEXS:
		case LITERAL_IF:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		case NUMERAL:
		{
			expression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			bound_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = bound_AST;
	}
	
	public final void fielddeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst fielddeclaration_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp94_AST = null;
		tmp94_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			fielddeclaration_AST = (XmlAst)currentAST.root;
			fielddeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(FIELDDECLARATION,"FIELDDECLARATION")).add(fielddeclaration_AST));
			setPlaceAttribute(fielddeclaration_AST);
			currentAST.root = fielddeclaration_AST;
			currentAST.child = fielddeclaration_AST!=null &&fielddeclaration_AST.getFirstChild()!=null ?
				fielddeclaration_AST.getFirstChild() : fielddeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		fielddeclaration_AST = (XmlAst)currentAST.root;
		returnAST = fielddeclaration_AST;
	}
	
	public final void iffExpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst iffExpression_AST = null;
		Token  op = null;
		XmlAst op_AST = null;
		
		impliesexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop105:
		do {
			if ((LA(1)==IFF)) {
				op = LT(1);
				if (inputState.guessing==0) {
					op_AST = (XmlAst)astFactory.create(op);
					astFactory.addASTChild(currentAST, op_AST);
				}
				match(IFF);
				if ( inputState.guessing==0 ) {
					setSimplePlaceAttribute(op_AST);
				}
				impliesexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop105;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			iffExpression_AST = (XmlAst)currentAST.root;
			iffExpression_AST = infix_to_prefix(iffExpression_AST);
			currentAST.root = iffExpression_AST;
			currentAST.child = iffExpression_AST!=null &&iffExpression_AST.getFirstChild()!=null ?
				iffExpression_AST.getFirstChild() : iffExpression_AST;
			currentAST.advanceChildToEnd();
		}
		iffExpression_AST = (XmlAst)currentAST.root;
		returnAST = iffExpression_AST;
	}
	
	public final void impliesexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst impliesexpression_AST = null;
		Token  op = null;
		XmlAst op_AST = null;
		
		orexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop108:
		do {
			if ((LA(1)==IMPLIES)) {
				op = LT(1);
				if (inputState.guessing==0) {
					op_AST = (XmlAst)astFactory.create(op);
					astFactory.addASTChild(currentAST, op_AST);
				}
				match(IMPLIES);
				if ( inputState.guessing==0 ) {
					setSimplePlaceAttribute(op_AST);
				}
				orexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop108;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			impliesexpression_AST = (XmlAst)currentAST.root;
			impliesexpression_AST = infix_to_prefix_right(impliesexpression_AST);
			currentAST.root = impliesexpression_AST;
			currentAST.child = impliesexpression_AST!=null &&impliesexpression_AST.getFirstChild()!=null ?
				impliesexpression_AST.getFirstChild() : impliesexpression_AST;
			currentAST.advanceChildToEnd();
		}
		impliesexpression_AST = (XmlAst)currentAST.root;
		returnAST = impliesexpression_AST;
	}
	
	public final void orexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst orexpression_AST = null;
		Token  op1 = null;
		XmlAst op1_AST = null;
		Token  op2 = null;
		XmlAst op2_AST = null;
		
		andexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop112:
		do {
			if ((LA(1)==OR||LA(1)==XOR)) {
				{
				switch ( LA(1)) {
				case OR:
				{
					op1 = LT(1);
					if (inputState.guessing==0) {
						op1_AST = (XmlAst)astFactory.create(op1);
						astFactory.addASTChild(currentAST, op1_AST);
					}
					match(OR);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op1_AST);
					}
					break;
				}
				case XOR:
				{
					op2 = LT(1);
					if (inputState.guessing==0) {
						op2_AST = (XmlAst)astFactory.create(op2);
						astFactory.addASTChild(currentAST, op2_AST);
					}
					match(XOR);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op2_AST);
					}
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
				andexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop112;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			orexpression_AST = (XmlAst)currentAST.root;
			orexpression_AST = infix_to_prefix(orexpression_AST);
			currentAST.root = orexpression_AST;
			currentAST.child = orexpression_AST!=null &&orexpression_AST.getFirstChild()!=null ?
				orexpression_AST.getFirstChild() : orexpression_AST;
			currentAST.advanceChildToEnd();
		}
		orexpression_AST = (XmlAst)currentAST.root;
		returnAST = orexpression_AST;
	}
	
	public final void andexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst andexpression_AST = null;
		Token  op = null;
		XmlAst op_AST = null;
		
		notexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop115:
		do {
			if ((LA(1)==AND)) {
				op = LT(1);
				if (inputState.guessing==0) {
					op_AST = (XmlAst)astFactory.create(op);
					astFactory.addASTChild(currentAST, op_AST);
				}
				match(AND);
				if ( inputState.guessing==0 ) {
					setSimplePlaceAttribute(op_AST);
				}
				notexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop115;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			andexpression_AST = (XmlAst)currentAST.root;
			andexpression_AST = infix_to_prefix(andexpression_AST);
			currentAST.root = andexpression_AST;
			currentAST.child = andexpression_AST!=null &&andexpression_AST.getFirstChild()!=null ?
				andexpression_AST.getFirstChild() : andexpression_AST;
			currentAST.advanceChildToEnd();
		}
		andexpression_AST = (XmlAst)currentAST.root;
		returnAST = andexpression_AST;
	}
	
	public final void notexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst notexpression_AST = null;
		Token  op = null;
		XmlAst op_AST = null;
		
		switch ( LA(1)) {
		case NOT:
		{
			{
			op = LT(1);
			if (inputState.guessing==0) {
				op_AST = (XmlAst)astFactory.create(op);
				astFactory.addASTChild(currentAST, op_AST);
			}
			match(NOT);
			if ( inputState.guessing==0 ) {
				setSimplePlaceAttribute(op_AST);
			}
			notexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			if ( inputState.guessing==0 ) {
				notexpression_AST = (XmlAst)currentAST.root;
				notexpression_AST = makeUnaryApplication(notexpression_AST);
				currentAST.root = notexpression_AST;
				currentAST.child = notexpression_AST!=null &&notexpression_AST.getFirstChild()!=null ?
					notexpression_AST.getFirstChild() : notexpression_AST;
				currentAST.advanceChildToEnd();
			}
			}
			notexpression_AST = (XmlAst)currentAST.root;
			break;
		}
		case IDENTIFIER:
		case LC:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		case MINUS:
		case LITERAL_LAMBDA:
		case LITERAL_LET:
		case RECEXS:
		case LITERAL_IF:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		case NUMERAL:
		{
			eqexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			notexpression_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = notexpression_AST;
	}
	
	public final void eqexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst eqexpression_AST = null;
		Token  op1 = null;
		XmlAst op1_AST = null;
		Token  op2 = null;
		XmlAst op2_AST = null;
		
		relexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop121:
		do {
			if ((LA(1)==EQ||LA(1)==NEQ)) {
				{
				switch ( LA(1)) {
				case EQ:
				{
					op1 = LT(1);
					if (inputState.guessing==0) {
						op1_AST = (XmlAst)astFactory.create(op1);
						astFactory.addASTChild(currentAST, op1_AST);
					}
					match(EQ);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op1_AST);
					}
					break;
				}
				case NEQ:
				{
					op2 = LT(1);
					if (inputState.guessing==0) {
						op2_AST = (XmlAst)astFactory.create(op2);
						astFactory.addASTChild(currentAST, op2_AST);
					}
					match(NEQ);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op2_AST);
					}
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
				relexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop121;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			eqexpression_AST = (XmlAst)currentAST.root;
			eqexpression_AST = infix_to_prefix(eqexpression_AST);
			currentAST.root = eqexpression_AST;
			currentAST.child = eqexpression_AST!=null &&eqexpression_AST.getFirstChild()!=null ?
				eqexpression_AST.getFirstChild() : eqexpression_AST;
			currentAST.advanceChildToEnd();
		}
		eqexpression_AST = (XmlAst)currentAST.root;
		returnAST = eqexpression_AST;
	}
	
	public final void relexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst relexpression_AST = null;
		Token  op1 = null;
		XmlAst op1_AST = null;
		Token  op2 = null;
		XmlAst op2_AST = null;
		Token  op3 = null;
		XmlAst op3_AST = null;
		Token  op4 = null;
		XmlAst op4_AST = null;
		
		infixapplication();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop125:
		do {
			if (((LA(1) >= GT && LA(1) <= LE))) {
				{
				switch ( LA(1)) {
				case GT:
				{
					op1 = LT(1);
					if (inputState.guessing==0) {
						op1_AST = (XmlAst)astFactory.create(op1);
						astFactory.addASTChild(currentAST, op1_AST);
					}
					match(GT);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op1_AST);
					}
					break;
				}
				case GE:
				{
					op2 = LT(1);
					if (inputState.guessing==0) {
						op2_AST = (XmlAst)astFactory.create(op2);
						astFactory.addASTChild(currentAST, op2_AST);
					}
					match(GE);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op2_AST);
					}
					break;
				}
				case LT:
				{
					op3 = LT(1);
					if (inputState.guessing==0) {
						op3_AST = (XmlAst)astFactory.create(op3);
						astFactory.addASTChild(currentAST, op3_AST);
					}
					match(LT);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op3_AST);
					}
					break;
				}
				case LE:
				{
					op4 = LT(1);
					if (inputState.guessing==0) {
						op4_AST = (XmlAst)astFactory.create(op4);
						astFactory.addASTChild(currentAST, op4_AST);
					}
					match(LE);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op4_AST);
					}
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
				infixapplication();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop125;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			relexpression_AST = (XmlAst)currentAST.root;
			relexpression_AST = infix_to_prefix(relexpression_AST);
			currentAST.root = relexpression_AST;
			currentAST.child = relexpression_AST!=null &&relexpression_AST.getFirstChild()!=null ?
				relexpression_AST.getFirstChild() : relexpression_AST;
			currentAST.advanceChildToEnd();
		}
		relexpression_AST = (XmlAst)currentAST.root;
		returnAST = relexpression_AST;
	}
	
	public final void infixapplication() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst infixapplication_AST = null;
		Token  op = null;
		XmlAst op_AST = null;
		
		additiveexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop128:
		do {
			if ((LA(1)==IDENTIFIER)) {
				op = LT(1);
				if (inputState.guessing==0) {
					op_AST = (XmlAst)astFactory.create(op);
					astFactory.addASTChild(currentAST, op_AST);
				}
				match(IDENTIFIER);
				if ( inputState.guessing==0 ) {
					setSimplePlaceAttribute(op_AST);
				}
				additiveexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop128;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			infixapplication_AST = (XmlAst)currentAST.root;
			infixapplication_AST = infix_to_prefix(infixapplication_AST);
			currentAST.root = infixapplication_AST;
			currentAST.child = infixapplication_AST!=null &&infixapplication_AST.getFirstChild()!=null ?
				infixapplication_AST.getFirstChild() : infixapplication_AST;
			currentAST.advanceChildToEnd();
		}
		infixapplication_AST = (XmlAst)currentAST.root;
		returnAST = infixapplication_AST;
	}
	
	public final void additiveexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst additiveexpression_AST = null;
		Token  op1 = null;
		XmlAst op1_AST = null;
		Token  op2 = null;
		XmlAst op2_AST = null;
		
		multiplicativeexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop132:
		do {
			if ((LA(1)==PLUS||LA(1)==MINUS)) {
				{
				switch ( LA(1)) {
				case PLUS:
				{
					op1 = LT(1);
					if (inputState.guessing==0) {
						op1_AST = (XmlAst)astFactory.create(op1);
						astFactory.addASTChild(currentAST, op1_AST);
					}
					match(PLUS);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op1_AST);
					}
					break;
				}
				case MINUS:
				{
					op2 = LT(1);
					if (inputState.guessing==0) {
						op2_AST = (XmlAst)astFactory.create(op2);
						astFactory.addASTChild(currentAST, op2_AST);
					}
					match(MINUS);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op2_AST);
					}
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
				multiplicativeexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop132;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			additiveexpression_AST = (XmlAst)currentAST.root;
			additiveexpression_AST = infix_to_prefix(additiveexpression_AST);
			currentAST.root = additiveexpression_AST;
			currentAST.child = additiveexpression_AST!=null &&additiveexpression_AST.getFirstChild()!=null ?
				additiveexpression_AST.getFirstChild() : additiveexpression_AST;
			currentAST.advanceChildToEnd();
		}
		additiveexpression_AST = (XmlAst)currentAST.root;
		returnAST = additiveexpression_AST;
	}
	
	public final void multiplicativeexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst multiplicativeexpression_AST = null;
		Token  op1 = null;
		XmlAst op1_AST = null;
		Token  op2 = null;
		XmlAst op2_AST = null;
		
		unaryexpression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop136:
		do {
			if ((LA(1)==MULT||LA(1)==DIV)) {
				{
				switch ( LA(1)) {
				case MULT:
				{
					op1 = LT(1);
					if (inputState.guessing==0) {
						op1_AST = (XmlAst)astFactory.create(op1);
						astFactory.addASTChild(currentAST, op1_AST);
					}
					match(MULT);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op1_AST);
					}
					break;
				}
				case DIV:
				{
					op2 = LT(1);
					if (inputState.guessing==0) {
						op2_AST = (XmlAst)astFactory.create(op2);
						astFactory.addASTChild(currentAST, op2_AST);
					}
					match(DIV);
					if ( inputState.guessing==0 ) {
						setSimplePlaceAttribute(op2_AST);
					}
					break;
				}
				default:
				{
					throw new NoViableAltException(LT(1), getFilename());
				}
				}
				}
				unaryexpression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop136;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			multiplicativeexpression_AST = (XmlAst)currentAST.root;
			multiplicativeexpression_AST = infix_to_prefix(multiplicativeexpression_AST);
			currentAST.root = multiplicativeexpression_AST;
			currentAST.child = multiplicativeexpression_AST!=null &&multiplicativeexpression_AST.getFirstChild()!=null ?
				multiplicativeexpression_AST.getFirstChild() : multiplicativeexpression_AST;
			currentAST.advanceChildToEnd();
		}
		multiplicativeexpression_AST = (XmlAst)currentAST.root;
		returnAST = multiplicativeexpression_AST;
	}
	
	public final void unaryexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst unaryexpression_AST = null;
		Token  op = null;
		XmlAst op_AST = null;
		
		switch ( LA(1)) {
		case MINUS:
		{
			{
			op = LT(1);
			if (inputState.guessing==0) {
				op_AST = (XmlAst)astFactory.create(op);
				astFactory.addASTChild(currentAST, op_AST);
			}
			match(MINUS);
			if ( inputState.guessing==0 ) {
				setSimplePlaceAttribute(op_AST);
			}
			unaryexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			if ( inputState.guessing==0 ) {
				unaryexpression_AST = (XmlAst)currentAST.root;
				unaryexpression_AST = makeUnaryApplication(unaryexpression_AST);
				currentAST.root = unaryexpression_AST;
				currentAST.child = unaryexpression_AST!=null &&unaryexpression_AST.getFirstChild()!=null ?
					unaryexpression_AST.getFirstChild() : unaryexpression_AST;
				currentAST.advanceChildToEnd();
			}
			}
			unaryexpression_AST = (XmlAst)currentAST.root;
			break;
		}
		case IDENTIFIER:
		case LC:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		case LITERAL_LAMBDA:
		case LITERAL_LET:
		case RECEXS:
		case LITERAL_IF:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		case NUMERAL:
		{
			simpleExpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			unaryexpression_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = unaryexpression_AST;
	}
	
	public final void simpleExpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst simpleExpression_AST = null;
		
		expressionprefix();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop141:
		do {
			if ((_tokenSet_5.member(LA(1)))) {
				expressionSuffix();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop141;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			simpleExpression_AST = (XmlAst)currentAST.root;
			simpleExpression_AST = makeSimpleExpression(simpleExpression_AST);
			currentAST.root = simpleExpression_AST;
			currentAST.child = simpleExpression_AST!=null &&simpleExpression_AST.getFirstChild()!=null ?
				simpleExpression_AST.getFirstChild() : simpleExpression_AST;
			currentAST.advanceChildToEnd();
		}
		simpleExpression_AST = (XmlAst)currentAST.root;
		returnAST = simpleExpression_AST;
	}
	
	public final void expressionprefix() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst expressionprefix_AST = null;
		
		{
		switch ( LA(1)) {
		case NUMERAL:
		{
			numeral();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LITERAL_LAMBDA:
		{
			lambdaabstraction();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		{
			quantifiedexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LITERAL_LET:
		{
			letexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LB:
		{
			arrayliteral();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case RECEXS:
		{
			recordliteral();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LC:
		{
			setexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LITERAL_IF:
		{
			conditional();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		default:
			boolean synPredMatched146 = false;
			if (((LA(1)==IDENTIFIER))) {
				int _m146 = mark();
				synPredMatched146 = true;
				inputState.guessing++;
				try {
					{
					nextvariable();
					}
				}
				catch (RecognitionException pe) {
					synPredMatched146 = false;
				}
				rewind(_m146);
				inputState.guessing--;
			}
			if ( synPredMatched146 ) {
				nextvariable();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				boolean synPredMatched149 = false;
				if (((_tokenSet_0.member(LA(1))))) {
					int _m149 = mark();
					synPredMatched149 = true;
					inputState.guessing++;
					try {
						{
						module();
						match(DOT);
						{
						switch ( LA(1)) {
						case LITERAL_INIT:
						{
							match(LITERAL_INIT);
							break;
						}
						case LITERAL_TRANS:
						{
							match(LITERAL_TRANS);
							break;
						}
						default:
						{
							throw new NoViableAltException(LT(1), getFilename());
						}
						}
						}
						}
					}
					catch (RecognitionException pe) {
						synPredMatched149 = false;
					}
					rewind(_m149);
					inputState.guessing--;
				}
				if ( synPredMatched149 ) {
					statepreds();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else if ((LA(1)==IDENTIFIER)) {
					nameexpr();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else if ((LA(1)==LP)) {
					tupleLiteral();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
			else {
				throw new NoViableAltException(LT(1), getFilename());
			}
			}}
			}
			expressionprefix_AST = (XmlAst)currentAST.root;
			returnAST = expressionprefix_AST;
		}
		
	public final void expressionSuffix() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst expressionSuffix_AST = null;
		
		switch ( LA(1)) {
		case LP:
		{
			argument();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			expressionSuffix_AST = (XmlAst)currentAST.root;
			break;
		}
		case LB:
		case DOT:
		{
			access();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			expressionSuffix_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_WITH:
		{
			updatesuffix();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			expressionSuffix_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = expressionSuffix_AST;
	}
	
	public final void nameexpr() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst nameexpr_AST = null;
		
		name();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			nameexpr_AST = (XmlAst)currentAST.root;
			nameexpr_AST = makeNameExpr((XmlAst)nameexpr_AST);
			currentAST.root = nameexpr_AST;
			currentAST.child = nameexpr_AST!=null &&nameexpr_AST.getFirstChild()!=null ?
				nameexpr_AST.getFirstChild() : nameexpr_AST;
			currentAST.advanceChildToEnd();
		}
		nameexpr_AST = (XmlAst)currentAST.root;
		returnAST = nameexpr_AST;
	}
	
	public final void nextvariable() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst nextvariable_AST = null;
		XmlAst id_AST = null;
		int eLine=0, eCol=0;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp95_AST = null;
		tmp95_AST = (XmlAst)astFactory.create(LT(1));
		match(QUOTE);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			nextvariable_AST = (XmlAst)currentAST.root;
			nextvariable_AST = makeNextOperator((XmlAst)nextvariable_AST);
			setPlaceAttribute(nextvariable_AST, id_AST.startLine, id_AST.startColumn, eLine, eCol);
			currentAST.root = nextvariable_AST;
			currentAST.child = nextvariable_AST!=null &&nextvariable_AST.getFirstChild()!=null ?
				nextvariable_AST.getFirstChild() : nextvariable_AST;
			currentAST.advanceChildToEnd();
		}
		nextvariable_AST = (XmlAst)currentAST.root;
		returnAST = nextvariable_AST;
	}
	
	public final void statepreds() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst statepreds_AST = null;
		XmlAst mod_AST = null;
		int eLine=0, eCol=0;
		
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp96_AST = null;
		tmp96_AST = (XmlAst)astFactory.create(LT(1));
		match(DOT);
		{
		switch ( LA(1)) {
		case LITERAL_INIT:
		{
			XmlAst tmp97_AST = null;
			tmp97_AST = (XmlAst)astFactory.create(LT(1));
			match(LITERAL_INIT);
			if ( inputState.guessing==0 ) {
				statepreds_AST = (XmlAst)currentAST.root;
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+4;
				statepreds_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MODINIT,"MODINIT")).add(statepreds_AST));
				currentAST.root = statepreds_AST;
				currentAST.child = statepreds_AST!=null &&statepreds_AST.getFirstChild()!=null ?
					statepreds_AST.getFirstChild() : statepreds_AST;
				currentAST.advanceChildToEnd();
			}
			break;
		}
		case LITERAL_TRANS:
		{
			XmlAst tmp98_AST = null;
			tmp98_AST = (XmlAst)astFactory.create(LT(1));
			match(LITERAL_TRANS);
			if ( inputState.guessing==0 ) {
				statepreds_AST = (XmlAst)currentAST.root;
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+5;
				statepreds_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MODTRANS,"MODTRANS")).add(statepreds_AST));
				currentAST.root = statepreds_AST;
				currentAST.child = statepreds_AST!=null &&statepreds_AST.getFirstChild()!=null ?
					statepreds_AST.getFirstChild() : statepreds_AST;
				currentAST.advanceChildToEnd();
			}
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			statepreds_AST = (XmlAst)currentAST.root;
			setPlaceAttribute(statepreds_AST, mod_AST.startLine, mod_AST.startColumn, eLine, eCol);
		}
		statepreds_AST = (XmlAst)currentAST.root;
		returnAST = statepreds_AST;
	}
	
	public final void numeral() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst numeral_AST = null;
		
		XmlAst tmp99_AST = null;
		if (inputState.guessing==0) {
			tmp99_AST = (XmlAst)astFactory.create(LT(1));
			astFactory.makeASTRoot(currentAST, tmp99_AST);
		}
		match(NUMERAL);
		if ( inputState.guessing==0 ) {
			numeral_AST = (XmlAst)currentAST.root;
			setPlaceAttribute(numeral_AST,
			LT(0).getLine(),
			LT(0).getColumn(),
			LT(0).getLine(),
			LT(0).getColumn()+numeral_AST.getText().length());
			// System.err.println("Numeral Parsed" + #numeral.getText());
			
		}
		numeral_AST = (XmlAst)currentAST.root;
		returnAST = numeral_AST;
	}
	
	public final void lambdaabstraction() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst lambdaabstraction_AST = null;
		XmlAst expr_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp100_AST = null;
		tmp100_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_LAMBDA);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		XmlAst tmp101_AST = null;
		tmp101_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		pvarDecls();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp102_AST = null;
		tmp102_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		XmlAst tmp103_AST = null;
		tmp103_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		expression();
		if (inputState.guessing==0) {
			expr_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			lambdaabstraction_AST = (XmlAst)currentAST.root;
			lambdaabstraction_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(LAMBDAABSTRACTION,"LAMBDAABSTRACTION")).add(lambdaabstraction_AST));
			setPlaceAttribute(lambdaabstraction_AST, sLine, sCol, expr_AST.endLine, expr_AST.endColumn);
			currentAST.root = lambdaabstraction_AST;
			currentAST.child = lambdaabstraction_AST!=null &&lambdaabstraction_AST.getFirstChild()!=null ?
				lambdaabstraction_AST.getFirstChild() : lambdaabstraction_AST;
			currentAST.advanceChildToEnd();
		}
		lambdaabstraction_AST = (XmlAst)currentAST.root;
		returnAST = lambdaabstraction_AST;
	}
	
	public final void quantifiedexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst quantifiedexpression_AST = null;
		Token  op1 = null;
		XmlAst op1_AST = null;
		Token  op2 = null;
		XmlAst op2_AST = null;
		
		{
		switch ( LA(1)) {
		case LITERAL_FORALL:
		{
			op1 = LT(1);
			if (inputState.guessing==0) {
				op1_AST = (XmlAst)astFactory.create(op1);
				astFactory.addASTChild(currentAST, op1_AST);
			}
			match(LITERAL_FORALL);
			if ( inputState.guessing==0 ) {
				setSimplePlaceAttribute(op1_AST);
			}
			break;
		}
		case LITERAL_EXISTS:
		{
			op2 = LT(1);
			if (inputState.guessing==0) {
				op2_AST = (XmlAst)astFactory.create(op2);
				astFactory.addASTChild(currentAST, op2_AST);
			}
			match(LITERAL_EXISTS);
			if ( inputState.guessing==0 ) {
				setSimplePlaceAttribute(op2_AST);
			}
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp104_AST = null;
		tmp104_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		pvarDecls();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp105_AST = null;
		tmp105_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		XmlAst tmp106_AST = null;
		tmp106_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			quantifiedexpression_AST = (XmlAst)currentAST.root;
			quantifiedexpression_AST = makeQuantifiedExpr(quantifiedexpression_AST);
			setPlaceAttribute(quantifiedexpression_AST);
			currentAST.root = quantifiedexpression_AST;
			currentAST.child = quantifiedexpression_AST!=null &&quantifiedexpression_AST.getFirstChild()!=null ?
				quantifiedexpression_AST.getFirstChild() : quantifiedexpression_AST;
			currentAST.advanceChildToEnd();
		}
		quantifiedexpression_AST = (XmlAst)currentAST.root;
		returnAST = quantifiedexpression_AST;
	}
	
	public final void letexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst letexpression_AST = null;
		XmlAst expr_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp107_AST = null;
		tmp107_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_LET);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		letdeclarations();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp108_AST = null;
		tmp108_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IN);
		expression();
		if (inputState.guessing==0) {
			expr_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			letexpression_AST = (XmlAst)currentAST.root;
			letexpression_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(LETEXPRESSION,"LETEXPRESSION")).add(letexpression_AST));
			setPlaceAttribute(letexpression_AST, sLine, sCol, expr_AST.endLine, expr_AST.endColumn);
			currentAST.root = letexpression_AST;
			currentAST.child = letexpression_AST!=null &&letexpression_AST.getFirstChild()!=null ?
				letexpression_AST.getFirstChild() : letexpression_AST;
			currentAST.advanceChildToEnd();
		}
		letexpression_AST = (XmlAst)currentAST.root;
		returnAST = letexpression_AST;
	}
	
	public final void arrayliteral() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst arrayliteral_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp109_AST = null;
		tmp109_AST = (XmlAst)astFactory.create(LT(1));
		match(LB);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		XmlAst tmp110_AST = null;
		tmp110_AST = (XmlAst)astFactory.create(LT(1));
		match(LB);
		indexVarDecl();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp111_AST = null;
		tmp111_AST = (XmlAst)astFactory.create(LT(1));
		match(RB);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp112_AST = null;
		tmp112_AST = (XmlAst)astFactory.create(LT(1));
		match(RB);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			arrayliteral_AST = (XmlAst)currentAST.root;
			arrayliteral_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ARRAYLITERAL,"ARRAYLITERAL")).add(arrayliteral_AST));
			setPlaceAttribute(arrayliteral_AST, sLine, sCol, eLine, eCol);
			currentAST.root = arrayliteral_AST;
			currentAST.child = arrayliteral_AST!=null &&arrayliteral_AST.getFirstChild()!=null ?
				arrayliteral_AST.getFirstChild() : arrayliteral_AST;
			currentAST.advanceChildToEnd();
		}
		arrayliteral_AST = (XmlAst)currentAST.root;
		returnAST = arrayliteral_AST;
	}
	
	public final void recordliteral() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst recordliteral_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp113_AST = null;
		tmp113_AST = (XmlAst)astFactory.create(LT(1));
		match(RECEXS);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		recordentry();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop163:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp114_AST = null;
				tmp114_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				recordentry();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop163;
			}
			
		} while (true);
		}
		XmlAst tmp115_AST = null;
		tmp115_AST = (XmlAst)astFactory.create(LT(1));
		match(RECEXE);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+2;
		}
		if ( inputState.guessing==0 ) {
			recordliteral_AST = (XmlAst)currentAST.root;
			recordliteral_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RECORDLITERAL,"RECORDLITERAL")).add(recordliteral_AST));
			setPlaceAttribute(recordliteral_AST, sLine, sCol, eLine, eCol);
			currentAST.root = recordliteral_AST;
			currentAST.child = recordliteral_AST!=null &&recordliteral_AST.getFirstChild()!=null ?
				recordliteral_AST.getFirstChild() : recordliteral_AST;
			currentAST.advanceChildToEnd();
		}
		recordliteral_AST = (XmlAst)currentAST.root;
		returnAST = recordliteral_AST;
	}
	
	public final void tupleLiteral() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst tupleLiteral_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp116_AST = null;
		tmp116_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expressions();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp117_AST = null;
		tmp117_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			tupleLiteral_AST = (XmlAst)currentAST.root;
			tupleLiteral_AST = makeTupleLiteralOrSetParens(tupleLiteral_AST);
			setPlaceAttribute(tupleLiteral_AST, sLine, sCol, eLine, eCol);
			currentAST.root = tupleLiteral_AST;
			currentAST.child = tupleLiteral_AST!=null &&tupleLiteral_AST.getFirstChild()!=null ?
				tupleLiteral_AST.getFirstChild() : tupleLiteral_AST;
			currentAST.advanceChildToEnd();
		}
		tupleLiteral_AST = (XmlAst)currentAST.root;
		returnAST = tupleLiteral_AST;
	}
	
	public final void conditional() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst conditional_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp118_AST = null;
		tmp118_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IF);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp119_AST = null;
		tmp119_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_THEN);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop176:
		do {
			if ((LA(1)==LITERAL_ELSIF)) {
				elsif();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop176;
			}
			
		} while (true);
		}
		XmlAst tmp120_AST = null;
		tmp120_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_ELSE);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp121_AST = null;
		tmp121_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_ENDIF);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+5;
		}
		if ( inputState.guessing==0 ) {
			conditional_AST = (XmlAst)currentAST.root;
			conditional_AST = makeConditional(conditional_AST);
			setPlaceAttribute(conditional_AST, sLine, sCol, eLine, eCol);
			currentAST.root = conditional_AST;
			currentAST.child = conditional_AST!=null &&conditional_AST.getFirstChild()!=null ?
				conditional_AST.getFirstChild() : conditional_AST;
			currentAST.advanceChildToEnd();
		}
		conditional_AST = (XmlAst)currentAST.root;
		returnAST = conditional_AST;
	}
	
	public final void argument() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst argument_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp122_AST = null;
		tmp122_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expressions();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp123_AST = null;
		tmp123_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			argument_AST = (XmlAst)currentAST.root;
			argument_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(TUPLELITERAL,"TUPLELITERAL")).add(argument_AST));
			setPlaceAttribute(argument_AST, sLine, sCol, eLine, eCol);
			currentAST.root = argument_AST;
			currentAST.child = argument_AST!=null &&argument_AST.getFirstChild()!=null ?
				argument_AST.getFirstChild() : argument_AST;
			currentAST.advanceChildToEnd();
		}
		argument_AST = (XmlAst)currentAST.root;
		returnAST = argument_AST;
	}
	
	public final void access() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst access_AST = null;
		XmlAst id_AST = null;
		XmlAst n_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		if ((LA(1)==LB)) {
			{
			XmlAst tmp124_AST = null;
			tmp124_AST = (XmlAst)astFactory.create(LT(1));
			match(LB);
			if ( inputState.guessing==0 ) {
				sLine = LT(0).getLine(); sCol = LT(0).getColumn();
			}
			expression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp125_AST = null;
			tmp125_AST = (XmlAst)astFactory.create(LT(1));
			match(RB);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			}
			if ( inputState.guessing==0 ) {
				access_AST = (XmlAst)currentAST.root;
				access_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ARRAYACCESS,"ARRAYACCESS")).add(access_AST));
				setPlaceAttribute(access_AST, sLine, sCol, eLine, eCol);
				currentAST.root = access_AST;
				currentAST.child = access_AST!=null &&access_AST.getFirstChild()!=null ?
					access_AST.getFirstChild() : access_AST;
				currentAST.advanceChildToEnd();
			}
			access_AST = (XmlAst)currentAST.root;
		}
		else {
			boolean synPredMatched205 = false;
			if (((LA(1)==DOT))) {
				int _m205 = mark();
				synPredMatched205 = true;
				inputState.guessing++;
				try {
					{
					match(DOT);
					identifier();
					}
				}
				catch (RecognitionException pe) {
					synPredMatched205 = false;
				}
				rewind(_m205);
				inputState.guessing--;
			}
			if ( synPredMatched205 ) {
				XmlAst tmp126_AST = null;
				tmp126_AST = (XmlAst)astFactory.create(LT(1));
				match(DOT);
				if ( inputState.guessing==0 ) {
					sLine = LT(0).getLine(); sCol = LT(0).getColumn();
				}
				identifier();
				if (inputState.guessing==0) {
					id_AST = (XmlAst)returnAST;
					astFactory.addASTChild(currentAST, returnAST);
				}
				if ( inputState.guessing==0 ) {
					access_AST = (XmlAst)currentAST.root;
					access_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RECORDACCESS,"RECORDACCESS")).add(access_AST));
					setPlaceAttribute(access_AST, sLine, sCol, id_AST.endLine, id_AST.endColumn);
					currentAST.root = access_AST;
					currentAST.child = access_AST!=null &&access_AST.getFirstChild()!=null ?
						access_AST.getFirstChild() : access_AST;
					currentAST.advanceChildToEnd();
				}
				access_AST = (XmlAst)currentAST.root;
			}
			else if ((LA(1)==DOT)) {
				XmlAst tmp127_AST = null;
				tmp127_AST = (XmlAst)astFactory.create(LT(1));
				match(DOT);
				if ( inputState.guessing==0 ) {
					sLine = LT(0).getLine(); sCol = LT(0).getColumn();
				}
				numeral();
				if (inputState.guessing==0) {
					n_AST = (XmlAst)returnAST;
					astFactory.addASTChild(currentAST, returnAST);
				}
				if ( inputState.guessing==0 ) {
					access_AST = (XmlAst)currentAST.root;
					access_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(TUPLEACCESS,"TUPLEACCESS")).add(access_AST));
					setPlaceAttribute(access_AST, sLine, sCol, n_AST.endLine, n_AST.endColumn);
					currentAST.root = access_AST;
					currentAST.child = access_AST!=null &&access_AST.getFirstChild()!=null ?
						access_AST.getFirstChild() : access_AST;
					currentAST.advanceChildToEnd();
				}
				access_AST = (XmlAst)currentAST.root;
			}
			else {
				throw new NoViableAltException(LT(1), getFilename());
			}
			}
			returnAST = access_AST;
		}
		
	public final void updatesuffix() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst updatesuffix_AST = null;
		XmlAst up_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp128_AST = null;
		tmp128_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_WITH);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		update();
		if (inputState.guessing==0) {
			up_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			updatesuffix_AST = (XmlAst)currentAST.root;
			updatesuffix_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(UPDATESUFFIX,"UPDATESUFFIX")).add(updatesuffix_AST));
			setPlaceAttribute(updatesuffix_AST, sLine, sCol, up_AST.endLine, up_AST.endColumn);
			currentAST.root = updatesuffix_AST;
			currentAST.child = updatesuffix_AST!=null &&updatesuffix_AST.getFirstChild()!=null ?
				updatesuffix_AST.getFirstChild() : updatesuffix_AST;
			currentAST.advanceChildToEnd();
		}
		updatesuffix_AST = (XmlAst)currentAST.root;
		returnAST = updatesuffix_AST;
	}
	
	public final void letdeclarations() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst letdeclarations_AST = null;
		
		letDeclaration();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop158:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp129_AST = null;
				tmp129_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				letDeclaration();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop158;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			letdeclarations_AST = (XmlAst)currentAST.root;
			letdeclarations_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(LETDECLARATIONS,"LETDECLARATIONS")).add(letdeclarations_AST));
			setPlaceAttribute(letdeclarations_AST);
			currentAST.root = letdeclarations_AST;
			currentAST.child = letdeclarations_AST!=null &&letdeclarations_AST.getFirstChild()!=null ?
				letdeclarations_AST.getFirstChild() : letdeclarations_AST;
			currentAST.advanceChildToEnd();
		}
		letdeclarations_AST = (XmlAst)currentAST.root;
		returnAST = letdeclarations_AST;
	}
	
	public final void letDeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst letDeclaration_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp130_AST = null;
		tmp130_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp131_AST = null;
		tmp131_AST = (XmlAst)astFactory.create(LT(1));
		match(EQ);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			letDeclaration_AST = (XmlAst)currentAST.root;
			letDeclaration_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(LETDECLARATION,"LETDECLARATION")).add(letDeclaration_AST));
			setPlaceAttribute(letDeclaration_AST);
			currentAST.root = letDeclaration_AST;
			currentAST.child = letDeclaration_AST!=null &&letDeclaration_AST.getFirstChild()!=null ?
				letDeclaration_AST.getFirstChild() : letDeclaration_AST;
			currentAST.advanceChildToEnd();
		}
		letDeclaration_AST = (XmlAst)currentAST.root;
		returnAST = letDeclaration_AST;
	}
	
	public final void indexVarDecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst indexVarDecl_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp132_AST = null;
		tmp132_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		indextype();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			indexVarDecl_AST = (XmlAst)currentAST.root;
			indexVarDecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(INDEXVARDECL,"INDEXVARDECL")).add(indexVarDecl_AST));
			setPlaceAttribute(indexVarDecl_AST);
			currentAST.root = indexVarDecl_AST;
			currentAST.child = indexVarDecl_AST!=null &&indexVarDecl_AST.getFirstChild()!=null ?
				indexVarDecl_AST.getFirstChild() : indexVarDecl_AST;
			currentAST.advanceChildToEnd();
		}
		indexVarDecl_AST = (XmlAst)currentAST.root;
		returnAST = indexVarDecl_AST;
	}
	
	public final void recordentry() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst recordentry_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp133_AST = null;
		tmp133_AST = (XmlAst)astFactory.create(LT(1));
		match(ASSIGN);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			recordentry_AST = (XmlAst)currentAST.root;
			recordentry_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RECORDENTRY,"RECORDENTRY")).add(recordentry_AST));
			setPlaceAttribute(recordentry_AST);
			currentAST.root = recordentry_AST;
			currentAST.child = recordentry_AST!=null &&recordentry_AST.getFirstChild()!=null ?
				recordentry_AST.getFirstChild() : recordentry_AST;
			currentAST.advanceChildToEnd();
		}
		recordentry_AST = (XmlAst)currentAST.root;
		returnAST = recordentry_AST;
	}
	
	public final void expressions() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst expressions_AST = null;
		
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop183:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp134_AST = null;
				tmp134_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				expression();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop183;
			}
			
		} while (true);
		}
		expressions_AST = (XmlAst)currentAST.root;
		returnAST = expressions_AST;
	}
	
	public final void setpredexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst setpredexpression_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp135_AST = null;
		tmp135_AST = (XmlAst)astFactory.create(LT(1));
		match(LC);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp136_AST = null;
		tmp136_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		type();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp137_AST = null;
		tmp137_AST = (XmlAst)astFactory.create(LT(1));
		match(VBAR);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp138_AST = null;
		tmp138_AST = (XmlAst)astFactory.create(LT(1));
		match(RC);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			setpredexpression_AST = (XmlAst)currentAST.root;
			setpredexpression_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(SETPREDEXPRESSION,"SETPREDEXPRESSION")).add(setpredexpression_AST));
			setPlaceAttribute(setpredexpression_AST, sLine, sCol, eLine, eCol);
			currentAST.root = setpredexpression_AST;
			currentAST.child = setpredexpression_AST!=null &&setpredexpression_AST.getFirstChild()!=null ?
				setpredexpression_AST.getFirstChild() : setpredexpression_AST;
			currentAST.advanceChildToEnd();
		}
		setpredexpression_AST = (XmlAst)currentAST.root;
		returnAST = setpredexpression_AST;
	}
	
	public final void setlistexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst setlistexpression_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp139_AST = null;
		tmp139_AST = (XmlAst)astFactory.create(LT(1));
		match(LC);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		case LC:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case NOT:
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		case MINUS:
		case LITERAL_LAMBDA:
		case LITERAL_LET:
		case RECEXS:
		case LITERAL_IF:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		case NUMERAL:
		{
			expression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			{
			_loop173:
			do {
				if ((LA(1)==COMMA)) {
					XmlAst tmp140_AST = null;
					tmp140_AST = (XmlAst)astFactory.create(LT(1));
					match(COMMA);
					expression();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else {
					break _loop173;
				}
				
			} while (true);
			}
			break;
		}
		case RC:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		XmlAst tmp141_AST = null;
		tmp141_AST = (XmlAst)astFactory.create(LT(1));
		match(RC);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			setlistexpression_AST = (XmlAst)currentAST.root;
			setlistexpression_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(SETLISTEXPRESSION,"SETLISTEXPRESSION")).add(setlistexpression_AST));
			setPlaceAttribute(setlistexpression_AST, sLine, sCol, eLine, eCol);
			currentAST.root = setlistexpression_AST;
			currentAST.child = setlistexpression_AST!=null &&setlistexpression_AST.getFirstChild()!=null ?
				setlistexpression_AST.getFirstChild() : setlistexpression_AST;
			currentAST.advanceChildToEnd();
		}
		setlistexpression_AST = (XmlAst)currentAST.root;
		returnAST = setlistexpression_AST;
	}
	
	public final void elsif() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst elsif_AST = null;
		
		XmlAst tmp142_AST = null;
		tmp142_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_ELSIF);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp143_AST = null;
		tmp143_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_THEN);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		elsif_AST = (XmlAst)currentAST.root;
		returnAST = elsif_AST;
	}
	
	public final void update() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst update_AST = null;
		
		updateposition();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp144_AST = null;
		tmp144_AST = (XmlAst)astFactory.create(LT(1));
		match(ASSIGN);
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		update_AST = (XmlAst)currentAST.root;
		returnAST = update_AST;
	}
	
	public final void updateposition() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst updateposition_AST = null;
		
		{
		int _cnt188=0;
		_loop188:
		do {
			switch ( LA(1)) {
			case LP:
			{
				argument();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				break;
			}
			case LB:
			case DOT:
			{
				access();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				break;
			}
			default:
			{
				if ( _cnt188>=1 ) { break _loop188; } else {throw new NoViableAltException(LT(1), getFilename());}
			}
			}
			_cnt188++;
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			updateposition_AST = (XmlAst)currentAST.root;
			updateposition_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(UPDATEPOSITION,"UPDATEPOSITION")).add(updateposition_AST));
			setPlaceAttribute(updateposition_AST);
			currentAST.root = updateposition_AST;
			currentAST.child = updateposition_AST!=null &&updateposition_AST.getFirstChild()!=null ?
				updateposition_AST.getFirstChild() : updateposition_AST;
			currentAST.advanceChildToEnd();
		}
		updateposition_AST = (XmlAst)currentAST.root;
		returnAST = updateposition_AST;
	}
	
	public final void identifiers() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst identifiers_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop192:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp145_AST = null;
				tmp145_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				identifier();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop192;
			}
			
		} while (true);
		}
		identifiers_AST = (XmlAst)currentAST.root;
		returnAST = identifiers_AST;
	}
	
	public final void pidentifiers() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst pidentifiers_AST = null;
		XmlAst ids_AST = null;
		
		identifiers();
		if (inputState.guessing==0) {
			ids_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			pidentifiers_AST = (XmlAst)currentAST.root;
			pidentifiers_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(IDENTIFIERS,"IDENTIFIERS")).add(pidentifiers_AST));
			setPlaceAttribute(pidentifiers_AST);
			currentAST.root = pidentifiers_AST;
			currentAST.child = pidentifiers_AST!=null &&pidentifiers_AST.getFirstChild()!=null ?
				pidentifiers_AST.getFirstChild() : pidentifiers_AST;
			currentAST.advanceChildToEnd();
		}
		pidentifiers_AST = (XmlAst)currentAST.root;
		returnAST = pidentifiers_AST;
	}
	
	public final void varDecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst varDecl_AST = null;
		XmlAst ids_AST = null;
		XmlAst ty_AST = null;
		
		identifiers();
		if (inputState.guessing==0) {
			ids_AST = (XmlAst)returnAST;
		}
		XmlAst tmp146_AST = null;
		tmp146_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		type();
		if (inputState.guessing==0) {
			ty_AST = (XmlAst)returnAST;
		}
		if ( inputState.guessing==0 ) {
			varDecl_AST = (XmlAst)currentAST.root;
			varDecl_AST=makeVarDecl(ids_AST,ty_AST);
			setPlaceAttribute(varDecl_AST);
			currentAST.root = varDecl_AST;
			currentAST.child = varDecl_AST!=null &&varDecl_AST.getFirstChild()!=null ?
				varDecl_AST.getFirstChild() : varDecl_AST;
			currentAST.advanceChildToEnd();
		}
		returnAST = varDecl_AST;
	}
	
	public final void lhs() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst lhs_AST = null;
		Token  q = null;
		XmlAst q_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		switch ( LA(1)) {
		case QUOTE:
		{
			q = LT(1);
			if (inputState.guessing==0) {
				q_AST = (XmlAst)astFactory.create(q);
				astFactory.addASTChild(currentAST, q_AST);
			}
			match(QUOTE);
			if ( inputState.guessing==0 ) {
				setSimplePlaceAttribute(q_AST);
			}
			break;
		}
		case EQ:
		case LB:
		case COMMA:
		case DOT:
		case LITERAL_IN:
		case LITERAL_TO:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		{
		_loop201:
		do {
			if ((LA(1)==LB||LA(1)==DOT)) {
				access();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop201;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			lhs_AST = (XmlAst)currentAST.root;
			lhs_AST = makeLhs((XmlAst)lhs_AST);
			currentAST.root = lhs_AST;
			currentAST.child = lhs_AST!=null &&lhs_AST.getFirstChild()!=null ?
				lhs_AST.getFirstChild() : lhs_AST;
			currentAST.advanceChildToEnd();
		}
		lhs_AST = (XmlAst)currentAST.root;
		returnAST = lhs_AST;
	}
	
	public final void rhsexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst rhsexpression_AST = null;
		XmlAst expr_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp147_AST = null;
		tmp147_AST = (XmlAst)astFactory.create(LT(1));
		match(EQ);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expression();
		if (inputState.guessing==0) {
			expr_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			rhsexpression_AST = (XmlAst)currentAST.root;
			rhsexpression_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RHSEXPRESSION,"RHSEXPRESSION")).add(rhsexpression_AST));
			setPlaceAttribute(rhsexpression_AST, sLine, sCol, expr_AST.endLine, expr_AST.endColumn);
			currentAST.root = rhsexpression_AST;
			currentAST.child = rhsexpression_AST!=null &&rhsexpression_AST.getFirstChild()!=null ?
				rhsexpression_AST.getFirstChild() : rhsexpression_AST;
			currentAST.advanceChildToEnd();
		}
		rhsexpression_AST = (XmlAst)currentAST.root;
		returnAST = rhsexpression_AST;
	}
	
	public final void rhsselection() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst rhsselection_AST = null;
		XmlAst expr_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp148_AST = null;
		tmp148_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IN);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expression();
		if (inputState.guessing==0) {
			expr_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			rhsselection_AST = (XmlAst)currentAST.root;
			rhsselection_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RHSSELECTION,"RHSSELECTION")).add(rhsselection_AST));
			setPlaceAttribute(rhsselection_AST, sLine, sCol, expr_AST.endLine, expr_AST.endColumn);
			currentAST.root = rhsselection_AST;
			currentAST.child = rhsselection_AST!=null &&rhsselection_AST.getFirstChild()!=null ?
				rhsselection_AST.getFirstChild() : rhsselection_AST;
			currentAST.advanceChildToEnd();
		}
		rhsselection_AST = (XmlAst)currentAST.root;
		returnAST = rhsselection_AST;
	}
	
	public final void rhsdefinition() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst rhsdefinition_AST = null;
		
		switch ( LA(1)) {
		case EQ:
		{
			rhsexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			rhsdefinition_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_IN:
		{
			rhsselection();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			rhsdefinition_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = rhsdefinition_AST;
	}
	
	public final void simpleDefinition() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst simpleDefinition_AST = null;
		
		lhs();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		rhsdefinition();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			simpleDefinition_AST = (XmlAst)currentAST.root;
			simpleDefinition_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(SIMPLEDEFINITION,"SIMPLEDEFINITION")).add(simpleDefinition_AST));
			setPlaceAttribute(simpleDefinition_AST);
			currentAST.root = simpleDefinition_AST;
			currentAST.child = simpleDefinition_AST!=null &&simpleDefinition_AST.getFirstChild()!=null ?
				simpleDefinition_AST.getFirstChild() : simpleDefinition_AST;
			currentAST.advanceChildToEnd();
		}
		simpleDefinition_AST = (XmlAst)currentAST.root;
		returnAST = simpleDefinition_AST;
	}
	
	public final void foralldefinition() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst foralldefinition_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp149_AST = null;
		tmp149_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		XmlAst tmp150_AST = null;
		tmp150_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_FORALL);
		XmlAst tmp151_AST = null;
		tmp151_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		pvarDecls();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp152_AST = null;
		tmp152_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		XmlAst tmp153_AST = null;
		tmp153_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		definitions();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp154_AST = null;
		tmp154_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			foralldefinition_AST = (XmlAst)currentAST.root;
			foralldefinition_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(FORALLDEFINITION,"FORALLDEFINITION")).add(foralldefinition_AST));
			setPlaceAttribute(foralldefinition_AST, sLine, sCol, eLine, eCol);
			currentAST.root = foralldefinition_AST;
			currentAST.child = foralldefinition_AST!=null &&foralldefinition_AST.getFirstChild()!=null ?
				foralldefinition_AST.getFirstChild() : foralldefinition_AST;
			currentAST.advanceChildToEnd();
		}
		foralldefinition_AST = (XmlAst)currentAST.root;
		returnAST = foralldefinition_AST;
	}
	
	public final void definitions() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst definitions_AST = null;
		
		{
		boolean synPredMatched215 = false;
		if (((LA(1)==IDENTIFIER||LA(1)==LP))) {
			int _m215 = mark();
			synPredMatched215 = true;
			inputState.guessing++;
			try {
				{
				definition();
				match(SEMI);
				definition();
				}
			}
			catch (RecognitionException pe) {
				synPredMatched215 = false;
			}
			rewind(_m215);
			inputState.guessing--;
		}
		if ( synPredMatched215 ) {
			definition();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp155_AST = null;
			tmp155_AST = (XmlAst)astFactory.create(LT(1));
			match(SEMI);
			definitions();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else {
			boolean synPredMatched217 = false;
			if (((LA(1)==IDENTIFIER||LA(1)==LP))) {
				int _m217 = mark();
				synPredMatched217 = true;
				inputState.guessing++;
				try {
					{
					definition();
					match(SEMI);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched217 = false;
				}
				rewind(_m217);
				inputState.guessing--;
			}
			if ( synPredMatched217 ) {
				definition();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				XmlAst tmp156_AST = null;
				tmp156_AST = (XmlAst)astFactory.create(LT(1));
				match(SEMI);
			}
			else if ((LA(1)==IDENTIFIER||LA(1)==LP)) {
				definition();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				throw new NoViableAltException(LT(1), getFilename());
			}
			}
			}
			definitions_AST = (XmlAst)currentAST.root;
			returnAST = definitions_AST;
		}
		
	public final void definition() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst definition_AST = null;
		
		switch ( LA(1)) {
		case IDENTIFIER:
		{
			simpleDefinition();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			definition_AST = (XmlAst)currentAST.root;
			break;
		}
		case LP:
		{
			foralldefinition();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			definition_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = definition_AST;
	}
	
	public final void guard() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst guard_AST = null;
		
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		case LC:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case NOT:
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		case MINUS:
		case LITERAL_LAMBDA:
		case LITERAL_LET:
		case RECEXS:
		case LITERAL_IF:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		case NUMERAL:
		{
			expression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case LITERAL_ELSE:
		{
			elseexpression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			guard_AST = (XmlAst)currentAST.root;
			guard_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(GUARD,"GUARD")).add(guard_AST));
			setPlaceAttribute(guard_AST);
			currentAST.root = guard_AST;
			currentAST.child = guard_AST!=null &&guard_AST.getFirstChild()!=null ?
				guard_AST.getFirstChild() : guard_AST;
			currentAST.advanceChildToEnd();
		}
		guard_AST = (XmlAst)currentAST.root;
		returnAST = guard_AST;
	}
	
	public final void elseexpression() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst elseexpression_AST = null;
		
		XmlAst tmp157_AST = null;
		if (inputState.guessing==0) {
			tmp157_AST = (XmlAst)astFactory.create(LT(1));
			astFactory.addASTChild(currentAST, tmp157_AST);
		}
		match(LITERAL_ELSE);
		if ( inputState.guessing==0 ) {
			elseexpression_AST = (XmlAst)currentAST.root;
			elseexpression_AST = makeNameExpr((XmlAst)elseexpression_AST);
			currentAST.root = elseexpression_AST;
			currentAST.child = elseexpression_AST!=null &&elseexpression_AST.getFirstChild()!=null ?
				elseexpression_AST.getFirstChild() : elseexpression_AST;
			currentAST.advanceChildToEnd();
		}
		elseexpression_AST = (XmlAst)currentAST.root;
		returnAST = elseexpression_AST;
	}
	
	public final void assignments() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst assignments_AST = null;
		
		{
		boolean synPredMatched223 = false;
		if (((LA(1)==IDENTIFIER))) {
			int _m223 = mark();
			synPredMatched223 = true;
			inputState.guessing++;
			try {
				{
				simpleDefinition();
				match(SEMI);
				simpleDefinition();
				}
			}
			catch (RecognitionException pe) {
				synPredMatched223 = false;
			}
			rewind(_m223);
			inputState.guessing--;
		}
		if ( synPredMatched223 ) {
			simpleDefinition();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp158_AST = null;
			tmp158_AST = (XmlAst)astFactory.create(LT(1));
			match(SEMI);
			assignments();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else {
			boolean synPredMatched225 = false;
			if (((LA(1)==IDENTIFIER))) {
				int _m225 = mark();
				synPredMatched225 = true;
				inputState.guessing++;
				try {
					{
					simpleDefinition();
					match(SEMI);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched225 = false;
				}
				rewind(_m225);
				inputState.guessing--;
			}
			if ( synPredMatched225 ) {
				simpleDefinition();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				XmlAst tmp159_AST = null;
				tmp159_AST = (XmlAst)astFactory.create(LT(1));
				match(SEMI);
			}
			else if ((LA(1)==IDENTIFIER)) {
				simpleDefinition();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				throw new NoViableAltException(LT(1), getFilename());
			}
			}
			}
			if ( inputState.guessing==0 ) {
				assignments_AST = (XmlAst)currentAST.root;
				assignments_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ASSIGNMENTS,"ASSIGNMENTS")).add(assignments_AST));
				setPlaceAttribute(assignments_AST);
				currentAST.root = assignments_AST;
				currentAST.child = assignments_AST!=null &&assignments_AST.getFirstChild()!=null ?
					assignments_AST.getFirstChild() : assignments_AST;
				currentAST.advanceChildToEnd();
			}
			assignments_AST = (XmlAst)currentAST.root;
			returnAST = assignments_AST;
		}
		
	public final void guardedcommand() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst guardedcommand_AST = null;
		
		guard();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp160_AST = null;
		tmp160_AST = (XmlAst)astFactory.create(LT(1));
		match(LONGARROW);
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		{
			assignments();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			break;
		}
		case RB:
		case ASYNC:
		case SYNC:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			guardedcommand_AST = (XmlAst)currentAST.root;
			guardedcommand_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(GUARDEDCOMMAND,"GUARDEDCOMMAND")).add(guardedcommand_AST));
			setPlaceAttribute(guardedcommand_AST);
			currentAST.root = guardedcommand_AST;
			currentAST.child = guardedcommand_AST!=null &&guardedcommand_AST.getFirstChild()!=null ?
				guardedcommand_AST.getFirstChild() : guardedcommand_AST;
			currentAST.advanceChildToEnd();
		}
		guardedcommand_AST = (XmlAst)currentAST.root;
		returnAST = guardedcommand_AST;
	}
	
	public final void basicmodule() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst basicmodule_AST = null;
		
		switch ( LA(1)) {
		case LITERAL_BEGIN:
		{
			basemodule();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_LOCAL:
		{
			hiding();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_OUTPUT:
		{
			newoutput();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_RENAME:
		{
			renaming();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_WITH:
		{
			withModule();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		case IDENTIFIER:
		{
			modulename();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_OBSERVE:
		{
			observeModule();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basicmodule_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
			boolean synPredMatched235 = false;
			if (((LA(1)==LP))) {
				int _m235 = mark();
				synPredMatched235 = true;
				inputState.guessing++;
				try {
					{
					match(LP);
					match(SYNC);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched235 = false;
				}
				rewind(_m235);
				inputState.guessing--;
			}
			if ( synPredMatched235 ) {
				multisynchronous();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				basicmodule_AST = (XmlAst)currentAST.root;
			}
			else {
				boolean synPredMatched237 = false;
				if (((LA(1)==LP))) {
					int _m237 = mark();
					synPredMatched237 = true;
					inputState.guessing++;
					try {
						{
						match(LP);
						match(ASYNC);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched237 = false;
					}
					rewind(_m237);
					inputState.guessing--;
				}
				if ( synPredMatched237 ) {
					multiasynchronous();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
					basicmodule_AST = (XmlAst)currentAST.root;
				}
				else if ((LA(1)==LP)) {
					{
					XmlAst tmp161_AST = null;
					tmp161_AST = (XmlAst)astFactory.create(LT(1));
					match(LP);
					module();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
					XmlAst tmp162_AST = null;
					tmp162_AST = (XmlAst)astFactory.create(LT(1));
					match(RP);
					}
					if ( inputState.guessing==0 ) {
						basicmodule_AST = (XmlAst)currentAST.root;
						basicmodule_AST = setModuleParens(basicmodule_AST);
						currentAST.root = basicmodule_AST;
						currentAST.child = basicmodule_AST!=null &&basicmodule_AST.getFirstChild()!=null ?
							basicmodule_AST.getFirstChild() : basicmodule_AST;
						currentAST.advanceChildToEnd();
					}
					basicmodule_AST = (XmlAst)currentAST.root;
				}
			else {
				throw new NoViableAltException(LT(1), getFilename());
			}
			}}
			returnAST = basicmodule_AST;
		}
		
	public final void basemodule() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst basemodule_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp163_AST = null;
		tmp163_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_BEGIN);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		basedeclarations();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp164_AST = null;
		tmp164_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_END);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+3;
		}
		if ( inputState.guessing==0 ) {
			basemodule_AST = (XmlAst)currentAST.root;
			basemodule_AST=(XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(BASEMODULE,"BASEMODULE")).add(basemodule_AST));
			setPlaceAttribute(basemodule_AST,sLine,sCol,eLine,eCol);
			currentAST.root = basemodule_AST;
			currentAST.child = basemodule_AST!=null &&basemodule_AST.getFirstChild()!=null ?
				basemodule_AST.getFirstChild() : basemodule_AST;
			currentAST.advanceChildToEnd();
		}
		basemodule_AST = (XmlAst)currentAST.root;
		returnAST = basemodule_AST;
	}
	
	public final void multisynchronous() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst multisynchronous_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp165_AST = null;
		tmp165_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		XmlAst tmp166_AST = null;
		tmp166_AST = (XmlAst)astFactory.create(LT(1));
		match(SYNC);
		XmlAst tmp167_AST = null;
		tmp167_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		indexVarDecl();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp168_AST = null;
		tmp168_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		XmlAst tmp169_AST = null;
		tmp169_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		module();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp170_AST = null;
		tmp170_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			multisynchronous_AST = (XmlAst)currentAST.root;
			multisynchronous_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MULTISYNCHRONOUS,"MULTISYNCHRONOUS")).add(multisynchronous_AST));
			setPlaceAttribute(multisynchronous_AST,sLine,sCol,eLine,eCol);
			currentAST.root = multisynchronous_AST;
			currentAST.child = multisynchronous_AST!=null &&multisynchronous_AST.getFirstChild()!=null ?
				multisynchronous_AST.getFirstChild() : multisynchronous_AST;
			currentAST.advanceChildToEnd();
		}
		multisynchronous_AST = (XmlAst)currentAST.root;
		returnAST = multisynchronous_AST;
	}
	
	public final void multiasynchronous() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst multiasynchronous_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		XmlAst tmp171_AST = null;
		tmp171_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		XmlAst tmp172_AST = null;
		tmp172_AST = (XmlAst)astFactory.create(LT(1));
		match(ASYNC);
		XmlAst tmp173_AST = null;
		tmp173_AST = (XmlAst)astFactory.create(LT(1));
		match(LP);
		indexVarDecl();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp174_AST = null;
		tmp174_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		XmlAst tmp175_AST = null;
		tmp175_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		module();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp176_AST = null;
		tmp176_AST = (XmlAst)astFactory.create(LT(1));
		match(RP);
		if ( inputState.guessing==0 ) {
			eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
		}
		if ( inputState.guessing==0 ) {
			multiasynchronous_AST = (XmlAst)currentAST.root;
			multiasynchronous_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MULTIASYNCHRONOUS,"MULTIASYNCHRONOUS")).add(multiasynchronous_AST));
			setPlaceAttribute(multiasynchronous_AST,sLine,sCol,eLine,eCol);
			currentAST.root = multiasynchronous_AST;
			currentAST.child = multiasynchronous_AST!=null &&multiasynchronous_AST.getFirstChild()!=null ?
				multiasynchronous_AST.getFirstChild() : multiasynchronous_AST;
			currentAST.advanceChildToEnd();
		}
		multiasynchronous_AST = (XmlAst)currentAST.root;
		returnAST = multiasynchronous_AST;
	}
	
	public final void hiding() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst hiding_AST = null;
		XmlAst mod_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp177_AST = null;
		tmp177_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_LOCAL);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		pidentifiers();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp178_AST = null;
		tmp178_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IN);
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			hiding_AST = (XmlAst)currentAST.root;
			hiding_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(HIDING,"HIDING")).add(hiding_AST));
			setPlaceAttribute(hiding_AST, sLine, sCol, mod_AST.endLine, mod_AST.endColumn);
			currentAST.root = hiding_AST;
			currentAST.child = hiding_AST!=null &&hiding_AST.getFirstChild()!=null ?
				hiding_AST.getFirstChild() : hiding_AST;
			currentAST.advanceChildToEnd();
		}
		hiding_AST = (XmlAst)currentAST.root;
		returnAST = hiding_AST;
	}
	
	public final void newoutput() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst newoutput_AST = null;
		XmlAst mod_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp179_AST = null;
		tmp179_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_OUTPUT);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		pidentifiers();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp180_AST = null;
		tmp180_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IN);
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			newoutput_AST = (XmlAst)currentAST.root;
			newoutput_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(NEWOUTPUT,"NEWOUTPUT")).add(newoutput_AST));
			setPlaceAttribute(newoutput_AST,sLine,sCol, mod_AST.endLine, mod_AST.endColumn);
			currentAST.root = newoutput_AST;
			currentAST.child = newoutput_AST!=null &&newoutput_AST.getFirstChild()!=null ?
				newoutput_AST.getFirstChild() : newoutput_AST;
			currentAST.advanceChildToEnd();
		}
		newoutput_AST = (XmlAst)currentAST.root;
		returnAST = newoutput_AST;
	}
	
	public final void renaming() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst renaming_AST = null;
		XmlAst mod_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp181_AST = null;
		tmp181_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_RENAME);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		renames();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp182_AST = null;
		tmp182_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_IN);
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			renaming_AST = (XmlAst)currentAST.root;
			renaming_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RENAMING,"RENAMING")).add(renaming_AST));
			setPlaceAttribute(renaming_AST, sLine, sCol, mod_AST.endLine, mod_AST.endColumn);
			currentAST.root = renaming_AST;
			currentAST.child = renaming_AST!=null &&renaming_AST.getFirstChild()!=null ?
				renaming_AST.getFirstChild() : renaming_AST;
			currentAST.advanceChildToEnd();
		}
		renaming_AST = (XmlAst)currentAST.root;
		returnAST = renaming_AST;
	}
	
	public final void withModule() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst withModule_AST = null;
		XmlAst mod_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp183_AST = null;
		tmp183_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_WITH);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		newVarDecls();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			withModule_AST = (XmlAst)currentAST.root;
			withModule_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(WITHMODULE,"WITHMODULE")).add(withModule_AST));
			setPlaceAttribute(withModule_AST, sLine, sCol, mod_AST.endLine, mod_AST.endColumn);
			currentAST.root = withModule_AST;
			currentAST.child = withModule_AST!=null &&withModule_AST.getFirstChild()!=null ?
				withModule_AST.getFirstChild() : withModule_AST;
			currentAST.advanceChildToEnd();
		}
		withModule_AST = (XmlAst)currentAST.root;
		returnAST = withModule_AST;
	}
	
	public final void modulename() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst modulename_AST = null;
		XmlAst n_AST = null;
		XmlAst a_AST = null;
		
		name();
		if (inputState.guessing==0) {
			n_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		moduleActuals();
		if (inputState.guessing==0) {
			a_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			modulename_AST = (XmlAst)currentAST.root;
			modulename_AST = (XmlAst)astFactory.make( (new ASTArray(3)).add((XmlAst)astFactory.create(MODULEINSTANCE,"MODULEINSTANCE")).add(makeModuleName(n_AST)).add(a_AST));
			if (a_AST.startLine != 0)
			setPlaceAttribute(modulename_AST); // "a" (moduleActuals) is not empty.
			else
			setPlaceAttribute(modulename_AST, n_AST);
			currentAST.root = modulename_AST;
			currentAST.child = modulename_AST!=null &&modulename_AST.getFirstChild()!=null ?
				modulename_AST.getFirstChild() : modulename_AST;
			currentAST.advanceChildToEnd();
		}
		modulename_AST = (XmlAst)currentAST.root;
		returnAST = modulename_AST;
	}
	
	public final void observeModule() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst observeModule_AST = null;
		XmlAst mod_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp184_AST = null;
		tmp184_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_OBSERVE);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		module();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp185_AST = null;
		tmp185_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_WITH);
		module();
		if (inputState.guessing==0) {
			mod_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			observeModule_AST = (XmlAst)currentAST.root;
			observeModule_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(OBSERVEMODULE,"OBSERVEMODULE")).add(observeModule_AST));
			setPlaceAttribute(observeModule_AST, sLine, sCol, mod_AST.endLine, mod_AST.endColumn);
			currentAST.root = observeModule_AST;
			currentAST.child = observeModule_AST!=null &&observeModule_AST.getFirstChild()!=null ?
				observeModule_AST.getFirstChild() : observeModule_AST;
			currentAST.advanceChildToEnd();
		}
		observeModule_AST = (XmlAst)currentAST.root;
		returnAST = observeModule_AST;
	}
	
	public final void basedeclarations() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst basedeclarations_AST = null;
		
		{
		_loop242:
		do {
			if ((_tokenSet_6.member(LA(1)))) {
				basedeclaration();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop242;
			}
			
		} while (true);
		}
		basedeclarations_AST = (XmlAst)currentAST.root;
		returnAST = basedeclarations_AST;
	}
	
	public final void basedeclaration() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst basedeclaration_AST = null;
		
		switch ( LA(1)) {
		case LITERAL_INPUT:
		{
			inputdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_OUTPUT:
		{
			outputdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_GLOBAL:
		{
			globaldecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_LOCAL:
		{
			localdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_DEFINITION:
		{
			defdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_INVARIANT:
		{
			invardecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_INITFORMULA:
		{
			initfordecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_INITIALIZATION:
		{
			initdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_TRANSITION:
		{
			transdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			basedeclaration_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = basedeclaration_AST;
	}
	
	public final void inputdecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst inputdecl_AST = null;
		XmlAst v_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp186_AST = null;
		tmp186_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_INPUT);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		varDecls();
		if (inputState.guessing==0) {
			v_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			inputdecl_AST = (XmlAst)currentAST.root;
			inputdecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(INPUTDECL,"INPUTDECL")).add(inputdecl_AST));
			setPlaceAttribute(inputdecl_AST, sLine, sCol, v_AST.endLine, v_AST.endColumn);
			currentAST.root = inputdecl_AST;
			currentAST.child = inputdecl_AST!=null &&inputdecl_AST.getFirstChild()!=null ?
				inputdecl_AST.getFirstChild() : inputdecl_AST;
			currentAST.advanceChildToEnd();
		}
		inputdecl_AST = (XmlAst)currentAST.root;
		returnAST = inputdecl_AST;
	}
	
	public final void outputdecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst outputdecl_AST = null;
		XmlAst v_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp187_AST = null;
		tmp187_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_OUTPUT);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		varDecls();
		if (inputState.guessing==0) {
			v_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			outputdecl_AST = (XmlAst)currentAST.root;
			outputdecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(OUTPUTDECL,"OUTPUTDECL")).add(outputdecl_AST));
			setPlaceAttribute(outputdecl_AST, sLine, sCol, v_AST.endLine, v_AST.endColumn);
			currentAST.root = outputdecl_AST;
			currentAST.child = outputdecl_AST!=null &&outputdecl_AST.getFirstChild()!=null ?
				outputdecl_AST.getFirstChild() : outputdecl_AST;
			currentAST.advanceChildToEnd();
		}
		outputdecl_AST = (XmlAst)currentAST.root;
		returnAST = outputdecl_AST;
	}
	
	public final void globaldecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst globaldecl_AST = null;
		XmlAst v_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp188_AST = null;
		tmp188_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_GLOBAL);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		varDecls();
		if (inputState.guessing==0) {
			v_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			globaldecl_AST = (XmlAst)currentAST.root;
			globaldecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(GLOBALDECL,"GLOBALDECL")).add(globaldecl_AST));
			setPlaceAttribute(globaldecl_AST, sLine, sCol, v_AST.endLine, v_AST.endColumn);
			currentAST.root = globaldecl_AST;
			currentAST.child = globaldecl_AST!=null &&globaldecl_AST.getFirstChild()!=null ?
				globaldecl_AST.getFirstChild() : globaldecl_AST;
			currentAST.advanceChildToEnd();
		}
		globaldecl_AST = (XmlAst)currentAST.root;
		returnAST = globaldecl_AST;
	}
	
	public final void localdecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst localdecl_AST = null;
		XmlAst v_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp189_AST = null;
		tmp189_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_LOCAL);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		varDecls();
		if (inputState.guessing==0) {
			v_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			localdecl_AST = (XmlAst)currentAST.root;
			localdecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(LOCALDECL,"LOCALDECL")).add(localdecl_AST));
			setPlaceAttribute(localdecl_AST, sLine, sCol, v_AST.endLine, v_AST.endColumn);
			currentAST.root = localdecl_AST;
			currentAST.child = localdecl_AST!=null &&localdecl_AST.getFirstChild()!=null ?
				localdecl_AST.getFirstChild() : localdecl_AST;
			currentAST.advanceChildToEnd();
		}
		localdecl_AST = (XmlAst)currentAST.root;
		returnAST = localdecl_AST;
	}
	
	public final void defdecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst defdecl_AST = null;
		XmlAst d_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp190_AST = null;
		tmp190_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_DEFINITION);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		definitions();
		if (inputState.guessing==0) {
			d_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			defdecl_AST = (XmlAst)currentAST.root;
			defdecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(DEFDECL,"DEFDECL")).add(defdecl_AST));
			setPlaceAttribute(defdecl_AST, sLine, sCol, d_AST.endLine, d_AST.endColumn);
			currentAST.root = defdecl_AST;
			currentAST.child = defdecl_AST!=null &&defdecl_AST.getFirstChild()!=null ?
				defdecl_AST.getFirstChild() : defdecl_AST;
			currentAST.advanceChildToEnd();
		}
		defdecl_AST = (XmlAst)currentAST.root;
		returnAST = defdecl_AST;
	}
	
	public final void invardecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst invardecl_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp191_AST = null;
		tmp191_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_INVARIANT);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			invardecl_AST = (XmlAst)currentAST.root;
			XmlAst tmp = invardecl_AST;
			setPlaceAttribute(tmp);
			invardecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(INVARDECL,"INVARDECL")).add(invardecl_AST));
			setPlaceAttribute(invardecl_AST, sLine, sCol, tmp.endLine, tmp.endColumn);
			currentAST.root = invardecl_AST;
			currentAST.child = invardecl_AST!=null &&invardecl_AST.getFirstChild()!=null ?
				invardecl_AST.getFirstChild() : invardecl_AST;
			currentAST.advanceChildToEnd();
		}
		invardecl_AST = (XmlAst)currentAST.root;
		returnAST = invardecl_AST;
	}
	
	public final void initfordecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst initfordecl_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp192_AST = null;
		tmp192_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_INITFORMULA);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		expression();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			initfordecl_AST = (XmlAst)currentAST.root;
			XmlAst tmp = initfordecl_AST;
			setPlaceAttribute(tmp);
			initfordecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(INITFORDECL,"INITFORDECL")).add(initfordecl_AST));
			setPlaceAttribute(initfordecl_AST, sLine, sCol, tmp.endLine, tmp.endColumn);
			currentAST.root = initfordecl_AST;
			currentAST.child = initfordecl_AST!=null &&initfordecl_AST.getFirstChild()!=null ?
				initfordecl_AST.getFirstChild() : initfordecl_AST;
			currentAST.advanceChildToEnd();
		}
		initfordecl_AST = (XmlAst)currentAST.root;
		returnAST = initfordecl_AST;
	}
	
	public final void initdecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst initdecl_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp193_AST = null;
		tmp193_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_INITIALIZATION);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		definitionorcommands();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			initdecl_AST = (XmlAst)currentAST.root;
			XmlAst tmp = initdecl_AST;
			setPlaceAttribute(tmp);
			initdecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(INITDECL,"INITDECL")).add(initdecl_AST));
			setPlaceAttribute(initdecl_AST, sLine, sCol, tmp.endLine, tmp.endColumn);
			currentAST.root = initdecl_AST;
			currentAST.child = initdecl_AST!=null &&initdecl_AST.getFirstChild()!=null ?
				initdecl_AST.getFirstChild() : initdecl_AST;
			currentAST.advanceChildToEnd();
		}
		initdecl_AST = (XmlAst)currentAST.root;
		returnAST = initdecl_AST;
	}
	
	public final void transdecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst transdecl_AST = null;
		int sLine=0, sCol=0;
		
		XmlAst tmp194_AST = null;
		tmp194_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_TRANSITION);
		if ( inputState.guessing==0 ) {
			sLine = LT(0).getLine(); sCol = LT(0).getColumn();
		}
		definitionorcommands();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			transdecl_AST = (XmlAst)currentAST.root;
			XmlAst tmp = transdecl_AST;
			setPlaceAttribute(tmp);
			transdecl_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(TRANSDECL,"TRANSDECL")).add(transdecl_AST));
			setPlaceAttribute(transdecl_AST, sLine, sCol, tmp.endLine, tmp.endColumn);
			currentAST.root = transdecl_AST;
			currentAST.child = transdecl_AST!=null &&transdecl_AST.getFirstChild()!=null ?
				transdecl_AST.getFirstChild() : transdecl_AST;
			currentAST.advanceChildToEnd();
		}
		transdecl_AST = (XmlAst)currentAST.root;
		returnAST = transdecl_AST;
	}
	
	public final void renames() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst renames_AST = null;
		
		rename();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop251:
		do {
			if ((LA(1)==COMMA)) {
				XmlAst tmp195_AST = null;
				tmp195_AST = (XmlAst)astFactory.create(LT(1));
				match(COMMA);
				rename();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop251;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			renames_AST = (XmlAst)currentAST.root;
			renames_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RENAMES,"RENAMES")).add(renames_AST));
			setPlaceAttribute(renames_AST);
			currentAST.root = renames_AST;
			currentAST.child = renames_AST!=null &&renames_AST.getFirstChild()!=null ?
				renames_AST.getFirstChild() : renames_AST;
			currentAST.advanceChildToEnd();
		}
		renames_AST = (XmlAst)currentAST.root;
		returnAST = renames_AST;
	}
	
	public final void rename() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst rename_AST = null;
		
		lhs();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp196_AST = null;
		tmp196_AST = (XmlAst)astFactory.create(LT(1));
		match(LITERAL_TO);
		lhs();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			rename_AST = (XmlAst)currentAST.root;
			rename_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(RENAME,"RENAME")).add(rename_AST));
			setPlaceAttribute(rename_AST);
			currentAST.root = rename_AST;
			currentAST.child = rename_AST!=null &&rename_AST.getFirstChild()!=null ?
				rename_AST.getFirstChild() : rename_AST;
			currentAST.advanceChildToEnd();
		}
		rename_AST = (XmlAst)currentAST.root;
		returnAST = rename_AST;
	}
	
	public final void newVarDecls() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst newVarDecls_AST = null;
		
		newVarDecl();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop291:
		do {
			if ((LA(1)==SEMI)) {
				XmlAst tmp197_AST = null;
				tmp197_AST = (XmlAst)astFactory.create(LT(1));
				match(SEMI);
				newVarDecl();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop291;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			newVarDecls_AST = (XmlAst)currentAST.root;
			newVarDecls_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(NEWVARDECLS,"NEWVARDECLS")).add(newVarDecls_AST));
			setPlaceAttribute(newVarDecls_AST);
			currentAST.root = newVarDecls_AST;
			currentAST.child = newVarDecls_AST!=null &&newVarDecls_AST.getFirstChild()!=null ?
				newVarDecls_AST.getFirstChild() : newVarDecls_AST;
			currentAST.advanceChildToEnd();
		}
		newVarDecls_AST = (XmlAst)currentAST.root;
		returnAST = newVarDecls_AST;
	}
	
	public final void moduleActuals() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst moduleActuals_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		{
		switch ( LA(1)) {
		case LB:
		{
			XmlAst tmp198_AST = null;
			tmp198_AST = (XmlAst)astFactory.create(LT(1));
			match(LB);
			if ( inputState.guessing==0 ) {
				sLine = LT(0).getLine(); sCol = LT(0).getColumn();
			}
			expressions();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp199_AST = null;
			tmp199_AST = (XmlAst)astFactory.create(LT(1));
			match(RB);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
			}
			break;
		}
		case EOF:
		case SEMI:
		case RP:
		case COMMA:
		case TURNSTILE:
		case LITERAL_IMPLEMENTS:
		case DOT:
		case LITERAL_WITH:
		case ASYNC:
		case SYNC:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			moduleActuals_AST = (XmlAst)currentAST.root;
			moduleActuals_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MODULEACTUALS,"MODULEACTUALS")).add(moduleActuals_AST));
			if (sLine != 0)
			setPlaceAttribute(moduleActuals_AST, sLine, sCol, eLine, eCol);
			
			currentAST.root = moduleActuals_AST;
			currentAST.child = moduleActuals_AST!=null &&moduleActuals_AST.getFirstChild()!=null ?
				moduleActuals_AST.getFirstChild() : moduleActuals_AST;
			currentAST.advanceChildToEnd();
		}
		moduleActuals_AST = (XmlAst)currentAST.root;
		returnAST = moduleActuals_AST;
	}
	
	public final void definitionorcommands() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst definitionorcommands_AST = null;
		
		{
		boolean synPredMatched283 = false;
		if (((_tokenSet_7.member(LA(1))))) {
			int _m283 = mark();
			synPredMatched283 = true;
			inputState.guessing++;
			try {
				{
				definitionorcommand();
				match(SEMI);
				definitionorcommand();
				}
			}
			catch (RecognitionException pe) {
				synPredMatched283 = false;
			}
			rewind(_m283);
			inputState.guessing--;
		}
		if ( synPredMatched283 ) {
			definitionorcommand();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp200_AST = null;
			tmp200_AST = (XmlAst)astFactory.create(LT(1));
			match(SEMI);
			definitionorcommands();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
		}
		else {
			boolean synPredMatched285 = false;
			if (((_tokenSet_7.member(LA(1))))) {
				int _m285 = mark();
				synPredMatched285 = true;
				inputState.guessing++;
				try {
					{
					definitionorcommand();
					match(SEMI);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched285 = false;
				}
				rewind(_m285);
				inputState.guessing--;
			}
			if ( synPredMatched285 ) {
				definitionorcommand();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
				XmlAst tmp201_AST = null;
				tmp201_AST = (XmlAst)astFactory.create(LT(1));
				match(SEMI);
			}
			else if ((_tokenSet_7.member(LA(1)))) {
				definitionorcommand();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				throw new NoViableAltException(LT(1), getFilename());
			}
			}
			}
			definitionorcommands_AST = (XmlAst)currentAST.root;
			returnAST = definitionorcommands_AST;
		}
		
	public final void labeledcommand() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst labeledcommand_AST = null;
		XmlAst id_AST = null;
		XmlAst gc_AST = null;
		
		identifier();
		if (inputState.guessing==0) {
			id_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		XmlAst tmp202_AST = null;
		tmp202_AST = (XmlAst)astFactory.create(LT(1));
		match(CLN);
		guardedcommand();
		if (inputState.guessing==0) {
			gc_AST = (XmlAst)returnAST;
			astFactory.addASTChild(currentAST, returnAST);
		}
		if ( inputState.guessing==0 ) {
			labeledcommand_AST = (XmlAst)currentAST.root;
			id_AST.setType(LABEL);
			labeledcommand_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(LABELEDCOMMAND,"LABELEDCOMMAND")).add(labeledcommand_AST));
			setPlaceAttribute(labeledcommand_AST);
			currentAST.root = labeledcommand_AST;
			currentAST.child = labeledcommand_AST!=null &&labeledcommand_AST.getFirstChild()!=null ?
				labeledcommand_AST.getFirstChild() : labeledcommand_AST;
			currentAST.advanceChildToEnd();
		}
		labeledcommand_AST = (XmlAst)currentAST.root;
		returnAST = labeledcommand_AST;
	}
	
	public final void namedcommand() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst namedcommand_AST = null;
		
		boolean synPredMatched270 = false;
		if (((LA(1)==IDENTIFIER))) {
			int _m270 = mark();
			synPredMatched270 = true;
			inputState.guessing++;
			try {
				{
				identifier();
				match(CLN);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched270 = false;
			}
			rewind(_m270);
			inputState.guessing--;
		}
		if ( synPredMatched270 ) {
			labeledcommand();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			namedcommand_AST = (XmlAst)currentAST.root;
		}
		else if ((_tokenSet_8.member(LA(1)))) {
			guardedcommand();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			namedcommand_AST = (XmlAst)currentAST.root;
		}
		else {
			throw new NoViableAltException(LT(1), getFilename());
		}
		
		returnAST = namedcommand_AST;
	}
	
	public final void somecommand() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst somecommand_AST = null;
		
		boolean synPredMatched273 = false;
		if (((_tokenSet_8.member(LA(1))))) {
			int _m273 = mark();
			synPredMatched273 = true;
			inputState.guessing++;
			try {
				{
				namedcommand();
				}
			}
			catch (RecognitionException pe) {
				synPredMatched273 = false;
			}
			rewind(_m273);
			inputState.guessing--;
		}
		if ( synPredMatched273 ) {
			namedcommand();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			somecommand_AST = (XmlAst)currentAST.root;
		}
		else if ((LA(1)==LB)) {
			multicommand();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			somecommand_AST = (XmlAst)currentAST.root;
		}
		else {
			throw new NoViableAltException(LT(1), getFilename());
		}
		
		returnAST = somecommand_AST;
	}
	
	public final void multicommand() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst multicommand_AST = null;
		
		XmlAst tmp203_AST = null;
		tmp203_AST = (XmlAst)astFactory.create(LT(1));
		match(LB);
		guardedcommand();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop279:
		do {
			if ((LA(1)==SYNC)) {
				XmlAst tmp204_AST = null;
				tmp204_AST = (XmlAst)astFactory.create(LT(1));
				match(SYNC);
				guardedcommand();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop279;
			}
			
		} while (true);
		}
		XmlAst tmp205_AST = null;
		tmp205_AST = (XmlAst)astFactory.create(LT(1));
		match(RB);
		if ( inputState.guessing==0 ) {
			multicommand_AST = (XmlAst)currentAST.root;
			multicommand_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(MULTICOMMAND,"MULTICOMMAND")).add(multicommand_AST));
			setPlaceAttribute(multicommand_AST);
			currentAST.root = multicommand_AST;
			currentAST.child = multicommand_AST!=null &&multicommand_AST.getFirstChild()!=null ?
				multicommand_AST.getFirstChild() : multicommand_AST;
			currentAST.advanceChildToEnd();
		}
		multicommand_AST = (XmlAst)currentAST.root;
		returnAST = multicommand_AST;
	}
	
	public final void somecommands() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst somecommands_AST = null;
		
		somecommand();
		if (inputState.guessing==0) {
			astFactory.addASTChild(currentAST, returnAST);
		}
		{
		_loop276:
		do {
			if ((LA(1)==ASYNC)) {
				XmlAst tmp206_AST = null;
				tmp206_AST = (XmlAst)astFactory.create(LT(1));
				match(ASYNC);
				somecommand();
				if (inputState.guessing==0) {
					astFactory.addASTChild(currentAST, returnAST);
				}
			}
			else {
				break _loop276;
			}
			
		} while (true);
		}
		if ( inputState.guessing==0 ) {
			somecommands_AST = (XmlAst)currentAST.root;
			somecommands_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(SOMECOMMANDS,"SOMECOMMANDS")).add(somecommands_AST));
			setPlaceAttribute(somecommands_AST);
			currentAST.root = somecommands_AST;
			currentAST.child = somecommands_AST!=null &&somecommands_AST.getFirstChild()!=null ?
				somecommands_AST.getFirstChild() : somecommands_AST;
			currentAST.advanceChildToEnd();
		}
		somecommands_AST = (XmlAst)currentAST.root;
		returnAST = somecommands_AST;
	}
	
	public final void definitionorcommand() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst definitionorcommand_AST = null;
		XmlAst sc_AST = null;
		int sLine=0, sCol=0, eLine=0, eCol=0;
		
		switch ( LA(1)) {
		case IDENTIFIER:
		case LP:
		{
			definition();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			definitionorcommand_AST = (XmlAst)currentAST.root;
			break;
		}
		case LB:
		{
			{
			XmlAst tmp207_AST = null;
			tmp207_AST = (XmlAst)astFactory.create(LT(1));
			match(LB);
			if ( inputState.guessing==0 ) {
				sLine = LT(0).getLine(); sCol = LT(0).getColumn();
			}
			somecommands();
			if (inputState.guessing==0) {
				sc_AST = (XmlAst)returnAST;
				astFactory.addASTChild(currentAST, returnAST);
			}
			XmlAst tmp208_AST = null;
			tmp208_AST = (XmlAst)astFactory.create(LT(1));
			match(RB);
			if ( inputState.guessing==0 ) {
				eLine = LT(0).getLine(); eCol = LT(0).getColumn()+1;
				setPlaceAttribute(sc_AST, sLine, sCol, eLine, eCol);
			}
			}
			definitionorcommand_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = definitionorcommand_AST;
	}
	
	public final void newVarDecl() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst newVarDecl_AST = null;
		
		switch ( LA(1)) {
		case LITERAL_INPUT:
		{
			inputdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			newVarDecl_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_OUTPUT:
		{
			outputdecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			newVarDecl_AST = (XmlAst)currentAST.root;
			break;
		}
		case LITERAL_GLOBAL:
		{
			globaldecl();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			newVarDecl_AST = (XmlAst)currentAST.root;
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		returnAST = newVarDecl_AST;
	}
	
	public final void actualtypes() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst actualtypes_AST = null;
		
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		case REAL:
		case NZREAL:
		case INTEGER:
		case NZINTEGER:
		case NATURAL:
		case BOOLEAN:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case LITERAL_ARRAY:
		case RECS:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		{
			type();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			{
			_loop299:
			do {
				if ((LA(1)==COMMA)) {
					XmlAst tmp209_AST = null;
					tmp209_AST = (XmlAst)astFactory.create(LT(1));
					match(COMMA);
					type();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else {
					break _loop299;
				}
				
			} while (true);
			}
			break;
		}
		case SEMI:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			actualtypes_AST = (XmlAst)currentAST.root;
			actualtypes_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ACTUALTYPES,"ACTUALTYPES")).add(actualtypes_AST));
			setPlaceAttribute(actualtypes_AST);
			currentAST.root = actualtypes_AST;
			currentAST.child = actualtypes_AST!=null &&actualtypes_AST.getFirstChild()!=null ?
				actualtypes_AST.getFirstChild() : actualtypes_AST;
			currentAST.advanceChildToEnd();
		}
		actualtypes_AST = (XmlAst)currentAST.root;
		returnAST = actualtypes_AST;
	}
	
	public final void actualexprs() throws RecognitionException, TokenStreamException {
		
		returnAST = null;
		ASTPair currentAST = new ASTPair();
		XmlAst actualexprs_AST = null;
		
		{
		switch ( LA(1)) {
		case IDENTIFIER:
		case LC:
		case LITERAL_BEGIN:
		case LB:
		case LP:
		case NOT:
		case LITERAL_FORALL:
		case LITERAL_EXISTS:
		case MINUS:
		case LITERAL_LAMBDA:
		case LITERAL_LET:
		case RECEXS:
		case LITERAL_IF:
		case LITERAL_WITH:
		case LITERAL_LOCAL:
		case LITERAL_OUTPUT:
		case LITERAL_RENAME:
		case LITERAL_OBSERVE:
		case NUMERAL:
		{
			expression();
			if (inputState.guessing==0) {
				astFactory.addASTChild(currentAST, returnAST);
			}
			{
			_loop303:
			do {
				if ((LA(1)==COMMA)) {
					XmlAst tmp210_AST = null;
					tmp210_AST = (XmlAst)astFactory.create(LT(1));
					match(COMMA);
					expression();
					if (inputState.guessing==0) {
						astFactory.addASTChild(currentAST, returnAST);
					}
				}
				else {
					break _loop303;
				}
				
			} while (true);
			}
			break;
		}
		case RC:
		{
			break;
		}
		default:
		{
			throw new NoViableAltException(LT(1), getFilename());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			actualexprs_AST = (XmlAst)currentAST.root;
			actualexprs_AST = (XmlAst)astFactory.make( (new ASTArray(2)).add((XmlAst)astFactory.create(ACTUALEXPRS,"ACTUALEXPRS")).add(actualexprs_AST));
			setPlaceAttribute(actualexprs_AST);
			currentAST.root = actualexprs_AST;
			currentAST.child = actualexprs_AST!=null &&actualexprs_AST.getFirstChild()!=null ?
				actualexprs_AST.getFirstChild() : actualexprs_AST;
			currentAST.advanceChildToEnd();
		}
		actualexprs_AST = (XmlAst)currentAST.root;
		returnAST = actualexprs_AST;
	}
	
	
	public static final String[] _tokenNames = {
		"<0>",
		"EOF",
		"<2>",
		"NULL_TREE_LOOKAHEAD",
		"CONTEXT",
		"CONTEXTBODY",
		"CONTEXTNAME",
		"CONSTANTDECLARATION",
		"PARAMETERS",
		"EXPRESSION",
		"CONDITIONAL",
		"RECORDLITERAL",
		"RECORDENTRY",
		"TYPE",
		"TYPEDECLARATION",
		"ASSERTIONDECLARATION",
		"CONTEXTDECLARATION",
		"MODULEDECLARATION",
		"IDENTIFIER",
		"VARDECL",
		"INPUTDECL",
		"OUTPUTDECL",
		"GLOBALDECL",
		"LOCALDECL",
		"ARRAYTYPE",
		"BASEMODULE",
		"MODULE",
		"BASICTYPE",
		"LAMBDAABSTRACTION",
		"REAL",
		"NZREAL",
		"INTEGER",
		"NZINTEGER",
		"NATURAL",
		"BOOLEAN",
		"TRANSDECL",
		"DEFINITION",
		"SIMPLEDEFINITION",
		"LHS",
		"RHSEXPRESSION",
		"RHSSELECTION",
		"APPLICATION",
		"OR",
		"SIMPLEEXPRESSION",
		"SCALARTYPE",
		"SUBRANGE",
		"FUNCTIONTYPE",
		"TUPLETYPE",
		"RECORDTYPE",
		"CONSTRUCTOR",
		"ACCESSOR",
		"FULLNAME",
		"FIELDDECLARATION",
		"TYPENAME",
		"QUALIFIEDTYPENAME",
		"DEFDECL",
		"FORALLDEFINITION",
		"LABEL",
		"INVARDECL",
		"INITFORDECL",
		"INITDECL",
		"GUARDEDCOMMAND",
		"LABELEDCOMMAND",
		"ASSIGNMENTS",
		"GUARD",
		"NAME",
		"ACTUALTYPES",
		"ACTUALEXPRS",
		"NAMEEXPR",
		"QUALIFIEDNAMEEXPR",
		"EQUATION",
		"DISEQUATION",
		"VARDECLS",
		"NEGATION",
		"IFFEXPRESSION",
		"IMPLICATION",
		"DISJUNCTION",
		"XOREXPRESSION",
		"CONJUNCTION",
		"GTEXPRESSION",
		"GEEXPRESSION",
		"LTEXPRESSION",
		"LEEXPRESSION",
		"PLUSEXPRESSION",
		"MINUSEXPRESSION",
		"MULTEXPRESSION",
		"DIVEXPRESSION",
		"ARGUMENT",
		"ARRAYACCESS",
		"ARRAYSELECTION",
		"RECORDACCESS",
		"RECORDSELECTION",
		"TUPLEACCESS",
		"TUPLESELECTION",
		"UPDATESUFFIX",
		"UPDATE",
		"UPDATEEXPRESSION",
		"UPDATEPOSITION",
		"TUPLELITERAL",
		"ACTUALPARAMETERS",
		"ARRAYLITERAL",
		"INDEXVARDECL",
		"NEXTOPERATOR",
		"SETPREDEXPRESSION",
		"SETLISTEXPRESSION",
		"SOMECOMMANDS",
		"MULTICOMMAND",
		"QUANTIFIEDEXPRESSION",
		"QUANTIFIER",
		"LETEXPRESSION",
		"LETDECLARATIONS",
		"LETDECLARATION",
		"ASYNCHRONOUSCOMPOSITION",
		"SYNCHRONOUSCOMPOSITION",
		"SCALARELEMENT",
		"MODULENAME",
		"QUALIFIEDMODULENAME",
		"MODULEINSTANCE",
		"MODULEACTUALS",
		"NEWOUTPUT",
		"RENAMING",
		"RENAME",
		"HIDING",
		"NEWVARDECLS",
		"MODULEMODELS",
		"MODULEIMPLEMENTS",
		"ASSERTIONPROPOSITION",
		"QUANTIFIEDASSERTION",
		"ASSERTIONOPERATOR",
		"ASSERTIONFORM",
		"MULTISYNCHRONOUS",
		"MULTIASYNCHRONOUS",
		"OBSERVEMODULE",
		"TYPEDECLS",
		"TYPEDECL",
		"WITHMODULE",
		"IDENTIFIERS",
		"RENAMES",
		"STATETYPE",
		"MODINIT",
		"MODTRANS",
		"LC",
		"RC",
		"CLN",
		"\"CONTEXT\"",
		"EQ",
		"SEMI",
		"\"BEGIN\"",
		"\"END\"",
		"\"TYPE\"",
		"LB",
		"RB",
		"\"MODULE\"",
		"LP",
		"RP",
		"\"OBLIGATION\"",
		"\"CLAIM\"",
		"\"LEMMA\"",
		"\"THEOREM\"",
		"AND",
		"IMPLIES",
		"IFF",
		"NOT",
		"\"FORALL\"",
		"\"EXISTS\"",
		"COMMA",
		"TURNSTILE",
		"\"IMPLEMENTS\"",
		"\"REFINES\"",
		"DOT",
		"\"DATATYPE\"",
		"BANG",
		"UNBOUNDED",
		"DOTDOT",
		"\"ARRAY\"",
		"\"OF\"",
		"ARROW",
		"RECS",
		"RECE",
		"\"STATE\"",
		"XOR",
		"NEQ",
		"GT",
		"GE",
		"LT",
		"LE",
		"PLUS",
		"MINUS",
		"MULT",
		"DIV",
		"\"INIT\"",
		"\"TRANS\"",
		"QUOTE",
		"\"LAMBDA\"",
		"\"LET\"",
		"\"IN\"",
		"RECEXS",
		"RECEXE",
		"ASSIGN",
		"VBAR",
		"\"IF\"",
		"\"THEN\"",
		"\"ELSE\"",
		"\"ENDIF\"",
		"\"ELSIF\"",
		"\"WITH\"",
		"LONGARROW",
		"ASYNC",
		"SYNC",
		"\"LOCAL\"",
		"\"OUTPUT\"",
		"\"RENAME\"",
		"\"TO\"",
		"\"OBSERVE\"",
		"\"INPUT\"",
		"\"GLOBAL\"",
		"\"DEFINITION\"",
		"\"INVARIANT\"",
		"\"INITFORMULA\"",
		"\"INITIALIZATION\"",
		"\"TRANSITION\"",
		"NUMERAL",
		"WS",
		"SL_COMMENT",
		"PERCENT",
		"HASH",
		"QMARK",
		"ALPHANUM",
		"EQIMPL",
		"SLASH",
		"HYPHEN",
		"STAR",
		"LTE",
		"GTE",
		"ALPHA",
		"OPCHAR1",
		"OPCHAR",
		"OPCHAR_NO_GT",
		"OPCHAR_NO_EQ",
		"OPCHAR_NO_HYPHEN_OR_GT",
		"DOUBLEQUOTE"
	};
	
	private static final long _tokenSet_0_data_[] = { 262144L, 0L, 34078720L, 3022848L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_0 = new BitSet(_tokenSet_0_data_);
	private static final long _tokenSet_1_data_[] = { 4398046511104L, 0L, 32212254720L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_1 = new BitSet(_tokenSet_1_data_);
	private static final long _tokenSet_2_data_[] = { 262144L, 0L, 576460872600788992L, 539894038L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_2 = new BitSet(_tokenSet_2_data_);
	private static final long _tokenSet_3_data_[] = { 33823129600L, 0L, 633318736134144L, 3022848L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_3 = new BitSet(_tokenSet_3_data_);
	private static final long _tokenSet_4_data_[] = { 262144L, 0L, 576460872600805376L, 539894038L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_4 = new BitSet(_tokenSet_4_data_);
	private static final long _tokenSet_5_data_[] = { 0L, 0L, 2199061004288L, 8192L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_5 = new BitSet(_tokenSet_5_data_);
	private static final long _tokenSet_6_data_[] = { 0L, 0L, 0L, 533069824L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_6 = new BitSet(_tokenSet_6_data_);
	private static final long _tokenSet_7_data_[] = { 262144L, 0L, 37748736L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_7 = new BitSet(_tokenSet_7_data_);
	private static final long _tokenSet_8_data_[] = { 262144L, 0L, 576460872600788992L, 539895062L, 0L, 0L, 0L, 0L };
	public static final BitSet _tokenSet_8 = new BitSet(_tokenSet_8_data_);
	
	}
