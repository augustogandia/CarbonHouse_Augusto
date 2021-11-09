from compas.datastructures import Mesh
from compas.datastructures import Network
from compas.datastructures import mesh_unify_cycles

from compas.geometry._core import subtract_vectors
from compas.geometry._core import cross_vectors
from compas.geometry._core import dot_vectors

from compas.geometry import Line, Point, is_point_on_plane, intersection_segment_segment,distance_point_point, translate_points
from compas.geometry import Vector
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors
from compas.geometry import Translation

from compas.geometry import intersection_mesh_mesh
from compas.geometry import is_colinear_line_line

def is_point_in_triangle(point, triangle, tol = 0.00001):

    def is_on_same_side(p1, p2, segment):
        a, b = segment
        v = subtract_vectors(b, a)
        c1 = cross_vectors(v, subtract_vectors(p1, a))
        c2 = cross_vectors(v, subtract_vectors(p2, a))
        if dot_vectors(c1, c2) >= -tol:
            return True
        return False

    a, b, c = triangle

    if is_on_same_side(point, a, (b, c)) and \
       is_on_same_side(point, b, (a, c)) and \
       is_on_same_side(point, c, (a, b)):
        return True

    return False

def is_vertex_on_face_plane(mesh, fkey, vertex):
    plane = (mesh.face_centroid(fkey), mesh.face_normal(fkey, unitized=True))

    if is_point_on_plane(vertex, plane):
        return True
    
    return False

def is_vertex_on_face(mesh, fkey, vertex):
    f_verts = [mesh.vertex_coordinates(vkey, axes='xyz') for vkey in mesh.face_vertices(fkey)]
    
    if is_vertex_on_face_plane(mesh, fkey, vertex):
        if len(f_verts) == 4:
            triangle_1 = [f_verts[2], f_verts[3], f_verts[0]]
            triangle_2 = [f_verts[0], f_verts[1], f_verts[2]]
            x1_1 = is_point_in_triangle(vertex, triangle_1); x1_2 = is_point_in_triangle(vertex, triangle_2)
            if x1_1 or x1_2: 
                return True 

        elif len(f_verts) == 3:
            triangle = [f_verts[0], f_verts[1], f_verts[2]]
            x = is_point_in_triangle(vertex, triangle)
            if x: 
                return True 
    return False

def intersection_edge_face(mesh, edge_start, edge_end):
    line_1 = Line(edge_start, edge_end) 
    intersections = []
    for ekey in mesh.edges():
        line_2 = Line(Point(mesh.vertex[ekey[0]]['x'], mesh.vertex[ekey[0]]['y'], mesh.vertex[ekey[0]]['z']),
                      Point(mesh.vertex[ekey[1]]['x'], mesh.vertex[ekey[1]]['y'], mesh.vertex[ekey[1]]['z'])) 
        x1, x2 = intersection_segment_segment(line_1, line_2)
        if x1 != None or x2 != None: 
            if distance_point_point(x1, x2) <= 1E-5 and not distance_point_point(x1, edge_start) <= 1E-5:
                intersections.append((edge_start, (x1[0], x1[1], x1[2]) ))
    return intersections

def get_mesh_vertices_coordinates(mesh):
    coordinates=[]
    for vertex in mesh.vertices():
        coordinates.append(tuple(mesh.vertex_coordinates(vertex)))
    return coordinates  

