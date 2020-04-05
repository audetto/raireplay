import os.path


def create_folder(name):
    if not os.path.exists(name):
        os.makedirs(name)
    return name


home_folder = os.path.expanduser("~")

root_folder = create_folder(os.path.join(home_folder, ".raireplay"))
data_folder = create_folder(os.path.join(root_folder, "data"))

replay_folder = create_folder(os.path.join(data_folder, "replay"))
raiplay_folder = create_folder(os.path.join(data_folder, "raiplay"))
raiplayradio_folder = create_folder(os.path.join(data_folder, "raiplayradio"))
item_folder = create_folder(os.path.join(data_folder, "items"))
page_folder = create_folder(os.path.join(data_folder, "pages"))
demand_folder = create_folder(os.path.join(data_folder, "demand"))
tg_folder = create_folder(os.path.join(data_folder, "tg"))
mediaset_folder = create_folder(os.path.join(data_folder, "mediaset"))
pluzz_folder = create_folder(os.path.join(data_folder, "pluzz"))
tf1_folder = create_folder(os.path.join(data_folder, "tf1"))
m6_folder = create_folder(os.path.join(data_folder, "m6"))

program_folder = create_folder(os.path.join(root_folder, "programs"))
