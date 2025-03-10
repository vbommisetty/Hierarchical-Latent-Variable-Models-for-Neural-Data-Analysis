import numpy as np
import matplotlib.pyplot as plt
from one.api import ONE
from brainbox.io.one import SpikeSortingLoader
from iblatlas.atlas import AllenAtlas
from statsmodels.stats.multitest import multipletests
from brainbox.io.one import SessionLoader, SpikeSortingLoader
from brainbox.singlecell import bin_spikes2D,bin_spikes

import os

def find_sensitive_clusters(
    pid,               # Probe insertion ID
    event_times,       # 1D array of event times (e.g. stimOn_times)
    sl,                # Your SessionLoader or object with sl.trials
    pre_time=0.5,      # Time (sec) before each event
    post_time=0.5,     # Time (sec) after each event
    bin_size=0.01,     # Bin size (sec)
    alpha=0.005,       # Significance level
    n_shuffles=500
):
    """
    1) Loads spikes/clusters for the given PID.
    2) Uses 'bin_spikes2D' to create an (nTrials x nClusters x nBins) array.
    3) Splits trials into left vs. right (based on sl.trials).
    4) Performs a permutation test for each cluster, comparing right minus left.
    5) Returns a list of cluster IDs with significant modulation.
    """

    one = ONE()
    ba = AllenAtlas()

    # ---------------- Load the spike data ----------------
    ssl = SpikeSortingLoader(pid=pid, one=one, atlas=ba)
    spikes, clusters, channels = ssl.load_spike_sorting()
    clusters = ssl.merge_clusters(spikes, clusters, channels)

    # -------------- Restrict to "good" clusters ---------------
    # IBL convention: label=1 => "good"
    # Make sure these fields exist in your data
    good_cluster_idx = (clusters['label'] >= 0.5)
    good_cluster_IDs = clusters['cluster_id'][good_cluster_idx]

    # Filter 'clusters' dict
    clusters_g = {key: val[good_cluster_idx] for key, val in clusters.items()}

    # Filter 'spikes' dict
    good_spk_indx = np.where(np.isin(spikes['clusters'], good_cluster_IDs))[0]
    spikes_g = {key: val[good_spk_indx] for key, val in spikes.items()}

    # convert to numpy array
    event_times = np.asarray(event_times)

    # all cluster ids (now only the "good" ones)
    cluster_ids = np.unique(spikes_g['clusters'])

    # ---------------- Bin with bin_spikes2D ----------------
    # shape(raster) => (nEvents, nClusters, nBins)
    # times => 1D array of length nBins (the bin centers)
    raster_3D, times = bin_spikes2D(
        spikes_g['times'],            # All spike times
        spikes_g['clusters'],         # Cluster IDs for each spike
        cluster_ids,                  # Which clusters to include
        event_times,                  # The event times to align to
        pre_time=pre_time,
        post_time=post_time,
        bin_size=bin_size
    )

    # Convert spike counts to firing rates (spikes/sec)
    raster_3D = raster_3D / bin_size  # (nTrials, nClusters, nBins)

    # ---------------- Identify left vs right trials ----------------
    left_idx = ~np.isnan(sl.trials['contrastLeft'])
    right_idx = ~np.isnan(sl.trials['contrastRight'])

    # For convenience, turn them into arrays of trial indices
    # (in case they're Pandas Series booleans)
    left_idx = np.asarray(left_idx)
    right_idx = np.asarray(right_idx)

    # ---------------- Permutation test for each cluster ----------------
    sig_clusters = []
    n_clusters = len(cluster_ids)
    n_bins = raster_3D.shape[2]

    for i, cid in enumerate(cluster_ids):
        # Extract this cluster's data => shape: (nTrials, nBins)
        cluster_raster = raster_3D[:, i, :]  # slice out cluster 'i'

        # Observed difference in firing rate (Right - Left) for each bin
        # shape => (nBins,)
        obs_diff = (
            np.nanmean(cluster_raster[right_idx, :], axis=0) -
            np.nanmean(cluster_raster[left_idx, :], axis=0)
        )

        # Build the null distribution via shuffling
        shuffled_diff = np.zeros((n_shuffles, n_bins))
        for s in range(n_shuffles):
            perm_left = np.random.permutation(left_idx)
            perm_right = np.random.permutation(right_idx)
            shuffled_diff[s, :] = (
                np.nanmean(cluster_raster[perm_right, :], axis=0) -
                np.nanmean(cluster_raster[perm_left, :], axis=0)
            )

        # Compute p-values
        p_vals = np.mean(np.abs(shuffled_diff) >= np.abs(obs_diff), axis=0)

        # Bonferroni
        bonf_threshold = alpha / n_bins
        bonf_reject = (p_vals < bonf_threshold)

        # FDR
        remaining = p_vals[bonf_reject]
        if len(remaining) > 0:
            _, p_fdr_corrected, _, _ = multipletests(remaining, alpha=alpha, method='fdr_bh')
            final_reject = np.copy(bonf_reject)
            final_reject[bonf_reject] = (p_fdr_corrected < alpha)
        else:
            final_reject = np.zeros_like(p_vals, dtype=bool)

        # If > 5 bins are significant, we call it “sensitive”
        if np.count_nonzero(final_reject) > 10:
            sig_clusters.append(cid)

        # to get only 30 clusters
        if len(sig_clusters) > 30:
          return sig_clusters, times

    return sig_clusters, times

