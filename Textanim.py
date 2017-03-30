import bpy
    
def string_to_ob(text="normally text goes here"):   
    cu = bpy.data.curves.new("name", 'FONT')
    ob = bpy.data.objects.new("name", cu)
    cu.body = text
    bpy.context.scene.objects.link(ob)
    bpy.context.scene.update()
    
    cu.align='CENTER'
    
    
    return ob

def make_animation(obj,linenumber=0,timedelay=0,timescaling=1):
    
    #,textplanenormal=mathutils.Vector((0,0,1))):
    #param?
    #anchor empties?
    
    #default plane is now
    #write -x to +x and
    #lines +y to -y 
    #i.e. top down european convention
    
    #x_base_offset=1
    y_base_offset=-1
    
    x_offset=0#linenumber*x_base_offset
    y_offset=linenumber*y_base_offset
    
    obj.animation_data_create()
    obj.animation_data.action = bpy.data.actions.new(name="AutomaticAction")
    
    xcurve=obj.animation_data.action.fcurves.new(data_path="location",index=0)
    xcurve.keyframe_points.add(2)
    xcurve.keyframe_points[0].co = (timedelay+0*timescaling,0+x_offset)
    xcurve.keyframe_points[0].interpolation='LINEAR'
    xcurve.keyframe_points[1].co = (timedelay+100*timescaling,1+x_offset)
    xcurve.keyframe_points[1].interpolation='LINEAR'
    
    ycurve=obj.animation_data.action.fcurves.new(data_path="location",index=1)
    ycurve.keyframe_points.add(2)
    ycurve.keyframe_points[0].co = (timedelay+0*timescaling,0+y_offset)
    ycurve.keyframe_points[0].interpolation='LINEAR'
    ycurve.keyframe_points[1].co = (timedelay+100*timescaling,1+y_offset)
    ycurve.keyframe_points[1].interpolation='LINEAR'
    
    zcurve=obj.animation_data.action.fcurves.new(data_path="location",index=2)
    zcurve.keyframe_points.add(2)
    zcurve.keyframe_points[0].co = (timedelay+0*timescaling,0)
    zcurve.keyframe_points[0].interpolation='LINEAR'
    zcurve.keyframe_points[1].co = (timedelay+100*timescaling,1)
    zcurve.keyframe_points[1].interpolation='LINEAR'
    
def copy_anim_from_proxy(obj,proxyname,linenumber=0,timedelay=0,timescaling=1):
    
    p=bpy.data.objects[proxyname]
    
    obj.animation_data_create()
    obj.animation_data.action = bpy.data.actions.new(name="AutomaticAction")
    
    
    for curve in p.animation_data.action.fcurves:
        
        #loops through all curves of the proxy object
        #adds an identical curve to the textobject action
        #and adds the same amount of keys
        
        dp=curve.data_path
        ai=curve.array_index
        
        text_curve=obj.animation_data.action.fcurves.new(curve.data_path,curve.array_index)
        keys=len(curve.keyframe_points)
        text_curve.keyframe_points.add(keys)
        
        k=0
        
        while k < keys:
            
            #this copies the keys with some modifications
            #like maybe delay, we'll see what else can be useful
            
            #obj.animation_data.action.fcurves.keyframe
            
            old_keys=curve.keyframe_points[k].co
            old_left=curve.keyframe_points[k].handle_left
            old_right=curve.keyframe_points[k].handle_right
            
            
            new_keys=(old_keys[0]+timedelay,old_keys[1])
            
            text_curve.keyframe_points[k].co=new_keys
            
            text_curve.keyframe_points[k].handle_left=(old_left[0]+timedelay,old_left[1])
            text_curve.keyframe_points[k].handle_right=(old_right[0]+timedelay,old_right[1])
            
            k+=1
            
        
def text_to_objects(textname):
    
    td=bpy.data.texts[textname]
    lines=td.lines
    
    line_i=0
    t=0
    for line in lines:
        SO=string_to_ob(line.body)
        #make_animation(SO,line_i,t)
        copy_anim_from_proxy(SO,"Proxy",line_i,t)
        line_i+=1
        t+=30
        
        
        
        
        #fcu_z = obj.animation_data.action.fcurves.new(data_path="location", index=2)
        #fcu_z.keyframe_points.add(2)
        #fcu_z.keyframe_points[0].co = 10.0, 0.0
        #fcu_z.keyframe_points[1].co = 20.0, 1.0
        
        #print(line.body)
        #SO.location[1]+=y
        #y+=-1
        
if __name__=="__main__":
    text_to_objects("Exampletext.txt")
