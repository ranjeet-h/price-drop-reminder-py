import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage
import random
import yagmail

# URL of the product to track
product_url_am = "https://www.amazon.in/ZEEL-Ladies-Waterproof-Solid-Raincoat/dp/B095HTY2V2/ref=pd_ci_mcx_mh_mcx_views_0?pd_rd_w=hJpqE&content-id=amzn1.sym.cd312cd6-6969-4220-8ac7-6dc7c0447352&pf_rd_p=cd312cd6-6969-4220-8ac7-6dc7c0447352&pf_rd_r=B55EACEJFD16BNKSXNZD&pd_rd_wg=KIjqy&pd_rd_r=9f75d664-fdfd-4e9f-bd51-f482fbad2100&pd_rd_i=B095HTY2V2"
product_url_fk = "https://www.flipkart.com/apple-iphone-14-blue-128-gb/p/itmdb77f40da6b6d?pid=MOBGHWFHSV7GUFWA&lid=LSTMOBGHWFHSV7GUFWAIB1T9P&marketplace=FLIPKART&store=tyy%2F4io&srno=b_1_1&otracker=browse&fm=organic&iid=78b404a8-7a5f-4bee-ad80-a8b0bd984abe.MOBGHWFHSV7GUFWA.SEARCH&ppt=hp&ppn=homepage&ssid=7fifnfx29c0000001689510378973"

# Price threshold for the alert
price_threshold = 65999

# Email configuration
sender_email = "**"
sender_password = "**"
receiver_email = "**"
smtp_server = "smtp.gmail.com"
smtp_port = 465

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, observer):
        self.observer = observer

    def on_modified(self, event):
        if not event.is_directory and event.src_path == os.path.abspath(__file__):
            print("Reloading script...")
            self.observer.stop()
            time.sleep(1)
            os.execv(sys.executable, [sys.executable] + sys.argv)

def get_product_price():
    try:
      print("Fetching product page...")
      headers = {
                  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
              }
      

      ip_port_list = [
          "103.149.194.110:32650",
          "103.87.168.109:32650",
          "128.199.17.176:8000",
          "14.139.57.195:23500",
          "103.112.253.229:32650",
          "175.101.85.129:8080",
          "103.138.185.1:83",
          "103.147.128.5:83"
      ]

      # Randomly select an IP address and port from the list
      random_proxy = random.choice(ip_port_list)

      # Create the proxies dictionary
      proxies = {
          "http": random_proxy
      }

      print(proxies)

      # # Proxy configuration
      # proxies = {
      #     "http": "103.149.194.110:32650"
      # }
      # Send HTTP GET request to fetch the product page
      response = requests.get(product_url_fk, headers=headers, proxies=proxies)
      # print("Parsing response...", response)
      response.raise_for_status()
      # print("Parsing response...", response.content)

      # Parse the HTML content
      soup = BeautifulSoup(response.content, "html.parser")
      # print("Beautiful soup", soup)

      # Extract the price element
      price_element = soup.find("div", {"class": "_30jeq3 _16Jk6d"})

      if price_element is None:
          price_element_am = soup.find("span", {"class": "a-price-whole"})
          if price_element_am is not None:
            price_str = price_element_am.text.replace(",", "").replace(".", "")
            price_element = float(price_str)
            print("Price element", price_element)
          else:
            return get_product_price()

      print("Price element", price_element)
      if price_element:
          if isinstance(price_element, float):
            price = price_element
          else:
            # Get the price value as a string and convert it to a float
            price_str = price_element.text.replace(",", "").replace("₹", "")
            price = float(price_str)
          print("Price", price)
          return price
      else:
          return None
    except Exception as e:
      print("Error occurred while fetching the product page", e)
      return None

def send_email_notification(price):
    print("Sending email notification...")
    # Compose the email message
    msg = EmailMessage()
    msg.set_content(f"The price has dropped below {price_threshold}. The current price is {price}.")
    msg["Subject"] = "Price Drop Alert"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
      # # Send the email
      # with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
      #     server.login(sender_email, sender_password)
      #     server.send_message(msg)
      #     print("Email sent to", receiver_email, "from", sender_email, "with the message", msg.get_content())
      # Initialize yagmail with the sender's email and password
      yag = yagmail.SMTP(sender_email, sender_password)

      # Compose the email message
      subject = "Price Drop Alert"
      body = f"The price has dropped below {price_threshold}. The current price is {price}."
      email_content = (body,)

      # Send the email
      yag.send(to=receiver_email, subject=subject, contents=email_content)
    except Exception as e:
      print("Error occurred while sending the email", e)

    # Send the email
    # with smtplib.SMTP(smtp_server, smtp_port) as server:
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     server.send_message(msg)
    #     print("Email sent to", receiver_email, "from", sender_email, "with the message", msg.get_content())

def check_price_drop():
    print("Checking for price drop...")
    # Get the current price
    current_price = get_product_price()
    print("Current price", current_price)
    print("Price threshold", price_threshold)
    if current_price is not None and int(current_price) <= int(price_threshold):
        print("Price dropped below threshold. Current price is", current_price)
        # Send an email notification
        # send_email_notification(current_price)

def main():
    # Run the script to check for price drops continuously
    while True:
        check_price_drop()

        # Delay between iterations (e.g., 1 minute)
        # log the time of the last iteration and show reverse countdown for the next iteration

        remaining_time = 60
        while remaining_time > 0:
            print(f"Waiting for {remaining_time} seconds...", end="\r")
            time.sleep(1)
            remaining_time -= 1
        print("Checking again...")

if __name__ == "__main__":
    event_handler = FileChangeHandler(Observer())
    event_handler.observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(__file__)), recursive=False)
    event_handler.observer.start()

    try:
        main()
    except KeyboardInterrupt:
        event_handler.observer.stop()
    event_handler.observer.join()
