
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.offsetbox as offsetbox
from mpl_toolkits.axes_grid1 import make_axes_locatable
from itertools import cycle
from ..structure import king_prof_funcs as kpf


def pl_center(
    gs, fig, asp_ratio, x_name, y_name, coord, bw_list, kde_cent,
        frame_kde_cent, fr_dens, clust_rad):
    """
    Coordinates 2D KDE.
    """

    ax = plt.subplot(gs[0:2, 0:2])
    frmt = '{:.4f}' if coord == 'deg' else '{:.0f}'
    ax.set_title((r'$KDE_{{bdw}}$ =' + frmt + ' [{}]').format(
        bw_list[1], coord), fontsize=9)
    plt.xlabel('{} ({})'.format(x_name, coord), fontsize=10)
    plt.ylabel('{} ({})'.format(y_name, coord), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)

    ax.minorticks_on()
    plt.axvline(x=kde_cent[0], linestyle='--', color='green')
    plt.axhline(y=kde_cent[1], linestyle='--', color='green')
    # Radius
    circle = plt.Circle(
        (kde_cent[0], kde_cent[1]), clust_rad, color='green', fill=False)
    fig.gca().add_artist(circle)

    ext_range, x_grid, y_grid, k_pos = frame_kde_cent
    kde = np.reshape(k_pos.T, x_grid.shape)
    im = plt.imshow(
        np.rot90(kde), cmap=plt.get_cmap('RdYlBu_r'), extent=ext_range)
    plt.contour(x_grid, y_grid, kde, colors='#551a8b', linewidths=0.5)
    # If RA is used, invert axis.
    if coord == 'deg':
        ax.invert_xaxis()

    # Colorbar on the right side of ax.
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="2%", pad=0.05)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_ticks([np.min(kde), np.ptp(kde) * .5, np.max(kde)])
    scale = 3600. if coord == 'deg' else 1.

    kde_dens_min, kde_dens_max = fr_dens.min(), fr_dens.max()
    midpt = ((kde_dens_max + kde_dens_min) * .5) / scale
    frmt = '{:.2E}' if midpt > 100. or midpt < .1 else '{:.0f}'
    cbar.ax.set_yticklabels([
        frmt.format(kde_dens_min / scale),
        frmt.format(midpt),
        frmt.format(kde_dens_max / scale)], rotation=90)
    cbar.ax.tick_params(labelsize=7)
    # Align bottom and middle labels. Don't include last label (one at the
    # top) as we don't want to change its alignment.
    for i, label in enumerate(cbar.ax.get_yticklabels()[:-1]):
        if i == 0:
            label.set_va("bottom")
        else:
            label.set_va("center")

    ax.set_aspect(aspect=asp_ratio)


def pl_knn_dens(
    gs, fig, asp_ratio, x_min, x_max, y_min, y_max, x_name, y_name, coord,
        NN_dd, xy_dens, fr_dens, NN_dist, kde_cent):
    """
    """
    ax = plt.subplot(gs[0:2, 2:4])
    ax.set_aspect(aspect=asp_ratio)
    # Set plot limits
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    # If RA is used, invert axis.
    if coord == 'deg':
        ax.invert_xaxis()
    ax.set_title((r'$kNN={}\;(d\leq d_{{p=25\%}})$').format(NN_dd), fontsize=9)

    plt.xlabel('{} ({})'.format(x_name, coord), fontsize=10)
    plt.ylabel('{} ({})'.format(y_name, coord), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.minorticks_on()
    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=.5)

    perc = np.percentile(NN_dist, 25)
    msk = NN_dist < perc
    xy, NN_d = xy_dens[msk], NN_dist[msk]
    for i, (x, y) in enumerate(xy):
        circle = plt.Circle(
            (x, y), NN_d[i], color='k', lw=.5, alpha=.5, fill=False)
        fig.gca().add_artist(circle)

    # Star with the smallest associated density.
    idx = np.argmin(fr_dens)
    circle = plt.Circle(
        (xy_dens[idx][0], xy_dens[idx][1]), NN_dist[idx], color='b', lw=1.5,
        fill=False, zorder=4)
    fig.gca().add_artist(circle)
    plt.plot([], [], color='b', lw=2., label=r"$dens_{min}$")
    # Star with the largest associated density.
    idx = np.argmax(fr_dens)
    circle = plt.Circle(
        (xy_dens[idx][0], xy_dens[idx][1]), NN_dist[idx], color='r', lw=1.,
        fill=False, zorder=5)
    fig.gca().add_artist(circle)
    plt.plot([], [], color='r', lw=2., label=r"$dens_{max}$")

    # Assigned center.
    plt.scatter(kde_cent[0], kde_cent[1], color='g', s=40, lw=1.5,
                marker='x', zorder=5)
    leg = plt.legend(fancybox=True, fontsize=10, handlelength=1., loc='best')
    leg.get_frame().set_alpha(0.7)


