




# ==============================================================================
# Main       
# ==============================================================================


if __name__ == "__main__":  

    import compas
    from compas_cloud import Proxy

    import compas_rhino
    from compas_rhino.geometry import RhinoSurface
    from compas_rhino.artists import MeshArtist

    from topology import get_assembly_topology
    import rhinoscriptsyntax as rs

    guids = compas_rhino.select_surfaces(message='Select multiple surfaces.')
    surfs = [RhinoSurface.from_guid(guid) for guid in guids] 

    meshes = {str(i):mesh for i,mesh in enumerate([surf.to_compas(cleanup=False) for surf in surfs])}

    topo = get_assembly_topology(meshes)

    for e in meshes:
        mesh = meshes[e]
        add_creases(mesh, topo, 10, 'test', 2)
        add_creases(mesh, topo, 5, 'test', 3)

    for e in meshes:
        mesh = meshes[e]
        face_topology_matrix(mesh, 'topo')
    
    for i,e in enumerate(meshes): 
        mesh = meshes[e]
        face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
        artist = MeshArtist(mesh, layer="Panel_" + str(i))
        artist.clear_layer()
        artist.draw()
        artist.draw_vertexlabels()
        rs.CurrentLayer("Panel_" + str(i))
        for fkey in mesh.faces():
            rs.AddTextDot((mesh.face_attribute(fkey, 'topo'), fkey),mesh.face_centroid(fkey))

    rs.CurrentLayer("Default")
