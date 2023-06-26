# Bank Transaction Analyzer

Bank Transaction Analyzer provides analysis and visualization of bank transaction data.

By default, the analyzer works with Nordea internet bank data (both old and new format) but can be customized to work 
with other banks and data formats too.

# Before usage

* Install Python >= 3.6.
* Install requirements.

For Ubuntu users there is installation script: ```./install.sh```.

# Basic usage

* Export your data from Nordea internet bank 
  * Old internet bank: Tilit / Tilitapahtumat ja tilin tiedot / Tapahtumaluettelo
  * New internet bank: Talous / tilit / Tapahtumat ja tiedot / CSV
* Start GUI program from command line by typing ```python3 main.py [-- config config_path]``` or simply ```./run.sh [config_path]``` if you are using virtualenv with Ubuntu.
* Load data with load button which opens file dialog where you can choose multiple files for analysis.
* Set filter values and press Enter to apply filtering.
* Change tabs to see different views and analyses for your filtered data.
* Events tab table can be sorted (left click) or grouped (right click) by any column by clicking corresponding column name.
* Add free form notes to events in Events tab.

Note:
Some simulated test data is also provided (in test_data folder). This data can be used to test application.

# Configuration

Following files under configurations folder can be used for configuration:

* config.json
* drop_data.json
* categories.json
* labels.json
* notes.json

**Drop data**

drop_data.json specifies which items should be always filtered out. E.g. "target": ["Liisa", "Mikko"] would filter out all the rows where target is Liisa or Mikko. You can add new items to drop_data list by modifying drop_data.json file directly or from Events tab by right clicking event you want to add to drop_data list.

**Categories**

Events are classified to different categories.  E.g. one could create category "Transport expenses" by selecting "target" as "vr|taksi|abc|teboil|neste" and "max_value" as 0. Every event can have only one category.

You can make your own category by creating new item in categories.json file or by selecting suitable filter values from GUI and pressing "Create category from existing filters" button. If an event matches to multiple categories, then the last category in the file will be used as the category of event.

**Labels**

Labels work like categories with the difference that event can have multiple labels.

You can make your own label by creating new item in labels.json file or by selecting suitable filter values from GUI and pressing "Create label from existing filters" button.

**Notes**

Notes files contains free notes for events, using event ids as keys. This file will be filled automatically based on notes user has added in tabs "Events" and "Events filtered out". The content of the file will be loaded when app launches and all the existing notes are shown in GUI.

# Screenshots (with simulated test data provided)

<p align="center">
<img src="screenshots/Income-outcome vs time.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/distributions.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/indicators.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/events.jpg" width="800px" />
</p>

<p align="center">
<img src="screenshots/events grouped.jpg" width="800px" />
</p>

# Advanced

## Using application with non-default data format

By default the analyzer works with Nordea internet bank data, with certain data format. However, the application can be 
used with other data formats too. This is done by implementing custom Loader and Transformer class.

Loader loads the raw data from files. It needs to inherit and implement LoaderInterface class.

Transformer collects relevant information from raw data and converts it to specified format that can be handled by 
application. It needs to inherit and implement TransformerInterface class. Output of Transformer is validated. It needs 
to pass validation checks defined in src/data_processing/validation.py file:

```
schema = pandas_schema.Schema([
        Column('value', decimal_validation + nan_validation),
        Column('time', datetime_validation + nan_validation),
        Column('bank', string_validation + nan_validation),
        Column('target', string_validation),
        Column('message', string_validation),
        Column('event', string_validation),
        Column('account_number', string_validation),
    ])
```

When custom Loader and Transformer classes are created, they can be used by adding bank to DataPreprocessor class
(src/data_processing/data_preprocessing.py).

## Alert checks

alert_checks folder contains some utilities to run different kind of alert checks to data. See alert_checks_sample.py as
an example. You can run it by typing ```python3 alert_checks_sample.py```; the checks are made to data in test_data folder by default.

