import wave
import asyncio
from livekit import rtc
from livekit.agents import tts, JobContext, Agent, AgentServer
from livekit.agents.voice import AgentSession
# Ensure you import your specific inference/stt/vad modules as well
from livekit.agents import cli, WorkerOptions
import os
from livekit.plugins import openai, deepgram, elevenlabs, silero
os.environ["LIVEKIT_URL"] = "http://127.0.0.1:7880"
os.environ["LIVEKIT_API_KEY"] = "devkey"
os.environ["LIVEKIT_API_SECRET"] = "secret"
#os.environ["DEEPGRAM_API_KEY"] = ""
#os.environ["OPENAI_API_KEY"] = ""
class PreRecordedTTS(tts.TTS):
    def __init__(self, sample_rate: int = 24000):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=sample_rate,
            num_channels=1,
        )

    def synthesize(
        self, text: str, **kwargs
    ) -> "tts.ChunkedStream":
        
        # FIXED: Ensure your default isn't the same as your trigger
        filepath = "ii.wav" 
        if "greet" in text.lower():
            filepath = "ii.wav"
            
        return _WavFileStream(
            tts=self,
            input_text=text,
            filepath=filepath,
            **kwargs
        )

class _WavFileStream(tts.ChunkedStream):
    def __init__(self, tts: tts.TTS, input_text: str, filepath: str, **kwargs):
        super().__init__(tts=tts, input_text=input_text, **kwargs)
        self._filepath = filepath

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        try:
            with wave.open(self._filepath, 'rb') as wf:
                sample_rate = wf.getframerate()
                num_channels = wf.getnchannels()
                
                output_emitter.initialize(
                    request_id="local_wav_playback",
                    sample_rate=sample_rate,
                    num_channels=num_channels,
                    mime_type="audio/pcm"
                )

                chunk_size = int(sample_rate * 0.02) 

                while True:
                    frames = wf.readframes(chunk_size)
                    if not frames:
                        break 
                    
                    output_emitter.push(frames)
                    await asyncio.sleep(0.02)

        except asyncio.CancelledError:
            pass
        
        
# Initialize your server
server = AgentServer()

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    session = AgentSession(
        # Assuming you have inference and silero correctly imported
        stt=deepgram.STT(model="nova-3"),
        llm=openai.LLM(model="gpt-4o"),
        tts=PreRecordedTTS(sample_rate=24000), 
        vad=silero.VAD.load()
        # Assuming TurnHandlingOptions and MultilingualModel are imported from your config
        
    )

    # FIXED: Replaced Assistant() with Agent()
    await session.start(
        room=ctx.room,
        agent=Agent(
            instructions="You are a helpful voice assistant.",
        )
    )

    # FIXED: Bypass the LLM and send the trigger word straight to your custom TTS
    # This avoids OpenAI latency and token costs for pre-recorded greetings.
    await session.say("greet")
    
    
if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=my_agent))