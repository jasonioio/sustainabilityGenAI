#UBC CIC Gen AI and Sustainability Hackathon 2024

A key sustainability goal defined by the UN includes clean and affordable energy; industry, innovation, and infrastructure; responsible consumption and production; climate action; and sustainable cities and communities. Energy use is a major aspect of UBC operations, hosting over 60,000 students and 16,000 staff on more than 400 hectares. 

In this project we implemented retrieval augmented generation (RAG) using various AWS services to create a chatbot with a visualization feature to allow users to ask questions about energy usage at UBC. 

We parsed the raw CSV file to a text file with rows of the building name, date, and energy use. We uploaded this file to Amazon S3, and connected this to a Amazon Bedrock Knowledge Base for RAG. In the Lambda function, we configured the Knowledge Base to prompt Claude 3 Sonnet with an engineered prompt returning a written answer and raw data to display on a chart. The front end is built with Streamlit, and graphs are drawn with Matplotlib. 

UBC's energy usage data is available here: https://energy.ubc.ca/projects/skyspark/

![alt text](arch_diagram.png "Architecture diagram")
