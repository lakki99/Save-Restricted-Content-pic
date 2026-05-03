# Don't Remove Credit Tg - @VJ_Bots
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import logging
from pyrogram import Client, filters
from pyrogram.types import Message

logger = logging.getLogger(__name__)

# Requirement 1, 2, 3, 4, 7:
# - filters.private: Only private messages
# - ~filters.bot: Ignore bots
# - filters.photo | filters.video | filters.audio: Only these media types
# - Document logic is handled inside the function to check for audio/video mime types
@Client.on_message(
    filters.private &
    ~filters.bot &
    (filters.photo | filters.video | filters.audio | filters.document)
)
async def media_handler(client: Client, message: Message):
    # Requirement 4: If it's a document, only process if it's video or audio
    if message.document:
        mime = message.document.mime_type or ""
        if not (mime.startswith("video/") or mime.startswith("audio/")):
            logger.info(f"Ignoring document with mime type: {mime}")
            return

    logger.info(f"Detected valid media from {message.from_user.id} (Type: {message.media})")

    file_path = None
    status_msg = None
    # Requirement 5: Download the media file
    try:
        # Optional: Operates silently by default to avoid cluttering chat,
        # but you can uncomment message.reply if you want feedback.
        # status_msg = await message.reply("Downloading media...")

        file_path = await message.download()
        if not file_path:
            raise Exception("Download failed")
        logger.info(f"Download success: {file_path}")

        if status_msg:
            await status_msg.edit("Download complete. Uploading to Saved Messages...")
    except Exception as e:
        logger.error(f"Download failure: {e}")
        if status_msg:
            await status_msg.edit(f"Failed to download media: {e}")
        else:
            await message.reply(f"Failed to download media: {e}")
        return

    # Requirement 5: Send/forward to "Saved Messages" (self chat)
    try:
        # "me" is a shortcut for Saved Messages in Pyrogram
        if message.photo:
            await client.send_photo("me", file_path, caption=message.caption)
        elif message.video:
            await client.send_video("me", file_path, caption=message.caption)
        elif message.audio:
            await client.send_audio("me", file_path, caption=message.caption)
        elif message.document:
            await client.send_document("me", file_path, caption=message.caption)

        logger.info("Upload to Saved Messages status: Success")
        if status_msg:
            await status_msg.edit("Media successfully saved to Saved Messages!")
    except Exception as e:
        logger.error(f"Upload to Saved Messages status: Failure - {e}")
        if status_msg:
            await status_msg.edit(f"Failed to upload to Saved Messages: {e}")
    finally:
        # Requirement 6: Delete the local file to save storage
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Deleted local file: {file_path}")
