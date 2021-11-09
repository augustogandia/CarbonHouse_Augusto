# import sys
# print(sys.version)

# import math

# from OCC.Core.gp import (gp_Pnt, gp_OX, gp_Vec, gp_Trsf, gp_DZ, gp_Ax2, gp_Ax3,
#                          gp_Pnt2d, gp_Dir2d, gp_Ax2d, gp_Pln)
# from OCC.Core.GC import GC_MakeArcOfCircle, GC_MakeSegment
# from OCC.Core.GCE2d import GCE2d_MakeSegment
# from OCC.Core.Geom import Geom_CylindricalSurface
# from OCC.Core.Geom2d import Geom2d_Ellipse, Geom2d_TrimmedCurve
# from OCC.Core.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire,
#                                      BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform)
# from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
# from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
# from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
# from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeThickSolid, BRepOffsetAPI_ThruSections
# from OCC.Core.BRepLib import breplib
# from OCC.Core.BRep import BRep_Builder
# from OCC.Core.GeomAbs import GeomAbs_Plane
# from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
# from OCC.Core.TopoDS import topods, TopoDS_Compound, TopoDS_Face
# from OCC.Core.TopExp import TopExp_Explorer
# from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
# from OCC.Core.TopTools import TopTools_ListOfShape

# from __future__ import print_function
# # import __future__

import compas
# from compas.datastructures import Mesh
# from compas.geometry import Shape
from compas_cloud import Proxy

height = 70
width = 50
thickness = 30

proxy = Proxy()
proxy = Proxy(background=True)

test = proxy.function('OCC.Core.gp.gp_Pnt')

neckLocation = test(0, 0, height)
# neckAxis = gp_DZ()
# neckAx2 = gp_Ax2(neckLocation, neckAxis)∞

# myNeckRadius = thickness / 4.0
# myNeckHeight = height / 10.0

# mkCylinder = BRepPrimAPI_MakeCylinder(neckAx2, myNeckRadius, myNeckHeight)

proxy.shutdown()

# print('test')

# # from compas_occ.interop.meshes import compas_mesh_to_occ_shell

