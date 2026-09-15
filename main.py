data = {}
#path = "dummy_key_val.txt"
with open("dummy_key_val.txt", 'r') as f:
    for line in f:
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()

def get(key):
    print(data.get(key))

def  set(key,value):
    data[key]=value

def delete(key):
    del data[key]

def write_back(path):
    with open(path, 'w') as f:
        for key,value in data.items():
        
            f.write(f"{key}={value}\n")
    

set("username", "zoya")
get("username")

write_back("dummy_key_val.txt")