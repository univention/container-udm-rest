# Blocklist Cleanup

This container serves as execution environment for the script `blocklist_clean_expired.py` which uses the UDM REST API client to delete expired blocklist entries.

It gets executed by `helm/udm-rest-api/templates/cronjob.yaml`, which runs this script in a given time period (default: once a day at 04:00 am).

For more details about blocklists, see [udm-blocklists](https://docs.software-univention.de/manual/5.2/en/user-management/udm-blocklists.html#udm-blocklists-activate)
