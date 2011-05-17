/* ************************************************************************
 * Indentation class
 *************************************************************************/

import java.util.*;

  class Indent {
    private Stack indents;
    private int indent=0;
    private int tab;
    
    Indent(int tab) {
      this.tab = tab;
      this.indents = new Stack();
    }
  
    Indent() {
      this(2);
    }

    void setTab(int tab) {
       this.tab = tab;
    }

    void openBlock(int tab) {
      indent+=tab;
      indents.push(new Integer(tab));
    }

   
    void openBlock() {
      openBlock(tab);
    }

    void closeBlock() { 
      try {
	int tabb = ((Integer) indents.pop()).intValue();
	indent-=tabb;
      } catch (EmptyStackException e) {
      }
    }

    public String toString(String s) {
       return toString()+s;
    }

    public String toString() {
      String s="";
      for(int i=0;i<indent;i++) 
        s += " ";
      return s;
    }
  }
