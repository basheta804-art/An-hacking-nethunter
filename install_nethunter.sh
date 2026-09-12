#!/data/data/com.termux/files/usr/bin/bash
# AN Hacking - NetHunter Rootless Installer
# Tested on: Termux, Kali NetHunter Rootless

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_banner() {
    echo -e "${BLUE}"
    echo "    █████╗ ███╗   ██╗    ██████╗  █████╗  ██████╗██╗  ██╗██╗███╗   ██╗ ██████╗"
    echo "   ██╔══██╗████╗  ██║    ██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██║████╗  ██║██╔════╝"
    echo "   ███████║██╔██╗ ██║    ██████╔╝███████║██║     █████╔╝ ██║██╔██╗ ██║██║  ███╗"
    echo "   ██╔══██║██║╚██╗██║    ██╔══██╗██╔══██║██║     ██╔═██╗ ██║██║╚██╗██║██║   ██║"
    echo "   ██║  ██║██║ ╚████║    ██║  ██║██║  ██║╚██████╗██║  ██╗██║██║ ╚████║╚██████╔╝"
    echo "   ╚═╝  ╚═╝╚═╝  ╚═══╝    ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝"
    echo -e "${NC}"
    echo -e "${GREEN}[*] NetHunter Rootless Edition Installer${NC}"
    echo ""
}

check_termux() {
    if [ ! -d "/data/data/com.termux" ]; then
        echo -e "${YELLOW}[!] Warning: Not running in Termux environment${NC}"
        read -p "Continue anyway? (y/n): " choice
        if [ "$choice" != "y" ]; then
            exit 1
        fi
    fi
}

update_packages() {
    echo -e "${BLUE}[*] Updating packages...${NC}"
    pkg update -y
    pkg upgrade -y
}

install_core() {
    echo -e "${BLUE}[*] Installing core dependencies...${NC}"
    
    pkg install -y \
        python \
        python-pip \
        nmap \
        nikto \
        git \
        curl \
        wget \
        perl \
        ruby \
        php \
        openssl-tool \
        dnsutils \
        whois \
        net-tools \
        iproute2 \
        procps
}

install_python_tools() {
    echo -e "${BLUE}[*] Installing Python tools...${NC}"
    
    pip install --upgrade pip
    
    pip install \
        python-nmap \
        requests \
        beautifulsoup4 \
        dnspython \
        urllib3 \
        certifi
}

install_nethunter_tools() {
    echo -e "${BLUE}[*] Installing NetHunter specific tools...${NC}"
    
    # Install whatweb if not present
    if ! command -v whatweb &> /dev/null; then
        echo -e "${YELLOW}[*] Installing whatweb...${NC}"
        git clone https://github.com/urbanadventurer/whatweb.git $PREFIX/share/whatweb
        ln -sf $PREFIX/share/whatweb/whatweb $PREFIX/bin/whatweb
    fi
    
    # Install testssl.sh
    if ! command -v testssl.sh &> /dev/null; then
        echo -e "${YELLOW}[*] Installing testssl.sh...${NC}"
        git clone --depth 1 https://github.com/drwetter/testssl.sh.git $PREFIX/share/testssl.sh
        ln -sf $PREFIX/share/testssl.sh/testssl.sh $PREFIX/bin/testssl.sh
    fi
}

setup_storage() {
    echo -e "${BLUE}[*] Setting up storage...${NC}"
    
    # Create working directory
    mkdir -p $HOME/AN-Hacking/{reports,wordlists,scans,modules}
    
    # Request storage permission (Termux)
    if [ -d "/data/data/com.termux" ]; then
        termux-setup-storage
    fi
    
    # Download common wordlists
    echo -e "${YELLOW}[*] Downloading wordlists...${NC}"
    cd $HOME/AN-Hacking/wordlists
    
    # Small wordlists for mobile
    curl -o common.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/Web-Content/common.txt
    curl -o subdomains.txt https://raw.githubusercontent.com/danielmiessler/SecLists/master/Discovery/DNS/subdomains-top1million-5000.txt
}

download_an_hacking() {
    echo -e "${BLUE}[*] Downloading AN Hacking...${NC}"
    
    cd $HOME/AN-Hacking
    
    # Download main script (replace with your GitHub URL)
    curl -o an_hacking_nethunter.py https://raw.githubusercontent.com/YOUR_USERNAME/an-hacking/main/an_hacking_nethunter.py
    chmod +x an_hacking_nethunter.py
    
    # Create launcher
    echo '#!/bin/bash' > $PREFIX/bin/an-hacking
    echo 'cd $HOME/AN-Hacking && python an_hacking_nethunter.py' >> $PREFIX/bin/an-hacking
    chmod +x $PREFIX/bin/an-hacking
}

print_completion() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║     Installation Complete!                                  ║"
    echo "╠════════════════════════════════════════════════════════════╣"
    echo "║  Usage:                                                    ║"
    echo "║    an-hacking          # Launch interactive menu          ║"
    echo "║    cd ~/AN-Hacking     # Working directory                ║"
    echo "║                                                            ║"
    echo "║  Working Directory: ~/AN-Hacking                          ║"
    echo "║  Reports: ~/AN-Hacking/reports/                           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Main execution
print_banner
check_termux
update_packages
install_core
install_python_tools
install_nethunter_tools
setup_storage
download_an_hacking
print_completion