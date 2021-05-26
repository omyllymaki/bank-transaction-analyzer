# Bank Transaction Analyzer

Bank Transaction Analyzer provides analysis and visualization of bank transaction data.

By default the analyzer works with Nordea internet bank data but can be customized to work with other data formats too.

## Before usage

* Install Python >= 3.6.
* Install requirements.

For Ubuntu users there is installation script: ```./install.sh```.

## Basic usage

* Export your data from Nordea internet bank (Tilit / Tilitapahtumat ja tilin tiedot / Tapahtumaluettelo).
* Start GUI program from command line by typing ```python3 main.py [-- config config_path]``` or simply ```./run.sh [config_path]``` if you are using virtualenv with Ubuntu.
* Load data with load button which opens file dialog where you can choose multiple files for analysis.
* Set filter values and analyze you data by pressing Analyze data; this updates the figures.
* Change tabs to see different views and analyses for your data.

Note:
Some simulated test data is also provided (in test_data folder). This data can be used to test application.

## Configuration

Following files under configurations folder can be used for configuration:

* config.json
* drop_data.json
* indicators.json

**Drop data**

drop_data.json specifies which items should be always filtered out. E.g. "target": ["Liisa", "Mikko"] would filter out all the rows where target is Liisa or Mikko. You can add new items to drop_data list by modifying drop_data.json file directly or from Events tab by right clicking event you want to add to drop_data list.    

**Indicators**

Indicator is a thing you want to follow over time. It can be e.g. salary, traveling expenses, housing costs, sport expenses and so on. E.g. "sale|prisma|citymarket|k market|s market|k supermarket|kylävalinta|lidl|siwa" as target would group purchases from multiple stores.

You can make your own indicator by creating new item in indicators.json file or by selecting suitable filter values from GUI and pressing "Create indicator from existing filters" button.

## Screenshots (with simulated test data provided)

<p align="center">
<img src="screenshots/Income-outcome vs time.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/Income-outcome by target.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/stacked bars.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/indicators.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/events.jpg" width="800px" />
</p>

## Using application with non-default data format

By default the analyzer works with Nordea internet bank data, with certain data format. However, the application can be used with other data formats too. This is done by implementing custom Loader and Transformer class.

Loader loads the raw data from files. It needs to inherit and implement LoaderInterface class.

Transformer collects relevant information from raw data and converts it to specified format that can be handled by application. It needs to inherit and implement TransformerInterface class. Output of Transformer is validated. It needs to pass validation checks defined in src/data_processing/validation.py file:

```
schema = pandas_schema.Schema([
        Column('value', decimal_validation + nan_validation),
        Column('time', datetime_validation + nan_validation),
        Column('target', string_validation),
        Column('message', string_validation),
        Column('event', string_validation),
        Column('account_number', string_validation),
    ])
```

When custom Loader and Transformer classes are created, they can be used by adding bank option to src/data_processing/bank_selection.py file and selecting that bank in config.json file.

## Alert checks

alert_checks folder contains some utilities to run different kind of alert checks to data. See alert_checks_sample.py as
an example. You can run it by typing ```python3 alert_checks_sample.py```; the checks are made to data in test_data folder by default. 

