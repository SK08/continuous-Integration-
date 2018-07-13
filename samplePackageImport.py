#   THIS CODE AND INFORMATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS
#   FOR A PARTICULAR PURPOSE. THIS CODE AND INFORMATION ARE NOT SUPPORTED BY XEBIALABS.

import sys
import os
from org.jdom2 import Element, Text, Document
from org.jdom2.output import XMLOutputter
import re
from java.io import File, FileInputStream, FileOutputStream
from java.util.zip import ZipEntry, ZipOutputStream
from jarray import zeros



###########  Class Definitions #######################
class Deployable(object):
	def __init__(self, name, type):
		self.name = name
		self.type= type
		self.properties = {}
		self.file = None
	
	def add(self, key, value):
		self.properties[key] = value
	
	def _toXmlElement(self):
		d = Element(self.type)
		d.setAttribute("name", self.name)
		if (self.file):
			d.setAttribute("file", self.file)
		for prop,val in self.properties.items():
			if not val:
				continue
			p = Element(prop)
			if isinstance(val, type([])):
				for listVal in val:
					v = Element("value")
					v.addContent(Text(listVal))
					p.addContent(v)
			elif isinstance(val,type({})):
				for k,v in val.items:
					e = Element("entry")
					e.setAttribute("key",k)
					e.addContent(Text(v))
					p.addContent(e)
			else:
				p.addContent(Text(val))
			d.addContent(p)
		return d		

class Manifest(object):
	
	def __init__(self,application,version):
		self.application = application
		self.version = version
		self.deployables = []
	
	def add(self,d):
		self.deployables.append(d)
	
	def toXml(self):
		depApp = Element("udm.DeploymentPackage")
		depApp.setAttribute("version",self.version)
		depApp.setAttribute("application",self.application)
		deployables = Element("deployables")
		for deployable in self.deployables:
			deployables.addContent(deployable._toXmlElement())
		depApp.addContent(deployables)
		xmlOutput = XMLOutputter()
		return xmlOutput.outputString(Document(depApp))


###########  Function Definitions #######################
def zipdir(basedir, archivename):
	assert os.path.isdir(basedir)
	fos = FileOutputStream(archivename)
	zos = ZipOutputStream(fos)
	addFolder(zos, basedir, basedir)
	zos.close()

def addFolder(zos,folderName,baseFolderName):
	f = File(folderName)
	if not f.exists():
		return
	if f.isDirectory():
		for f2 in f.listFiles():
			addFolder(zos,f2.absolutePath,baseFolderName)
		return
	entryName = folderName[len(baseFolderName)+1:len(folderName)]
	ze = ZipEntry(entryName)
	zos.putNextEntry(ze)
	inputStream = FileInputStream(folderName)
	buffer = zeros(1024, 'b')
	rlen = inputStream.read(buffer)
	while (rlen > 0):
		zos.write(buffer, 0, rlen)
		rlen = inputStream.read(buffer)
	inputStream.close()
	zos.closeEntry()

def writeManifest(path, manifest):
	f= open(os.path.join(path,"deployit-manifest.xml"), "w")
	xml = manifest.toXml()
	print xml
	f.write(xml)
	f.close()

# look for files with CAR extension - associate them to comp.CarAppArchive
# deployabes, and add them to the manifest
def createCARAPPDeployables(manifest,appHome):
	cronacleAppHome = appHome + os.sep + "Cronacle"
	carFiles = [f for f in os.listdir(cronacleAppHome) if f.endswith('.CAR')]
	print carFiles
	for carFile in carFiles:
		d = Deployable(carFile[0:carFile.rfind('.')], "comp.CarAppArchive")
		d.file = "CARAPP/%s" % carFile
		manifest.add(d)

# look for XML files - associate them to comp.FileAppXML deployabes, and
# add them to the manifest
def createFileAppDeployables(manifest,appHome):
	pcAppHome = appHome + os.sep + "FileApp"
	pcFiles = [f for f in os.listdir(pcAppHome) if f.endswith('.xml')]
	for pcFile in pcFiles:
		d = Deployable(pcFile[0:pcFile.rfind('.')], "comp.FileAppXml")
		d.file = "FileApp/%s" % pcFile
		f = open(pcAppHome + os.sep + pcFile)
		folders = []
		repoFound = False
		for line in f:
			if not repoFound:
				repoMatch = re.match(r'<REPOSITORY NAME="([A-Z_0-9a-z]*)"',line)
				if (repoMatch):
					d.add("sourceRepository",repoMatch.group(1))
					repoFound = True
			folderMatch = re.match( r'<FOLDER NAME="([A-Z_0-9a-z]*)"', line)
			if (folderMatch):
				folders.append(folderMatch.group(1))
		d.add("folderNames",folders)
		manifest.add(d)

def generatePackage(appName,appVersion,exportHome):
	appHome = exportHome + os.sep + appName
	manifest = Manifest(appName,appVersion)
	createCARAPPDeployables(manifest,appHome)
	createFileAppDeployables(manifest,appHome)
	writeManifest(appHome,manifest)
	zipdir(appHome, "%s%s%s-%s.dar" % (exportHome,os.sep,appName,appVersion))

###########  Global Definitions #######################
appName="YOUR_APP"
appVersion="1.0"
exportHome="/your/export/path"
