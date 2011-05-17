# Make sure these three are set correctly before running Make
ANTLRPATH=/home/tiwari/hs-constraints/ashish-tools/hybridsal2xml/antlr-2.7.1/
JAVAC=javac
RTJARPATH=/usr/lib/jvm/java-6-openjdk/jre/lib/rt.jar

# Do not modify below.
JAVAFLAGS =
JAVACLASSPATH = .:${ANTLRPATH}:${ANTLRPATH}/antlr.jar:${RTJARPATH}::

.SUFFIXES:
.SUFFIXES: .java .class
.java.class : ; (export CLASSPATH=${JAVACLASSPATH}; $(JAVAC) $(JAVAFLAGS) $<)

install: all
	sed -e "s|__HYBRIDSAL_PATH__|${PWD}|g;s|__ANTLRPATH__|${ANTLRPATH}|g" hybridsal2xml.template > hybridsal2xml

all : HybridSalTokenTypes.class \
      HybridSalLexer.class \
      HybridSalParser.class \
      XmlAst.class \
      HybridSal2Xml.class

HybridSalParser.java HybridSalLexer.java HybridSalTokenTypes.java : HybridSalParser.g
	(export CLASSPATH=${JAVACLASSPATH}; java antlr.Tool $(ANTLRFLAGS) HybridSalParser.g)

test: hybridsal2xml examples/SimpleThermo3.sal all HybridSal2Xml.class
	rm -Rf examples/SimpleThermo3.xml
	hybridsal2xml examples/SimpleThermo3.sal > examples/SimpleThermo3.xml
	if [ -s examples/SimpleThermo3.xml ] ; then echo "hybridsal2xml installation successfully tested" ; fi

cleanall:
	rm -f *.class HybridSalParser.java HybridSalLexer.java \
			HybridSalTokenTypes.java
