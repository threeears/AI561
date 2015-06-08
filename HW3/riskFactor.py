import sys

class Node:
	
	def __init__(self, name,no):
		self.name = name
		self.no = no
		self.valueList = []# categorized variables for the  node's feature
		self.parent = []#parent nodes 
		self.CPT = {} # CPT table for the node, it is a dictionary
		self.parentBase = {} # the counts of parents' combinations

class Query:
	
	def __init__(self, no):
		self.no = no
		self.res = 0
		self.emuList = {"0":[],"1":[]} #{"0":[enumeration list for all exist features],"1":[enumeration list for conditional exist features]}	
		self.fixDic = {} # key-value pairs stores all exist features and their standardized categories
		self.conDic = {}# key-value pairs stores conditional features existed with their categories
		self.andList = []# list name of all exist features
		self.alfaList = [] # list name of conditional exist features
		

def roundRes (res):
	# round the possibility into 4 digits decimal 
	res = str(round(res,4))
	if 6-len(res)!=0:
		for i in range(0,6-len(res)):
			res = res+'0'
	return res


def findAllConditions(curNode,start,clist,cstring):
	# find all conditional features for current node
	# exp: smoke has only one parent that is income, then the all condition for income is 
	# income < 25000: 0, 25000<income<50000:1, 50000<income<750000: 2, >750000:3

	if start == len(curNode.parent):#reach the last level
		item = ""+cstring
		clist.append(item)
		#print item
		return

	for i in range(0,len(curNode.parent[start].valueList)):
		#print "current parent is %s" %curNode.parent[start].name
		#print "current value is %d"%i
		cstring+=str(curNode.parent[start].no)+str(i)
		findAllConditions(curNode,start+1,clist,cstring)
		cstring=cstring[0:-2]
	return 


def findAllCombinations(curNode,cList,curDic,nodeNum):
	#  combination of conditional features and query features
	#  after found all the combinations of parents, now we add the current node to the 
	#  combination as well, which leads to all the rows in the nodes' CPT table we need

	curValueList = curNode.valueList
	for i in range(0,len(curValueList)):
		for j in range(0,len(cList)):
			item = str(nodeNum)+str(i)+cList[j]
			curDic[item]=0


def createCPT(nodeList,dataList):
	#each CPT is represented as a dictionary, 
	#where key is the footprint of conditional query, value is its correspondent possibility

	# find all rows in the CPT table
	for i in range(0,len(nodeList)):
		# print "********************************************************"
		# print nodeList[i].name
		curNode = nodeList[i]#node i in the list
		curDic = {}#CPT table for current node
		curParent = curNode.parent
		curVL = curNode.valueList
		cList = []
		findAllConditions(curNode,0,cList,"")
		findAllCombinations(curNode,cList,curDic,i)
		nodeList[i].CPT = curDic
		#print nodeList[i].CPT
		parentBase={}

		for m in range(0,len(cList)):
			parentBase[cList[m]]=0
		nodeList[i].parentBase = parentBase
		# print "parent bases are: "
		# print parentBase

		digits = [] #digit to look out for  in  order to check patterns
		for k in range(0,len(curParent)):
			digits.append(curParent[k].no)
		#print digits
		#build CPT node by node,

		for j in range(0,len(dataList)):
			# scan through datalist to compute CPT for each item in CPT table(dictionary)
			if len(curParent)==0:
				#check  if it has parent 
				nodeList[i].parentBase["full"]=len(dataList)
				itemPattern_Condition = str(curNode.no)+str(dataList[j][curNode.no])
				nodeList[i].CPT[itemPattern_Condition]+=1
			else:
				itemPattern_Parent = ""
				for m in digits:
					itemPattern_Parent+=str(m) +str(dataList[j][m])
				nodeList[i].parentBase[itemPattern_Parent]+=1

				itemPattern_Condition = str(curNode.no)+str(dataList[j][curNode.no])+itemPattern_Parent
				nodeList[i].CPT[itemPattern_Condition]+=1

		
	for i in range(0,len(nodeList)):
		# print "****************"
		# print nodeList[i].name
		for key in nodeList[i].CPT:
			p = key[2:]
			if len(p)==0:
				nodeList[i].CPT[key] = (1.0 * nodeList[i].CPT[key])/nodeList[i].parentBase["full"]
			else:
				nodeList[i].CPT[key] = (1.0 * nodeList[i].CPT[key])/nodeList[i].parentBase[p]
		#print nodeList[i].CPT
				
	return

	
