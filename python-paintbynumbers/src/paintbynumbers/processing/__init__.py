"""Processing pipeline for paint-by-numbers generation."""

from paintbynumbers.processing.facetmanagement import (
    Facet,
    FacetResult,
    PathSegment,
    FacetBoundarySegment,
)
from paintbynumbers.processing.facetbuilder import FacetBuilder
from paintbynumbers.processing.colorreduction import ColorReducer, ColorMapResult
from paintbynumbers.processing.facetreduction import FacetReducer
from paintbynumbers.processing.facetbordertracer import FacetBorderTracer
from paintbynumbers.processing.facetbordersegmenter import FacetBorderSegmenter
from paintbynumbers.processing.facetlabelplacer import FacetLabelPlacer

__all__ = [
    'Facet',
    'FacetResult',
    'PathSegment',
    'FacetBoundarySegment',
    'FacetBuilder',
    'ColorReducer',
    'ColorMapResult',
    'FacetReducer',
    'FacetBorderTracer',
    'FacetBorderSegmenter',
    'FacetLabelPlacer',
]
