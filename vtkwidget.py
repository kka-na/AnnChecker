
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PyQt5.QtWidgets import *


import colorsys
import numpy as np

class VTKWidget():
    def __init__(self):
        self.vtkWidget = QVTKRenderWindowInteractor()

    def init(self):
        self.ren = vtk.vtkRenderer()
        self.ren.SetBackground(0.0, 0.05, 0.13)
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.ren_init()

    def ren_init(self):
        self.ren.ResetCamera()
        self.camera = vtk.vtkCamera()
        self.camera.SetPosition(-50, 0, 50)
        self.camera.SetFocalPoint(0, 0, 0)
        self.camera.Roll(-120)
        self.camera.SetViewUp(1, 0, 0)
        self.ren.SetActiveCamera(self.camera)
        self.iren.Initialize()
        self.iren.Start()

    def set_point_cloud(self, points, boxes):
        # x,y,z
        cloud_actor = self.points2actor(points)
        bbox_actors = self.box2actor(boxes)
        self.ren.AddActor(cloud_actor)
        for bbox_actor in bbox_actors:
            self.ren.AddActor(bbox_actor)
        self.ren_init()

    def points2actor(self, xyz):
        points = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()
        vcolors = vtk.vtkUnsignedCharArray()

        vcolors.SetNumberOfComponents(3)
        vcolors.SetName("Colors")
        vcolors.SetNumberOfTuples(len(xyz))

        norm_intensities = self.intensity_normalize(xyz[:, 3])

        for i in range(0, len(xyz)):
            p = xyz[i][:3]
            intensity = norm_intensities[i]
            color = self.get_color_by_intensity(intensity)
            vcolors.SetTuple3(i, color[0], color[1], color[2])
            point_id = points.InsertNextPoint(p)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(point_id)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetVerts(vertices)
        polydata.GetPointData().SetScalars(vcolors)
        polydata.Modified()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(0.1)
        return actor

    def box2actor(self, boxes):
        griddatas = []
        for i in range(len(boxes)):
            corners = self.calc_corners(boxes[i])
            points = vtk.vtkPoints()
            hexahead = vtk.vtkHexahedron()
            vcolors = vtk.vtkUnsignedCharArray()

            vcolors.SetNumberOfComponents(3)
            vcolors.SetName("Colors")
            vcolors.SetNumberOfTuples(len(boxes))

            for i, c in enumerate(corners):
                point_id = points.InsertNextPoint(c[0], c[1], c[2])
                hexahead.GetPointIds().SetId(point_id, i)
            griddata = vtk.vtkUnstructuredGrid()
            griddata.SetPoints(points)
            griddata.InsertNextCell(
                hexahead.GetCellType(), hexahead.GetPointIds())
            griddatas.append(griddata)

        actors = []
        for i in range(len(griddatas)):
            mapper = vtk.vtkDataSetMapper()
            mapper.SetInputData(griddatas[i])
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.GetProperty().SetColor(
                self.get_color_by_cls(int(boxes[i]['cls'])))
            actor.GetProperty().SetOpacity(0.5)
            actors.append(actor)
        return actors

    def calc_corners(self, bbox):
        hx = bbox['lhw'][0]/2.0
        hy = bbox['lhw'][1]
        hz = bbox['lhw'][2]/2.0
        cx = [hx, hx, -hx, -hx, hx, hx, -hx, -hx]
        cy = [0, 0, 0, 0, -hy, -hy, -hy, -hy]
        cz = [hz, -hz, -hz, hz, hz, -hz, -hz, hz]
        corners = np.vstack([cx, cy, cz])
        rot = bbox['heading']
        R = np.array([[np.cos(rot), 0, np.sin(rot)],
                      [0, 1, 0],
                      [-np.sin(rot), 0, np.cos(rot)]])
        corners = np.dot(R, corners).T+np.array([bbox['xyz']])
        corners = np.array(corners[:, [2, 0, 1]])*np.array([[1, -1, -1]])
        return corners

    def intensity_normalize(self, intensities):
        max_intensity = 0
        for i in intensities:
            if i >= max_intensity:
                max_intensity = i
        norm_intensities = (np.array(intensities)/max_intensity)*240
        return norm_intensities

    def get_color_by_intensity(self, intensity):
        h = ((240-intensity)+60)/360.0
        (h, l, s) = (h, 0.5, 1.0)
        (r, g, b) = colorsys.hls_to_rgb(h, l, s)
        (r, g, b) = (int(r*255), int(g*255), int(b*255))
        return (r, g, b)

    def get_color_by_cls(self, cls):
        if cls % 5 == 0:
            (r, g, b) = (0.584, 0.501, 1.0)
        elif cls % 5 == 1:
            (r, g, b) = (0.498, 1.0, 0.917)
        elif cls % 5 == 2:
            (r, g, b) = (0.956, 0.498, 0.749)
        elif cls % 5 == 3:
            (r, g, b) = (1.0, 0.721, 0.423)
        else:
            (r, g, b) = (0.545, 0.913, 0.992)
        return (r, g, b)
