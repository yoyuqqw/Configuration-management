import unittest
import tarfile
import os
import io
from shell_emulator import ShellEmulator

class TestShellEmulator(unittest.TestCase):
    def setUp(self):
        # Создаем тестовый tar-архив
        self.test_tar_path = "test_vfs.tar"
        with tarfile.open(self.test_tar_path, "w") as tar:
            for file_name, content in {
                "файл1.txt": b"Hello, World!\nThis is a test file.\nSecond line.\n",
                "папка1/файл2.txt": b"Another file in a directory.\n",
                "папка1/папка2/файл3.txt": b"Nested directory file.\n",
            }.items():
                tarinfo = tarfile.TarInfo(name=file_name)
                tarinfo.size = len(content)
                tar.addfile(tarinfo, fileobj=io.BytesIO(content))

        # Создаем тестовый конфигурационный файл
        self.config_path = "test_config.toml"
        with open(self.config_path, "w") as f:
            f.write(
                """
                user_name = "test_user"
                computer_name = "test_computer"
                vfs_path = "test_vfs.tar"
                """
            )

        self.shell = ShellEmulator(config_path=self.config_path)

    def tearDown(self):
        # Удаляем временные файлы после тестов
        os.remove(self.test_tar_path)
        os.remove(self.config_path)

    def test_ls(self):
        self.shell.current_path = "/"
        self.shell.ls()
        # Пример проверки вывода. Можно заменить на перехват stdout

    def test_cd(self):
        self.shell.cd("папка1")
        self.assertEqual(self.shell.current_path, "/папка1/")

    def test_tail(self):
        output = self.shell.tail("файл1.txt")
        self.assertIn("Hello, World!", output)

    def test_mv(self):
        self.shell.mv("файл1.txt", "папка1/файл1_renamed.txt")
        self.assertIn("/папка1/файл1_renamed.txt", self.shell.members)
        self.assertNotIn("/файл1.txt", self.shell.members)

    def test_rev(self):
        reversed_content = self.shell.rev("файл1.txt")
        self.assertEqual(reversed_content, "\n.enil dnoceS\n.elif tset a si sihT\n!dlroW ,olleH")

if __name__ == "__main__":
    unittest.main()
