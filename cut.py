 #  ***** BEGIN GPL LICENSE BLOCK *****
 #
 #  This program is free software: you can redistribute it and/or modify
 #  it under the terms of the GNU General Public License as published by
 #  the Free Software Foundation, either version 3 of the License, or
 #  (at your option) any later version.
 #
 #  This program is distributed in the hope that it will be useful,
 #  but WITHOUT ANY WARRANTY; without even the implied warranty of
 #  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #  GNU General Public License for more details.
 #
 #  You should have received a copy of the GNU General Public License
 #  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 #
 #  The Original Code is Copyright (C) 2013 by Max Voss
 #  All rights reserved.
 #
 #  Contact: maxivoss@hotmail.de
 #
 #  The Original Code is: all of this file.
 #
 #  Contributor(s): none yet.
 #
 #  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "Cut",
    "description": "Cuts a mesh with a plane.",
    "author": "Max Voss (max12345)",
    "version": (0.91, 0),
    "blender": (2, 71, 0),
    "location": "Mesh>Cut",
    "warning": "Working in theory and my test cases. Not in depth tested.",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.5/Py/"
                "Scripts/Mesh/Cut",
    "category": "Mesh"}

#ok so this is a script to perform planar cuts on mesh objects
#which means it will put a plane you define through the object,
#add vertices where needed and it will restructure faces
#so that at the end you have two separate meshes, one on each 
#side of the plane. You can choose to have the ends capped,

#(can I do this already?)
#or not, or to just introduce the new verts, without cutting,
#so you can do something with the edges

import bpy
import bmesh
from mathutils import Vector

def find_sides(mesh,point,direction):
    
   # polys                 = mesh.polygons
    edges=mesh.edges
    verts                 = mesh.vertices
    
    in_plane_points=[]
    on_side_a_total=[]
    on_side_b_total=[]
    cut_edges=[]
    for edge in edges:
    #for polygon in polys:
        # so we're really interested in faces that have vertices on
        # both sides of the plane
        # the rest we can almost ignore
        
        on_side_a=[]
        on_side_b=[]
        in_plane=[]
        new_edge=[]
        for index in edge.vertices:
            p=verts[index].co
            lp=p-point
            product=direction.dot(lp)
            product=round(product,4)
            if product>0:
                on_side_a.append(index)
            if product<0:
                on_side_b.append(index)
            if product==0:
                in_plane.append(index)
                in_plane_points.append(index)
            new_edge.append(index)
                
        #these are needed for selection purposes
        
        on_side_a_total+=on_side_a
        on_side_b_total+=on_side_b
        
        
        if (on_side_a and on_side_b) or (on_side_a and in_plane) or (on_side_b and in_plane):
            
            new_edge.sort()
            cut_edges.append(new_edge)
        
    return on_side_a_total ,on_side_b_total, in_plane_points,cut_edges

def determine_new_geometry(mesh,cut_edges,verts,point,direction)
    
    #these still matter. A lot. need to fix that.
    cut_plane_points=[]
    new_verts=[]
    vert_amount=len(verts)
    mapping={}
    face_creation=[]
    for edge in cut_edges:
        v1=verts[edge[0]]
        v2=verts[edge[1]]
        
        point_vec=v1.co-v2.co
        face_point=Vector(point)
        if point_vec.dot(direction)!=0:
            d=(face_point-v2.co).dot(direction)/point_vec.dot(direction)
        else:
            d=0
        
        new_vert=Vector(v2.co)+d*point_vec
        new_vert=tuple(new_vert)
        
        if new_vert not in new_verts:
            new_verts.append(new_vert)
            mapping.update({tuple(edge):new_vert})
            
        d=round(d,5)
        #special cases for overlap/remove
                
        if d==0:
            cut_plane_points.append(new_vert)
            #in_plane_points.append(vert_index)
        if d==1:
            cut_plane_points.append(new_vert)
            #in_plane_points.append(vert_index)
    
    print("creating the new faces")
    for p in mesh.polygons:
        
        face_cut_edges=[]
        cut=False
        for e in p.edge_keys:
            e=list(e)
            e.sort()
            
            if e in cut_edges:
                cut=True
                face_cut_edges.append(e)
        if face_cut_edges!=[]:
            #ok so I want to keep the old thingies and I want to replace 
            #the cut edges with new ones.
            face_creation.append((p,face_cut_edges))
        
    return new_verts,mapping,face_creation
  
