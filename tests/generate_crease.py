from math import cos

from compas.geometry import Vector, distance_point_point 

def vertices_from_loop(loop):
    verts_loop = []

    for ekey in loop:
        u, v = ekey
        if u not in verts_loop:
            verts_loop.append(u)
        if v not in verts_loop:
            verts_loop.append(v)    

    return verts_loop

def add_crease_parallel_boundary_edge(mesh, edge, dist, attr_name, attr_value):
    n_vkey = mesh.vertex_neighbors(edge[0], ordered=True)

    #find existing edge from primitive edge ends
    for e in n_vkey:
        e_loop = mesh.edge_loop((edge[0], e))
        end = e_loop[-1][1]
        if len(e_loop) > 1 and end == edge[1]:
            edge = (edge[0], e)

    if mesh.is_edge_on_boundary(edge[0], edge[1]):
        if mesh.halfedge_face(edge[0], edge[1]) is None:
            edge = (edge[1], edge[0])

        e_loop = mesh.edge_loop((edge[0], edge[1]))
        verts_loop = vertices_from_loop(e_loop)
        next_i = 0
        new_verts = []

        for i,vkey in enumerate(verts_loop):
            nbrs = mesh.vertex_neighbors(vkey, ordered=True)

            if next_i < (len(verts_loop)-1):
                next_i = i + 1
            elif next_i == (len(verts_loop)-1):
                next_i = i-1

            pred_i = nbrs.index(verts_loop[next_i])

            if pred_i  < (len(nbrs)-1):
                succ_i = pred_i + 1
            elif pred_i == (len(nbrs)-1):
                succ_i = pred_i - 1

            m_vect = Vector.from_data(mesh.edge_vector(vkey, verts_loop[next_i]))
            e_vect = Vector.from_data(mesh.edge_vector(vkey, nbrs[succ_i]))

            ang = 1.5708 - m_vect.angle(e_vect)
            e_len = mesh.edge_length(vkey, nbrs[succ_i])
            new_vkey = mesh.split_edge(vkey, nbrs[succ_i],t=abs(dist/cos(ang))/e_len, allow_boundary=True)
            mesh.edge_attribute((vkey, new_vkey),attr_name, attr_value); mesh.edge_attribute((new_vkey, nbrs[succ_i]),attr_name ,attr_value)
            mesh.vertex_attribute(new_vkey, attr_name, value=attr_value)
            new_verts.append(new_vkey)

        for fkey in list(mesh.faces()):
            face_verts = mesh.face_vertices(fkey)
            f_verts = [vkey for vkey in face_verts if vkey in new_verts]

            if len(f_verts) > 0:
                new_faces = mesh.split_face(fkey,f_verts[0],f_verts[1])
                new_edge = mesh.face_adjacency_halfedge(new_faces[0], new_faces[1])
                mesh.edge_attribute(new_edge, attr_name, value=attr_value)
        
        return new_verts

    else:
        print("Edge not on boundary")

def add_creases(mesh, topology, distance, attr_name, attr_value):
    name = mesh.attributes['name'] 
    interfaces = topology[name]
    vertices = mesh.vertex

    for i in interfaces:
        edge = []
        v1 = i[1][0]; v2 = i[1][1]

        for vkey in vertices:
            if distance_point_point(v1, (vertices[vkey]['x'], vertices[vkey]['y'], vertices[vkey]['z'])) <= 1E-5: 
                edge.append(vkey)
            if distance_point_point(v2, (vertices[vkey]['x'], vertices[vkey]['y'], vertices[vkey]['z'])) <= 1E-5: 
                edge.append(vkey)
        
        if len(edge) == 2:
            add_crease_parallel_boundary_edge(mesh, (edge[0], edge[1]), distance, attr_name, attr_value)   

def primitive_mesh_edge_order(meshes):
    return {mesh.attributes['name']:mesh.face_halfedges(0) for mesh in meshes.values()}

def face_topology_matrix(mesh, attr_name):
    center_face = min(list(mesh.faces()))

    for fkey in mesh.faces():
        for vkey in mesh.face_vertices(fkey):
            if mesh.vertex_degree(vkey) == 2:
                starting_face = fkey
                break

    current_face = starting_face
    complete_bound_ring = False
    mesh.face_attribute(current_face, attr_name, 2)

    for i in range(len(list(mesh.faces()))):
        nbrs = mesh.face_neighbors(current_face) 
        flag = True
        for nbr in nbrs:
            
            if flag:
                nbr_surrounding_attributes = [mesh.face_attribute(fkey, attr_name) for fkey in mesh.face_neighbors(nbr) if mesh.face_attribute(fkey, attr_name)]
                #confirm nbr is on boundary
                if mesh.is_face_on_boundary(nbr) and not complete_bound_ring:

                    if len(nbr_surrounding_attributes) == 1 and mesh.face_attribute(current_face, attr_name) == 2 and not mesh.face_attribute(nbr, attr_name):
                        current_face = nbr
                        mesh.face_attribute(nbr, attr_name, 3)
                        flag = False

                    elif len(nbr_surrounding_attributes) == 1 and mesh.face_attribute(current_face, attr_name) == 3 and not mesh.face_attribute(nbr, attr_name):
                        current_face = nbr
                        mesh.face_attribute(nbr, attr_name, 2)
                        flag = False

                    elif len(nbr_surrounding_attributes) == 2 and not mesh.face_attribute(nbr, attr_name):
                        current_face = nbr
                        mesh.face_attribute(nbr, attr_name, 3)
                        complete_bound_ring = True
                        flag = False

                elif not mesh.face_attribute(center_face, attr_name) and complete_bound_ring:
                    mesh.face_attribute(center_face, attr_name, 2)
                    flag = False

                elif not mesh.is_face_on_boundary(nbr) and len(nbr_surrounding_attributes) >= 2 and not mesh.face_attribute(nbr, attr_name) and complete_bound_ring:
                    current_face = nbr
                    mesh.face_attribute(nbr, attr_name, 3)
                    flag = False

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

    print(topo)

    for mesh in meshes.values():
        add_creases(mesh, topo, 10, 'test', 2)
        add_creases(mesh, topo, 5, 'test', 3)

    for mesh in meshes.values():
        face_topology_matrix(mesh, 'topo')
    
    for key,mesh in meshes.items(): 
        face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
        artist = MeshArtist(mesh, layer="Panel_" + key)
        artist.clear_layer()
        artist.draw()
        artist.draw_vertexlabels()
        rs.CurrentLayer("Panel_" + key)
        for fkey in mesh.faces():
            rs.AddTextDot((mesh.face_attribute(fkey, 'topo'), fkey),mesh.face_centroid(fkey))

    rs.CurrentLayer("Default")


