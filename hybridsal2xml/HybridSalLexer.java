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
		_loop302:
		do {
			if ((_tokenSet_2.member(LA(1)))) {
				{
				match(_tokenSet_2);
				}
			}
			else {
				break _loop302;
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
		int _cnt326=0;
		_loop326:
		do {
			if (((LA(1) >= '0' && LA(1) <= '9'))) {
				matchRange('0','9');
			}
			else {
				if ( _cnt326>=1 ) { break _loop326; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
			}
			
			_cnt326++;
		} while (true);
		}
		{
		if ((LA(1)=='.')) {
			match('.');
			{
			int _cnt329=0;
			_loop329:
			do {
				if (((LA(1) >= '0' && LA(1) <= '9'))) {
					matchRange('0','9');
				}
				else {
					if ( _cnt329>=1 ) { break _loop329; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt329++;
			} while (true);
			}
		}
		else {
		}
		
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
		
		boolean synPredMatched334 = false;
		if (((LA(1)=='A') && (LA(2)=='N') && (LA(3)=='D'))) {
			int _m334 = mark();
			synPredMatched334 = true;
			inputState.guessing++;
			try {
				{
				match("AND");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched334 = false;
			}
			rewind(_m334);
			inputState.guessing--;
		}
		if ( synPredMatched334 ) {
			match("AND");
			{
			int _cnt336=0;
			_loop336:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt336>=1 ) { break _loop336; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt336++;
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
		
		boolean synPredMatched339 = false;
		if (((LA(1)=='O') && (LA(2)=='R') && (_tokenSet_3.member(LA(3))))) {
			int _m339 = mark();
			synPredMatched339 = true;
			inputState.guessing++;
			try {
				{
				match("OR");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched339 = false;
			}
			rewind(_m339);
			inputState.guessing--;
		}
		if ( synPredMatched339 ) {
			match("OR");
			{
			int _cnt341=0;
			_loop341:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt341>=1 ) { break _loop341; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt341++;
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
		
		boolean synPredMatched344 = false;
		if (((LA(1)=='X') && (LA(2)=='O') && (LA(3)=='R'))) {
			int _m344 = mark();
			synPredMatched344 = true;
			inputState.guessing++;
			try {
				{
				match("XOR");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched344 = false;
			}
			rewind(_m344);
			inputState.guessing--;
		}
		if ( synPredMatched344 ) {
			match("XOR");
			{
			int _cnt346=0;
			_loop346:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt346>=1 ) { break _loop346; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt346++;
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
		
		boolean synPredMatched349 = false;
		if (((LA(1)=='N') && (LA(2)=='O') && (LA(3)=='T'))) {
			int _m349 = mark();
			synPredMatched349 = true;
			inputState.guessing++;
			try {
				{
				match("NOT");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched349 = false;
			}
			rewind(_m349);
			inputState.guessing--;
		}
		if ( synPredMatched349 ) {
			match("NOT");
			{
			int _cnt351=0;
			_loop351:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt351>=1 ) { break _loop351; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt351++;
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
		
		boolean synPredMatched359 = false;
		if (((LA(1)=='=') && (LA(2)=='>') && (_tokenSet_4.member(LA(3))))) {
			int _m359 = mark();
			synPredMatched359 = true;
			inputState.guessing++;
			try {
				{
				match("=>");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched359 = false;
			}
			rewind(_m359);
			inputState.guessing--;
		}
		if ( synPredMatched359 ) {
			match("=>");
			{
			int _cnt361=0;
			_loop361:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt361>=1 ) { break _loop361; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt361++;
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
			boolean synPredMatched363 = false;
			if (((LA(1)=='=') && (_tokenSet_5.member(LA(2))))) {
				int _m363 = mark();
				synPredMatched363 = true;
				inputState.guessing++;
				try {
					{
					match('=');
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched363 = false;
				}
				rewind(_m363);
				inputState.guessing--;
			}
			if ( synPredMatched363 ) {
				match('=');
				mOPCHAR_NO_GT(false);
				{
				_loop365:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop365;
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
		
		boolean synPredMatched370 = false;
		if (((LA(1)=='/') && (LA(2)=='=') && (_tokenSet_4.member(LA(3))))) {
			int _m370 = mark();
			synPredMatched370 = true;
			inputState.guessing++;
			try {
				{
				match("/=");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched370 = false;
			}
			rewind(_m370);
			inputState.guessing--;
		}
		if ( synPredMatched370 ) {
			match("/=");
			{
			int _cnt372=0;
			_loop372:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt372>=1 ) { break _loop372; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt372++;
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
			boolean synPredMatched374 = false;
			if (((LA(1)=='/') && (_tokenSet_6.member(LA(2))))) {
				int _m374 = mark();
				synPredMatched374 = true;
				inputState.guessing++;
				try {
					{
					match('/');
					mOPCHAR_NO_EQ(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched374 = false;
				}
				rewind(_m374);
				inputState.guessing--;
			}
			if ( synPredMatched374 ) {
				match('/');
				mOPCHAR_NO_EQ(false);
				{
				_loop376:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop376;
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
		
		boolean synPredMatched381 = false;
		if (((LA(1)=='+') && (_tokenSet_4.member(LA(2))))) {
			int _m381 = mark();
			synPredMatched381 = true;
			inputState.guessing++;
			try {
				{
				match('+');
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched381 = false;
			}
			rewind(_m381);
			inputState.guessing--;
		}
		if ( synPredMatched381 ) {
			match('+');
			{
			int _cnt383=0;
			_loop383:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt383>=1 ) { break _loop383; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt383++;
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
		
		boolean synPredMatched389 = false;
		if (((LA(1)=='-') && (LA(2)=='-') && (LA(3)=='>'))) {
			int _m389 = mark();
			synPredMatched389 = true;
			inputState.guessing++;
			try {
				{
				match("-->");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched389 = false;
			}
			rewind(_m389);
			inputState.guessing--;
		}
		if ( synPredMatched389 ) {
			match("-->");
			{
			int _cnt391=0;
			_loop391:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt391>=1 ) { break _loop391; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt391++;
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
			boolean synPredMatched393 = false;
			if (((LA(1)=='-') && (LA(2)=='-') && (_tokenSet_5.member(LA(3))))) {
				int _m393 = mark();
				synPredMatched393 = true;
				inputState.guessing++;
				try {
					{
					match("--");
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched393 = false;
				}
				rewind(_m393);
				inputState.guessing--;
			}
			if ( synPredMatched393 ) {
				match("--");
				mOPCHAR_NO_GT(false);
				{
				_loop395:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop395;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else {
				boolean synPredMatched397 = false;
				if (((LA(1)=='-') && (LA(2)=='>') && (_tokenSet_4.member(LA(3))))) {
					int _m397 = mark();
					synPredMatched397 = true;
					inputState.guessing++;
					try {
						{
						match("->");
						mOPCHAR(false);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched397 = false;
					}
					rewind(_m397);
					inputState.guessing--;
				}
				if ( synPredMatched397 ) {
					match("->");
					{
					int _cnt399=0;
					_loop399:
					do {
						if ((_tokenSet_4.member(LA(1)))) {
							mOPCHAR(false);
						}
						else {
							if ( _cnt399>=1 ) { break _loop399; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
						}
						
						_cnt399++;
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
					boolean synPredMatched401 = false;
					if (((LA(1)=='-') && (_tokenSet_7.member(LA(2))))) {
						int _m401 = mark();
						synPredMatched401 = true;
						inputState.guessing++;
						try {
							{
							match('-');
							mOPCHAR_NO_HYPHEN_OR_GT(false);
							}
						}
						catch (RecognitionException pe) {
							synPredMatched401 = false;
						}
						rewind(_m401);
						inputState.guessing--;
					}
					if ( synPredMatched401 ) {
						match('-');
						mOPCHAR_NO_HYPHEN_OR_GT(false);
						{
						_loop403:
						do {
							if ((_tokenSet_4.member(LA(1)))) {
								mOPCHAR(false);
							}
							else {
								break _loop403;
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
		
		boolean synPredMatched407 = false;
		if (((LA(1)=='*') && (_tokenSet_4.member(LA(2))))) {
			int _m407 = mark();
			synPredMatched407 = true;
			inputState.guessing++;
			try {
				{
				match('*');
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched407 = false;
			}
			rewind(_m407);
			inputState.guessing--;
		}
		if ( synPredMatched407 ) {
			match('*');
			{
			int _cnt409=0;
			_loop409:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt409>=1 ) { break _loop409; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt409++;
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
		
		boolean synPredMatched415 = false;
		if (((LA(1)=='<') && (LA(2)=='=') && (LA(3)=='>'))) {
			int _m415 = mark();
			synPredMatched415 = true;
			inputState.guessing++;
			try {
				{
				match("<=>");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched415 = false;
			}
			rewind(_m415);
			inputState.guessing--;
		}
		if ( synPredMatched415 ) {
			match("<=>");
			{
			int _cnt417=0;
			_loop417:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt417>=1 ) { break _loop417; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt417++;
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
			boolean synPredMatched419 = false;
			if (((LA(1)=='<') && (LA(2)=='=') && (_tokenSet_5.member(LA(3))))) {
				int _m419 = mark();
				synPredMatched419 = true;
				inputState.guessing++;
				try {
					{
					match("<=");
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched419 = false;
				}
				rewind(_m419);
				inputState.guessing--;
			}
			if ( synPredMatched419 ) {
				match("<=");
				mOPCHAR_NO_GT(false);
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
			else if ((LA(1)=='<') && (LA(2)=='=') && (true)) {
				match("<=");
				if ( inputState.guessing==0 ) {
					_ttype = LE;
				}
			}
			else {
				boolean synPredMatched423 = false;
				if (((LA(1)=='<') && (_tokenSet_6.member(LA(2))))) {
					int _m423 = mark();
					synPredMatched423 = true;
					inputState.guessing++;
					try {
						{
						match('<');
						mOPCHAR_NO_EQ(false);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched423 = false;
					}
					rewind(_m423);
					inputState.guessing--;
				}
				if ( synPredMatched423 ) {
					match('<');
					mOPCHAR_NO_EQ(false);
					{
					_loop425:
					do {
						if ((_tokenSet_4.member(LA(1)))) {
							mOPCHAR(false);
						}
						else {
							break _loop425;
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
		
		boolean synPredMatched430 = false;
		if (((LA(1)=='>') && (LA(2)=='=') && (_tokenSet_4.member(LA(3))))) {
			int _m430 = mark();
			synPredMatched430 = true;
			inputState.guessing++;
			try {
				{
				match(">=");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched430 = false;
			}
			rewind(_m430);
			inputState.guessing--;
		}
		if ( synPredMatched430 ) {
			match(">=");
			{
			int _cnt432=0;
			_loop432:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt432>=1 ) { break _loop432; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt432++;
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
			boolean synPredMatched434 = false;
			if (((LA(1)=='>') && (_tokenSet_6.member(LA(2))))) {
				int _m434 = mark();
				synPredMatched434 = true;
				inputState.guessing++;
				try {
					{
					match('>');
					mOPCHAR_NO_EQ(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched434 = false;
				}
				rewind(_m434);
				inputState.guessing--;
			}
			if ( synPredMatched434 ) {
				match('>');
				mOPCHAR_NO_EQ(false);
				{
				_loop436:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop436;
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
			_loop442:
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
					break _loop442;
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
			_loop445:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					break _loop445;
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
