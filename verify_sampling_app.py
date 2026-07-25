import os
import time
import subprocess
from playwright.sync_api import sync_playwright

def run_cuj():
    # Start local Python HTTP server in background
    print("Starting background web server...")
    # Kill any process on port 8080 first
    subprocess.run("kill $(lsof -t -i :8080) 2>/dev/null || true", shell=True)

    server_process = subprocess.Popen(
        ["python3", "-m", "http.server", "8080"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for the server to start
    time.sleep(1.5)

    # Ensure verification directories exist
    os.makedirs("/home/jules/verification/videos", exist_ok=True)
    os.makedirs("/home/jules/verification/screenshots", exist_ok=True)

    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="/home/jules/verification/videos",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        try:
            print("Navigating to Le Gouessant App...")
            page.goto("http://localhost:8080/index.html")
            page.wait_for_timeout(1000)

            # --- AUTHENTICATION CUJ ---
            # Fill out the login form
            print("Logging in with chauffeur1 / password123...")
            page.locator("#login-username").fill("chauffeur1")
            page.wait_for_timeout(500)
            page.locator("#login-password").fill("password123")
            page.wait_for_timeout(500)

            # Take screenshot of login screen
            page.screenshot(path="/home/jules/verification/screenshots/01_login_screen.png")

            # Click submit inside login-form specifically to avoid strict-mode violation
            page.locator("#login-form button[type='submit']").click()
            page.wait_for_timeout(1000)

            # Verify we are on dashboard
            print("On Dashboard, verifying KPI cards...")
            page.screenshot(path="/home/jules/verification/screenshots/02_dashboard_loaded.png")

            # --- FORM CREATION CUJ ---
            # Create a new Potato Sampling order
            print("Entering new sampling order...")
            page.locator("#form-lot-number").fill("2026-X45")
            page.wait_for_timeout(500)

            # Select Potato Variety
            page.locator("#form-variety").select_option("Agata")
            page.wait_for_timeout(500)

            # Set Crate Count and Weight
            page.locator("#form-bacs-count").fill("15")
            page.wait_for_timeout(500)
            page.locator("#form-weight").fill("345.8")
            page.wait_for_timeout(500)

            # Set Producer and Location
            page.locator("#form-producer").fill("GAEC de la Vallée - M. Robert")
            page.wait_for_timeout(500)
            page.locator("#form-picking-city").fill("Loudéac")
            page.wait_for_timeout(500)
            page.locator("#form-picking-address").fill("5 Rue de la Fontaine")
            page.wait_for_timeout(500)

            # Set Comment
            page.locator("#form-comment").fill("Excellente qualité. Calibre homogène 35-45mm. Pas d'impacts d'insectes.")
            page.wait_for_timeout(500)

            # Take screenshot before saving
            page.screenshot(path="/home/jules/verification/screenshots/03_form_filled.png")

            # Submit form
            print("Submitting the sampling form...")
            page.locator("#form-btn-submit").click()
            page.wait_for_timeout(1000)

            # --- FILTER / SEARCH CUJ ---
            # Enter search text to filter the table
            print("Filtering the table for Robert...")
            page.locator("#search-query").fill("Robert")
            page.wait_for_timeout(1000)
            page.screenshot(path="/home/jules/verification/screenshots/04_filtered_results.png")

            # Clear search
            page.locator("#search-query").fill("")
            page.wait_for_timeout(500)

            # --- TICKET PREVIEW CUJ ---
            # Click receipt button of the newly created row (or the top row)
            print("Opening print receipt ticket...")
            # Clicking the first receipt button
            page.locator("button[title='Voir / Imprimer le ticket']").first.click()
            page.wait_for_timeout(1000)

            # Take screenshot of the receipt ticket inside modal
            page.screenshot(path="/home/jules/verification/screenshots/05_ticket_receipt_modal.png")

            # Close modal using button ID or generic click
            page.locator("button:has-text('Fermer')").first.click()
            page.wait_for_timeout(500)

            # --- SETTINGS CUJ ---
            # Open settings modal
            print("Opening settings...")
            page.locator("button[title='Paramètres']").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="/home/jules/verification/screenshots/06_settings_modal.png")

            # Go to Admin tab
            print("Switching to Admin Tab...")
            page.locator("#settings-tab-admin").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="/home/jules/verification/screenshots/08_admin_locked_tab.png")

            # Unlock admin tab with 0342 PIN
            print("Unlocking with PIN 0342...")
            page.locator("#admin-pin-input").fill("0342")
            page.wait_for_timeout(500)
            page.locator("button:has-text('Déverrouiller')").click()
            page.wait_for_timeout(1000)
            page.screenshot(path="/home/jules/verification/screenshots/09_admin_unlocked_tab.png")

            # Close settings
            page.locator("button:has-text('Fermer')").last.click()
            page.wait_for_timeout(1000)

            print("Process completed successfully!")
            page.screenshot(path="/home/jules/verification/screenshots/verification.png")

        finally:
            print("Closing context & browser...")
            context.close()
            browser.close()
            print("Stopping background web server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    run_cuj()
