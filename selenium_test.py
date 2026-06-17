import time
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def run_tests():
    # Firefox options for headless mode
    options = Options()
    options.add_argument("-headless")
    
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(1280, 1024)
    wait = WebDriverWait(driver, 10)
    
    print("Initialized Firefox WebDriver.")
    
    try:
        # ----------------------------------------------------
        # TEST CASE 1: Login Success (Standard User)
        # ----------------------------------------------------
        print("\n=== Test Case 1: Login Success ===")
        driver.get("https://www.saucedemo.com/")
        
        # Enter username and password
        username_input = wait.until(EC.presence_of_element_located((By.ID, "user-name")))
        password_input = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_input.send_keys("standard_user")
        password_input.send_keys("secret_sauce")
        login_button.click()
        
        # Verify redirect to inventory page
        wait.until(EC.url_to_be("https://www.saucedemo.com/inventory.html"))
        title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".title")))
        assert "Products" in title_element.text
        
        # Capture screenshot
        driver.save_screenshot("sel_login_success.png")
        print("Saved screenshot: sel_login_success.png")
        
        # ----------------------------------------------------
        # TEST CASE 2: Add Product to Cart & Verify Cart
        # ----------------------------------------------------
        print("\n=== Test Case 2: Add Product to Cart ===")
        # Select first product: Sauce Labs Backpack
        add_to_cart_btn = wait.until(EC.element_to_be_clickable((By.ID, "add-to-cart-sauce-labs-backpack")))
        add_to_cart_btn.click()
        
        # Verify cart badge updates to 1
        cart_badge = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "shopping_cart_badge")))
        assert cart_badge.text == "1"
        
        # Click on shopping cart link
        cart_link = driver.find_element(By.CLASS_NAME, "shopping_cart_link")
        cart_link.click()
        
        # Verify URL and correct product in cart
        wait.until(EC.url_to_be("https://www.saucedemo.com/cart.html"))
        item_in_cart = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "inventory_item_name")))
        assert item_in_cart.text == "Sauce Labs Backpack"
        
        driver.save_screenshot("sel_cart_item_added.png")
        print("Saved screenshot: sel_cart_item_added.png")
        
        # ----------------------------------------------------
        # TEST CASE 3: Checkout Process
        # ----------------------------------------------------
        print("\n=== Test Case 3: Checkout Process ===")
        checkout_btn = wait.until(EC.element_to_be_clickable((By.ID, "checkout")))
        checkout_btn.click()
        
        # Enter checkout information
        wait.until(EC.url_to_be("https://www.saucedemo.com/checkout-step-one.html"))
        first_name = driver.find_element(By.ID, "first-name")
        last_name = driver.find_element(By.ID, "last-name")
        postal_code = driver.find_element(By.ID, "postal-code")
        
        first_name.send_keys("Nguyen")
        last_name.send_keys("Van A")
        postal_code.send_keys("100000")
        driver.find_element(By.ID, "continue").click()
        
        # Confirm and finish checkout
        wait.until(EC.url_to_be("https://www.saucedemo.com/checkout-step-two.html"))
        driver.find_element(By.ID, "finish").click()
        
        # Verify checkout completion
        wait.until(EC.url_to_be("https://www.saucedemo.com/checkout-complete.html"))
        complete_header = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "complete-header")))
        assert "Thank you for your order!" in complete_header.text
        
        driver.save_screenshot("sel_checkout_complete.png")
        print("Saved screenshot: sel_checkout_complete.png")
        
        # ----------------------------------------------------
        # TEST CASE 4: Logout
        # ----------------------------------------------------
        print("\n=== Test Case 4: Logout ===")
        # Click hamburger menu
        burger_menu = wait.until(EC.element_to_be_clickable((By.ID, "react-burger-menu-btn")))
        burger_menu.click()
        
        # Click logout link
        logout_link = wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link")))
        logout_link.click()
        
        # Verify redirected back to login page
        wait.until(EC.url_to_be("https://www.saucedemo.com/"))
        assert driver.find_element(By.ID, "login-button").is_displayed()
        
        driver.save_screenshot("sel_logout_success.png")
        print("Saved screenshot: sel_logout_success.png")
        
        print("\nALL TESTS PASSED SUCCESSFULLY!")
        
    except Exception as e:
        driver.save_screenshot("sel_error.png")
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    run_tests()
