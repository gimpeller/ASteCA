
from . import move_isochrone
from . import synth_cluster
from ..best_fit.mcmc_common import closeSol


def main(e_max, fundam_params, theor_tracks, plot_isoch_data, isoch_fit_params,
         err_lst, completeness, max_mag_syn, st_dist_mass, R_V, ext_coefs,
         N_fc, cmpl_rnd, err_rnd):
    '''
    # Generate shifted isochrone and synthetic cluster for plotting.
    '''
    # Use mean fit values for all parameters.
    synth_cl_params = isoch_fit_params['mean_sol']
    # Grid values for (z, a, M)
    synth_cl_params_grid = closeSol(fundam_params, synth_cl_params, [0, 1, 4])

    # Find indexes for metallicity and age. If indexes are not found due
    # to some difference in the significant figures, use the indexes
    # [0, 0] to prevent the code from halting.
    try:
        m_i = fundam_params[0].index(synth_cl_params_grid[0])
        a_i = fundam_params[1].index(synth_cl_params_grid[1])
    except Exception:
        m_i, a_i = [0, 0]
        print("  WARNING: metallicity and age for best match synthetic\n"
              "  cluster not found.")

    # Generate shifted best fit isochrone.
    isochrone = plot_isoch_data[m_i][a_i]
    shift_isoch = move_isochrone.main(
        isochrone, synth_cl_params[2], synth_cl_params[3], R_V, ext_coefs,
        N_fc)

    # Generate best fit synthetic cluster.
    isochrone = theor_tracks[m_i][a_i]
    synth_clst = synth_cluster.main(
        e_max, err_lst, completeness, max_mag_syn, st_dist_mass, isochrone,
        R_V, ext_coefs, N_fc, cmpl_rnd, err_rnd, synth_cl_params_grid)

    return shift_isoch, synth_clst
