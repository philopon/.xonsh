from . import conda_wrapper
from xonsh.prompt.gitstatus import gitstatus
from subprocess import SubprocessError


def set_prompt():
    __xonsh__.env["PROMPT"] = (
        '{env_name:{}}'
        '{BOLD_#5f5f5f}{puser}{ssh_color}@{phostname} '
        '{BOLD_#d78700}{cwd}'
        '{NO_COLOR}{git_info: ({})}\n'
        '{prompt_end_color}{prompt_end}{NO_COLOR} '
    )

    circle_number = {
        1: "❶",
        2: "❷",
        3: "❸",
        4: "❹",
        5: "❺",
        6: "❻",
        7: "❼",
        8: "❽",
        9: "❾",
        10: "❿",
        11: "⓫",
        12: "⓬",
        13: "⓭",
        14: "⓮",
        15: "⓯",
        16: "⓰",
        17: "⓱",
        18: "⓲",
        19: "⓳",
        20: "⓴",
    }

    __xonsh__.env["PRIVATE"] = False

    def puser():
        return "XXXXX" if __xonsh__.env["PRIVATE"] else __xonsh__.env["PROMPT_FIELDS"]["user"]

    def phostname():
        return "XXXXX" if __xonsh__.env["PRIVATE"] else __xonsh__.env["PROMPT_FIELDS"]["hostname"]

    def git_info():
        try:
            s = gitstatus()
            chunks = [s.branch]
            if s.untracked > 0:
                chunks.extend(["{#af0000}", circle_number.get(s.untracked, "●"), "{NO_COLOR} "])
            if s.changed > 0:
                chunks.extend(["{#ffaf00}", circle_number.get(s.changed, "●"), "{NO_COLOR} "])
            if s.staged > 0:
                chunks.extend(["{#00af00}", circle_number.get(s.staged, "●"), "{NO_COLOR} "])

            return "".join(chunks)
        except SubprocessError:
            return None

    def ssh_color():
        return '{BOLD_#ff5f5f}' if 'SSH_CONNECTION' in __xonsh__.env else ''

    def prompt_end_color():
        if len(__xonsh__.history) > 0 and __xonsh__.history[-1].rtn != 0:
            return "{BOLD_#d70000}"
        else:
            return "{BOLD_#00d700}"

    __xonsh__.env["PROMPT_FIELDS"]['env_name'] = conda_wrapper.env_name
    __xonsh__.env["PROMPT_FIELDS"]['ssh_color'] = ssh_color
    __xonsh__.env["PROMPT_FIELDS"]['prompt_end_color'] = prompt_end_color
    __xonsh__.env["PROMPT_FIELDS"]['git_info'] = git_info
    __xonsh__.env["PROMPT_FIELDS"]['puser'] = puser
    __xonsh__.env["PROMPT_FIELDS"]['phostname'] = phostname
