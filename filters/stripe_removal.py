from __future__ import (absolute_import, division, print_function)
# Remove stripes in sinograms / ring artefacts in reconstructed volume
import helper as h


def cli_register(parser):
    parser.add_argument(
        "--pre-stripe-removal-wf",
        nargs='*',
        required=False,
        type=str,
        help="Stripe removal using wavelett-fourier method. Available parameters:\n\
        level (int, optional) Number of discrete wavelet transform levels.\n\
        wname (str, optional) Type of the wavelet filter. 'haar', 'db5', 'sym5', etc.\n\
        sigma (float, optional) Damping parameter in Fourier space.\n\
        pad (bool, optional) If True, extend the size of the sinogram by padding with zeros."
    )

    parser.add_argument(
        "--pre-stripe-removal-ti",
        nargs='*',
        required=False,
        type=str,
        help="Stripe removal using Titarenko's approach. Available parameters:\n\
              nblock (int, optional) Number of blocks.\n\
              alpha (int, optional) Damping factor.")

    parser.add_argument(
        "--pre-stripe-removal-sf",
        nargs='*',
        required=False,
        type=str,
        help="Stripe removal using smoothing-filter method. Available parameters:\n\
        size (int, optional) Size of the smoothing filter.")

    return parser


def gui_register(par):
    raise NotImplementedError("GUI doesn't exist yet")


def methods():
    return [
        'wf', 'wavelet-fourier', 'ti', 'titarenko', 'sf', 'smoothing-filter'
    ]


def execute(data, wf, ti, sf, cores=None, chunksize=None):
    # get the first one, the rest will be processed
    msg = "Starting removal of stripes/ring artifacts using the method '{0}'..."
    if wf is not None:
        h.pstart(msg.format('Wavelett-Fourier'))
        data = _wf(data, wf, cores, chunksize)
        h.pstop("Finished removal of stripes/ring artifacts.")

    elif ti is not None:
        h.pstart(msg.format('Titarenko'))
        data = _ti(data, ti, cores, chunksize)
        h.pstop("Finished removal of stripes/ring artifacts.")

    elif sf is not None:
        h.pstart(msg.format('Smoothing-Filter'))
        data = _sf(data, sf, cores, chunksize)
        h.pstop("Finished removal of stripes/ring artifacts.")

    return data


def _wf(data, params, cores, chunksize):
    from recon.tools import importer
    tomopy = importer.do_importing('tomopy')
    kwargs = dict(
        level=None,
        wname=u'db5',
        sigma=2,
        pad=True,
        ncore=cores,
        nchunk=chunksize)
    params = dict(map(lambda p: p.split('='), params))

    kwargs['level'] = int(params.get('level')) if params.get('level') else None
    kwargs['wname'] = str(
        params.get('wname')) if params.get('wname') else 'db5'
    kwargs['sigma'] = int(params.get('sigma')) if params.get('sigma') else 2
    kwargs['pad'] = bool(params.get('pad')) if params.get('pad') else True

    return tomopy.prep.stripe.remove_stripe_fw(data, **kwargs)
    # TODO find where this is from? iprep?
    # data = iprep.filters.remove_stripes_ring_artifacts(
    #     data, 'wavelet-fourier')


def _ti(data, params, cores, chunksize):
    data = tomopy.prep.stripe.remove_stripe_fw(data)


def _sf(data, params, cores, chunksize):
    data = tomopy.prep.stripe.remove_stripe_sf(data)
