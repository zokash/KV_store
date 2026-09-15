data = {}
path = "dummy_key_val.txt"
with open(path, 'r') as f:
    for line in f:
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

def get(key):
    return data.get(key)

def  set(key,value):
    data[key]=value

def delete(key):
    del data[key]

def write_back(path):
    file = open(path, 'w')
    file.write(data)
    file.close()