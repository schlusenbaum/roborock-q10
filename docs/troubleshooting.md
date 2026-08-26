# Troubleshooting

## Rooms Are Not Available

Make sure the official Roborock integration is working correctly.

The Q10 integration reads room information from the map data of the existing vacuum entity.

Try calling:

`roborock_q10.get_rooms`

and check the Home Assistant logs.

## A Room Name Is Unknown

Room names are validated against the rooms currently known from the map.

Check the available room names and make sure the spelling matches exactly.

## Map Data Is Missing

The vacuum may not have received map data yet.

Refreshing the Roborock API or triggering a map update can make the room information available.

## Check Diagnostics

The diagnostic service can be used during troubleshooting:

```yaml
service: roborock_q10.diagnose
data:
  entity_id: vacuum.your_q10
  mode: map
```

Check the Home Assistant logs for diagnostic output.
