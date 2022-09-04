# aggregator-news-currency-messenger
This service provides an opportunity to track the exchange rates of 46 countries, cryptocurrency rates, as well as the latest world news from the meduza.io news portal.
For the exchange of information between users of the service there is a common chat-room.

## Data sources
* The exchange rates: https://www.cbr.ru/currency_base/daily
* The cryptocurrency rates: https://myfin.by/crypto-rates
* The news-portal: https://meduza.io

## Requirements
* Python 3.10;
* PostgreSQL.

## Installation
Install requirements:

        pip install -r requiremets

Create a database and specify the access parameters in the file:

* `config.py`

Fill in the following fields in file config.py:

        host = "your_host"
        user = "user_name"
        password = "your_password"
        db_name = "your_db_name"

# Application launch
After setting the database parameters, run the file:

* `app.py`
