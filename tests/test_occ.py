# import os

# import compas
# from compas.datastructures import Mesh
# from compas_occ.interop.meshes import compas_mesh_to_occ_shell
# from compas_occ.brep.datastructures import BRepShape
# # from compas_occ.brep.booleans import boolean_union_shape_shape


# # HERE = os.path.dirname(__file__)
# # TEMP = compas._os.absjoin(HERE, '../temp')
# # FILE_1 = os.path.join(TEMP, 'object1.json')
# # FILE_2 = os.path.join(TEMP, 'object2.json')

# # mesh_1 = Mesh.from_json(FILE_1)
# # mesh_2 = Mesh.from_json(FILE_2)

# brep_1 = BRepShape(compas_mesh_to_occ_shell(mesh_1))
# brep_2 = BRepShape(compas_mesh_to_occ_shell(mesh_2))

# # shape = boolean_union_shape_shape(brep_1, brep_2, convert=False)
# test = brep_1.edges()

# for i in test:
#     print(i)
# print(test)

  
# from compas.geometry import Polyline, Frame

# from compas_occ.interop.shapes import Box, Sphere
# from compas_occ.brep.booleans import boolean_union_shape_shape, boolean_difference_shape_shape
# from compas_occ.geometry.surfaces import BSplineSurface
# from compas_occ.geometry.curves import BSplineCurve

# from compas_view2.app import App
# from compas_view2.objects import Object, BoxObject, SphereObject

# Object.register(Box, BoxObject)
# Object.register(Sphere, SphereObject)

# box = Box(Frame.worldXY(), 1, 1, 1)
# sphere1 = Sphere([0.5 * box.xsize, 0.5 * box.ysize, 0.5 * box.zsize], 0.5)
# sphere2 = Sphere([0, 0.5 * box.ysize, 0.25 * box.zsize], 0.5)
# shape1 = boolean_union_shape_shape(sphere1, sphere2, convert=False)

# print(shape1)
# shape2 = boolean_difference_shape_shape(shape1, box, convert=False)

# viewer = App()

# for face in shape2.faces():
#     surface = BSplineSurface.from_face(face)
#     viewer.add(surface.to_vizmesh(resolution=16), show_edges=True)

# for edge in shape2.edges():
#     curve = BSplineCurve.from_edge(edge)
#     if curve:
#         viewer.add(Polyline(curve.to_locus(resolution=16)), linecolor=(1, 0, 0), linewidth=5)

# viewer.run()


from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Display.SimpleGui import init_display

step_reader = STEPControl_Reader()

display, start_display, add_menu, add_function_to_menu = init_display()

# display.

print(step_reader)