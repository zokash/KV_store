from functools import wraps
import time
from datetime import datetime
import inspect
import argparse

data = {}


'''  
#path = "dummy_key_val.txt"
with open("dummy_key_val.txt", 'r') as f:
    for line in f:
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
'''
def timed(func):
    if inspect.isgeneratorfunction(func) == True:
        @wraps(func)
        def gen_wrapper(*args, **kwargs):
            start_time = datetime.now()
            start = time.time()
            res = func(*args, **kwargs)
            status = "incomplete"
            try:
                
                for item in res:
                    yield item
                status = "successful!"
                
                

            except Exception as e:
                status = f"failed due to {e}!"
                raise
            finally:
                end = time.time()
                with open("logs.txt", 'a') as f:
                    f.write(f"{func.__name__} {status} Started at {start_time} and ran for {end-start}sec\n")
                
        return gen_wrapper
        
    
    else:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            start = time.time()
            try:
                res=func(*args, **kwargs)
                end = time.time()
                with open("logs.txt", 'a') as f:
                    f.write(f"{func.__name__} successful! Started at {start_time} and ran for {end-start}sec\n")
                return res
    
            except Exception as e:
                
                with open("logs.txt", 'a') as f:
                    f.write(f"{func.__name__} failed due to {type(e).__name__}! Started at {start_time} \n")
                    raise 

    return wrapper

@timed
def get(key):
    return (data.get(key))

@timed
def  set_val(key,value):
    data[key]=value

@timed
def delete_val(key):
    del data[key]

@timed
def write_back(f):
    for key, value in data.items():
        f.write(f"{key}={value}\n")
    


@timed
def list_all():
    for key,val in data.items():
        yield (key,val)

@timed
def print_all():
    for key, val in list_all():
        print(f"{key} : {val}")
        #raise KeyError
        
        
class FM_for_KV_store:
    def __init__(self,filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, self.mode)
        self.file.seek(0) #'a+' starts your read position at EOF, so __enter__'s loop reads nothing. this line is to correct that
        for line in self.file:
            key,value = line.split("=", 1)
            data[key.strip()] = value.strip()
        return self.file

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.file.seek(0)
        self.file.truncate()
        try:
            write_back(self.file)
        finally:
            self.file.close()

with FM_for_KV_store("dummy_key_val.txt", 'a+'):

    

    parser = argparse.ArgumentParser(description="A simple file-based key-value store")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # for: python kvstore.py set username kashzo
    set_parser = subparsers.add_parser("set")
    set_parser.add_argument("key")
    set_parser.add_argument("value")

    # for: python kvstore.py get username
    get_parser = subparsers.add_parser("get")
    get_parser.add_argument("key")

    # for: python kvstore.py delete username
    delete_parser = subparsers.add_parser("delete")
    delete_parser.add_argument("key")

    # for: python kvstore.py list
    list_parser = subparsers.add_parser("list")

    args = parser.parse_args()

    if args.command == "set":
        print(f"Setting {args.key} to {args.value}")
        set_val(args.key,args.value)
    elif args.command == "get":
        print(f"Getting {args.key}")
        print(get(args.key))
    elif args.command == "delete":
        print(f"Deleting {args.key}")
        delete_val(args.key)
    elif args.command == "list":
        print("Listing all keys")
        print_all()

    '''
    set_val("username", "kashish")
    print(get("username"))
    #delete_val("false_key")
   

    print_all()
    '''