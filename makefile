PROD_IPA := '192.168.143.237'
STAGING_IPA := '192.168.143.238'
LOCAL_IPA := '192.168.45.233'
PYTHON := .venv/bin/python
CURRENT_DIR := $(shell pwd)


.PHONY: setup
setup: .built_exploit_tree .screenshot_configured .git_initialized .venv/bin/activate .install_stuff .venv/bin/activate
	@ echo "ALL DONE"

.screenshot_configured:
	xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/Print" -r 2>/dev/null || true
	xfconf-query -c xfce4-keyboard-shortcuts -p "/commands/custom/Print" -s "bash -c 'NAME=Screenshot-\$$(date +%Y-%m-%d-%H-%M-%S).png; xfce4-screenshooter --fullscreen --save $(CURRENT_DIR)/IMAGES/\$$NAME && notify-send \"Screenshot Saved\" \"\$$NAME\"'" --create --type string
	mkdir -p $${HOME}/.config/xfce4
	printf "mode=0\nregion=0\naction=1\nscreenshot_dir=file://$(CURRENT_DIR)\nlast-save-directory=$(CURRENT_DIR)\nhost=\ntitle=\ntimestamp=true\n" > $${HOME}/.config/xfce4/xfce4-screenshooter

# .PHONY: .venv/bin/activate
.venv/bin/activate:
	python3 -m venv .venv && . .venv/bin/activate && $(PYTHON) -m pip install --upgrade pip requests beautifulsoup4 lxml mysql_mimic && $(PYTHON) -m pip install flask flask-cors websocket-client

.git_initialized:
	git init
	touch .git_initialized

.install_stuff:
	sudo apt update && sudo apt install -y seclists
	sudo apt update && sudo apt install php php-cli
	touch .install_stuff


.built_exploit_tree:
	mkdir -p IMAGES
	mkdir -p TEMP
	touch note.md
	touch script.py
	touch .built_exploit_tree


host: 
	@ $(PYTHON) -m http.server 4444

debug:
	open http://$(STAGING_IPA):8000/?folder=/home/student/docedit

pull_code: 
	rsync -avz student@$(STAGING_IPA):/home/student/docedit ~/Downloads/

ssh:
	ssh student@${STAGING_IPA}

staging: 
	open http://$(STAGING_IPA)

prod:
	open http://$(PROD_IPA)

run:
	@ $(PYTHON) daves_base_script.py --target http://$(STAGING_IPA) --laddr $(LOCAL_IPA) --lport 4444
	
real:
	@ $(PYTHON) daves_base_script.py --target http://$(PROD_IPA) --laddr $(LOCAL_IPA) --lport 4444
	
ffuf:
	feroxbuster -u http://$(PROD_IPA) -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt -x php,js,json,bak -t 50