import sys
sys.path.insert(0, '/root/glosim2/')
from libmatch.soap import get_Soaps
from libmatch.utils import get_soapSize, get_spkit, get_spkitMax, ase2qp, qp2ase
import numpy as np


def get_frame_slices(frames, nocenters=None):
    slices = []
    strides = [0]
    for frame in frames:
        numbers = frame.get_atomic_numbers()
        aa = []
        if nocenters is not None:
            for nn in numbers:
                if nn not in nocenters:
                    aa.append(nn)
        else:
            aa = numbers
            # numbers = np.setdiff1d(numbers,nocenters)
        strides.append(len(aa))
    strides = np.cumsum(strides)
    for st, nd in zip(strides[:-1], strides[1:]):
        slices.append(slice(st, nd))
    return slices, strides


def get_fingerprints(frames, soap_param):
    fings = get_Soaps(frames, **soap_param)
    slices, strides = get_frame_slices(
        frames, nocenters=soap_param['nocenters'])
    ii = 0
    Nenv = strides[-1]
    Nsoap = get_Nsoap(spkitMax=soap_param['spkitMax'], nmax=soap_param['nmax'],
                      lmax=soap_param['lmax'])
    soaps = np.zeros((Nenv, Nsoap))
    for frame in fings:
        for key, center in frame.iteritems():
            soaps[ii] = center
            ii += 1
    return soaps, slices, strides


def get_chunck(slices, chunk_len):
    N = len(slices)
    Nchunk = N // chunk_len

    if Nchunk == 1 and N % chunk_len == 0:
        return [slice(N)], [slices], [slices]

    frame_ids = [slice(it*chunk_len, (it+1)*chunk_len) for it in range(Nchunk)]
    if N % chunk_len != 0:
        frame_ids.append(slice((Nchunk)*chunk_len, (N)))

    chuncks_global = [
        [slices[ii] for ii in range(it*chunk_len, (it+1)*chunk_len)]
        for it in range(Nchunk)]
    if N % chunk_len != 0:
        chuncks_global.append([slices[ii]
                               for ii in range((Nchunk)*chunk_len, (N))])

    chuncks = []
    for it in range(Nchunk):
        st_ref = slices[it*chunk_len].start
        aa = []
        for ii in range(it*chunk_len, (it+1)*chunk_len):
            st, nd = slices[ii].start-st_ref, slices[ii].stop-st_ref
            aa.append(slice(st, nd))
        chuncks.append(aa)

    if N % chunk_len != 0:
        aa = []
        st_ref = slices[Nchunk*chunk_len].start
        for ii in range((Nchunk)*chunk_len, N):
            st, nd = slices[ii].start-st_ref, slices[ii].stop-st_ref
            aa.append(slice(st, nd))
        chuncks.append(aa)

    return frame_ids, chuncks, chuncks_global


def get_Nsoap(spkitMax, nmax, lmax):
    Nsoap = 0
    for sp1 in spkitMax:
        for sp2 in spkitMax:
            if sp1 == sp2:
                Nsoap += nmax*(nmax+1)*(lmax+1) / 2
            elif sp1 > sp2:
                Nsoap += nmax**2*(lmax+1)
    return Nsoap + 1


def estimate_cost(frames, soap_param):
    """Estimates size of soap vector in GB"""
    Ncenter = 0
    for f in frames:
        numbers = f.get_atomic_numbers()
        for sp in numbers:
            if sp not in soap_param['nocenters']:
                Ncenter += 1
    sz = Nsoap * Ncenter * 8 / 1e9
    return sz
