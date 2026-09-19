# AFC: what a Standard Power AP has to prove

Automated Frequency Coordination protects the 6 GHz band's licensed
incumbents, chiefly fixed point-to-point microwave links. (Satellite
uplink receivers are protected separately: the FCC decided AFC was not
needed for them and instead capped how much power an outdoor Standard
Power AP may radiate skyward.) AFC follows the lineage of DFS (vacate on
radar) and CBRS (ask a database first): a cloud service that knows where
the incumbents are and tells each AP what it may transmit at its
location.

## The request

Before transmitting at Standard Power, an AP must send the AFC service
its latitude, longitude, and height above ground, each with a stated
uncertainty. The service evaluates that position against the incumbent
database and returns a grant listing allowed channels and power levels.
Standard Power operates only in U-NII-5 and U-NII-7; the grant subtracts
from those.

## The re-check, and what failure looks like

Grants are not permanent. The AP re-authorizes every 24 hours, and the
answer can change. An AP that cannot reach the service or fails its
check-in may not keep transmitting at Standard Power past the grace
period the rules allow. What happens next is product-dependent: Cisco's
dual-mode indoor APs drop to LPI, with LPI's lower power ceilings and
smaller cells, while SP-only hardware (some outdoor APs) has no LPI to
drop to and the radio goes quiet. Confirm your AP's behavior, and design
so the network survives the LPI picture either way.

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
removes the whole channel. Whether wide channels survive depends on the
grant at your location: sites clear of incumbents can run them, and
Cisco documents 160 MHz Standard Power operation. Plans built on 20 and
40 MHz are simply harder for a notch to break, which keeps reuse
predictable across many sites.

## What AFC does not do

AFC checks registered, fixed incumbents and nothing else. Wireless
microphones, cameras, and other transient local interference sources are
not in the database and do not change a grant. Detecting and handling
local interference stays your infrastructure's job in both modes.

## Cisco 9800-CL specifics

A 9800-CL cannot talk to Cisco's AFC service until the controller is
onboarded to the Cisco cloud with a one-time-password token import, and
it needs DNS plus outbound HTTPS (and OCSP) reachability from the
controller (per the C9800 AFC configuration guide chapters). The
controller runs a periodic AFC service health check (my bench unit
reported on a 30-second cadence; Cisco's documentation shows longer
timers, so treat the interval as release-dependent) and reports the
current state in a readable field: a healthy service sets `cloud-hc-ok`,
an unhealthy one names the blocker, for example `not-otp-upgraded`. The
scripts in `../c9800/netconf/` read that state over NETCONF.
