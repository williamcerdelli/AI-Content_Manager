# native libraries
import os
import json

# third party modules
from dotenv import load_dotenv
import openai
from notion_client import Client

load_dotenv()


# token_notion
TOKEN_NOTION = os.getenv("NOTION_API_KEY")

# database_id
DATABASE_ID = os.getenv("DATABASE_ID")

# token_openai
openai.api_key = os.getenv("OPENAI_API_KEY")


def write_text(client, page_id, text, type_name):
    client.blocks.children.append(
        block_id=page_id,
        children=[
            {
                "object": "block",
                "type": type_name,
                type_name: {
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
            # id': block_id,
            'type': block_type,
            'text': rich_text[0]['plain_text']
        }

        if has_children:
            nested_children = read_text(client, block_id)
            simple_block['children'] = create_simple_blocks_from_content(
                client,
                nested_children
                )

        page_simple_blocks.append(simple_block)

    return page_simple_blocks


def read_page(client, notion_page_id):
    content = read_text(client, notion_page_id)

    simple_blocks = create_simple_blocks_from_content(client, content)

    return json.dumps(simple_blocks)


def ai_response(ai_prompt, instructions="", tokens=200):
    response = openai.Completion.create(
      model="text-davinci-003",
      prompt=f"{instructions},{ai_prompt}",
      temperature=0.5,
      max_tokens=tokens,
      top_p=0.3,
      frequency_penalty=0.5,
      presence_penalty=0
    )
    return response["choices"][0]["text"].strip()


def update_status(client, page_id):
    client.pages.update(
        page_id=page_id,
        properties={
            'Status': {
                'status': {
                    'name': 'Done'
                }
            },
        }
    )


def update_page(client, page):
    ai_prompt = read_page(client, page["id"])

    article = ai_response(ai_prompt)

    print(f"article='{article}'")

    write_text(client, page["id"], article, "paragraph")

    update_status(client, page["id"])


def main():
    client = Client(auth=TOKEN_NOTION)

    df = read_df(client, DATABASE_ID)

    # Filter a list of pages ready for processing
    df_ready = [page for page in df if ai_ready(page)]

    print(f"{len(df_ready)} pages need to be processed")

    for page in df_ready:
        update_page(client, page)


if __name__ == '__main__':
    main()