def prepQuery(qList,queryItem,nodeList):

	emuList = []
	
	for i in range(0,len(qList)):
		dicItem = qList[i]
		#print dicItem
		for k in range(0,len(nodeList)):
			if nodeList[k].name in dicItem:
				# if the node is in the query
				# standardize it in my CPT category
				values = nodeList[k].valueList
				if nodeList[k].name == "income":
					for j in range(0,len(income.valueList)):
						if int(qList[i][nodeList[k].name]) <= int(income.valueList[j]):
							if i==1:
								queryItem.conDic["income"]=j
							queryItem.fixDic["income"]=j
							break
				elif nodeList[k].name == "bmi":
					for j in range(0,len(bmi.valueList)):
						if qList[i][nodeList[k].name] == bmi.valueList[j]:
							if i==1:
								queryItem.conDic["bmi"]=j
							queryItem.fixDic["bmi"]=j
				else:
					if qList[i][nodeList[k].name]=='yes':
						if i==1:
							queryItem.conDic[nodeList[k].name]=1
						queryItem.fixDic[nodeList[k].name]=1

					else:
						if i==1:
							queryItem.conDic[nodeList[k].name]=0
						queryItem.fixDic[nodeList[k].name]=0
					
		# specify two and lists, one is condition+query, one is condition

		for key in dicItem:
			if i == 1:
				queryItem.alfaList.append(key)
			queryItem.andList.append(key)

	# find enumarations for comdition+query and condition lists
	emu0=[]
	emu1=[]
	fix0=[]
	fix1=[]
	for m in nodeList:
		if m.name in queryItem.fixDic:
			emu0.append(m)
			fix0.append(m)
		if m.name in qList[1]:
			emu1.append(m)
			fix1.append(m)

	
	emu0=findEnumerationList(queryItem,emu0,nodeList)
	emu1=findEnumerationList(queryItem,emu1,nodeList)

	i = 0
	while i < len(emu0):
		if emu0[i] in fix0:
			emu0.remove(emu0[i])
		else:
			i+=1
	i=0
	while i < len(emu1):
		if emu1[i] in fix1:
			emu1.remove(emu1[i])
		else:
			i+=1

	queryItem.emuList["0"]=emu0
	queryItem.emuList["1"]=emu1




def findEnumerationList(queryItem,emuList,nodeList):
	#emuList here is a list of objects, try to find all the objects to enumerate
	if isClosedEnumeration(emuList,nodeList)==True:
		return emuList
	else:
		for i in nodeList:
			if i in emuList:
				for item in i.parent:
					if item  not in emuList:
						emuList.append(item)

	return findEnumerationList(queryItem,emuList,nodeList)


def isClosedEnumeration(emuList, nodeList):
	# emuList here is a list of objects, check if found the all objects
	for i in emuList:
		for j in i.parent:
			if j not in emuList:
				return False
	return True

def AndProbability(nodeList,fixDic,andList,emuList,tempDic,level,res):
	#calculate joint probability
	
	if len(emuList)==0:
		#print "no need to expand"
		r = cal_AndHelper(tempDic,nodeList)
		res.append(r)
		return res

	if level == len(emuList):
		#start adding on res
		r = cal_AndHelper(tempDic,nodeList)
		res.append(r)
		return 
		

	curEmu = emuList[level] # it is a node now
	for i in range(0,len(curEmu.valueList)):
		tempDic[curEmu.name] = i
		AndProbability(nodeList,fixDic,andList,emuList,tempDic,level+1,res)
	
	return res

def cal_AndHelper(dictionary,nodeList):
	#EXP:dictionary = {'bmi': 0, 'stroke': 1, 'bp': 0, 'smoke': 0, 'income': 2, 'cholesterol': 0, 'exercise': 0}
	#print dictionary
	cptDic = {}

	for i in range(0,len(nodeList)):
		if nodeList[i].name in dictionary:
			# find the CPT for node i
			parentI = nodeList[i].parent
			footprint = str(i)+str(dictionary[nodeList[i].name])
			for j in parentI:
				footprint+=str(j.no)+str(dictionary[nodeList[j.no].name])
			cptDic[footprint] = nodeList[i].CPT[footprint]
	#print cptDic
	res = 1
	for key in cptDic:
		res*=cptDic[key]
	#print res
	return res



""" SET UP THE GRAPH """
#constructing the graph, attention, the category is ordered in the same way as python list element ordering
income = Node("income",0)
income.valueList=[25000,50000,75000,sys.maxsize]
income.parent = []

exercise = Node("exercise",1)
exercise.valueList=['no','yes']
exercise.parent=[income]

smoke = Node("smoke",2)
smoke.valueList=['no','yes']
smoke.parent=[income]

