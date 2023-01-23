# native libraries
import os
import requests
import json
from pprint import pprint

# third party modules
from dotenv import load_dotenv
import os
import openai
import pandas as pd
from notion_client import Client

load_dotenv()


# token_notion
token_notion = os.getenv("NOTION_API_KEY")
database_id = '932b90e793db484f93daaf2bda259819'

# token_openai
token_openai = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")


def write_text(client, page_id, text, type):
    client.blocks.children.append(
        block_id=page_id,
        children=[
            {
            "object": "block",
            "type": type,
            type: {
                    "rich_text": [
                        {
                        "type": "text",
                        "text": {
                            "content": text
                            }
                        }
                    ]

                }
            }
        
        ]
    )
    

def read_text(client, page_id):
    response = client.blocks.children.list(block_id=page_id)
    return response['results']

def read_df(client, database_id):
    response = client.databases.query(database_id=database_id)
    return response['results']

def ai_ready(page):
   return page['properties']['Status']['status']['name'] == 'Ready'


def create_simple_blocks_from_content(client, content):

    page_simple_blocks = []

    for block in content:

        block_id = block['id']
        block_type = block['type']
        has_children = block['has_children']
        rich_text = block[block_type]['rich_text']

        if not rich_text:
            return page_simple_blocks


        simple_block = {
#             'id': block_id,
            'type': block_type,
            'text': rich_text[0]['plain_text']
        }

        if has_children:
            nested_children = read_text(client, block_id)
            simple_block['children'] = create_simple_blocks_from_content(client, nested_children)

        page_simple_blocks.append(simple_block)


    return page_simple_blocks


def read_page(client,notion_page_id):
    content = read_text(client, notion_page_id)

    simple_blocks = create_simple_blocks_from_content(client, content)

    return simple_blocks
    

def ai_response(ai_prompt):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=json.dumps(ai_prompt),
      temperature=0.5,
      max_tokens=5,
      top_p=0.3,
      frequency_penalty=0.5,
      presence_penalty=0
    )
    
    return response["choices"][0]["text"].strip("/n")


def update_status(client, page_id):
    client.pages.update(
        page_id = page_id,
        properties = {
     'Status': {
    'status': {
     'name': 'Done'}},
    }
        
    )


def update_page(client,df):
    for page in df:
        if ai_ready(page):
            ai_prompt = read_page(client, page["id"])
            
            response = ai_response(ai_prompt)
#             response = "Hello World"
            
            write_text(client, page["id"], response, "paragraph")
            
            update_status(client, page["id"])
            
    
def main():
    client = Client(auth=token_notion)
    
    df = read_df(client, database_id)
    
    update_page(client,df)
    

if __name__ == '__main__':
    main()
    