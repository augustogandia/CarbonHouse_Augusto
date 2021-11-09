from compas.datastructures import Mesh
from compas.datastructures import mesh_unify_cycles

def facefilter(face):
    success, w, h = face.GetSurfaceSize()
    if success:
        if w > 10 and h > 10:
            return True
    return False

if __name__ == "__main__":  

    import compas_rhino
    from compas_rhino.geometry import RhinoSurface
    from compas_rhino.artists import MeshArtist
    import rhinoscriptsyntax as rs

    guids = compas_rhino.select_surfaces(message='Select multiple surfaces.')
    surfs = [RhinoSurface.from_guid(guid) for guid in guids] 
    meshes = {str(i):mesh for i,mesh in enumerate([surf.to_compas(cleanup=False) for surf in surfs])}
    
    #draw topology info in Rhino
    for key, mesh in meshes.items():
        artist = MeshArtist(mesh, layer="Panel_" + key) 
        artist.clear_layer()     
        artist.draw_vertexlabels()
        
        rs.CurrentLayer("Panel_" + key)
        rs.AddTextDot(mesh.attributes['name'],mesh.face_centroid(0))
    rs.CurrentLayer("Default")

