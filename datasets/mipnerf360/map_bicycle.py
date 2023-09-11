from pathlib import Path

from hloc import extract_features, pairs_from_retrieval, match_features, pairs_from_exhaustive, reconstruction
from pixsfm.refine_hloc import PixSfM

import pycolmap
from hloc.localize_sfm import QueryLocalizer, pose_from_cluster

retrieval_conf = extract_features.confs['netvlad']
num_matched=7
feature_conf = extract_features.confs['superpoint_max']
matcher_conf = match_features.confs['superpoint+lightglue']
pixsfm_max_edge=1600

images = Path('bicycle/images/')
outputs = Path('outputs/bicycle/')
sfm_pairs = outputs / 'pairs-sfm.txt'

loc_pairs = outputs / 'pairs-loc.txt'

# Find image pairs

print(f"Finding the {num_matched} most similar images to each image using NetVLAD...")

retrieval_path = extract_features.main(
    conf=retrieval_conf,
    image_dir=images,
    export_dir=outputs)

pairs_from_retrieval.main(
    descriptors=retrieval_path,
    output=sfm_pairs,
    num_matched=num_matched)

# Extract features

print(f"Extracting image features using Superpoint (max quality)...")

feature_path = extract_features.main(
    conf=feature_conf,
    image_dir=images,
    export_dir=outputs)

# Match features

print(f"Matching image features using Superpoint+LightGlue...")

match_path = match_features.main(matcher_conf, sfm_pairs, feature_conf['output'], outputs)

# Sparse 3D reconstruction

print(f"Performing sparse 3D reconstruction using Pixel-Perfect SfM...")

sfm_dir = outputs / 'sfm'

sfm = PixSfM({"dense_features": {"max_edge": pixsfm_max_edge}})
refined, sfm_outputs = sfm.reconstruction(
    sfm_dir,
    images,
    sfm_pairs,
    feature_path,
    match_path)
