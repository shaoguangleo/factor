#!/usr/bin/python
"""
Script to apply a primary-beam correction to a mosaic image
"""
import lofar.parmdb as lp
import numpy as np
import sys, os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import argparse
from argparse import RawTextHelpFormatter

mpl.rc('font',size =8 )
mpl.rc('figure.subplot',left=0.05, bottom=0.05, right=0.95, top=0.95 )


def normalize(phase):
    """
    Normalize phase to the range [-pi, pi].
    """

    # Convert to range [-2*pi, 2*pi].
    out = np.fmod(phase, 2.0 * np.pi)

    # Convert to range [-pi, pi]
    out[out < -np.pi] += 2.0 * np.pi
    out[out > np.pi] -= 2.0 * np.pi

    return out


def scaletimes(t):

    t = t-t[0]

    t = t/3600.

    return t


def solplot_scalarphase(parmdb, imageroot, refstationi, plot_international=False):
    parmdbmtable = lp.parmdb(parmdb)
    soldict = parmdbmtable.getValuesGrid('*')
    names = parmdbmtable.getNames()

    'Gain:1:1:Phase:RS508HBA'
    stationsnames = np.array([name.split(':')[-1] for name in names])
    stationsnames = np.unique(stationsnames)
    if not plot_international:
        stationsnames = np.array([name for name in stationsnames if name[0] in ['C','R'] ])
    Nstat = len(stationsnames)

    refstation = stationsnames[refstationi]
    phase_ref = soldict['CommonScalarPhase:{s}'.format(s=refstation)]['values']
    times= soldict['CommonScalarPhase:{s}'.format(s=refstation)]['times']
    num_channels = phase_ref.shape[1]

    Nr = int(np.ceil(np.sqrt(Nstat)))
    Nc = int(np.ceil(np.float(Nstat)/Nr))

    for chan_indx in range(num_channels):
        f, ax = plt.subplots(Nr, Nc, sharex=True, sharey=True, figsize=(16,12))
        axs = ax.reshape((Nr*Nc,1))
        for istat, station in enumerate(stationsnames):
            phase = soldict['CommonScalarPhase:{s}'.format(s=station)]['values'][:, chan_indx]
            phase_ref_chan = phase_ref[:, chan_indx]

            # don't plot flagged phases
            phase = np.ma.masked_where(phase==0, phase)

            #try:
            if len(phase) > 1000:
                fmt = ','
            else:
                fmt = '.'
            ls= 'none'

            axs[istat][0].plot(times, normalize(phase-phase_ref_chan), color='b',  marker=fmt, ls=ls, label='CommonScalarPhase',mec='b')
            axs[istat][0].set_ylim(-3.2, 3.2)
            axs[istat][0].set_xlim(times.min(), times.max())
            axs[istat][0].set_title(station)

        f.savefig(imageroot+"_scalarphase_channel{}.png".format(chan_indx),dpi=100)
        plt.close(f)

    return


def solplot_tec(parmdb, imageroot, refstationi, plot_international=False, freq=None):
    parmdbmtable = lp.parmdb(parmdb)
    soldict = parmdbmtable.getValuesGrid('*')

    if freq is None:
        tfrange = parmdbmtable.getRange()
        print 'freqrange', tfrange[0:2]
        freq = np.average(tfrange[0:2])
        print 'freq', freq/1e6, 'MHz'

    names = parmdbmtable.getNames()

    'Gain:1:1:Phase:RS508HBA'
    stationsnames = np.array([name.split(':')[-1] for name in names])
    stationsnames = np.unique(stationsnames)
    if not plot_international:
        stationsnames = np.array([name for name in stationsnames if name[0] in ['C','R'] ])
    Nstat = len(stationsnames)

    refstation = stationsnames[refstationi]
    times = soldict['CommonScalarPhase:{s}'.format(s=refstation)]['times']
    times = scaletimes(times)
    phase_ref = soldict['CommonScalarPhase:{s}'.format(s=refstation)]['values']
    tec_ref = soldict['TEC:{s}'.format(s=refstation)]['values']
    num_channels = phase_ref.shape[1]

    Nr = int(np.ceil(np.sqrt(Nstat)))
    Nc = int(np.ceil(np.float(Nstat)/Nr))

    for chan_indx in range(num_channels):
        f, ax = plt.subplots(Nr, Nc, sharex=True, sharey=True, figsize=(16,12))
        axs = ax.reshape((Nr*Nc,1))
        ymin = 2
        ymax = 0
        for istat, station in enumerate(stationsnames):
            phase = soldict['CommonScalarPhase:{s}'.format(s=station)]['values'][:, chan_indx]
            tec = soldict['TEC:{s}'.format(s=station)]['values'][:, chan_indx]
            phase_ref_chan = phase_ref[:, chan_indx]
            tec_ref_chan = tec_ref[:, chan_indx]

            phase = np.ma.masked_where(phase==0, phase)
            if len(times) > 1000:
                fmt = ','
            else:
                fmt = '.'
            ls='none'

            phasep = phase - phase_ref_chan
            tecp =  -8.44797245e9*(tec - tec_ref_chan)/freq

            axs[istat][0].plot(times, np.mod(phasep+tecp +np.pi, 2*np.pi) - np.pi, color='b',  marker=fmt, ls=ls, label='Phase+TEC', mec='b')
            axs[istat][0].set_ylim(-np.pi, np.pi)
            axs[istat][0].set_xlim(times.min(), times.max())
            axs[istat][0].set_title(station)

        f.savefig(imageroot+"_tec_channel{}.png".format(chan_indx),dpi=100)
        plt.close(f)
    return


