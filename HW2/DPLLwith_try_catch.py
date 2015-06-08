import sys
import pprint
import copy
from collections import defaultdict

""" READ THE INPUT FILE """
with open(sys.argv[2]) as f:
    content = f.readlines()


""" FUNCTION DEFINIATIONS """

def Init(CNFlist,flag):
	# a list of lists, each list contains only unit clause, examples include:
	# for (A or B) and (C or ~D) => [[A,B],[C,~D]]
	# for ~B => [[~B]], for A or B => [[A,B]]
	clauses=[]
	if CNFlist[0]=="and":
		for i in range(1,len(CNFlist)):
			clauses.append(Init(CNFlist[i],flag)[0])

	elif CNFlist[0]=="or":
		sub =[]
		flag = False
		for i in range(1,len(CNFlist)):
			if len(CNFlist[i])==2:
				sub.append(Init(CNFlist[i],flag)[0])
			else:
				if CNFlist[i] not in symbol:
					symbol.append(CNFlist[i])
				sub.append(CNFlist[i])
		clauses.append(sub)

	elif CNFlist[0]=="not":
		if CNFlist[1] not in symbol:
			symbol.append(CNFlist[1])
		s = "~"+CNFlist[1]+""
		if flag==True:
			clauses.append([s])
		else:
			clauses.append(s)

	else:
		if flag==True:# need to present as list if start with "and"
			clauses.append([CNFlist[0]])
		else:
			clauses.append(CNFlist[0])
		if CNFlist[0] not in symbol:
			symbol.append(CNFlist[0])
	return clauses



def removeClause(clauses,toRemove):
	# remove clause in the sentence
	# return True: alg is stopped, sentence is satisfiable
	# return False: keep going
	element =[]
	if toRemove[1]==True:
		element = toRemove[0]
	else:
		element = "~"+toRemove[0]

	i=0
	while i<len(clauses):
		if element in clauses[i]:
			clauses.remove(clauses[i])
		else:
			i=i+1	
	if len(clauses)==0:
		# sentence is empty, satisfiable
		return True
	return False;


def removeLiteral(c,toRemove):
	# remove reverse literal in the clauses
	# if return True, end the alg, return false
	# if return False, keep going
	
	literal = toRemove[0]
	if toRemove[1]==True:
		literal ="~"+toRemove[0]
	
	for i in c:
		if literal in i:
			i.remove(literal)
			if len(i)==0:
				#print "empty clauses exist, the sentence is false"
				return True
	return False




def findPureSymbol(clauses):
	dic = {}
	
	for i in range(0,len(clauses)):
		for j in clauses[i]:
			if j not in dic:
				if len(j)==2 and j[1] in dic:
					dic[j[1]]=False
				elif len(j)==1 and "~"+j[0] in dic:
					dic["~"+j[0]]=False
				else:
					dic[j]=True

	for i in dic:
		if dic[i]==True:
			if len(i)==2:
				return [i[1],False]#only exist ~Q, Q is false
			else:
				return [i,True]#only exist Q, Q is true
	return None



def findUnitClause(clauses):
	# find unit literal
	# remove clause contain the literal
	# remove literal in the clauses that contain the negation of the literal
	# add new assignment into module
	for i in clauses:
		if len(i)==1:
			if len(i)==1:
				return [i[0],True]
			else:
				return [i[1],False]
	return


def DPLL (clauses,symbol,model):
	result = False
	if len(clauses)==0:
		result = True
		return [result,model]
	
	pureSymbol=[]
	pureSymbol = findPureSymbol(clauses)

	if pureSymbol != None and len(pureSymbol)==2:
		# delete symbol pureSymbol[0] in the symbol list, model plus symbol and value
		# remove all the clauses containg the pure symbol
		# add new assignment to model
		# recursive call DPLL
		model.append(pureSymbol)
		symbol.remove(pureSymbol[0])
		result = removeClause(clauses,pureSymbol)
		if result == True:
			return [result,model]
		result = DPLL(clauses,symbol,model)
		if result ==True:
			return [result,model]


	unitClause=[]
	unitClause = findUnitClause(clauses)

	if unitClause!=None:
		# remove clause contain the literal
		# remove literal in the clauses that contain the negation of the literal
		# add new assignment into model
		# recursively call DPLL
		model.append(unitClause)
		symbol.remove(unitClause[0])

		result = removeClause(clauses,unitClause)
		if result==True:
			return [result,model]
		result = removeLiteral(clauses,unitClause)
		if result ==True:
			result = False
			return [result,model]
		result = DPLL(clauses,symbol,model)
		if result==True:
			return [result,model]
	
	# splitting part	
	if len(symbol)!=0:
		nextSymbol = symbol[0]
		symbol.remove(nextSymbol)
		tryTrue=False
		tryFalse=False


		if model==None:
			model=[]	
		#if result ==False and
		if result ==True:
			return [result,model]
		else:
			modelLeft = model[:]
			modelRight = model[:]

			clauseRight = copy.deepcopy(clauses)
			clauseLeft = copy.deepcopy(clauses)

			symbolLeft = symbol[:]
			symbolRight = symbol[:]

			
			modelLeft.append([nextSymbol,True])			
			result = removeClause(clauseLeft,[nextSymbol,True])
			if result ==True:
				return [result,modelLeft]
			
			result = removeLiteral(clauseLeft,[nextSymbol,True])			
			if result ==True:
				result = False
				return [result,model]
			
			tryTrue = DPLL(clauseLeft,symbolLeft,modelLeft)
			
			if tryTrue[0]!=False:
				return tryTrue
			else:
				
				modelRight.append([nextSymbol,False])
				result = removeClause(clauseRight,[nextSymbol,False])
				
				if result==True:
					return [result,modelRight]
				result = removeLiteral(clauseRight,[nextSymbol,False])
				
				if result ==True:
					result = False
					return [result,model]

				tryFalse = DPLL(clauseRight,symbolRight,modelRight)
				if tryFalse[0]!=False:				
					return tryFalse
				else:
					return [False,model]
				
	else:
		return [result,model]


def extendModel(model,symbol):
	# convert model into desired output form
	output = ["true"]
	for i in symbol:
		if i not in model:
			model.append([i,True])

	for i in model:
		if i[1]==True:
			output.append(i[0]+"=true")
		else:
			output.append(i[0]+"=false")

	return output



""" WRITE TO OUTPUT FILE TO SOLVE SAT PROBLEM"""

model=[]
symbol=[]
text_file = open("CNF_satisfiability.txt", "w")

for i in range(1,int(content[0])+1):
	mylist = eval(content[i])
	symbol=[]
	bkSymbol = copy.deepcopy(symbol)
	model = []
	result = []
	try:
		clauses=Init(mylist,True)
		result = DPLL(clauses,symbol,model)

	except:
		continue
	if result[0]!=False:
		print>>text_file,extendModel(result[1],bkSymbol)
	else:
		model = ["false"]
		print>>text_file,model
	
