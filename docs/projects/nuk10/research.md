# nuk10 research

Question (owner message pt141u): what yield does a nuclear explosion need to split the Earth, how many Hiroshima-size explosions is that, and is all the nuclear weaponry of all countries enough to split the Earth and destroy the atmosphere?

## Definitions
- "Split the Earth" = supply the gravitational binding energy, i.e. the energy needed to disperse all the mass to infinity. For a uniform sphere U = 3GM^2/(5R). G = 6.674e-11, M = 5.972e24 kg, R = 6.371e6 m -> U = 2.242e32 J. With the real (PREM) density profile U = 2.49e32 J (Wikipedia, Gravitational binding energy; Chao 2014 for the order of magnitude). A weaker definition (just a crack) has no physical threshold, so the video uses the binding energy and says so.
- "Destroy the atmosphere" = lift the whole air mass out of Earth's gravity well: E = m_atm * GM/R. m_atm = 5.148e18 kg (Trenberth & Smith 2005) -> 3.221e26 J. Escape speed 11.19 km/s.
- 1 kt TNT = 4.184e12 J (the standard convention).

## Yardsticks
- Hiroshima ("Little Boy"), 6 Aug 1945: 15 kt (+/- 3) per the LANL reconstruction and ICNND -> 6.276e13 J. Treated respectfully; ~135 000 is the arsenal count, not casualties.
- Tsar Bomba, 30 Oct 1961: 50 Mt -> 2.092e17 J.
- World arsenal: about 12 000 warheads (FAS/SIPRI 2026). The UN document with FAS 2023 yields gives roughly 2 030 Mt total yield, which includes retired warheads awaiting dismantlement. The video says "около 2 гигатонн" and treats it as an upper-bound estimate (the Cold War peak was higher, ~10 Gt in the late 1980s, which only changes the ratio by 5x).
- Chicxulub impactor: about 1e23 J (Nature Reviews Earth & Environment 2022; arXiv:1403.6391; range 1e23 to 3e23 J). The video uses the lower value.

## Results (calc.py, calc_output.txt)
| Quantity | Value |
|---|---|
| Hiroshimas to split Earth | 3.57e18 (3,6 квинтиллиона) |
| Tsar Bombas to split Earth | 1.07e15 (about a quadrillion) |
| Hiroshimas in the arsenal | 1.35e5 (135 thousand) |
| Earth binding energy / arsenal | 2.64e13 (26 trillion times) |
| Hiroshimas to strip the atmosphere | 5.13e12 (5 trillion) |
| Atmosphere energy / arsenal | 3.79e7 (38 million times) |
| Sun output equal to the atmosphere energy | 0.84 s |
| Sun output equal to the Earth binding energy | 6.8 days |
| Chicxulub / arsenal | 1.18e4 (12 thousand times) |
| Analogy: Earth-Sun 150 million km vs the arsenal share | 5.7 mm (a rice grain) |

Sensitivity: replacing the arsenal with the Cold War peak (about 10x) or the PREM profile changes the headline ratio only by a factor of 3 to 10; "tens of trillions of times" stays true.

## Nuclear winter line
Xia et al. 2022 (Nature Food): a full-scale US-Russia war would put about 150 Tg of soot in the stratosphere and leave more than 5 billion people without enough food within two years. Stated in the video as "в плохом сценарии", i.e. a model result, not a certainty.

## Facts left out on purpose
- No exact per-country warhead table on screen (the numbers are estimates and keep changing).
- No claim that a bomb could crack the crust: the video only says the planet survives much bigger events (Chicxulub).

## Risky Russian words (voice) and how they were checked
See ipa_table.md (inline IPA on every word sent to ElevenLabs v4) and sources.md (gramota.ru / Wiktionary stress checks). ASR round trip with a word timeline (v/asr_vo.log) confirmed the words are audible; stress is NOT verified by ear.