def find_sensitive_clusters_dict(atlas_acronym):
    one = ONE(base_url='https://openalyx.internationalbrainlab.org', \
          password='international', \
          silent=True)
    insertions = one.search_insertions(atlas_acronym=atlas_acronym, query_type='remote')
    print(f"Found {len(insertions)} insertions in {atlas_acronym}.")
    sig_clusters_dict = {}

    if len(insertions) > 0:
        pid = insertions[32]
        print("Using PID:", pid)
        eid, pname = one.pid2eid(pid)

        sl = SessionLoader(eid=eid, one=one)
        sl.load_trials()
        trials = sl.trials

        # 1) Stim
        sig_stim_clusters, stim_times = find_sensitive_clusters(
            pid,
            event_times=trials['stimOn_times'],
            sl=sl,
            pre_time=0.5,
            post_time=0.5,
            bin_size=0.05,
            alpha=0.005,
            n_shuffles=500
        )

        # 2) Movement
        sig_movement_clusters, move_times = find_sensitive_clusters(
            pid,
            event_times=trials['firstMovement_times'],
            sl=sl,
            pre_time=0.5,
            post_time=0.5,
            bin_size=0.05,
            alpha=0.005,
            n_shuffles=500
        )

        # 3) Reward
        sig_reward_clusters, reward_times = find_sensitive_clusters(
            pid,
            event_times=trials['feedback_times'],
            sl=sl,
            pre_time=0.5,
            post_time=0.5,
            bin_size=0.05,
            alpha=0.005,
            n_shuffles=500
        )

    sig_clusters_dict['pid'] = pid
    sig_clusters_dict['stimOn'] = sig_stim_clusters
    sig_clusters_dict['firstMovement'] = sig_movement_clusters
    sig_clusters_dict['feedback'] = sig_reward_clusters

    return sig_clusters_dict


def extract_spikes_for_pcca_by_region(pid, sig_scdg, sig_sciw, event_type, one, ba):
    """
    Extracts spike data for PCCA analysis, keeping regions separate

    Args:
        pid: Probe insertion ID
        sig_scdg: Dictionary with sensitive clusters for SCdg
        sig_sciw: Dictionary with sensitive clusters for SCiw
        event_type: 'stimOn', 'firstMovement', or 'feedback'
        one, ba: Required objects for data loading

    Returns:
        Dictionary with separate spike data for each region
    """
    # Map event type to column name
    event_column = f"{event_type}_times"

    # Get the clusters for each region
    scdg_clusters = set(sig_scdg[event_type])
    sciw_clusters = set(sig_sciw[event_type])

    # We need at least one cluster from each region to load session data
    reference_cluster = next(iter(scdg_clusters)) if scdg_clusters else next(iter(sciw_clusters))

    # Load session data once for efficiency
    all_spikes, all_clusters, sl = load_cluster_data(pid, reference_cluster, one, ba)

    # Get event times
    if event_column not in sl.trials.columns:
        raise ValueError(f"{event_column} not found in trials data")

    event_times = sl.trials[event_column].to_numpy()

    # Process SCdg clusters
    scdg_data = {}
    for cluster_id in scdg_clusters:
        try:
            # Get spike times for this cluster
            cluster_spike_times = all_spikes['times'][all_spikes['clusters'] == cluster_id]

            # Bin the spikes
            binned_spikes, bin_times = bin_spikes(
                cluster_spike_times, event_times,
                pre_time=0.5, post_time=1.0, bin_size=0.05
            )

            scdg_data[cluster_id] = {
                'times': cluster_spike_times,
                'binned': binned_spikes,
                'bin_times': bin_times
            }
        except Exception as e:
            print(f"Error processing SCdg cluster {cluster_id}: {e}")

    # Process SCiw clusters
    sciw_data = {}
    for cluster_id in sciw_clusters:
        try:
            # Get spike times for this cluster
            cluster_spike_times = all_spikes['times'][all_spikes['clusters'] == cluster_id]

            # Bin the spikes
            binned_spikes, bin_times = bin_spikes(
                cluster_spike_times, event_times,
                pre_time=0.5, post_time=1.0, bin_size=0.05
            )

            sciw_data[cluster_id] = {
                'times': cluster_spike_times,
                'binned': binned_spikes,
                'bin_times': bin_times
            }
        except Exception as e:
            print(f"Error processing SCiw cluster {cluster_id}: {e}")

    return {
        'SCdg': scdg_data,
        'SCiw': sciw_data,
        'trials': sl,
        'event_times': event_times,
        'bin_times': bin_times if 'bin_times' in locals() else None
    }

