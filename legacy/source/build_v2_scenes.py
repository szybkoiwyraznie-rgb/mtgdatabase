import numpy as np
import soundfile as sf
from scipy import signal
import subprocess
import os

sr = 44100

def load_resample(path, target_sr=44100):
    data, orig_sr = sf.read(path)
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    if orig_sr != target_sr:
        new_len = int(len(data) * target_sr / orig_sr)
        data = signal.resample(data, new_len)
    return data

# =========================================================================
# BUILD SCENE A (V2): Dunland Cliff / Uruk-hai / Crebain / Sword
# =========================================================================
dur_a = 5.6
samples_a = int(sr * dur_a)
t_a = np.linspace(0, dur_a, samples_a, endpoint=False)
L_a = np.zeros(samples_a)
R_a = np.zeros(samples_a)

# 1. Atmospheric wind & cinematic sub-drone (as liked by user)
f0 = 44.0
sub_a = 0.5 * np.sin(2 * np.pi * f0 * t_a) + 0.25 * np.sin(2 * np.pi * (f0*1.5) * t_a)
drone_env = np.clip(t_a / 2.0, 0.2, 1.0)
drone_env[-int(sr*0.9):] *= np.linspace(1.0, 0.0, int(sr*0.9))
sub_a = np.tanh(sub_a * drone_env * 1.5) * 0.45

# Wind
b_lp, a_lp = signal.butter(2, 380 / (sr/2), btype='low')
wind_a = signal.lfilter(b_lp, a_lp, np.random.normal(0, 1, samples_a))
wind_a = wind_a / np.max(np.abs(wind_a)) * 0.35 * np.sin(np.pi * t_a / dur_a)**0.5

L_a += sub_a * 0.9 + wind_a * 0.8
R_a += sub_a * 0.9 + wind_a * 1.1

# 2. Torch ignite & crackle (around 0.8s - 2.6s)
t_torch = int(sr * 0.8)
torch_len = int(sr * 2.0)
tt = np.linspace(0, 2.0, torch_len)
b_bp, a_bp = signal.butter(2, [200 / (sr/2), 950 / (sr/2)], btype='band')
torch_whoosh = signal.lfilter(b_bp, a_bp, np.random.normal(0, 1, torch_len)) * np.sin(np.pi * np.clip(tt/0.8, 0, 1))**2 * np.exp(-tt*1.2) * 1.6
L_a[t_torch:t_torch+torch_len] += torch_whoosh * 0.7
R_a[t_torch:t_torch+torch_len] += torch_whoosh * 0.5

# 3. REAL Wing Flaps (using organic whoosh from Gravity Sound)
whoosh_raw = load_resample('/home/user/real_stems/whoosh_flap.mp3', sr)
whoosh_cut = whoosh_raw[:int(sr * 0.55)]
# Two quick wing flaps at 2.0s and 2.35s
for flap_t, pan in [(1.9, -0.3), (2.25, -0.1)]:
    idx = int(flap_t * sr)
    flen = min(len(whoosh_cut), samples_a - idx)
    L_a[idx:idx+flen] += whoosh_cut[:flen] * (0.8 - pan * 0.3) * 1.2
    R_a[idx:idx+flen] += whoosh_cut[:flen] * (0.8 + pan * 0.3) * 1.2

# 4. REAL Raven from Yellowstone National Park
raven_raw = load_resample('/home/user/real_stems/nps_raven.mp3', sr)
# Extract clean loud call around 7.7s to 9.2s
raven_call = raven_raw[int(sr * 7.75):int(sr * 9.2)]
# Pitch shift down 12% (larger, more menacing war raven)
raven_call = signal.resample(raven_call, int(len(raven_call) * 1.14))
# Normalize
raven_call = raven_call / (np.max(np.abs(raven_call)) + 1e-4) * 0.95

