
import sys
from os.path import join


def phot_syst_filt_check(all_systs, entry, phot_syst, filter_name):
    """
    Check photometric system and filter names.
    """
    if phot_syst not in all_systs.keys():
        sys.exit("\nERROR: unknown photometric system '{}', given in"
                 "'{}'.".format(phot_syst, entry))
    if filter_name not in all_systs[phot_syst][1]:
        sys.exit("\nERROR: filter '{}' given in '{}' is not present\n"
                 "in '{}' photometric system.".format(
                     filter_name, entry, all_systs[phot_syst][0]))


def check(mypath, pd):
    """
    Check that the magnitudes, colors and kinematic data are properly defined.
    Store data to read from cluster's file, to load the correct set of
    isochrones, and to properly generate the synthetic clusters (if the best
    match function is set to run).
    """

    # Check read mode.
    if pd['read_mode'] not in pd['read_mode_accpt']:
        sys.exit("ERROR: read mode '{}' given in the input parameters\n"
                 "file is incorrect.".format(pd['read_mode']))

    # Check px/deg.
    if pd['id_coords'][-1] not in pd['coord_accpt']:
        sys.exit("ERROR: coordinate units '{}' given in the input parameters\n"
                 "file are incorrect.".format(pd['id_coords'][-1]))

    # Read column indexes for the IDs and the coordinates.
    if pd['read_mode'] == 'num':
        # Name of columns when no header is present. The '+ 1' is because
        # astropy Tables' first column is named 'col1', not 'col0'.
        id_col, x_col, y_col = [
            'col' + str(int(i) + 1) for i in pd['id_coords'][0:3]]
    else:
        id_col, x_col, y_col = pd['id_coords'][0:3]

    # Dictionary of photometric systems defined in the CMD service.
    all_systs = pd['cmd_systs']

    # Extract magnitudes (filters) data.
    mag_col, e_mag_col, filters = [], [], []
    for mag in pd['id_mags'][0::2]:
        try:
            column_id, phot_syst, filter_name = mag.split(',')
        except ValueError:
            sys.exit("ERROR: bad formatting for filter '{}'".format(mag))
        # Used to read data from cluster file in 'get_data.
        mag_col += [
            'col' + str(int(column_id) + 1) if pd['read_mode'] == 'num' else
            column_id]
        if pd['bf_flag']:
            # Check.
            phot_syst_filt_check(all_systs, mag, phot_syst, filter_name)
        # Name of photometric system and filter, used to extract its
        # synthetic data from the correct theoretical isochrone.
        filters.append((phot_syst, filter_name))
    # Extract magnitude error columns.
    if len(pd['id_mags'][1::2]) == len(pd['id_mags'][0::2]):
        for column_id in pd['id_mags'][1::2]:
            e_mag_col += [
                'col' + str(int(column_id) + 1) if pd['read_mode'] == 'num'
                else column_id]
    elif len(pd['id_mags'][1::2]) < len(pd['id_mags'][0::2]):
        sys.exit("ERROR: missing error column name/index for filter"
                 " in 'params_input dat'.")

    # Extract colors data.
    col_col, e_col_col, c_filters, colors = [], [], [], []
    for col in pd['id_cols'][0::2]:
        try:
            column_id, phot_syst, filter_name1, filter_name2 = col.split(',')
        except ValueError:
            sys.exit("ERROR: bad formatting for color '{}'".format(col))
        col_col += [
            'col' + str(int(column_id) + 1) if pd['read_mode'] == 'num'
            else column_id]
        if pd['bf_flag']:
            # Check.
            phot_syst_filt_check(all_systs, col, phot_syst, filter_name1)
            phot_syst_filt_check(all_systs, col, phot_syst, filter_name2)
        c_filters.append((phot_syst, filter_name1))
        c_filters.append((phot_syst, filter_name2))
        colors.append((phot_syst, filter_name1 + ',' + filter_name2))
    # Extract colors error columns.
    if len(pd['id_cols'][1::2]) == len(pd['id_cols'][0::2]):
        for column_id in pd['id_cols'][1::2]:
            e_col_col += [
                'col' + str(int(column_id) + 1) if pd['read_mode'] == 'num'
                else column_id]
    elif len(pd['id_cols'][1::2]) < len(pd['id_cols'][0::2]):
        sys.exit("ERROR: missing error column name/index for color"
                 " in 'params_input dat'.")

    all_syst_filters, iso_paths = [], []
    if pd['bf_flag']:
        # Remove duplicate filters (if they exist), and combine them into one
        # tuple per photometric system.
        # The resulting list looks like this:
        # [('2', 'T1', 'C'), ('4', 'B', 'V'), ('65', 'J')]
        # where the first element of each tuple points to the photometric
        # system, and the remaining elements are the unique filters in that
        # system.
        all_syst_filters = list(set(filters + c_filters))
        d = {}
        for k, v in all_syst_filters:
            d.setdefault(k, [k]).append(v)
        all_syst_filters = sorted(map(tuple, d.values()))

        # Fix isochrones location according to the CMD and set selected.
        text1 = pd['cmd_evol_tracks'][pd['evol_track']][0]
        # Generate correct name for the isochrones path.
        iso_paths = []
        for p_syst in all_syst_filters:
            text2 = all_systs[p_syst[0]][0]
            # Set iso_path according to the above values.
            iso_paths.append(
                join(mypath + 'isochrones/' + text1 + '_' + text2))

        # REMOVE when support for multiple photometric systems is in place.
        if len(all_syst_filters) > 1:
            sys.exit("ERROR: more than one photometric system defined.")
        # REMOVE when support for multiple mags/colors is in place.
        if len(filters) > 1:
            sys.exit("ERROR: more than one filter defined.")
        if len(colors) > 2:
            sys.exit("ERROR: more than two colors defined.")

    # Add data to parameters dictionary.
    pd['id_col'], pd['x_col'], pd['y_col'], pd['coords'],\
        pd['mag_col'], pd['e_mag_col'], pd['filters'], pd['col_col'],\
        pd['e_col_col'], pd['colors'], pd['all_syst_filters'],\
        pd['iso_paths'] = id_col, x_col, y_col, pd['id_coords'][-1], mag_col,\
        e_mag_col, filters, col_col, e_col_col, colors,\
        all_syst_filters, iso_paths

    # Read PMs, parallax, and RV data.
    k_cols = ('plx', 'e_plx', 'pmx', 'e_pmx', 'pmy', 'e_pmy', 'rv', 'e_rv')
    for i, ci in enumerate(pd['id_kinem']):
        if ci not in ('n', 'N'):
            try:
                pd[k_cols[i] + '_col'] = 'col' + str(int(ci) + 1) if\
                    pd['read_mode'] == 'num' else ci
            except ValueError:
                sys.exit("ERROR: bad index ('{}') for '{}' column"
                         " in 'params_input dat'.".format(ci, k_cols[i]))
        else:
            pd[k_cols[i] + '_col'] = False

    # Check that PMs are either both or none defined.
    if pd['pmx_col'] != pd['pmy_col']:
        sys.exit("ERROR: both (or none) PM dimensions must be defined"
                 " in 'params_input dat'.")

    # Check that error columns are present
    for col in ('plx_col', 'pmx_col', 'pmy_col', 'rv_col'):
        if pd[col] is not False and pd['e_' + col] is False:
            sys.exit("ERROR: missing error column for '{}' in"
                     "'params_input dat'.".format(col))

    # Check max error values.
    for i, e in enumerate(pd['err_max']):
        try:
            float(e)
        except ValueError:
            if e not in ('n', 'N'):
                sys.exit("ERROR: bad value ('{}') for '{}' max error"
                         " in 'params_input dat'.".format(e, i))

    return pd
