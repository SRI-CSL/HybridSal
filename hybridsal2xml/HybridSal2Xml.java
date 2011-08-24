// package csl.sal.sal2xml

// import HybridSal.HybridSalParser;
// import HybridSal.HybridSalLexer;
// import HybridSal.XmlAst;
//import SalToken;
import antlr.Token;
import antlr.TokenBuffer;
import java.io.*;
import java.lang.reflect.*;
import antlr.CommonAST;
import antlr.collections.AST;
import antlr.DumpASTVisitor;
import antlr.RecognitionException;
import antlr.MismatchedTokenException;
import antlr.NoViableAltException;

class HybridSal2Xml {
  static boolean showTree = false;
  
  public static void main(String[] args) {
    // Use a try/catch block for parser exceptions
    try {
      // if we have at least one command-line argument
      if (args.length > 0 ) {
	File outputFile = null;
	File inputFile = null;
	String rule = "context";
	// for each directory/file specified on the command line
	for(int i=0; i< args.length;i++) {
	  if ( args[i].equals("-o") ) {
	    if ( i+1<args.length ) {
	      outputFile = new File(args[i+1]);
	      i++;
	    } else {
	      printUsage();
	    }
	  } else if ( args[i].equals("-nt") ) {
	    if ( i+1<args.length ) {
	      rule = args[i+1];
	      i++;
	    } else {
	      printUsage();
	    }
	  } else {
	    parseFile(args[i], outputFile, rule); // parse it
	  }
	}
      } else {
	printUsage();
      }
    }
    catch(Exception e) {
      System.err.println("exception: "+e);
      e.printStackTrace(System.err);   // so we can get stack trace
    }
  }

  public static void printUsage() {
    System.err.println("Usage: java HybridSal2Xml [-o xmlfile] salfile");
    System.exit(1);
  }

//    static SalASTFactory astFactory = new SalASTFactory();
    
  public static void parseFile(String f, File outputFile, String rule)
    throws Exception {
    InputStream s;
    String fname = f;
    if ( f.equals("-") ) {
      s = System.in;
      fname = "stdin";
    } else {
      File file = new File(f);
      s = new FileInputStream(file);
    }
    Method pmethod = HybridSalParser.class.getMethod(rule);
    //    try {
      HybridSalLexer lexer = new HybridSalLexer(s);
      //lexer.setTokenObjectClass("HybridSalToken");
      lexer.setFilename(fname);
      HybridSalParser parser = new HybridSalParser(lexer);
      parser.setFilename(fname);
      //parser.setASTFactory(astFactory);
      parser.setASTNodeClass("XmlAst");
      // parser.context();
      // System.out.println(pmethod.toString());
      
      // Here is where we actually parse
      try {
	pmethod.invoke(parser);
      }
      catch(IllegalAccessException e) {
	System.err.println("Illegal Access Exception: "+e);
	e.printStackTrace(System.err);   // so we can get stack trace
	System.exit(1);
      }
      catch(IllegalArgumentException e) {
	System.err.println("Illegal Argument Exception: "+e);
	e.printStackTrace(System.err);   // so we can get stack trace
	System.exit(1);
      }
      catch(InvocationTargetException e) {
	if ( e.getTargetException() instanceof RecognitionException ) {
	  RecognitionException exc = (RecognitionException)e.getTargetException();
	  if ((exc instanceof MismatchedTokenException
	       && ((MismatchedTokenException)exc).token != null)
	      ||
	      (exc instanceof NoViableAltException
	       && ((NoViableAltException)exc).token != null)) {
	    if ( exc.fileName != null ) {
	      System.err.println(exc.fileName+":"+exc.line+":"+exc.column
				 +": "+exc.getMessage());
	    } else {
	      System.err.println("line "+exc.line+", col "+exc.column
				 +": "+exc.getMessage());
	    }
	  } else {
	    System.err.println(exc.getMessage());
	  }
	} else {
	System.err.println(e.getTargetException());
	}
	e.printStackTrace(System.err);   // so we can get stack trace
	System.exit(1);
      }
      // Check if there is anything left
      // Doesn't quite work - e.g., [t -> t] complains about the ']'
//        Token next = lexer.getTokenObject();
//        if (next.getType() != Token.EOF_TYPE) {
//  	System.err.println(fname+":"+next.getLine()+":"+next.getColumn()
//  			   +": unexpected token: "+next.getText());
//  	System.exit(1);
//        }
      CommonAST t = (CommonAST)parser.getAST();
      // Print the resulting tree out in LISP notation
      //System.out.println(t.toStringList());
      //      System.out.println(t.toStringTree());
      // Walker code
//        SalWalker walker = new SalWalker();
//        walker.context(t);

      // Use XmlAST
      Writer w;
      if ( outputFile != null) {
	w = new OutputStreamWriter(new FileOutputStream(outputFile));
      } else {
	w = new OutputStreamWriter(System.out);
      }
      w.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
      w.write("<!DOCTYPE "+HybridSalParser._tokenNames[t.getType()]+" SYSTEM \"sal.dtd\">\n");
      w.write("<!--  XML version of "+fname+"  -->\n");
      t.xmlSerialize(w);
      w.write("\n");
      w.flush();
      //    }
//      catch(TokenStreamException e) {
//        System.err.println("HybridSal Token Exception: "+e);
//      }
//      catch(RecognitionException e) {
//        System.err.println("HybridSal Recognition Exception: "+e);
//      }
  }  
}
