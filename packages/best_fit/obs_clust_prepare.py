
import numpy as np
from ..decont_algors.local_cell_clean import bin_edges_f


def main(cl_max_mag, lkl_method, bin_method):
    '''
    Prepare observed cluster array here to save time before the algorithm to
    find the best synthetic cluster fit is used.
    '''

    # Extract photometric data, and membership probabilities. Remove ID's to
    # make entire array of floats.
    mags_cols_cl = [[], []]
    for mag in zip(*zip(*cl_max_mag)[1:][2]):
        mags_cols_cl[0].append(mag)
    for col in zip(*zip(*cl_max_mag)[1:][4]):
        mags_cols_cl[1].append(col)

    # Square errors here to not repeat the same calculations each time a
    # new synthetic cluster is matched.
    e_mags_cols = []
    for e_m in zip(*zip(*cl_max_mag)[1:][3]):
        e_mags_cols.append(np.square(e_m))
    for e_c in zip(*zip(*cl_max_mag)[1:][5]):
        e_mags_cols.append(np.square(e_c))

    # Store membership probabilities here.
    memb_probs = np.array(zip(*cl_max_mag)[1:][6])

    if lkl_method == 'tolstoy':
        # Store and pass to use in likelihood function. The 'obs_st' list is
        # made up of:
        # obs_st = [star_1, star_2, ...]
        # star_i = [phot_1, phot_2, phot_3, ...]
        # phot_j = [phot_val, error]
        # Where 'phot_j' is a photometric dimension (magnitude or color), and
        # 'phot_val', 'error' the associated value and error for 'star_i'.
        obs_st = []
        mags_cols = mags_cols_cl[0] + mags_cols_cl[1]
        for st_phot, st_e_phot in zip(zip(*mags_cols), zip(*e_mags_cols)):
            obs_st.append(zip(*[st_phot, st_e_phot]))
        obs_clust = [obs_st, memb_probs]

    elif lkl_method in ['dolphin', 'mighell']:
        # Obtain bin edges for each dimension, defining a grid.
        bin_edges = bin_edges_f(bin_method, mags_cols_cl)

        # Put all magnitudes and colors into a single list.
        obs_mags_cols = mags_cols_cl[0] + mags_cols_cl[1]
        # Obtain histogram for observed cluster.
        cl_histo = np.histogramdd(obs_mags_cols, bins=bin_edges)[0]

        # Generate a weighted histogram: "the values of the returned
        # histogram are equal to the sum of the weights belonging to the
        # samples falling into each bin."
        w = np.histogramdd(
            obs_mags_cols, bins=bin_edges, weights=memb_probs)[0]
        # Divide by the number of stars in each bin to obtain the average MP
        # per bin (add a small float to avoid a 'ZeroDivisionError')
        bin_weight = w / (cl_histo + 1.e-9)

        # Flatten N-dimensional histograms.
        cl_histo_f = np.array(cl_histo).ravel()
        bin_weight_f = np.array(bin_weight).ravel()

        # Index of bins where n_i = 0 (no observed stars). Used by the
        # 'Dolphin' and 'Mighell' likelihoods.
        cl_z_idx = [cl_histo_f != 0]

        # Remove all bins where n_i = 0 (no observed stars). Used by the
        # 'Dolphin' likelihood.
        cl_histo_f_z = cl_histo_f[cl_z_idx]
        bin_weight_f_z = bin_weight_f[cl_z_idx]

        # (Weighted) Dolphin n_i dependent constant.
        # n_i constant: 2 * [sum(n_i * ln(n_i)) - N] =
        # 2 * [sum(n_i * ln(n_i)) - sum(n_i)] =
        # 2 * sum(n_i * ln(n_i) - n_i) =
        # 2 * sum(n_i * (ln(n_i) - 1)) =
        # Weighted: 2 * sum(w_i * n_i * (ln(n_i) - 1))
        dolphin_cst = 2. * np.sum(
            bin_weight_f_z * cl_histo_f_z * (np.log(cl_histo_f_z) - 1.))

        obs_clust = [bin_edges, cl_histo, cl_histo_f, cl_z_idx, cl_histo_f_z,
                     dolphin_cst, bin_weight_f_z]

    return obs_clust
