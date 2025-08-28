# Toronto Public Library Data Analysis

## Introduction

This project provides an in-depth analysis of the Toronto Public Library (TPL) system using open data from the City of Toronto. The goal is to make the data more accessible and understandable for the general public, providing insights into how Torontonians use their library system. This repository explores trends in library usage, including circulation, visits, registrations, and more.

## Datasets

This analysis is based on the following datasets from the City of Toronto's Open Data portal:

* **library-branch-general-information.csv**: General information about each library branch, including address, square footage, and services offered.
* **library-circulation.csv**: Annual circulation data (checkouts and renewals) for each library branch.
* **library-visits.csv**: Annual number of visits to each library branch.
* **library-card-registrations.csv**: Annual number of new library card registrations at each branch.
* **library-workstation-usage.csv**: Annual number of workstation (computer) sessions at each branch.
* **library-branch-programs-and-events-feed.csv**: Information about programs and events held at library branches.

## Key Insights

My analysis has revealed several key insights into the TPL system:

* **Digital vs. Physical Circulation**: While physical circulation has been declining, digital circulation has seen a significant increase, especially since 2020. This highlights the growing importance of digital resources for the TPL.
* **Impact of the Pandemic**: The COVID-19 pandemic had a major impact on library usage, with a sharp decrease in physical visits and a corresponding surge in the use of digital services.
* **Branch Size and Usage**: There is a positive correlation between the square footage of a library branch and its circulation, visits, and registrations. Larger branches tend to have higher usage statistics.
* **Busiest Branches**: The Toronto Reference Library is consistently one of the busiest branches in terms of circulation, visits, and workstation usage.

## How to Use

This repository is organized into the following directories:

* **/data**: Contains the raw and cleaned datasets used in the analysis.
* **/code**: Contains the Jupyter notebooks and Python scripts used for data analysis and visualization.
  * **/EDA**: Exploratory Data Analysis notebooks.
  * **/NLP**: Natural Language Processing analysis of event data (work in progress).
  * **streamlit_dashboard.py**: A Streamlit application to interactively explore the data.
* **/output**: Contains the plots and other output files generated from the analysis.
* **/utils**: Contains utility scripts for downloading and processing the data.

To explore the data yourself, you can run the Streamlit dashboard:

```bash
streamlit run code/streamlit_dashboard.py
```

## Work in Progress

I am continuously working to improve this analysis. Future work includes:

* **Events Analysis**: A deeper analysis of the types of events offered by the TPL and their impact on community engagement.
* **NLP Pipeline**: Developing a Natural Language Processing pipeline to analyze the descriptions of library events and gain insights into the topics and themes that am most popular.
* **Interactive Dashboard**: Adding more features and visualizations to the Streamlit dashboard to make it even more interactive and user-friendly.

I hope this analysis is a valuable resource for anyone interested in the Toronto Public Library system.
