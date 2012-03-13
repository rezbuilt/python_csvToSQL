import csv,os,time,urllib,urllib2,time


fileDirectory = "data_stores/businessLists"
sleep_time = 2
root_url = "http://maps.google.com/maps/geo?"
gkey = "APIKEY"
return_codes = {'200':'SUCCESS',
	'400':'BAD REQUEST',
	'500':'SERVER ERROR',
	'601':'MISSING QUERY',
	'602':'UNKOWN ADDRESS',
	'603':'UNAVAILABLE ADDRESS',
	'604':'UNKOWN DIRECTIONS',
	'610':'BAD KEY',
	'620':'TOO MANY QUERIES'
}


def listOptions():
	fileCount = 0
	fileArr = []
	print(' Select a CSV file in ' + fileDirectory)
	for filename in os.listdir(fileDirectory):
		print('');
		fileArr.append([])
		print '   ' + str(fileCount + 1) + ' - ' + filename.replace('_', ' ').replace('.csv','');
		fileArr[fileCount].append(filename)
		fileCount = fileCount + 1
	print '   0 - Exit'
	return fileArr

def listData(data):
	dataCount = 0
	print(' Headings: ')
	for row in data[0]:
		print '   ' + str(dataCount + 1) + ' - ' + row;
		dataCount = dataCount + 1

def questionStore():
	print('');
	var = raw_input(" Which Data Store?: ")
	if(var == '0'):
		os._exit(1)
	return var

def questionData():
	print('');
	qvar = raw_input("  List attributes (comma delimited): ")
	return qvar
def questionAddData():
	print('');
	qvaradd = raw_input("  List address attributes to geocode with (comma delimited): ")
	return qvaradd

def questionAtt(att):
	print('   Heading: ' + att);
	qavar = raw_input("   Column:  ")
	return qavar

def questionTable():
	table = raw_input("   Insert table name:  ")
	return table

def questionFile():
	print(' ')
	print('   Save to File')
	dir = raw_input("   File name/directory:  ")
	return dir

def questionAddl():
	print(' ')
	dirQatt = raw_input("   Attribute Name:  ")
	dirQval = raw_input("   Attrubute Value: ")
	return dirQatt + ',' + dirQval

def questionHowManyAdl():
	print(' ')
	dirQ = raw_input("   Would you like to add additional attributes? [y/n]:  ")
	print(' ');

	if(str(dirQ) == 'y'):
		return 	int(raw_input("   How many additional attributes?:  "))
	else:
		return 0

def questionGeoCode():
	print('')
	geoQ = raw_input("   Would you like to geocode address? [y/n]:  ")
	return geoQ


def geocode(addr,out_fmt='csv'):

	#encode our dictionary of url parameters
	values = {'q' : addr, 'output':out_fmt, 'key':gkey}
	data = urllib.urlencode(values)

	#set up our request
	url = root_url+data
	req = urllib2.Request(url)

	#make request and read response
	response = urllib2.urlopen(req)
	geodat = response.read().split(',')
	response.close()

	#handle the data returned from google
	code = return_codes[geodat[0]]

	if code == 'SUCCESS':
		code,precision,lat,lng = geodat
		print('Geocoded: ' + addr)
		return {'code':code,'precision':precision,'lat':lat,'lng':lng}
	else:
		return {'code':code}

def start():
	files = listOptions()
	selected = questionStore()	
	fileName = files[0][int(selected) - 1]
	file = open(fileDirectory + '/' + str(fileName),"rb")
	return file
#start here
print('                       ')
print('     CSV to SQL Insert/Update + Geocoding & Additional Attributes  ')
print('     Created by:   Michael Rzeznik - rezbuilt.com   ')
print('     Created on:   3/10/12 ')
print('     Updated on:   3/12/12 ')
print('     Version:      1.4 ')
print('                       ')

file = start()
allRows = csv.reader(file, delimiter=',')

dataStructure = []
dataCount = 0

for row in allRows:
	dataStructure.append([])
	dataStructure[dataCount].append(row)
	dataCount = dataCount + 1

listData(dataStructure[0])
allHeads = []
headings = questionData()

allHeads = headings.split(',')
finalArray = []

print('   Assign database column names to attributes')
print('')
for h in allHeads:
	thisAttInt = int(h) - 1;
	thisAtt = dataStructure[0][0][thisAttInt]
	finalArray.append(str(thisAttInt) + ',' + questionAtt(thisAtt))


sqlBuild = ''

addl = []
howManyAdl = questionHowManyAdl()
for i in range(howManyAdl):
	allQueryQuestion = questionAddl()
	if(allQueryQuestion != ''):
		addl.append(allQueryQuestion)
	
table = questionTable()

qCode = questionGeoCode()
isGeo = 0

if(qCode == 'y'):
	isGeo = 1
	listData(dataStructure[0])
	allAddAtts = []
	addressAtts = questionAddData()
	allAddAtts = addressAtts.split(',')
	latAtt = raw_input("  Latitude Database Column:  ")
	lonAtt = raw_input("  Longitude Database Column: ")

for fa in dataStructure:
	eachAtt = []
	sqlBuild = sqlBuild + " INSERT INTO `" + table + "` SET "
	arrLen = len(finalArray);
	arrCount = 0;
	for arrer in finalArray:
		eachAtt = arrer.split(',')	
		arrCount = arrCount + 1
		if(arrCount == arrLen):
			sqlBuild = sqlBuild + " `" + eachAtt[1] + '` = "' + fa[0][int(eachAtt[0])] + '" '
		else:
			sqlBuild = sqlBuild + " `" + eachAtt[1] + '` = "' + fa[0][int(eachAtt[0])] + '", '
	
	harrLen = len(addl)
	harrCount = 0

	for harrer in addl:
		heachAtt = harrer.split(',')	

		if(harrCount == 0):
			sqlBuild = sqlBuild + ', '

		harrCount = harrCount + 1

		if(harrCount == harrLen):
			sqlBuild = sqlBuild + " `" + heachAtt[0] + '` = "' + heachAtt[1] + '" '
		else:
			sqlBuild = sqlBuild + " `" + heachAtt[0] + '` = "' + heachAtt[1] + '", '
		
	if(isGeo == 1):
		toGeoAddress = '';
		for aAtt in allAddAtts:
			if(fa[0][int(aAtt)] != ''):
				toGeoAddress = toGeoAddress + fa[0][int(aAtt)] + ' '
			
		geoData = geocode(toGeoAddress)
		if len(geoData) > 1:
				sqlBuild = sqlBuild + ', `' + latAtt + '` = "' + geoData['lat'] + '" '
				sqlBuild = sqlBuild + ', `' + lonAtt + '` = "' + geoData['lng'] + '" '



	sqlBuild = sqlBuild + ';'

print sqlBuild

filer = questionFile()

finalFile = open(filer,"w")
finalFile.write(sqlBuild)
finalFile.close()
