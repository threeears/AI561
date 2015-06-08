import sys
import pprint

""" READ THE INPUT FILE """
with open(sys.argv[2]) as f:
    content = f.readlines()


def isValidCNF(mylist):
	check = True;
	if len(mylist)<=1:
		return True
	if mylist[0] == "implies" or mylist[0] == "iff":
		return False
	if mylist[0] == "not" and len(mylist[1])>=2:
		return False
	if mylist[0] == "and":
		for i in range(1,len(mylist)):
			if mylist[i][0]=="not":
				check=isValidCNF(mylist[i])
			elif mylist[i][0]=="implies" or mylist[i][0]=="iff" or mylist[i][0]=="and":
				check=False
			elif mylist[i][0]=="or":
				check=isValidCNF(mylist[i])
			if check==False:
				return False

	if mylist[0] == "or":
		for i in range(1, len(mylist)):
			if mylist[i][0]=="or" or mylist[i][0]=="and":
				return False
			if isValidCNF(mylist[i])==False:
				return False
	# print "it is a true for ..."
	# print mylist
	return True





def checkDuplication(mylist):
	tempList=[]
	if len(mylist)==1:
		return mylist[0]
	for i in mylist:
		if i not in tempList:
			tempList.append(i)
	if len(tempList)==2:
		if tempList[0]=="or" or tempList[0]=="and":
			tempList=tempList[1]
	return tempList


# CNF Converter
def CNF_Converter(mylist):
	if isValidCNF(mylist)==True :
		return mylist

	if mylist[0]=="implies":
		#do something here
		mylist = solve_Imply(mylist)
		mylist[1] = CNF_Converter(mylist[1])
		mylist[2] = CNF_Converter(mylist[2])

	elif mylist[0]=="iff":
		#do something here:
		mylist = solve_iff(mylist)
		mylist[1] = CNF_Converter(mylist[1])
		mylist[2] = CNF_Converter(mylist[2])

	elif mylist[0]=="not":
		#do something here
		mylist = solve_neg(mylist)

	elif mylist[0]=="and":
	    # do somethin
	    mylist = solve_and(mylist)
	    return mylist
	elif mylist[0]=="or" :
		# do something
		mylist = solve_or(mylist)
	
	#print "CNF_Converter result before cleaning"
	# pp = pprint.PrettyPrinter(indent=4)
	# pp.pprint(mylist)	
	mylist = sorted(mylist,reverse=True)
	mylist = checkDuplication(mylist)
	#print "CNF_Converter result after cleaning"
	# pp = pprint.PrettyPrinter(indent=4)
	# pp.pprint(mylist)	
	return mylist



def solve_Imply(mylist):
	# A=>B ; ~A V B
	tempList=["or",["not",mylist[1]],mylist[2]]

	# print "operation imply"
	# print tempList
	return tempList


def solve_iff(mylist):
	# A iff B : A=>B && B=>A : ~AVB && ~BVA
	tempList=[]
	tempList.append("and")
	left =["or",["not",mylist[1]],mylist[2]]
	right =["or",["not",mylist[2]],mylist[1]]
	tempList.append(left)
	tempList.append(right)
	# print "operation iff"
	# print tempList
	return tempList

def solve_neg(mylist):
	# if isValidCNF(mylist)==True:
	# 	return mylist
	# dicuss neg include (neg, and, or, implication, iff)
	# print "Before neg" # mylist include not operator
	# print mylist
	tempList=[]
	
	if len(mylist[1])==1:
		return mylist

	if mylist[1][0]=="not":
		tempList = mylist[1][1]

	elif mylist[1][0]=="and":
		#~ (A^B^C) : ~A V ~B, wait maybe not only two operators
		tempList.append("or")
		for element in range(1,len(mylist[1])):
			tempList.append(["not",mylist[1][element]])

	elif mylist[1][0]=="or":
		# ~(AVB) : ~A ^ ~B:
		tempList.append("and")
		for element in range(1,len(mylist[1])):
			tempList.append(["not",mylist[1][element]])
	# print "neg before valid.."
	# print tempList

	while isValidCNF(tempList)==False:
		tempList = CNF_Converter(tempList)
	# print "afater net"
	# print tempList
	return tempList


def solve_or(mylist):
	if isValidCNF(mylist)==True:
		return mylist
	mylist = combine_or(mylist)# combine all the same or operators
	while isValidCNF(mylist)==False:
			mylist = CNF_Converter(mylist)
	return mylist

def combine_or(mylist):
	# or, combine or A^B or C or D or C^H
	# print "before combining or"
	# print mylist
	res=[]
	res.append("or")
	res_Ands=[] # a set for and operators
	for i in range(1, len(mylist)):
		if mylist[i][0]=="not":
			subRes = CNF_Converter(mylist[i])# after conversion it could be and or anything else
			if subRes[0]=="and":
				res_Ands.append(subRes)
			else:
				res.append(subRes)
		elif mylist[i][0]=="or":
			for j in range(1, len(mylist[i])):
				res.append(mylist[i][j])
		elif mylist[i][0]=="and":
			res_Ands.append(mylist[i])
		else:
			res.append(mylist[i])

	if len(res_Ands)==0:
		# print "after combining or case 1"
		# print res
		return res
	else:
		# start to distribute 
		res_Ands = distributeOnAndList(res_Ands)
		if res!=["or"]:# equals empty case
			res_Ands = distributeOrInAnd(res,res_Ands)
		# print "after combining or case2"
		# print res_Ands
		return res_Ands

