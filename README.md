<p align="center">
  <img src="https://i.imgur.com/SPYT1zV.png" width="154">
  <h1 align="center">FB <br/>Parser</h1>
  <p align="center">A desktop application that implements <b>search, analysis, and graphical display</b> of data
  received from users of such social networks like <b>Facebook and Vkontakte</b>.
Implemented in Python.<p>
  <p align="center">
	<a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/built%20with-Python3-ffc0cb.svg" />
    </a>
    <a href="https://github.com/SeleniumHQ/selenium">
    <img src="https://img.shields.io/badge/built%20with-Selenium-7fffd4.svg" />
    </a>
  </p>
</p>


## Table of contents
- [Project Structure](#structure)
- [How to install and run Parser](#installation)
  * [Installation](#installation)
	* [Dependencies](#dependencies)
  * [Running App](#running)

### Structure

* **data/**
    - **FB_data.xlsx** --> initial data (Excel) with likes & subscribers info.  **!!! MUST BE NAMED *FB_data* !!!**
    - **fb_data.csv** --> converted data for future parser work.
* **example_output/**
    - **fb_hse_usr_jobs.csv** --> example (real data) of parsed data (id, name, current job, previous job).
* **output/**
    - **fb_hse_usr_jobs.csv** --> OUTPUT, parsed data
* **src/**
    - **convertor.py** --> python code, that converts .xlsx to .csv
    - **crawler.py** --> the main code of parser

## **Installation**

__Important:__ depending on your system, make sure to use `pip3` and `python3` instead.
#### Dependencies
* (or install *requirements.txt*)
```elm
pip install bs4 (v0.0.1)
pip install selenium (v3.141.0)
pip install beautifulsoup4 (v4.9.3)
pip install pandas (v1.2.4)
pip install openpyxl (v3.0.7)
```

__Important:__ Selenium requires a driver to interface with the chosen browser.  
* download **[Chrome driver](https://sites.google.com/a/chromium.org/chromedriver/downloads)** (depends on Chrome version)
__Important:__ **!!!**  Path to *chromedriver* you can change in **crawler.py**. (Has to be correct!)
<img src="https://i.imgur.com/QMXptaq.png" width="154">

#### Running

To run app, you'll need to run the **[file](https://github.com/DoktaPola/fb_parser/blob/main/src/crawler.py)** script you've just downloaded.

If this Facebook account is blocked one day, you can change **login** and **password** to new ones in **crawler.py**, like so:
```python
login="****",
password="****"
```

File **crawler.py** will launch the facebook parser and start working (takes a lot of time).

---

> **Disclaimer**<a name="disclaimer" />: Please Note that this is a research project. I am by no means responsible for any usage of this tool. Use on your own behalf. I'm also not responsible if your accounts get banned due to extensive use of this tool.