def pl_field_dens(
    gs, coord, fdens_method, fr_dist, fr_dens, fdens_min_d, fdens_lst,
        fdens_std_lst, field_dens_d, field_dens, field_dens_std):
    """
    Field density values for different percentiles.
    """
    # Convert from deg to arcmin if (ra,dec) were used.
    if coord == 'deg':
        fr_dist, fdens_min_d, field_dens_d = np.array(fr_dist) * 60.,\
            np.array(fdens_min_d) * 60., field_dens_d * 60.
        fr_dens, fdens_lst, fdens_std_lst = [
            np.array(_) / 3600. for _ in (fr_dens, fdens_lst, fdens_std_lst)]
        field_dens = field_dens / 3600.
        coord2 = 'arcmin'
    else:
        coord2 = 'px'

    delta_y = np.ptp(fr_dens) * .1
    ymin = max(0., min(fr_dens) - delta_y)
    ymax = max(fr_dens) + delta_y

    ax = plt.subplot(gs[0:2, 4:6])
    plt.ylim(ymin, ymax)
    ax.minorticks_on()
    plt.xlabel(
        r'Distance to center $[{}]$'.format(coord2), fontsize=10)
    plt.ylabel(r"$\rho$ $[st/{}^{{2}}]$".format(coord2), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))
    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=.5)

    plt.scatter(fr_dist, fr_dens, c='k', s=5, alpha=.2, zorder=1)
    plt.errorbar(
        fdens_min_d, fdens_lst, yerr=fdens_std_lst, fmt='b', ms=25,
        ecolor='r', lw=1.2)

    t1 = r"$d_{{field}}=$ {:.1E} $[st/{}^{{2}}]$".format(
        field_dens, coord2)

    # Check if a manual value was used
    if not np.isnan(field_dens_d):
        plt.scatter(
            field_dens_d, field_dens, marker='o', s=25, c='g', label=t1,
            zorder=5)
    else:
        ax.hlines(
            field_dens, xmin=fdens_min_d[0], xmax=fdens_min_d[-1], color='g',
            label=t1)

    leg = plt.legend(fancybox=True, fontsize=10, loc='upper right')
    leg.get_frame().set_alpha(0.7)


def pl_rad_find(
    gs, coord, clust_rad, e_rad, rad_rads, rad_N_membs, rad_N_field,
        rad_CI):
    """
    Radius estimation plot.
    """
    # Convert from deg to arcmin if (ra,dec) were used.
    if coord == 'deg':
        rad_rads = np.array(rad_rads) * 60.
        clust_rad, e_rad = clust_rad * 60., e_rad * 60.
        coord2 = 'arcmin'
    else:
        coord2 = 'px'

    ax = plt.subplot(gs[2:4, 0:2])
    plt.ylim(0., 1.02)
    ax.minorticks_on()
    plt.xlabel(r'radius $[{}]$'.format(coord2), fontsize=10)
    plt.ylabel(r"$N_{memb}\;|\;N_{field}\;|\;CI$", fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)

    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=.5)

    plt.plot(rad_rads, rad_N_membs, c='g', label=r'$N_{memb}$')
    plt.plot(rad_rads, rad_N_field, c='b', ls='--', label=r'$N_{field}$')
    plt.plot(rad_rads, rad_CI, ls=':', c='k', label='CI')
    plt.axvline(x=clust_rad, lw=1.5, color='r', label=r"$r_{cl}$")
    if e_rad > 0.:
        plt.axvspan((clust_rad - e_rad), (clust_rad + e_rad),
                    facecolor='grey', alpha=0.25)
    # Legends.
    leg = plt.legend(fancybox=True, fontsize=10)
    leg.get_frame().set_alpha(0.7)

    xmin, xmax = ax.get_xlim()
    plt.xlim(max(xmin, 0.), xmax)


