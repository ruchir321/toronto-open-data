# Toronto Open Data Explorer Agent

Use agent to explore datasets and generate high level insights from toronto open data.

create ckan mcp?? what does that even mean?

Agent will think like a data portal expert. It will have read access to metadata and other resources made available through ckan api. It will smartly query data needed to inform user query. It will provided links, insights and code for relevant datasets.

The ultimate goal is to provide user a strong confidence that the data portal has useful dataset for their use.

Use case examples:

[1] A business user who has a straightforward question and needs an immediate answer:

user: what businesses applied for license in my ward? 

agent: according to this dataset (xyz) published by (abc) dept., your ward had 67 new applications for businesses. here is the data and here is the code for further exploration.

[2] A technical user who is looking to explain data and find trends:

user: how is the ferry services performing in the second half of september each year? give me an STL decomposition of ferry services traffic for annual time series data.

agent: (1) here, i have used (xyz) dataset and found out that ferry services has (123) purchases and (456) redemptions in the second half of september each year on average. The box plot better explains the distribution of the values across the time series. 

    (2) The STL decomposition for the ferry services shows seasonality in the months (JUN-SEP). The trend has been steady across each year with a slight uptick in 2023 because Batman visited the Wards Island community center. Here is the code you can use to get started with a further in depth analysis