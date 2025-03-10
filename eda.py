import numpy as np
import matplotlib.pyplot as plt
from one.api import ONE
from brainbox.io.one import SpikeSortingLoader
from iblatlas.atlas import AllenAtlas
from statsmodels.stats.multitest import multipletests
from brainbox.singlecell import bin_spikes2D,bin_spikes
from brainbox.io.one import SessionLoader, SpikeSortingLoader

import os

def get_diff_arrays_for_one_cluster(pid,
                                    sl,
                                    cluster_id,
                                    event_times,
                                    pre_time=0.5,
                                    post_time=0.5,
                                    bin_size=0.05,
                                    alpha=0.005,
                                    n_shuffles=500):
    """
    Bins spikes around event_times for the specified cluster_id,
    computes:
      obs_diff: observed (Right - Left) difference in each time bin,
      shuffled_diff: the null distribution of differences (via label shuffling),
      final_reject: boolean mask of significant time bins after corrections,
      time_bins: the bin centers from the binning.

    Returns
    -------
    obs_diff : 1D array
        Observed (Right - Left) difference in firing rate at each time bin.
    shuffled_diff : 2D array
        Null distribution from shuffled trial labels (shape n_shuffles x n_bins).
    final_reject : 1D boolean array
        True for bins that remain significant after multiple-comparisons correction.
    time_bins : 1D array
        The bin centers for plotting (same length as obs_diff).
    """
    # --- Load the data ---
    one = ONE()
    ba = AllenAtlas()
    ssl = SpikeSortingLoader(pid=pid, one=one, atlas=ba)
    spikes, clusters, channels = ssl.load_spike_sorting()
    clusters = ssl.merge_clusters(spikes, clusters, channels)

    # --- Define the full set of cluster IDs ---
    cluster_ids = np.unique(spikes['clusters'])

    # --- Convert event_times to numpy array ---
    event_times = np.asarray(event_times)

    # --- Bin spikes for ALL clusters in cluster_ids ---
    # This gives us a raster with shape (nTrials, nClusters, nBins)
    # plus the bin center times.
    raster_3D, time_bins = bin_spikes2D(
        spikes['times'],        # full spike times
        spikes['clusters'],     # each spike's cluster ID
        cluster_ids,            # the set of cluster IDs we're including
        event_times,
        pre_time=pre_time,
        post_time=post_time,
        bin_size=bin_size
    )

    # Convert spike counts to firing rates
    raster_3D = raster_3D / bin_size  # shape => (nTrials, nClusters, nBins)

    # --- Find the index for 'cluster_id' within 'cluster_ids' ---
    matching_idx = np.where(cluster_ids == cluster_id)[0]
    if len(matching_idx) == 0:
        raise IndexError(f"Cluster {cluster_id} not found in cluster_ids.")
    cluster_idx = matching_idx[0]

    # --- Identify "left" vs "right" trials ---
    left_idx = ~np.isnan(sl.trials['contrastLeft'])
    right_idx = ~np.isnan(sl.trials['contrastRight'])

    # Extract just this cluster's data => shape (nTrials, nBins)
    cluster_raster = raster_3D[:, cluster_idx, :]

    # --- Observed difference (Right - Left) in each bin ---
    obs_diff = (
        np.nanmean(cluster_raster[right_idx, :], axis=0) -
        np.nanmean(cluster_raster[left_idx, :], axis=0)
    )

    # --- Build null distribution via shuffling ---
    n_bins = cluster_raster.shape[1]
    shuffled_diff = np.zeros((n_shuffles, n_bins))
    for s in range(n_shuffles):
        perm_left = np.random.permutation(left_idx)
        perm_right = np.random.permutation(right_idx)
        shuffled_diff[s, :] = (
            np.nanmean(cluster_raster[perm_right, :], axis=0) -
            np.nanmean(cluster_raster[perm_left, :], axis=0)
        )

    # --- Compute p-values (two-sided) ---
    p_vals = np.mean(np.abs(shuffled_diff) >= np.abs(obs_diff), axis=0)

    # --- Multiple-comparisons correction ---
    bonf_threshold = alpha / n_bins
    bonf_reject = (p_vals < bonf_threshold)

    remaining = p_vals[bonf_reject]
    if len(remaining) > 0:
        _, p_fdr_corrected, _, _ = multipletests(remaining, alpha=alpha, method='fdr_bh')
        final_reject = np.copy(bonf_reject)
        final_reject[bonf_reject] = (p_fdr_corrected < alpha)
    else:
        final_reject = np.zeros_like(p_vals, dtype=bool)

    # Return arrays needed for plotting
    return obs_diff, shuffled_diff, final_reject, time_bins

