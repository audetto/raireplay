import logging

def setTorExitNodes(country):
    import stem
    import stem.connection

    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        controller.set_conf("ExcludeNodes", "")
        value = country
        if not "." in value:
            value = "{" + value + "}"
        controller.set_conf("ExitNodes", value)


def setTorExcludeNodes(skip):
    import stem
    import stem.connection

    with stem.control.Controller.from_port() as controller:
        controller.authenticate()
        controller.set_conf("ExcludeNodes", skip)


def getTorExitNodes():
    try:
        import stem
        import stem.connection

        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            res = controller.get_conf("ExitNodes")
            return res
    except Exception as e:
        logging.info('Exception: {0}'.format(e))
        return None


def getTorExcludeNodes():
    try:
        import stem
        import stem.connection

        with stem.control.Controller.from_port() as controller:
            controller.authenticate()
            res = controller.get_conf("ExcludeNodes")
            return res
    except Exception as e:
        logging.info('Exception: {0}'.format(e))
        return None
