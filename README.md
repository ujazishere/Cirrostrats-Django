## Clone the repo:
`git clone https://github.com/ujazishere/Cirrostrats.git`

## Create .env file and include following contents -- mind the api key
```
ujazzzmay0525api="<api_key>"
ismail_fa_apiKey="<api_key>"         # Ismail key

# Gmail auth for email notification
smtp_password="dsxi rywz jmxn qwiz"

# fire email on lookup and incude this as subject
EC2_location="Local"
# EC2_location="Production"

# Runnign gate scrape -- 0 for local, 1 for production 
# run_lengthy_web_scrape=0
run_lengthy_web_scrape=1
```

## Using Docker:
`docker compose up`

