from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from math import floor

from time import sleep
import signal
import os

help_text = """ Spot Commands:
    pl [index] - Goes to the specified playlist, or lists them.
	s [index] - Goes to the specified song, or lists them.
	p - Play/Pause.
	n - Next.
	b - Back.
	sh - Toggle Shuffle.
	re - Toggle Repeat.
	run [expr] - (Debug command) Python Eval.
"""

print("Loading...")

options = Options()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)


def login():
	driver.implicitly_wait(30)
	driver.get("https://accounts.spotify.com/login")
	driver.find_elements_by_css_selector("input")[0].send_keys(os.environ.get("SPOT_USER"))
	driver.find_elements_by_css_selector("input")[1].send_keys(os.environ.get("SPOT_PASS"))
	sleep(2)
	driver.find_elements_by_css_selector("button")[0].click()
	sleep(2)

scroll_code = """
setInterval(function(){
	for(let x of document.getElementsByTagName('div'))
		x.scrollTop = x.scrollHeight
	},
1000)
"""

song_scroll = """
song = document.querySelectorAll("ol > div > div > li")[%]
for(let x of document.getElementsByTagName("div"))
	x.scrollTop = song.scrollTop
"""

shuffle_on = """
return !document.body.innerHTML.includes('title="Enable shuffle"')
"""

repeat_on = """
return !document.body.innerHTML.includes('title="Enable repeat"')
"""

shuffle = repeat = playlists = play = skip = previous = None
current_playlist = 0
songs = []

def get_context():
	global playlists, play, skip, previous
	playlists = driver.find_elements(By.XPATH, "//hr/following-sibling::div//a")
	shuffle, previous, play, skip, repeat = driver.find_elements_by_css_selector(".control-button")[1:6]

def print_song(id, song, artist, album, duration):
	if(duration == "ADD"):
		return
	columns, _ = os.get_terminal_size()
	width = floor(columns / 15)
	s = str(id).ljust(width, ".")[:width - 1] + "."
	s += song.ljust(7 * width, ".")[:7 * width - 1] + "."
	s += artist.ljust(3 * width, ".")[:3 * width - 1] + "."
	s += album.ljust(3 * width, ".")[:3 * width - 1] + "."
	s += duration.ljust(width, ".")[:width - 1] + "."
	print(s)

login()
driver.get("https://open.spotify.com")
get_context()
print("Ready!")

while (command := input("> ")) != "q":
	try:
		args = command.split()

		if args[0] == "pl":
			if len(args) == 1:
				for i in range(len(playlists)):
					print(f" {i}. {playlists[i].text}")
			elif int(args[1]) in range(len(playlists)):
				playlists[int(args[1])].click()
				current_playlist = int(args[1])
				driver.execute_script(scroll_code)
				get_context()
			else:
				print("Playlist not found.")
		
		elif args[0] == "s":
			songs = driver.find_elements(By.XPATH, "//ol//li")
			if(len(args) == 1):
				print_song("ID" ,"SONG", "ARTIST", "ALBUM", "DURATION")
				for i in range(len(songs)):
					name, artist, _, album, duration = songs[i].text.split("\n")
					print_song(i, name, artist, album, duration)
			elif int(args[1]) in range(len(songs)):
				driver.execute_script(song_scroll.replace("%", args[1]))
				songs[int(args[1])].find_elements(By.TAG_NAME, "div")[0].click()
				songs[int(args[1])].find_elements(By.TAG_NAME, "div")[1].click()

		elif args[0] == "p":
			play.click()
		
		elif args[0] == "n":
			skip.click()
		
		elif args[0] == "b":
			previous.click()
		
		elif args[0] == "sh":
			if(driver.execute_script(shuffle_on)):
				print("Turning shuffle OFF")
			else:
				print("Turning shuffle ON")
			driver.find_elements_by_css_selector(".control-button")[1].click()

		elif args[0] == "re":
			if(driver.execute_script(repeat_on)):
				print("Turning repeat OFF")
			else:
				print("Turning repeat ON")
			driver.find_elements_by_css_selector(".control-button")[5].click()

		elif args[0] == "run":
			exec(" ".join(args[1:]))
		
		elif args[0] == "h":
			print(help_text)
		
		else:
			print(f"Command '{args[0]}' not found.")

	except:
		print("Command Failed.")

driver.quit()
exit()
