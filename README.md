# Outplay-Google-Sheets
This script is for Outplay Call list automation using Outplay API and Google sheets API
How does this work????? 
Its very simple and follows the following steps
1. The code hits the Outplay API
2. The Outplay API returns a list of calls based on the conditions provided
3. The list is limited to 50 entries per API hit so had to use a loop for 3000 entries
4. The list is in json format so it is converted to a csv
5. The CSV is then appended to a google sheet by calling the google sheets api.
