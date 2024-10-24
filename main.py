import threading
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import pandas as pd
from tkinter import *

window = Tk()
window.title("AmazonTR Scrape Price")
window.geometry("500x700")

img = PhotoImage(file="price.png")
img_label = Label(image=img)
img_label.place(x=130, y=30)

link_label = Label(text="Enter Link", font=('Helvetica', 15, 'bold'))
link_label.place(x=210, y=280)

link_entry = Entry(width=50, font=('Helvetica', 10, 'bold'))
link_entry.focus()
link_entry.place(x=88, y=310)
def scrapePrice():
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(1)

        link = link_entry.get()
        product_name = []
        product_price = []
        product_link = []

        driver.get(f"{link}")

        messagebox.showinfo(title="Getting ready!", message="Your list is being prepared. Please wait.")

        while True:
            try:
                items = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//div[contains(@class, "s-result-item s-asin")]')))

                try:
                    cookie_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "sp-cc-accept")))
                    cookie_button.click()
                except (NoSuchElementException, StaleElementReferenceException):
                    pass
                except TimeoutException:
                    pass

                for item in items:
                    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]')))
                    try:
                        name = item.find_element(By.XPATH, './/span[@class="a-size-base-plus a-color-base a-text-normal"]').text
                    except (NoSuchElementException, StaleElementReferenceException):
                        name = "none"
                    product_name.append(name)

                    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, './/span[@class="a-price-whole"]')))
                    try:
                        price = item.find_element(By.XPATH, './/span[@class="a-price-whole"]').text
                    except (NoSuchElementException, StaleElementReferenceException):
                        price = "0"
                    product_price.append(price)

                    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]')))
                    try:
                        link = item.find_element(By.XPATH, './/a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]').get_attribute("href")
                    except (NoSuchElementException, StaleElementReferenceException):
                        link = "none"
                    product_link.append(link)

                try:
                    next_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '//a[contains(@class,"s-pagination-next")]')))
                    next_button.click()
                    WebDriverWait(driver, 30).until(EC.staleness_of(items[0]))
                except TimeoutException:
                    break

            except TimeoutException:
                break

        data = {
            'Product Name': product_name,
            'Price': product_price,
            'Link': product_link
        }

        df = pd.DataFrame(data)
        df.to_html("amazon_products.html", index=False)

        driver.quit()
        messagebox.showinfo(title="Success", message="Your price list is ready ! File name: amazon_products.html\n Note: The application may not have added all the products from the link to the list due to internet connection issues or other reasons.")

    except Exception:
        messagebox.showerror("Error", f"Error: Please enter a valid link.")


def start_automation():
    threading.Thread(target=scrapePrice).start()


start_button = Button(window, text="Scrape Prices", command=start_automation, width=15, font=('Helvetica', 10, 'bold'))
start_button.place(x=195, y=340)
exit_button = Button(text="Exit", width=10, command=lambda: window.destroy(), font=('Helvetica', 10, 'bold'))
exit_button.place(x=208, y=380)

window.mainloop()