def get_assembly_topology(meshes):
    topology = {}
    topology_network = Network()

    """
    #Set empty topology dictionary in the format {'1': [], '0': [], '2': []}
    for i, mesh in meshes.items():
        mesh.attributes['name'] = i
        topology.setdefault(mesh.attributes['name'], [])

    for i, mesh in enumerate(meshes.values()):
        rest = [m for m in meshes.values()] 
        rest.pop(i) 

    #Generate dictionary with the topology of the structure
    #E.g. {'1': [['0', ((-977.79714116360481, -4854.900851526756, 0.0), (-214.47130357217961, -4854.900851526756, 0.0))]], '0': [['1', ((-214.47130357217961, -4854.900851526756, 0.0), (-977.79714116360481, -4854.900851526756, 0.0))]]}
    #{surface name : [[connected to surface name, (shared vertex 1 coordinates, shared vertex 2 coordinates)]], surface name : [[connected to surface name, (shared vertex 1 coordinates, shared vertex 2 coordinates)]]}
    
        for ekey in mesh.face_halfedges(0):
            v1 = (mesh.vertex[ekey[0]]['x'], mesh.vertex[ekey[0]]['y'], mesh.vertex[ekey[0]]['z'])
            v2 = (mesh.vertex[ekey[1]]['x'], mesh.vertex[ekey[1]]['y'], mesh.vertex[ekey[1]]['z'])
            for mesh_i in rest: 
            # edge of face touches completely other face
                if is_vertex_on_face(mesh_i, 0, v1) and is_vertex_on_face(mesh_i, 0, v2):
                    if [mesh_i.attributes['name'], (v1, v2)] not in topology[mesh.attributes['name']]:
                        topology[mesh.attributes['name']].append([mesh_i.attributes['name'], (v1, v2)])
                        
            # first vertex of edge touches other face
                if is_vertex_on_face(mesh_i, 0, v1) and not is_vertex_on_face(mesh_i, 0, v2): 
                    intersections = intersection_edge_face(mesh_i, v1, v2)
                    for i in intersections:
                        if [mesh_i.attributes['name'],(i[0], i[1])] not in topology[mesh.attributes['name']]:
                            topology[mesh.attributes['name']].append([mesh_i.attributes['name'],(i[0], i[1])])

            # second vertex of edge touches other face
                if is_vertex_on_face(mesh_i, 0, v2) and not is_vertex_on_face(mesh_i, 0, v1):
                    intersections = intersection_edge_face(mesh_i, v2, v1)
                    for i in intersections:
                        if [mesh_i.attributes['name'],(i[0], i[1])] not in topology[mesh.attributes['name']]:
                            topology[mesh.attributes['name']].append([mesh_i.attributes['name'],(i[0], i[1])])

            # if both vertices don't touch other face
                if is_vertex_on_face(mesh_i, 0, v2) == False: 
                    if is_vertex_on_face(mesh_i, 0, v1) == False: 
                        intersections = [i[1] for i in intersection_edge_face(mesh_i, v2, v1)]
                        if len(intersections) == 2 and not distance_point_point(intersections[0], intersections[1]) <= 1E-5:    
                            if ([mesh_i.attributes['name'],(intersections[0], intersections[1])] not in topology[mesh.attributes['name']]):
                                topology[mesh.attributes['name']].append([mesh_i.attributes['name'],(intersections[0], intersections[1])])
                            elif [mesh.attributes['name'],(intersections[0], intersections[1])] not in topology[mesh_i.attributes['name']]:
                                topology[mesh_i.attributes['name']].append([mesh.attributes['name'],(intersections[0], intersections[1])])
    print topology

    for key, value in topology.items(): 
        for e in value:
            temp = [e[0] for e in topology[e[0]]]
            if key not in temp:          
                topology[e[0]].append([key, (value[0][1][0], value[0][1][1])])
    """
    

    #Create a Network data structure considering the topology the rhino surfaces
    #nodes will represent panels and edges connections
    """
    #Add a panel (node) per srf and its corresponding attributes to the Network
    for key, mesh in meshes.items():         
        topology_network.add_node(key)
        topology_network.node_attribute(key, "mesh", mesh)
        topology_network.node_attribute(key, "mesh_normal", mesh.normal())
        topology_network.node_attribute(key, "panel_width", 50)
    
    
    #Add a joint (edge) per srf connection (directed = only once) to the tolopology network (Should be replaced in the future)
    for node, nbrs in topology.items():
        #Iter neighbors 
        for nbr in nbrs:
            nbr_key = nbr[0]
            #If not reversed and add some attributes
            if (node, nbr_key) not in topology_network.edges() and (nbr_key, node) not in topology_network.edges():
                #Add edge
                topology_network.add_edge(node, nbr_key)

    #Set panel type attribute
    for key in topology_network.nodes():
        #Get panel mesh
        mesh = topology_network.node_attribute(key, "mesh")
        #Get neighbor panels
        nbrs = topology_network.neighbors(key)
        #Get vertices
        mesh_vertices_coordinates = get_mesh_vertices_coordinates(mesh)
        #Iter mesh vertices coordinates
        vertex=0
        for vertex_coordinates in mesh_vertices_coordinates:
            #Iter neighbors
            vertex_type=0
            extrusion_normals=[topology_network.node_attribute(key, "mesh_normal")]
            for nbr_key in nbrs:
                #Get mesh
                nbr_mesh = topology_network.node_attribute(nbr_key, "mesh")
                #Get neighbor vertices coordinates
                nbr_mesh_vertices_coordinates = get_mesh_vertices_coordinates(nbr_mesh)
                if vertex_coordinates in nbr_mesh_vertices_coordinates:
                    nbr_normal=topology_network.node_attribute(nbr_key, "mesh_normal")
                    extrusion_normals.append(nbr_normal)
                    vertex_type+=1

            mesh.vertex_attribute(vertex, "vertex_type", vertex_type)
            mesh.vertex_attribute(vertex, "neighbor_normals", extrusion_normals)
            vertex+=1

    #Calculate extrusion vector and store as joint attribute (edge)
    for keys in topology_network.edges():

        #get normal from both connected panels
        n1 = topology_network.node_attribute(keys[0], "mesh_normal")
        n2 = topology_network.node_attribute(keys[1], "mesh_normal")
        #calculate extrusion vector = n_p1 + n_p2
        e = add_vectors(n1, n2)
        topology_network.edge_attribute(keys, "extrusion_vector", e)

    return topology, topology_network
    """

