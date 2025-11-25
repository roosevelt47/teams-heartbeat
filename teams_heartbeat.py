from playwright.sync_api import sync_playwright
import time
import os
from datetime import datetime

# ===== CONFIGURATION =====
YOUR_EMAIL = "jasraj.johal@purolator.com"  # Replace with your work email
LOOP_SLEEP_MS = 180000  # 3 minutes
RUN_HOURS = 8
SESSION_FILE = "teams_session_backup.json"
# =========================


def main():
    if not os.path.exists(SESSION_FILE):
        print(f"Error: {SESSION_FILE} not found!")
        print("Run save_session.py first to capture your session.")
        return

    print("Starting headless browser with saved session...")

    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
            ],
            ignore_default_args=['--enable-automation'],
        )

        # Create context with saved session
        context = browser.new_context(
            storage_state=SESSION_FILE,
        )

        page = context.new_page()

        # Inject anti-detection scripts
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4, 5],
            });
            window.chrome = { runtime: {} };
        """)

        print("Navigating to Teams...")
        page.goto("https://teams.microsoft.com/v2/",
                  wait_until="domcontentloaded")

        # Wait for page to load
        print("Waiting for Teams to load (20 seconds)...")
        page.wait_for_timeout(20000)

        # Check if we're on login page (session expired)
        if "login" in page.url.lower():
            print("Error: Session expired or Teams redirected to login.")
            print("You may need to log in again with the visible browser.")
            browser.close()
            return

        # Search for your self-chat
        try:
            print(f"Searching for your self-chat ({YOUR_EMAIL})...")

            # Find and click search box
            search_box = page.locator('input[id="ms-searchux-input"]').first
            search_box.wait_for(timeout=10000)
            search_box.click()
            page.wait_for_timeout(500)
            search_box.fill(YOUR_EMAIL)
            page.wait_for_timeout(2000)

            # Click on your profile result
            your_profile = page.locator(
                '[data-tid*="AUTOSUGGEST_SUGGESTION_TOPHITS"]:has-text("(You)")').first
            if your_profile.is_visible(timeout=5000):
                print("✓ Found your profile, opening chat...")
                your_profile.click()
                page.wait_for_timeout(3000)
            else:
                print("⚠ Could not find profile, pressing Enter...")
                page.keyboard.press("Enter")
                page.wait_for_timeout(3000)

        except Exception as e:
            print(f"Warning: Could not auto-navigate to self-chat: {e}")
            print("Continuing anyway...")

        # Find message box
        try:
            print("Looking for message box...")
            message_box = page.locator(
                '[data-tid="ckeditor"][contenteditable="true"]').first
            message_box.wait_for(timeout=30000)
            print("✓ Found message box!")

            # Find send button
            send_button = page.locator(
                '[data-tid="sendMessageCommands-send"]').first
            print("✓ Found send button!")

        except Exception as e:
            print(f"Error: Could not find message box.")
            print(f"Details: {e}")
            print("\nTeams may have blocked headless mode.")
            print("Taking screenshot for debugging...")
            page.screenshot(path="teams_headless_error.png")
            print("Screenshot saved to: teams_headless_error.png")
            browser.close()
            return

        print("\nSending initial message...")
        try:
            # Send initial message
            current_time = datetime.now().strftime("%I:%M:%S %p")
            initial_message = f"Active - {current_time}"

            message_box.click()
            page.keyboard.type(initial_message, delay=100)
            page.wait_for_timeout(500)
            send_button.click()
            print(f"✓ Sent initial message: '{initial_message}'")

            page.wait_for_timeout(3000)

            # Find the last message (the one we just sent)
            print("\n✓✓✓ SUCCESS! Now will edit the message with current time...")
            print(f"\nStarting edit loop for {RUN_HOURS} hours...")
            print("Press Ctrl+C to stop.\n")

            end_time = time.time() + RUN_HOURS * 60 * 60
            cycle_count = 0
            consecutive_failures = 0

            while time.time() < end_time:
                try:
                    # Close any notification popups that might block interactions
                    try:
                        notification_close = page.locator(
                            '[data-tid="app-layout-area--in-app-notifications"] button[aria-label*="Close"], [data-tid="app-layout-area--in-app-notifications"] button[aria-label*="Dismiss"]').first
                        if notification_close.is_visible(timeout=1000):
                            notification_close.click()
                            page.wait_for_timeout(500)
                    except:
                        pass  # No notifications to close

                    # Ensure we're on the chat view (scroll to make message visible)
                    last_message = page.locator(
                        '[data-tid="chat-pane-message"]').last

                    # Wait for message to be in viewport and visible
                    try:
                        last_message.scroll_into_view_if_needed(timeout=5000)
                        page.wait_for_timeout(500)
                    except:
                        # If scroll fails, try clicking on the message box to refocus the chat
                        message_box.click()
                        page.wait_for_timeout(1000)
                        last_message.scroll_into_view_if_needed(timeout=5000)

                    # Now hover to show buttons
                    last_message.hover(force=True)
                    page.wait_for_timeout(1000)

                    # Click the edit button (find it globally since it appears on hover)
                    edit_button = page.locator(
                        'button[data-tid="message-actions-edit"]').first
                    edit_button.wait_for(state="visible", timeout=5000)
                    edit_button.click()
                    page.wait_for_timeout(500)

                    # The message box becomes active for editing
                    # Select all and replace with new time
                    page.keyboard.press("Control+A")
                    page.wait_for_timeout(200)

                    current_time = datetime.now().strftime("%I:%M:%S %p")
                    new_message = f"Active - {current_time}"
                    page.keyboard.type(new_message, delay=50)
                    page.wait_for_timeout(500)

                    # Click the "Done" button to save the edit
                    done_button = page.locator(
                        'button[data-tid="newMessageCommands-send"][name="done"]').first
                    done_button.click()

                    cycle_count += 1
                    consecutive_failures = 0  # Reset failure count on success
                    if cycle_count % 10 == 0:
                        print(
                            f"Updated message {cycle_count} times... Current time: {current_time}")

                    page.wait_for_timeout(LOOP_SLEEP_MS)

                except Exception as e:
                    consecutive_failures += 1
                    print(f"Error editing message: {e}")
                    
                    if consecutive_failures >= 3:
                        print(f"\n⚠ Failed {consecutive_failures} times in a row. Session may have expired.")
                        print("Please run save_session.py again to refresh your session, then restart the bot.")
                        browser.close()
                        return
                    
                    print(f"Retrying in 10 seconds... (Attempt {consecutive_failures}/3)")
                    time.sleep(10)

            print(f"\nDone! Updated message {cycle_count} times total.")

        except Exception as e:
            print(f"Error: {e}")
            print("Taking screenshot...")
            page.screenshot(path="teams_headless_edit_error.png")
            print("Screenshot saved to: teams_headless_edit_error.png")

        browser.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