bmi = Node("bmi",3)
bmi.valueList=['underweight','normal','overweight','obese']
bmi.parent=[income,exercise]

bp = Node("bp",4)
bp.valueList=['no','yes']
bp.parent=[income,exercise,smoke]

cholesterol = Node("cholesterol",5)
cholesterol.valueList=['no','yes']
cholesterol.parent=[income,exercise,smoke]

angina = Node("angina",6)
angina.valueList=['no','yes']
angina.parent=[bmi,bp,cholesterol]

attack = Node("attack",7)
attack.valueList=['no','yes']
attack.parent=[bmi,bp,cholesterol]

stroke = Node("stroke",8)
stroke.valueList=['no','yes']
stroke.parent=[bmi,bp,cholesterol]

diabetes = Node("diabetes",9)
diabetes.valueList = ['no','yes']
diabetes.parent=[bmi]

nodeList = [income,exercise,smoke,bmi,bp,cholesterol,angina,attack,stroke,diabetes]
dataList = []





""" READ THE DATAFILE """
with open(sys.argv[4]) as f:
    content = f.readlines()
for i in range(1,len(content)):
	# scan through each data record
	item = content[i].split()
	# categorize each data record into my standard CPT category
	formatted_item = []
	#check income
	for j in range(0,len(income.valueList)):
		if int(item[0]) <= int(income.valueList[j]):
			formatted_item.append(j)
			break
	#check exercise
	for j in range(0,len(exercise.valueList)):
		if item[1] == exercise.valueList[j]:
			formatted_item.append(j)

	#check smoke
	for j in range(0,len(smoke.valueList)):
		if item[2] == smoke.valueList[j]:
			formatted_item.append(j)

	#check bmi
	for j in range(0,len(bmi.valueList)):
		if item[3] == bmi.valueList[j]:
			formatted_item.append(j)
	#check bp
	for j in range(0,len(bp.valueList)):
		if item[4] == bp.valueList[j]:
			formatted_item.append(j)
	#check cholesterol
	for j in range(0,len(cholesterol.valueList)):
		if item[5] == cholesterol.valueList[j]:
			formatted_item.append(j) 
	#check angina
	for j in range(0,len(angina.valueList)):
		if item[6] == angina.valueList[j]:
			formatted_item.append(j)
	#check attack
	for j in range(0,len(attack.valueList)):
		if item[7] == angina.valueList[j]:
			formatted_item.append(j)
	#check stroke
	for j in range(0,len(stroke.valueList)):
		if item[8] == stroke.valueList[j]:
			formatted_item.append(j)
	#check diabetes
	for j in range(0,len(diabetes.valueList)):
		if item[9] == diabetes.valueList[j]:
			formatted_item.append(j)

	dataList.append(formatted_item)

#constructing CPT for each node on the fly
# CPT FORMAT: 
#income.CPT: [{"01":P1},{"02":P2},{"03":P3},{"04":P4}], there are four categories for feature income, left digit present the income.no, the right digit present the number of category the P falls into.
# for "diabete"
#smoke.CPT: [{"2000",P1},{"2001",P2},{"2002",P3},{"2003",P4}...], odd digit present for the no of feature, even digit present for the no of effects based on the feature.
# first two digits stands for the feature and its value for the current node we are computing for CPT
# the rest digits stands for the parents' combination for the current node we are computing for CPT
# {"2000":P1} stands for P(smoke = no/income<250000)=P1
createCPT(nodeList,dataList)


""" READ THE INPUT FILE """
with open(sys.argv[2]) as f2:
    query = f2.readlines()



""" SOLVE AND OUTPUT TO FILE """
text_file = open("riskFactor.out", "w")

for i in range(1,len(query)):
	qList = eval(query[i])
	#print qList
	queryItem = Query(i-1) # queries start from 0

	# print "************* prepossessing query %d ******"%i
	prepQuery(qList,queryItem,nodeList)
	
	res_and=[]
	res_alfa=[]

	try:
		res_and = AndProbability(nodeList,queryItem.fixDic,queryItem.andList,queryItem.emuList["0"],queryItem.fixDic,0,[])	
		res_alfa = AndProbability(nodeList,queryItem.fixDic,queryItem.alfaList,queryItem.emuList["1"],queryItem.conDic,0,[])
	except:
		print "error calculating this result "

	sum1 = 0.0
	for i in res_and:
		sum1 +=i

	sum2 = 0.0
	for i in res_alfa:
		sum2+=i
	
	queryItem.res = roundRes(sum1/sum2)
	print queryItem.res
	print>>text_file,queryItem.res
	














