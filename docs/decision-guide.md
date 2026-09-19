# The LPI versus Standard Power decision

## The two modes in one paragraph each

**Low Power Indoor (LPI)** is the default for indoor 6 GHz. No
registration, no location reporting, no external dependency, and access to
the full band including channels at the band edges. The power spectral
density rules allow 3 dB more transmit power each time channel width
doubles (up to the EIRP ceiling), so wide channels hold their SNR and
genuinely work. The cost is power: LPI's ceilings are low, and client
devices get fixed ceilings 6 dB below the AP's, so the AP reaches the
client at distances where the client can no longer reach the AP.

**Standard Power** raises the power ceilings on both sides of the link
(the EIRP cap by 6 dB, the power-density cap by far more). Clients are
still capped at least 6 dB below the AP's authorized power, so the
asymmetry never goes away, but with a sufficient grant both the AP and
the client may run louder, which extends talk-back range, raises client
MCS rates, and cuts per-client airtime. The costs are an Automated
Frequency Coordination (AFC) dependency (3D location with stated
uncertainty, 24-hour re-authorization, product-dependent fallback on
failure), operation limited to U-NII-5 and U-NII-7, and the loss of
whatever channels the AFC masks off at your location, which hits 80 and
160 MHz plans hardest. See `afc-primer.md`.

## The failure pattern that drives the decision

Free-space math says a 6 GHz cell should run only 1 to 2 dB smaller than
the same AP at 5 GHz. LPI's client ceiling makes the usable cell smaller
than the math suggests, because the limit is the client's uplink, not the
AP's downlink. The place this shows up is the one-for-one hardware swap:
a 6 GHz AP on every existing 5 GHz cable drop produces coverage holes
between drops that the old design never had. The durable fix is a
placement redesign. When new cabling is off the table, Standard Power is
the mechanism that can narrow the gap. Verify with a survey rather than
assuming it closes.

## Prerequisites before the preferences

Standard Power is not a preference you can score your way into. Three
things are required, and if any one is missing the answer is LPI until
you fix it: hardware and clients that support Standard Power in a
regulatory domain that authorizes it, reliable AP geolocation (every
grant depends on it), and a team that owns the AFC operational
dependency. `../decision/decide.py` asks these first and refuses to
recommend Standard Power while any of them fails.

## Decision table

| Lean | When |
|---|---|
| LPI | Fresh design with correct AP placement for 6 GHz propagation. |
| LPI | High density with clients close to APs. |
| LPI | Wide channels (80 or 160 MHz) are a requirement. |
| LPI | Any Standard Power prerequisite above is missing. |
| Standard Power | One-for-one replacement on existing cable drops. |
| Standard Power | Coverage complaints traced to client talk-back at cell edge. |
| Standard Power | Large open spaces where reach beats channel count. |
| Standard Power | The channel plan is 20 or 40 MHz anyway. |

`../decision/decide.py` walks these questions interactively.

## Channel width is part of the same decision

Standard Power pairs naturally with 20 and 40 MHz plans, because narrow
channels route around whatever exclusion notches your grant carries and
keep reuse intact. LPI pairs with wide channels, because the PSD rules
preserve SNR as width grows. Wide-channel Standard Power is not
impossible (where the grant is clean, 160 MHz works and Cisco documents
it), but you are betting the channel plan on the incumbent map around
each site. Most enterprise client populations are one- and two-stream
mobile devices running traffic that needs a few megabits per second, so
40 MHz is a sound default in either mode. Go wider when a specific
client population needs it and your mode's rules or grant support it.

## Whichever mode you pick

Design for the fallback. The rules give a failed AFC check-in a grace
period, and what happens after it is product-dependent: Cisco's
dual-mode indoor APs drop to LPI, SP-only hardware goes quiet. For
dual-mode indoor gear the LPI coverage picture is the floor your design
must survive; for SP-only gear the floor is a dead radio, and the
design has to survive that instead.
Survey for client talk-back, not just AP signal. And monitor the AFC
state if you enable Standard Power, because channel and power grants can
change from outside your network. The `pyats/` precheck in this repo
covers the controller side for the Catalyst 9800.
