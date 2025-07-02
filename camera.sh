#1. Check if the python3.11 available it not 
#
#   load downlaod folder with deps

#2. check if venv is present or not 
#
# if not load it

#3. check if the model pth is or not if not laod them 
#
#load the model path

#4. run venv and then run the main.py
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

# A shell function you can call any time to jump back here
goto_here() {
    cd "$SCRIPT_DIR" || return
}

require_net() {
  ping -c1 -W"${2:-2}" "${1:-8.8.8.8}" >/dev/null 2>&1 && 
    echo "✔ Internet reachable (${1:-8.8.8.8})" || {
    echo "✖ No Internet connection — exiting." >&2
    exit 1
  }
}

check_directory() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo "✅ Directory '$dir' exists."
        cd python-offline
        sudo apt install ./*.deb
    else
        echo "❌ Directory '$dir' does not exist."
        require_net
        echo "creating file and downloading from net"
        mkdir python-offline
        cd python-offline
        apt-get download python3.11 python3.11-venv ffmpeg
        sudo apt install apt-rdepends
        apt-rdepends python3.11 python3.11-venv python3.11-distutils ffmpeg \
          | grep -v "^ " \
          | xargs apt-get download

        sudo apt install ./*.deb
    fi
}

checkk() {
    local dir="$1"
    if [ -d "$dir" ]; then
        echo "✅ Directory '$dir' exists."
        source venv/bin/activate
    else
        python3.11 -m venv venv
        source venv/bin/activate
        pip install -r require.txt
    fi
}


isinstalled() {
  if apt list --installed 2>/dev/null | grep -q "^$1/"; then
    echo "✅ $1 is installed."
    checkk venv
    cp -r ./models/torch ~/.cache/torch
    cd face_recog
    python3.11 main.py


  else
    echo "❌ $1 is NOT installed."
    check_directory python-offline
    goto_here
    cp -r ./models/torch ~/.cache/torch
  fi
}


isinstalled python3.11