t_raven = int(sr * 2.5)
rlen = min(len(raven_call), samples_a - t_raven)
L_a[t_raven:t_raven+rlen] += raven_call[:rlen] * 1.15
R_a[t_raven:t_raven+rlen] += raven_call[:rlen] * 0.95

# 5. REAL Sword Draw (Gravity Sound Sword 12 + Swipe)
sword_raw = load_resample('/home/user/real_stems/sword_draw.mp3', sr)
sword_swipe = load_resample('/home/user/real_stems/sword_swipe.mp3', sr)
# Normalize sword
sword_raw = sword_raw / np.max(np.abs(sword_raw)) * 0.95

t_sword = int(sr * 3.7)
slen = min(len(sword_raw), samples_a - t_sword)
L_a[t_sword:t_sword+slen] += sword_raw[:slen] * 1.1
R_a[t_sword:t_sword+slen] += sword_raw[:slen] * 1.3

# Final mix normalization
mix_a = np.column_stack([L_a, R_a])
mix_a = mix_a / (np.max(np.abs(mix_a)) + 1e-4) * 0.92
sf.write('/tmp/raw_scene_a_v2.wav', mix_a, sr)

# Process with canyon echo via ffmpeg
subprocess.run([
    '/home/user/bin/ffmpeg', '-y', '-i', '/tmp/raw_scene_a_v2.wav',
    '-af', 'aecho=0.85:0.7:130|250:0.25|0.18,acompressor=threshold=-13dB:ratio=3.8:attack=15:release=200',
    '/home/user/sfx_demos/event_a_v2_natural_stems.mp3'
], check=True)
print("Scene A V2 built!")

# =========================================================================
# BUILD SCENE B (V2): Zendikar Flooded Canyon / Baloth / Grizzly Growl
# =========================================================================
dur_b = 5.4
samples_b = int(sr * dur_b)
t_b = np.linspace(0, dur_b, samples_b, endpoint=False)
L_b = np.zeros(samples_b)
R_b = np.zeros(samples_b)

# 1. Cavern ambiance & water flow bed
b_w, a_w = signal.butter(2, [70 / (sr/2), 600 / (sr/2)], btype='band')
water_bed = signal.lfilter(b_w, a_w, np.cumsum(np.random.normal(0, 1, samples_b)))
water_bed = water_bed / np.max(np.abs(water_bed)) * 0.25

# High cave drips
for dt in [0.35, 1.1, 2.9, 4.3]:
    d_idx = int(dt * sr)
    d_len = int(sr * 0.07)
    if d_idx + d_len < samples_b:
        t_d = np.linspace(0, 0.07, d_len)
        f_drip = np.linspace(2400, 800, d_len)
        drip_snd = np.sin(2 * np.pi * f_drip * t_d) * np.exp(-t_d * 50)
        L_b[d_idx:d_idx+d_len] += drip_snd * 0.35
        R_b[d_idx:d_idx+d_len] += drip_snd * 0.2

L_b += water_bed * 0.75
R_b += water_bed * 0.85

# 2. Eldrazi otherworldly dissonant drone
f_eld = 68.0
drone_e = (0.35 * np.sin(2 * np.pi * f_eld * t_b) +
           0.25 * np.sin(2 * np.pi * (f_eld * 1.414) * t_b) +
           0.18 * np.sin(2 * np.pi * (f_eld * 2.828) * t_b + 0.6 * np.sin(2 * np.pi * 3.2 * t_b)))
e_env = 0.35 + 0.45 * (1 - np.cos(np.pi * t_b / dur_b))
drone_e *= e_env * 0.38
L_b += drone_e * 0.85
R_b += drone_e * 1.1

# 3. REAL Footsteps & Water Eruption (Heavy Baloth Stomps)
gravel_raw = load_resample('/home/user/real_stems/gravel_feet.mp3', sr)
splash_raw = load_resample('/home/user/real_stems/splash.wav', sr)

