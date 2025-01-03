# Investment
Investment project

## Requirements
- !pip install yfinance
  
- !pip install pandas



## TOC
- fear_and_greed_index.csv : Record fgi between 2024/09/01 to 2024/12/31,
  could be done by either typing or web-crawling.
  Note that bs4 + requests is not enough for crawling. You'll need Selenium to achieve this.

- FGI_invest.py : Main program. Just run this file in whatever python compiler. 


## Outputs
Running FGI_invest.py will generate 

- histort.csv : Trading history
  
- asset_summary.csv : Final value & Profit


## License
- MIT