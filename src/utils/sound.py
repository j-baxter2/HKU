import arcade

def load_sound(name:str, source = "builtin", file_type = "wav"):
    if source == "builtin":
        path = f":resources:sounds/{name}.{file_type}"
    elif source == "hku":
        path = f"resources/sounds/{name}.{file_type}"
    else:
        path = name

    if name != None:
        sound = arcade.load_sound(path)
        return sound
    else:
        pass

def play_sound(sound):
    if sound:
        arcade.play_sound(sound)
    else:
        pass