def primitive_mesh_edge_order(meshes):
    return [(mesh.attributes['name'], mesh.face_halfedges(0)) for mesh in meshes]

#(Move to another file)
def extrude_panels(meshes, topology_network):
    for key in topology_network.nodes():
        #Get mesh
        mesh = topology_network.node_attribute(key, "mesh")
        #Get mesh vertices coordinates
        mesh_vertices_coordinates = get_mesh_vertices_coordinates(mesh)
        #Get vertices
        for vertex_key in range (0,4):
            vertex_type=mesh.vertex_attribute(vertex_key, "vertex_type")

            #If vertex type = 0 extrude along mesh normal
            if vertex_type == 0:
                #Get vertex coordinates
                mesh_vertex_coordinate = mesh_vertices_coordinates[vertex_key]
                #Calculate vertex extrusion
                vertex_v = Vector(mesh_vertex_coordinate[0], mesh_vertex_coordinate[1], mesh_vertex_coordinate[2])
                raw_normal = topology_network.node_attribute (key, "mesh_normal")
                normal_v = Vector(raw_normal[0], raw_normal[1], raw_normal[2])
                normal_v_scaled= normal_v * topology_network.node_attribute (key, "panel_width")          
                s_v = subtract_vectors(vertex_v, normal_v_scaled)
                mesh.add_vertex(x=s_v[0], y=s_v[1], z=s_v[2])           

            #if vertex type = 1 extrude along extrusion_vector
            elif vertex_type == 1:
                #Get vertex coordinates
                mesh_vertex_coordinate = mesh_vertices_coordinates[vertex_key]
                vertex_v = Vector(mesh_vertex_coordinate[0], mesh_vertex_coordinate[1], mesh_vertex_coordinate[2])
                #Calculate vertex extrusion
                extrusion_normals = mesh.vertex_attribute(vertex_key, "neighbor_normals")
                raw_e_n1=extrusion_normals[0]
                raw_e_n2=extrusion_normals[1]
                e_n1_v=Vector(raw_e_n1[0], raw_e_n1[1], raw_e_n1[2])
                e_n2_v=Vector(raw_e_n2[0], raw_e_n2[1], raw_e_n2[2]) 
                normal_v = e_n1_v+e_n2_v
                normal_scaled = normal_v * topology_network.node_attribute (key, "panel_width")
                s_v = subtract_vectors (vertex_v, normal_scaled)
                mesh.add_vertex(x=s_v[0], y=s_v[1], z=s_v[2])
                
            #if vertex type = 2 extrude along extrusion_vector + extrusion_vector
            elif vertex_type == 2:
                #Get vertex coordinates
                mesh_vertex_coordinate = mesh_vertices_coordinates[vertex_key]
                vertex_v = Vector(mesh_vertex_coordinate[0], mesh_vertex_coordinate[1], mesh_vertex_coordinate[2])
                #Calculate vertex extrusion
                extrusion_normals = mesh.vertex_attribute(vertex_key, "neighbor_normals")
                raw_e_n1=extrusion_normals[0]
                raw_e_n2=extrusion_normals[1]
                raw_e_n3=extrusion_normals[2]
                e_n1_v=Vector(raw_e_n1[0], raw_e_n1[1], raw_e_n1[2])
                e_n2_v=Vector(raw_e_n2[0], raw_e_n2[1], raw_e_n2[2])
                e_n3_v=Vector(raw_e_n3[0], raw_e_n3[1], raw_e_n3[2])
                normal_v = e_n1_v+e_n2_v+e_n3_v
                normal_scaled = normal_v * topology_network.node_attribute (key, "panel_width")
                s_v = subtract_vectors (vertex_v, normal_scaled)
                mesh.add_vertex(x=s_v[0], y=s_v[1], z=s_v[2])

        mesh.add_face([4,6,5,7])
        mesh.add_face([0,2,6,4])
        mesh.add_face([1,2,6,5])

