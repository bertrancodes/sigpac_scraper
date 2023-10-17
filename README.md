## What is this?
This programm was born out of the necessity to download a large number of SIGPAC (see [this](https://www.mapa.gob.es/es/agricultura/temas/sistema-de-informacion-geografica-de-parcelas-agricolas-sigpac-/default.aspx)) polygons, with minimal human intervention. It aims to solve that problem but it has a lot of rough edges and should be treated as an alpha version, at best. I have only tested it on Linux, but it should work on Windows too.

## Usage
First of all, you need to clone the repository:
> git clone https://github.com/bertrancodes/sigpac_scraper

Then you'll need to cd into the repository and install the required packages:
> pip3 install -r requirements.txt

Once the dependencies are taken care of, you need to run the setup.py:
> python3 setup.py

This downloads the drivers for Firefox, Chrome and Opera and stores the path to these files on a YAML file so they can be easily accessed by the scraper. After that you can just run the file through the command line:

> python3 sigpac_scraper.py -inp=path/to/csv -wb=your_favorite_webbrowser

Currently only supports Firefox (default), Chrome and Opera.
