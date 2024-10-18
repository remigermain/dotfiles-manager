#!/usr/bin/env bash
# shellcheck disable=SC2155,SC2034,SC1091,SC2207
#--------------------------------------------
#   oh-my-zsh settings
#--------------------------------------------
export LANG=en_US.UTF-8
export ZSH="$HOME/.oh-my-zsh"

hascmd () {
	if command -v "$1" &>/dev/null; then
		return 0
	fi
	return 1
}

select_command() {
	for cmd in "$@"; do
		if hascmd "$cmd" ; then
			echo "$cmd"
			return
		fi
	done
	echo "echo command not found"
}

# safe set alias if "from" and "to" are different
safe-alias() {
	from=$1
	to=$2
	if [[ "$from" != "$to" ]]; then
		# shellcheck disable=SC2139
		alias "$from"="$to"
	fi
}

errx () {
	echo "$1"
	exit 1
}

export VSCODEAPP="$(select_command codium code)"
export EDITOR="$(select_command vim neovim vi nano)"
export DISABLE_UNTRACKED_FILES_DIRTY="true"

export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
export RUST_BACKTRACE=full

export BASE_DIR_PATH="$HOME/.myconfig"
export APP_PATH="$BASE_DIR_PATH/app"
export BIN_PATH="$BASE_DIR_PATH/bin"
export SCRIPTS_PATH="$BASE_DIR_PATH/scripts"
export WORKSPACES_PATH="$HOME/workspaces"
export DOTFILE_PATH="$WORKSPACES_PATH/dotfiles"

# no ( venv ) in prompt
export VIRTUAL_ENV_DISABLE_PROMPT=1

export CHROME_EXECUTABLE="$(select_command chromium-browser chrome firefox)"
export PATH=$PATH:$APP_PATH:$BIN_PATH:$HOME/.local/bin:$(find -H "$SCRIPTS_PATH" -type d | tr "\n" ":" | rev | cut -c 2- | rev)
export PATH="${KREW_ROOT:-$HOME/.krew}/bin:$PATH:$HOME/.cargo/bin"
export MANPATH=/usr/share/man
export ZSH_THEME="agnoster"
fpath="$ZSH/custom/completions $fpath"

# ---------------
# Zsh
# ---------------
setopt shwordsplit
plugins=(
    git
    python
	pip
    docker
	direnv
	kubectl
	kubectx
	minikube

	virtualenvwrapper

#	zsh-autosuggestions
	zsh-syntax-highlighting
)
autoload -U add-zsh-hook

# place this after nvm initialization!
source "$ZSH/oh-my-zsh.sh"

# ---------------
# System
# ---------------
safe-alias codium "$VSCODEAPP"
safe-alias code "$VSCODEAPP"
safe-alias vscode "$VSCODEAPP"
safe-alias v "$EDITOR"
alias xx="chmod +x"
alias mine='sudo chown -R $USER:$USER .'

[[ -f "$BIN_PATH/z/z.sh" ]] && source "$BIN_PATH/z/z.sh"
alias dd="dd status=progress"
alias vgf="valgrind --tool=memcheck --leak-check=full"
alias open="xdg-open"
alias xcopy="xclip -sel clip"
alias cp="rsync --info=progress2"
# ignore papging
alias bat="bat -P"
pk() {
	kill -9 $(pgrep -f "$@")
}
jlog() {
	journalctl -q -f _PID=$(pgrep -f "$@")
}
scat() {
	cat "$@" 2>/dev/null
}
anyfindcat() {
	grep -nri "$@" 2>/dev/null
}
alias \?="anyfindcat"

anyfind() {
	find . -name "*$1*" 2>/dev/null
}
alias f\?="anyfind"

# key bindings
bindkey "^[[1;3C" forward-word
bindkey "^[[1;3D" backward-word

extract () {
	# default output where you are
	output="${2:-'./'}"
    if [ -f "$1" ]; then
        case $1 in
            *.tar.bz2)  tar -jxvf "$1" -C "$output"                       ;;
            *.tar.gz)   tar -zxvf "$1" -C "$output"                       ;;
            *.tar.xz|*.tar)   tar -xvf "$1" -C "$output"                  ;;
            *.bz2)      bunzip2 "$1" -d "$output"                         ;;
            *.dmg)      hdiutil mount "$1"                    ;; # macos
            *.gz)       gunzip "$1"                           ;;
            *.tbz2)     tar -jxvf "$1" -C "$output"                       ;;
            *.tgz)      tar -zxvf "$1" -C "$output"                       ;;
            *.zip)      unzip "$1" -d "$output"                           ;;
            *.ZIP)      unzip "$1" -d "$output"                           ;;
            *.pax)      pax -r < "$1"                    ;;
            *.pax.Z)    uncompress "$1" --stdout | pax -r     ;;
            *.rar)      unrar x "$1"                          ;;
            *.Z)        uncompress "$1"                       ;;
            *)          echo "'$1' cannot be extracted/mounted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

