from compas.geometry import distance_point_point, Vector, angle_vectors_signed, add_vectors, cross_vectors 
import compas_rhino
from compas_rhino.geometry import RhinoMesh
# from generate_crease import add_crease_parallel_boundary_edge, vertices_from_loop
from generate_crease import vertices_from_loop
from math import cos


def add_mp_creases(mesh, topology, attr_name, *args):
    name = mesh.attributes['name'] 
    interfaces = topology[name]

    for i in interfaces:
        v1 = i[1][0]; v2 = i[1][1]
        edge = get_ekey_from_coordinates(mesh, v1, v2)
        edge = find_existing_halfedge(mesh,edge)

#add attribute to split edge

        if edge:
            if mesh.edge_attribute(edge, attr_name) == 'mp_innie':
                add_crease_parallel_boundary_edge(mesh, (edge[0], edge[1]), args[0], attr_name, 'mp_innie')  
                add_crease_parallel_boundary_edge(mesh, (edge[0], edge[1]), args[1], attr_name, 'mp_innie')  
            elif mesh.edge_attribute(edge, attr_name) == 'mp_outie':
                add_crease_parallel_boundary_edge(mesh, (edge[0], edge[1]), args[2], attr_name, 'mp_outie')  


def find_existing_halfedge(mesh,edge):
    n_vkey = mesh.vertex_neighbors(edge[0], ordered=True)

    for e in n_vkey:
        e_loop = mesh.edge_loop((edge[0], e))
        end = e_loop[-1][1]
        if len(e_loop) > 1 and end == edge[1]:
            edge = (edge[0], e)

    return edge


def add_crease_parallel_boundary_edge(mesh, edge, dist, attr_name, attr_value):

    edge = find_existing_halfedge(mesh,edge)

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
            old_attr = mesh.edge_attribute([vkey, nbrs[succ_i]],attr_name)
            ang = 1.5708 - m_vect.angle(e_vect)
            e_len = mesh.edge_length(vkey, nbrs[succ_i])
            new_vkey = mesh.split_edge(vkey, nbrs[succ_i],t=abs(dist/cos(ang))/e_len, allow_boundary=True)
            mesh.edge_attribute([vkey, new_vkey],attr_name, old_attr); mesh.edge_attribute([new_vkey, nbrs[succ_i]],attr_name ,old_attr)

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

def get_ekey_from_coordinates(mesh, p1, p2):
    vertices = mesh.vertex
    edge = []

    for vkey in vertices:
        if distance_point_point(p1, (vertices[vkey]['x'], vertices[vkey]['y'], vertices[vkey]['z'])) <= 1E-5: 
            edge.append(vkey)
        if distance_point_point(p2, (vertices[vkey]['x'], vertices[vkey]['y'], vertices[vkey]['z'])) <= 1E-5: 
            edge.append(vkey)

    if len(edge) == 2:
        return edge
    
    else:
        return None

def get_panels_by_type(layer, attr):
    guids = compas_rhino.get_objects(layer=layer)
    surfs = [RhinoSurface.from_guid(guid) for guid in guids] 
    meshes = [surf.to_compas(cleanup=False) for surf in surfs]

    for mesh in meshes:
        mesh.attributes['type'] = str(attr)

    return meshes

def find_mesh_from_surface(meshes, guid):
    mesh_rhino = RhinoSurface.from_guid(guid).to_compas(cleanup=False)
    m_gkeys = [gkey for gkey in mesh_rhino.gkey_key()]

    for mesh in meshes.values():
        gkeys = [gkey for gkey in mesh.gkey_key()]

        if m_gkeys == gkeys:
            return mesh.attributes['name']

