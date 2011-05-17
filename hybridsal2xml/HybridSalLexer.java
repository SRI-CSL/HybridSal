// $ANTLR 2.7.1: "HybridSalParser.g" -> "HybridSalLexer.java"$

import java.io.InputStream;
import antlr.TokenStreamException;
import antlr.TokenStreamIOException;
import antlr.TokenStreamRecognitionException;
import antlr.CharStreamException;
import antlr.CharStreamIOException;
import antlr.ANTLRException;
import java.io.Reader;
import java.util.Hashtable;
import antlr.CharScanner;
import antlr.InputBuffer;
import antlr.ByteBuffer;
import antlr.CharBuffer;
import antlr.Token;
import antlr.CommonToken;
import antlr.RecognitionException;
import antlr.NoViableAltForCharException;
import antlr.MismatchedCharException;
import antlr.TokenStream;
import antlr.ANTLRHashString;
import antlr.LexerSharedInputState;
import antlr.collections.impl.BitSet;
import antlr.SemanticException;

public class HybridSalLexer extends antlr.CharScanner implements HybridSalTokenTypes, TokenStream
 {
public HybridSalLexer(InputStream in) {
	this(new ByteBuffer(in));
}
public HybridSalLexer(Reader in) {
	this(new CharBuffer(in));
}
public HybridSalLexer(InputBuffer ib) {
	this(new LexerSharedInputState(ib));
}
public HybridSalLexer(LexerSharedInputState state) {
	super(state);
	literals = new Hashtable();
	literals.put(new ANTLRHashString("INIT", this), new Integer(190));
	literals.put(new ANTLRHashString("INITFORMULA", this), new Integer(218));
	literals.put(new ANTLRHashString("FORALL", this), new Integer(163));
	literals.put(new ANTLRHashString("END", this), new Integer(148));
	literals.put(new ANTLRHashString("DATATYPE", this), new Integer(170));
	literals.put(new ANTLRHashString("TO", this), new Integer(212));
	literals.put(new ANTLRHashString("CONTEXT", this), new Integer(144));
	literals.put(new ANTLRHashString("EXISTS", this), new Integer(164));
	literals.put(new ANTLRHashString("THEN", this), new Integer(201));
	literals.put(new ANTLRHashString("INPUT", this), new Integer(214));
	literals.put(new ANTLRHashString("TRANSITION", this), new Integer(220));
	literals.put(new ANTLRHashString("INITIALIZATION", this), new Integer(219));
	literals.put(new ANTLRHashString("ARRAY", this), new Integer(174));
	literals.put(new ANTLRHashString("TRANS", this), new Integer(191));
	literals.put(new ANTLRHashString("RENAME", this), new Integer(211));
	literals.put(new ANTLRHashString("WITH", this), new Integer(205));
	literals.put(new ANTLRHashString("OF", this), new Integer(175));
	literals.put(new ANTLRHashString("IF", this), new Integer(200));
	literals.put(new ANTLRHashString("LEMMA", this), new Integer(157));
	literals.put(new ANTLRHashString("THEOREM", this), new Integer(158));
	literals.put(new ANTLRHashString("OBLIGATION", this), new Integer(155));
	literals.put(new ANTLRHashString("STATE", this), new Integer(179));
	literals.put(new ANTLRHashString("REFINES", this), new Integer(168));
	literals.put(new ANTLRHashString("ELSIF", this), new Integer(204));
	literals.put(new ANTLRHashString("OBSERVE", this), new Integer(213));
	literals.put(new ANTLRHashString("BEGIN", this), new Integer(147));
	literals.put(new ANTLRHashString("INVARIANT", this), new Integer(217));
	literals.put(new ANTLRHashString("LOCAL", this), new Integer(209));
	literals.put(new ANTLRHashString("CLAIM", this), new Integer(156));
	literals.put(new ANTLRHashString("MODULE", this), new Integer(152));
	literals.put(new ANTLRHashString("IN", this), new Integer(195));
	literals.put(new ANTLRHashString("ENDIF", this), new Integer(203));
	literals.put(new ANTLRHashString("OUTPUT", this), new Integer(210));
	literals.put(new ANTLRHashString("LET", this), new Integer(194));
	literals.put(new ANTLRHashString("ELSE", this), new Integer(202));
	literals.put(new ANTLRHashString("IMPLEMENTS", this), new Integer(167));
	literals.put(new ANTLRHashString("DEFINITION", this), new Integer(216));
	literals.put(new ANTLRHashString("LAMBDA", this), new Integer(193));
	literals.put(new ANTLRHashString("GLOBAL", this), new Integer(215));
	literals.put(new ANTLRHashString("TYPE", this), new Integer(149));
caseSensitiveLiterals = true;
setCaseSensitive(true);
}

public Token nextToken() throws TokenStreamException {
	Token theRetToken=null;
tryAgain:
	for (;;) {
		Token _token = null;
		int _ttype = Token.INVALID_TYPE;
		resetText();
		try {   // for char stream error handling
			try {   // for lexical error handling
				switch ( LA(1)) {
				case '\t':  case '\n':  case '\u000c':  case '\r':
				case ' ':
				{
					mWS(true);
					theRetToken=_returnToken;
					break;
				}
				case ')':
				{
					mRP(true);
					theRetToken=_returnToken;
					break;
				}
				case ']':
				{
					mRB(true);
					theRetToken=_returnToken;
					break;
				}
				case '{':
				{
					mLC(true);
					theRetToken=_returnToken;
					break;
				}
				case '}':
				{
					mRC(true);
					theRetToken=_returnToken;
					break;
				}
				case ',':
				{
					mCOMMA(true);
					theRetToken=_returnToken;
					break;
				}
				case ';':
				{
					mSEMI(true);
					theRetToken=_returnToken;
					break;
				}
				case '!':
				{
					mBANG(true);
					theRetToken=_returnToken;
					break;
				}
				case '?':
				{
					mQMARK(true);
					theRetToken=_returnToken;
					break;
				}
				case '0':  case '1':  case '2':  case '3':
				case '4':  case '5':  case '6':  case '7':
				case '8':  case '9':
				{
					mNUMERAL(true);
					theRetToken=_returnToken;
					break;
				}
				case '\'':
				{
					mQUOTE(true);
					theRetToken=_returnToken;
					break;
				}
				case '=':
				{
					mEQIMPL(true);
					theRetToken=_returnToken;
					break;
				}
				case '/':
				{
					mSLASH(true);
					theRetToken=_returnToken;
					break;
				}
				case '+':
				{
					mPLUS(true);
					theRetToken=_returnToken;
					break;
				}
				case '-':
				{
					mHYPHEN(true);
					theRetToken=_returnToken;
					break;
				}
				case '*':
				{
					mSTAR(true);
					theRetToken=_returnToken;
					break;
				}
				case '<':
				{
					mLTE(true);
					theRetToken=_returnToken;
					break;
				}
				case '>':
				{
					mGTE(true);
					theRetToken=_returnToken;
					break;
				}
				case '_':
				{
					mUNBOUNDED(true);
					theRetToken=_returnToken;
					break;
				}
				case '"':
				{
					mDOUBLEQUOTE(true);
					theRetToken=_returnToken;
					break;
				}
				default:
					if ((LA(1)=='A') && (LA(2)=='N') && (LA(3)=='D')) {
						mAND(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='X') && (LA(2)=='O') && (LA(3)=='R')) {
						mXOR(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='N') && (LA(2)=='O') && (LA(3)=='T')) {
						mNOT(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='%') && (_tokenSet_0.member(LA(2)))) {
						mSL_COMMENT(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='[') && (LA(2)=='#')) {
						mRECS(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='#') && (LA(2)==']')) {
						mRECE(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='(') && (LA(2)=='#')) {
						mRECEXS(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='#') && (LA(2)==')')) {
						mRECEXE(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='O') && (LA(2)=='R') && (true)) {
						mOR(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)==':') && (LA(2)=='=')) {
						mASSIGN(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='.') && (LA(2)=='.')) {
						mDOTDOT(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='|') && (LA(2)=='|')) {
						mSYNC(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='[') && (LA(2)==']')) {
						mASYNC(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='|') && (LA(2)=='-')) {
						mTURNSTILE(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='(') && (true)) {
						mLP(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='[') && (true)) {
						mLB(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='.') && (true)) {
						mDOT(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)==':') && (true)) {
						mCLN(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='|') && (true)) {
						mVBAR(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='%') && (true)) {
						mPERCENT(true);
						theRetToken=_returnToken;
					}
					else if ((LA(1)=='#') && (true)) {
						mHASH(true);
						theRetToken=_returnToken;
					}
					else if ((_tokenSet_1.member(LA(1))) && (true) && (true)) {
						mIDENTIFIER(true);
						theRetToken=_returnToken;
					}
				else {
					if (LA(1)==EOF_CHAR) {uponEOF(); _returnToken = makeToken(Token.EOF_TYPE);}
				else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				}
				if ( _returnToken==null ) continue tryAgain; // found SKIP token
				_ttype = _returnToken.getType();
				_returnToken.setType(_ttype);
				return _returnToken;
			}
			catch (RecognitionException e) {
				throw new TokenStreamRecognitionException(e);
			}
		}
		catch (CharStreamException cse) {
			if ( cse instanceof CharStreamIOException ) {
				throw new TokenStreamIOException(((CharStreamIOException)cse).io);
			}
			else {
				throw new TokenStreamException(cse.getMessage());
			}
		}
	}
}

	public final void mWS(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = WS;
		int _saveIndex;
		
		{
		switch ( LA(1)) {
		case ' ':
		{
			match(' ');
			break;
		}
		case '\t':
		{
			match('\t');
			break;
		}
		case '\n':
		{
			match('\n');
			if ( inputState.guessing==0 ) {
				newline();
			}
			break;
		}
		case '\r':
		{
			match('\r');
			break;
		}
		case '\u000c':
		{
			match('\f');
			break;
		}
		default:
		{
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			_ttype = Token.SKIP;
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mSL_COMMENT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = SL_COMMENT;
		int _saveIndex;
		
		match("%");
		{
		_loop301:
		do {
			if ((_tokenSet_2.member(LA(1)))) {
				{
				match(_tokenSet_2);
				}
			}
			else {
				break _loop301;
			}
			
		} while (true);
		}
		{
		switch ( LA(1)) {
		case '\n':
		{
			match('\n');
			break;
		}
		case '\r':
		{
			match('\r');
			{
			if ((LA(1)=='\n')) {
				match('\n');
			}
			else {
			}
			
			}
			break;
		}
		default:
		{
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		}
		}
		if ( inputState.guessing==0 ) {
			_ttype = Token.SKIP; newline();
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mLP(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LP;
		int _saveIndex;
		
		match('(');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRP(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RP;
		int _saveIndex;
		
		match(')');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mLB(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LB;
		int _saveIndex;
		
		match('[');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRB(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RB;
		int _saveIndex;
		
		match(']');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mLC(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LC;
		int _saveIndex;
		
		match('{');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRC(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RC;
		int _saveIndex;
		
		match('}');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRECS(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RECS;
		int _saveIndex;
		
		match("[#");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRECE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RECE;
		int _saveIndex;
		
		match("#]");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRECEXS(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RECEXS;
		int _saveIndex;
		
		match("(#");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mRECEXE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = RECEXE;
		int _saveIndex;
		
		match("#)");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mDOT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = DOT;
		int _saveIndex;
		
		match('.');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mCOMMA(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = COMMA;
		int _saveIndex;
		
		match(',');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mCLN(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = CLN;
		int _saveIndex;
		
		match(':');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mSEMI(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = SEMI;
		int _saveIndex;
		
		match(';');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mBANG(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = BANG;
		int _saveIndex;
		
		match('!');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mVBAR(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = VBAR;
		int _saveIndex;
		
		match('|');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mPERCENT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = PERCENT;
		int _saveIndex;
		
		match('%');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mHASH(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = HASH;
		int _saveIndex;
		
		match('#');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mQMARK(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = QMARK;
		int _saveIndex;
		
		match('?');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mNUMERAL(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = NUMERAL;
		int _saveIndex;
		
		{
		int _cnt325=0;
		_loop325:
		do {
			if (((LA(1) >= '0' && LA(1) <= '9'))) {
				matchRange('0','9');
			}
			else {
				if ( _cnt325>=1 ) { break _loop325; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
			}
			
			_cnt325++;
		} while (true);
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mALPHANUM(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = ALPHANUM;
		int _saveIndex;
		
		{
		switch ( LA(1)) {
		case 'A':  case 'B':  case 'C':  case 'D':
		case 'E':  case 'F':  case 'G':  case 'H':
		case 'I':  case 'J':  case 'K':  case 'L':
		case 'M':  case 'N':  case 'O':  case 'P':
		case 'Q':  case 'R':  case 'S':  case 'T':
		case 'U':  case 'V':  case 'W':  case 'X':
		case 'Y':  case 'Z':  case 'a':  case 'b':
		case 'c':  case 'd':  case 'e':  case 'f':
		case 'g':  case 'h':  case 'i':  case 'j':
		case 'k':  case 'l':  case 'm':  case 'n':
		case 'o':  case 'p':  case 'q':  case 'r':
		case 's':  case 't':  case 'u':  case 'v':
		case 'w':  case 'x':  case 'y':  case 'z':
		{
			mALPHA(false);
			break;
		}
		case '0':  case '1':  case '2':  case '3':
		case '4':  case '5':  case '6':  case '7':
		case '8':  case '9':
		{
			matchRange('0','9');
			break;
		}
		case '?':
		{
			match('?');
			break;
		}
		case '_':
		{
			match('_');
			break;
		}
		default:
		{
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		}
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mALPHA(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = ALPHA;
		int _saveIndex;
		
		{
		switch ( LA(1)) {
		case 'a':  case 'b':  case 'c':  case 'd':
		case 'e':  case 'f':  case 'g':  case 'h':
		case 'i':  case 'j':  case 'k':  case 'l':
		case 'm':  case 'n':  case 'o':  case 'p':
		case 'q':  case 'r':  case 's':  case 't':
		case 'u':  case 'v':  case 'w':  case 'x':
		case 'y':  case 'z':
		{
			matchRange('a','z');
			break;
		}
		case 'A':  case 'B':  case 'C':  case 'D':
		case 'E':  case 'F':  case 'G':  case 'H':
		case 'I':  case 'J':  case 'K':  case 'L':
		case 'M':  case 'N':  case 'O':  case 'P':
		case 'Q':  case 'R':  case 'S':  case 'T':
		case 'U':  case 'V':  case 'W':  case 'X':
		case 'Y':  case 'Z':
		{
			matchRange('A','Z');
			break;
		}
		default:
		{
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		}
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mAND(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = AND;
		int _saveIndex;
		
		boolean synPredMatched330 = false;
		if (((LA(1)=='A') && (LA(2)=='N') && (LA(3)=='D'))) {
			int _m330 = mark();
			synPredMatched330 = true;
			inputState.guessing++;
			try {
				{
				match("AND");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched330 = false;
			}
			rewind(_m330);
			inputState.guessing--;
		}
		if ( synPredMatched330 ) {
			match("AND");
			{
			int _cnt332=0;
			_loop332:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt332>=1 ) { break _loop332; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt332++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='A') && (LA(2)=='N') && (LA(3)=='D')) {
			match("AND");
		}
		else {
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mOR(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = OR;
		int _saveIndex;
		
		boolean synPredMatched335 = false;
		if (((LA(1)=='O') && (LA(2)=='R') && (_tokenSet_3.member(LA(3))))) {
			int _m335 = mark();
			synPredMatched335 = true;
			inputState.guessing++;
			try {
				{
				match("OR");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched335 = false;
			}
			rewind(_m335);
			inputState.guessing--;
		}
		if ( synPredMatched335 ) {
			match("OR");
			{
			int _cnt337=0;
			_loop337:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt337>=1 ) { break _loop337; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt337++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='O') && (LA(2)=='R') && (true)) {
			match("OR");
		}
		else {
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mXOR(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = XOR;
		int _saveIndex;
		
		boolean synPredMatched340 = false;
		if (((LA(1)=='X') && (LA(2)=='O') && (LA(3)=='R'))) {
			int _m340 = mark();
			synPredMatched340 = true;
			inputState.guessing++;
			try {
				{
				match("XOR");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched340 = false;
			}
			rewind(_m340);
			inputState.guessing--;
		}
		if ( synPredMatched340 ) {
			match("XOR");
			{
			int _cnt342=0;
			_loop342:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt342>=1 ) { break _loop342; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt342++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='X') && (LA(2)=='O') && (LA(3)=='R')) {
			match("XOR");
		}
		else {
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mNOT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = NOT;
		int _saveIndex;
		
		boolean synPredMatched345 = false;
		if (((LA(1)=='N') && (LA(2)=='O') && (LA(3)=='T'))) {
			int _m345 = mark();
			synPredMatched345 = true;
			inputState.guessing++;
			try {
				{
				match("NOT");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched345 = false;
			}
			rewind(_m345);
			inputState.guessing--;
		}
		if ( synPredMatched345 ) {
			match("NOT");
			{
			int _cnt347=0;
			_loop347:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt347>=1 ) { break _loop347; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt347++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='N') && (LA(2)=='O') && (LA(3)=='T')) {
			match("NOT");
		}
		else {
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mASSIGN(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = ASSIGN;
		int _saveIndex;
		
		match(":=");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mDOTDOT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = DOTDOT;
		int _saveIndex;
		
		match("..");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mQUOTE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = QUOTE;
		int _saveIndex;
		
		match("\'");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mIMPLIES(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = IMPLIES;
		int _saveIndex;
		
		match("=>");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mEQ(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = EQ;
		int _saveIndex;
		
		match('=');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mEQIMPL(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = EQIMPL;
		int _saveIndex;
		
		boolean synPredMatched355 = false;
		if (((LA(1)=='=') && (LA(2)=='>') && (_tokenSet_4.member(LA(3))))) {
			int _m355 = mark();
			synPredMatched355 = true;
			inputState.guessing++;
			try {
				{
				match("=>");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched355 = false;
			}
			rewind(_m355);
			inputState.guessing--;
		}
		if ( synPredMatched355 ) {
			match("=>");
			{
			int _cnt357=0;
			_loop357:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt357>=1 ) { break _loop357; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt357++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='=') && (LA(2)=='>') && (true)) {
			match("=>");
			if ( inputState.guessing==0 ) {
				_ttype = IMPLIES;
			}
		}
		else {
			boolean synPredMatched359 = false;
			if (((LA(1)=='=') && (_tokenSet_5.member(LA(2))))) {
				int _m359 = mark();
				synPredMatched359 = true;
				inputState.guessing++;
				try {
					{
					match('=');
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched359 = false;
				}
				rewind(_m359);
				inputState.guessing--;
			}
			if ( synPredMatched359 ) {
				match('=');
				mOPCHAR_NO_GT(false);
				{
				_loop361:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop361;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else if ((LA(1)=='=') && (true)) {
				match('=');
				if ( inputState.guessing==0 ) {
					_ttype = EQ;
				}
			}
			else {
				throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
			}
			}
			if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
				_token = makeToken(_ttype);
				_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
			}
			_returnToken = _token;
		}
		
	protected final void mOPCHAR(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = OPCHAR;
		int _saveIndex;
		
		{
		match(_tokenSet_4);
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mOPCHAR_NO_GT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = OPCHAR_NO_GT;
		int _saveIndex;
		
		{
		match(_tokenSet_5);
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mDIV(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = DIV;
		int _saveIndex;
		
		match('/');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mNEQ(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = NEQ;
		int _saveIndex;
		
		match("/=");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mSLASH(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = SLASH;
		int _saveIndex;
		
		boolean synPredMatched366 = false;
		if (((LA(1)=='/') && (LA(2)=='=') && (_tokenSet_4.member(LA(3))))) {
			int _m366 = mark();
			synPredMatched366 = true;
			inputState.guessing++;
			try {
				{
				match("/=");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched366 = false;
			}
			rewind(_m366);
			inputState.guessing--;
		}
		if ( synPredMatched366 ) {
			match("/=");
			{
			int _cnt368=0;
			_loop368:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt368>=1 ) { break _loop368; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt368++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='/') && (LA(2)=='=') && (true)) {
			match("/=");
			if ( inputState.guessing==0 ) {
				_ttype = NEQ;
			}
		}
		else {
			boolean synPredMatched370 = false;
			if (((LA(1)=='/') && (_tokenSet_6.member(LA(2))))) {
				int _m370 = mark();
				synPredMatched370 = true;
				inputState.guessing++;
				try {
					{
					match('/');
					mOPCHAR_NO_EQ(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched370 = false;
				}
				rewind(_m370);
				inputState.guessing--;
			}
			if ( synPredMatched370 ) {
				match('/');
				mOPCHAR_NO_EQ(false);
				{
				_loop372:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop372;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else if ((LA(1)=='/') && (true)) {
				match('/');
				if ( inputState.guessing==0 ) {
					_ttype = DIV;
				}
			}
			else {
				throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
			}
			}
			if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
				_token = makeToken(_ttype);
				_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
			}
			_returnToken = _token;
		}
		
	protected final void mOPCHAR_NO_EQ(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = OPCHAR_NO_EQ;
		int _saveIndex;
		
		{
		match(_tokenSet_6);
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mSYNC(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = SYNC;
		int _saveIndex;
		
		match("||");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mASYNC(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = ASYNC;
		int _saveIndex;
		
		match("[]");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mPLUS(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = PLUS;
		int _saveIndex;
		
		boolean synPredMatched377 = false;
		if (((LA(1)=='+') && (_tokenSet_4.member(LA(2))))) {
			int _m377 = mark();
			synPredMatched377 = true;
			inputState.guessing++;
			try {
				{
				match('+');
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched377 = false;
			}
			rewind(_m377);
			inputState.guessing--;
		}
		if ( synPredMatched377 ) {
			match('+');
			{
			int _cnt379=0;
			_loop379:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt379>=1 ) { break _loop379; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt379++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='+') && (true)) {
			match('+');
		}
		else {
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mLONGARROW(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LONGARROW;
		int _saveIndex;
		
		match("-->");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mARROW(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = ARROW;
		int _saveIndex;
		
		match("->");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mMINUS(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = MINUS;
		int _saveIndex;
		
		match('-');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mHYPHEN(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = HYPHEN;
		int _saveIndex;
		
		boolean synPredMatched385 = false;
		if (((LA(1)=='-') && (LA(2)=='-') && (LA(3)=='>'))) {
			int _m385 = mark();
			synPredMatched385 = true;
			inputState.guessing++;
			try {
				{
				match("-->");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched385 = false;
			}
			rewind(_m385);
			inputState.guessing--;
		}
		if ( synPredMatched385 ) {
			match("-->");
			{
			int _cnt387=0;
			_loop387:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt387>=1 ) { break _loop387; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt387++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='-') && (LA(2)=='-') && (LA(3)=='>')) {
			match("-->");
			if ( inputState.guessing==0 ) {
				_ttype = LONGARROW;
			}
		}
		else {
			boolean synPredMatched389 = false;
			if (((LA(1)=='-') && (LA(2)=='-') && (_tokenSet_5.member(LA(3))))) {
				int _m389 = mark();
				synPredMatched389 = true;
				inputState.guessing++;
				try {
					{
					match("--");
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched389 = false;
				}
				rewind(_m389);
				inputState.guessing--;
			}
			if ( synPredMatched389 ) {
				match("--");
				mOPCHAR_NO_GT(false);
				{
				_loop391:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop391;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else {
				boolean synPredMatched393 = false;
				if (((LA(1)=='-') && (LA(2)=='>') && (_tokenSet_4.member(LA(3))))) {
					int _m393 = mark();
					synPredMatched393 = true;
					inputState.guessing++;
					try {
						{
						match("->");
						mOPCHAR(false);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched393 = false;
					}
					rewind(_m393);
					inputState.guessing--;
				}
				if ( synPredMatched393 ) {
					match("->");
					{
					int _cnt395=0;
					_loop395:
					do {
						if ((_tokenSet_4.member(LA(1)))) {
							mOPCHAR(false);
						}
						else {
							if ( _cnt395>=1 ) { break _loop395; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
						}
						
						_cnt395++;
					} while (true);
					}
					if ( inputState.guessing==0 ) {
						_ttype = IDENTIFIER;
					}
				}
				else if ((LA(1)=='-') && (LA(2)=='>') && (true)) {
					match("->");
					if ( inputState.guessing==0 ) {
						_ttype = ARROW;
					}
				}
				else {
					boolean synPredMatched397 = false;
					if (((LA(1)=='-') && (_tokenSet_7.member(LA(2))))) {
						int _m397 = mark();
						synPredMatched397 = true;
						inputState.guessing++;
						try {
							{
							match('-');
							mOPCHAR_NO_HYPHEN_OR_GT(false);
							}
						}
						catch (RecognitionException pe) {
							synPredMatched397 = false;
						}
						rewind(_m397);
						inputState.guessing--;
					}
					if ( synPredMatched397 ) {
						match('-');
						mOPCHAR_NO_HYPHEN_OR_GT(false);
						{
						_loop399:
						do {
							if ((_tokenSet_4.member(LA(1)))) {
								mOPCHAR(false);
							}
							else {
								break _loop399;
							}
							
						} while (true);
						}
						if ( inputState.guessing==0 ) {
							_ttype = IDENTIFIER;
						}
					}
					else if ((LA(1)=='-') && (LA(2)=='-') && (true)) {
						match("--");
						if ( inputState.guessing==0 ) {
							_ttype = IDENTIFIER;
						}
					}
					else if ((LA(1)=='-') && (true)) {
						match('-');
						if ( inputState.guessing==0 ) {
							_ttype = MINUS;
						}
					}
					else {
						throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
					}
					}}}
					if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
						_token = makeToken(_ttype);
						_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
					}
					_returnToken = _token;
				}
				
	protected final void mOPCHAR_NO_HYPHEN_OR_GT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = OPCHAR_NO_HYPHEN_OR_GT;
		int _saveIndex;
		
		{
		match(_tokenSet_7);
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mMULT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = MULT;
		int _saveIndex;
		
		match('*');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mSTAR(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = STAR;
		int _saveIndex;
		
		boolean synPredMatched403 = false;
		if (((LA(1)=='*') && (_tokenSet_4.member(LA(2))))) {
			int _m403 = mark();
			synPredMatched403 = true;
			inputState.guessing++;
			try {
				{
				match('*');
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched403 = false;
			}
			rewind(_m403);
			inputState.guessing--;
		}
		if ( synPredMatched403 ) {
			match('*');
			{
			int _cnt405=0;
			_loop405:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt405>=1 ) { break _loop405; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt405++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='*') && (true)) {
			match('*');
			if ( inputState.guessing==0 ) {
				_ttype = MULT;
			}
		}
		else {
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mIFF(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = IFF;
		int _saveIndex;
		
		match("<=>");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mLE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LE;
		int _saveIndex;
		
		match("<=");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mLT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LT;
		int _saveIndex;
		
		match('<');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mLTE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = LTE;
		int _saveIndex;
		
		boolean synPredMatched411 = false;
		if (((LA(1)=='<') && (LA(2)=='=') && (LA(3)=='>'))) {
			int _m411 = mark();
			synPredMatched411 = true;
			inputState.guessing++;
			try {
				{
				match("<=>");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched411 = false;
			}
			rewind(_m411);
			inputState.guessing--;
		}
		if ( synPredMatched411 ) {
			match("<=>");
			{
			int _cnt413=0;
			_loop413:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt413>=1 ) { break _loop413; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt413++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='<') && (LA(2)=='=') && (LA(3)=='>')) {
			match("<=>");
			if ( inputState.guessing==0 ) {
				_ttype = IFF;
			}
		}
		else {
			boolean synPredMatched415 = false;
			if (((LA(1)=='<') && (LA(2)=='=') && (_tokenSet_5.member(LA(3))))) {
				int _m415 = mark();
				synPredMatched415 = true;
				inputState.guessing++;
				try {
					{
					match("<=");
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched415 = false;
				}
				rewind(_m415);
				inputState.guessing--;
			}
			if ( synPredMatched415 ) {
				match("<=");
				mOPCHAR_NO_GT(false);
				{
				_loop417:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop417;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else if ((LA(1)=='<') && (LA(2)=='=') && (true)) {
				match("<=");
				if ( inputState.guessing==0 ) {
					_ttype = LE;
				}
			}
			else {
				boolean synPredMatched419 = false;
				if (((LA(1)=='<') && (_tokenSet_6.member(LA(2))))) {
					int _m419 = mark();
					synPredMatched419 = true;
					inputState.guessing++;
					try {
						{
						match('<');
						mOPCHAR_NO_EQ(false);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched419 = false;
					}
					rewind(_m419);
					inputState.guessing--;
				}
				if ( synPredMatched419 ) {
					match('<');
					mOPCHAR_NO_EQ(false);
					{
					_loop421:
					do {
						if ((_tokenSet_4.member(LA(1)))) {
							mOPCHAR(false);
						}
						else {
							break _loop421;
						}
						
					} while (true);
					}
					if ( inputState.guessing==0 ) {
						_ttype = IDENTIFIER;
					}
				}
				else if ((LA(1)=='<') && (true)) {
					match('<');
					if ( inputState.guessing==0 ) {
						_ttype = LT;
					}
				}
				else {
					throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
				}
				}}
				if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
					_token = makeToken(_ttype);
					_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
				}
				_returnToken = _token;
			}
			
	protected final void mGE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = GE;
		int _saveIndex;
		
		match(">=");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mGT(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = GT;
		int _saveIndex;
		
		match('>');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mGTE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = GTE;
		int _saveIndex;
		
		boolean synPredMatched426 = false;
		if (((LA(1)=='>') && (LA(2)=='=') && (_tokenSet_4.member(LA(3))))) {
			int _m426 = mark();
			synPredMatched426 = true;
			inputState.guessing++;
			try {
				{
				match(">=");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched426 = false;
			}
			rewind(_m426);
			inputState.guessing--;
		}
		if ( synPredMatched426 ) {
			match(">=");
			{
			int _cnt428=0;
			_loop428:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt428>=1 ) { break _loop428; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt428++;
			} while (true);
			}
			if ( inputState.guessing==0 ) {
				_ttype = IDENTIFIER;
			}
		}
		else if ((LA(1)=='>') && (LA(2)=='=') && (true)) {
			match(">=");
			if ( inputState.guessing==0 ) {
				_ttype = GE;
			}
		}
		else {
			boolean synPredMatched430 = false;
			if (((LA(1)=='>') && (_tokenSet_6.member(LA(2))))) {
				int _m430 = mark();
				synPredMatched430 = true;
				inputState.guessing++;
				try {
					{
					match('>');
					mOPCHAR_NO_EQ(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched430 = false;
				}
				rewind(_m430);
				inputState.guessing--;
			}
			if ( synPredMatched430 ) {
				match('>');
				mOPCHAR_NO_EQ(false);
				{
				_loop432:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop432;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else if ((LA(1)=='>') && (true)) {
				match('>');
				if ( inputState.guessing==0 ) {
					_ttype = GT;
				}
			}
			else {
				throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
			}
			}
			if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
				_token = makeToken(_ttype);
				_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
			}
			_returnToken = _token;
		}
		
	public final void mTURNSTILE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = TURNSTILE;
		int _saveIndex;
		
		match("|-");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mUNBOUNDED(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = UNBOUNDED;
		int _saveIndex;
		
		match('_');
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mIDENTIFIER(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = IDENTIFIER;
		int _saveIndex;
		
		switch ( LA(1)) {
		case 'A':  case 'B':  case 'C':  case 'D':
		case 'E':  case 'F':  case 'G':  case 'H':
		case 'I':  case 'J':  case 'K':  case 'L':
		case 'M':  case 'N':  case 'O':  case 'P':
		case 'Q':  case 'R':  case 'S':  case 'T':
		case 'U':  case 'V':  case 'W':  case 'X':
		case 'Y':  case 'Z':  case 'a':  case 'b':
		case 'c':  case 'd':  case 'e':  case 'f':
		case 'g':  case 'h':  case 'i':  case 'j':
		case 'k':  case 'l':  case 'm':  case 'n':
		case 'o':  case 'p':  case 'q':  case 'r':
		case 's':  case 't':  case 'u':  case 'v':
		case 'w':  case 'x':  case 'y':  case 'z':
		{
			{
			mALPHA(false);
			{
			_loop438:
			do {
				switch ( LA(1)) {
				case 'A':  case 'B':  case 'C':  case 'D':
				case 'E':  case 'F':  case 'G':  case 'H':
				case 'I':  case 'J':  case 'K':  case 'L':
				case 'M':  case 'N':  case 'O':  case 'P':
				case 'Q':  case 'R':  case 'S':  case 'T':
				case 'U':  case 'V':  case 'W':  case 'X':
				case 'Y':  case 'Z':  case 'a':  case 'b':
				case 'c':  case 'd':  case 'e':  case 'f':
				case 'g':  case 'h':  case 'i':  case 'j':
				case 'k':  case 'l':  case 'm':  case 'n':
				case 'o':  case 'p':  case 'q':  case 'r':
				case 's':  case 't':  case 'u':  case 'v':
				case 'w':  case 'x':  case 'y':  case 'z':
				{
					mALPHA(false);
					break;
				}
				case '0':  case '1':  case '2':  case '3':
				case '4':  case '5':  case '6':  case '7':
				case '8':  case '9':
				{
					matchRange('0','9');
					break;
				}
				case '?':
				{
					match('?');
					break;
				}
				case '_':
				{
					match('_');
					break;
				}
				default:
				{
					break _loop438;
				}
				}
			} while (true);
			}
			}
			break;
		}
		case '$':  case '&':  case '@':  case '^':
		case '~':
		{
			{
			mOPCHAR1(false);
			{
			_loop441:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					break _loop441;
				}
				
			} while (true);
			}
			}
			break;
		}
		default:
		{
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		}
		_ttype = testLiteralsTable(_ttype);
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	protected final void mOPCHAR1(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = OPCHAR1;
		int _saveIndex;
		
		{
		switch ( LA(1)) {
		case '$':
		{
			match('$');
			break;
		}
		case '&':
		{
			match('&');
			break;
		}
		case '@':
		{
			match('@');
			break;
		}
		case '^':
		{
			match('^');
			break;
		}
		case '~':
		{
			match('~');
			break;
		}
		default:
		{
			throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());
		}
		}
		}
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	public final void mDOUBLEQUOTE(boolean _createToken) throws RecognitionException, CharStreamException, TokenStreamException {
		int _ttype; Token _token=null; int _begin=text.length();
		_ttype = DOUBLEQUOTE;
		int _saveIndex;
		
		match("\"");
		if ( _createToken && _token==null && _ttype!=Token.SKIP ) {
			_token = makeToken(_ttype);
			_token.setText(new String(text.getBuffer(), _begin, text.length()-_begin));
		}
		_returnToken = _token;
	}
	
	
	private static final long _tokenSet_0_data_[] = { -4294953472L, 9223372032291373055L, 0L, 0L };
	public static final BitSet _tokenSet_0 = new BitSet(_tokenSet_0_data_);
	private static final long _tokenSet_1_data_[] = { 343597383680L, 5188146763348836351L, 0L, 0L };
	public static final BitSet _tokenSet_1 = new BitSet(_tokenSet_1_data_);
	private static final long _tokenSet_2_data_[] = { -4294962688L, 9223372032291373055L, 0L, 0L };
	public static final BitSet _tokenSet_2 = new BitSet(_tokenSet_2_data_);
	private static final long _tokenSet_3_data_[] = { -8935423135679774720L, 576460745995190270L, 0L, 0L };
	public static final BitSet _tokenSet_3 = new BitSet(_tokenSet_3_data_);
	private static final long _tokenSet_4_data_[] = { 8070640009025159168L, 4611686019501129729L, 0L, 0L };
	public static final BitSet _tokenSet_4 = new BitSet(_tokenSet_4_data_);
	private static final long _tokenSet_5_data_[] = { 3458953990597771264L, 4611686019501129729L, 0L, 0L };
	public static final BitSet _tokenSet_5 = new BitSet(_tokenSet_5_data_);
	private static final long _tokenSet_6_data_[] = { 5764796999811465216L, 4611686019501129729L, 0L, 0L };
	public static final BitSet _tokenSet_6 = new BitSet(_tokenSet_6_data_);
	private static final long _tokenSet_7_data_[] = { 3458918806225682432L, 4611686019501129729L, 0L, 0L };
	public static final BitSet _tokenSet_7 = new BitSet(_tokenSet_7_data_);
	
	}
