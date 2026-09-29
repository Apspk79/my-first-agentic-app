"""
Image generation function tool for IT Support & Knowledge Base Assistant.
Uses gemini-3.1-flash-lite-image model in global region.
Saves image as an ADK artifact and uploads directly to public GCS bucket.
"""

import uuid
from google import genai
from google.genai import types as genai_types
from google.cloud import storage
from google.adk.tools import ToolContext

# CRITICAL: Hardcode bucket name and project ID as string literals.
BUCKET_NAME = "it-helpdesk-assets-67e0fb58"
PROJECT_ID = "qwiklabs-gcp-01-67e0fb58e2a5"


def generate_it_diagram(topic: str, tool_context: ToolContext) -> str:
    """Generate a technical diagram or illustration for an IT item or concept (e.g. 'VPN Network Setup', 'Server Topology', 'Hardware Connections').

    Args:
        topic: The IT topic or item description to generate a diagram for.
        tool_context: ADK ToolContext to save artifacts.

    Returns:
        Public HTTPS URL of the generated image in Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A clean, professional technical diagram vector illustration showing: {topic}"

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        mime_type = "image/jpeg"
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or mime_type
                break

        if not image_bytes:
            return f"Failed to generate image for topic: '{topic}'."

        ext = "png" if "png" in mime_type else "jpg"
        filename = f"diagram_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload same image bytes directly to public GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        object_key = f"diagrams/{filename}"
        blob = bucket.blob(object_key)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_key}"
        return f"Successfully generated IT diagram for '{topic}'. Public URL: {public_url}"

    except Exception as e:
        return f"Error generating IT diagram: {str(e)}"