def assign_innies_outies(meshes, mkey, topology):
    mesh = meshes[mkey]

    for ekey in mesh.edges():

        if not mesh.edge_attribute(ekey, 'conn_type'):
            edge_vcoords = [mesh.vertex_coordinates(vkey, axes='xyz') for vkey in ekey]

            for p in topology[mkey]:
                nbr_ekey = get_ekey_from_coordinates(meshes[p[0]], p[1][0], p[1][1])

                if distance_point_point(edge_vcoords[0], p[1][0]) <= 1E-5 or distance_point_point(edge_vcoords[0], p[1][1]) <= 1E-5:  
                    if distance_point_point(edge_vcoords[1], p[1][0]) <= 1E-5 or distance_point_point(edge_vcoords[1], p[1][1]) <= 1E-5:

                        if not meshes[p[0]].edge_attribute(nbr_ekey, 'conn_type'):
                            mesh.edge_attribute(ekey, 'conn_type', 'mp_innie')
                        
                        elif meshes[p[0]].edge_attribute(nbr_ekey, 'conn_type'):
                            mesh.edge_attribute(ekey, 'conn_type', 'mp_outie')

def primitive_mesh_edge_order(meshes):
    return {mesh.attributes['name']:mesh.face_halfedges(0) for mesh in meshes.values()}

def face_topology_matrix(meshes, fkey, topology):
    mesh = meshes[fkey]
    interfaces = topology[mesh.attributes['name']]

    for i in interfaces:
        v1 = i[1][0]; v2 = i[1][1]
        prim_edge = get_ekey_from_coordinates(mesh, v1, v2)
        edge = find_existing_halfedge(mesh, prim_edge)

        edge_attr = mesh.edge_attribute([edge[0], edge[1]], 'conn_type')
        start = prim_edge[0]
        end = prim_edge[1]
        e_loop = mesh.edge_loop((edge[0], edge[1]))

        start_nbrs = mesh.vertex_neighbors(start, ordered=True)
        end_nbrs = mesh.vertex_neighbors(end, ordered=True)
        start_nbr_edge_attr = [mesh.edge_attribute([start, vkey], 'conn_type') for vkey in start_nbrs if vkey not in e_loop[0]][0]
        end_nbr_edge_attr = [mesh.edge_attribute([end, vkey], 'conn_type') for vkey in end_nbrs if vkey not in e_loop[-1]][0]

        if edge_attr == 'mp_innie' and start_nbr_edge_attr == 'mp_innie' and end_nbr_edge_attr == 'mp_innie':
            order = [2, 3, 2, 3, 2]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == 'mp_innie' and end_nbr_edge_attr == 'mp_outie':
            order = [2, 3, 2, 0]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == 'mp_outie' and end_nbr_edge_attr == 'mp_innie':
            order = [0, 2, 3, 2]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == 'mp_outie' and end_nbr_edge_attr == 'mp_outie':
            order = [0, 2, 0]
        
        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == None and end_nbr_edge_attr == 'mp_outie':
            order = [2, 0]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == 'mp_outie' and end_nbr_edge_attr == None:
            order = [0, 2]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == None and end_nbr_edge_attr == 'mp_innie':
            order = [2, 3, 2]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == 'mp_innie' and end_nbr_edge_attr == None:
            order = [2, 3, 2]

        elif edge_attr == 'mp_innie' and start_nbr_edge_attr == None and end_nbr_edge_attr == None:
            order = [2]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == 'mp_innie' and end_nbr_edge_attr == 'mp_innie':
            order = [0, 0, 4, 0, 0]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == 'mp_innie' and end_nbr_edge_attr == 'mp_outie':
            order = [0, 0, 4, 4]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == 'mp_outie' and end_nbr_edge_attr == 'mp_innie':
            order = [4, 4, 0, 0]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == 'mp_outie' and end_nbr_edge_attr == 'mp_outie':
            order = [4, 4, 4]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == None and end_nbr_edge_attr == 'mp_outie':
            order = [4, 4]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == 'mp_outie' and end_nbr_edge_attr == None:
            order = [4, 4]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == None and end_nbr_edge_attr == 'mp_innie':
            order = [4, 0, 0]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == 'mp_innie' and end_nbr_edge_attr == None:
            order = [0, 0, 4]

        elif edge_attr == 'mp_outie' and start_nbr_edge_attr == None and end_nbr_edge_attr == None:
            order = [4]

        else: 
            order = None

        if order:
            for i,ekey in enumerate(e_loop):
                if mesh.is_edge_on_boundary(ekey[0], ekey[1]):
                    if not mesh.halfedge_face(ekey[0], ekey[1]):
                        ekey = [ekey[1], ekey[0]]
                    fkey = mesh.halfedge_face(ekey[0], ekey[1])
                    mesh.face_attribute(fkey, 'topo', order[i])
                    if mesh.face_attribute(fkey, 'prim_edge'):
                        current_prim_edge_attr = mesh.face_attribute(fkey, 'prim_edge')[0]
                        mesh.face_attribute(fkey, 'prim_edge', [current_prim_edge_attr, (prim_edge[0], prim_edge[1])])
                    else:
                        mesh.face_attribute(fkey, 'prim_edge', [(prim_edge[0], prim_edge[1])])

    #add topologic attribute to the other faces

    mesh_centroid = mesh.centroid()
    smallest_dist_to_centroid = [0, 1E15]

    for fkey in mesh.faces():
        fkey_centroid = mesh.face_centroid(fkey)
        distance = distance_point_point(mesh_centroid, fkey_centroid)
        if distance < smallest_dist_to_centroid[1]:
                smallest_dist_to_centroid = [fkey, distance]

    for fkey in mesh.faces():
        if mesh.face_attribute(fkey, 'topo') == None and fkey != smallest_dist_to_centroid[0]:
            nbrs_face_topo_attr = []
            mesh.face_attribute(fkey, 'topo', 3)
            nbrs = mesh.face_neighborhood(fkey)

            for nbr in nbrs:
                if mesh.is_face_on_boundary(nbr) and mesh.face_attribute(nbr, 'prim_edge') != None and mesh.face_attribute(nbr, 'topo') != 0 :
                    nbr_attr = mesh.face_attribute(nbr, 'prim_edge')
                    nbrs_face_topo_attr.append((nbr_attr[0]))
            
            nbrs_face_topo_attr = [x for n, x in enumerate(nbrs_face_topo_attr) if x not in nbrs_face_topo_attr[:n]]
            mesh.face_attribute(fkey, 'prim_edge', nbrs_face_topo_attr)

    mesh.face_attribute(smallest_dist_to_centroid[0], 'topo', 2)
    # print(smallest, mesh.attributes['name'])

