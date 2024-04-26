# A simple python script to send POST data to a fake 24 word "recovery" site, you may need to change the postData to align with how the site posts it.
# Response code 200 means it works :)
# This is an updated version which still achieves the same thing as in the video

import requests, random, concurrent.futures, time, json, os, ctypes
from colors import Fore


missing_files = [file for file in ['data/words.txt', 'user-config.json', 'data/dev-config.json', 'data/user-agents.txt'] if not os.path.exists(file)]
if missing_files:
	print(f"{Fore.RED}Missing files: {Fore.RESET}{', '.join(missing_files)}")
	exit()

# load configs and proxies
with open('user-config.json', 'r') as f:
	USER_CONFIG: dict = json.load(f)

with open('data/dev-config.json', 'r') as f:
	DEV_CONFIG: dict = json.load(f)

with open('data/words.txt', 'r') as f:
	WORDS_ARRAY = [word.rstrip() for word in f.readlines()]

with open('data/user-agents.txt', 'r') as f:
	USER_AGENTS = [ua.rstrip() for ua in f.readlines()]

AUTO_REMOVE_BAD_PROXIES = USER_CONFIG.get('auto_remove_bad_proxies', False)
using_proxies_from_file = True # needed for automatically removing bad proxies from the file

if os.path.exists('data/proxies.txt'):
	with open('data/proxies.txt', 'r') as f:
		proxies_array = [{'http': "http://" + proxy.rstrip(), 'https': "https://" + proxy.rstrip()} for proxy in f.readlines()]
else:
	proxies_array = []

if not proxies_array:
	print(f"{Fore.YELLOW}Warning: No proxies found, you may continue but this will most likely wont accomplish anything,{Fore.RESET}")
	print(f"{Fore.YELLOW}optionally I can try and fetch some proxies for you, or you can add them manually in proxies.txt{Fore.RESET}")
	
	if input(f"\n{Fore.BLUE}Would you like me to fetch some proxies for you? (y/n): {Fore.RESET}").lower() == 'y':
		print(f"{Fore.YELLOW}Fetching proxies...{Fore.RESET}")

		proxies = []
		good_sources = 0

		for url in DEV_CONFIG['proxy_sources']:
			try:
				response = requests.get(url)
				if response.status_code == 200:
					proxies.extend(response.text.split('\n'))
					good_sources += 1
			except Exception as e:
				print(f"{Fore.RED}Failed to fetch proxies from {url}{Fore.RESET}")
		
		if not proxies:
			print(f"{Fore.RED}Failed to automatically fetch proxies, you will need to add them manually in proxies.txt or continue without proxies{Fore.RESET}")
			exit()

		# remove any empty strings and duplicates
		proxies = list(set(filter(None, proxies)))

		print(f"{Fore.GREEN}Fetched {len(proxies):,} proxies, from {good_sources:,} source(s){Fore.RESET}")

		# ask the user if they want to save the proxies
		if input(f"\n{Fore.BLUE}Would you like to save the proxies to proxies.txt? (y/n): {Fore.RESET}").startswith() == 'y':
			with open('data/proxies.txt', 'w') as f:
				f.write('\n'.join(proxies))
		else:
			using_proxies_from_file = False
		
		# convert the proxies to the format we need
		proxies_array = [{'http': "http://" + proxy, 'https': "https://" + proxy} for proxy in proxies]
		
	elif input(f"\n{Fore.BLUE}Would you like to continue without proxies? (y/n): {Fore.RESET}").lower() != 'y':
		exit()
def title(t: str) -> None:
    if os.name == "nt":
        ctypes.windll.kernel32.SetConsoleTitleW(t)
    else:
        print(f"\033]0;{t}\007", end="", flush=True)
        
        

print("\n" + Fore.CYAN + "-" * 50 + Fore.RESET)
print(f"{Fore.YELLOW}Loaded {Fore.GREEN}{len(WORDS_ARRAY):,}{Fore.YELLOW} words, {Fore.GREEN}{len(USER_AGENTS):,}{Fore.YELLOW} user-agents, and {Fore.GREEN}{len(proxies_array):,}{Fore.YELLOW} proxies{Fore.RESET}")

AUTO_REMOVE_BAD_PROXIES = AUTO_REMOVE_BAD_PROXIES and using_proxies_from_file


ORIGINAL_PROXY_COUNT = len(proxies_array)

sent_requests = 0
failed_requests = 0

def screwScammers() -> None:
	global sent_requests, failed_requests

	while True:
		try:
			fails = 0
			title(t=f"Screw Scammers | Sent requests: {sent_requests:,} | Failed requests: {failed_requests:,} | Proxies: {len(proxies_array):,}/{ORIGINAL_PROXY_COUNT:,} | Threads: {USER_CONFIG['thread_count']} | made by The 5 Dollar Wrench")

			random_words = random.sample(WORDS_ARRAY, 24)
			post_data = {key:value for (key, value) in zip(USER_CONFIG['post_keys'], random_words)}

			proxy = random.choice(proxies_array) if proxies_array else {}

			try:
				response = requests.post(USER_CONFIG['url'], data=post_data, proxies=proxy, headers={'User-Agent': random.choice(USER_AGENTS)}, timeout=5)
			except requests.exceptions.ProxyError:
				proxies_array.remove(proxy)
				continue

			if response.status_code != 200 or USER_CONFIG['failure_response'] in response.text:
				failed_requests += 1

				if USER_CONFIG['max_failures'] != -1 and (fails := fails + 1) >= USER_CONFIG['max_failures']:
					break

				time.sleep(USER_CONFIG['failure_timeout'])
			else:
				sent_requests += 1
				fails = 0 # reset the fails counter if we successfully send a request
				
		except Exception as e: # most likely a network-related error that can be *somewhat* safely ignored
			pass


def main() -> None:
	with concurrent.futures.ThreadPoolExecutor(max_workers=USER_CONFIG['thread_count']) as executor:
		for _ in range(USER_CONFIG['thread_count']):
			executor.submit(screwScammers)

		last_save = time.time()

		while True:
			print(f"{Fore.CYAN}Sent requests: {Fore.GREEN}{sent_requests:,}{Fore.CYAN}, Failed requests: {Fore.RED}{failed_requests:,}{Fore.CYAN}, Proxies: {Fore.GREEN}{len(proxies_array):,}{Fore.RESET}/{Fore.RED}{ORIGINAL_PROXY_COUNT:,}{Fore.RESET}", end='\r')
			
			if AUTO_REMOVE_BAD_PROXIES and time.time() - last_save >= 0.1:
				with open('data/proxies.txt', 'w') as f:
					f.write('\n'.join([f"{proxy['http'].split('//')[1]}" for proxy in proxies_array]))
				
				last_save = time.time() 
			
			time.sleep(1)

try:
	if __name__ == '__main__':
		main()
except KeyboardInterrupt:
	print(f"\n{Fore.RED}Waiting for threads to exit, press CTRL+C again to force exit{Fore.RESET}")