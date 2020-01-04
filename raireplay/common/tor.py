import logging
import stem.control


def set_tor_exit_nodes(country):

    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        controller.set_conf("ExcludeNodes", "")
        value = country
        if not "." in value:
            value = "{" + value + "}"
        controller.set_conf("ExitNodes", value)


def set_tor_exclude_nodes(skip):
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        controller.set_conf("ExcludeNodes", skip)


def get_tor_exit_nodes():
    try:
        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            res = controller.get_conf("ExitNodes")
            return res
    except stem.SocketError:
        return None
    except Exception:
        logging.exception('TOR exit nodes')
        return None


def get_tor_exclude_nodes():
    try:
        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            res = controller.get_conf("ExcludeNodes")
            return res
    except stem.SocketError:
        return None
    except Exception:
        logging.exception('TOR exclude nodes')
        return None
