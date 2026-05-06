import json

# Beispiel Json Daten
example_data = {"Modules": [{
    "moduleName": "Module1",
    "moduleId": "TEST01X",
    "moduleEcts": 5
},{
    "moduleName": "Module2",
    "moduleId": "TEST02X",
    "moduleEcts": 10
}]}
print("example_data:")
print(json.dumps(example_data, indent=4))
filename = "testdata.json"
with open(filename, "w") as f:
    json.dump(example_data, f)
    print("wrote json to file")

# Wurde es richtig geschrieben?
with open(filename, "r") as f:
    filedata = json.load(f)
    if filedata == example_data:
        print("comparison succeeded")
    else:
        print("comparison failed")
