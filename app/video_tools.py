"""
Video generation function tool for IT Support & Knowledge Base Assistant.
Uses gemini-omni-flash-preview model in global region.
Saves video as an ADK artifact and uploads directly to public GCS bucket.
"""

import uuid
from google import genai
from google.genai import types as genai_types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcode bucket name and project ID as string literals.
BUCKET_NAME = "it-helpdesk-assets-67e0fb58"
PROJECT_ID = "qwiklabs-gcp-01-67e0fb58e2a5"


def generate_it_video(topic: str, tool_context: ToolContext) -> str:
    """Generate a short video animation or tutorial for an IT item, procedure, or concept (e.g. 'Laptop Cable Setup', 'Server Restart Sequence Video', 'Router Setup Guide').

    Args:
        topic: The IT topic, hardware procedure, or concept to generate a short video for.
        tool_context: ADK ToolContext to save artifacts.

    Returns:
        Public HTTPS URL of the generated video in Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    prompt = f"A clear, modern technical animation demonstrating IT concept: {topic}"

    try:
        video_bytes = None
        mime_type = "video/mp4"

        try:
            interaction = client.interactions.create(
                model="gemini-omni-flash-preview",
                input=prompt,
                response_format={"type": "video", "delivery": "inline"},
            )
            if hasattr(interaction, "outputs") and interaction.outputs:
                for out in interaction.outputs:
                    if hasattr(out, "video") and out.video:
                        video_bytes = getattr(out.video, "bytes", None) or getattr(out.video, "data", None)
                        mime_type = getattr(out.video, "mime_type", mime_type)
                        if video_bytes:
                            break
            if not video_bytes and hasattr(interaction, "output_video"):
                ov = interaction.output_video
                video_bytes = getattr(ov, "bytes", None) or getattr(ov.data, "bytes", None)
        except Exception:
            pass

        if not video_bytes:
            try:
                response = client.models.generate_content(
                    model="gemini-omni-flash-preview",
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        response_modalities=["VIDEO"],
                    ),
                )
                for part in response.candidates[0].content.parts:
                    if part.inline_data:
                        video_bytes = part.inline_data.data
                        mime_type = part.inline_data.mime_type or mime_type
                        break
            except Exception:
                pass

        if not video_bytes:
            return f"Failed to generate video for topic: '{topic}'."

        ext = "mp4" if "mp4" in mime_type else "webm"
        filename = f"video_{uuid.uuid4().hex[:8]}.{ext}"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = genai_types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
        tool_context.save_artifact(filename=filename, artifact=artifact_part)

        # 2. Upload same video bytes directly to public GCS bucket (no local file)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        object_key = f"videos/{filename}"
        blob = bucket.blob(object_key)
        blob.upload_from_string(video_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_key}"
        return f"Successfully generated IT video for '{topic}'. Public URL: {public_url}"

    except Exception as e:
        return f"Error generating IT video: {str(e)}"
