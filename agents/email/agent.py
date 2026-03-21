"""
Communications Agent for PreCall Briefing

Parses Slack channel exports to extract conversation context, key points, and action items.
Supports Slack export JSON format.
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Communications Agent")

import os
DATA_DIR = Path(os.getenv("COMMS_DATA_PATH", "./data/slack"))


class QueryRequest(BaseModel):
    client_name: str
    days_back: Optional[int] = 14


def normalize_name(value: str) -> str:
    """Normalize names for robust matching across datasets."""
    return "".join(ch for ch in value.lower() if ch.isalnum())


def find_slack_channel(client_name: str) -> Optional[Path]:
    """Find Slack export file matching client name."""
    client_lower = client_name.lower().replace(" ", "-")
    client_norm = normalize_name(client_name)
    
    for file in DATA_DIR.glob("*.json"):
        file_norm = normalize_name(file.stem)
        if client_lower in file.stem.lower() or file.stem.lower() in client_lower or client_norm in file_norm:
            return file
    
    # Try partial match
    for file in DATA_DIR.glob("*.json"):
        # Check inside file for channel name
        try:
            with open(file) as f:
                data = json.load(f)
                channel_name = data.get("channel", {}).get("name", "")
                if client_lower in channel_name.lower() or client_norm in normalize_name(channel_name):
                    return file
        except:
            continue
    
    return None


def parse_slack_export(file_path: Path, days_back: int = 14) -> dict:
    """Parse Slack export JSON and extract relevant information."""
    with open(file_path) as f:
        data = json.load(f)
    
    channel = data.get("channel", {})
    users = data.get("users", {})
    messages = data.get("messages", [])
    summary = data.get("summary", {})
    
    # Filter messages by date
    cutoff = datetime.now() - timedelta(days=days_back)
    recent_messages = []
    
    for msg in messages:
        msg_date = msg.get("date")
        if msg_date:
            try:
                msg_datetime = datetime.fromisoformat(msg_date.replace("Z", "+00:00"))
                if msg_datetime.replace(tzinfo=None) >= cutoff:
                    recent_messages.append(msg)
            except:
                recent_messages.append(msg)  # Include if date parsing fails
    
    # Format messages with user names
    formatted_messages = []
    for msg in recent_messages:
        user_id = msg.get("user", "")
        user_info = users.get(user_id, {})
        formatted_messages.append({
            "timestamp": msg.get("date"),
            "from": user_info.get("name", user_id),
            "is_internal": user_info.get("is_internal", False),
            "text": msg.get("text", ""),
            "reactions": msg.get("reactions", [])
        })
    
    # Build threads from messages (group by topic/time proximity)
    threads = []
    if formatted_messages:
        # For simplicity, treat all messages as one thread
        threads.append({
            "channel": channel.get("name", "unknown"),
            "messages": formatted_messages,
            "participant_count": len(set(m.get("from") for m in formatted_messages)),
            "message_count": len(formatted_messages)
        })
    
    return {
        "channel": {
            "name": channel.get("name"),
            "purpose": channel.get("purpose"),
            "member_count": len(users)
        },
        "threads": threads,
        "summary": {
            "total_messages": len(recent_messages),
            "date_range": summary.get("date_range", {}),
            "key_topics": summary.get("key_topics", []),
            "sentiment": summary.get("sentiment", "neutral")
        },
        "action_items": summary.get("pending_items", []),
        "key_concerns": summary.get("key_topics", [])
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    files = list(DATA_DIR.glob("*.json"))
    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "files_found": len(files)
    }


@app.post("/query")
async def query(request: QueryRequest):
    """Query for Slack conversations related to a client."""
    file_path = find_slack_channel(request.client_name)
    
    if not file_path:
        return {"error": f"No Slack channel found for '{request.client_name}'"}
    
    try:
        return parse_slack_export(file_path, request.days_back)
    except Exception as e:
        return {"error": f"Failed to parse Slack export: {str(e)}"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
