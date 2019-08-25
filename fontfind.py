import os

print("\n\nnew\n\n")
path="/usr/share/fonts/"
r=os.walk(path)
print("starting")
for root,dirs,files in r:
    for file in files:
        try:
            if file[-3]==".fd":
                print(root,file)
            #bpy.data.fonts.load(root+"/"+file)
        except:
            
            pass
print("finished")
