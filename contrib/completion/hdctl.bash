#!/bin/bash
# hdctl bash completion script
# Installation: source contrib/completion/hdctl.bash
# Or: install -D contrib/completion/hdctl.bash ~/.bash_completion.d/hdctl

_hdctl_completion() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev="${COMP_WORDS[COMP_CWORD-1]}"
    local first="${COMP_WORDS[1]}"

    # Base commands
    local commands="login logout pages users jobs env help version"

    case $first in
        login)
            # login <username>
            if [[ $COMP_CWORD -eq 2 ]]; then
                _hdctl_users
            fi
            ;;
        pages)
            # pages [list|view|create|update|delete]
            local subcommands="list view create update delete search"
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=($(compgen -W "$subcommands" -- "$cur"))
            elif [[ $COMP_CWORD -eq 3 ]]; then
                case $prev in
                    view|update|delete)
                        _hdctl_page_ids
                        ;;
                    search)
                        # Free text search
                        COMPREPLY=()
                        ;;
                esac
            fi
            ;;
        users)
            # users [list|create|delete|roles]
            local subcommands="list create delete roles"
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=($(compgen -W "$subcommands" -- "$cur"))
            elif [[ $COMP_CWORD -eq 3 ]]; then
                case $prev in
                    delete|roles)
                        _hdctl_users
                        ;;
                esac
            fi
            ;;
        jobs)
            # jobs [list|view|cancel|status]
            local subcommands="list view cancel status"
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=($(compgen -W "$subcommands" -- "$cur"))
            elif [[ $COMP_CWORD -eq 3 ]]; then
                case $prev in
                    view|cancel|status)
                        _hdctl_job_ids
                        ;;
                esac
            fi
            ;;
        env)
            # env [list|set|get|unset]
            local subcommands="list set get unset"
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=($(compgen -W "$subcommands" -- "$cur"))
            elif [[ $COMP_CWORD -eq 3 ]]; then
                case $prev in
                    get|unset|set)
                        _hdctl_env_vars
                        ;;
                esac
            fi
            ;;
        help)
            # help [command]
            if [[ $COMP_CWORD -eq 2 ]]; then
                COMPREPLY=($(compgen -W "$commands" -- "$cur"))
            fi
            ;;
        *)
            # No subcommand yet, suggest main commands
            if [[ $COMP_CWORD -eq 1 ]]; then
                COMPREPLY=($(compgen -W "$commands" -- "$cur"))
            fi
            ;;
    esac

    return 0
}

# Dynamic page IDs from Agenda API
_hdctl_page_ids() {
    local token="${HDCTL_TOKEN:-250886}"
    local api_url="${HDCTL_API:-http://127.0.0.1:12399}"

    # Fetch page IDs from API with timeout
    local pages=$(curl -s -m 2 \
        -H "Authorization: Bearer $token" \
        "$api_url/agenda/pages" 2>/dev/null | \
        jq -r '.[].id' 2>/dev/null || echo "")

    if [[ -z "$pages" ]]; then
        # Fallback: static list if API unavailable
        pages=$(seq 1 16)
    fi

    COMPREPLY=($(compgen -W "$pages" -- "$cur"))
}

# Dynamic user list
_hdctl_users() {
    local token="${HDCTL_TOKEN:-250886}"
    local api_url="${HDCTL_API:-http://127.0.0.1:12399}"

    local users=$(curl -s -m 2 \
        -H "Authorization: Bearer $token" \
        "$api_url/users" 2>/dev/null | \
        jq -r '.[].username' 2>/dev/null || echo "admin")

    COMPREPLY=($(compgen -W "$users" -- "$cur"))
}

# Dynamic job IDs
_hdctl_job_ids() {
    local token="${HDCTL_TOKEN:-250886}"
    local api_url="${HDCTL_API:-http://127.0.0.1:12399}"

    local jobs=$(curl -s -m 2 \
        -H "Authorization: Bearer $token" \
        "$api_url/jobs" 2>/dev/null | \
        jq -r '.[].id' 2>/dev/null || echo "")

    COMPREPLY=($(compgen -W "$jobs" -- "$cur"))
}

# Dynamic environment variables
_hdctl_env_vars() {
    local token="${HDCTL_TOKEN:-250886}"
    local api_url="${HDCTL_API:-http://127.0.0.1:12399}"

    local vars=$(curl -s -m 2 \
        -H "Authorization: Bearer $token" \
        "$api_url/env" 2>/dev/null | \
        jq -r 'keys[]' 2>/dev/null || env | cut -d= -f1 | sort)

    COMPREPLY=($(compgen -W "$vars" -- "$cur"))
}

# Register completion
complete -o bashdefault -o default -o nospace -F _hdctl_completion hdctl
