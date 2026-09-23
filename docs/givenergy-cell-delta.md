# GivEnergy battery cell delta

`packages/givenergy.yaml` works out a cell voltage delta for each of the five
GivEnergy battery packs, and alerts when any pack stays unbalanced.

## Sensors

| Entity | What it is |
| --- | --- |
| `sensor.givenergy_<serial>_cell_delta` | Highest cell voltage minus lowest, across the pack's 16 cells, in mV |
| `binary_sensor.givenergy_<serial>_cell_imbalance` | `on` once that pack has been over 50 mV for 15 minutes without a break |
| `binary_sensor.givenergy_cell_imbalance` | `on` while any of the per-pack sensors is `on`; this is what the alert watches |
| `alert.givenergy_cell_imbalance` | Phone notification while the binary sensor is `on`, repeated every 4 hours, can be acknowledged |

The serials are `dx2320g655`, `dz2324g237`, `dx2319r335`, `dz2239r348` and
`df2240g031`. Each delta sensor reads the `sensor.givtcp_<serial>_battery_cell_<n>_voltage`
entities that GivTCP publishes. It goes `unavailable` unless all 16 cells
report a value, so a missing cell can't make the spread look smaller than it is.

Each pack has its own 15-minute timer. Two packs that are each over the
threshold for 10 minutes, one after the other, won't raise the alert.

If a pack's delta sensor goes unavailable, its imbalance sensor keeps its last
state. A dropout therefore can't raise the alert, and it can't clear one
either, so "back under 50 mV" only arrives after a real reading.

The aggregate sensor has an `over_threshold` attribute that lists each
offending pack and its delta. The alert message uses it, along with the
inverter SoC.

## Reading the delta

These are LFP cells. Between roughly 15% and 95% SoC the voltage curve is so
flat that even a mismatched pack reads only a few mV, so a small mid-range
delta tells you very little. The curve only gets steep at either end:

- **Near full**, the delta shows how well the BMS is top-balancing. If it's
  high here but falls back after a few full charges, the cells are drifting
  and the balancing is catching them.
- **Near empty** (the reserve is 4%, so the packs do get there), the lowest
  cell falls away first. A high delta here points to one cell having less
  capacity than the rest. Balancing can't fix that.

Heavy charge or discharge current also opens up the spread for a while,
because each cell has slightly different internal resistance. The 15-minute
`delay_on` is there so those spikes don't reach the alert.

To change the 50 mV threshold, edit the `> 50` in each per-pack imbalance
sensor, and the alert's `done_message`.

## Dashboard cards

Dashboards on this instance are storage-mode, so there's no dashboard YAML
in the repo. To add either card, paste it into a dashboard's card editor.

The recorder keeps only 7 days of state history, so a `history-graph` covers
the recent past at full resolution:

```yaml
type: history-graph
title: Battery cell delta
hours_to_show: 48
entities:
  - entity: sensor.givenergy_dx2320g655_cell_delta
    name: DX2320G655
  - entity: sensor.givenergy_dz2324g237_cell_delta
    name: DZ2324G237
  - entity: sensor.givenergy_dx2319r335_cell_delta
    name: DX2319R335
  - entity: sensor.givenergy_dz2239r348_cell_delta
    name: DZ2239R348
  - entity: sensor.givenergy_df2240g031_cell_delta
    name: DF2240G031
  - entity: sensor.givtcp_fd2308f368_soc
    name: SoC
```

SoC is on the same card so you can see which end of the curve a peak came
from. It gets its own `%` axis.

The delta sensors have `state_class: measurement`, so they also get long-term
statistics, which the recorder keeps indefinitely. For a trend over months,
plot the daily maximum:

```yaml
type: statistics-graph
title: Battery cell delta, daily peak
chart_type: line
period: day
days_to_show: 90
stat_types:
  - max
entities:
  - entity: sensor.givenergy_dx2320g655_cell_delta
    name: DX2320G655
  - entity: sensor.givenergy_dz2324g237_cell_delta
    name: DZ2324G237
  - entity: sensor.givenergy_dx2319r335_cell_delta
    name: DX2319R335
  - entity: sensor.givenergy_dz2239r348_cell_delta
    name: DZ2239R348
  - entity: sensor.givenergy_df2240g031_cell_delta
    name: DF2240G031
```

If one pack's daily peak keeps climbing while the others stay flat, that pack
is the one to raise with GivEnergy.
