
# App use analysis for Norbu
The analysis for the Norbu project used data imported from BigQuery. The goal of the analysis is to find out user 7, 14, 21, 28 day retention rates, user LTV, product popularity, user journey and potential barriers to user experience. 

This folder contains analysis report and presentation for the Norbu app analysis project: 

- The jupyter notebook analysis file
- The html analysis file
- The p2p presentation
- The sankey diagram user journey plotting function file in both .py and .ipynb


The notebook and the function file shows how to access values of particular event parameters in the BigQuery nested data structure, as well as how to plot user journeys using sankey diagram. Analysts who are interested in using the function file will need to change the parameters based on their data structure. 

An article published on Medium based on this project can be accessed at https://xiacui.medium.com/mindfulness-app-how-to-analyse-user-behaviour-using-google-firebase-events-data-c5f20ef06669 

Note: graphs using plotly may not show in Jupyter notebook. To see full visualizations, html can be downloaded and viewed on your local machine.
