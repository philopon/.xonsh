import conda_wrapper
from xonsh.prompt.gitstatus import gitstatus
from subprocess import SubprocessError


def set_prompt():
    $PROMPT = (
        '{env_name:{}}'
        '{BOLD_#5f5f5f}{user}{ssh_color}@{hostname} '
        '{BOLD_#d78700}{cwd}'
        '{NO_COLOR}{git_info: ({})}\n'
        '{prompt_end_color}{prompt_end}{NO_COLOR} '
    )

    def git_info():
        try:
            s = gitstatus()
            chunks = [s.branch]
            if s.changed > 0:
                chunks.append("{#ffaf00}● {NO_COLOR}")
            if s.staged > 0:
                chunks.append("{#00d700}● {NO_COLOR}")

            return "".join(chunks)
        except SubprocessError:
            return None

    def ssh_color():
        return '{BOLD_#ff5f5f}' if 'SSH_CONNECTION' in ${...} else ''

    def prompt_end_color():
        if len(__xonsh__.history) > 0 and __xonsh__.history[-1].rtn != 0:
            return "{BOLD_#d70000}"
        else:
            return "{BOLD_#00d700}"

    $PROMPT_FIELDS['env_name'] = conda_wrapper.env_name
    $PROMPT_FIELDS['ssh_color'] = ssh_color
    $PROMPT_FIELDS['prompt_end_color'] = prompt_end_color
    $PROMPT_FIELDS['git_info'] = git_info