def create_new_faces(bm,vertlist):
    for f in vertlist:
        bmface=[]
        for vert in f:
            bmface.append(bm.verts[vert])
        bmesh.ops.contextual_create(bm,geom=bmface)
  
def remove_cut_faces(mesh,bm,cut_edges):
    remove_faces=[]
    new_faces={}
    for face in bm.faces:
        for edge in face.edges:
            edge=[edge.verts[0].index,edge.verts[1].index]
            edge.sort()
            
            if edge in cut_edges:
                if face not in remove_faces:
                    remove_faces.append(face)
                if face not in new_faces:
                    new_faces.update({face:[edge]})
                else:
                    if edge not in new_faces[face]:
                        new_faces[face].append(edge)
                
    bmesh.ops.delete(bm,geom=remove_faces,context=5)
    bmesh.update_edit_mesh(mesh,destructive=True)
    return new_faces
    
def separate(bm):
    #this is for separating
    bpy.ops.mesh.select_all(action = "DESELECT")
    bm.verts[0].select   = True
    
    bpy.ops.mesh.select_linked()
    
    #ok, now separate into a new object/mesh
    
    #mode 3 creates too many verts?
    r=bpy.ops.mesh.separate(type="SELECTED")    

def make_new_faces(side_a,side_b,face_creation_inputs,mapping,new_verts,verts_length,mode_single):
    #select all from bmesh and combine to faces.
    #fuck.
    new_side_a_faces=[]
    new_side_b_faces=[]
    #face_creation_inputs
    #these contain the old faces and the edges that get replaced
    
    #the new verts get mapped to these edges in "mapping".
    new_vert_length=len(new_verts)
    while face_creation_inputs!=[]:
        fctp=face_creation_inputs.pop(0)
        new_a=[]
        new_b=[]
        
        for v in fctp[0].vertices:
            if v in side_a:
                new_a.append(v)
            if v in side_b:
                new_b.append(v)
        
        for edge in fctp[1]:
            new_vert=mapping[tuple(edge)]
            new_vert_index=new_verts.index(new_vert)
            new_vert_a=new_vert_index+verts_length
            #depending on the mode
            if mode_single:
                new_vert_b=new_vert_a
            else:
                new_vert_b=new_vert_a+new_vert_length
            for v in edge:
                #except this will not work, not always at least.
                #because I'll need to add new_verts more than once.
                if v in side_a:
                    if v not in new_a:
                        new_a.append(v)
                    if new_vert_a not in new_a:
                        new_a.append(new_vert_a)
                    #AND THE NEW VERT
                if v in side_b:
                    if v not in new_b:
                        new_b.append(v)
                    if new_vert_b not in new_b:
                        new_b.append(new_vert_b)
                    #AND THE NEW VERT
                    
        #and that should be it.
        new_side_a_faces.append(new_a)
        new_side_b_faces.append(new_b)
        
        #basically, I will add one new face on each side.
        #one will only have side a verts and new verts
        #and the other will only have side b verts and new verts
    
    return new_side_a_faces, new_side_b_faces
        
        
    
    
    a=1
    

