class Rectangle:

    def __init__(self, width, height):
        self.width = width
        self.height = height
 
    def get_area(self):
        return self.width * self.height
 
    def set_width(self, width):
        self.width = width
 
    def set_height(self, height):
        self.height = height

import pytest
from django.test import RequestFactory
from plottable.rectangle import Rectangle
from plottable.settings import SPLOT_ANNOTATION_COLOR
from plottable.settings import SPLOT_ANNOTATION_STYLE
from plottable.settings import SPLOT_ANNOTATION_WIDTH
from plottable.utils import get_splot_config


class TestSplotAnnotation:

    @pytest.mark.django_db
    @pytest.mark.parametrize("width", [10, 15])
    @pytest.mark.parametrize("height", [10, 15])
    @pytest.mark.parametrize("color", ["red", "green", "blue"])
    @pytest.mark.parametrize("style", ["solid", "dashed", "dot"])
    @pytest.mark.parametrize("width", [1, 2, 3, 4, 5])
    @pytest.mark.parametrize("annotator", ["circle", "square"])
    def test_splot_annotation(self, width, height, color, style, width_splot, annotator):
        # create the rectangle
        rectangle = Rectangle(width, height)

        # create the annotation
        annotation = SPLOT_ANNOTATION_STYLE.lookup(style) \
            .create(rectangle, {
                                    "color": color,
                                       "width": width_splot,
                                       "annotator": annotator,
                                                                                                                                                                                              ])
        # create the splot
        splot = get_splot_config(rectangle, width_splot, annotator)

        # add the annotation to the splot
        splot.add_annotation(annotation)

        # add the rectangle to the splot
        splot.add_object(rectangle)

        # create a request
        req = RequestFactory()
        res = req.get(f"/splot/{splot.id}/annotate")

        # check the response
        assert res.status_code == 200

    @pytest.mark.django_db
    @pytest.mark.parametrize("width", [10, 15])
    @pytest.mark.parametrize("height", [10, 15])
    @pytest.mark.parametrize("color", ["red", "green", "blue"])
    @pytest.mark.parametrize("style", ["solid", "dashed", "dot"])
    @pytest.mark.