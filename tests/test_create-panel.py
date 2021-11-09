import compas
import compas_rhino
from compas_rhino.geometry import RhinoSurface
from compas.datastructures import Mesh
from compas_rhino.artists import MeshArtist


def facefilter(face):
    return True

#Generate mesh from surface
guid = compas_rhino.select_surface("Select Surface")
surf = RhinoSurface.from_guid(guid)
mesh = surf.to_compas(facefilter=facefilter, cleanup=False)

fkey = [f for f in mesh.faces()][0]
print([v for v in mesh.face_vertices(fkey)])
# mesh.flip_cycles()
fverts = [v for v in mesh.face_vertices(fkey)] 

#Offest face according to panel thickness

mesh_off = compas.datastructures.mesh_offset(mesh, distance=-3.0)

#Generate closed mesh indluding offseted face

fkey = [f for f in mesh_off.faces()][0]
off_verts = mesh_off.face_coordinates(fkey, axes='xyz')

new_verts = []

for i, v in enumerate(fverts):
    mesh.add_vertex(key=v + len(fverts), x=off_verts[i][0], y=off_verts[i][1], z=off_verts[i][2])
    new_verts.append(v + len(fverts))


new_verts.reverse()
fverts.reverse()
mesh.add_face(new_verts)
for i in range(len(fverts)):
    mesh.add_face([new_verts[i],new_verts[i-1],fverts[i-1], fverts[i] ])

mesh.compas_quadmesh_to_occ_shell()

artist = MeshArtist(mesh,layer="Blocks")
artist.clear_layer()
artist.draw_mesh()


