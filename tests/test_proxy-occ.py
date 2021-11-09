import compas
from compas.datastructures import Mesh
from compas.geometry import Shape
from compas_cloud import Proxy
from compas_occ.interop.meshes import compas_mesh_to_occ_shell
from compas_occ.brep.datastructures import BRepShape
import time

# proxy = Proxy()
# print(proxy.check())
# test = proxy.function('compas_occ.interop.meshes.compas_mesh_to_occ_shell')


v1 = (0,0,0)
v2 = (0,1,0)
v3 = (1,1,0)

vertices = [v1,v2,v3]

mesh = Mesh.from_vertices_and_faces(vertices, [vertices[0], vertices[1],vertices[2]])

shell = compas_mesh_to_occ_shell(mesh)
shape = BRepShape(shell)



# pls = compas_mesh_to_occ_shell(mesh)
# pls = test(mesh)
print(shape)

# proxy.shutdown()




