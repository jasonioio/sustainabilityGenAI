import boto3
import json
import logging
import os
import time

logger = logging.getLogger()
logger.setLevel(logging.INFO)

REGION = os.environ["REGION"]
SOURCE_TYPE = "BEDROCK_KNOWLEDGEBASE"

modelName = os.environ["BedrockModelName"]
modelArn = f"arn:aws:bedrock:{REGION}::foundation-model/{modelName}"
knowledgeBaseId = os.environ["KnowledgeBaseId"]
client = boto3.client("bedrock-agent-runtime")

promptTemplate = """You are a question answering agent working for the University of British Columbia answering questions. I will provide you with a set of search results and a user's question. Answer the users question using the search results. 

<data_format> 
The search results are 1-indexed. 
The search results contain information about UBC buildings and their energy use on a given day. 
The search results are sorted by day.
The data spans 2018 to 2024 comprehensively. 
Some values may be missing.  
The energy data includes: 
Building name 
Energy usage (in kWh)
Date (year, month, day)
</data_format>

Use this data for your report:<data>{{$search_results$}}</data>
     
Here is the user's question:
<question>
$query$
</question>
                
<instructions>
Think about the user’s query and what they are asking, and what you need to do to answer them.
Make sure you go through all relevant portions of the search results to provide the user the best answer.
For basic queries like "Which building used the most energy on a given day?" or "What day did Building X use the most energy in a year?", use the available data and perform direct lookups or comparisons.
For advanced queries like "What is the average energy usage of Building Y in 2022?", calculate the required statistics using historical data.
Be prepared to calculate the maximum, minimum, average, sum, and standard deviation of energy use for different buildings or across time frames.
Users may also ask to filter by specific date ranges, such as "Between 2019 and 2021," or compare multiple buildings.
</instructions>

<example> <user_query>Which building used the most energy on March 15, 2023?</user_query> <analysis>Search the data for energy usage on the specified date, compare usage across buildings, and identify the building with the highest value.</analysis> </example> 
<example> <user_query>What day did the library use the most energy in 2020?</user_query> <analysis>Filter the energy usage data for the library in 2020, find the day with the highest energy consumption.</analysis> </example> 
<!-- Advanced Analysis Examples --> 
<example> <user_query>What is the average energy usage of the Science Building between 2019 and 2021?</user_query> <analysis>Filter energy usage for the Science Building between 2019 and 2021. Calculate the average of energy usage values within the date range.</analysis> </example> 
<example> <user_query>What is the standard deviation of energy use for Building X in 2022?</user_query> <analysis>Filter energy data for Building X in 2022, calculate the standard deviation based on the data points.</analysis> </example> 
<!-- Comparative and Mathematical Tasks --> 
<example> <user_query>Which building had the lowest average energy usage in 2020?</user_query> <analysis>Calculate the average energy usage for each building in 2020, and identify the one with the lowest value.</analysis> </example> 
<example> <user_query>How much total energy did the campus use between January 2020 and December 2023?</user_query> <analysis>Sum the energy usage for all buildings within the specified date range.</analysis> </example> 
<!-- Encourage Analytical Thinking --> <example> <user_query>What are the major trends in energy use across UBC between 2018 and 2024?</user_query> <analysis>Analyze the data over time for overall increases or decreases in energy use, seasonal variations, or notable patterns across years and buildings.</analysis> </example> 

<thought_process> 
Always reason through the problem. Ask yourself: - Is the user query clear, or do I need to ask for clarification? - What data filters or calculations do I need to apply to provide an accurate answer? - Would additional context (such as trends or anomalies) enhance the user’s understanding? 
</thought_process>

<output_format_instructions>
	Respond in JSON format as follows:
	{
  	"description": "Your detailed response based on $query$",
  	"array": []  // An array of JSON objects that display the relevant data in the format of {key: EnergyConsumption}
	}
	If only one value is returned, return one object with the accompanying key being the most reasonable in response to the prompt.
  </output_format_instructions>

"""


def retrieve_generate_knowledgebase(event):
    print(event)
    eventArgs = json.loads(event["body"])
    print(eventArgs)
    prompt = eventArgs["prompt"]
    print(prompt)
   # sessionId = eventArgs["conversationId"] if "conversationId" in eventArgs else None
    sessionId = None
    

    bedrock_response = {}
    if sessionId:
        bedrock_response = client.retrieve_and_generate(
            input={"text": prompt},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledgeBaseId,
                    "modelArn": modelArn,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "overrideSearchType": "HYBRID",
                        }
                    },
                    "generationConfiguration": {
                        "promptTemplate": {
                            "textPromptTemplate": promptTemplate
                        }
                    }
                }
            }
        )
    else:
        bedrock_response = client.retrieve_and_generate(
            input={"text": prompt},
            retrieveAndGenerateConfiguration={
                "type": "KNOWLEDGE_BASE",
                "knowledgeBaseConfiguration": {
                    "knowledgeBaseId": knowledgeBaseId,
                    "modelArn": modelArn,
                    "retrievalConfiguration": {
                        "vectorSearchConfiguration": {
                            "overrideSearchType": "HYBRID",
                        }
                    },
                    "generationConfiguration": {
                        "promptTemplate": {
                            "textPromptTemplate": promptTemplate
                        }
                    }
                }
            },
        )

    timestamp = bedrock_response["ResponseMetadata"]["HTTPHeaders"]["date"]
    epochTimestampInt = int(
        time.mktime(time.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z"))
    )
    epochTimestamp = str(epochTimestampInt)

    response = {}
    response["type"] = SOURCE_TYPE
    response["conversationId"] = bedrock_response["sessionId"]
    response["systemMessageId"] = bedrock_response["sessionId"]
    response["systemMessage"] = bedrock_response["output"]["text"]
    response["epochTimeStamp"] = epochTimestamp
    response["sourceAttributions"] = bedrock_response["citations"]

    restApiResponse = json.dumps(response)
    response = restApiResponse

    return response


def handler(event, context):
    print(REGION)
    print(modelArn)
    print(modelName)
    logger.info(f"received event: {event}")
    response = retrieve_generate_knowledgebase(event)
    logger.info(response)
    return {
        "statusCode": 200,
        "body": response,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        }
    }
    
