import math
G=6.67430e-11; M=5.9722e24; R=6.371e6
KT=4.184e12; MT=4.184e15
hiro=15*KT; tsar=50*MT
Ubind_uniform=3*G*M**2/(5*R)
Ubind_prem=2.49e32     # PREM-based, Chao 2014 / Wikipedia
atm_m=5.1480e18        # Trenberth & Smith 2005
vesc=math.sqrt(2*G*M/R)
Eatm=atm_m*G*M/R       # lift every kg from surface radius to infinity (upper-level gas needs slightly less)
arsenal_Mt=2030        # FAS 2023 data via UN doc (incl. retired), used as upper-ish estimate for 2026 (12,187 warheads FAS 2026 vs 12,520 in 2023)
arsenal_active_Mt=1700 # active-service estimate quoted on r/nuclearweapons (low confidence) - not used for headline
arsenal=arsenal_Mt*MT
peak=25000*MT          # ICNND: Cold War peak ~25,000 Mt (1974)
chic=1e23
S=1361; Pearth=S*math.pi*R**2
Lsun=3.828e26
yr=365.25*86400
def f(n,x): print(f"{n:48s} {x:.4g}")
f('Hiroshima J',hiro); f('Tsar Bomba J',tsar)
f('Earth binding uniform J',Ubind_uniform); f('Earth binding PREM J',Ubind_prem)
f('v_escape m/s',vesc); f('atm mass kg',atm_m); f('atm escape energy J',Eatm)
f('arsenal J (2030 Mt)',arsenal)
print('--- Hiroshimas')
f('Hiroshimas for Earth (uniform)',Ubind_uniform/hiro); f('Hiroshimas for Earth (PREM)',Ubind_prem/hiro)
f('Tsar Bombas for Earth (uniform)',Ubind_uniform/tsar)
f('Hiroshimas for atmosphere',Eatm/hiro); f('Tsar Bombas for atmosphere',Eatm/tsar)
f('Hiroshimas in arsenal',arsenal/hiro); f('Tsar-equivalents in arsenal',arsenal/tsar)
print('--- ratios')
f('Earth binding / arsenal',Ubind_uniform/arsenal); f('PREM binding / arsenal',Ubind_prem/arsenal)
f('atm energy / arsenal',Eatm/arsenal)
f('Earth binding / Cold-War peak arsenal',Ubind_uniform/peak); f('atm / Cold-War peak',Eatm/peak)
f('Earth binding / (10x arsenal)',Ubind_uniform/(10*arsenal))
f('arsenal / Earth binding',arsenal/Ubind_uniform); f('arsenal / atm energy',arsenal/Eatm)
print('--- analogies')
f('years of 1 Hiroshima/s for Earth',Ubind_uniform/hiro/yr)
f('same / age of universe 13.8e9',Ubind_uniform/hiro/yr/13.8e9)
f('Hiroshimas per second since Big Bang (13.8Gyr)',Ubind_uniform/hiro/(13.8e9*yr))
f('Sun output seconds = Earth binding',Ubind_uniform/Lsun/1.0)
f('Sun output days = Earth binding',Ubind_uniform/Lsun/86400)
f('Sun output seconds = atm energy',Eatm/Lsun)
f('Sunlight on Earth W',Pearth)
f('arsenal in seconds of sunlight on Earth',arsenal/Pearth)
f('Chicxulub / arsenal',chic/arsenal); f('Chicxulub (3e23)/arsenal',3e23/arsenal)
f('Earth binding / Chicxulub',Ubind_uniform/chic); f('Earth binding / Chicxulub 3e23',Ubind_uniform/3e23)
f('Chicxulub in Hiroshimas',chic/hiro); f('Chicxulub 3e23 in Hiroshimas',3e23/hiro)
f('atm / Chicxulub',Eatm/chic)
print('--- human scale: arsenal as fraction of Earth binding, if Earth = Everest-ish? use mass analogy')
frac=arsenal/Ubind_uniform
f('if Earth binding = 1 Moscow-Paris? ; fraction',frac)
# analogy: Earth binding = distance Earth-Sun (1.496e11 m) -> arsenal = ? m
f('if Earth binding=Earth-Sun distance, arsenal is (mm)',frac*1.496e11*1000)
# analogy: Earth binding = all water of Earth's oceans (1.335e21 kg ~ 1.335e21 L) -> arsenal in litres
f('if Earth binding=all oceans(1.335e21 L), arsenal litres',frac*1.335e21)
f('same in teaspoons(5mL)',frac*1.335e21/0.005)
# analogy: atmosphere: if atm energy = 1 year, arsenal = seconds
f('if atm energy = 1 year, arsenal = seconds',Eatm and arsenal/Eatm*yr)
f('if Earth binding = 1 year of seconds, arsenal = s',frac*yr)
