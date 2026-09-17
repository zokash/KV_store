from functools import wraps
import time
from datetime import datetime
import inspect

data = {}
#path = "dummy_key_val.txt"
with open("dummy_key_val.txt", 'r') as f:
    for line in f:
        key, value = line.split("=", 1)
        data[key.strip()] = value.strip()
'''
def timed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        start = time.time()
        try:
            res=func(*args, **kwargs)
            end = time.time()
            with open("logs.txt", 'a') as f:
                f.write(f"{func.__name__} started at {start_time} and ran for {end-start}sec\n")
            return res

        except Exception as e:
            
            with open("logs.txt", 'a') as f:
                f.write(f"{func.__name__} started at {start_time} and failed due to {type(e).__name__}\n")
                raise 

    return wrapper
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
def write_back(path):
    with open(path, 'w') as f:
        for key,value in data.items():
        
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
        break
        

set_val("password", "sonusonu")
print(get("username"))
#delete_val("false_key")
write_back("dummy_key_val.txt")

print_all()