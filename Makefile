
example=examples/hsal-xml/SimpleThermo4.xml

all:
	python src/HSalExtractRelAbs.py ${example} > /tmp/1.xml
	python src/HSalXMLPP.py ${example}
	python src/HSalXMLPP.py /tmp/1.xml
