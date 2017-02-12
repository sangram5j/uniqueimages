#!/usr/bin/python

import sys
import re
import os
import exifread
from PIL import Image
from PIL.ExifTags import TAGS	
from array import array

FLIDX = 0
FLPATHIDX = 1
FLSZIDX = 2
CNTIDX = 3
imagetyps = ['.jpg', '.jpeg', '.png', '.mov', '.mts']#Have set all the types to lower-case 
strslash = '/'
ufid_var = []
fltrfl = 'filefilter.txt'

def DbgFile(ufid_var):
	fd = open('allentries.csv', 'w')
	for entry in ufid_var:
		fd.write(str(entry) + '\n')
	fd.close()

def getimginfo(fn):
	ret = {}
	print(fn)
	try:
		i = Image.open(fn)
		info = i._getexif()
		for tag, value in info.items():
			decoded = TAGS.get(tag, tag)
			ret[decoded] = value
	except IOError:
		print "Error: can\'t read Image-file", fn
	except:
		print "Error: Image-file tags are empty", fn
	return ret

def imagetype(fl):
	fl = fl.lower()
	for i in range(0, len(imagetyps)):
		if fl.endswith(imagetyps[i]) == True:
			return True
	return False

def uqcount(lufidtImglst, fl):
	c_matchidx = -1
	if len(lufidtImglst) > 0:
		for entry in lufidtImglst:
			c_matchidx = c_matchidx + 1
			if entry[FLIDX]==fl:
				return c_matchidx 

	return -1

def retainmatch(flno, selarr):
	for i in range(0, len(selarr) - 2):
		if flno == selarr[i]:
			return True
	return False

def delimagefile(flstr):
	print "\n" + flstr + "\n"
	ch = raw_input("Do you want to delete the file(Press y/n) : ")
	if ch == 'y':
		os.remove(flstr)

def eliminatefl(entry):
	onekB = 1024
	nofls = len(entry[FLPATHIDX])
	print "\n----------->Deleting the redundant files------->"
	print "------------------------------------------------->"
	for i in range(0, nofls):
		flsz = float(entry[FLSZIDX][i])/onekB
		print entry[FLPATHIDX][i] + entry[FLIDX] + " (" + str(float("{0:.2f}".format(flsz))) + "KB)" + " : " + str(i)

	inputstr = "\nEnter r(fl_no1, fl_no2...) to retain and delete rest:\
				 \nEnter d(fl_no1, fl_no2...) to delete set of files:\
					\nEnter n to skip\n"	
	ch = raw_input(inputstr)
	spch = re.split('[(,)]', ch)
	try:
		if len(spch) <= 0: 		
			raise Exception("Input syntax error")
		if spch[0] == 'r':
			for i in range(0, nofls):
				if retainmatch(i, spch) == False:								
					filenm = entry[FLPATHIDX][int(spch[i+1])] + entry[FLIDX]
					delimagefile(filenm)
					print "\nDeletion success\n------------------------------------->"
		elif spch[0] == 'd':
			for i in range(0, len(spch) - 2):
				filenm = entry[FLPATHIDX][int(spch[i+1])] + entry[FLIDX]
				delimagefile(filenm)
				print "\nDeletion success\n------------------------------------->"
		elif spch[0] == 'n':
			print "skipping the file :" + entry[FLIDX]
			print "\n------------------------------------->"
	except:
		print "Error: Unexpected error deleting the image file"		
	
def scanfiles(Imgpath):
	# traverse root directory, and list directories as dirs and files as files
	for root, dirs, files in os.walk(Imgpath):
		path = root.split(os.sep)
		for fl in files:
			if imagetype(fl) == True:
				filepath = '/'.join(path) + strslash
				#print(filepath + fl)
				statinfo = os.stat(filepath + fl)
				ufid_var.append((fl, filepath, statinfo.st_size))
				#imgattr = getimginfo(filepath + fl)
				#print(imgattr['ExifImageWidth'],  imgattr['ExifImageHeight'])
		#DbgFile(ufid_var)
			else:
				#print("file not image type", fl)
				print("")
	print "Total Image entries : " + str(len(ufid_var))

	curridx = 0
	ufidtImglst = []	
	for entry in ufid_var:
		curridx = curridx + 1
		idx = uqcount(ufidtImglst, entry[FLIDX])	
		if  idx == -1:
			ufidtImglst.append((entry[FLIDX], [entry[FLPATHIDX]], entry[FLSZIDX], 1)) 
		else:
			#print("Found duplicate entry: curridx ", curridx, ufidtImglst[idx], "Current entry", entry)
			tmppatha = list(ufidtImglst[idx])
			tmppathb = list(tmppatha[FLPATHIDX])
			tmppathc = array('L', [tmppatha[FLSZIDX]])
			tmppathb.append(entry[FLPATHIDX])
			tmppathc.append(entry[FLSZIDX])
			tmppatha = (tmppatha[FLIDX], tuple(tmppathb), tuple(tmppathc), tmppatha[CNTIDX]+1)
			ufidtImglst[idx] = tuple(tmppatha)
		
	print "No of duplicate entries : " + str(len(ufid_var) - len(ufidtImglst))
	ufidtImglst = list(ufidtImglst)
	for entry in ufidtImglst:
		if entry[CNTIDX] > 1:
			eliminatefl(entry)

def loadfiltypes():
	try:
		fd = open(fltrfl, 'r')
		imagetypes = str(fd.readline())
		print "Please edit the " + fltrfl + " file"
		print "File types considered :" + imagetypes
		fd.close()
	except:
		print "\nFile types not found, condsidering the default ones:\n"
		print str(imagetypes)

def main(argv):
	if len(argv) > 1:
		loadfiltypes()		
		photo_path = argv[1]
		print "Scanning the image path : \"" + photo_path + "\""
		scanfiles(photo_path)
		sys.exit("\nThanks for using the script !!!")
	else:
		sys.exit("Exiting the application as the file path is invalid")



if __name__ == "__main__":
	main(sys.argv)
