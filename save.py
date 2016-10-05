import pandas as pd 
import datetime

now = datetime.datetime.now()
fileName = str(now)+".xlsx"

writer = pd.ExcelWriter(fileName, engine='xlsxwriter')



def Save(dataset):
	for dic in sorted(dataset):
		print("-------------",dic,"-----------------")
		labelArray = []
		dataArray = []
		sheetName = str(dic)
	
		for subdic in sorted(dataset[dic]):
			dataArray.append(dataset[dic][subdic])
			labelArray.append(subdic)
		
			print(subdic, dataset[dic][subdic])		
		print("-------------------------------------")
		df = pd.DataFrame({'Label':labelArray,
							'Value':dataArray})
		df.to_excel(writer, sheet_name=sheetName)
	writer.save()
	writer.close()