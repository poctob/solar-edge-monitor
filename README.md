# SolarEdge Monitor

## Simple API based monitor for SolarEdge solar systems

### Principle of operation

This service polls SolarEdge API for inverter power output. If last reported output is less than the threshold value, an alert is generated.
The API call checks inverter energy produced between 12 p.m and 1 p.m.
Alert is generated by sending an email.
Every inverter in the SolarEdge site account will be checked.

### Implementation specifics

This service is written to run as Azure Function, but it can be easily adopted to run on other cloud platforms or locally.
There are two function:
1. Timer triggered: runs every day at 22:00 GMT.
2. Http triggered: takes a single query parameter **date** in **YYYY-MM-DD** format ex: `?date=2021-08-21`. Http trigger can be used to view inverter output and check inverter power for any day in the past. Function URL by default is as follows:
`https://<your function host url>/api/CheckInverterOutput?date=<date parameter>`

### Configuration
The following environmental (Azure Function configuration) values are needed to run this service:

- **alertPowerThreshold** - integer, typically 200 is a good value
- **baseURL** - string, base user of SolarEdge API server, typically it is https://monitoringapi.solaredge.com/
- **siteId** - string, SolarEdge site id, it can be found in your SolarEdge web portal
- **solarEdgeApiKey** - string, API key for your SolarEdge account, also found in your SolarEdge web portal
- **sendGridApiKey** - string, API key for your SendGrid account, configure it in Azure portal
- **toEmail** - string, this is where alert emails will be sent
- **fromEmail** - string, email address from which the alerts will be sent, make sure to clear the domain with SendGrid
