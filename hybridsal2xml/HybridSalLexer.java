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
		{
		if ((LA(1)=='.')) {
			match('.');
			{
			int _cnt328=0;
			_loop328:
			do {
				if (((LA(1) >= '0' && LA(1) <= '9'))) {
					matchRange('0','9');
				}
				else {
					if ( _cnt328>=1 ) { break _loop328; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt328++;
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
		
		boolean synPredMatched333 = false;
		if (((LA(1)=='A') && (LA(2)=='N') && (LA(3)=='D'))) {
			int _m333 = mark();
			synPredMatched333 = true;
			inputState.guessing++;
			try {
				{
				match("AND");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched333 = false;
			}
			rewind(_m333);
			inputState.guessing--;
		}
		if ( synPredMatched333 ) {
			match("AND");
			{
			int _cnt335=0;
			_loop335:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt335>=1 ) { break _loop335; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt335++;
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
		
		boolean synPredMatched338 = false;
		if (((LA(1)=='O') && (LA(2)=='R') && (_tokenSet_3.member(LA(3))))) {
			int _m338 = mark();
			synPredMatched338 = true;
			inputState.guessing++;
			try {
				{
				match("OR");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched338 = false;
			}
			rewind(_m338);
			inputState.guessing--;
		}
		if ( synPredMatched338 ) {
			match("OR");
			{
			int _cnt340=0;
			_loop340:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt340>=1 ) { break _loop340; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt340++;
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
		
		boolean synPredMatched343 = false;
		if (((LA(1)=='X') && (LA(2)=='O') && (LA(3)=='R'))) {
			int _m343 = mark();
			synPredMatched343 = true;
			inputState.guessing++;
			try {
				{
				match("XOR");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched343 = false;
			}
			rewind(_m343);
			inputState.guessing--;
		}
		if ( synPredMatched343 ) {
			match("XOR");
			{
			int _cnt345=0;
			_loop345:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt345>=1 ) { break _loop345; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt345++;
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
		
		boolean synPredMatched348 = false;
		if (((LA(1)=='N') && (LA(2)=='O') && (LA(3)=='T'))) {
			int _m348 = mark();
			synPredMatched348 = true;
			inputState.guessing++;
			try {
				{
				match("NOT");
				mALPHANUM(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched348 = false;
			}
			rewind(_m348);
			inputState.guessing--;
		}
		if ( synPredMatched348 ) {
			match("NOT");
			{
			int _cnt350=0;
			_loop350:
			do {
				if ((_tokenSet_3.member(LA(1)))) {
					mALPHANUM(false);
				}
				else {
					if ( _cnt350>=1 ) { break _loop350; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt350++;
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
		
		boolean synPredMatched358 = false;
		if (((LA(1)=='=') && (LA(2)=='>') && (_tokenSet_4.member(LA(3))))) {
			int _m358 = mark();
			synPredMatched358 = true;
			inputState.guessing++;
			try {
				{
				match("=>");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched358 = false;
			}
			rewind(_m358);
			inputState.guessing--;
		}
		if ( synPredMatched358 ) {
			match("=>");
			{
			int _cnt360=0;
			_loop360:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt360>=1 ) { break _loop360; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt360++;
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
			boolean synPredMatched362 = false;
			if (((LA(1)=='=') && (_tokenSet_5.member(LA(2))))) {
				int _m362 = mark();
				synPredMatched362 = true;
				inputState.guessing++;
				try {
					{
					match('=');
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched362 = false;
				}
				rewind(_m362);
				inputState.guessing--;
			}
			if ( synPredMatched362 ) {
				match('=');
				mOPCHAR_NO_GT(false);
				{
				_loop364:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop364;
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
		
		boolean synPredMatched369 = false;
		if (((LA(1)=='/') && (LA(2)=='=') && (_tokenSet_4.member(LA(3))))) {
			int _m369 = mark();
			synPredMatched369 = true;
			inputState.guessing++;
			try {
				{
				match("/=");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched369 = false;
			}
			rewind(_m369);
			inputState.guessing--;
		}
		if ( synPredMatched369 ) {
			match("/=");
			{
			int _cnt371=0;
			_loop371:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt371>=1 ) { break _loop371; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt371++;
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
			boolean synPredMatched373 = false;
			if (((LA(1)=='/') && (_tokenSet_6.member(LA(2))))) {
				int _m373 = mark();
				synPredMatched373 = true;
				inputState.guessing++;
				try {
					{
					match('/');
					mOPCHAR_NO_EQ(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched373 = false;
				}
				rewind(_m373);
				inputState.guessing--;
			}
			if ( synPredMatched373 ) {
				match('/');
				mOPCHAR_NO_EQ(false);
				{
				_loop375:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop375;
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
		
		boolean synPredMatched380 = false;
		if (((LA(1)=='+') && (_tokenSet_4.member(LA(2))))) {
			int _m380 = mark();
			synPredMatched380 = true;
			inputState.guessing++;
			try {
				{
				match('+');
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched380 = false;
			}
			rewind(_m380);
			inputState.guessing--;
		}
		if ( synPredMatched380 ) {
			match('+');
			{
			int _cnt382=0;
			_loop382:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt382>=1 ) { break _loop382; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt382++;
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
		
		boolean synPredMatched388 = false;
		if (((LA(1)=='-') && (LA(2)=='-') && (LA(3)=='>'))) {
			int _m388 = mark();
			synPredMatched388 = true;
			inputState.guessing++;
			try {
				{
				match("-->");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched388 = false;
			}
			rewind(_m388);
			inputState.guessing--;
		}
		if ( synPredMatched388 ) {
			match("-->");
			{
			int _cnt390=0;
			_loop390:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt390>=1 ) { break _loop390; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt390++;
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
			boolean synPredMatched392 = false;
			if (((LA(1)=='-') && (LA(2)=='-') && (_tokenSet_5.member(LA(3))))) {
				int _m392 = mark();
				synPredMatched392 = true;
				inputState.guessing++;
				try {
					{
					match("--");
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched392 = false;
				}
				rewind(_m392);
				inputState.guessing--;
			}
			if ( synPredMatched392 ) {
				match("--");
				mOPCHAR_NO_GT(false);
				{
				_loop394:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop394;
					}
					
				} while (true);
				}
				if ( inputState.guessing==0 ) {
					_ttype = IDENTIFIER;
				}
			}
			else {
				boolean synPredMatched396 = false;
				if (((LA(1)=='-') && (LA(2)=='>') && (_tokenSet_4.member(LA(3))))) {
					int _m396 = mark();
					synPredMatched396 = true;
					inputState.guessing++;
					try {
						{
						match("->");
						mOPCHAR(false);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched396 = false;
					}
					rewind(_m396);
					inputState.guessing--;
				}
				if ( synPredMatched396 ) {
					match("->");
					{
					int _cnt398=0;
					_loop398:
					do {
						if ((_tokenSet_4.member(LA(1)))) {
							mOPCHAR(false);
						}
						else {
							if ( _cnt398>=1 ) { break _loop398; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
						}
						
						_cnt398++;
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
					boolean synPredMatched400 = false;
					if (((LA(1)=='-') && (_tokenSet_7.member(LA(2))))) {
						int _m400 = mark();
						synPredMatched400 = true;
						inputState.guessing++;
						try {
							{
							match('-');
							mOPCHAR_NO_HYPHEN_OR_GT(false);
							}
						}
						catch (RecognitionException pe) {
							synPredMatched400 = false;
						}
						rewind(_m400);
						inputState.guessing--;
					}
					if ( synPredMatched400 ) {
						match('-');
						mOPCHAR_NO_HYPHEN_OR_GT(false);
						{
						_loop402:
						do {
							if ((_tokenSet_4.member(LA(1)))) {
								mOPCHAR(false);
							}
							else {
								break _loop402;
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
		
		boolean synPredMatched406 = false;
		if (((LA(1)=='*') && (_tokenSet_4.member(LA(2))))) {
			int _m406 = mark();
			synPredMatched406 = true;
			inputState.guessing++;
			try {
				{
				match('*');
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched406 = false;
			}
			rewind(_m406);
			inputState.guessing--;
		}
		if ( synPredMatched406 ) {
			match('*');
			{
			int _cnt408=0;
			_loop408:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt408>=1 ) { break _loop408; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt408++;
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
		
		boolean synPredMatched414 = false;
		if (((LA(1)=='<') && (LA(2)=='=') && (LA(3)=='>'))) {
			int _m414 = mark();
			synPredMatched414 = true;
			inputState.guessing++;
			try {
				{
				match("<=>");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched414 = false;
			}
			rewind(_m414);
			inputState.guessing--;
		}
		if ( synPredMatched414 ) {
			match("<=>");
			{
			int _cnt416=0;
			_loop416:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt416>=1 ) { break _loop416; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt416++;
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
			boolean synPredMatched418 = false;
			if (((LA(1)=='<') && (LA(2)=='=') && (_tokenSet_5.member(LA(3))))) {
				int _m418 = mark();
				synPredMatched418 = true;
				inputState.guessing++;
				try {
					{
					match("<=");
					mOPCHAR_NO_GT(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched418 = false;
				}
				rewind(_m418);
				inputState.guessing--;
			}
			if ( synPredMatched418 ) {
				match("<=");
				mOPCHAR_NO_GT(false);
				{
				_loop420:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop420;
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
				boolean synPredMatched422 = false;
				if (((LA(1)=='<') && (_tokenSet_6.member(LA(2))))) {
					int _m422 = mark();
					synPredMatched422 = true;
					inputState.guessing++;
					try {
						{
						match('<');
						mOPCHAR_NO_EQ(false);
						}
					}
					catch (RecognitionException pe) {
						synPredMatched422 = false;
					}
					rewind(_m422);
					inputState.guessing--;
				}
				if ( synPredMatched422 ) {
					match('<');
					mOPCHAR_NO_EQ(false);
					{
					_loop424:
					do {
						if ((_tokenSet_4.member(LA(1)))) {
							mOPCHAR(false);
						}
						else {
							break _loop424;
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
		
		boolean synPredMatched429 = false;
		if (((LA(1)=='>') && (LA(2)=='=') && (_tokenSet_4.member(LA(3))))) {
			int _m429 = mark();
			synPredMatched429 = true;
			inputState.guessing++;
			try {
				{
				match(">=");
				mOPCHAR(false);
				}
			}
			catch (RecognitionException pe) {
				synPredMatched429 = false;
			}
			rewind(_m429);
			inputState.guessing--;
		}
		if ( synPredMatched429 ) {
			match(">=");
			{
			int _cnt431=0;
			_loop431:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					if ( _cnt431>=1 ) { break _loop431; } else {throw new NoViableAltForCharException((char)LA(1), getFilename(), getLine());}
				}
				
				_cnt431++;
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
			boolean synPredMatched433 = false;
			if (((LA(1)=='>') && (_tokenSet_6.member(LA(2))))) {
				int _m433 = mark();
				synPredMatched433 = true;
				inputState.guessing++;
				try {
					{
					match('>');
					mOPCHAR_NO_EQ(false);
					}
				}
				catch (RecognitionException pe) {
					synPredMatched433 = false;
				}
				rewind(_m433);
				inputState.guessing--;
			}
			if ( synPredMatched433 ) {
				match('>');
				mOPCHAR_NO_EQ(false);
				{
				_loop435:
				do {
					if ((_tokenSet_4.member(LA(1)))) {
						mOPCHAR(false);
					}
					else {
						break _loop435;
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
			_loop441:
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
					break _loop441;
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
			_loop444:
			do {
				if ((_tokenSet_4.member(LA(1)))) {
					mOPCHAR(false);
				}
				else {
					break _loop444;
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
