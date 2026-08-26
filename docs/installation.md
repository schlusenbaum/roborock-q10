# Installation

## Prerequisites

Before installing this integration, the official Home Assistant Roborock integration must already be configured and working with your Roborock Q10.

This integration does not connect to the Roborock cloud independently. It extends the existing Roborock vacuum entity provided by Home Assistant.

## Installation via HACS

1. Open HACS in Home Assistant.
2. Open **Integrations**.
3. Open the menu and select **Custom repositories**.
4. Add this GitHub repository.
5. Select **Integration** as the repository type.
6. Install **Roborock Q10**.
7. Restart Home Assistant.

## Manual Installation

Copy the directory

`custom_components/roborock_q10`

into the `custom_components` directory of your Home Assistant configuration.

Restart Home Assistant afterwards.

## Initial Setup

After the restart, add the Roborock Q10 integration through **Settings → Devices & services**.

Select the existing Roborock vacuum entity that represents the Q10.

The integration then creates the additional Q10-specific entities and services.