def solplot_clock(parmdb, imageroot, refstationi, plot_international=False):
    parmdbmtable = lp.parmdb(parmdb)
    soldict = parmdbmtable.getValuesGrid('*')
    names = parmdbmtable.getNames()

    'Gain:1:1:Phase:RS508HBA'
    stationsnames = np.array([name.split(':')[-1] for name in names])
    stationsnames = np.unique(stationsnames)
    if not plot_international:
        stationsnames = np.array([name for name in stationsnames if name[0] in ['C','R'] ])
    Nstat = len(stationsnames)

    refstation = stationsnames[refstationi]
    #phase_ref = soldict['Clock:{s}'.format(s=refstation)]['values']
    times= soldict['Clock:1:{s}'.format(s=refstation)]['times']

    Nr = int(np.ceil(np.sqrt(Nstat)))
    Nc = int(np.ceil(np.float(Nstat)/Nr))
    f, ax = plt.subplots(Nr, Nc, sharex=True, sharey=True, figsize=(16,12))
    axs = ax.reshape((Nr*Nc,1))
    ymin = 2
    ymax = 0
    for istat, station in enumerate(stationsnames):
        clock00 = soldict['Clock:0:{s}'.format(s=station)]['values']
        clock11 = soldict['Clock:1:{s}'.format(s=station)]['values']

        if len(clock00) > 0:
            ymax = max(np.max(clock00),ymax)
        if len(clock11) > 0:
            ymax = max(np.max(clock11),ymax)
        if len(clock00) > 0:
            ymin = min(np.min(clock00),ymin)
        if len(clock11) > 0:
            ymin = min(np.min(clock11),ymin)
        fmt = '.'
        ls='none'

        axs[istat][0].plot(times, clock00, color='b',  marker=fmt, ls=ls, label='Clock 0:0', mec='b')
        axs[istat][0].plot(times, clock11, color='g',  marker=fmt, ls=ls, label='Clock 1:1', mec='g')
        axs[istat][0].set_ylim(ymin, ymax)
        axs[istat][0].set_xlim(times.min(), times.max())
        axs[istat][0].set_title(station)

    f.savefig(imageroot+"_clock.png",dpi=100)
    return