loadenv () {
	if [[ $# == "0" ]]; then
		echo "you need to specified at least one file..."
		return 1
	fi
	for file in "${@}"; do
		export "$(grep -v '^#' "$file" | xargs)"
	done
}

unloadenv () {
	if [[ $# == "0" ]]; then
		echo "you need to specified at least one file..."
		return 1
	fi
	for file in "${@}"; do
		unset "$(grep -v '^#' "$file" | sed -E 's/(.*)=.*/\1/' | xargs)"
	done
}
watchexec () {
	file=$1
	while true; do
		inotifywait -e close_write "$file" &>/dev/null
		# run command without first file watch
		"${@:2}"
	done
}

sdir() {
	find . -maxdepth "${1:-1}" ! -path . -exec du -sh "{}" ";" | sort -rh
}

# ---------------
# Docker
# ---------------
alias dpsm='docker ps -a'
alias dps='docker ps -a --format "table {{.ID}}\t{{.Status}}\t{{.Names}}"'
alias dcps='docker-compose ps -a'
alias dlogs='docker logs'
alias dclogs='docker-compose logs'
alias drm='docker rm -f $(docker ps -a -q | tr "\n" " ")'
alias drs='docker restart'
alias dkill='docker kill $(docker ps -a -q | tr "\n" " ")'
alias dex='docker exec -it'
compdef dex='docker' 2>/dev/null
alias docker-compose="docker compose"

drmi() {
	docker rmi "$(docker images | grep "$1" | awk "{print \$3}" | uniq)"
}

dfclean () {
	echo "clean image..."
	docker image rm -f "$(sudo \\docker images -q)" 1&>/dev/null
	echo "clean volume..."
	docker volume prune -f 1&>/dev/null
	echo "clean system..."
	docker system prune -f 1&>/dev/null
	echo "clean container..."
	docker container prune -f 1&>/dev/null
	echo "clean network..."
	docker network prune -f 1&>/dev/null
}

docker-debug() {
	container=$1
	volumes=(
		 --volume "$SCRIPTS_PATH:/root/.myconfig/scripts"
		 --volume "$(readlink -f "$BASE_DIR_PATH/docker-extras.py"):/root/.myconfig/docker-extras.py"
		 --volume "$HOME/.zshrc:/root/.zshrc"
		 --volume "$HOME/.vimrc:/root/.vimrc"
		 --volume "/var/run/docker.sock:/var/run/docker.sock"
	)
	uniqueId="$1$(date)"
	command docker-debug "${volumes[@]}" "$@" bash -c "export NETSHOOT_DOCKER=$container && zsh" 2>"/tmp/$uniqueId"
	error=$(cat "/tmp/$uniqueId")

	# ignore CTR+C/D or exit command
	[[ -z "$error" || "$error" == *"Error: ExitStatus 130"* ||  "$error" == *"Error: ExitStatus 127"* ]] && return
	
	echo "$error"
	return 1
}

docker() {
    if [[ $1 == "debug" ]]; then
		# remove first args
		shift
        docker-debug "$@"
    else
        command docker "$@"
    fi
}


# ---------------
# Javascript
# ---------------
# nvm
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" 2>/dev/null 1>/dev/null
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"

if hascmd nvm_find_nvmrc; then
	load-nvmrc() {
		local nvmrc_path

		nvmrc_path="$(nvm_find_nvmrc)"
		if [ -n "$nvmrc_path" ]; then
			local nvmrc_node_version
			nvmrc_node_version=$(nvm version "$(cat "${nvmrc_path}")")

			if [ "$nvmrc_node_version" = "N/A" ]; then
			nvm install
			elif [ "$nvmrc_node_version" != "$(nvm version)" ]; then
			nvm use
			fi
		elif [ -n "$(PWD=$OLDPWD nvm_find_nvmrc)" ] && [ "$(nvm version)" != "$(nvm version default)" ]; then
			echo "Reverting to nvm default version"
			nvm use default
		fi
	}
	add-zsh-hook chpwd load-nvmrc
	load-nvmrc
fi

# bun completions
[ -s "/home/remi/.local/share/reflex/bun/_bun" ] && source "/home/remi/.local/share/reflex/bun/_bun"
export BUN_INSTALL="$HOME/.local/share/reflex/bun"
export PATH="$BUN_INSTALL/bin:$PATH:$BASE_DIR_PATH/flutter/bin"

# pnpm
export PNPM_HOME="/home/remi/.local/share/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac


# ---------------
# Python
# ---------------

# pyenv
export PYENV_ROOT="$HOME/.pyenv"
[[ -d "$PYENV_ROOT/bin" ]] && export PATH="$PYENV_ROOT/bin:$PATH"
if hascmd pyenv; then
	eval "$(pyenv init -)"
	load-pyenv() {
		force=$1
		pyenvLocal=$(pyenv local 2>/dev/null)
		results="$?"
		if [[ "$results" != "0" || "$force" == "true" ]]; then
			if [[ "$PYENV_VIRTUAL_ENV" != "" ]]; then
				if [[ "$force" != "true" ]]; then
					echo "(pyenv deactivate) $pyenvLocal"
				fi
				pyenv deactivate 2>/dev/null
				unset PYENV_VIRTUAL_ENV
			fi
			if [[ "$force" != "true" ]]; then
				return
			fi
		fi
		if [[ "$results" == "0" && "$PYENV_VIRTUAL_ENV" != *"/$pyenvLocal" ]]; then
			echo "(pyenv activate) $pyenvLocal"
			pyenv activate "$pyenvLocal"
		fi
	}
	add-zsh-hook chpwd load-pyenv
	load-pyenv "true"
fi

PYTHON_VERSION="$(scat ./.pyversion || scat ~/.pyversion || echo '3')"
export PYTHONSTARTUP="$DOTFILE_PATH/common/linked/startup.py"
export PYTHON_VERSION
alias python='python$PYTHON_VERSION'
alias pydev="PYTHON_COLORS=1 PYTHONBREAKPOINT=1 python -W always -d -X dev"
alias pyopti="python -OO -u"
function pip() {
	python -m pip "$@"
}
compdef pip="pip"
alias ipy="bpython"
alias bpy="bpython"
alias pypy="pypy3"
alias venv="source ./venv/bin/activate"
cvenv() {
	"python${1:-3}" -m venv venv --system-site-packages && venv && pip install --upgrade pip && deactivate
}
alias dvenv="deactivate"
alias delvenv="rm -rf .venv"
hascmd uv && eval "$(uv generate-shell-completion zsh)"
hascmd uvx && eval "$(uvx --generate-shell-completion zsh)"

function py() {
	if [[ $# -eq 0 ]]; then
		# if not arguements, run bpython
		bpython
	else
		python "$@"
	fi
}
alias py="py"

# ---------------
# Media
# ---------------
alias spotdl="spotdl -o ~/Music/spotdl"
alias yt-dlp="yt-dlp --embed-subs --write-subs --write-auto-subs --sub-langs fr "
alias yt-dlp-tor="yt-dlp --proxy socks5://localhost:9150 "
ffmpeg265() {
	input=$1
	output=$(echo "$input" | sed "s/\.\([^.]*\)/-conv.\1/g")
	ffmpeg -i "$input" -vcodec libx265 "$output"
}

svgo() {
	npx run svgo "$@"
}

# ---------------
# Utils
# ---------------
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal

install_vscode_extentions () {
	exts=$(sed 's/^/ --install-extension /' "$1" | tr '\n' ' ')
	$VSCODEAPP --force $exts
}

prompt_virtualenv() {
	env=()
    color="#4aa5f0"
  if [[ -n $VIRTUAL_ENV ]]; then
	env+=("env($(basename "$VIRTUAL_ENV"))")
  fi
#   info=($(prompt_logo_dir))
#   if [[ -n "$info" ]]; then
#     env=("${info[1]}" $env)
#     color=${info[2]}
#   fi

  if [[ -n "${env[*]}" ]]; then
    prompt_segment $color default "%{%F{black}%}$env"
  fi
}

# -------------
# docker netshoot
# -------------
if [[ "$NETSHOOT_DOCKER" ]]; then
	# shellcheck disable=SC1090
	source "$(which load_docker_netshoot)"
fi