def get_mesh_from_rhino(guids):
    #Create List with the vertices of each srf
    rhino_srfs = [rs.SurfacePoints(guid) for guid in guids]

    #(clean) rhino_srf = rs.SurfacePoints(guid)
    #Sort vertices according to Rhino's convention
    #   (normal up)            
    #      0---1                                 
    #      -   -                 
    #      -   -                 
    #      3---4                 
    #Use the list of vertices to create a list of meshes while correcting rhino vertex inconsistency 
    #(clean) mesh = Mesh.from_vertices_and_faces([rhino_srf[0],rhino_srf[1],rhino_srf[3],rhino_srf[2]],[[0,1,3,2]])
    #(clean) return mesh
    meshes = [Mesh.from_vertices_and_faces([rhino_srf[0],rhino_srf[1],rhino_srf[3],rhino_srf[2]],[[0,1,3,2]]) for rhino_srf in rhino_srfs]
    return meshes
                
# ==============================================================================
# Main
# ==============================================================================


if __name__ == "__main__":  

    import compas_rhino
    from compas_rhino.geometry import RhinoSurface
    from compas_rhino.artists import MeshArtist

    import rhinoscriptsyntax as rs
    
    guids = compas_rhino.select_surfaces(message='Select multiple surfaces')
    srfs =  get_mesh_from_rhino (guids)
    meshes = {str(i):mesh for i, mesh in enumerate(srfs)}
    
    #get topology
    get_assembly_topology (meshes)
    """
    
    
    

    guids = compas_rhino.select_surfaces(message='Select multiple surfaces.')
    surfs = [RhinoSurface.from_guid(guid) for guid in guids] 
    meshes = {str(i):mesh for i,mesh in enumerate([surf.to_compas(cleanup=False) for surf in surfs])}
    
    
    
    get_assembly_topology (meshes)
    #get topology
    #topology, topology_network = get_assembly_topology (meshes)
    """
    """
    #extrude panels
    extrude_panels(meshes, topology_network)
    
    #draw topology info in Rhino
    for key, mesh in meshes.items():
        artist = MeshArtist(mesh, layer="Panel_" + key) 
        artist.clear_layer()     
        artist.draw_vertexlabels()
        
        rs.CurrentLayer("Panel_" + key)
        rs.AddTextDot(mesh.attributes['name'],mesh.face_centroid(0))
    rs.CurrentLayer("Default")
    """