def cut(blendmode,point=Vector((0,0,0)) , direction=Vector((0,0,1)),mode="1" ):
    """this is primary cutting function"""
    
    #modes
    #1 cut_cap_ends
    #2 cut_dont_cap
    #3 cut_only_new_faces
    
    print("cutting")
    #point     = Vector(self.plane_position)  #point in the plane
    #direction = Vector(self.direction)   #normal of the plane

    ob=bpy.context.active_object
    if ob is None:
        return {'FINISHED'}
    
    if mode in ["1","2"]:
        mode_single=False
    else:
        mode_single=True
        
    name=ob.name
    
    mesh                  = ob.data
    verts=mesh.vertices
    
    direction.normalize()
    
    #this basically defines the problem, which bits I can keep and 
    #where I need to do stuff.
    
    side_a,side_b,plane,cut_edges=find_sides(mesh,point,direction)
    
    #where are my new verts?
    
    new_verts, mapping,face_creation_inputs = determine_new_geometry(mesh,cut_edges,verts,point,direction)#,crosssection_polygons)
    #new faces
    
    side_a_faces,side_b_faces = make_new_faces(side_a,side_b,
                            face_creation_inputs,mapping,new_verts,len(verts),mode_single)
    #ok, first, I create all the new geometry, then I delete the old stuff
    
    setback=False
    
    if ob.mode=='OBJECT':
        setback                      = True
        bpy.ops.object.mode_set(mode = 'EDIT')
    
    me = mesh
    bm = bmesh.from_edit_mesh(me)
            
    #add new verts
    #print("new verts",new_verts)
    if mode_single:
        for vert in new_verts:
            bm.verts.new(vert)
    else:
        for vert in new_verts:
            bm.verts.new(vert)
        for vert in new_verts:
            bm.verts.new(vert)
        
    
        
    bm.verts.ensure_lookup_table()
    
    
    
    
    #add the new faces
    create_new_faces(bm,side_a_faces)
    create_new_faces(bm,side_b_faces)
    if not mode_single:
        r1=[range(len(verts),len(verts)+len(new_verts))]
        r2=[range(len(verts)+len(new_verts),len(verts)+len(new_verts)*2)]
        #print("r1,r2",r1,r2)
        create_new_faces(bm,r1)
        create_new_faces(bm,r2)
                    
    #remove old faces
    remove_cut_faces(mesh,bm,cut_edges)
    
    bmesh.update_edit_mesh(mesh,destructive=True)
    
    bpy.ops.mesh.select_all(action = "SELECT")
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.mesh.select_all(action = "DESELECT")
    #now for the splitting
    #deselect everything
    
    bm.verts.ensure_lookup_table()
    
    if mode!="3":
        separate(bm)
    #return {"FINISHED"}
    if setback:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    #if I don't have 2 objects at the end, this will fail...
    
    if mode!="3":
        #ok, provided my original was named, "x" i now have "x.001" as new object
        bpy.data.scenes[0].objects[name].select = True
        nob                                     = bpy.data.scenes[0].objects[name+".001"]
        
        nob.select                              = False
        bpy.context.scene.objects.active        = ob
        
        
        if blendmode:
            return {'FINISHED'}
        else:
            return ob,nob
    return {'FINISHED'}

class Cutter(bpy.types.Operator):
    """object cutting tool"""

    bl_idname = "object.cut"
    bl_label = "Cut"

    bl_options = {'REGISTER', 'UNDO'}
    
    direction = bpy.props.FloatVectorProperty(
        name="Normal Direction",
        description="The normal of the cutting plane",
        default=(1.0,0.0,0.0),
        subtype="XYZ")
        
    plane_position=bpy.props.FloatVectorProperty(
        name="Plane Position",
        description="The position of the cutting plane",
        default=(0.0,0.0,0.0),
        subtype="XYZ")
        
    @classmethod
    def poll(cls, context):
        obj                      = context.object
        return (obj and obj.type == 'MESH')
    
    def execute(self,context):
        print("\n\nexecuting\n\n")
        r         = cut(True,self.plane_position,self.direction)
        
        if r == {'FINISHED'}:
            return {'FINISHED'}
        

#utility things

def menu_func(self,context):
    self.layout.operator(Cutter.bl_idname)

#addon_keymaps=[]
    
def register():
    
    bpy.utils.register_class(Cutter)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)
    
    #wm = bpy.context.window_manager
    #km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
    #kmi = km.keymap_items.new(Cutter.bl_idname, 'K', 'PRESS', ctrl=True, shift=False)
    
    #addon_keymaps.append(km)

def unregister():
    bpy.utils.unregister_class(Cutter)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
 
if __name__ == "__main__":
    register()
    #c=Cutter()
    #Cutter.execute()
    #
    #execute()

    #cut(False,mode="3")
