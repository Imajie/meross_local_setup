# Meross Switch configuration

This script will configure a [Meross](https://meross.com) switch to connect to a local MQTT broker for control.

## Usage

To configure the switch first ensure that the computer running the script is connected to the Meross\_SW\_XXXX wifi network.

The MQTT broker must be running with TLS enabled.

```bash
./switch.py --broker [broker ip or hostname] --port [broker MQTT port]
```
