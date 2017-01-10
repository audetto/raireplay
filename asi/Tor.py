import stem
import stem.connection


def setTorExitNodes(country):
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        controller.set_conf("ExcludeNodes", "")
        value = country
        if not "." in value:
            value = "{" + value + "}"
        controller.set_conf("ExitNodes", value)


def setTorExcludeNodes(skip):
    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        controller.set_conf("ExcludeNodes", skip)


def getTorExitNodes():
    try:
        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            res = controller.get_conf("ExitNodes")
            return res
    except:
        return None

def getTorExcludeNodes():
    try:
        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            res = controller.get_conf("ExcludeNodes")
            return res
    except:
        return None
