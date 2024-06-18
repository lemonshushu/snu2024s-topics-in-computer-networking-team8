import argparse
import logging
import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Visit a website using Selenium and Firefox."
    )
    parser.add_argument("website", help="The website URL to visit")
    parser.add_argument("host", help="The remote command executor host")
    parser.add_argument("port", help="The remote command executor port")
    parser.add_argument("--http3", action="store_true", help="Enable HTTP/3")
    return parser.parse_args()


def main(website, command_executor, http3_enable):
    options = FirefoxOptions()
    options.add_argument('--private-window')
    if not http3_enable:
        options.set_preference('network.http.http3.enable', False)

    try:
        driver = webdriver.Remote(command_executor=command_executor, options=options)
        driver.implicitly_wait(20)

        logging.info(f"Visiting {website}")
        driver.get(website)

        try:
            WebDriverWait(driver, 20).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            logging.info(
                "Page loaded successfully, waiting for an additional 10 seconds."
            )
            # time.sleep(10)

        except Exception as e:
            logging.error(f"Page did not load within 20 seconds: {e}")

    except Exception as e:
        logging.error(f"An error occurred: {e}")

    finally:
        driver.quit()
        logging.info("Browser closed.")


if __name__ == "__main__":
    setup_logging()
    args = parse_arguments()
    if args.http3:
        print("HTTP/3 is enabled.")
    else:
        print("HTTP/3 is disabled. Falling back to HTTP/2.")
    command_executor = f"http://{args.host}:{args.port}"
    main(args.website, command_executor, args.http3)
