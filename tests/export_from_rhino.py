import os

import compas
from compas.datastructures import Mesh
import compas_rhino
from compas_rhino.geometry import RhinoSurface

from compas_rhino.artists import MeshArtist


HERE = os.path.dirname(__file__)
TEMP = compas._os.absjoin(HERE, '../temp')
FILE = os.path.join(TEMP, 'object2.json')


def facefilter(face):
    return True

guid = compas_rhino.select_object('Select objet to export')
obj = RhinoSurface.from_guid(guid)

mesh = obj.to_compas(facefilter=facefilter, cleanup=False)


mesh.to_json(FILE)

