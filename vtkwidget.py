
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from PyQt5.QtWidgets import *


import colorsys


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

        for i in range(0, len(xyz)):
            p = xyz[i][:3]
            intensity = xyz[i][3]
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
        actor.GetProperty().SetPointSize(0.01)
        return actor

    def box2actor(self, boxes):
        griddatas = []
        for i in range(len(boxes)):
            corners = self.calc_corners(boxes[i])
            points = vtk.vtkPoints()
            hexahead = vtk.vtkHexahedron()
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
            transform = vtk.vtkTransform()
            # transform.Translate(boxes[i]['xzy'][0],
            #                     boxes[i]['xzy'][1], boxes[i]['xzy'][2])
            # transform.RotateZ(boxes[i]['heading']*180/3.141592)
            # transform.Translate(-boxes[i]['xzy'][0],
            #                     -boxes[i]['xzy'][1], -boxes[i]['xzy'][2])
            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            actor.SetUserMatrix(transform.GetMatrix())
            actor.GetProperty().SetColor(
                self.get_color_by_cls(boxes[i]['cls']))
            actor.GetProperty().SetOpacity(0.5)
            actors.append(actor)
        return actors

    def calc_corners(self, bbox):
        corners = []
        hx = bbox['wlh'][0]/2.0
        hy = bbox['wlh'][1]/2.0
        hz = bbox['wlh'][2]/2.0
        cx = bbox['xzy'][0]
        cy = bbox['xzy'][1]
        cz = bbox['xzy'][2]
        corners.append((cx+hx, cy+hy, cz-hz))
        corners.append((cx+hx, cy-hy, cz-hz))
        corners.append((cx-hx, cy-hy, cz-hz))
        corners.append((cx-hx, cy+hy, cz-hz))
        corners.append((cx+hx, cy+hy, cz+hz))
        corners.append((cx+hx, cy-hy, cz+hz))
        corners.append((cx-hx, cy-hy, cz+hz))
        corners.append((cx-hx, cy+hy, cz+hz))
        return corners

    def get_color_by_intensity(self, intensity):
        (h, s, v) = ((180-(intensity))/179.0, 1.0, 1.0)
        (r, g, b) = colorsys.hsv_to_rgb(h, s, v)
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
        elif cls % 5 == 4:
            (r, g, b) = (0.545, 0.913, 0.992)
        return (int(r*255), int(g*255), int(b*255))
