import os
import sys
import asyncio
import tempfile
from pathlib import Path
from dotenv import load_dotenv

import discord
from discord.ext import commands

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Load environment variables from .env
load_dotenv()

# Add project root to sys.path
BASE_DIR = Path(__file__).parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from stt_service import transcribe_audio
from summarizer import generate_summary, DEFAULT_MODEL, PROVIDER_MODELS
import voice_recorder
import meeting_log

# Configure Discord Intents
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Supported Audio Formats
AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac", ".aac"}
DISCORD_MSG_LIMIT = 1900  # Safe threshold under 2000 chars

# -----------------------------------------------------------------------------
# HELPER: SAFE MESSAGE SEND WITH RETRY FOR WINERROR 121 / NETWORK TIMEOUTS
# -----------------------------------------------------------------------------
async def safe_send(destination, content: str = None, file: discord.File = None, embed: discord.Embed = None):
    """
    Gửi tin nhắn hoặc file đính kèm với cơ chế Retry tự động 
    để khắc phục lỗi WinError 121 (Semaphore Timeout) trên Windows.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            kwargs = {}
            if content:
                kwargs["content"] = content
            if file:
                kwargs["file"] = file
            if embed:
                kwargs["embed"] = embed
                
            return await destination.send(**kwargs)
        except (discord.ClientOSError, OSError, asyncio.TimeoutError) as err:
            print(f"⚠️ [Network Retry] Lỗi kết nối gửi tin nhắn ({err}). Thử lại lần {attempt + 1}/{max_retries}...")
            if attempt == max_retries - 1:
                raise err
            await asyncio.sleep(1.5 * (attempt + 1))
        except Exception as err:
            raise err

@bot.event
async def on_ready():
    print("\n" + "="*60)
    print(f"🤖 DISCORD BOT ĐÃ KẾT NỐI THÀNH CÔNG: {bot.user.name} (ID: {bot.user.id})")
    print("="*60)
    print("📌 Các lệnh hỗ trợ:")
    print("  └─ !note : Upload file MP3 + tóm tắt cuộc họp")
    print("  └─ !start: Bot join Voice Channel & ghi âm bằng py-cord (VoiceClient.start_recording)")
    print("  └─ !stop : Dừng ghi âm & tự động tạo Meeting Notes")
    print("  └─ !help_meeting: Hướng dẫn chi tiết")
    print("="*60 + "\n")

# Bắt lỗi CommandNotFound để tránh log rác khi người dùng gõ !!
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Bỏ qua lỗi khi gõ lệnh không tồn tại (ví dụ: !!)
        return
    print(f"⚠️ [Command Error] {error}")

# -----------------------------------------------------------------------------
# WORKFLOW 1: MANUAL UPLOAD MODE (!note)
# -----------------------------------------------------------------------------
@bot.command(name="note", aliases=["meeting", "tomtat"])
async def manual_note(ctx, *, custom_prompt: str = None):
    """
    Workflow 1: User upload file MP3/Audio + !note -> STT -> LLM Summary -> Meeting Notes
    """
    # Kiểm tra file đính kèm
    if not ctx.message.attachments:
        await safe_send(
            ctx.channel,
            content=(
                "⚠️ **Vui lòng đính kèm 1 file âm thanh MP3/M4A/WAV khi gõ lệnh `!note`!**\n"
                "Ví dụ: Kéo thả file `cuoc_hop.mp3` vào khung chat Discord và gõ `!note`."
            )
        )
        return

    attachment = ctx.message.attachments[0]
    file_ext = Path(attachment.filename).suffix.lower()

    if file_ext not in AUDIO_EXTENSIONS:
        await safe_send(
            ctx.channel,
            content=f"❌ File `{attachment.filename}` không hợp lệ. Hỗ trợ các định dạng: `{', '.join(AUDIO_EXTENSIONS)}`"
        )
        return

    # Thông báo khởi chạy
    status_msg = await safe_send(
        ctx.channel,
        content=(
            f"⏳ **Kute AI Meeting**: Đã nhận file `{attachment.filename}` ({(attachment.size/(1024*1024)):.2f} MB).\n"
            f"🎙️ Đang tải file và tiến hành Speech-to-Text & Tóm tắt LLM (vui lòng chờ trong giây lát)..."
        )
    )

    # Tạo session ngay khi lệnh !note được gọi, audio tải về được ghi thẳng vào meeting_log/
    session_dir = meeting_log.start_session(
        ctx.guild.id,
        ctx.channel.name,
        source="upload",
        metadata={
            "guild_name": ctx.guild.name,
            "channel_id": ctx.channel.id,
            "channel_name": ctx.channel.name,
            "requested_by": str(ctx.author),
            "original_filename": attachment.filename,
        },
    )
    audio_path = meeting_log.audio_path_for(session_dir, file_ext)

    try:
        # Tải mảng bytes về memory và ghi trực tiếp ra đĩa (vào session_dir trong meeting_log/)
        file_bytes = await attachment.read()
        with open(audio_path, "wb") as f:
            f.write(file_bytes)

        # 1. Non-blocking Speech-to-Text (chạy bằng asyncio.to_thread)
        raw_transcript = await asyncio.to_thread(transcribe_audio, str(audio_path))

        # 2. Non-blocking LLM Summarization
        meeting_notes = await asyncio.to_thread(
            generate_summary,
            raw_transcript,
            provider="groq",
            model_name=None,
            custom_system_prompt=custom_prompt
        )

        # 3. Phân tách và gửi kết quả theo giới hạn 2000 ký tự Discord
        await send_meeting_notes_to_channel(ctx.channel, meeting_notes, raw_transcript, attachment.filename)

        # 4. Hoàn tất log cuộc họp (ghi transcript.txt + meeting_notes.md, cập nhật metadata.json)
        try:
            meeting_log.finalize_session(session_dir, raw_transcript, meeting_notes)
        except Exception as e:
            print(f"⚠️ Lỗi khi lưu meeting_log: {e}")

        if status_msg:
            try:
                await status_msg.edit(content=f"✅ **Kute AI Meeting**: Đã hoàn thành tóm tắt cuộc họp cho file `{attachment.filename}`!")
            except Exception:
                pass

    except Exception as e:
        print(f"❌ [!note] Lỗi xử lý file `{attachment.filename}`: {e}")
        err_msg = "❌ **Đã xảy ra lỗi khi xử lý file ghi âm.** Vui lòng thử lại sau."
        if status_msg:
            try:
                await status_msg.edit(content=err_msg)
            except Exception:
                await safe_send(ctx.channel, content=err_msg)
        else:
            await safe_send(ctx.channel, content=err_msg)

# -----------------------------------------------------------------------------
# WORKFLOW 2: AUTOMATIC VOICE CHANNEL RECORDING (!start, !stop, auto-leave)
# -----------------------------------------------------------------------------
@bot.command(name="start", aliases=["join", "ghiam"])
async def start_recording_cmd(ctx):
    """
    Workflow 2: Bot tham gia Voice Channel và ghi âm cuộc họp bằng py-cord (VoiceClient.start_recording)
    """
    if not ctx.author.voice or not ctx.author.voice.channel:
        await safe_send(ctx.channel, content="⚠️ Bạn phải tham gia vào một **Voice Channel (Kênh thoại)** trước khi sử dụng lệnh `!start`!")
        return

    voice_channel = ctx.author.voice.channel
    guild_id = ctx.guild.id

    if voice_recorder.is_recording(guild_id):
        await safe_send(ctx.channel, content="⚠️ Bot đang trong một phiên ghi âm cuộc họp tại phòng thoại khác!")
        return

    # Tạo session ngay khi lệnh !start được gọi; audio từng người nói sẽ được lưu vào đây khi !stop
    session_dir = meeting_log.start_session(
        guild_id,
        voice_channel.name,
        source="voice_recording",
        metadata={
            "guild_name": ctx.guild.name,
            "voice_channel_id": voice_channel.id,
            "voice_channel_name": voice_channel.name,
            "text_channel_id": ctx.channel.id,
            "text_channel_name": ctx.channel.name,
            "requested_by": str(ctx.author),
        },
    )

    # Kết nối tới Voice Channel (VoiceClient mặc định của py-cord đã hỗ trợ ghi âm)
    try:
        if ctx.voice_client:
            voice_client = ctx.voice_client
            await voice_client.move_to(voice_channel)
        else:
            voice_client = await voice_channel.connect()
    except Exception as e:
        print(f"❌ [!start] Lỗi kết nối tới kênh thoại '{voice_channel.name}': {e}")
        await safe_send(ctx.channel, content="❌ Không thể kết nối tới kênh thoại. Vui lòng thử lại sau.")
        return

    # Khởi tạo tiến trình ghi âm; kết quả xử lý (STT + tóm tắt + log) diễn ra trong
    # recording_finished_callback khi !stop được gọi hoặc phòng thoại trống.
    voice_recorder.start_voice_recording(
        guild_id, voice_channel.id, voice_client, recording_finished_callback, ctx.channel, session_dir
    )

    await safe_send(
        ctx.channel,
        content=(
            f"🎙️ **Kute AI Meeting**: Bot đã kết nối tới kênh thoại **{voice_channel.name}** và bắt đầu ghi âm cuộc họp!\n"
            f"💡 Khi kết thúc cuộc họp, hãy gõ `!stop` (hoặc Bot sẽ tự động dừng nếu mọi người rời phòng)."
        )
    )

@bot.command(name="stop", aliases=["leave", "ketthuc"])
async def stop_recording_cmd(ctx):
    """
    Workflow 2: Dừng ghi âm -> kích hoạt recording_finished_callback để rời kênh & tạo Meeting Notes
    """
    guild_id = ctx.guild.id

    if not voice_recorder.is_recording(guild_id):
        await safe_send(ctx.channel, content="⚠️ Hiện không có cuộc họp nào đang được ghi âm!")
        return

    voice_recorder.stop_voice_recording(guild_id)

async def recording_finished_callback(sink: "discord.sinks.Sink", text_channel: discord.TextChannel, session_dir: Path):
    """
    Callback do py-cord tự gọi (async) sau khi VoiceClient.stop_recording() hoàn tất.
    Gộp audio từng người nói, disconnect, chạy STT + tóm tắt và lưu log cuộc họp.
    """
    guild_id = sink.vc.guild.id
    recording_session = voice_recorder.pop_recording_session(guild_id)

    # Disconnect khỏi kênh thoại
    try:
        await sink.vc.disconnect()
    except Exception as e:
        print(f"⚠️ Lỗi disconnect voice: {e}")

    status_msg = await safe_send(
        text_channel,
        content=(
            "⏹️ **Kute AI Meeting**: Đã dừng ghi âm cuộc họp và ngắt kết nối kênh thoại.\n"
            "⚡ Đang tiến hành Speech-to-Text và LLM Tóm tắt cuộc họp..."
        )
    )

    # Gộp audio từng người nói (sink.audio_data) thành 1 file audio.wav trong session_dir
    audio_path = voice_recorder.save_sink_audio(sink, session_dir)
    if not audio_path:
        print("⚠️ Không ghi nhận được giọng nói nào trong phòng thoại. Tạo file WAV mẫu im lặng...")
        empty_path = session_dir / "audio.wav"
        voice_recorder.create_valid_empty_wav(str(empty_path), duration_sec=3.0)
        audio_path = str(empty_path)

    try:
        # Non-blocking STT
        raw_transcript = await asyncio.to_thread(transcribe_audio, audio_path)

        # Non-blocking LLM Summarization
        meeting_notes = await asyncio.to_thread(generate_summary, raw_transcript, "groq")

        # Gửi kết quả lên Channel
        await send_meeting_notes_to_channel(text_channel, meeting_notes, raw_transcript, "Voice_Recording.wav")

        # Hoàn tất log cuộc họp (ghi transcript.txt + meeting_notes.md, cập nhật metadata.json)
        try:
            meeting_log.finalize_session(
                session_dir,
                raw_transcript,
                meeting_notes,
                extra_metadata={
                    "start_time": recording_session["start_time"] if recording_session else None,
                    "speaker_count": len(sink.audio_data),
                },
            )
        except Exception as e:
            print(f"⚠️ Lỗi khi lưu meeting_log: {e}")

        if status_msg:
            await status_msg.edit(content="🎉 **Kute AI Meeting**: Biên bản cuộc họp đã được tạo thành công!")

    except Exception as e:
        print(f"❌ [!stop] Lỗi xử lý biên bản cuộc họp (guild {guild_id}): {e}")
        err_msg = "❌ **Đã xảy ra lỗi khi tạo biên bản cuộc họp.** Vui lòng thử lại sau."
        if status_msg:
            await status_msg.edit(content=err_msg)
        else:
            await safe_send(text_channel, content=err_msg)

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """
    Tự động phát hiện khi phòng thoại trống (chỉ còn lại Bot) -> tự động dừng ghi âm và tạo Meeting Notes
    """
    if before.channel and before.channel != after.channel:
        channel = before.channel
        guild = channel.guild
        voice_client = guild.voice_client

        if voice_client and voice_client.channel == channel and voice_recorder.is_recording(guild.id):
            human_members = [m for m in channel.members if not m.bot]
            if len(human_members) == 0:
                print(f"👥 Kênh thoại {channel.name} không còn thành viên. Tự động ngắt kết nối & tạo Meeting Notes...")
                
                target_text_channel = None
                for c in guild.text_channels:
                    if c.permissions_for(guild.me).send_messages:
                        target_text_channel = c
                        break

                if target_text_channel:
                    await safe_send(target_text_channel, content=f"📢 **Phòng thoại `{channel.name}` đã trống.** Bot tự động kết thúc cuộc họp và tạo biên bản...")

                # Kích hoạt recording_finished_callback (đã đăng ký lúc !start) để xử lý & gửi biên bản
                voice_recorder.stop_voice_recording(guild.id)

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS & DISCORD LIMIT HANDLING
# -----------------------------------------------------------------------------
async def send_meeting_notes_to_channel(channel, meeting_notes: str, raw_transcript: str, original_filename: str):
    """
    Xử lý gửi kết quả tuân thủ giới hạn 2000 ký tự của Discord.
    """
    if len(meeting_notes) <= DISCORD_MSG_LIMIT:
        await safe_send(channel, content=f"📋 **MEETING NOTES** ({original_filename}):\n\n{meeting_notes}")
    else:
        preview_text = meeting_notes[:800] + "\n\n...(Xem toàn bộ nội dung trong file đính kèm bên dưới)..."
        
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as md_file:
            md_file.write(meeting_notes)
            md_path = md_file.name

        try:
            discord_file = discord.File(md_path, filename=f"Meeting_Notes_{Path(original_filename).stem}.md")
            await safe_send(
                channel,
                content=f"📋 **MEETING NOTES (File đính kèm)** - `{original_filename}`:\n\n{preview_text}",
                file=discord_file
            )
        finally:
            if os.path.exists(md_path):
                os.remove(md_path)

@bot.command(name="help_meeting", aliases=["huongdan"])
async def help_meeting_cmd(ctx):
    """Lệnh trợ giúp hướng dẫn sử dụng Bot."""
    embed = discord.Embed(
        title="🤖 Kute AI Meeting Bot - Hướng dẫn sử dụng",
        description="Chuyển đổi ghi âm cuộc họp thành Meeting Notes Markdown tự động bằng Speech-to-Text & LLM.",
        color=0x6366F1
    )
    embed.add_field(
        name="📁 Workflow 1: Upload File Thủ Công",
        value="• Đính kèm file `.mp3`, `.m4a`, `.wav` vào ô chat.\n• Gõ lệnh `!note` (hoặc `!note <Prompt chỉ dẫn tùy chọn>`).\n• Bot sẽ tự động trả về Meeting Notes trực tiếp hoặc đính kèm file `.md`.",
        inline=False
    )
    embed.add_field(
        name="🎙️ Workflow 2: Bot Tự Ghi Âm Kênh Thoại",
        value="• Gõ `!start`: Bot tham gia phòng thoại hiện tại của bạn và bắt đầu ghi âm.\n• Gõ `!stop`: Bot dừng ghi âm, ngắt kết nối và tự động xuất Meeting Notes.\n• **Tự động**: Khi mọi người rời phòng thoại, Bot tự động kết thúc cuộc họp!",
        inline=False
    )
    embed.set_footer(text="Powered by Groq Whisper Large V3 & Llama 3.3 70B")
    await safe_send(ctx.channel, embed=embed)

def main():
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token or token == "your_discord_bot_token_here":
        print("\n❌ LỖI KHỞI CHẠY DISCORD BOT:")
        print("Biến DISCORD_BOT_TOKEN chưa được cấu hình trong file .env!")
        print("Vui lòng truy cập https://discord.com/developers/applications để tạo Bot và cập nhật Token vào file .env.\n")
        sys.exit(1)

    print("🚀 Đang kết nối Discord Bot...")
    bot.run(token)

if __name__ == "__main__":
    main()