def pl_rad_dens(
    gs, coord, radii, rdp_points, field_dens, field_dens_std, clust_rad,
    e_rad, rdp_stddev, core_rad, e_core, tidal_rad, e_tidal, K_cent_dens,
        flag_2pk_conver, flag_3pk_conver):
    """
    Radial density plot.
    """

    # Convert from deg to arcmin if (ra,dec) were used.
    if coord == 'deg':
        radii = np.array(radii) * 60.
        clust_rad, e_rad = clust_rad * 60., e_rad * 60.
        core_rad, e_core, tidal_rad, e_tidal = core_rad * 60., e_core * 60.,\
            tidal_rad * 60., e_tidal * 60.
        field_dens, field_dens_std, K_cent_dens = field_dens / 3600.,\
            field_dens_std / 3600., K_cent_dens / 3600.
        rdp_points = np.array(rdp_points) / 3600.
        rdp_stddev = np.array(rdp_stddev) / 3600.
        coord2 = 'arcmin'
    else:
        coord2 = 'px'

    ax = plt.subplot(gs[2:4, 2:4])
    # Get max and min values in x,y
    x_min = max(min(radii) - (max(radii) / 20.), 0)
    x_max = min(max(radii) + (max(radii) / 20.), 3. * clust_rad)

    N_h = int(.5 * len(rdp_points))
    delta_total = (max(rdp_points) - field_dens)
    delta_backg = 0.1 * delta_total
    y_min = max((field_dens - delta_backg) -
                (max(rdp_points[:N_h]) - min(rdp_points[:N_h])) / 10., 0)
    y_max = max(rdp_points[:N_h]) + (
        max(rdp_points[:N_h]) - min(rdp_points[:N_h])) / 10.
    # Set plot limits
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    ax.minorticks_on()
    # Set axes labels
    plt.xlabel(r'radius $[{}]$'.format(coord2), fontsize=10)
    plt.ylabel(r"$\rho$ $[st/{}^{{2}}]$".format(coord2), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)
    ax.ticklabel_format(axis='y', style='sci', scilimits=(0, 0))

    ax.grid(b=True, which='major', color='gray', linestyle='--', lw=.5)
    # Legend texts
    kp_text = '3P' if flag_3pk_conver else '2P'
    r_frmt = '{:.0f}' if coord2 == 'px' else '{:.2f}'
    t1 = (r"$r_{{cl}}=$" + r_frmt + r"$\pm$" + r_frmt + r' $[{}]$').format(
        clust_rad, e_rad, coord2)
    texts = [
        '{} King profile'.format(kp_text),
        (r"$r_c=$" + r_frmt + r"$\pm$" + r_frmt + r" $[{}]$").format(
            core_rad, e_core, coord2),
        (r"$r_t=$" + r_frmt + r"$\pm$" + r_frmt + r" $[{}]$").format(
            tidal_rad, e_tidal, coord2)
    ]
    # Plot density profile
    ax.plot(radii, rdp_points, marker='o', ms=5, lw=1.5, zorder=3,
            label="RDP")
    # Plot Poisson error bars
    plt.errorbar(
        radii, rdp_points, yerr=rdp_stddev, fmt='none', ecolor='grey',
        lw=.8, zorder=1)
    # Plot background level.
    ax.hlines(y=field_dens, xmin=0, xmax=max(radii), color='k', ls='--',
              zorder=5)
    if not np.isnan(field_dens_std):
        ax.hlines(
            y=field_dens - field_dens_std, xmin=0, xmax=max(radii),
            color='k', ls=':', zorder=5)
        ax.hlines(
            y=field_dens + field_dens_std, xmin=0, xmax=max(radii),
            color='k', ls=':', zorder=5)
    # Plot radius.
    y_mid_point = (y_max + y_min) * .5
    ax.vlines(x=clust_rad, ymin=field_dens, ymax=y_mid_point, lw=1.5,
              color='r', label=t1, zorder=5)
    # Plot radius error zone.
    if e_rad > 0.:
        plt.axvspan((clust_rad - e_rad), (clust_rad + e_rad),
                    facecolor='grey', alpha=0.25)

    # Plot 3-P King profile.
    if flag_3pk_conver:
        # Plot curve.
        ax.plot(radii, kpf.three_params(
            radii, tidal_rad, K_cent_dens, core_rad, field_dens),
            'g--', label=texts[0], lw=2., zorder=3)
        # Plot r_t radius as an arrow. vline is there to show the label.
        ax.vlines(x=tidal_rad, ymin=field_dens, ymax=y_mid_point,
                  label=texts[2], color='g')
        # ax.arrow(tidal_rad, arr_y_up, 0., arr_y_dwn, fc="g", ec="g",
        #          head_width=head_w, head_length=head_l, zorder=4)
        # Plot r_c as a dashed line.
        ax.vlines(x=core_rad, ymin=field_dens, ymax=kpf.three_params(
            core_rad, tidal_rad, K_cent_dens, core_rad, field_dens),
            label=texts[1], color='g', linestyles=':', lw=2., zorder=5)
    # Plot 2-P King profile if 3-P was not found.
    elif flag_2pk_conver:
        # Plot curve.
        ax.plot(radii, kpf.two_params(
            radii, K_cent_dens, core_rad, field_dens), 'g--', label=texts[0],
            lw=2., zorder=3)
        # Plot r_c as a dashed line.
        ax.vlines(x=core_rad, ymin=field_dens, ymax=kpf.two_params(
            core_rad, K_cent_dens, core_rad, field_dens), label=texts[1],
            color='g', linestyles=':', lw=2., zorder=4)

    # get handles
    handles, labels = ax.get_legend_handles_labels()
    # use them in the legend
    ax.legend(handles, labels, loc='upper right', numpoints=2, fontsize=10)

    #
    # Log-log plot
    ax = plt.subplot(gs[2:4, 4:6])
    ax.minorticks_on()
    ax.grid(b=True, which='both', color='gray', linestyle='--', lw=.5)
    plt.xlabel(r'log(radius) $[{}]$'.format(coord2), fontsize=10)
    plt.ylabel(r"log($\rho$) $[st/{}^{{2}}]$".format(coord2), fontsize=10)
    ax.tick_params(axis='both', which='both', labelsize=8)

    ax.plot(radii, rdp_points, marker='o', ms=5, lw=1.5, zorder=5)
    ax.hlines(y=field_dens, xmin=min(radii), xmax=max(radii),
              color='k', ls='--', zorder=5)
    if not np.isnan(field_dens_std):
        ax.hlines(
            y=field_dens - field_dens_std, xmin=min(radii), xmax=max(radii),
            color='k', ls=':', zorder=5)
        ax.hlines(
            y=field_dens + field_dens_std, xmin=min(radii), xmax=max(radii),
            color='k', ls=':', zorder=5)
    ax.vlines(
        x=clust_rad, ymin=field_dens, ymax=y_mid_point, lw=1.5, color='r')
    if e_rad > 0.:
        plt.axvspan((clust_rad - e_rad), (clust_rad + e_rad),
                    facecolor='grey', alpha=0.25)
    # Plot 3-P King profile.
    if flag_3pk_conver:
        ax.plot(radii, kpf.three_params(
            radii, tidal_rad, K_cent_dens, core_rad, field_dens),
            'g--', lw=2., zorder=3)
        ax.vlines(x=core_rad, ymin=field_dens, ymax=kpf.three_params(
            core_rad, tidal_rad, K_cent_dens, core_rad, field_dens),
            color='g', linestyles=':', lw=2., zorder=5)
    # Plot 2-P King profile if 3-P was not found.
    elif flag_2pk_conver:
        ax.plot(radii, kpf.two_params(
            radii, K_cent_dens, core_rad, field_dens), 'g--', lw=2., zorder=3)
        ax.vlines(x=core_rad, ymin=field_dens, ymax=kpf.two_params(
            core_rad, K_cent_dens, core_rad, field_dens), color='g',
            linestyles=':', lw=2., zorder=4)

    ax.set_xscale('log')
    ax.set_yscale('log')


