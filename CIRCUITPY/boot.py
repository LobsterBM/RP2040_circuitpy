import storage 

storage.remount("/", False)

with open("/tmp.txt","a") as fp:
    fp.write("hello world")
    fp.close()
    
