"""Quick test script to verify Gemini integration."""
import asyncio
import sys
sys.path.insert(0, '/Users/apple/Data/Certified-Cloud-Applied-Generative-AI-Engineering/Q4-Agentic-AI/ai_driven_development/Hackathons/02-evolution-of-todo/Phase-III-AI-Chatbot/backend')

from src.agent import get_agent_response, openai_client, DEFAULT_MODEL

async def test_gemini():
    """Test Gemini API integration."""
    print(f"🔍 Testing Gemini Integration")
    print(f"✓ Client initialized: {openai_client is not None}")
    print(f"✓ Using model: {DEFAULT_MODEL}")
    print()

    if not openai_client:
        print("❌ No LLM client initialized!")
        return

    # Test simple message
    print("📤 Sending test message: 'Create a task to buy groceries tomorrow'")
    response = await get_agent_response(
        user_message="Create a task to buy groceries tomorrow",
        conversation_history=[],
        user_id=1  # Test user ID
    )

    print()
    print("📨 Response received:")
    print(f"✓ Response text: {response.get('response', 'N/A')[:200]}...")
    print(f"✓ Tool calls: {len(response.get('tool_calls', []))} tool(s) executed")

    if response.get('tool_calls'):
        for tool in response['tool_calls']:
            print(f"  - {tool.get('tool_name')}: {tool.get('result', {}).get('success', False)}")

    if response.get('error'):
        print(f"❌ Error: {response['error']}")
    else:
        print()
        print("✅ Gemini integration test PASSED!")

if __name__ == "__main__":
    asyncio.run(test_gemini())