def solplot_phase_phasors(parmdb, imageroot, refstationi, plot_international=False):
    parmdbmtable = lp.parmdb(parmdb)
    soldict = parmdbmtable.getValuesGrid('*')
    names = parmdbmtable.getNames()

    'Gain:1:1:Phase:RS508HBA'
    stationsnames = np.array([name.split(':')[-1] for name in names])
    stationsnames = np.unique(stationsnames)
    if not plot_international:
        stationsnames = np.array([name for name in stationsnames if name[0] in ['C','R'] ])
    Nstat = len(stationsnames)

    refstation = stationsnames[refstationi]
    phase11_ref = soldict['Gain:1:1:Phase:{s}'.format(s=refstation)]['values']
    phase00_ref = soldict['Gain:0:0:Phase:{s}'.format(s=refstation)]['values']
    times= soldict['Gain:1:1:Phase:{s}'.format(s=refstation)]['times']
    num_channels = phase11_ref.shape[1]

    Nr = int(np.ceil(np.sqrt(Nstat)))
    Nc = int(np.ceil(np.float(Nstat)/Nr))

    for chan_indx in range(num_channels):
        f, ax = plt.subplots(Nr, Nc, sharex=True, sharey=True, figsize=(16,12))
        axs = ax.reshape((Nr*Nc,1))
        for istat, station in enumerate(stationsnames):
            phase11 = soldict['Gain:1:1:Phase:{s}'.format(s=station)]['values'][:, chan_indx]
            phase00 = soldict['Gain:0:0:Phase:{s}'.format(s=station)]['values'][:, chan_indx]
            phase00_ref_chan = phase00_ref[:, chan_indx]
            phase11_ref_chan = phase11_ref[:, chan_indx]

            # don't plot flagged phases
            phase00 = np.ma.masked_where(phase00==0, phase00)
            phase11 = np.ma.masked_where(phase11==0, phase11)

            if len(times) > 1000:
                fmt = ','
            else:
                fmt = '.'

            ls='none'

            axs[istat][0].plot(times, normalize(phase00-phase00_ref_chan), color='b',  marker=fmt, ls=ls, label='Gain:0:0:Phase',mec='b')
            axs[istat][0].plot(times, normalize(phase11-phase11_ref_chan), color='g',  marker=fmt, ls=ls, label='Gain:1:1:Phase',mec='g')
            axs[istat][0].set_ylim(-3.2, 3.2)
            axs[istat][0].set_xlim(times.min(), times.max())
            axs[istat][0].set_title(station)

        f.savefig(imageroot+"_phase_channel{}.png".format(chan_indx),dpi=100)
        plt.close(f)
    return


def solplot_phase(parmdb, imageroot, refstationi, norm_amp_lim=False, median_amp=False, plot_international=False):

    parmdbmtable = lp.parmdb(parmdb)

    soldict = parmdbmtable.getValuesGrid('*')
    names = parmdbmtable.getNames()

    'Gain:1:1:Phase:RS508HBA'
    stationsnames = np.array([name.split(':')[-1] for name in names])
    stationsnames = np.unique(stationsnames)
    if not plot_international:
        stationsnames = np.array([name for name in stationsnames if name[0] in ['C','R'] ])
    Nstat = len(stationsnames)

    refstation = stationsnames[refstationi]
    times = soldict['Gain:1:1:Real:{s}'.format(s=refstation)]['times']
    times = scaletimes(times)

    real11_ref = soldict['Gain:1:1:Real:{s}'.format(s=refstation)]['values']
    real00_ref = soldict['Gain:0:0:Real:{s}'.format(s=refstation)]['values']
    imag11_ref = soldict['Gain:1:1:Imag:{s}'.format(s=refstation)]['values']
    imag00_ref = soldict['Gain:0:0:Imag:{s}'.format(s=refstation)]['values']
    num_channels = real11_ref.shape[1]

    valscorr00 = real00_ref +1.j*imag00_ref
    valscorr11 = real11_ref +1.j*imag11_ref

    phase00_ref = np.angle(valscorr00)
    phase11_ref = np.angle(valscorr11)

    Nr = int(np.ceil(np.sqrt(Nstat)))
    Nc = int(np.ceil(np.float(Nstat)/Nr))

    for chan_indx in range(num_channels):
        fp, axp = plt.subplots(Nr, Nc, sharex=True, sharey=True, figsize=(16,12))
        axsp = axp.reshape((Nr*Nc,1))
        for istat, station in enumerate(stationsnames):

            real11 = soldict['Gain:1:1:Real:{s}'.format(s=station)]['values'][:, chan_indx]
            real00 = soldict['Gain:0:0:Real:{s}'.format(s=station)]['values'][:, chan_indx]
            imag11 = soldict['Gain:1:1:Imag:{s}'.format(s=station)]['values'][:, chan_indx]
            imag00 = soldict['Gain:0:0:Imag:{s}'.format(s=station)]['values'][:, chan_indx]

            valscorr00 = real00 +1.j*imag00
            valscorr11 = real11 +1.j*imag11

            phase00_ref_chan = phase00_ref[:, chan_indx]
            phase11_ref_chan = phase11_ref[:, chan_indx]

            if len(np.unique(real11)) > 500:
                fmt = ','
            else:
                fmt = '.'
            ls='none'
            phase00 = np.angle(valscorr00)
            phase11 = np.angle(valscorr11)

            # don't plot flagged phases
            phase00 = np.ma.masked_where(phase00==0, phase00)
            phase11 = np.ma.masked_where(phase11==0, phase11)

            axsp[istat][0].plot(times, normalize(phase00-phase00_ref_chan), color='b',  marker=fmt, ls=ls, label='Gain:0:0:Phase',mec='b')
            axsp[istat][0].plot(times, normalize(phase11-phase11_ref_chan), color='g',  marker=fmt, ls=ls, label='Gain:1:1:Phase',mec='g')
            axsp[istat][0].set_ylim(-3.2, 3.2)
            axsp[istat][0].set_xlim(times.min(), times.max())
            axsp[istat][0].set_title(station)

        fp.savefig(imageroot+"_phase_channel{}.png".format(chan_indx),dpi=100)
    return