def move_faces_mp(meshes, fkey, topology):
    

        # prim_edge = get_ekey_from_coordinates(mesh, v1, v2)

        # edge_vector = Vector.from_start_end(v1, v2)

        # nbr_edge = get_ekey_from_coordinates(meshes[nbr_fkey], v1, v2)
        # mesh_normal = mesh.face_normal(center_face, unitized=True)

        # nbr_center_face = min(list(meshes[nbr_fkey].faces()))

        # mesh_normal = mesh.face_normal(center_face, unitized=True)
        # nbr_mesh_normal = meshes[nbr_fkey].face_normal(nbr_center_face, unitized=True)

        # mesh_centroid = mesh.centroid()
        # nbr_mesh_centroid = meshes[nbr_fkey].centroid()

        # front_mesh_point = [mesh_centroid[0] + mesh_normal[0],  mesh_centroid[1] + mesh_normal[1], mesh_centroid[2] + mesh_normal[2]]
        # front_nbr_mesh_point = [nbr_mesh_centroid[0] + nbr_mesh_normal[0],  nbr_mesh_centroid[1] + nbr_mesh_normal[1], nbr_mesh_centroid[2] + nbr_mesh_normal[2]]

        # back_mesh_point = [mesh_centroid[0],  mesh_centroid[1], mesh_centroid[2]]
        # back_nbr_mesh_point = [nbr_mesh_centroid[0],  nbr_mesh_centroid[1], nbr_mesh_centroid[2]]

        # distance_front = distance_point_point(front_mesh_point, front_nbr_mesh_point)
        # distance_back = distance_point_point(back_mesh_point, back_nbr_mesh_point)

        # if distance_front > distance_back:

        #     edge = find_existing_halfedge(mesh, prim_edge)

        #     test = Vector.from_data(mesh_normal).cross(edge_vector)

        #     new_test = [test[0] * 0.1, test[1] * 0.1, test[2] * 0.1]
        #     new_vertex_a = [v1[0] + new_test[0], v1[1] + new_test[1], v1[2] + new_test[2]]
        #     new_vertex_b = [v1[0] - new_test[0], v1[1] - new_test[1], v1[2] - new_test[2]]

        #     for i in range(len(mesh.face_halfedges(center_face))):
        #         if i not in prim_edge:
        #             ref_point = mesh.vertex_coordinates(i, axes='xyz')
        #             break

        #     if distance_point_point(ref_point, new_vertex_a) > distance_point_point(ref_point, new_vertex_b):
        #         mesh.add_vertex(x=new_vertex_b[0], y= new_vertex_b[1], z= new_vertex_b[2])
        #     elif distance_point_point(ref_point, new_vertex_a) < distance_point_point(ref_point, new_vertex_b):
        #         mesh.add_vertex(x=new_vertex_a[0], y= new_vertex_a[1], z= new_vertex_a[2])
        #     # start_coords = mesh.vertex_coordinates(edge[0], axes='xyz')
    pass

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":  

    
    from compas_rhino.geometry import RhinoSurface
    from compas_rhino.artists import MeshArtist

    from topology import get_assembly_topology

    import rhinoscriptsyntax as rs
    
    # walls = get_panels_by_type('wall', 'wall')
    # roofs = get_panels_by_type('roof', 'roof')
    # floors = get_panels_by_type('floor', 'floor')
    # meshes = walls + roofs + floors

    # meshes = {str(i):mesh for i,mesh in enumerate(floors + roofs + walls)}

    guids = compas_rhino.select_surfaces(message='Select multiple surfaces.')
    surfs = [RhinoSurface.from_guid(guid) for guid in guids] 
    meshes = {str(i):mesh for i,mesh in enumerate([surf.to_compas(cleanup=False) for surf in surfs])}

    layers = rs.LayerNames(sort=False)
    no_delete_layers = ['Default', 'wall', 'floor', 'roof']

    for layer in no_delete_layers:
        rs.LayerVisible(layer,True)

    for layer in layers:
        if layer not in no_delete_layers:
            rs.PurgeLayer(layer)

    topo = get_assembly_topology(meshes)

    # first = find_mesh_from_surface(meshes, compas_rhino.select_object(message="Select first panel"))
    # last = find_mesh_from_surface(meshes, compas_rhino.select_object(message="Select last panel"))

    # assign_innies_outies(meshes, first, topo)
    # assign_innies_outies(meshes, last, topo)

    for mkey in meshes:
        assign_innies_outies(meshes, mkey,topo)

    for mesh in meshes.values():
        add_mp_creases(mesh, topo, 'conn_type', 10, 5, 5)

    for fkey in meshes:
        face_topology_matrix(meshes, fkey, topo)

#artist
    for key,mesh in meshes.items(): 
        artist = MeshArtist(mesh, layer="Panel_" + key)
        artist.clear_layer()
        artist.draw()
        # artist.draw_vertexlabels()
        rs.CurrentLayer("Panel_" + key)
        for fkey in mesh.faces():
            if mesh.face_attribute(fkey, 'topo') != None:
                rs.AddTextDot((mesh.face_attribute(fkey, 'topo'), mesh.face_attribute(fkey, 'prim_edge')),mesh.face_centroid(fkey))
        # for ekey in mesh.edges():
        #     rs.AddTextDot(mesh.edge_attribute(ekey, 'conn_type'),mesh.edge_point(ekey[0], ekey[1], t=0.5))

    for layer in no_delete_layers:
        rs.LayerVisible(layer, False)
    
    rs.CurrentLayer("Default")
