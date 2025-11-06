import { delay, IMap, RGB } from "./common";
import { getNeighbors4 } from "./lib/boundaryUtils";
import { FacetBuilder } from "./lib/FacetBuilder";
import { Point } from "./structs/point";
import { BooleanArray2D, Uint32Array2D, Uint8Array2D } from "./structs/typedarrays";
import { FacetResult, Facet } from "./facetmanagement";
import { FacetReducer } from "./facetReducer";

export class FacetCreator {
    private static builder: FacetBuilder = new FacetBuilder();

    /**
     *  Constructs the facets with its border points for each area of pixels of the same color
     */
    public static async getFacets(width: number, height: number, imgColorIndices: Uint8Array2D, onUpdate: ((progress: number) => void) | null = null): Promise<FacetResult> {
        const result = new FacetResult();
        result.width = width;
        result.height = height;
        // setup visited mask
        const visited = new BooleanArray2D(result.width, result.height);
        // setup facet map & array
        result.facetMap = new Uint32Array2D(result.width, result.height);
        result.facets = [];
        // depth first traversal to find the different facets
        let count = 0;
        for (let j: number = 0; j < result.height; j++) {
            for (let i: number = 0; i < result.width; i++) {
                const colorIndex = imgColorIndices.get(i, j);
                if (!visited.get(i, j)) {
                    const facetIndex = result.facets.length;
                    // build a facet starting at point i,j using FacetBuilder
                    const facet = FacetCreator.builder.buildFacet(facetIndex, colorIndex, i, j, visited, imgColorIndices, result);
                    result.facets.push(facet);
                    if (count % 100 === 0) {
                        await delay(0);
                        if (onUpdate != null) {
                            onUpdate(count / (result.width * result.height));
                        }
                    }
                }
                count++;
            }
        }
        await delay(0);
        // fill in the neighbours of all facets by checking the neighbours of the border points
        for (const f of result.facets) {
            if (f != null) {
                FacetCreator.buildFacetNeighbour(f, result);
            }
        }
        if (onUpdate != null) {
            onUpdate(1);
        }
        return result;
    }

    /**
     *  Builds a facet at given x,y using depth first search to visit all pixels of the same color
     *  @deprecated Use FacetBuilder.buildFacet() instead. Kept for backward compatibility.
     */
    public static buildFacet(facetIndex: number, facetColorIndex: number, x: number, y: number, visited: BooleanArray2D, imgColorIndices: Uint8Array2D, facetResult: FacetResult) {
        return FacetCreator.builder.buildFacet(facetIndex, facetColorIndex, x, y, visited, imgColorIndices, facetResult);
    }

    /**
     * Check which neighbour facets the given facet has by checking the neighbour facets at each border point
     */
    public static buildFacetNeighbour(facet: Facet, facetResult: FacetResult) {
        facet.neighbourFacets = [];
        const uniqueFacets: IMap<boolean> = {}; // poor man's set
        for (const pt of facet.borderPoints) {
            // Get all 4-connected neighbors within bounds
            const neighbors = getNeighbors4(pt.x, pt.y, facetResult.width, facetResult.height);
            for (const neighbor of neighbors) {
                const neighborFacetId = facetResult.facetMap.get(neighbor.x, neighbor.y);
                if (neighborFacetId !== facet.id) {
                    uniqueFacets[neighborFacetId] = true;
                }
            }
        }
        for (const k of Object.keys(uniqueFacets)) {
            if (uniqueFacets.hasOwnProperty(k)) {
                facet.neighbourFacets.push(parseInt(k));
            }
        }
        // the neighbour array is updated so it's not dirty anymore
        facet.neighbourFacetsIsDirty = false;
    }
}