def solplot_amp(parmdb, imageroot, refstationi, norm_amp_lim=False, median_amp=False, plot_international=False):

    parmdbmtable = lp.parmdb(parmdb)
    soldict = parmdbmtable.getValuesGrid('*')
    names = parmdbmtable.getNames()

    'Gain:1:1:Phase:RS508HBA'
    stationsnames = np.array([name.split(':')[-1] for name in names])
    stationsnames = np.unique(stationsnames)
    if not plot_international:
        stationsnames = np.array([name for name in stationsnames if name[0] in ['C','R'] ])
    Nstat = len(stationsnames)

    refstation = stationsnames[refstationi]
    times = soldict['Gain:1:1:Real:{s}'.format(s=refstation)]['times']
    times = scaletimes(times)

    real11_ref = soldict['Gain:1:1:Real:{s}'.format(s=refstation)]['values']
    real00_ref = soldict['Gain:0:0:Real:{s}'.format(s=refstation)]['values']
    imag11_ref = soldict['Gain:1:1:Imag:{s}'.format(s=refstation)]['values']
    imag00_ref = soldict['Gain:0:0:Imag:{s}'.format(s=refstation)]['values']
    num_channels = real11_ref.shape[1]

    valscorr00 = real00_ref +1.j*imag00_ref
    valscorr11 = real11_ref +1.j*imag11_ref

    amp00_ref = np.abs(valscorr00)
    amp11_ref = np.abs(valscorr11)

    Nr = int(np.ceil(np.sqrt(Nstat)))
    Nc = int(np.ceil(np.float(Nstat)/Nr))

    for chan_indx in range(num_channels):
        fa, axa = plt.subplots(Nr, Nc, sharex=True, sharey=True, figsize=(16,12))
        axsa = axa.reshape((Nr*Nc,1))
        ymin = 2
        ymax = 0
        for istat, station in enumerate(stationsnames):

            real11 = soldict['Gain:1:1:Real:{s}'.format(s=station)]['values'][:, chan_indx]
            real00 = soldict['Gain:0:0:Real:{s}'.format(s=station)]['values'][:, chan_indx]
            imag11 = soldict['Gain:1:1:Imag:{s}'.format(s=station)]['values'][:, chan_indx]
            imag00 = soldict['Gain:0:0:Imag:{s}'.format(s=station)]['values'][:, chan_indx]

            valscorr00 = real00 +1.j*imag00
            valscorr11 = real11 +1.j*imag11

            amp00_ref_chan = amp00_ref[:, chan_indx]
            amp11_ref_chan = amp11_ref[:, chan_indx]

            if len(np.unique(real11)) > 500:
                fmt = ','
            else:
                fmt = '.'
            ls='none'
            amp00 = np.abs(valscorr00)
            amp11 = np.abs(valscorr11)

            ## for y scale: check max and min values
            amp00m = np.ma.masked_where(amp00==1, amp00).compressed()
            amp11m = np.ma.masked_where(amp11==1, amp11).compressed()

            if len(amp00m) > 0:
                ymax = max(np.max(amp00m),ymax)
            if len(amp11m) > 0:
                ymax = max(np.max(amp11m),ymax)
            if len(amp00m) > 0:
                ymin = min(np.min(amp00m),ymin)
            if len(amp11m) > 0:
                ymin = min(np.min(amp11m),ymin)

            # don't plot flagged amplitudes
            amp00 = np.ma.masked_where(amp00==1, amp00)
            amp11 = np.ma.masked_where(amp11==1, amp11)

            axsa[istat][0].plot(times, amp00, color='b', marker=fmt, ls=ls, label='Gain:0:0:Amp',mec='b')
            axsa[istat][0].plot(times, amp11, color='g', marker=fmt, ls=ls, label='Gain:1:1:Amp',mec='g')
            if median_amp:
                median_amp00 = np.median(amp00)
                median_amp11 = np.median(amp11)

                axsa[istat][0].plot([times[0], times[-1]], [median_amp00,median_amp00], color='b', label='<Gain:0:0:Amp>')
                axsa[istat][0].plot([times[0], times[-1]], [median_amp11,median_amp11], color='g', label='<Gain:1:1:Amp>')

            if norm_amp_lim:
                axsa[istat][0].set_ylim(0,2 )
            else:
                axsa[istat][0].set_ylim(ymin,ymax)

            axsa[istat][0].set_xlim(times.min(), times.max())
            axsa[istat][0].set_title(station)

        fa.savefig(imageroot+"_amp_channel{}.png".format(chan_indx),dpi=100)
    return


