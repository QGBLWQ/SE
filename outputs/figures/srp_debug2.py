"""SRP-PHAT debug 2 — check individual angles"""
import numpy as np
from scipy.signal import butter, filtfilt

fs=16000; c=343; d=0.04; th=30; thr=np.radians(th)
dur=0.1; t=np.arange(0,dur,1/fs); N=len(t); Nfft=512

np.random.seed(42)
src=np.random.randn(N)
b,a=butter(4,[400/(fs/2),4000/(fs/2)],btype='band')
src=filtfilt(b,a,src); src/=np.std(src)

def ds(sig,tau):
    ss=tau*fs; si=int(np.floor(ss)); sf=ss-si
    out=np.roll(sig,-si)
    if sf!=0: out=(1-abs(sf))*out+abs(sf)*np.roll(out,-1)
    return out

s0=ds(src,0)+0.05*np.random.randn(N)
s1=ds(src,-d*np.sin(thr)/c)+0.05*np.random.randn(N)

# Use rfft (positive freqs only)
start=N//4; seg0,seg1=s0[start:start+Nfft],s1[start:start+Nfft]
X0=np.fft.rfft(seg0); X1=np.fft.rfft(seg1)
fr=np.fft.rfftfreq(Nfft,1/fs)
mask=(fr>400)&(fr<4500)
fm=fr[mask]

G=X0*np.conj(X1); Gph=G/(np.abs(G)+1e-8)

for th_cand in [30, -30, 25, 35]:
    r=np.radians(th_cand)
    tau_t=d*np.sin(r)/c
    # Try BOTH sign conventions
    p_pos=np.exp(1j*2*np.pi*fm*tau_t)
    p_neg=np.exp(-1j*2*np.pi*fm*tau_t)
    s_pos=np.real(np.sum(Gph[mask]*p_pos))
    s_neg=np.real(np.sum(Gph[mask]*p_neg))
    print(f"θ={th_cand:3d}°:  pos_sign={s_pos:8.1f}  neg_sign={s_neg:8.1f}")
