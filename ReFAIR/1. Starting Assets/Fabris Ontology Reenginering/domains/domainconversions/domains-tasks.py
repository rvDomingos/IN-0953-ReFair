# Python program to read
# json file


import json

# Opening JSON file
f = open('taskSeries.json')
f1 = open('domains-taskSeries.json')

taskSeries = json.load(f)
domains = json.load(f1)
print(taskSeries)
print(domains)

tmpList = []
for taskSerie in taskSeries:
    for domain in domains:
        if taskSerie['Number'] == domain['tasksSerie']:
            for x in range(22):
                task = "{}{}".format('Task', (x+1))
                if taskSerie[task] != "":
                    tmpList.append({'domain': domain['domain'], 'task': taskSerie[task]})
# returns JSON object as
# a dictionary

print(tmpList)
with open("domains-tasks.json", "w") as outfile:
    json.dump(tmpList, outfile)


# Closing file
f.close()
f1.close()