# Configuration

The integration is configured through Home Assistant's config flow.

## Vacuum Entity

During setup, select the existing vacuum entity created by Home Assistant's official Roborock integration.

For example:

`vacuum.roborock_q10`

The exact entity ID depends on your Home Assistant configuration.

## Relationship to the Official Roborock Integration

The Q10 integration does not create its own cloud connection.

Instead, it uses the API and coordinator of the existing Roborock vacuum entity.

This means the official Roborock integration must remain installed and configured.

## Map Updates

The integration listens for map updates and stores information about known maps and their rooms.

Map information can also be refreshed manually using the available services.
