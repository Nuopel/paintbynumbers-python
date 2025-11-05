import { RGB } from "./common";
import { CLUSTERING_DEFAULTS, FACET_THRESHOLDS, IMAGE_CONSTANTS, SEGMENTATION_CONSTANTS } from "./lib/constants";

export enum ClusteringColorSpace {
    RGB = 0,
    HSL = 1,
    LAB = 2,
}

export class Settings {
    public kMeansNrOfClusters: number = CLUSTERING_DEFAULTS.DEFAULT_COLOR_COUNT;
    public kMeansMinDeltaDifference: number = CLUSTERING_DEFAULTS.CONVERGENCE_THRESHOLD;
    public kMeansClusteringColorSpace: ClusteringColorSpace = ClusteringColorSpace.RGB;

    public kMeansColorRestrictions: Array<RGB | string> = [];

    public colorAliases: { [key: string]: RGB } = {};

    public narrowPixelStripCleanupRuns: number = SEGMENTATION_CONSTANTS.DEFAULT_NARROW_STRIP_CLEANUP_RUNS; // 3 seems like a good compromise between removing enough narrow pixel strips to convergence. This fixes e.g. https://i.imgur.com/dz4ANz1.png

    public removeFacetsSmallerThanNrOfPoints: number = FACET_THRESHOLDS.MIN_FACET_SIZE;
    public removeFacetsFromLargeToSmall: boolean = true;
    public maximumNumberOfFacets: number = FACET_THRESHOLDS.MAX_FACET_COUNT;

    public nrOfTimesToHalveBorderSegments: number = SEGMENTATION_CONSTANTS.DEFAULT_HALVE_ITERATIONS;

    public resizeImageIfTooLarge: boolean = true;
    public resizeImageWidth: number = IMAGE_CONSTANTS.DEFAULT_RESIZE_WIDTH;
    public resizeImageHeight: number = IMAGE_CONSTANTS.DEFAULT_RESIZE_HEIGHT;

    public randomSeed: number = new Date().getTime();
}
