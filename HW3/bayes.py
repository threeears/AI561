import sys
import pprint

class Disease:
	effectList=[] #effects of a certain disease
	CPTT = [] #P(effect/cause)
	CPTF = [] #P(effect/~cause)
	def __init__(self, name,prior):
		self.name = name
		self.prior = float(prior)
		
class Patient:
	def __init__(self, number):
		self.number = number
		self.finding =[] #synptoms of the patient


def AndProbability(patient,disease, finding):
	# calculate the np-th patient the joint-probability of nd-th disease, all start from zero
	result = 1.0
	for i in range(0, len(finding)):
		if finding[i]=='T':
			result = result * disease.CPTT[i]
		elif finding[i]=='F':
			result = result * (1 - disease.CPTT[i])
		else:
			continue
	result = result * disease.prior
	return result

def cal_Alfa(patient,disease,finding,posResult):
	# calculate alfa, which is P(effect1, effect2, effect3...)
	result = 1.0
	for i in range(0, len(finding)):
		if finding[i]=='T':
			result = result * disease.CPTF[i]
		elif finding[i]=='F':
			result = result * (1 - disease.CPTF[i])
		else:
			continue
	result = result * (1 - disease.prior)
	return result + posResult

def roundRes (res):
	# round the possibility into 4 digits decimal 
	res = str(round(res,4))
	if 6-len(res)!=0:
		for i in range(0,6-len(res)):
			res = res+'0'
	return res

def search_Unknown(patient,disease,finding,MinMax,start):
	# solution for Q2, for each unknown finding/synptom, try both T and F
	count = 0
	for i in range(0,len(finding)):
		if finding[i]!='U':
			count = count + 1
		else: 
			break

	if count == len(finding):
		# no unknown effects, only one possible result
		pos = AndProbability(patient,disease,finding)
		a = cal_Alfa(patient,disease,finding,pos)
		#print "min %s, max %s before" %(MinMax[0], MinMax[1])
		res = pos/a
		if res > MinMax[1]:
			# maxValue
			MinMax[1] = res
		if res < MinMax[0]:
			# miniValue
			MinMax[0] = res
		#print "min %s, max %s after " %(MinMax[0], MinMax[1])
		return MinMax

	
	for i in range(start,len(finding)):
		if finding[i]=='U':
			finding[i]='T'
			res1 = search_Unknown(patient,disease,finding,MinMax,i+1)
			finding[i]='F'
			res2 = search_Unknown(patient,disease,finding,MinMax,i+1)
			finding[i]='U'
			MinMax[0] = min(res1[0],res2[0])
			MinMax[1] = max(res2[0],res2[1])
	return MinMax

def next_Step(patient,disease,finding,dic,posDiff,negDiff,cur):
	# find the next unknown effect to test on, which makes dramatic change in possibility
	# solution for Q3
	for i  in range(0,len(finding)):
		if finding[i]=='U':
			finding[i]='T'
			pos = AndProbability(patient,disease,finding)
			a = cal_Alfa(patient,disease,finding,pos)
			res = pos/a
			diff = res - cur
			#print "unknown effect is %s,if it is True, possibility would be %f, diff would be %f" %(disease.effectList[i],res,diff)
			if diff > 0 and diff > posDiff:
				posDiff = diff
				dic["increase"] = [disease.effectList[i],'T']#,res]
			if diff < 0 and diff < negDiff:
				negDiff = diff
				dic["decrease"] = [disease.effectList[i],'T']#,res]

			finding[i] = 'F'
			pos = AndProbability(patient,disease,finding)
			a = cal_Alfa(patient,disease,finding,pos)
			res = pos/a
			diff = res - cur
			#print "unknown effect is %s,if it is False, possibility would be %f,diff would be %f" %(disease.effectList[i],res,diff)
			if diff > 0 and diff > posDiff:
				posDiff = diff
				dic["increase"] = [disease.effectList[i],'F']#,res]
			if diff < 0 and diff < negDiff:
				negDiff = diff
				dic["decrease"] = [disease.effectList[i],'F']#,res]

			finding[i] = 'U'
			
	if "increase" not in dic:
		dic["increase"]=['none','N']
	if "decrease" not in dic:
		dic["decrease"]=['none','N']
	
	#print dic
	return dic


""" READ THE INPUT FILE """
with open(sys.argv[2]) as f:
    content = f.readlines()
line = content[0].split()
NumDisease = int(line[0])
NumPatient = int(line[1])
disList = []
patList = []
# read diseases
i=1
while i<4*NumDisease+1:
	genInfo = content[i].split()
	disease = Disease(genInfo[0],genInfo[2])
	effectInfo = eval(content[i+1])
	CPT_T  = eval(content[i+2])
	CPT_F = eval(content[i+3])
	disease.effectList = effectInfo
	disease.CPTT = CPT_T
	disease.CPTF = CPT_F
	disList.append(disease)
	i = i+4
# read patients
k=0
base = i
while i < NumDisease*NumPatient+base:
	patient = Patient(k)
	for j in range(0,NumDisease):
		find = eval(content[i+j])
		patient.finding.append(find)

	patList.append(patient)	
	i = i+NumDisease
	k = k + 1


""" SOLVE AND OUTPUT FILE """

outputName = sys.argv[2].split('/')
outputName = outputName[len(outputName)-1][0:-4]+"_inference.txt"
text_file = open(outputName, "w")

for i in range(0,len(patList)):
	# iterate through all the patient
	print>>text_file, "Patient-%d:" % (i+1)
	Q1 = {}
	Q2 = {}
	Q3 = {}
	for j in range(0, len(disList)):
		#iterate through all the diseases for each patient
		patient = patList[i]
		disease = disList[j]
		finding = patient.finding[j]
		try:
			# Solve for Q1
			pos = AndProbability(patient,disease,finding)
			a = cal_Alfa(patient,disease,finding,pos)
			res = roundRes(pos/a)
			Q1[disease.name] = res
			# Solve for Q2
			Q2result = search_Unknown(patient,disease,finding,[1,0],0) 
			Q2min = roundRes(Q2result[0])
			Q2max = roundRes(Q2result[1])
			Q2[disease.name] = [Q2min,Q2max]
			# Solve for Q3
			Q3result = next_Step(patient,disease,finding,{},0,0,pos/a)
			Q3[disease.name] = [Q3result["increase"][0],Q3result["increase"][1],Q3result["decrease"][0],Q3result["decrease"][1]]
		except:
			print "error calculating this result"
	print>>text_file,Q1
	print>>text_file,Q2
	print>>text_file,Q3
text_file.close()

