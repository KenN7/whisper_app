from notion_client import AsyncClient

notion = AsyncClient(auth="")
NOTION_DATABASE_ID = "YOUR_DATABASE_ID"


# --- Notion Integration ---
def add_transcript_to_notion(transcript):
    notion.pages.create(
        parent={"database_id": NOTION_DATABASE_ID},
        properties={
            "Title": {"title": [{"text": {"content": "Transcript"}}]},
            # Add any other desired properties for your Notion page
            "Transcript": {"rich_text": [{"text": {"content": transcript}}]},
        },
    )