def prepare_pcca_matrices(region_data, condition='left-right'):
    """
    Prepares data matrices for PCCA between SCdg and SCiw

    Args:
        region_data: Output from extract_spikes_for_pcca_by_region
        condition: 'left-right', 'correct-incorrect', or 'all'

    Returns:
        X_scdg, X_sciw: Data matrices for each region
        trial_idx: Sorted trial indices
    """
    trials = region_data['trials']

    # Get trial indices for the condition
    trial_idx, dividers, colors, labels = sort_trials_condition(trials, condition)

    # Get binned data for both regions
    scdg_binned = []
    scdg_clusters = []
    for cluster_id, data in region_data['SCdg'].items():
        scdg_binned.append(data['binned'][trial_idx])
        scdg_clusters.append(cluster_id)

    sciw_binned = []
    sciw_clusters = []
    for cluster_id, data in region_data['SCiw'].items():
        sciw_binned.append(data['binned'][trial_idx])
        sciw_clusters.append(cluster_id)

    # Check if we have data for both regions
    if not scdg_binned or not sciw_binned:
        print("Missing data for one or both regions")
        return None, None, None, None, None

    # Get dimensions
    n_trials = scdg_binned[0].shape[0]
    n_timebins = scdg_binned[0].shape[1]
    n_scdg = len(scdg_binned)
    n_sciw = len(sciw_binned)

    # Create arrays [trials × time × neurons] for each region
    X_scdg = np.zeros((n_trials, n_timebins, n_scdg))
    for i, binned in enumerate(scdg_binned):
        X_scdg[:, :, i] = binned

    X_sciw = np.zeros((n_trials, n_timebins, n_sciw))
    for i, binned in enumerate(sciw_binned):
        X_sciw[:, :, i] = binned

    return X_scdg, X_sciw, trial_idx, scdg_clusters, sciw_clusters

def load_cluster_data(pid, cluster_id, one, ba):
    """
    Loads spikes and trials for the given probe insertion ID (pid),
    filters to 'good' clusters, and returns:
      - spikes_g (dict of spike times/clusters for good clusters)
      - sl (SessionLoader with sl.trials)
      - cluster_id (the same, but we confirm it's 'good')
    Raises ValueError if cluster_id not found among good clusters.
    """

    # --- load the spike data ---
    ssl = SpikeSortingLoader(pid=pid, one=one, atlas=ba)
    spikes, clusters, channels = ssl.load_spike_sorting()
    clusters = ssl.merge_clusters(spikes, clusters, channels)

    # --- filter to good clusters ---
    good_mask = (clusters['label'] >= 0.5) #kinda good clusters
    good_cluster_ids = clusters['cluster_id'][good_mask]
    if cluster_id not in good_cluster_ids:
        raise ValueError(f"Cluster {cluster_id} is not labeled 'good' or not found in this PID.")

    # filter spikes
    good_spk_idx = np.where(np.isin(spikes['clusters'], good_cluster_ids))[0]
    spikes_g = {k: v[good_spk_idx] for k, v in spikes.items()}

    # print how many SCdg clusters we have
    scdg_mask = (clusters['acronym'][good_mask] == 'SCdg')
    scdg_ids = clusters['cluster_id'][good_mask][scdg_mask]
    print(f"SCdg clusters found: {scdg_ids}")

    # --- Load trials ---
    eid, pname = one.pid2eid(pid)
    sl = SessionLoader(eid=eid, one=one)
    sl.load_trials()

    return spikes_g, clusters, sl

def sort_trials_condition(sl, condition='left-right'):
    """
    Returns (trial_idx, dividers, colors, labels) for the specified condition.
    Conditions:
      1) 'left-right': sorts by choice=-1 (left) vs choice=+1 (right)
      2) 'correct-incorrect': uses sl.trials['feedbackType'] == 1 => correct, 0 => incorrect
      3) 'all': lumps all trials together
    """

    valid_idx = np.arange(len(sl.trials))
    if 'choice' in sl.trials.columns:
        pass

    # build arrays
    choice = sl.trials['choice'].to_numpy()
    fb_type = None
    if 'feedbackType' in sl.trials.columns:
        fb_type = sl.trials['feedbackType'].to_numpy()

    if condition == 'left-right':
        left_idx = np.where(choice == -1)[0]
        right_idx = np.where(choice == 1)[0]
        trial_idx = np.concatenate([left_idx, right_idx])
        dividers = [len(left_idx)]
        colors = ['orange', 'purple']
        labels = ['Left', 'Right']

    elif condition == 'correct-incorrect':
        if fb_type is None:
            raise ValueError("feedbackType not found in sl.trials; can't do correct-incorrect sort.")
        corr_idx = np.where(fb_type > 0)[0]
        incorr_idx = np.where(fb_type < 0)[0]
        trial_idx = np.concatenate([corr_idx, incorr_idx])
        dividers = [len(corr_idx)]
        colors = ['green', 'red']
        labels = ['Correct', 'Incorrect']

    elif condition == 'all':
        # All trials in one block
        trial_idx = np.arange(len(sl.trials))
        dividers = []
        colors = ['gray']
        labels = ['All Trials']
    else:
        raise ValueError(f"Unknown condition: {condition}")

    # Filter out any out-of-range indices if needed
    trial_idx = trial_idx[trial_idx < len(sl.trials)]

    return trial_idx, dividers, colors, labels