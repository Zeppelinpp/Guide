import asyncio
from google.adk.models.lite_llm import LiteLlm
from google.adk.agents.llm_agent import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from src.settings import settings

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")  # Log tool execution
    city_normalized = city.lower().replace(" ", "")  # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C.",
        },
        "london": {
            "status": "success",
            "report": "It's cloudy in London with a temperature of 15°C.",
        },
        "tokyo": {
            "status": "success",
            "report": "Tokyo is experiencing light rain and a temperature of 18°C.",
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have weather information for '{city}'.",
        }



# SETUP
APP_NAME = "weather_app"
USER_ID = "user_123"
SESSION_ID = "session_123"

# DEFINE AGENT WITH LITELLM AND TOOLS
weather_agent = Agent(
    model=LiteLlm(model="dashscope/qwen-turbo", api_key=settings.qwen_config["api_key"]),
    name="weather_agent",
    description="A helpful assistant that can answer questions about the weather.",
    instruction="Answer user questions to the best of your knowledge. Response in a naulty way.",
    tools=[get_weather],
)

# CREATE SESSION SERVICE AND SESSION
session_service = InMemorySessionService()
async def init_session(app_name: str, user_id: str, session_id: str):
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )
    return session
asyncio.run(init_session(APP_NAME, USER_ID, SESSION_ID))

# RUNNER: Orchestrate the agent execution loop
runner = Runner(
    agent=weather_agent,
    app_name=APP_NAME,
    session_service=session_service,
)


async def call_agent_async(user_input: str, runner, user_id: str, session_id: str):
    print(f"\n>>> User: {user_input}")
    content = types.Content(role="user", parts=[types.Part(text=user_input)])

    final_response_text = "Agent did not respond. Please try again."

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        print(f" [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or "Unknown error"}"
            break
    
    print(f"\n<<< Agent Response: {final_response_text}")



asyncio.run(call_agent_async("What is the weather in Tokyo?", runner, USER_ID, SESSION_ID))