def plot_difference_with_significance(time_bins,
                                      obs_diff,
                                      shuffled_diff,
                                      final_reject,
                                      title="Observed vs. Shuffled Differences"):
    """
    Plots the observed difference in firing rates over time (obs_diff),
    overlays the null distribution (shuffled_diff) as a shaded region,
    and highlights time bins deemed significant (final_reject).

    Parameters
    ----------
    time_bins : 1D array
        The time axis (bin centers), shape (n_bins,).
    obs_diff : 1D array
        Observed difference (Right - Left) per time bin, shape (n_bins,).
    shuffled_diff : 2D array
        Null distribution from shuffled trial labels, shape (n_shuffles, n_bins).
    final_reject : 1D boolean array
        Boolean mask of which bins are significant after corrections, shape (n_bins,).
    title : str
        Plot title.
    """

    # percentile boundaries
    lower_bound = np.percentile(shuffled_diff, 2.5, axis=0)
    upper_bound = np.percentile(shuffled_diff, 97.5, axis=0)

    plt.figure(figsize=(10, 5))

    # observed difference
    plt.plot(time_bins, obs_diff, label="Observed Difference")

    # horizontal line at zero
    plt.axhline(0, linestyle='--', label="Zero Reference")

    # null distribution
    plt.fill_between(time_bins,
                     lower_bound, upper_bound,
                     alpha=0.3, label="Null Distribution (95% CI)")

    # highlight time bins that are significant
    plt.fill_between(time_bins,
                     obs_diff,
                     where=final_reject,
                     interpolate=True,
                     alpha=0.3,
                     label="Significant Bins")

    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Difference in Firing Rate (Hz)")
    plt.legend()
    plt.savefig(f"results/{title}.png", dpi=300, bbox_inches='tight')
    plt.close()

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


