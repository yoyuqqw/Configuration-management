import os
import tarfile
import toml

class ShellEmulator:
    def __init__(self, config_path="config.toml"):
        self.load_config(config_path)
        self.current_path = "/"  # Начальная директория
        self.tar = tarfile.open(self.config["vfs_path"], "r")
        self.members = {"/" + m.name: m for m in self.tar.getmembers()}  # Все элементы с абсолютными путями

    def load_config(self, config_path):
        try:
            self.config = toml.load(config_path)
        except Exception as e:
            print(f"Ошибка загрузки конфигурационного файла: {e}")
            self.config = None

    def ls(self):
        """Выводит содержимое текущей директории."""
        try:
            prefix = self.current_path.rstrip("/") + "/"
            items = set()
            for name in self.members:
                if name.startswith(prefix) and name != prefix:
                    sub_path = name[len(prefix):].split("/")[0]
                    items.add(sub_path)
            print("\n".join(sorted(items)) if items else "Текущая директория пуста.")
        except Exception as e:
            print(f"Ошибка при выполнении ls: {e}")

    def cd(self, path):
        """Переход в указанную директорию."""
        try:
            if path == "..":
                # Переход на уровень выше
                self.current_path = os.path.dirname(self.current_path.rstrip("/"))
                if not self.current_path:
                    self.current_path = "/"
            elif path.startswith("/"):
                # Абсолютный путь
                new_path = path.rstrip("/") + "/"
                if new_path in self.members and self.members[new_path].isdir():
                    self.current_path = new_path
                else:
                    raise FileNotFoundError(f"Путь {path} не найден.")
            else:
                # Относительный путь
                new_path = os.path.join(self.current_path, path).rstrip("/") + "/"
                if new_path in self.members and self.members[new_path].isdir():
                    self.current_path = new_path
                else:
                    raise FileNotFoundError(f"Путь {path} не найден.")
        except Exception as e:
            print(f"Ошибка при выполнении cd: {e}")

    def exit(self):
        """Завершает работу эмулятора."""
        print("Выход из эмулятора.")
        self.tar.close()
        exit()

    def tail(self, filename):
        """Выводит последние 10 строк указанного файла."""
        try:
            filepath = os.path.join(self.current_path, filename).lstrip("/")
            if filepath in self.members:
                file = self.tar.extractfile(self.members[filepath])
                if file:
                    lines = file.readlines()
                    print(b"".join(lines[-10:]).decode("utf-8"))
                else:
                    print(f"Невозможно открыть файл {filename}.")
            else:
                print(f"Файл {filename} не найден.")
        except Exception as e:
            print(f"Ошибка при выполнении tail: {e}")

    def mv(self, source, destination):
        """Перемещает файл или директорию."""
        try:
            source_path = os.path.join(self.current_path, source).lstrip("/")
            destination_path = os.path.join(self.current_path, destination).lstrip("/")
            if source_path in self.members:
                self.members[destination_path] = self.members.pop(source_path)
                print(f"{source} перемещён в {destination}.")
            else:
                print(f"Источник {source} не найден.")
        except Exception as e:
            print(f"Ошибка при выполнении mv: {e}")

    def rev(self, filename):
        """Выводит строки файла в обратном порядке."""
        try:
            filepath = os.path.join(self.current_path, filename).lstrip("/")
            if filepath in self.members:
                file = self.tar.extractfile(self.members[filepath])
                if file:
                    lines = file.readlines()
                    reversed_lines = [line.decode("utf-8")[::-1] for line in lines]
                    print("\n".join(reversed_lines))
                else:
                    print(f"Невозможно открыть файл {filename}.")
            else:
                print(f"Файл {filename} не найден.")
        except Exception as e:
            print(f"Ошибка при выполнении rev: {e}")

    def run(self):
        """Запускает эмулятор командной строки."""
        try:
            while True:
                command = input(f"{self.config['user_name']}@{self.config['computer_name']} {self.current_path}$ ").strip()
                if command.startswith("ls"):
                    self.ls()
                elif command.startswith("cd"):
                    self.cd(command.split(" ", 1)[1])
                elif command.startswith("exit"):
                    self.exit()
                elif command.startswith("tail"):
                    self.tail(command.split(" ", 1)[1])
                elif command.startswith("mv"):
                    parts = command.split(" ", 2)
                    if len(parts) == 3:
                        self.mv(parts[1], parts[2])
                    else:
                        print("Использование: mv <источник> <назначение>")
                elif command.startswith("rev"):
                    self.rev(command.split(" ", 1)[1])
                else:
                    print(f"Неизвестная команда: {command}")
        except KeyboardInterrupt:
            print("\nВыход из эмулятора.")
            self.tar.close()

if __name__ == "__main__":
    shell = ShellEmulator()
    shell.run()
