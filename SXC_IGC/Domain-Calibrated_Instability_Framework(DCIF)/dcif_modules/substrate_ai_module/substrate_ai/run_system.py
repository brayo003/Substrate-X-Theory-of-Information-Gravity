# V12_SYNC_VERIFIED: 2026-03-13
import sys
from cognitive_governor_final import CognitiveGovernor

def run():
    # Initialize system
    try:
        gov = CognitiveGovernor(mode="local")
        print("\n🚀 UNIFIED SUBSTRATE AI ONLINE")
        print("Status: EPISTEMIC_STRICT | Substrate: LOCAL_GEMMA")
        print("Type 'exit' to quit.")
    except Exception as e:
        print(f"❌ Initialization Failed: {e}")
        return

    while True:
        try:
            query = input("\n👤 USER: ")
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue

            # Process through the Governor
            result = gov.process_question(query)
            
            print(f"\n🤖 AI: {result['response']}")
            print(f"📊 [METADATA] Tension: {result.get('tension', 0):.2f} | Strategy: {result.get('strategy', 'unknown')}")
        
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ Runtime Error: {e}")

if __name__ == "__main__":
    run()
