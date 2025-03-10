
###############################################################################
# SETUP / IMPORTS
###############################################################################
import logging
import os

os.makedirs("results", exist_ok=True)

logger = logging.getLogger('ibllib')
logger.setLevel(logging.CRITICAL)

os.environ["TQDM_DISABLE"] = "1"

import numpy as np
import matplotlib.pyplot as plt
from statsmodels.stats.multitest import multipletests
from one.api import ONE
from brainbox.io.one import SessionLoader, SpikeSortingLoader
from brainbox.singlecell import bin_spikes
from brainbox.singlecell import bin_spikes2D


from iblatlas.atlas import AllenAtlas
ba = AllenAtlas()

one = ONE(base_url='https://openalyx.internationalbrainlab.org', \
          password='international', \
          silent=True)

from eda import plot_cluster_all, get_diff_arrays_for_one_cluster, plot_difference_with_significance
from preprocessing import find_sensitive_clusters_dict
from sklearn.decomposition import PCA
from PCCA import PCCA

###############################################################################
# EDA
###############################################################################

pid = '3675290c-8134-4598-b924-83edb7940269'
[eid, pname] = one.pid2eid(pid)

ssl = SpikeSortingLoader(pid=pid, one=one, atlas=ba)
spikes, clusters, channels = ssl.load_spike_sorting()
clusters = ssl.merge_clusters(spikes, clusters, channels)

sl = SessionLoader(eid=eid, one=one)
sl.load_trials()
trials = sl.trials

sig = find_sensitive_clusters_dict(atlas_acronym='SCdg')

cluster_to_plot = sig['stimOn'][-2]

obs_diff, shuffled_diff, final_reject, time_bins = get_diff_arrays_for_one_cluster(
    pid=pid,
    sl=sl,
    cluster_id=cluster_to_plot,
    event_times=trials['stimOn_times'],
    pre_time=0.5,
    post_time=01.0,
    bin_size=0.05,
    alpha=0.005,
    n_shuffles=500
)

plot_difference_with_significance(
    time_bins=time_bins,
    obs_diff=obs_diff,
    shuffled_diff=shuffled_diff,
    final_reject=final_reject,
    title=f"Stim - Cluster {cluster_to_plot}"
)

plot_cluster_all(pid=pid, cluster_id=328, one=one, ba=ba)

###############################################################################
# PREPROCESSING FOR PCCA
###############################################################################

from preprocessing import extract_spikes_for_pcca_by_region, prepare_pcca_matrices

sig_scdg = find_sensitive_clusters_dict(atlas_acronym='SCdg')
sig_sciw = find_sensitive_clusters_dict(atlas_acronym='SCiw')

data = extract_spikes_for_pcca_by_region(sig_scdg['pid'], sig_scdg, sig_sciw,'stimOn', one, ba)
X_scdg, X_sciw, trial_idx, scdg_clusters, sciw_clusters = prepare_pcca_matrices(data, condition='left-right')

###############################################################################
# PCCA
###############################################################################

# Original 3D shapes
print(X_scdg.shape)  # (n_trials, n_clusters, n_time_bins)
print(X_sciw.shape)

# Reshape into 2D (flatten cluster and time dimensions)
X_scdg_flat = X_scdg.reshape(X_scdg.shape[0], -1)
X_sciw_flat = X_sciw.reshape(X_sciw.shape[0], -1)

print(X_scdg_flat.shape)  # (n_trials, n_clusters * n_time_bins)
print(X_sciw_flat.shape)

# Apply PCA to reduce dimensionality
pca_components = 200  # You can adjust this based on variance explained
pca1 = PCA(n_components=pca_components)
pca2 = PCA(n_components=pca_components)

X1_pcca = pca1.fit_transform(X_scdg_flat)
X2_pcca = pca2.fit_transform(X_sciw_flat)

print(X1_pcca.shape)  # Now (n_trials, pca_components)
print(X2_pcca.shape)

def pcca_rmse(X1, X2, components=2):
    # 1) Fit
    pcca = PCCA(components, 100)
    pcca.fit(X1_pcca, X2_pcca)

    # 2) Generate same # of samples as original
    n_samples = X1.shape[0]
    X1_gen, X2_gen = pcca.sample()

    # 3) RMSE
    num_samples = min(X1.shape[0], X2.shape[0])

    if X1.shape[0] != X2.shape[0]:
        X1, X2 = X1[:num_samples], X2[:num_samples]

    rmse1 = np.sqrt(np.mean((X1_gen - X1_pcca)**2))
    rmse2 = np.sqrt(np.mean((X2_gen - X2_pcca)**2))
    return rmse1, rmse2

# Suppose X1, X2 are (nSamples, nFeaturesA/B)
latent_dims = range(1,15)
rmseA, rmseB = [], []

for d in latent_dims:
    rA, rB = pcca_rmse(X1_pcca, X2_pcca, d)
    rmseA.append(rA)
    rmseB.append(rB)
    print(f"latent_dims {d} done")

plt.plot(latent_dims, rmseA, marker='o', label='SCdg RMSE')
plt.plot(latent_dims, rmseB, marker='s', label='SCiw RMSE')
plt.xlabel("Number of Latent Components")
plt.ylabel("RMSE")
plt.title("PCCA Reconstruction Error")
plt.legend()
plt.savefig(f"results/PCCA Reconstruction Error.png", dpi=300, bbox_inches='tight')
plt.close()

print("Done!")