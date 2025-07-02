import tui

menu_data = [
    "camera_ffmpeg",
    "select_machine",
    "history",
    "test",
    "Exit",  # Leaf item – still quits immediately
]

lst = []
option = "try"

while (option != "Exit"):
    app = tui.MenuApp(menu_data)
    app.run()
    option = app.selected_option

    if option == "camera_ffmpeg":
        import camera_ffmpeg
    elif option == "history":
        import webpage
    elif option == "test":
        import test
    elif option == "select_machine":
        import select_machine




    lst.append(option)

print("Selected option:", lst)