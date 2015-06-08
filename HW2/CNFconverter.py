import sys
import pprint

""" READ THE INPUT FILE """
with open(sys.argv[2]) as f:
    content = f.readlines()


""" FUNCTION DEFINATIONS """

def isValidCNF(mylist):
	# check the CNF is valid or not
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
				mylist[i]= sorted(mylist[i],reverse=True)
				check=isValidCNF(mylist[i])
			if check==False:
				return False

	if mylist[0] == "or":
		for i in range(1, len(mylist)):
			if mylist[i][0]=="or" or mylist[i][0]=="and":
				return False
			if isValidCNF(mylist[i])==False:
				return False

	return True





def checkDuplication(mylist):
	# remove duplication in the clause
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
	# take "implies", "iff", "not", "and", "or" operations on mylist
	if isValidCNF(mylist)==True :
		return mylist

	if mylist[0]=="implies":
		mylist = solve_Imply(mylist)
		mylist[1] = CNF_Converter(mylist[1])
		mylist[2] = CNF_Converter(mylist[2])

	elif mylist[0]=="iff":
		mylist = solve_iff(mylist)
		mylist[1] = CNF_Converter(mylist[1])
		mylist[2] = CNF_Converter(mylist[2])

	elif mylist[0]=="not":
		mylist = solve_neg(mylist)

	elif mylist[0]=="and":
	    mylist = solve_and(mylist)

	elif mylist[0]=="or" :
		mylist = solve_or(mylist)

	mylist = sorted(mylist,reverse=True)
	mylist = checkDuplication(mylist)

	return mylist



def solve_Imply(mylist):
	# A=>B ; ~A or B
	tempList=["or",["not",mylist[1]],mylist[2]]
	return tempList


def solve_iff(mylist):
	# A iff B : A=>B && B=>A : (~A or B) && (~B or A)
	tempList=[]
	tempList.append("and")
	left =["or",["not",mylist[1]],mylist[2]]
	right =["or",["not",mylist[2]],mylist[1]]
	tempList.append(left)
	tempList.append(right)

	return tempList

def solve_neg(mylist):	
	# dicuss not operation include (neg, and, or, implication, iff)
	tempList=[]
	
	if len(mylist[1])==1:
		return mylist

	if mylist[1][0]=="not":
		tempList = mylist[1][1]

	elif mylist[1][0]=="and":
		# ~(A & B & C) : ~A or ~B or ~C, wait maybe not only two operators
		tempList.append("or")
		for element in range(1,len(mylist[1])):
			tempList.append(["not",mylist[1][element]])

	elif mylist[1][0]=="or":
		# ~(A or B) : ~A & ~B:
		tempList.append("and")
		for element in range(1,len(mylist[1])):
			tempList.append(["not",mylist[1][element]])

	return tempList


def solve_or(mylist):
	# "or" operation starter
	if isValidCNF(mylist)==True:
		return mylist
	mylist = combine_or(mylist)# combine all the same "or" operators
	return mylist

def combine_or(mylist):
	# in "or" operation
	# combine all the same "or" operators into literals and "and" connected literals
	# for cases like A&B or C&D or E&F or K or G
	# res = K,G
	# res_ands = A&B, C&D, E&F
	res=[]
	res.append("or") # a set for literals connected directly by "or"
	res_Ands=[] # a set for "and" operators
	for i in range(1, len(mylist)):
		if mylist[i][0]=="not":
			subRes = CNF_Converter(mylist[i])# after conversion it could be "and" or anything else
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
		return res
	else:
		# start to distribute 
		res_Ands = distributeOnAndList(res_Ands)
		if res!=["or"]:# equals empty case
			res_Ands = distributeOrInAnd(res,res_Ands)
		return res_Ands

def distributeOrInAnd(orList, andList):
	# in "or" operation
	# given 1 "and" connected literals and a set of literals, convert to CNF
	# for example: andList = A&B, orList = C, D
	# operation would be conver A&B or C or D into CNF form => (C or D or A) & (C or D or B)
	tempList = [];
	tempList.append("and")
	for i in range(0,len(andList)):
		for j in range(1, len(andList[i])):			
			subList = []
			subList.append("or")
			subList.append(orList)
			subList.append(andList[i][j])
			tempList.append(subList)
	return tempList



def distributeOnAndList(andList):
	# in "or" operation
	# solve cases like: A&B or C&D  => (A or D) & (A or C) & (B or C) & (B or D)
	# result combines to one "and" connected clause
	tempList=[]
	length = len(andList)
	if length==1: # only 1 and clause
		return andList

	for i  in range(1, len(andList)):
		tempList=[]
		tempList.append("and")

		for j in range(1, len(andList[i-1])):
			for k in range(1, len(andList[i])):
				subList = ["or",andList[i-1][j],andList[i][k]]
				#subList = CNF_Converter(subList)
				subList = sorted(subList,reverse=True)
				subList = checkDuplication(subList)
				tempList.append(subList)

		andList[i]=tempList
	return tempList

def solve_and(mylist):
	# "and" operations starter
	if isValidCNF(mylist)==True:
		print " the and sentence is true"
		return mylist
	
	mylist = combine_and(mylist)
	return mylist

def combine_and(mylist):
	# in "and" operation
	# discuss cases when clauses in "and" is not a CNF clause
	# "and" sould be followed by "or" , "not" only
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


def dfs(mylist):
	operator=[]
	operator.append(mylist[0])
	res = []
	for i in range(1,len(mylist)):
		temp = dfs(mylist[i]) # operate on the children's level
		if len(temp)==1:
			res.append(temp[0])#only one literal,
		else:
			res.append(temp) 
	
	for i in res:
		operator.append(i) # append child to current operation

	res = CNF_Converter(operator) # operatate on this level
	res = sorted(res,reverse=True) 
	res = checkDuplication(res)
	return res




""" OUTPUT CNF SENTENCE TO FILE """

text_file = open("sentences_CNF.txt", "w")
for i in range(1,int(content[0])+1):
	mylist = eval(content[i])
	mylist = dfs(mylist)
	while isValidCNF(mylist)==False: # make the format valid
	 	mylist = CNF_Converter(mylist)
	if len(mylist)==1:
		mylist="'"+mylist+"'"
	print>>text_file,mylist
text_file.close()
	


