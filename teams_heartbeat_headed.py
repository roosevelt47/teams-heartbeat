from playwright.sync_api import sync_playwright
import time
from datetime import datetime

# ===== CONFIGURATION =====
# Replace with your work email (not used in headed version)
YOUR_EMAIL = "email@example.com"
LOOP_SLEEP_MS = 180000  # 3 minutes
RUN_HOURS = 8
# =========================


def main():
    print("Connecting to running Edge browser on port 9222...")
    print("Make sure Edge is running with: --remote-debugging-port=9222")
    print()

    with sync_playwright() as p:
        try:
            # Connect to existing browser
            browser = p.chromium.connect_over_cdp("http://localhost:9222")

            # Get the default context (the real browser's context)
            context = browser.contexts[0]

            # Get or create page
            if len(context.pages) > 0:
                page = context.pages[0]
            else:
                page = context.new_page()

            print(f"Connected! Current URL: {page.url}")

            # Navigate to Teams if not already there
            if "teams.microsoft.com" not in page.url:
                print("Navigating to Teams...")
                page.goto("https://teams.microsoft.com/v2/",
                          wait_until="domcontentloaded")
                page.wait_for_timeout(5000)

            print("Waiting for message box to be ready...")

            # Find message box
            message_box = page.locator(
                '[data-tid="ckeditor"][contenteditable="true"]').first
            message_box.wait_for(timeout=30000)
            print("✓ Found message box!")

            # Find send button
            send_button = page.locator(
                '[data-tid="sendMessageCommands-send"]').first
            print("✓ Found send button!")

            print("\nSending initial message...")

            # Send initial message
            current_time = datetime.now().strftime("%I:%M:%S %p")
            initial_message = f"Active - {current_time}"

            message_box.click()
            page.keyboard.type(initial_message, delay=100)
            page.wait_for_timeout(500)
            send_button.click()
            print(f"✓ Sent initial message: '{initial_message}'")

            page.wait_for_timeout(3000)

            # Now start editing loop
            print("\n✓✓✓ SUCCESS! Now will edit the message with current time...")
            print(f"\nStarting edit loop for {RUN_HOURS} hours...")
            print("Press Ctrl+C to stop.\n")

            end_time = time.time() + RUN_HOURS * 60 * 60
            cycle_count = 0

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
                    if cycle_count % 10 == 0:
                        print(
                            f"Updated message {cycle_count} times... Current time: {current_time}")

                    page.wait_for_timeout(LOOP_SLEEP_MS)

                except Exception as e:
                    print(f"Error editing message: {e}")
                    print("Retrying in 10 seconds...")
                    time.sleep(10)

            print(f"\nDone! Updated message {cycle_count} times total.")

        except Exception as e:
            print(f"Error: {e}")
            print("\nMake sure:")
            print("1. Edge is running with --remote-debugging-port=9222")
            print("2. You're logged into Teams")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped by user.")