def pl_full_frame(
    gs, fig, project, x_offset, y_offset, x_name, y_name, coord, x_min, x_max,
    y_min, y_max, asp_ratio, kde_cent, clust_rad, frac_cl_area, x, y,
    st_sizes_arr, core_rad, e_core, tidal_rad, e_tidal, K_conct_par,
        flag_2pk_conver, flag_3pk_conver):
    '''
    x,y finding chart of full frame
    '''
    ax = plt.subplot(gs[4:6, 0:2])
    ax.set_aspect(aspect=asp_ratio)
    ax.set_title(
        r"$N_{{stars}}$={}, $A_{{fr}}$={:.0f}% (phot incomp)".format(
            len(x), 100. * frac_cl_area), fontsize=9)
    # Set plot limits
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    # If RA is used, invert axis.
    if coord == 'deg':
        ax.invert_xaxis()
    # Set axis labels
    plt.xlabel('{} ({})'.format(x_name, coord), fontsize=10)
    plt.ylabel('{} ({})'.format(y_name, coord), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Set minor ticks
    ax.minorticks_on()
    # Plot r_cl.
    circle = plt.Circle((kde_cent[0], kde_cent[1]), clust_rad, color='r',
                        fill=False, lw=1.5)
    fig.gca().add_artist(circle)
    if flag_3pk_conver is True:
        # Plot tidal radius.
        circle = plt.Circle(
            (kde_cent[0], kde_cent[1]), tidal_rad, color='g', fill=False,
            lw=1.5)
        fig.gca().add_artist(circle)
        # Plot core radius.
        if core_rad > 0:
            circle = plt.Circle(
                (kde_cent[0], kde_cent[1]), core_rad, color='g',
                fill=False, ls='dashed', lw=1.)
            fig.gca().add_artist(circle)
    elif flag_2pk_conver is True:
        # Plot core radius.
        if core_rad > 0:
            circle = plt.Circle(
                (kde_cent[0], kde_cent[1]), core_rad, color='g',
                fill=False, ls='dashed', lw=1.)
            fig.gca().add_artist(circle)
    # Add text box
    r_frmt = '{:.0f}' if coord == 'px' else '{:.5f}'
    if coord == 'deg' and project:
        x_cent = (kde_cent[0] / np.cos(np.deg2rad(kde_cent[1] + y_offset))) +\
            x_offset
    else:
        x_cent = kde_cent[0]
    t1 = (r'${}_{{c}} =$' + r_frmt + r'$\,{}$').format(x_name, x_cent, coord)
    t2 = (r'${}_{{c}} =$' + r_frmt + r'$\,{}$').format(
        y_name, kde_cent[1] + y_offset, coord)
    text = t1 + '\n' + t2
    ob = offsetbox.AnchoredText(text, pad=0.2, loc=2, prop=dict(size=10))
    ob.patch.set(alpha=0.85)
    ax.add_artist(ob)
    # Plot stars.
    plt.scatter(x, y, marker='o', c='black', s=st_sizes_arr)


def pl_zoom_frame(
    gs, fig, x_name, y_name, coord, x_zmin, x_zmax, y_zmin, y_zmax, cont_index,
        n_memb_i, kde_plot, x_data, y_data, st_sizes_arr, kde_cent, clust_rad):
    '''
    Zoom on x,y finding chart.
    '''
    ax = plt.subplot(gs[4:6, 2:4])
    # Force square plot.
    ax.set_aspect('equal')
    # Set plot limits.
    plt.xlim(x_zmin, x_zmax)
    plt.ylim(y_zmin, y_zmax)
    if coord == 'deg':
        # If RA is used, invert axis.
        ax.invert_xaxis()
    # Set axis labels
    plt.xlabel('{} ({})'.format(x_name, coord), fontsize=10)
    plt.ylabel('{} ({})'.format(y_name, coord), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Set minor ticks
    ax.minorticks_on()
    # Plot radius.
    circle = plt.Circle((kde_cent[0], kde_cent[1]), clust_rad, color='r',
                        fill=False, lw=1.5, zorder=5)
    # Stars inside the cluster
    N_in = 0
    for x, y in zip(*[x_data, y_data]):
        if np.sqrt((x - kde_cent[0])**2 + (y - kde_cent[1])**2) <= clust_rad:
            N_in += 1
    ax.set_title(
        (r"$N_{{r<r_{{cl}}}}$={}, $N_{{memb}}\approx${} [$CI = {:.2f}$] " +
         "(phot incomp)").format(N_in, n_memb_i, cont_index), fontsize=9)
    fig.gca().add_artist(circle)

    # Plot contour levels if it was obtained.
    if kde_plot:
        ext_range, x, y, k_pos = kde_plot
        # Number of contour lines depends on how large the cluster area is
        # compared with the area where the positional KDE was obtained.
        frac_xy = (ext_range[1] - ext_range[0]) / (2. * clust_rad)
        if frac_xy <= 1.5:
            c_lines = 5
        elif 1.5 < frac_xy <= 2.:
            c_lines = 10
        elif 2. < frac_xy <= 2.5:
            c_lines = 15
        elif 2.5 < frac_xy <= 3.:
            c_lines = 20
        elif 3 < frac_xy <= 3.5:
            c_lines = 25
        elif 3.5 < frac_xy:
            c_lines = 30

        kde = np.reshape(k_pos.T, x.shape)
        plt.contour(x, y, kde, c_lines, colors='b', linewidths=0.6)
    # Plot stars.
    plt.scatter(x_data, y_data, marker='o', c='black', s=st_sizes_arr,
                zorder=1)
    # Plot center.
    plt.scatter(kde_cent[0], kde_cent[1], color='r', s=40, lw=1.5,
                marker='x', zorder=5)


def pl_cl_fl_regions(
    gs, fig, x_name, y_name, coord, x_min, x_max, y_min, y_max, asp_ratio,
        kde_cent, clust_rad, field_regions_i, field_regions_rjct_i,
        cl_region_i, cl_region_rjct_i, flag_no_fl_regs_i):
    '''
    Cluster and field regions defined.
    '''
    ax = plt.subplot(gs[4:6, 4:6])
    ax.set_aspect(aspect=asp_ratio)
    # Set plot limits
    plt.xlim(x_min, x_max)
    plt.ylim(y_min, y_max)
    # If RA is used, invert axis.
    if coord == 'deg':
        ax.invert_xaxis()
    # Set axis labels
    plt.xlabel('{} ({})'.format(x_name, coord), fontsize=10)
    plt.ylabel('{} ({})'.format(y_name, coord), fontsize=10)
    ax.tick_params(axis='both', which='major', labelsize=8)

    # Set minor ticks
    ax.minorticks_on()
    ax.grid(b=True, which='both', color='gray', linestyle='--', lw=.5)
    # Radius
    circle = plt.Circle((kde_cent[0], kde_cent[1]), clust_rad,
                        color='k', fill=False)
    fig.gca().add_artist(circle)

    # Plot cluster region.
    if len(cl_region_rjct_i) > 0:
        plt.scatter(
            list(zip(*cl_region_rjct_i))[1], list(zip(*cl_region_rjct_i))[2],
            marker='o', c='red', s=8, edgecolors='w', lw=.2)
    plt.scatter(list(zip(*cl_region_i))[1], list(zip(*cl_region_i))[2],
                marker='o', c='red', s=8, edgecolors='w', lw=.2)

    N_flrg = 0
    if not flag_no_fl_regs_i:
        col0 = cycle(['DimGray', 'ForestGreen', 'maroon', 'RoyalBlue'])
        col1 = cycle(['DimGray', 'ForestGreen', 'maroon', 'RoyalBlue'])
        # Stars inside the field regions with accepted errors.
        for i, reg in enumerate(field_regions_i):
            fl_reg = list(zip(*reg))
            N_flrg += len(fl_reg[0])
            plt.scatter(fl_reg[1], fl_reg[2], marker='o',
                        c=next(col0), s=8, edgecolors='w', lw=.2)
        # Stars inside the field regions with rejected errors.
        for i, reg in enumerate(field_regions_rjct_i):
            if reg:
                fl_reg = list(zip(*reg))
                N_flrg += len(fl_reg[0])
                plt.scatter(fl_reg[1], fl_reg[2], marker='o',
                            c=next(col1), s=8, edgecolors='w', lw=.2)

    ax.set_title(r"$N_{{stars}}$={} (phot incomp); $N_{{fregs}}$={}".format(
        len(cl_region_i) + len(cl_region_rjct_i) + N_flrg,
        len(field_regions_i)), fontsize=9)


def plot(N, *args):
    '''
    Handle each plot separately.
    '''

    plt_map = {
        0: [pl_center, 'density positional chart'],
        1: [pl_knn_dens, 'kNN per-star densities'],
        2: [pl_field_dens, 'Field density'],
        3: [pl_rad_find, 'Radius estimation'],
        4: [pl_rad_dens, 'radial density function'],
        5: [pl_full_frame, 'full frame'],
        6: [pl_zoom_frame, 'zoomed frame'],
        7: [pl_cl_fl_regions, 'cluster and field regions defined']
    }

    fxn = plt_map.get(N, None)[0]
    if fxn is None:
        raise ValueError("  ERROR: there is no plot {}.".format(N))

    try:
        fxn(*args)
    except Exception:
        print("  WARNING: error when plotting {}".format(plt_map.get(N)[1]))
        import traceback
        print(traceback.format_exc())
