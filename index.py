import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed


class VoterListScraper:
    def __init__(self, proxies=None):
        """
        The function initializes variables for a specific URL and headers in a Python script.
        """
        self.req_url = "https://voterlist.election.gov.np/bbvrs1/index_process_1.php"
        self.headers_list = {
            "Accept": "*/*",
            "User-Agent": "Thunder Client (https://www.thunderclient.com)",
            "Content-Type": "multipart/form-data; boundary=kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A"
        }
        self.proxies = proxies

    def fetch_options(self, payload):
        """
        The function `fetch_options` sends a POST request with a payload to a specified URL and returns
        the JSON result if the response status code is 200.
        
        :param payload: The `payload` parameter in the `fetch_options` method is typically a dictionary
        containing the data that you want to send in the POST request to the specified URL
        (`self.req_url`). This data could include any information or parameters required by the server to
        process the request and provide the desired response
        :return: the "result" key from the JSON response if the status code is 200. Otherwise, it returns
        None.
        """
        response = requests.post(self.req_url, data=payload, headers=self.headers_list, proxies=self.proxies)

        if response.status_code == 200:
            return response.json()["result"]
        return None

    def extract_options(self, html, pattern):
        """
        The function `extract_options` takes in HTML content and a pattern, and returns a list of all
        occurrences of the pattern in the HTML.
        
        :param html: HTML content from which you want to extract options
        :param pattern: The `pattern` parameter in the `extract_options` function is a regular expression
        pattern that is used to search for specific content within the `html` input. The `re.findall`
        function is then used to find all non-overlapping matches of the pattern in the html content and
        return them as a
        :return: The `extract_options` method returns a list of all non-overlapping matches of the
        `pattern` in the `html` string using the `re.findall` function.
        """
        return re.findall(pattern, html)

    def save_link(self, state, district, district_text, vdc, vdc_text, ward, ward_text, reg_centre, reg_centre_text, href):
        """
        The function saves information about a link to a text file in a specific format.
        """
        file_name = str(state) + "_links.txt" # File name format: state_links.txt
        with open(file_name, "a") as save:
            save.write(f"State: {state} District: {district} ({district_text}), VDC: {vdc} ({vdc_text}), Ward: {ward} ({ward_text}), Reg Centre: {reg_centre} ({reg_centre_text}), Link: {href}\n")

    def scrape(self):
        """
        The function `scrape` collects data by iterating through different levels of administrative
        divisions and extracting voter list links.
        """

        state_input = int(input("Enter the state numbe which data you want to scrape (1-7): "))
        state_list = [state_input]

        # Loop for all states

        for state in state_list:
            # Fetch district options
            district_payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"state\"\r\n\r\n{state}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"list_type\"\r\n\r\ndistrict\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
            district_options_html = self.fetch_options(district_payload)
            if not district_options_html:
                print(f"Failed to get district options for State: {state}")
                continue
            
            district_options = self.extract_options(district_options_html, r'<option value="(\d+)">([^<]+)</option>')

            # loop for all districts
            for district, district_text in district_options:
                # Fetch VDC options
                vdc_payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"state\"\r\n\r\n{state}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"district\"\r\n\r\n{district}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"list_type\"\r\n\r\nvdc\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
                vdc_options_html = self.fetch_options(vdc_payload)
                if not vdc_options_html:
                    print(f"Failed to get VDC options for State: {state}, District: {district}")
                    continue

                vdc_options = self.extract_options(vdc_options_html, r'<option value="(\d+)">([^<]+)</option>')

                # loop for all VDCs

                for vdc, vdc_text in vdc_options:
                    # Fetch ward options
                    ward_payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"state\"\r\n\r\n{state}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"district\"\r\n\r\n{district}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"vdc\"\r\n\r\n{vdc}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"list_type\"\r\n\r\nward\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
                    ward_options_html = self.fetch_options(ward_payload)
                    if not ward_options_html:
                        print(f"Failed to get ward options for State: {state}, District: {district}, VDC: {vdc}")
                        continue

                    ward_options = self.extract_options(ward_options_html, r'<option value="(\d+)">([^<]+)</option>')

                    # loop for all wards

                    for ward, ward_text in ward_options:
                        # Fetch registration center options
                        reg_centre_payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"state\"\r\n\r\n{state}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"district\"\r\n\r\n{district}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"vdc\"\r\n\r\n{vdc}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"ward\"\r\n\r\n{ward}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"list_type\"\r\n\r\nreg_centre\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
                        reg_centre_options_html = self.fetch_options(reg_centre_payload)
                        if not reg_centre_options_html:
                            print(f"Failed to get reg_centre options for State: {state}, District: {district}, VDC: {vdc}, Ward: {ward}")
                            continue

                        reg_centre_options = self.extract_options(reg_centre_options_html, r'<option value="(\d+)">([^<]+)</option>')

                        # loop for all registration centers

                        for reg_centre, reg_centre_text in reg_centre_options:
                            # Fetch the final voter list link
                            final_payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"state\"\r\n\r\n{state}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"district\"\r\n\r\n{district}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"vdc_mun\"\r\n\r\n{vdc}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"ward\"\r\n\r\n{ward}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"reg_centre\"\r\n\r\n{reg_centre}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
                            final_response = requests.post("https://voterlist.election.gov.np/bbvrs1/view_ward_1.php", data=final_payload, headers=self.headers_list)

                            if final_response.status_code == 200:
                                pattern = r"<a\s+style=\"color:white\"\s+target=\"_blank\"\s+href='([^']+)'>आफ्नो मतदान केन्द्र हेर्नुहोस्</a>"
                                match = re.search(pattern, final_response.text)
                                if match:
                                    href = match.group(1)
                                    self.save_link(state, district, district_text, vdc, vdc_text, ward, ward_text, reg_centre, reg_centre_text, href)
                                else:
                                    print("Link not found")
                            else:
                                print(f"Failed to get final response for State: {state}, District: {district}, VDC: {vdc}, Ward: {ward}, Reg Centre: {reg_centre}")



if __name__ == "__main__":
    # Create an instance of the scraper and run it
    scraper = VoterListScraper()
    scraper.scrape()