def distributeOrInAnd(orList, andList):
	# print "distribute or in and ......."
	# print "orList"
	# print orList
	# print "andList"
	# print andList
	# print "......................."
	# X V (D^E) : XVD ^ XVE
	tempList = [];
	tempList.append("and")
	for i in range(0,len(andList)):
		for j in range(1, len(andList[i])):			
			subList = []
			subList.append("or")
			subList.append(orList)
			subList.append(andList[i][j])
			tempList.append(subList)
	# print tempList
	while isValidCNF(tempList)==False:
		tempList = CNF_Converter(tempList)
	# print tempList
	return tempList


# def calculate2AndsOverOr(AL1, AL2):
# 	print AL1
# 	print AL2
# 	# the and lists are CNF, which means they could contain or clause
# 	subList=[]
# 	parentList=[]
# 	symbol=[]

# 	for i in range(1,len(AL1)):
# 		for j in range(1,len(AL2)):



# 	return parentList



def distributeOnAndList(andList):
	# print "distributr only the andlist"
	# print andList
	# A^B V C^D V E^F
	tempList=[]
	length = len(andList)
	if length==1: # only 1 and clause
		return andList

	for i  in range(1, len(andList)):
		tempList=[]
		tempList.append("and")

		for j in range(1, len(andList[i-1])):
			for k in range(1, len(andList[i])):
				
				# every time multiply two and clause over or
				# the way to calculate subList is to be changed
				#subList = calculate2AndsOverOr(andList[i-1][j],andList[i][k])
				subList = ["or",andList[i-1][j],andList[i][k]]

				while isValidCNF(subList)==False:
					subList = CNF_Converter(subList)

				sorted(subList,reverse=True)
				subList = checkDuplication(subList)
				tempList.append(subList)

		andList[i]=tempList
		while isValidCNF(tempList)==False:
			tempList = CNF_Converter(tempList)
	return tempList

def solve_and(mylist):
	if isValidCNF(mylist)==True:
		return mylist
	# print "mylist is not true for and operation"
	# print mylist
	mylist = combine_and(mylist)
	# print "after combining and.."
	# print mylist
	return mylist

def combine_and(mylist):
	# print "before combining and"
	# print mylist
	res=[]
	res.append("and")
	for i in range(1, len(mylist)):
		if mylist[i][0]=="not":
			res.append(CNF_Converter(mylist[i]))
		elif mylist[i][0]=="and":
			for j in range(1, len(mylist[i])):
				res.append(mylist[i][j])
		elif mylist[i][0]=="or":
			res.append(CNF_Converter(mylist[i]))
		else:
			res.append(mylist[i])
	return res
# conver all iff, implies into and or and not first


def dfs(mylist):
	operator=[]
	operator.append(mylist[0])
	res = []
	#print " start another level...."
	for i in range(1,len(mylist)):
		temp = dfs(mylist[i]) # operate on the children's level
		if len(temp)==1:
			res.append(temp[0])#only one element,
		else:
			res.append(temp)  # get CNF for every child
	
	for i in res:
		operator.append(i) # append child to current operation
	# print "operator is "
	# print operator
	res = CNF_Converter(operator) # operatate on this level
	# print "result ...."
	# print res
	while isValidCNF(res)==False: # make the format valid
		res = CNF_Converter(res)
	# pp = pprint.PrettyPrinter(indent=4)
	# pp.pprint(res)
	res = checkDuplication(res)

	return res

def removeSuperList(mylist):
	#print "start to remove super lists"

	tempList=[]
	if mylist[0]!="and":
		return mylist
	else:
		# compare pairwise,
		tempList.append(mylist[1]) 

		for i in range(2,len(mylist)):
			# CHECK IF current List contains base list or vice versa
			#print tempList
			size = len(tempList)
			k=0
			count = 0
			while count<size:
			# compare tempList[k], mylist[i]
				# if size>=2:
				# 	print tempList[k]
				# 	print mylist[i]
				# 	print count
				smaller=[]
				bigger=[]
				if len(tempList[k])<=len(mylist[i]):
					smaller = tempList[k]
					bigger = mylist[i]
				else:
					smaller=mylist[i]
					bigger=tempList[k]

				check = True
				for j in range(1,len(smaller)):
					if smaller[j] not in bigger:
						check = False
						break
				if check==True:# smaller is included by bigger
					if tempList[k]==bigger:
						tempList.remove(bigger)
						if smaller not in tempList:
							tempList.append(smaller)
						else:
							k=k+1
				else:
					if mylist[i] not in tempList:
						tempList.append(mylist[i])	
					k = k+1	
				count = count+1
				
	tempList[:0]=["and"]	
	return tempList						






text_file = open("sentences_CNF.txt", "w")
#print input file
for i in range(1,int(content[0])+1):
	mylist = eval(content[i])
	mylist = dfs(mylist)
	mylist = removeSuperList(mylist)
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(mylist)
	print>>text_file,mylist
text_file.close()
	

# still lack of deduplication

