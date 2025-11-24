from playwright.sync_api import sync_playwright
import json
import os

def main():
    with sync_playwright() as p:
        print("Connecting to your browser on port 9222...")
        browser = p.chromium.connect_over_cdp("http://localhost:9222")
        
        contexts = browser.contexts
        if not contexts:
            print("Error: No browser context found.")
            return
            
        context = contexts[0]
        
        print("Capturing session state...")
        
        # Save storage state (cookies, localStorage, etc.)
        storage_state = context.storage_state()
        
        # Save to file
        state_file = "teams_session_backup.json"
        with open(state_file, 'w') as f:
            json.dump(storage_state, f, indent=2)
        
        print(f"✓ Session saved to: {state_file}")
        print(f"  - {len(storage_state.get('cookies', []))} cookies saved")
        print(f"  - {len(storage_state.get('origins', []))} localStorage origins saved")
        
        browser.close()
        
        print("\nYou can now use this session in other scripts!")
        print("The session will also remain in: C:\\temp\\edge_debug")


if __name__ == "__main__":
    main()
