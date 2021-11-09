import compas






# ==============================================================================
# Main       
# ==============================================================================

if __name__ == "__main__":  

    import compas_rhino
    from compas_rhino.geometry import RhinoSurface
    from compas_rhino.artists import MeshArtist

    import rhinoscriptsyntax as rs
    from generate_crease import add_creases
    from topology import get_assembly_topology

    guids = compas_rhino.select_surfaces(message='Select multiple surfaces.')
    surfs = [RhinoSurface.from_guid(guid) for guid in guids] 
    meshes = [surf.to_compas(cleanup=False) for surf in surfs]

    for i,mesh in enumerate(meshes):
        mesh.attributes['name'] = str(i)

    # primitive_order = 
    topo = get_assembly_topology(meshes)
    for mesh in meshes:
        add_creases(mesh, topo, 10, 'type', 3)
        add_creases(mesh, topo, 5, 'type', 3)

    # for mesh in meshes:
    #     for ekey in mesh.edges():
    #         if mesh.is_edge_on_boundary(ekey[0], ekey[1]):
    #             mesh.vertex_attribute(new_vkey, attr_name, value=attr_value)

    #             mesh.edge_attribute(ekey, 'type', 2)
    #         # if not mesh.edge_attribute(ekey, 'type'):
    #         #     print(mesh.edge_attribute(ekey, 'type'))
                
        
        for fkey in mesh.faces():
            face_vertices = mesh.face_vertices(fkey)
            vertices_attributes = [mesh.vertex_attribute(vkey, 'type') for vkey in face_vertices]
            print(vertices_attributes)
            # for ekey in face_edges:
            #     print(mesh.edge_attribute(ekey, 'type'))



    for i,mesh in enumerate(meshes): 
        artist = MeshArtist(mesh, layer="Panel_" + str(i))
        artist.clear_layer()
        artist.draw()
        artist.draw_vertexlabels()
        rs.CurrentLayer("Panel_" + str(i))
        # rs.AddTextDot(mesh.attributes['name'],mesh.face_centroid(0))

    rs.CurrentLayer("Default")