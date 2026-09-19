# The LPI versus Standard Power decision

## The two modes in one paragraph each

**Low Power Indoor (LPI)** is the default for indoor 6 GHz. No
registration, no location reporting, no external dependency, and access to
the full band including channels at the band edges. The power spectral
density rules add 3 dB of allowed transmit power each time channel width
doubles, so SNR holds steady at 80 and 160 MHz and wide channels genuinely
work. The cost is on the client side: client devices must transmit up to
6 dB below the AP's power, so the AP reaches the client at distances where
the client can no longer reach the AP.

**Standard Power** removes the client restriction, which restores client
talk-back, raises client MCS rates, and cuts per-client airtime. The costs
are an Automated Frequency Coordination (AFC) dependency (exact 3D
location, 24-hour re-authorization, fallback to LPI on any failure) and
the loss of channels to AFC exclusion masks, which hits 80 and 160 MHz
plans hardest. See `afc-primer.md`.

## The failure pattern that drives the decision

Free-space math says a 6 GHz cell should run only 1 to 2 dB smaller than
the same AP at 5 GHz. The 6 dB client penalty makes the usable cell
smaller than the math suggests, because the limit is the client's uplink,
not the AP's downlink. The place this shows up is the one-for-one
hardware swap: a 6 GHz AP on every existing 5 GHz cable drop produces
coverage holes between drops that the old design never had. The durable
fix is a placement redesign. When new cabling is off the table, Standard
Power is the mechanism that closes the gap.

## Decision table

| Lean | When |
|---|---|
| LPI | Fresh design with correct AP placement for 6 GHz propagation. |
| LPI | High density with clients close to APs. |
| LPI | Wide channels (80 or 160 MHz) are a requirement. |
| LPI | No appetite for AFC operations and monitoring. |
| Standard Power | One-for-one replacement on existing cable drops. |
| Standard Power | Coverage complaints traced to client talk-back at cell edge. |
| Standard Power | Large open spaces where reach beats channel count. |
| Standard Power | The channel plan is 20 or 40 MHz anyway. |

`../decision/decide.py` walks these questions interactively.

## Channel width is part of the same decision

Standard Power pairs with 20 and 40 MHz plans, because narrow channels
route around AFC exclusion notches and keep reuse intact. LPI pairs with
wide channels, because the PSD rules preserve SNR as width grows. Most
enterprise client populations are one- and two-stream mobile devices
running traffic that needs a few megabits per second, so 40 MHz is a
sound default in either mode. Go wider only when a specific client
population needs it and you are in LPI.

## Whichever mode you pick

Design for the fallback. A Standard Power AP that fails its AFC check-in
drops to LPI on its own, so the LPI coverage picture is your worst case
either way. Survey for client talk-back, not just AP signal. And monitor
the AFC state if you enable Standard Power, because channel and power
grants can change from outside your network. The `pyats/` monitor in this
repo does that for the Catalyst 9800.
