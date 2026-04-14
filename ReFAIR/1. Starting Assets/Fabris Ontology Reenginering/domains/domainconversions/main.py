# Python program to read
# json file


import json

# Opening JSON file
f = open('domains.json')

# returns JSON object as
# a dictionary
data = json.load(f)
print(data)
# Iterating through the json
# list
index = 1
tmpList = []
while index <= 29:
	for i in data['Domains + task Series']:
			tasksSerie = "{} {}".format('Tasks Serie', index)
			print(tasksSerie)
			try:
				#print (i['Name'], i[tasksSerie])
				if i['Name'] <> 'N/A':
					tmpList.append({'domain': i['Name'], 'tasksSerie' : i[tasksSerie]})
			except KeyError:
				print('errore')
	index = index + 1

print(tmpList)
with open("domains-taskSeries.json", "w") as outfile:
    json.dump(tmpList, outfile)


# Closing file
f.close()
