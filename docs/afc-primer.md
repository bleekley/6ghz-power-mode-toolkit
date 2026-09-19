# AFC: what a Standard Power AP has to prove

Automated Frequency Coordination protects the 6 GHz band's incumbents,
mainly fixed point-to-point microwave links and satellite downlink
receivers. It follows the lineage of DFS (vacate on radar) and CBRS (ask a
database first): a cloud service that knows where the incumbents are and
tells each AP what it may transmit at its location.

## The request

Before transmitting at Standard Power, an AP must send the AFC service
its latitude, longitude, and height above ground. The service evaluates
that position against the incumbent database and returns a grant listing
allowed channels and power levels.

## The re-check, and the fallback

Grants are not permanent. The AP re-authorizes every 24 hours, and the
answer can change. An AP that cannot reach the service, cannot produce a
usable location, or fails its check-in falls back to LPI, with the 6 dB
client penalty and smaller cells that come with it. Design so the network
survives that fallback.

## The indoor location problem

GNSS does not reliably work indoors, and height above ground is the
coordinate an AFC evaluation cares about most. Vendors solve this with
anchor APs near windows or exterior walls that hold a GNSS lock, and
derive interior AP positions from the anchors over 802.11 measurement
protocols. Uncertainty grows with each hop away from an anchor, and the
AFC treats uncertainty as risk: a position reported with a large
uncertainty radius is evaluated as if the AP could be anywhere inside it,
and the grant comes back restricted. Location accuracy decides whether
Standard Power was worth enabling.

## The channel mask

The AFC carves exclusion notches around incumbent frequencies, wider as
power rises, often drawn as an upside-down V on a channel chart. A notch
that clips any part of an 80 or 160 MHz channel's contiguous block
removes the whole channel. Plans built on 20 and 40 MHz route around the
notches and keep their reuse.

## What AFC does not do

AFC checks registered, fixed incumbents and nothing else. Wireless
microphones, cameras, and other transient local interference sources are
not in the database and do not change a grant. Detecting and handling
local interference stays your infrastructure's job in both modes.

## Cisco 9800-CL specifics

A 9800-CL cannot talk to Cisco's AFC service until the controller is
onboarded to the Cisco cloud with a one-time-password token import, and
it needs DNS plus outbound HTTPS from the controller (per the C9800 AFC
configuration guide chapters). The controller checks service health on a
30-second timer and reports the current blocker in a readable field, for
example `not-otp-upgraded: true`. The scripts in `../c9800/netconf/` read
that state over NETCONF.
