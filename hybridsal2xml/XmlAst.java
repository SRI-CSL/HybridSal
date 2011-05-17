import antlr.CommonAST;
import antlr.Token;
import antlr.collections.AST;
import java.io.*;
import java.util.*;
import java.lang.*;

public class XmlAst extends CommonAST {
  Hashtable attributes = new Hashtable();
  int parens = 0;
  int startLine = 0, startColumn = 0, endLine = 0, endColumn = 0;
  static Indent indent = new Indent();

  public String attributesString() {
    String attrString = "";
    for (Enumeration enm = attributes.keys(); enm.hasMoreElements();) {
      String attr = (String)(enm.nextElement());
      String val = (String)(attributes.get(attr));
      attrString += " "+attr+"=\""+val+"\"";
    }
    return attrString;
  }

  public void xmlSerializeRootOpen(Writer out) throws IOException {
    if (parens > 0) {
      attributes.put("PARENS",""+parens);
    }
    if (startLine > 0) {
      attributes.put("PLACE",
		     startLine+" "+startColumn+" "+endLine+" "+endColumn);
    }
    out.write(indent.toString("<"+getText()+attributesString()+">\n"));
    indent.openBlock();
  }

  public void xmlSerializeNode(Writer out) throws IOException {
    if (parens > 0) {
      attributes.put("PARENS",""+parens);
    }
    if (startLine > 0) {
      attributes.put("PLACE",
		     startLine+" "+startColumn+" "+endLine+" "+endColumn);
    }
    if (getText().equals("")) {
      out.write(indent.toString
		("<"+HybridSalParser._tokenNames[getType()]+attributesString()+" />"));
    }
    else if (getText().equals(HybridSalParser._tokenNames[getType()])) {
      out.write(indent.toString
		("<"+HybridSalParser._tokenNames[getType()]+attributesString()+">"
		 +"</"+HybridSalParser._tokenNames[getType()]+">\n"));
    }
    else {
      out.write(indent.toString
		("<"+HybridSalParser._tokenNames[getType()]+attributesString()+">"+encode(getText())
		 +"</"+HybridSalParser._tokenNames[getType()]+">\n"));
    }
  }
   
  public void xmlSerializeRootClose(Writer out) throws IOException {
      indent.closeBlock();
      out.write(indent.toString("</"+encode(getText())+">\n"));
  }
}