def plot_raster_psth(axs, spike_times, event_times, trial_idx, dividers, colors, labels,
                     pre_time=0.5, post_time=1.0, raster_bin=0.01, psth_bin=0.02):
    """
    Given a 2-element array of Axes: axs[0] = PSTH, axs[1] = Raster,
    plots a PSTH + raster for a single event type.
    - spike_times: 1D array of spike times for this cluster (good cluster)
    - event_times: array of times to align to (e.g. stimOn_times)
    - trial_idx, dividers, colors, labels: from sort_trials_condition
    - pre_time, post_time: time window for binning
    - raster_bin, psth_bin: bin sizes for raster and PSTH
    """
    # drop nans
    not_nan = ~np.isnan(event_times)
    event_times = event_times[not_nan]

    trial_idx = [t for t in trial_idx if t < len(event_times)]
    trial_idx = np.array(trial_idx)

    raster, t_raster = bin_spikes(
        spike_times, event_times, pre_time=pre_time, post_time=post_time,
        bin_size=raster_bin
    )

    # build PSTH matrix
    psth, t_psth = bin_spikes(
        spike_times, event_times, pre_time=pre_time, post_time=post_time,
        bin_size=psth_bin
    )
    # convert counts to rates
    psth = psth / psth_bin

    dividers = [0] + dividers + [len(trial_idx)]

    # ========== PSTH ==========
    for block_i in range(len(dividers) - 1):
        block_start = dividers[block_i]
        block_end = dividers[block_i + 1]
        block_ids = trial_idx[block_start:block_end]
        if len(block_ids) == 0:
            continue
        color_i = colors[block_i] if block_i < len(colors) else '0.5'
        label_i = labels[block_i] if block_i < len(labels) else f"Block {block_i}"

        mean_rate = np.nanmean(psth[block_ids, :], axis=0)
        sem_rate = np.nanstd(psth[block_ids, :], axis=0) / np.sqrt(len(block_ids))

        axs[0].fill_between(t_psth, mean_rate - sem_rate, mean_rate + sem_rate,
                            color=color_i, alpha=0.3)
        axs[0].plot(t_psth, mean_rate, color=color_i, label=label_i)

    axs[0].axvline(0, linestyle='--', color='k')
    axs[0].set_ylabel("Firing Rate (Hz)")
    axs[0].legend(loc='best')

    # ========== RASTER ==========
    raster_sorted = raster[trial_idx, :]
    axs[1].imshow(raster_sorted, cmap='binary', origin='lower',
                  extent=[-pre_time, post_time, 0, len(trial_idx)],
                  aspect='auto')
    axs[1].axvline(0, linestyle='--', color='k')
    axs[1].set_ylabel("Trials (sorted)")

    width = 0.1
    for block_i in range(len(dividers) - 1):
        block_start = dividers[block_i]
        block_end = dividers[block_i + 1]
        color_i = colors[block_i] if block_i < len(colors) else '0.5'
        axs[1].fill_between(
            [post_time, post_time + width],
            [block_end, block_end], [block_start, block_start],
            color=color_i, alpha=0.5
        )

    axs[1].set_xlim([-pre_time, post_time + width])


def plot_cluster_all(pid, cluster_id, one, ba):
    """
    1) Loads data for a single cluster (must be 'good').
    2) Creates 3 separate figures:
       (a) Left vs Right
       (b) Correct vs Incorrect
       (c) All Trials
    3) Each figure has 3 rows (stimOn, firstMove, feedback).
       Each row has 2 subplots (PSTH + Raster).
    """

    # load data and confirm cluster is good
    spikes_g, clusters, sl = load_cluster_data(pid, cluster_id, one, ba)

    event_names = ["stimOn_times", "firstMovement_times", "feedback_times"]

    conditions = ["left-right", "correct-incorrect", "all"]
    condition_titles = ["Left vs Right", "Correct vs Incorrect", "All Trials"]

    for cond, cond_title in zip(conditions, condition_titles):
        fig, axs = plt.subplots(nrows=3, ncols=2, figsize=(10, 12), sharex=False)
        fig.suptitle(f"PID={pid}, Cluster={cluster_id}\nCondition: {cond_title}", fontsize=16)

        for i, evt_name in enumerate(event_names):
            if evt_name not in sl.trials.columns:
                print(f"Warning: {evt_name} not found in sl.trials.")
                continue

            trial_idx, dividers, colors, labels = sort_trials_condition(sl, condition=cond)

            event_times = sl.trials[evt_name].to_numpy()
            ax_psth = axs[i, 0]
            ax_raster = axs[i, 1]
            # plot PSTH + raster
            plot_raster_psth(
                axs=[ax_psth, ax_raster],
                spike_times=spikes_g['times'][spikes_g['clusters'] == cluster_id],
                event_times=event_times,
                trial_idx=trial_idx,
                dividers=dividers,
                colors=colors,
                labels=labels,
                pre_time=0.5,
                post_time=1.0,
                raster_bin=0.01,
                psth_bin=0.02
            )

            ax_psth.set_title(evt_name)
            if i == 2:
                ax_raster.set_xlabel("Time (s)")

        plt.tight_layout()
        filename = f"PID_{pid}_Cluster_{cluster_id}_{cond}"
        plt.savefig(f"results/{filename}.png", dpi=300, bbox_inches='tight')
        plt.close()