# Extract 2 distinct real rock crunches
crunch1 = gravel_raw[int(sr * 1.2):int(sr * 1.8)]
crunch2 = gravel_raw[int(sr * 3.4):int(sr * 4.0)]

# Extract real water splashes
sp1 = splash_raw[int(sr * 3.2):int(sr * 4.6)]
sp2 = splash_raw[int(sr * 25.2):int(sr * 26.8)]

# Heavy sub impact generator (the visceral chest-thumping weight of a 5-ton beast)
def beast_impact(intensity=1.0):
    t_imp = np.linspace(0, 0.35, int(sr * 0.35))
    freq = np.linspace(80, 28, len(t_imp))
    sub = np.sin(2 * np.pi * freq * t_imp) * np.exp(-t_imp * 12) * intensity
    return np.tanh(sub * 1.6) * 0.85

# Step 1 at 1.15s
idx1 = int(1.15 * sr)
sub1 = beast_impact(1.2)
L_b[idx1:idx1+len(sub1)] += sub1 * 0.9
R_b[idx1:idx1+len(sub1)] += sub1 * 0.7
c1_len = min(len(crunch1), samples_b - idx1)
L_b[idx1:idx1+c1_len] += crunch1[:c1_len] * 0.7
R_b[idx1:idx1+c1_len] += crunch1[:c1_len] * 0.5
sp1_len = min(len(sp1), samples_b - idx1)
L_b[idx1:idx1+sp1_len] += sp1[:sp1_len] * 1.3
R_b[idx1:idx1+sp1_len] += sp1[:sp1_len] * 1.0

# Step 2 at 2.5s (heavier)
idx2 = int(2.5 * sr)
sub2 = beast_impact(1.4)
L_b[idx2:idx2+len(sub2)] += sub2 * 0.8
R_b[idx2:idx2+len(sub2)] += sub2 * 1.0
c2_len = min(len(crunch2), samples_b - idx2)
L_b[idx2:idx2+c2_len] += crunch2[:c2_len] * 0.6
R_b[idx2:idx2+c2_len] += crunch2[:c2_len] * 0.8
sp2_len = min(len(sp2), samples_b - idx2)
L_b[idx2:idx2+sp2_len] += sp2[:sp2_len] * 1.1
R_b[idx2:idx2+sp2_len] += sp2[:sp2_len] * 1.5

# 4. REAL Grizzly Bear Vocal (Yellowstone NPS) -> Pitched down into a Baloth
grizzly_raw = load_resample('/home/user/real_stems/nps_grizzly.mp3', sr)
# Extract clean heavy roar/grunt at 2.3s - 4.2s
grizzly_cut = grizzly_raw[int(sr * 2.2):int(sr * 3.8)]
# Pitch down by 25% (makes it sound like a colossal prehistoric creature)
baloth_roar = signal.resample(grizzly_cut, int(len(grizzly_cut) * 1.28))
baloth_roar = baloth_roar / np.max(np.abs(baloth_roar)) * 0.85

t_roar = int(sr * 1.6)
rlen = min(len(baloth_roar), samples_b - t_roar)
L_b[t_roar:t_roar+rlen] += baloth_roar[:rlen] * 0.95
R_b[t_roar:t_roar+rlen] += baloth_roar[:rlen] * 0.8

# Final mix normalization
mix_b = np.column_stack([L_b, R_b])
mix_b = mix_b / (np.max(np.abs(mix_b)) + 1e-4) * 0.92
sf.write('/tmp/raw_scene_b_v2.wav', mix_b, sr)

# Process with cave reverb via ffmpeg
subprocess.run([
    '/home/user/bin/ffmpeg', '-y', '-i', '/tmp/raw_scene_b_v2.wav',
    '-af', 'aecho=0.85:0.75:160|300:0.35|0.22,acompressor=threshold=-12dB:ratio=3.5:attack=15:release=220',
    '/home/user/sfx_demos/event_b_v2_natural_stems.mp3'
], check=True)
print("Scene B V2 built!")