def main(parmdb, imageroot, freq=150.0, plot_tec=True, plot_amp=True,
    plot_phase=True, plot_scalarphase=False, median_amp=False, norm_amp_lim=False,
    plot_clock=False, phasors=False, plot_international=False, refstation=0):
    """
    Make various plots
    """
    if freq != 0:
        reffreq = float(freq) * 1e6
    else:
        reffreq = None

    if plot_scalarphase:
        solplot_scalarphase(parmdb, imageroot, refstation, plot_international=plot_international)

    if plot_phase:
        if phasors:
            solplot_phase_phasors(parmdb, imageroot, refstation, plot_international=plot_international)
        else:
            solplot_phase(parmdb, imageroot, refstation, plot_international=plot_international)

    if plot_amp:
        solplot_amp(parmdb, imageroot, refstation, norm_amp_lim=norm_amp_lim, median_amp=median_amp, plot_international=plot_international)

    if plot_tec:
        solplot_tec(parmdb, imageroot, refstation, plot_international=plot_international, freq=reffreq)

    if plot_clock:
        solplot_clock(parmdb, imageroot, refstation, plot_international=plot_international)


if __name__ == "__main__":
    descriptiontext = "Plot selfcal solutions.\n"
    parser = argparse.ArgumentParser(description=descriptiontext, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-c', '--clock', dest='clock', action="store_true", default=False, help="plot clock solutions")
    parser.add_argument('-a', '--amp', dest='amp', action="store_true", default=False, help="plot amp solutions")
    parser.add_argument('-p', '--phase', dest='phase', action="store_true", default=False, help="plot phase solutions")
    parser.add_argument('--phasors', dest='phasors', action="store_true", default=False, help="set phase-only")
    parser.add_argument('--freq', dest='freq', default=0, help="reference frequency for TEC plotting in MHz")
    parser.add_argument('-t','--tec', dest='tec', action="store_true", default=False, help="set tec-mode plotting on and plot phase (TEC+scalarpahse)")
    parser.add_argument('-s', '--scalarphase', dest='scalarphase', action="store_true", default=False, help="plot scalarphase solutions")
    parser.add_argument('-n', '--norm-amplitude-limits', dest='norm_amp_lim', action="store_true", default=False, help="plot amps between 0 and 2")
    parser.add_argument('-m', '--plot-median-amplitude', dest='median_amp', action="store_true", default=False, help="plot median amplitudes")
    parser.add_argument('-i', '--plot-international-stations', dest='plot_international', action="store_true", default=False, help="plot international stations")
    parser.add_argument('-r', '--refstation', dest='refstation', default=0, help="given reference station (integer)")
    parser.add_argument('parmdb', help="Name of solution parmdb")
    parser.add_argument('imageroot', help="Root name for output images")

    args = parser.parse_args()
    main(args.parmdb, args.imageroot, freq=args.freq, plot_tec=args.tec, plot_amp=args.amp,
        plot_phase=args.phase, plot_scalarphase=args.scalarphase, median_amp=args.median_amp,
        norm_amp_lim=args.norm_amp_lim, plot_clock=args.clock, phasors=args.phasors,
        plot_international=args.plot_international, refstation=args.refstation)
