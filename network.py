import requests

def POST_CSV(url: str, csv_content: str):
    headers = {
        "Content-Type": "text/csv"
    }

    try:
        response = requests.post(url, headers=headers, data=csv_content)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text)

    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    url = "https://bci-uscneuro.tech/api/upload"
    # change this to grab 127 lines of csv data, or add lines sequentially
    csv_content = "message\ntest\n"

    # change this condition to post once csv content is 127 rows in size?
    while True:
    	POST_CSV(url, csv_content)
	time.sleep(1)
